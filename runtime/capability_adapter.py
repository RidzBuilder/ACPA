"""Explicit capability and adapter resolution boundary for ACPA GAP-ACPA-003."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
import json

SUPPORTED_CAPABILITIES = {
    "scene.composition", "camera.motion", "product.interaction",
    "product.dispensing", "product.application", "macro.detail",
    "json.compilation", "output.validation",
}

LOCAL_ADAPTER_CAPABILITIES = {"local-smoke-adapter": SUPPORTED_CAPABILITIES.copy()}


@dataclass(frozen=True)
class CapabilityRequirement:
    capability_id: str
    status: str
    adapter_candidates: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class AdapterResolution:
    resolution_id: str
    status: str
    adapter_id: str | None
    requirements: tuple[CapabilityRequirement, ...]
    unresolved: tuple[str, ...] = ()
    needs_review: tuple[str, ...] = ()
    engine_id: str = "local-smoke"

    def to_contract_dict(self) -> dict[str, Any]:
        return {
            "resolution_id": self.resolution_id,
            "engine_id": self.engine_id,
            "adapter_id": self.adapter_id,
            "status": self.status,
            "unsupported_capabilities": list(self.unresolved),
            "notes": "; ".join(
                r.reason for r in self.requirements if r.reason
            ),
        }


class Adapter(Protocol):
    adapter_id: str
    def execute(self, execution_package: dict[str, Any]) -> dict[str, Any]: ...


class LocalSmokeAdapter:
    adapter_id = "local-smoke-adapter"

    def execute(self, execution_package: dict[str, Any]) -> dict[str, Any]:
        if execution_package.get("status") != "compiled":
            return {"status": "rejected", "reason": "execution_package_not_compiled",
                    "adapter_id": self.adapter_id}
        if execution_package.get("adapter") != self.adapter_id:
            return {"status": "rejected", "reason": "adapter_mismatch",
                    "adapter_id": self.adapter_id}
        required = ("engine", "capabilities", "payload", "validation")
        if any(key not in execution_package for key in required):
            return {"status": "rejected", "reason": "execution_package_incomplete",
                    "adapter_id": self.adapter_id}
        if execution_package.get("validation", {}).get("status") != "passed":
            return {"status": "rejected", "reason": "execution_package_not_validated",
                    "adapter_id": self.adapter_id}
        return {
            "status": "passed",
            "adapter_id": self.adapter_id,
            "engine": execution_package.get("engine"),
            "observable_effect": "local adapter accepted execution package",
            "output_ref": "local-smoke-output-001",
            "validation": {"status": "passed"},
        }


def resolve_capability_adapter(
    required: list[str], *, engine_context: str = "local-smoke"
) -> AdapterResolution:
    requirements: list[CapabilityRequirement] = []
    unresolved: list[str] = []
    needs_review: list[str] = []

    for capability_id in required:
        if capability_id not in SUPPORTED_CAPABILITIES:
            requirements.append(CapabilityRequirement(
                capability_id, "unsupported", reason="capability_not_registered"))
            unresolved.append(capability_id)
        elif engine_context != "local-smoke":
            requirements.append(CapabilityRequirement(
                capability_id, "needs_review", reason="engine_context_not_implemented"))
            needs_review.append(capability_id)
        else:
            requirements.append(CapabilityRequirement(
                capability_id, "supported", ("local-smoke-adapter",)))

    if unresolved:
        return AdapterResolution("local-resolution-blocked-001", "blocked", None,
                                 tuple(requirements), tuple(unresolved),
                                 tuple(needs_review), engine_context)
    if needs_review:
        return AdapterResolution("local-resolution-review-001", "needs_review", None,
                                 tuple(requirements), tuple(unresolved),
                                 tuple(needs_review), engine_context)
    return AdapterResolution("local-resolution-001", "resolved",
                             "local-smoke-adapter", tuple(requirements),
                             engine_id=engine_context)


def compile_for_adapter(plan: dict[str, Any], resolution: AdapterResolution) -> dict[str, Any]:
    if resolution.status != "resolved" or not resolution.adapter_id:
        return {
            "status": "blocked",
            "reason": resolution.status,
            "resolution_id": resolution.resolution_id,
            "unresolved": list(resolution.unresolved),
            "needs_review": list(resolution.needs_review),
        }
    return {
        "status": "compiled",
        "engine": resolution.engine_id,
        "adapter": resolution.adapter_id,
        "capabilities": [r.capability_id for r in resolution.requirements],
        "payload": {
            "content_family": plan["content_family"],
            "pattern_id": plan["pattern_id"],
            "scenes": plan["scenes"],
        },
        "validation": {"status": "passed"},
    }


def execute_with_adapter(execution_package: dict[str, Any],
                         adapter: Adapter | None = None) -> dict[str, Any]:
    adapter = adapter or LocalSmokeAdapter()
    return adapter.execute(execution_package)


def conformance_smoke() -> dict[str, Any]:
    plan = {
        "content_family": "Macro Demo",
        "pattern_id": "macro-demo-v0.1",
        "scenes": [{"scene_id": "S01", "purpose": "Product Hook"}],
    }
    resolution = resolve_capability_adapter(
        ["scene.composition", "product.application", "output.validation"])
    package = compile_for_adapter(plan, resolution)
    execution = execute_with_adapter(package)
    blocked = resolve_capability_adapter(["unknown.capability"])
    review = resolve_capability_adapter(["scene.composition"],
                                        engine_context="external-provider")
    return {
        "status": "passed" if (
            resolution.status == "resolved" and package["status"] == "compiled"
            and execution["status"] == "passed"
            and blocked.status == "blocked" and review.status == "needs_review"
        ) else "failed",
        "resolution": resolution.to_contract_dict(),
        "package": {"status": package["status"], "adapter": package.get("adapter")},
        "execution": execution,
        "blocked_case": blocked.to_contract_dict(),
        "review_case": review.to_contract_dict(),
    }


if __name__ == "__main__":
    print(json.dumps(conformance_smoke(), indent=2))
