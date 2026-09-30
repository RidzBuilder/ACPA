import json
import unittest
from pathlib import Path
from runtime.capability_adapter import LocalSmokeAdapter, compile_for_adapter, execute_with_adapter, resolve_capability_adapter

PLAN={"content_family":"Macro Demo","pattern_id":"macro-demo-v0.1","scenes":[{"scene_id":"S01","purpose":"Product Hook"}]}

class CapabilityAdapterTests(unittest.TestCase):
    def test_supported_resolves(self):
        r=resolve_capability_adapter(["scene.composition"])
        self.assertEqual(r.status,"resolved")
        self.assertEqual(r.adapter_id,"local-smoke-adapter")

    def test_unsupported_blocks(self):
        r=resolve_capability_adapter(["unknown.capability"])
        self.assertEqual(r.status,"blocked")
        self.assertIsNone(r.adapter_id)
        self.assertEqual(compile_for_adapter(PLAN,r)["status"],"blocked")

    def test_external_context_requires_review(self):
        r=resolve_capability_adapter(["scene.composition"],engine_context="external-provider")
        self.assertEqual(r.status,"needs_review")
        self.assertIsNone(r.adapter_id)

    def test_selected_adapter_executes(self):
        r=resolve_capability_adapter(["scene.composition"])
        result=execute_with_adapter(compile_for_adapter(PLAN,r))
        self.assertEqual(result["status"],"passed")
        self.assertEqual(result["validation"]["status"],"passed")

    def test_uncompiled_package_is_rejected(self):
        result=execute_with_adapter({"adapter":"local-smoke-adapter"},LocalSmokeAdapter())
        self.assertEqual(result["status"],"rejected")
        self.assertEqual(result["reason"],"execution_package_not_compiled")

    def test_mismatch_rejected(self):
        result=execute_with_adapter({"status":"compiled","adapter":"wrong-adapter"},LocalSmokeAdapter())
        self.assertEqual(result["status"],"rejected")

    def test_contract_shape(self):
        schema=json.loads(Path("contracts/adapter-resolution.schema.json").read_text())
        for r in [resolve_capability_adapter(["scene.composition"]),
                  resolve_capability_adapter(["unknown.capability"]),
                  resolve_capability_adapter(["scene.composition"],engine_context="external-provider")]:
            record=r.to_contract_dict()
            self.assertEqual(set(record),set(schema["properties"]))
            self.assertIn(record["status"],schema["properties"]["status"]["enum"])

if __name__=="__main__":
    unittest.main()
