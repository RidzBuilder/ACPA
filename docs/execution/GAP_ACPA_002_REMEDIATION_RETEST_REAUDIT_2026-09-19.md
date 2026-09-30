# GAP-ACPA-002 — Agentic Runtime Loop Remediation & Evidence

Date: 2026-09-19
Branch: `execution/mep-2026-09-19`
Scope: bounded remediation of GAP-ACPA-002 only.

## Objective

Prove, at runtime, a bounded agentic loop consistent with the locked ACPA
orchestration semantics:

`Intent → Plan → Capability Resolution → Execution → Observation → Evaluation → Correction/Next Decision`

The remediation must not claim production engine execution, persistent evidence
storage, or full AOS behavior.

## Implementation

Added `runtime/agent_loop.py`.

The runtime exposes:

1. explicit intent and measurable success criteria;
2. vendor-neutral production plan construction;
3. capability resolution before execution;
4. bounded execution attempts;
5. observable execution result;
6. evaluation decision;
7. correction/retry after failure;
8. measurable completion state;
9. explicit G4 human approval boundary.

The executor is injected through a narrow function boundary so the agent loop is
not coupled to a specific external provider.

## Behavioral tests

### Test A — Golden path

Observed event sequence:

1. `intent.accepted`
2. `plan.created`
3. `capabilities.resolved`
4. `execution.started`
5. `execution.observed`
6. `evaluation.accepted`

Result:
- status: `completed`
- attempts: 1
- decision: `accept`
- completed: true

### Test B — Failure → observation → correction → retry → success

Injected first-attempt failure:
`simulated_adapter_timeout`

Observed event sequence:

1. `intent.accepted`
2. `plan.created`
3. `capabilities.resolved`
4. `execution.started`
5. `execution.observed` = failed
6. `correction.decided` = retry_execution
7. `execution.started`
8. `execution.observed` = passed
9. `evaluation.accepted`

Result:
- status: `completed`
- attempts: 2
- first observation: failed
- second observation: passed
- correction decision was explicitly recorded

### Test C — Human boundary

With the human gate enabled, a technically successful execution does not
become an unrestricted final completion.

Result:
- status: `passed` (gate state reached)
- decision: `needs_human_approval`
- completed: false
- gate: G4

This preserves the canonical human boundary before external execution/promotion.

## Re-test

Local isolated behavioral assertions executed against the committed runtime
semantics:

- 4 agent-loop behavioral tests: 4 passed, 0 failed.
- Golden path: PASS.
- Failure/correction/retry: PASS.
- Human boundary: PASS.
- Measurable goal completion: PASS.

The existing GAP-ACPA-001 runtime tests remain part of the repository test suite.

## Evidence hierarchy

- E2: executable implementation exists in repository.
- E3: runtime behavioral execution reproduced locally.
- E4: trace contains ordered state transitions, observations, decision and
  correction evidence.
- E5: deterministic test scenarios are reproducible from repository commands.

## Boundary / non-claims

This remediation does NOT prove:

- production video/image engine execution;
- external provider reliability;
- persistent EvaluationRecord/EvidenceRecord storage;
- complete adapter ecosystem;
- Emergent compatibility;
- full AOS-level autonomy;
- autonomous authority beyond the explicit human gate.

## Gate recommendation

GAP-ACPA-002 is eligible for closure only for the bounded acceptance scope
defined above. The next dependency remains GAP-ACPA-003.
