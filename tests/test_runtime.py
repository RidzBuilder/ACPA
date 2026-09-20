import unittest
from runtime.acpa_runtime import health, validate_plan, resolve_capabilities, compile_execution, smoke_execute

class ACPAExecutableSurfaceTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(health()["status"], "ready")

    def test_plan_validation(self):
        self.assertEqual(validate_plan({"content_family":"Macro Demo","pattern_id":"p","scenes":[{"scene_id":"S01","purpose":"Hook"}]}), [])

    def test_unsupported_capability_is_explicit(self):
        r=resolve_capabilities(["unknown.capability"])
        self.assertEqual(r["requirements"][0]["status"], "unsupported")

    def test_compilation_blocks_unsupported(self):
        r=compile_execution({"content_family":"x","pattern_id":"p","scenes":[{"scene_id":"S","purpose":"x"}]}, resolve_capabilities(["unknown.capability"]))
        self.assertEqual(r["status"], "blocked")

    def test_ma_exp_001_smoke(self):
        r=smoke_execute()
        self.assertEqual(r["status"], "passed")
        self.assertEqual(r["experiment_id"], "MA-EXP-001")

if __name__=="__main__":
    unittest.main()
