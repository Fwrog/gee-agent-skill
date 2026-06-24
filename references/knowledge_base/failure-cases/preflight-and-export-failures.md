# Failure Cards: Preflight And Export Failures

source_id: failure-preflight-export-catalog
source_type: failure-catalog
publisher: gee-agent-skill
source_url: https://developers.google.com/earth-engine/guides/debugging; https://developers.google.com/earth-engine/guides/usage; https://developers.google.com/earth-engine/guides/auth; https://developers.google.com/earth-engine/guides/exporting
last_checked: 2026-06-24
primary_status: derived-from-official-docs
risk_level: medium

## Empty Collection

known_failure: EMPTY_COLLECTION

Cause: AOI/date/cloud filters leave no images. Recovery: verify AOI overlap, widen date range, relax cloud filters, or choose another dataset.

## Image Has No Bands

known_failure: IMAGE_HAS_NO_BANDS

Cause: a collection reduction or masked image produced an empty image. Recovery: check collection count, required bands, QA masks, and date/AOI coverage before reducers or export.

## Projection Or Scale Mismatch

known_failure: PROJECTION_SCALE_MISMATCH

Cause: reducer/export scale or CRS does not match data resolution or AOI size. Recovery: state scale/CRS in the plan, estimate pixel count, and review native projection assumptions.

## Memory, Quota, Or Timeout

known_failure: QUOTA_OR_TIMEOUT

Cause: geometry too large, reducer too expensive, export too broad, or too many tasks. Recovery: reduce AOI, adjust scale, use `tileScale`, simplify geometry, or split exports.

## Missing QA Band

known_failure: NO_QA_BAND

Cause: masking policy expects a QA/SCL band not present in the selected dataset. Recovery: use dataset-specific QA bands or change masking strategy.

## Invalid AOI

known_failure: EMPTY_AOI

Cause: missing asset, empty FeatureCollection, invalid geometry, or placeholder AOI. Recovery: replace placeholders, validate feature count and area, and simplify complex geometry.

## Failed Export

known_failure: EXPORT_TASK_ERROR

Cause: invalid destination, unsupported schema, huge region, missing selectors, Drive permission issues, or backend failure. Recovery: inspect task status, error message, export metadata, selectors, and destination.

## Preflight Required

known_failure: PREFLIGHT_REQUIRED

Cause: a live export path was requested before the plan was reviewed, rendered, validated, and preflighted. Recovery: run `plan review`, `validate`, and `preflight` first, then use `--confirm-live` only after those gates pass.

## Authentication Or Project Errors

known_failure: AUTH_ERROR
known_failure: PROJECT_ERROR

Cause: missing local OAuth, expired credentials, project id not set, Earth Engine API disabled, or IAM mismatch. Recovery: authenticate locally, run `gee-skill auth check --project <id> --json`, and do not share credential files or token paths.
