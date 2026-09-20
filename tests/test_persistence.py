import tempfile
import unittest
from pathlib import Path

from runtime.persistence import PersistenceError, RecordRegistry, persist_ma_exp_001


class PersistenceConformanceTests(unittest.TestCase):
    def test_execution_evaluation_evidence_chain_persists_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = persist_ma_exp_001(tmp)
            self.assertEqual(result["status"], "passed")

            registry = RecordRegistry(tmp)
            execution = registry.read_execution("MA-EXP-001-EXEC-001")
            evaluation = registry.read_evaluation("MA-EXP-001-EVAL-001")
            evidence = registry.read_evidence("MA-EXP-001-EVID-001")

            self.assertEqual(execution["experiment_id"], "MA-EXP-001")
            self.assertEqual(evaluation["execution_id"], execution["execution_id"])
            self.assertEqual(evidence["evaluation_id"], evaluation["evaluation_id"])
            self.assertEqual(evidence["promotion_status"], "provisional")

            # Verify persistence is durable across registry re-instantiation.
            reloaded = RecordRegistry(Path(tmp))
            self.assertEqual(
                reloaded.verify_linkage("MA-EXP-001-EVID-001")["status"], "passed"
            )

    def test_evaluation_separates_observation_failure_hypothesis_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            registry.write_evaluation({
                "record_type": "evaluation",
                "evaluation_id": "EVAL-X",
                "experiment_id": "EXP-X",
                "execution_id": "EXEC-X",
                "observations": ["output observed"],
                "failures": ["simulated failure"],
                "hypotheses": ["adapter timeout"],
                "decision": "iterate",
            })
            record = registry.read_evaluation("EVAL-X")
            self.assertEqual(record["observations"], ["output observed"])
            self.assertEqual(record["failures"], ["simulated failure"])
            self.assertEqual(record["hypotheses"], ["adapter timeout"])
            self.assertEqual(record["decision"], "iterate")

    def test_invalid_promotion_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            with self.assertRaises(PersistenceError):
                registry.write_evidence({
                    "record_type": "evidence",
                    "evidence_id": "EVID-X",
                    "experiment_id": "EXP-X",
                    "execution_id": "EXEC-X",
                    "evaluation_id": "EVAL-X",
                    "result": "passed",
                    "decision": "accept_as_experiment",
                    "promotion_status": "unknown",
                })

    def test_broken_linkage_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            registry.write_execution({
                "record_type": "execution",
                "execution_id": "EXEC-X",
                "experiment_id": "EXP-A",
                "status": "passed",
                "execution_package": {},
            })
            registry.write_evaluation({
                "record_type": "evaluation",
                "evaluation_id": "EVAL-X",
                "experiment_id": "EXP-B",
                "execution_id": "EXEC-X",
                "observations": [],
                "decision": "blocked",
            })
            registry.write_evidence({
                "record_type": "evidence",
                "evidence_id": "EVID-X",
                "experiment_id": "EXP-B",
                "execution_id": "EXEC-X",
                "evaluation_id": "EVAL-X",
                "result": "blocked",
                "decision": "blocked",
                "promotion_status": "rejected",
            })
            with self.assertRaises(PersistenceError):
                registry.verify_linkage("EVID-X")


if __name__ == "__main__":
    unittest.main()
