# GAP-ACPA-004 — Runtime Persistence / EvaluationRecord / EvidenceRecord

## Scope
This remediation closes only the bounded persistence acceptance surface required by
the MEP. It does not claim production database durability or external-provider
evidence.

## Canonical contract trace
C5 Execution Compilation produces an ExecutionPackage.
C6 Evaluation consumes generated output/QC observations and produces EvaluationRecord.
C7 Evidence Promotion consumes EvaluationRecord and produces EvidenceRecord.

The implemented bounded chain is:

`ExecutionPackage`
→ `ExecutionRecord`
→ `EvaluationRecord`
→ `EvidenceRecord`
→ linkage verification.

## Remediation
Added `runtime/persistence.py` with a stdlib-only file-backed JSONL registry:
- explicit execution/evaluation/evidence record types;
- stable experiment/execution/evaluation/evidence identifiers;
- separate observations, failures, hypotheses and decision fields;
- explicit promotion state;
- cross-record linkage verification;
- explicit persistence errors for malformed records or broken linkage;
- deterministic MA-EXP-001 persistence smoke.

## Re-test
Test file: `tests/test_persistence.py`

Acceptance cases:
1. Execution → EvaluationRecord → EvidenceRecord persists and reloads.
2. EvaluationRecord separates observation/failure/hypothesis/decision.
3. Invalid promotion status is rejected.
4. Broken experiment linkage is rejected.

Actual result: 4/4 tests passed in an isolated local conformance run (0 failed). A fresh RecordRegistry instance reloaded the JSONL records and linkage verification returned `passed`.

## Evidence maturity
- E1: contract/schema design.
- E2: implementation in canonical execution branch.
- E3: local runtime execution of persistence tests.
- E4: persisted records and linkage trace from MA-EXP-001.
- E5: reproducible conformance test using a temporary persistence store.

## Boundaries
This does not prove:
- production database durability;
- distributed consistency;
- external engine execution;
- Emergent compatibility;
- submission readiness.

## Gate
GAP-ACPA-004 may be CLOSED only if the four persistence conformance tests pass
and a fresh registry instance can reload and verify the persisted chain.
Gate result: PASS for the bounded acceptance scope. GAP-ACPA-004 is CLOSED (bounded).
