# Error Taxonomy

Every structured error includes category, likely cause, retryability, suggested fix, and whether user action is required.

- `AUTH_ERROR`: credentials or Earth Engine access are missing.
- `PROJECT_ERROR`: Google Cloud Project is missing, inaccessible, or not enabled for Earth Engine.
- `DATASET_NOT_FOUND`: dataset id is wrong or unavailable.
- `BAND_NOT_FOUND`: selected band does not exist for the dataset.
- `EMPTY_COLLECTION`: filters produced no images.
- `GEOMETRY_ERROR`: AOI geometry, asset id, or administrative filter is invalid.
- `REDUCER_SCALE_ERROR`: scale, CRS, tileScale, maxPixels, or pixel budget is unsuitable.
- `EXPORT_TASK_ERROR`: export creation, destination, or task state failed.
- `QUOTA_OR_TIMEOUT`: platform quota, memory, queue, or timeout limits were hit.
- `CLIENT_SERVER_MISUSE`: unsafe client-side calls such as large `getInfo()` usage.

Validation findings carry the category when it is known. Live failures are classified from the original exception and written into `live_run_report.json`.

