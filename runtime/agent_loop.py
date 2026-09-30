"""Bounded ACPA agentic runtime loop with explicit output validation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from .acpa_runtime import compile_execution, resolve_capabilities, validate_plan


@dataclass
class AgentState:
    phase: str = "draft"
    attempt: int = 0
    observation: dict[str, Any] = field(default_factory=dict)
    decision: str = "continue"
    correction: str | None = None
    completed: bool = False


def _plan() -> dict[str, Any]:
    return {
        "content_family": "Macro Demo",
        "pattern_id": "macro-demo-v0.1",
        "scenes": [
            {"scene_id": "S01", "purpose": "Product Hook"},
            {"scene_id": "S02", "purpose": "Dispense"},
            {"scene_id": "S03", "purpose": "Application"},
            {"scene_id": "S04", "purpose": "Macro Proof"},
            {"scene_id": "S05", "purpose": "Benefit"},
            {"scene_id": "S06", "purpose": "Brand Closure"},
        ],
    }


def validate_executor_result(result: Any) -> list[str]:
    if not isinstance(result, dict):
        return ["executor_result_not_object"]
    errors: list[str] = []
    if result.get("status") != "passed":
        errors.append("executor_status_not_passed")
        return errors
    output_ref = result.get("output_ref")
    if not isinstance(output_ref, str) or not output_ref.strip():
        errors.append("missing_output_ref")
    validation = result.get("validation")
    if not isinstance(validation, dict) or validation.get("status") != "passed":
        errors.append("output_validation_not_passed")
    return errors


def run_agent_loop(
    executor: Callable[[dict[str, Any], int], dict[str, Any]] | None = None,
    *,
    max_attempts: int = 2,
    require_human_gate: bool = True,
) -> dict[str, Any]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    state = AgentState()
    trace: list[dict[str, Any]] = []

    def record(event: str, **data: Any) -> None:
        trace.append({"sequence": len(trace) + 1, "event": event,
                      "attempt": state.attempt, "phase": state.phase, **data})

    intent = {
        "intent_id": "MA-EXP-001-AGENT-001",
        "goal": "compile a valid Macro Demo execution package",
        "success_criteria": ["plan_valid", "capabilities_supported", "execution_success"],
    }
    state.phase = "intent"
    record("intent.accepted", intent=intent)

    state.phase = "planning"
    plan = _plan()
    record("plan.created", plan=plan)

    errors = validate_plan(plan)
    if errors:
        state.phase = "needs_review"
        state.decision = "blocked"
        record("plan.rejected", errors=errors)
        return _result(state, trace)

    resolution = resolve_capabilities([
        "scene.composition", "product.dispensing", "product.application",
        "macro.detail", "json.compilation", "output.validation",
    ])
    record("capabilities.resolved", resolution=resolution)

    package = compile_execution(plan, resolution)
    if package["status"] != "compiled":
        state.phase = "blocked"
        state.decision = "blocked"
        record("compilation.blocked", package=package)
        return _result(state, trace)

    if require_human_gate:
        state.phase = "human_gate"
        state.decision = "needs_human_approval"
        record("human_gate.required", gate="G4",
               execution_package_id="local-smoke-package-001")
        return _result(state, trace)

    executor = executor or _default_executor

    while state.attempt < max_attempts and not state.completed:
        state.attempt += 1
        state.phase = "executing"
        record("execution.started")

        result = executor(package, state.attempt)
        state.observation = result
        state.phase = "observing"
        record("execution.observed", observation=result)

        validation_errors = validate_executor_result(result)
        if result.get("status") == "passed" and not validation_errors:
            state.phase = "evaluating"
            state.decision = "accept"
            state.completed = True
            record("evaluation.accepted", criteria={"execution_success": True,
                                                    "output_validation": True})
            break

        state.phase = "correcting"
        if validation_errors:
            record("output.validation_failed", errors=validation_errors)

        if state.attempt < max_attempts:
            state.correction = "retry_execution"
            state.decision = "continue"
            record("correction.decided", correction=state.correction)
        else:
            state.correction = "max_attempts_reached"
            state.decision = "blocked"
            record("correction.blocked", correction=state.correction)

    return _result(state, trace)


def _default_executor(package: dict[str, Any], attempt: int) -> dict[str, Any]:
    return {
        "status": "passed",
        "attempt": attempt,
        "output_ref": "local-smoke-output-001",
        "observable_effect": "execution_package accepted by local adapter",
        "validation": {"status": "passed"},
    }


def _result(state: AgentState, trace: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "passed" if state.decision == "needs_human_approval" else
                  ("completed" if state.completed else state.decision),
        "goal": "compile a valid Macro Demo execution package",
        "attempts": state.attempt,
        "state": {"phase": state.phase, "decision": state.decision,
                  "completed": state.completed, "correction": state.correction},
        "trace": trace,
        "human_boundary": "G4 approval required before external execution/promotion",
    }


def run_failure_then_correction() -> dict[str, Any]:
    def executor(package: dict[str, Any], attempt: int) -> dict[str, Any]:
        if attempt == 1:
            return {"status": "failed", "error": "simulated_adapter_timeout"}
        return {
            "status": "passed",
            "attempt": attempt,
            "output_ref": "local-smoke-output-001",
            "observable_effect": "retry accepted by local adapter",
            "validation": {"status": "passed"},
        }
    return run_agent_loop(executor, max_attempts=2, require_human_gate=False)


if __name__ == "__main__":
    print(json.dumps(run_agent_loop(require_human_gate=False), indent=2))
