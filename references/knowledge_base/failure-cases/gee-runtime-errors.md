# Known Failure Cases: Earth Engine Runtime

source_id: failure-cases-gee-runtime
source_type: known-failure-cases
publisher: gee-agent-skill
source_url: https://developers.google.com/earth-engine/guides/auth; https://developers.google.com/earth-engine/guides/debugging; https://developers.google.com/earth-engine/guides/usage; https://developers.google.com/earth-engine/apidocs/export-table-todrive
retrieved_at: 2026-06-21
primary_status: derived-from-official-docs
risk_level: medium

## Error Categories

known_failure: AUTH_ERROR
known_failure: PROJECT_ERROR
known_failure: DATASET_NOT_FOUND
known_failure: BAND_NOT_FOUND
known_failure: EMPTY_COLLECTION
known_failure: GEOMETRY_ERROR
known_failure: REDUCER_SCALE_ERROR
known_failure: EXPORT_TASK_ERROR
known_failure: QUOTA_OR_TIMEOUT
known_failure: UNSAFE_GETINFO
known_failure: CLIENT_SERVER_MISUSE
known_failure: PREFLIGHT_REQUIRED

- AUTH_ERROR: credentials missing, expired, or not authorized for Earth Engine.
- PROJECT_ERROR: no Google Cloud Project, Earth Engine API disabled, or IAM mismatch.
- DATASET_NOT_FOUND: collection id is wrong or unavailable.
- BAND_NOT_FOUND: selected band does not exist for dataset or sensor.
- EMPTY_COLLECTION: date, AOI, or cloud filters leave no imagery.
- GEOMETRY_ERROR: AOI asset/filter is invalid or too complex.
- REDUCER_SCALE_ERROR: reducer scale, CRS, maxPixels, or tileScale is unsuitable.
- EXPORT_TASK_ERROR: task creation, destination, selector, or Drive/GCS permission failure.
- QUOTA_OR_TIMEOUT: memory, pixel, concurrency, queue, or runtime limit.
- UNSAFE_GETINFO: generated production code uses `getInfo()` to fetch server objects locally instead of exporting or using bounded preflight probes.
- CLIENT_SERVER_MISUSE: blocking `getInfo()` or client-side operations on large server objects.
- PREFLIGHT_REQUIRED: live export was requested before review, validation, and preflight gates were completed.

## Recovery Pattern

Classify the failure, record it in `live_run_report.json` or `validation_report.json`, preserve the original message, and give a retryability flag plus suggested fix.
