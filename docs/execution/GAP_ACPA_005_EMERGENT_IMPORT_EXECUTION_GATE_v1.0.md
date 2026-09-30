# GAP-ACPA-005 — Emergent Import / Build Compatibility — Execution Gate

## Entry condition
GAP-ACPA-004 is CLOSED for its bounded acceptance scope:
ExecutionRecord → EvaluationRecord → EvidenceRecord persistence is implemented and
reproducibly tested.

## Objective
Perform controlled import of the canonical ACPA execution branch into Emergent,
then verify build, preview/start, and preservation of the canonical golden-path
semantics.

## Current status
**OPEN — READY FOR CONTROLLED EXTERNAL EXECUTION**

This repository-side gate is ready. Actual Emergent import/build/run evidence is
not claimed from GitHub-only inspection.

## Required sequence
1. Connect GitHub in Emergent.
2. Pull repository RidzBuilder/ACPA.
3. Select branch execution/mep-2026-09-19.
4. Record Emergent interpretation of the repository and generated project structure.
5. Build/resolve dependencies.
6. Start Preview.
7. Verify runtime health.
8. Execute the ACPA golden path:
   Asset/intent → plan → capability resolution → adapter → execution →
   observation → evaluation → evidence.
9. Verify persistence/evidence behavior in the imported runtime.
10. Capture screenshots/logs/URLs/commit references.
11. Compare expected contract semantics against actual behavior.
12. Re-test failures if any.
13. Re-audit and either CLOSE or REOPEN GAP-005.

## Acceptance criteria
- Import completes from the specified branch.
- Build completes without unresolved required dependencies.
- Preview starts and remains operational.
- Canonical golden-path semantics are preserved.
- Agentic loop remains observable.
- Capability/adapter boundary remains explicit.
- EvaluationRecord and EvidenceRecord remain linked to execution identity.
- Any unsupported external engine behavior is explicit rather than silently mocked.
- Evidence is reproducible and tied to the imported commit.

## Evidence maturity target
E3 Runtime execution + E4 Behavioral trace. E5 reproducible conformance is preferred.

## Non-negotiable boundary
A successful import/build is not by itself proof of agentic behavior.
A deployed URL is not by itself proof of conformance.
GAP-005 can close only from observed Emergent runtime evidence.

## External platform reference
Emergent's current GitHub integration documentation states that an existing
repository can be pulled into an Emergent workspace by selecting the GitHub
integration and choosing the repository and branch. The same documentation
describes Preview as the testing environment before deployment.
