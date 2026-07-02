# Failure Case: GEE Live Export Contract Failures

source_id: failure-gee-live-export-contract
source_type: curated-failure-case
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/exporting; https://developers.google.com/earth-engine/apidocs/export-image-todrive; https://developers.google.com/earth-engine/apidocs/export-table-todrive
last_checked: 2026-07-02
known_failure: UNSUPPORTED_EXPORT_CRS
known_failure: EXPORT_BAND_DTYPE_MISMATCH
known_failure: DEPRECATED_ASSET_REPLACEMENT
known_failure: BOUNDARY_SCHEMA_MISMATCH
known_failure: LARGE_DRIVE_FETCH_UNSTABLE
known_failure: REDUCE_RESOLUTION_WITHOUT_DEFAULT_PROJECTION
known_failure: BOUNDARY_GEOMETRY_PRODUCT_GRID_TRANSFORM
known_failure: NULL_METRIC_BREAKS_EXPORT
known_failure: PRODUCT_GRID_IMAGE_CLIP_TRANSFORM
known_failure: ANNUAL_RASTER_OUT_OF_MEMORY
risk_level: high

## Symptoms

Live Earth Engine exports pass dry rendering but fail, stall, or produce unusable downstream files because the export contract was underspecified.

Common symptoms include:

- `Export.image.toDrive` fails when the requested CRS is not accepted by Earth Engine export workers.
- GeoTIFF export fails because image bands have mixed numeric dtypes such as Float32 and Float64.
- A dataset card or template uses a stale asset id even though the catalog has a replacement asset.
- Boundary filters return zero features because the public boundary dataset uses different name, parent, or code fields than expected.
- Large Drive CSV outputs exist, but connector-side raw download is unreliable; the workflow needs a resumable direct Earth Engine table download or a smaller partitioned export.
- `Image.reduceResolution` fails because a median, count, or other collection-reduced image has no valid default projection.
- `reduceRegion`, `sample`, `clip`, or image export fails when an administrative geometry is transformed into a product projection such as MODIS sinusoidal.
- A metric export fails because an empty matched-pixel group produces null reducer outputs and the script applies numeric operations such as `sqrt` to null.
- Annual GeoTIFF export fails with transform errors such as `Image.clip: Unable to transform edge...` when product-grid images are clipped per window and later exported in another CRS.
- Annual GeoTIFF export fails with `Execution failed; out of memory` when many per-window fine-to-coarse rasters are stacked before export.

## Required Gates

- Preflight every live export with source image counts, AOI feature count, expected band names, scale, CRS, selectors, and output folder metadata.
- Cast all image export bands to a uniform dtype before `Export.image.toDrive`, usually with `.toFloat()` unless integer precision is required and reviewed.
- Validate the CRS on a smoke export before launching multi-year or large-AOI image exports.
- Verify boundary schema with actual field names and sample values before filtering by place names or parent administrative units.
- Set an explicit default projection before `reduceResolution` when aggregating fine-resolution composites to a coarser product grid.
- Treat "boundary resolved" and "boundary works with this product grid" as separate checks.
- Make validation metrics null-safe for empty windows or strata; hard-fail locally only after exported data prove there are no valid matched pixels for the intended analysis scope.
- For annual image stacks, avoid per-window clipping of product-grid images before cross-CRS export. Prefer keeping inputs unclipped, setting the export `region`, and clipping only the final display/analysis product when necessary.
- For annual fine-to-coarse rasters, prefer low-memory ordering when scientifically acceptable: compute the annual fine-resolution composite, set a valid default projection, then aggregate once to the coarse product grid.
- Record task id, description, Drive folder, state, source assets, CRS, scale, and claim boundary in a durable log.
- For large table outputs, prefer explicit selectors and partitioned exports; when Drive fetch is unstable, use Earth Engine signed table downloads or smaller year/region chunks for local analysis.

## Recovery

Retry image exports after casting bands to one dtype and selecting a CRS known to work for the target workflow. Replace stale asset ids only after checking an official catalog or provider page. If boundary schema does not expose the required parent fields, downgrade the claim or switch to a boundary source whose schema can express the study unit. If a collection composite has no valid default projection, apply `setDefaultProjection` before `reduceResolution`. If an administrative geometry fails during product-grid transforms, fall back to a documented simplified geometry or bounding polygon and state the boundary downgrade. If annual product-grid GeoTIFFs fail after per-window `clip`, rebuild the annual stack from unclipped product-grid images and let `Export.image.toDrive(region=...)` define the output bounds. If annual fine-to-coarse raster stacks run out of memory, reduce server-side graph complexity by aggregating the annual fine-resolution composite once, and keep valid-count masks as byte images before summing. If reducer metrics can be null, guard downstream numeric operations with `ee.Algorithms.If` or equivalent null-safe logic. If raw Drive download fails for a large CSV, keep the Drive task as export evidence and materialize analysis inputs through a signed Earth Engine table download or smaller partitioned exports.

## Cannot Claim

- A completed public substitute export does not prove authoritative administrative, county, or cadastral accuracy.
- A successful smoke export does not prove that all larger annual exports have completed; each task still needs observed terminal state.
- A direct analysis download is not the same artifact as the Drive export unless the source image, AOI, selectors, scale, CRS, and year are recorded and matched.
