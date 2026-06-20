# Evaluation And RAG Design Notes

source_id: gee-eval-rag-notes
source_type: research-note
publisher: gee-agent-skill
url: https://arxiv.org/abs/2412.05587
retrieved_at: 2026-06-21
primary_status: non-canonical
risk_level: medium

## Use Research Notes Carefully

GEE-OPs and AutoGEEval++ are useful for designing operator-aware retrieval, task taxonomies, and evaluation cases. They are not canonical API documentation and should not override Google Earth Engine guides, API references, or Data Catalog entries.

For focused notes, read:

- `research/gee-ops-operator-kb.md` when designing operator-chain metadata and retrieval prompts.
- `research/autogeeval-plus-evaluation.md` when designing unit, combo, theme, boundary, and error taxonomy tests.
- `operator-chains/sentinel2-ndvi-monthly-zonal.md` when planning Sentinel-2 monthly NDVI zonal CSV workflows.
- `failure-cases/gee-runtime-errors.md` when classifying validation or live execution failures.

## Retrieval Metadata

Useful metadata fields include `source_id`, `title`, `url`, `publisher`, `source_type`, `primary_status`, `retrieved_at`, `dataset_id`, `method_name`, `task_domain`, `cloud_mask_method`, `reducer_type`, `export_target`, `quota_risk`, `auth_requirement`, `known_caveats`, and `risk_level`.

## Evaluation Tasks

Evaluation should include offline tasks for retrieval accuracy, template rendering, static validation, dry execution boundaries, and export monitoring mocks. Live Earth Engine tests should be opt-in.
