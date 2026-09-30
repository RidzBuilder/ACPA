import tempfile
import unittest
from pathlib import Path
from runtime.persistence import PersistenceError, RecordRegistry, persist_ma_exp_001

class PersistenceConformanceTests(unittest.TestCase):
    def test_chain_persists_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(persist_ma_exp_001(tmp)["status"], "passed")
            registry = RecordRegistry(Path(tmp))
            evaluation = registry.read_evaluation("MA-EXP-001-EVAL-001")
            evidence = registry.read_evidence("MA-EXP-001-EVID-001")
            self.assertEqual(evaluation["execution_id"], "MA-EXP-001-EXEC-001")
            self.assertEqual(evidence["decision"], evaluation["decision"])
            self.assertEqual(evidence["promotion_status"], evaluation["promotion_status"])
            self.assertEqual(registry.verify_linkage("MA-EXP-001-EVID-001")["status"], "passed")

    def test_invalid_promotion_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            with self.assertRaises(PersistenceError):
                registry.write_evidence({"record_type":"evidence","evidence_id":"E",
                    "experiment_id":"X","execution_id":"E","evaluation_id":"V","result":"passed",
                    "decision":"accept_as_experiment","promotion_status":"unknown"})

    def test_broken_linkage_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            registry.write_execution({"record_type":"execution","execution_id":"EXEC",
                "experiment_id":"A","status":"passed","execution_package":{}})
            registry.write_evaluation({"record_type":"evaluation","evaluation_id":"EVAL",
                "experiment_id":"B","execution_id":"EXEC","observations":[],"decision":"blocked"})
            registry.write_evidence({"record_type":"evidence","evidence_id":"EVID",
                "experiment_id":"B","execution_id":"EXEC","evaluation_id":"EVAL",
                "result":"blocked","decision":"blocked","promotion_status":"rejected"})
            with self.assertRaises(PersistenceError):
                registry.verify_linkage("EVID")

    def test_contradictory_evidence_decision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = RecordRegistry(tmp)
            registry.write_execution({"record_type":"execution","execution_id":"EXEC",
                "experiment_id":"X","status":"passed","execution_package":{}})
            registry.write_evaluation({"record_type":"evaluation","evaluation_id":"EVAL",
                "experiment_id":"X","execution_id":"EXEC","observations":[],
                "decision":"blocked","promotion_status":"rejected"})
            registry.write_evidence({"record_type":"evidence","evidence_id":"EVID",
                "experiment_id":"X","execution_id":"EXEC","evaluation_id":"EVAL",
                "result":"passed","decision":"promote","promotion_status":"promoted"})
            with self.assertRaises(PersistenceError):
                registry.verify_linkage("EVID")

if __name__ == "__main__":
    unittest.main()
