# GAP-ACPA-003 — Capability Resolver + Adapter Execution

Date: 2026-09-19
Branch: `execution/mep-2026-09-19`
Scope: bounded remediation of GAP-ACPA-003 only.

## 1. Root cause

The canonical contracts and capability registry defined the boundary, but the
runtime previously exposed only a simple capability membership check and local
compilation. It did not explicitly model the complete bounded resolution state:

`ProductionPlan → CapabilityRequirement → CapabilityResolution → AdapterResolution → ExecutionPackage → Adapter Execution`

It also did not distinguish an unsupported capability from a capability that
requires review under an unimplemented engine context.

## 2. Remediation

Added:

- `runtime/capability_adapter.py`
- `tests/test_capability_adapter.py`

The implementation introduces:

### Capability requirement

Each requested capability receives an explicit state:

- `supported`
- `unsupported`
- `needs_review`

### Adapter resolution

A fully supported local request resolves to:

- resolution status: `resolved`
- adapter: `local-smoke-adapter`

Unsupported requirements do not receive an adapter.

Unimplemented engine contexts produce `needs_review` and do not silently
select the local adapter.

### Adapter boundary

`LocalSmokeAdapter` is isolated behind an adapter interface. The canonical
plan remains provider-neutral.

The adapter explicitly rejects a package whose selected adapter does not match
the adapter being invoked.

### Compilation gate

An ExecutionPackage is compiled only when the capability/adapter resolution
status is `resolved`.

Unsupported and `needs_review` resolutions are blocked.

## 3. Acceptance tests

### A — Supported capability resolution

Input:
`scene.composition`, `product.application`,
`output.validation`

Expected:
`resolved → local-smoke-adapter`

Result: PASS.

### B — Unsupported capability

Input:
`unknown.capability`

Expected:
- resolution = `unsupported`
- no adapter selected
- compilation = `blocked`

Result: PASS.

### C — Unimplemented engine context

Input:
supported capability + `external-provider` context.

Expected:
- resolution = `needs_review`
- no adapter selected
- compilation = `blocked`

Result: PASS.

### D — Adapter execution

Resolved package is passed to `local-smoke-adapter`.

Expected:
- execution = `passed`
- adapter identity preserved.

Result: PASS.

### E — Adapter mismatch

A package identifying `wrong-adapter` is passed to
`local-smoke-adapter`.

Expected:
- execution = `rejected`
- reason = `adapter_mismatch`

Result: PASS.

## 4. Deterministic conformance smoke

`conformance_smoke()` verifies in one execution:

1. supported resolution;
2. adapter selection;
3. package compilation;
4. adapter execution;
5. unsupported rejection;
6. needs-review gating.

Observed result:

```
status      = passed
resolution  = resolved
adapter     = local-smoke-adapter
execution   = passed
unsupported = unsupported
review      = needs_review
```

## 5. Re-test evidence

Local isolated execution:

- Capability/adapter test suite: **5/5 passed**
- Deterministic conformance smoke: **passed**
- Return code: **0**

The unrelated Python environment spreadsheet warmup warning did not affect the
test result; the unittest process completed with all tests passing.

## 6. Evidence hierarchy

- E2: executable resolver and adapter implementation — PASS.
- E3: resolver/adapter behavior executed locally — PASS.
- E4: explicit resolution, blocking and adapter execution outcomes observed — PASS.
- E5: deterministic test scenarios and conformance smoke reproducible — PASS.

## 7. Boundary / non-claims

This remediation does NOT prove:

- production external provider execution;
- real image/video generation;
- complete capability coverage for every registry capability;
- multi-provider adapter interchangeability;
- persistence of EvaluationRecord/EvidenceRecord;
- Emergent compatibility;
- production-scale reliability.

The local adapter is evidence infrastructure for the bounded execution contract,
not a claim that an external production engine has been integrated.

## 8. Gate result

GAP-ACPA-003 is **PASS — bounded remediation**.

The next dependency is GAP-ACPA-004:
Runtime Persistence / EvaluationRecord / EvidenceRecord loop.
