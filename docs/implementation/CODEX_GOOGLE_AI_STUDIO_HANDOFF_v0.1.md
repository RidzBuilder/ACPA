# ACPA — Codex / Google AI Studio Handoff v0.1

## Implementation order
1. Read Architecture Specification v0.1.
2. Read Architecture Acceptance & LOCK v0.1.
3. Read Canonical Agent Specification.
4. Implement contracts under contracts/.
5. Preserve the three layers.
6. Implement prompt specifications.
7. Implement capability and adapter resolution.
8. Implement validation and state transitions.
9. Implement evidence persistence.
10. Run MA-EXP-001 as the first controlled test.

## Non-negotiable
The implementation host must not infer missing architecture. Ambiguity becomes needs_review.

## Builder neutrality
Codex, Google AI Studio or another host may differ internally, but canonical contracts and governance remain compatible.

## Definition of done
Asset → Intent → Pattern → Plan → Capability Resolution → Adapter → Execution Package → Output → Evaluation → Evidence is traceable end-to-end.
