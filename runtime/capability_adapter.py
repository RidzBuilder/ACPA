"""Explicit capability and adapter resolution boundary for ACPA GAP-ACPA-003.

Bounded local implementation only. The canonical plan remains vendor-neutral;
provider-specific execution is isolated behind an adapter interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
import json

SUPPORTED_CAPABILITIES = {
    "scene.composition",
    "camera.motion",
    "product.interaction",
    "product.dispensing",
    "product.application",
    "macro.detail",
    "json.compilation",
    "output.validation",
}

LOCAL_ADAPTER_CAPABILITIES = {
    "local-smoke-adapter": SUPPORTED_CAPABILITIES.copy(),
}


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


class Adapter(Protocol):
    adapter_id: str

    def execute(self, execution_package: dict[str, Any]) -> dict[str, Any]:
        ...


class LocalSmokeAdapter:
    adapter_id = "local-smoke-adapter"

    def execute(self, execution_package: dict[str, Any]) -> dict[str, Any]:
        if execution_package.get("adapter") != self.adapter_id:
            return {
                "status": "rejected",
                "reason": "adapter_mismatch",
                "adapter_id": self.adapter_id,
            }
        return {
            "status": "passed",
            "adapter_id": self.adapter_id,
            "engine": execution_package.get("engine"),
            "observable_effect": "local adapter accepted execution package",
            "output_ref": "local-smoke-output-001",
        }


def resolve_capability_adapter(
    required: list[str],
    *,
    engine_context: str = "local-smoke",
) -> AdapterResolution:
    """Resolve all required capabilities to one compatible adapter."""
    requirements: list[CapabilityRequirement] = []
    unresolved: list[str] = []
    needs_review: list[str] = []

    for capability_id in required:
        if capability_id not in SUPPORTED_CAPABILITIES:
            requirements.append(CapabilityRequirement(
                capability_id=capability_id,
                status="unsupported",
                reason="capability_not_registered",
            ))
            unresolved.append(capability_id)
        elif engine_context != "local-smoke":
            requirements.append(CapabilityRequirement(
                capability_id=capability_id,
                status="needs_review",
                reason="engine_context_not_implemented",
            ))
            needs_review.append(capability_id)
        else:
            requirements.append(CapabilityRequirement(
                capability_id=capability_id,
                status="supported",
                adapter_candidates=("local-smoke-adapter",),
            ))

    if unresolved:
        return AdapterResolution(
            resolution_id="local-resolution-unsupported-001",
            status="unsupported",
            adapter_id=None,
            requirements=tuple(requirements),
            unresolved=tuple(unresolved),
            needs_review=tuple(needs_review),
        )

    if needs_review:
        return AdapterResolution(
            resolution_id="local-resolution-review-001",
            status="needs_review",
            adapter_id=None,
            requirements=tuple(requirements),
            unresolved=tuple(unresolved),
            needs_review=tuple(needs_review),
        )

    return AdapterResolution(
        resolution_id="local-resolution-001",
        status="resolved",
        adapter_id="local-smoke-adapter",
        requirements=tuple(requirements),
    )


def compile_for_adapter(
    plan: dict[str, Any],
    resolution: AdapterResolution,
) -> dict[str, Any]:
    """Compile only when the capability/adapter boundary is resolved."""
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
        "engine": "local-smoke",
        "adapter": resolution.adapter_id,
        "capabilities": [r.capability_id for r in resolution.requirements],
        "payload": {
            "content_family": plan["content_family"],
            "pattern_id": plan["pattern_id"],
            "scenes": plan["scenes"],
        },
        "validation": {"status": "passed"},
    }


def execute_with_adapter(
    execution_package: dict[str, Any],
    adapter: Adapter | None = None,
) -> dict[str, Any]:
    """Execute through the selected adapter and reject mismatches explicitly."""
    adapter = adapter or LocalSmokeAdapter()
    return adapter.execute(execution_package)


def conformance_smoke() -> dict[str, Any]:
    """Produce a deterministic capability→adapter conformance trace."""
    plan = {
        "content_family": "Macro Demo",
        "pattern_id": "macro-demo-v0.1",
        "scenes": [{"scene_id": "S01", "purpose": "Product Hook"}],
    }
    resolution = resolve_capability_adapter(
        ["scene.composition", "product.application", "output.validation"]
    )
    package = compile_for_adapter(plan, resolution)
    execution = execute_with_adapter(package)
    unsupported = resolve_capability_adapter(["unknown.capability"])
    review = resolve_capability_adapter(
        ["scene.composition"], engine_context="external-provider"
    )
    return {
        "status": "passed" if (
            resolution.status == "resolved"
            and package["status"] == "compiled"
            and execution["status"] == "passed"
            and unsupported.status == "unsupported"
            and review.status == "needs_review"
        ) else "failed",
        "resolution": {
            "status": resolution.status,
            "adapter_id": resolution.adapter_id,
        },
        "package": {
            "status": package["status"],
            "adapter": package.get("adapter"),
        },
        "execution": execution,
        "unsupported_case": {
            "status": unsupported.status,
            "unresolved": list(unsupported.unresolved),
        },
        "review_case": {
            "status": review.status,
            "needs_review": list(review.needs_review),
        },
    }


if __name__ == "__main__":
    print(json.dumps(conformance_smoke(), indent=2))
