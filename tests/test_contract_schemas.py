import json
import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]

def validate_subset(value,schema,path="$"):
    errors=[]
    t=schema.get("type")
    if t=="object":
        if not isinstance(value,dict): return [f"{path}:object"]
        errors += [f"{path}:missing:{k}" for k in schema.get("required",[]) if k not in value]
        if schema.get("additionalProperties") is False:
            errors += [f"{path}:additional:{k}" for k in value if k not in schema.get("properties",{})]
        for k,v in value.items():
            if k in schema.get("properties",{}): errors += validate_subset(v,schema["properties"][k],path+"."+k)
    elif t=="array":
        if not isinstance(value,list): errors.append(f"{path}:array")
        else:
            for i,v in enumerate(value): errors += validate_subset(v,schema.get("items",{}),f"{path}[{i}]")
    elif t=="string" and not isinstance(value,str): errors.append(f"{path}:string")
    elif isinstance(t,list) and "null" in t and value is not None and not isinstance(value,str): errors.append(f"{path}:string_or_null")
    if "enum" in schema and value not in schema["enum"]: errors.append(f"{path}:enum")
    return errors

class ContractSchemaTests(unittest.TestCase):
    def test_persisted_records_match_schemas(self):
        from tempfile import TemporaryDirectory
        from runtime.persistence import persist_ma_exp_001,RecordRegistry
        with TemporaryDirectory() as tmp:
            persist_ma_exp_001(tmp); r=RecordRegistry(tmp)
            pairs={"evaluation-record.schema.json":r.read_evaluation("MA-EXP-001-EVAL-001"),
                   "evidence-record.schema.json":r.read_evidence("MA-EXP-001-EVID-001")}
            for name,record in pairs.items():
                schema=json.loads((ROOT/"contracts"/name).read_text())
                self.assertEqual(validate_subset(record,schema),[],name)

    def test_adapter_resolution_schema(self):
        from runtime.capability_adapter import resolve_capability_adapter
        schema=json.loads((ROOT/"contracts"/"adapter-resolution.schema.json").read_text())
        for r in [resolve_capability_adapter(["scene.composition"]),
                  resolve_capability_adapter(["unknown.capability"]),
                  resolve_capability_adapter(["scene.composition"],engine_context="external-provider")]:
            self.assertEqual(validate_subset(r.to_contract_dict(),schema),[])

if __name__=="__main__": unittest.main()
