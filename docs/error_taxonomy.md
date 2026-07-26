# Error Taxonomy

Every structured error includes agent-facing `code`/`hint` fields plus category, likely cause, retryability, suggested fix, and whether user action is required.

- `AUTH_ERROR`: credentials or Earth Engine access are missing.
- `PROJECT_ERROR`: Google Cloud Project is missing, inaccessible, or not enabled for Earth Engine.
- `NETWORK_ERROR`: live initialization hit a transient network, TLS, or OAuth token endpoint failure.
- `DATASET_NOT_FOUND`: dataset id is wrong or unavailable.
- `BAND_NOT_FOUND`: selected band does not exist for the dataset.
- `EMPTY_COLLECTION`: filters produced no images.
- `EMPTY_AOI`: district or AOI boundary source returned zero usable features.
- `V03_CONTEXT_REVIEW_REQUIRED`: v0.3 plan context still contains placeholders such as AOI assets or export metadata.
- `V03_PREFLIGHT_UNSUPPORTED`: selected v0.3 template does not yet have a preflight adapter.
- `AOI_SCHEMA_ERROR`: AOI source exists but the required geometry/property schema is not usable.
- `DISTRICT_NOT_FOUND`: requested district name did not match the boundary source.
- `EMPTY_IMAGE_COLLECTION`: Sentinel-2 date/AOI/cloud filters returned zero candidate images.
- `EMPTY_FILTERED_COLLECTION`: candidate images exist before cloud filtering but none remain after cloud metadata filtering.
- `NO_NDVI_BAND`: NDVI band was not produced before reduction/export.
- `NO_REQUIRED_BAND`: selected dataset is missing one or more recipe-required bands.
- `NO_QA_BAND`: selected dataset is missing the expected QA or mask band.
- `NULL_NDVI_STAT`: NDVI band exists but the sanity reducer returned no mean value.
- `GEOMETRY_ERROR`: AOI geometry, asset id, or administrative filter is invalid.
- `REDUCER_SCALE_ERROR`: scale, CRS, tileScale, maxPixels, or pixel budget is unsuitable.
- `EXPORT_TASK_ERROR`: export creation, destination, or task state failed.
- `EXPORT_TASK_FAILED`: a submitted export task reached failed state.
- `EXPORT_TASK_NOT_OBSERVED`: the script ran but the expected Earth Engine export task was not visible in the monitored task list.
- `NO_EXPORT_TARGET`: plan export destination metadata is incomplete.
- `AMBIGUOUS_TASK`: natural-language request is missing required date, AOI, metric, or output intent.
- `UNSUPPORTED_TASK`: natural-language request is outside the currently registered deterministic recipes.
- `QUOTA_OR_TIMEOUT`: platform quota, memory, queue, or timeout limits were hit.
- `UNSAFE_GETINFO`: generated production code attempts to materialize Earth Engine server objects locally with `getInfo()`.
- `CLIENT_SERVER_MISUSE`: unsafe client-side calls such as large `getInfo()` usage.
- `PREFLIGHT_REQUIRED`: live export was requested before the review, validation, and preflight gate sequence was completed.

Validation findings carry the category when it is known. Live failures are classified from the original exception and written into `live_run_report.json`.

## Annual-workflow validation codes

The `annual_endmember_transition` semantic profile also emits stable, non-provider-specific findings:

- `COLLECTION_GEOMETRY_UNBOUNDED`: a tiled/global collection lacks a reviewed metadata-property filter before reduction.
- `SPATIAL_FILTER_INEFFECTIVE`: an AOI-only spatial filter is treated as sufficient even though image footprints may not prune the collection.
- `COMPLEX_EXPORT_REGION_RISK`: a complex feature geometry is passed directly as the export region instead of using a bounding rectangle plus raster mask.
- `MONOLITHIC_REDUCTION_RISK`: a large multi-band annual graph is reduced before bounded tile or band-group staging.
- `CATEGORICAL_FRACTION_SEMANTICS_UNSAFE`: preaggregated class fractions do not declare whole-cell versus valid-area composition semantics, or valid-area thresholds omit a minimum-support normalization gate.

The first two are blocking errors because they can silently admit unrelated observations. The export-region and monolithic-graph findings are warnings: fix them before large live tasks, but do not treat a static warning alone as proof that an Earth Engine task will fail.
