#!/usr/bin/env python3
"""Minimal ACPA executable surface for MEP remediation.

Stdlib-only. This runtime is intentionally bounded: it exposes health/readiness,
contract-shaped plan validation, capability resolution, local adapter compilation,
and a deterministic smoke execution path. It does not replace external engines.
"""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

CAPABILITIES = {
    "scene.composition", "camera.motion", "product.interaction",
    "product.dispensing", "product.application", "macro.detail",
    "json.compilation", "output.validation"
}

def health() -> dict[str, Any]:
    return {"status": "ready", "service": "acpa-runtime", "version": "0.1"}

def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors=[]
    for key in ("content_family","pattern_id","scenes"):
        if key not in plan: errors.append(f"missing:{key}")
    if not isinstance(plan.get("scenes"), list) or not plan.get("scenes"):
        errors.append("invalid:scenes")
    return errors

def resolve_capabilities(required: list[str]) -> dict[str, Any]:
    items=[]
    for capability_id in required:
        status="supported" if capability_id in CAPABILITIES else "unsupported"
        items.append({"capability_id": capability_id, "status": status})
    return {"resolution_id":"local-smoke-resolution-001","requirements":items}

def compile_execution(plan: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    unsupported=[x["capability_id"] for x in resolution["requirements"] if x["status"]=="unsupported"]
    if unsupported:
        return {"status":"blocked","reason":"unsupported_capabilities","unsupported_capabilities":unsupported}
    return {
        "status":"compiled",
        "engine":"local-smoke",
        "adapter":"local-smoke-adapter",
        "capabilities":[x["capability_id"] for x in resolution["requirements"]],
        "payload":{"content_family":plan["content_family"],"pattern_id":plan["pattern_id"],"scenes":plan["scenes"]},
        "validation":{"status":"passed"}
    }

def smoke_execute() -> dict[str, Any]:
    plan={
        "content_family":"Macro Demo",
        "pattern_id":"macro-demo-v0.1",
        "grammar":"ATTENTION → PRODUCT → HUMAN/CONTEXT → PROOF/DEMONSTRATION → BENEFIT/CLAIM → ACTION → BRAND",
        "scenes":[
            {"scene_id":"S01","purpose":"Product Hook","asset_ids":["product_primary"],"duration_seconds":2},
            {"scene_id":"S02","purpose":"Dispense","asset_ids":["product_primary","hand_reference"],"duration_seconds":2},
            {"scene_id":"S03","purpose":"Application","asset_ids":["product_primary","hand_reference","skin_reference"],"duration_seconds":3},
            {"scene_id":"S04","purpose":"Macro Proof","asset_ids":["skin_reference","product_primary"],"duration_seconds":3},
            {"scene_id":"S05","purpose":"Benefit","asset_ids":["product_primary","skin_reference"],"duration_seconds":2},
            {"scene_id":"S06","purpose":"Brand Closure","asset_ids":["product_primary"],"duration_seconds":2},
        ]
    }
    errors=validate_plan(plan)
    if errors: return {"status":"failed","stage":"validation","errors":errors}
    resolution=resolve_capabilities(["scene.composition","product.dispensing","product.application","macro.detail","json.compilation","output.validation"])
    package=compile_execution(plan,resolution)
    if package["status"]!="compiled": return {"status":"failed","stage":"compilation","package":package}
    return {"status":"passed","experiment_id":"MA-EXP-001","execution_package":package,"evaluation":{"decision":"accept_as_experiment","promotion_status":"provisional"}}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/health","/readiness"):
            self.send_response(404); self.end_headers(); return
        body=json.dumps(health()).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_): pass

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["health","smoke","serve"])
    p.add_argument("--port",type=int,default=8080)
    a=p.parse_args()
    if a.command=="health": print(json.dumps(health()))
    elif a.command=="smoke": print(json.dumps(smoke_execute(),indent=2))
    else:
        HTTPServer(("0.0.0.0",a.port),Handler).serve_forever()
