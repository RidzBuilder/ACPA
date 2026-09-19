# ACPA — Repository Execution Contract v1.0

Status: DRAFT / EXECUTION GATE ARTIFACT
Authority: ACPA Architecture v0.1 LOCKED + Canonical Agent Specification v0.1 + Input/Output Contracts v0.1

## Purpose
Define the minimum explicit execution expectations for an external builder/runtime without changing ACPA architecture semantics.

## Required canonical flow
AssetManifest → ContentIntent → PatternSelection → ProductionPlan → SceneSpec → CapabilityRequirement → AdapterResolution → ExecutionPackage → EvaluationRecord → EvidenceRecord

## Required runtime surfaces
1. Application/runtime entry point.
2. Agent orchestration entry point.
3. Contract/schema validation.
4. Capability resolution.
5. Adapter boundary.
6. Execution-package compilation.
7. Output/evaluation recording.
8. Evidence persistence.
9. Deterministic health/readiness endpoint or equivalent.
10. Test command covering the golden path and failure states.

## Golden-path candidate
MA-EXP-001 — Macro Demo — 10–15 seconds:
Product Hook → Dispense → Application → Macro Proof → Benefit → Brand Closure.

The exact executable golden path remains subject to Phase B/C validation.

## Required failure states
- missing input/asset
- incomplete or ambiguous intent
- unsupported capability
- unavailable/incompatible adapter
- execution failure
- output validation failure
- human approval boundary not satisfied

## Builder constraints
- Preserve three layers: L1 Asset Intelligence, L2 Content & Production Orchestration, L3 Execution Compiler.
- Keep canonical planning vendor-neutral.
- Resolve capabilities explicitly.
- Keep provider-specific behavior behind adapters.
- Never silently invent missing brief data or unsupported capabilities.
- Experimental evidence remains provisional until promoted.
- Material architecture changes require revision/addendum and acceptance gate.

## Current conformance
The repository documents these expectations, but runtime implementation conformance is NOT YET PROVEN.
