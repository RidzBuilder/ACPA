# ACPA PR #1 Forensic Audit — GAP-ACPA-004

Date: 2026-09-27
Repository: RidzBuilder/ACPA
PR: #1 — MEP persistence remediation: GAP-ACPA-004
Base: main @ bcc03b6d18378776ec6aac3fe12759a6ae6c3587
Head audited: execution/mep-2026-09-19 @ b8ad58b68f06e27c5e77d1b76fe19c7f1a966877

## 1. Evidence-backed baseline
- PR state: OPEN; not merged.
- Branch comparison: 27 commits ahead, 0 behind main.
- PR reports 19 changed files, +1,529 lines.
- Combined commit statuses for audited HEAD: no status entries returned.
- PR-triggered workflow runs for audited HEAD: none returned.
- Therefore GitHub-hosted CI is NOT VERIFIED. Do not represent local test claims in PR docs as a passing hosted workflow.
- This audit did not modify main and did not merge the PR.

## 2. Blocking findings observed in review and source inspection

### AUD-004-01 — Evidence/evaluation decision contradiction
RecordRegistry.verify_linkage checks IDs and experiment IDs only. It does not require evidence.decision and evidence.promotion_status to agree with the referenced evaluation. Contradictory evidence may verify.
Required remediation: enforce consistency between evaluation decision/promotion status and evidence decision/promotion status; add negative tests.

### AUD-004-02 — Executor output is accepted without output validation
run_agent_loop treats any executor dictionary with status=passed as success, even without a nonempty output_ref or validation evidence.
Required remediation: validate output reference and required output-validation fields before accepting execution; malformed outputs must fail/enter correction or blocked state. Add adversarial tests.

### AUD-004-03 — EvaluationRecord schema omits execution_id
Runtime persistence requires and writes execution_id, while contracts/evaluation-record.schema.json forbids undeclared fields due to additionalProperties=false.
Required remediation: align canonical schema and runtime record shape; add schema conformance tests for persisted records.

### AUD-004-04 — AdapterResolution does not match canonical schema
Runtime resolution returns status=unsupported and extra fields, while canonical schema requires engine_id and string adapter_id, allows blocked rather than unsupported, and forbids undeclared fields.
Required remediation: define one canonical serialization/contract shape for resolved, blocked, and needs_review states; add schema conformance tests for each state.

### AUD-004-05 — Agent-loop CLI import context
python runtime/agent_loop.py uses a relative import and lacks package context.
Required remediation: provide a documented executable module/CLI entry point and exercise it in CI.

### AUD-004-06 — CI coverage is incomplete / hosted run absent
Current workflow runs unittest discovery, health, and smoke, but the audited HEAD has no GitHub workflow run or status evidence returned. It does not explicitly run the agent-loop CLI or schema conformance checks.
Required remediation: extend CI to cover all new conformance paths and obtain a successful GitHub Actions run on the final PR HEAD.

## 3. Gate decision
GAP-ACPA-004: BLOCKED pending remediation of AUD-004-01 through AUD-004-06, tests against committed code, and successful hosted CI evidence.
No merge authorization is inferred from this audit. Keep main unchanged. A bounded local file-backed persistence result must not be described as production database durability, external-provider execution, or Emergent compatibility.

## 4. Required sequence
1. Remediate evaluation/evidence consistency.
2. Validate executor output before success.
3. Align EvaluationRecord schema and persisted shape.
4. Align AdapterResolution schema and serialized states.
5. Provide runnable agent-loop CLI.
6. Extend CI for tests, schema validation, health, smoke, and CLI.
7. Run full suite against clean checkout and capture exact results.
8. Verify GitHub Actions success on final PR HEAD.
9. Re-audit each acceptance criterion and only then consider merge eligibility.