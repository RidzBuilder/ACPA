import unittest

from runtime.agent_loop import run_agent_loop, run_failure_then_correction


class ACPAAgenticRuntimeLoopTests(unittest.TestCase):
    def test_golden_path_has_traceable_multi_step_loop(self):
        result = run_agent_loop(require_human_gate=False)
        self.assertEqual(result["status"], "completed")
        events = [item["event"] for item in result["trace"]]
        self.assertIn("intent.accepted", events)
        self.assertIn("plan.created", events)
        self.assertIn("capabilities.resolved", events)
        self.assertIn("execution.started", events)
        self.assertIn("execution.observed", events)
        self.assertIn("evaluation.accepted", events)
        self.assertGreaterEqual(len(events), 6)

    def test_failure_triggers_observation_and_correction(self):
        result = run_failure_then_correction()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["attempts"], 2)
        events = [item["event"] for item in result["trace"]]
        self.assertIn("correction.decided", events)
        observations = [
            item["observation"]
            for item in result["trace"]
            if item["event"] == "execution.observed"
        ]
        self.assertEqual(observations[0]["status"], "failed")
        self.assertEqual(observations[1]["status"], "passed")

    def test_human_boundary_is_explicit(self):
        result = run_agent_loop(require_human_gate=True)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["state"]["decision"], "needs_human_approval")
        self.assertFalse(result["state"]["completed"])
        self.assertEqual(result["human_boundary"], "G4 approval required before external execution/promotion")

    def test_goal_completion_is_measurable(self):
        result = run_agent_loop(require_human_gate=False)
        self.assertEqual(result["state"]["completed"], True)
        self.assertEqual(result["state"]["decision"], "accept")
        self.assertEqual(result["attempts"], 1)


if __name__ == "__main__":
    unittest.main()
