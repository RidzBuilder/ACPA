"""Bounded persistent execution/evaluation/evidence registry for ACPA GAP-ACPA-004.

Stdlib-only, file-backed JSON records. This is a conformance surface, not a
production database. The registry preserves explicit linkage:
ExecutionRecord -> EvaluationRecord -> EvidenceRecord.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PersistenceError(RuntimeError):
    pass


class RecordRegistry:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _write(self, kind: str, record_id: str, record: dict[str, Any]) -> str:
        if not record_id or record.get("record_type") != kind:
            raise PersistenceError(f"invalid_{kind.lower()}_record")
        path = self.root / f"{kind.lower()}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return str(path)

    def write_execution(self, record: dict[str, Any]) -> str:
        required = ("execution_id", "experiment_id", "status", "execution_package")
        if any(key not in record for key in required):
            raise PersistenceError("execution_record_missing_required_field")
        record = {**record, "record_type": "execution"}
        return self._write("execution", record["execution_id"], record)

    def write_evaluation(self, record: dict[str, Any]) -> str:
        required = ("evaluation_id", "experiment_id", "execution_id", "observations", "decision")
        if any(key not in record for key in required):
            raise PersistenceError("evaluation_record_missing_required_field")
        if record["decision"] not in {
            "iterate", "accept_as_experiment", "promote", "reject", "blocked"
        }:
            raise PersistenceError("invalid_evaluation_decision")
        record = {**record, "record_type": "evaluation"}
        return self._write("evaluation", record["evaluation_id"], record)

    def write_evidence(self, record: dict[str, Any]) -> str:
        required = (
            "evidence_id", "experiment_id", "execution_id",
            "evaluation_id", "result", "decision", "promotion_status"
        )
        if any(key not in record for key in required):
            raise PersistenceError("evidence_record_missing_required_field")
        if record["promotion_status"] not in {
            "unreviewed", "provisional", "promoted", "rejected"
        }:
            raise PersistenceError("invalid_promotion_status")
        record = {**record, "record_type": "evidence"}
        return self._write("evidence", record["evidence_id"], record)

    def _read_all(self, kind: str) -> list[dict[str, Any]]:
        path = self.root / f"{kind}.jsonl"
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def read_execution(self, execution_id: str) -> dict[str, Any]:
        return self._find("execution", "execution_id", execution_id)

    def read_evaluation(self, evaluation_id: str) -> dict[str, Any]:
        return self._find("evaluation", "evaluation_id", evaluation_id)

    def read_evidence(self, evidence_id: str) -> dict[str, Any]:
        return self._find("evidence", "evidence_id", evidence_id)

    def _find(self, kind: str, key: str, value: str) -> dict[str, Any]:
        for record in reversed(self._read_all(kind)):
            if record.get(key) == value:
                return record
        raise PersistenceError(f"{kind}_not_found:{value}")

    def verify_linkage(self, evidence_id: str) -> dict[str, Any]:
        evidence = self.read_evidence(evidence_id)
        execution = self.read_execution(evidence["execution_id"])
        evaluation = self.read_evaluation(evidence["evaluation_id"])
        if execution["experiment_id"] != evidence["experiment_id"]:
            raise PersistenceError("experiment_link_mismatch_execution")
        if evaluation["experiment_id"] != evidence["experiment_id"]:
            raise PersistenceError("experiment_link_mismatch_evaluation")
        if evaluation["execution_id"] != evidence["execution_id"]:
            raise PersistenceError("execution_link_mismatch_evaluation")
        return {
            "status": "passed",
            "execution_id": execution["execution_id"],
            "evaluation_id": evaluation["evaluation_id"],
            "evidence_id": evidence["evidence_id"],
            "experiment_id": evidence["experiment_id"],
        }


def persist_ma_exp_001(root: str | Path) -> dict[str, Any]:
    """Persist one deterministic execution→evaluation→evidence chain."""
    registry = RecordRegistry(root)
    execution = {
        "record_type": "execution",
        "execution_id": "MA-EXP-001-EXEC-001",
        "experiment_id": "MA-EXP-001",
        "status": "passed",
        "execution_package": {
            "engine": "local-smoke",
            "adapter": "local-smoke-adapter",
            "capabilities": [
                "scene.composition", "product.dispensing",
                "product.application", "macro.detail",
                "json.compilation", "output.validation",
            ],
        },
        "output_ref": "local-smoke-output-001",
    }
    registry.write_execution(execution)

    evaluation = {
        "record_type": "evaluation",
        "evaluation_id": "MA-EXP-001-EVAL-001",
        "experiment_id": "MA-EXP-001",
        "execution_id": execution["execution_id"],
        "observations": [
            "local adapter accepted execution package",
            "deterministic smoke execution returned passed",
        ],
        "failures": [],
        "hypotheses": ["tested configuration is internally consistent"],
        "decision": "accept_as_experiment",
        "promotion_status": "provisional",
    }
    registry.write_evaluation(evaluation)

    evidence = {
        "record_type": "evidence",
        "evidence_id": "MA-EXP-001-EVID-001",
        "experiment_id": "MA-EXP-001",
        "execution_id": execution["execution_id"],
        "evaluation_id": evaluation["evaluation_id"],
        "result": "passed",
        "decision": evaluation["decision"],
        "promotion_status": evaluation["promotion_status"],
        "source": "bounded-local-runtime",
    }
    registry.write_evidence(evidence)
    return registry.verify_linkage(evidence["evidence_id"])
