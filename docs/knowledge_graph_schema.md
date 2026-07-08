# Knowledge Graph Schema

The v0.4 graph uses local JSON/YAML only. It does not require Neo4j, hosted vector databases, LangChain, or external LLM APIs.

## Node Types

`Source`, `EvidenceCard`, `Dataset`, `Band`, `QAField`, `ScaleFactor`, `Operator`, `Recipe`, `Workflow`, `ValidationDemo`, `Metric`, `Rule`, `FailureCase`, `RecoveryPattern`, `Claim`, `ClaimBoundary`, `Script`, `Test`, `OutputArtifact`, `EvaluationCase`, `PlannerHint`, `ValidatorHint`.

## Edge Types

`cites_source`, `extracted_from`, `supports_claim`, `limits_claim`, `uses_dataset`, `has_band`, `has_qa_field`, `requires_scale_factor`, `uses_operator`, `requires_rule`, `has_failure_mode`, `recovers_by`, `implemented_in`, `tested_by`, `validated_by`, `reports_metric`, `depends_on`, `contradicts`, `generalizes_to`, `evaluated_by`, `derived_from`, `grounded_by`, `invalidates`, `warns_about`, `suitable_for`, `unsuitable_for`.

## Validation Rules

- Every edge endpoint must exist.
- Every node id must be stable and lowercase-ish.
- Every `EvidenceCard` node must cite a `Source`.
- Dataset facts for current API/catalog behavior must be grounded by Tier A evidence.
- `Claim` nodes need support and boundaries.
- `Golden` validation demos must link to claim boundaries.
- Public graph files must not contain private asset ids, secrets, local paths, or unpublished claims.
