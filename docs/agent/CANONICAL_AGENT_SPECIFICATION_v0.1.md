# ACPA — Canonical Agent Specification v0.1

**Status:** Implementation-ready specification
**Authority:** Architecture v0.1 LOCKED

## Mission
ACPA converts evidence, client/reference assets and approved content intent into a traceable canonical production plan and, only after capability and adapter resolution, an engine-specific Execution Package.

## Layers
### L1 — Asset Intelligence
Identifies asset type, role, readiness, constraints and reference relationships. Output: AssetManifest.

### L2 — Content & Production Orchestration
Selects content family/pattern and constructs production grammar, scenes, asset mapping, visual direction, copy/CTA and constraints. Output: ProductionPlan. Must remain vendor-neutral.

### L3 — Execution Compiler
Resolves capabilities, selects adapter, compiles engine-specific payload and validates it. Must not silently change creative intent.

## Canonical chain
AssetManifest → ContentIntent → PatternSelection → ProductionPlan → SceneSpec → CapabilityRequirement → AdapterResolution → ExecutionPackage → EvaluationRecord → EvidenceRecord.

## Invariants
- Evidence-derived knowledge remains distinguishable from inference.
- Client-specific observations do not become universal rules automatically.
- Unsupported capabilities are explicit rejection/block states.
- Every scene traces to intent and assets.
- Every execution package identifies engine and adapter.
- Every output traces to an experiment and evaluation.
- Material architecture changes require revision/addendum and acceptance gate.

## Human gates
G1 Asset readiness → G2 pattern/family → G3 canonical plan → G4 execution package → G5 output QC → G6 evidence promotion.

## First domain
Mutiara Ayu Skincare is the first evidence domain, not the architectural boundary.

## First experiment
MA-EXP-001 — Macro Demo — 10–15 seconds.
Product Hook → Dispense → Application → Macro Proof → Benefit → Brand Closure.

## Failure behavior
Return structured blocked, needs_review or rejected states when required inputs, capabilities, constraints or approvals are missing.
