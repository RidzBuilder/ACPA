import unittest

from runtime.capability_adapter import (
    LocalSmokeAdapter,
    compile_for_adapter,
    execute_with_adapter,
    resolve_capability_adapter,
)


PLAN = {
    "content_family": "Macro Demo",
    "pattern_id": "macro-demo-v0.1",
    "scenes": [{"scene_id": "S01", "purpose": "Product Hook"}],
}


class CapabilityAdapterTests(unittest.TestCase):
    def test_supported_capabilities_resolve_to_adapter(self):
        r = resolve_capability_adapter(
            ["scene.composition", "product.application", "output.validation"]
        )
        self.assertEqual(r.status, "resolved")
        self.assertEqual(r.adapter_id, "local-smoke-adapter")
        self.assertEqual([x.status for x in r.requirements], ["supported"] * 3)

    def test_unsupported_capability_is_explicit_and_blocks(self):
        r = resolve_capability_adapter(["unknown.capability"])
        self.assertEqual(r.status, "unsupported")
        self.assertIsNone(r.adapter_id)
        self.assertEqual(r.unresolved, ("unknown.capability",))
        package = compile_for_adapter(PLAN, r)
        self.assertEqual(package["status"], "blocked")
        self.assertEqual(package["reason"], "unsupported")

    def test_non_local_engine_context_requires_review(self):
        r = resolve_capability_adapter(
            ["scene.composition"], engine_context="external-provider"
        )
        self.assertEqual(r.status, "needs_review")
        self.assertIsNone(r.adapter_id)
        self.assertEqual(r.needs_review, ("scene.composition",))
        self.assertEqual(compile_for_adapter(PLAN, r)["status"], "blocked")

    def test_resolved_package_executes_through_selected_adapter(self):
        r = resolve_capability_adapter(["scene.composition"])
        package = compile_for_adapter(PLAN, r)
        self.assertEqual(package["adapter"], "local-smoke-adapter")
        result = execute_with_adapter(package)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["adapter_id"], "local-smoke-adapter")

    def test_adapter_mismatch_is_rejected(self):
        adapter = LocalSmokeAdapter()
        package = {
            "status": "compiled",
            "engine": "local-smoke",
            "adapter": "wrong-adapter",
        }
        result = execute_with_adapter(package, adapter)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "adapter_mismatch")


if __name__ == "__main__":
    unittest.main()
