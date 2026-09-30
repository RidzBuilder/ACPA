import unittest
from runtime.agent_loop import run_agent_loop, run_failure_then_correction, validate_executor_result

class ACPAAgenticRuntimeLoopTests(unittest.TestCase):
    def test_golden_path(self):
        result = run_agent_loop(require_human_gate=False)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["state"]["completed"])

    def test_failure_correction_retry(self):
        result = run_failure_then_correction()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["attempts"], 2)

    def test_human_boundary(self):
        result = run_agent_loop(require_human_gate=True)
        self.assertEqual(result["state"]["decision"], "needs_human_approval")
        self.assertFalse(result["state"]["completed"])
        self.assertNotIn("execution.started", [x["event"] for x in result["trace"]])

    def test_malformed_success_output_is_blocked(self):
        result = run_agent_loop(lambda package, attempt: {"status":"passed"},
                                max_attempts=1, require_human_gate=False)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["state"]["completed"])

    def test_output_validation_contract(self):
        self.assertEqual(validate_executor_result({"status":"passed"}),
                         ["missing_output_ref","output_validation_not_passed"])
        self.assertEqual(validate_executor_result({"status":"passed","output_ref":"o",
                         "validation":{"status":"passed"}}), [])

if __name__ == "__main__":
    unittest.main()
