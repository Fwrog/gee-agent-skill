# Error Taxonomy

Every structured error includes category, likely cause, retryability, suggested fix, and whether user action is required.

- `AUTH_ERROR`: credentials or Earth Engine access are missing.
- `PROJECT_ERROR`: Google Cloud Project is missing, inaccessible, or not enabled for Earth Engine.
- `DATASET_NOT_FOUND`: dataset id is wrong or unavailable.
- `BAND_NOT_FOUND`: selected band does not exist for the dataset.
- `EMPTY_COLLECTION`: filters produced no images.
- `EMPTY_AOI`: district or AOI boundary source returned zero usable features.
- `AOI_SCHEMA_ERROR`: AOI source exists but the required geometry/property schema is not usable.
- `DISTRICT_NOT_FOUND`: requested district name did not match the boundary source.
- `EMPTY_IMAGE_COLLECTION`: Sentinel-2 date/AOI/cloud filters returned zero candidate images.
- `EMPTY_FILTERED_COLLECTION`: candidate images exist before cloud filtering but none remain after cloud metadata filtering.
- `NO_NDVI_BAND`: NDVI band was not produced before reduction/export.
- `NULL_NDVI_STAT`: NDVI band exists but the sanity reducer returned no mean value.
- `GEOMETRY_ERROR`: AOI geometry, asset id, or administrative filter is invalid.
- `REDUCER_SCALE_ERROR`: scale, CRS, tileScale, maxPixels, or pixel budget is unsuitable.
- `EXPORT_TASK_ERROR`: export creation, destination, or task state failed.
- `EXPORT_TASK_FAILED`: a submitted export task reached failed state.
- `AMBIGUOUS_TASK`: natural-language request is missing required date, AOI, metric, or output intent.
- `UNSUPPORTED_TASK`: natural-language request is outside the deterministic v0.1 router.
- `QUOTA_OR_TIMEOUT`: platform quota, memory, queue, or timeout limits were hit.
- `CLIENT_SERVER_MISUSE`: unsafe client-side calls such as large `getInfo()` usage.

Validation findings carry the category when it is known. Live failures are classified from the original exception and written into `live_run_report.json`.
