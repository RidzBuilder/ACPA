# GAP-ACPA-001 Remediation v1.0

## Objective
Establish a minimal, reproducible executable surface without changing ACPA's locked three-layer architecture.

## Implemented surface
- `runtime/acpa_runtime.py`: stdlib-only runtime.
- `health/readiness`: deterministic HTTP endpoint.
- `smoke`: controlled MA-EXP-001 execution path.
- `tests/test_runtime.py`: executable conformance/smoke tests.

## Commands
- `python3 -m unittest discover -s tests -v`
- `python3 runtime/acpa_runtime.py health`
- `python3 runtime/acpa_runtime.py smoke`
- `python3 runtime/acpa_runtime.py serve --port 8080`

## Scope boundary
This remediation proves an executable surface only. It does not by itself promote the runtime to full agentic, adapter, evidence, or Emergent conformance.

## Acceptance evidence
GitHub Actions is used to execute the test suite on push to this branch. Runtime readiness is PASS only if the resulting workflow run passes.
