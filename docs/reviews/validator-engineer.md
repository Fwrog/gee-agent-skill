# Validator Engineer Review: Semantic Validator and Error Taxonomy

Status: partially implemented; good direction, but not yet a complete structured taxonomy contract.

## What Is In Place

- `Finding` already carries `severity`, `code`, `message`, `line`, `hint`, and optional `category`; `ValidationReport.to_dict()` exposes `semantic_rulesets` and per-finding `category`.
- `errors.py` defines the target categories with `likely_cause`, `retryable`, `suggested_fix`, and `user_action_required`: `AUTH_ERROR`, `PROJECT_ERROR`, `DATASET_NOT_FOUND`, `BAND_NOT_FOUND`, `EMPTY_COLLECTION`, `GEOMETRY_ERROR`, `REDUCER_SCALE_ERROR`, `EXPORT_TASK_ERROR`, `QUOTA_OR_TIMEOUT`, `CLIENT_SERVER_MISUSE`, plus fallback categories.
- CLI validation output now prints categories when present, and live-run exception handling uses `classify_exception()` to return the structured error payload.
- Existing targeted tests pass after rerun: `python -m pytest tests\test_validation.py tests\test_execution_boundaries.py -q -p no:cacheprovider`.

## Required Contract

Each validator finding that can block or guide user action should serialize a stable envelope:

```json
{
  "severity": "error|warning|info",
  "code": "stable-rule-code",
  "category": "BAND_NOT_FOUND",
  "message": "human-readable failure",
  "line": 42,
  "rule_id": "sentinel2_ndvi_monthly_zonal.s2-ndvi-bands",
  "ruleset": "sentinel2_ndvi_monthly_zonal",
  "retryable": false,
  "likely_cause": "The script selects a band not present in the chosen dataset.",
  "suggested_fix": "Check dataset bands and update the workflow template or task context."
}
```

`hint` can remain as backward-compatible display text, but `suggested_fix` should be the machine-readable field. `retryable` should mean same request can be retried after external state changes; source edits, task-context fixes, or template fixes should normally be `retryable: false` even when the user can rerun after changing input.

## Review Findings

- Semantic findings are not yet taxonomy-complete. `semantic.py` creates most errors through `_require()` without `category`, `retryable`, `suggested_fix`, `ruleset`, or `rule_id`, so important failures such as `s2-ndvi-bands`, `s2-scale`, `s2-region-filter`, `export-description`, and `csv-format` lose the structured taxonomy in JSON output.
- Category mapping should be explicit per rule, not inferred from prose. Suggested mappings: missing or wrong dataset id -> `DATASET_NOT_FOUND`; wrong/missing bands -> `BAND_NOT_FOUND`; empty/over-filtered date or cloud policy risk -> `EMPTY_COLLECTION`; missing region or invalid AOI -> `GEOMETRY_ERROR`; scale/CRS/tileScale/maxPixels issues -> `REDUCER_SCALE_ERROR`; export call/description/selectors/file format/task status issues -> `EXPORT_TASK_ERROR`; excessive `getInfo()` or client-side fetches -> `CLIENT_SERVER_MISUSE`.
- Static validator rules are still text-fragile. Checks such as `"scale" in text`, `"region=" in text`, exact `"B8"`/`"B4"` quoting, and comment/string matches can create false positives or false negatives. Prefer AST-backed call/keyword extraction for `filterDate`, `filterBounds`, `select`, `normalizedDifference`, reducer/export kwargs, and `getInfo()`.
- Runtime error classification is useful but needs ambiguity fixtures. Keyword order can misclassify mixed messages such as permission-denied assets, project-disabled API errors, export quota failures, and pixel-limit reducer failures. The taxonomy should preserve `original`, raw message, category, retryability, and suggested fix in run traces.
- `PROJECT_ERROR`, `DATASET_NOT_FOUND`, `EMPTY_COLLECTION`, `EXPORT_TASK_ERROR`, and `QUOTA_OR_TIMEOUT` are mostly runtime concepts today. The validator should still emit preflight warnings or errors when scripts omit a project gate, use unknown dataset ids against the local dataset registry, risk empty collections, lack export task metadata, or omit pixel/quota controls.

## Regression Tests To Add

- Schema tests: every `error` finding has `category`, `retryable`, `suggested_fix`, `likely_cause`, `rule_id`, and stable JSON keys; warnings that map to user action should follow the same contract.
- Semantic negative fixtures: Sentinel-2 wrong band, missing cloud mask, no monthly aggregation, missing `image_count`, no selectors; Landsat missing `ST_B10` scale/offset or `QA_PIXEL`; Sentinel-1 missing IW/polarization/before-after/change metric; CSV export missing `fileFormat`, `description`, or `selectors`.
- Taxonomy mapping tests for all requested categories: `AUTH_ERROR`, `PROJECT_ERROR`, `DATASET_NOT_FOUND`, `BAND_NOT_FOUND`, `EMPTY_COLLECTION`, `GEOMETRY_ERROR`, `REDUCER_SCALE_ERROR`, `EXPORT_TASK_ERROR`, `QUOTA_OR_TIMEOUT`, and `CLIENT_SERVER_MISUSE`.
- Classifier tests with realistic Earth Engine exception strings, including ambiguous messages, to lock retryability and suggested fixes.
- CLI JSON tests for `gee-skill validate --json --semantic-rules ...` proving categories and suggested fixes survive serialization.
- Non-regression tests for false positives: comments containing `scale=`, string literals containing `region=`, single-quoted band names, band constants, and generated templates that should still pass.

## Acceptance Bar

The upgrade is ready when validator JSON and run-trace error JSON use the same taxonomy fields, every semantic rule declares its category and suggested fix, the CLI can print concise hints without dropping structured fields, and offline tests cover both happy-path templates and category-specific negative fixtures without importing or initializing live Earth Engine dependencies.
