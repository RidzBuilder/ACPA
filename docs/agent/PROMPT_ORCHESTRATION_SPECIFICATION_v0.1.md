# ACPA — Prompt / Orchestration Specification v0.1

## Purpose
Define deterministic agent responsibilities for Codex, Google AI Studio or another implementation host. Prompts are implementation artifacts; canonical contracts remain authoritative.

## Orchestration
1. Load locked architecture and governance.
2. Ingest inputs.
3. Validate completeness.
4. Build AssetManifest.
5. Build ContentIntent without inventing missing brief data.
6. Retrieve evidence and pattern references.
7. Select provisional family/pattern.
8. Build vendor-neutral ProductionPlan.
9. Human approval G3.
10. Resolve capabilities explicitly.
11. Select adapter.
12. Compile ExecutionPackage.
13. Validate package.
14. Human approval G4.
15. Execute externally.
16. Evaluate output.
17. Record evidence.
18. Promote only when evidence supports promotion.

## Agent roles
Asset Intelligence Agent: asset classification/readiness only.
Content Orchestrator Agent: intent + evidence → ProductionPlan.
Execution Compiler Agent: approved ProductionPlan → engine-specific package.
Evaluation Agent: output → structured observations/evidence.

## Prompt construction order
Context → Authority → Inputs → Task → Constraints → Output schema → Validation → Failure states.

## Anti-drift
Do not bypass layers, invent hidden client requirements, mix engine syntax into canonical planning, or promote experimental patterns automatically.

## Execution JSON principle
Execution JSON is a compiled artifact, not the architecture source of truth.
