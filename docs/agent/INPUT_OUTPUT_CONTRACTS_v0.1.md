# ACPA — Input / Output Contracts v0.1

## C1 Asset Intake
Input: supplied asset references/files and labels.
Output: AssetManifest with asset_id, asset_type, role, source, status and constraints.

## C2 Content Intent
Input: approved brief when available; otherwise explicitly labeled experimental intent; platform, duration, family hint, CTA and constraints.
Output: ContentIntent. Missing brief information must not be invented.

## C3 Orchestration
Input: AssetManifest + ContentIntent + evidence/pattern references.
Output: vendor-neutral ProductionPlan.

## C4 Capability Resolution
Input: ProductionPlan + Capability Registry + engine context.
Output: CapabilityResolution + AdapterResolution. Each requirement is supported, unsupported, conditional or needs_review.

## C5 Execution Compilation
Input: approved ProductionPlan + accepted capability resolution + adapter.
Output: ExecutionPackage containing engine, adapter, capabilities, compiled payload and validation.

## C6 Evaluation
Input: generated output + QC observations.
Output: EvaluationRecord separating observation, failure, hypothesis and decision.

## C7 Evidence Promotion
Input: EvaluationRecord.
Output: EvidenceRecord with promotion status: unreviewed, provisional, promoted or rejected.

## State model
draft → needs_review → approved → compiled → executed → evaluated → promoted/rejected
