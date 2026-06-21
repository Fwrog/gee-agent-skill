# Workflow Pattern: Hong Kong January 2024 NDVI CSV v0.1

source_id: workflow-hk-january-ndvi-v01
source_type: workflow-pattern
publisher: gee-agent-skill
source_url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED; https://developers.google.com/earth-engine/apidocs/ee-image-normalizeddifference; https://developers.google.com/earth-engine/apidocs/ee-image-reduceregion; https://developers.google.com/earth-engine/apidocs/export-table-todrive
retrieved_at: 2026-06-21
primary_status: derived-from-official-docs
dataset_id: COPERNICUS/S2_SR_HARMONIZED
operator_chain: ImageCollection.filterDate -> filterBounds -> filter -> map(mask_sentinel2_scl) -> map(add_ndvi) -> select -> mean -> reduceRegion -> ee.batch.Export.table.toDrive
task_tags: hong-kong, ndvi, january-2024, csv-export, v0.1
operator_tags: filterDate, filterBounds, normalizedDifference, reduceRegion, Export.table.toDrive
failure_tags: EMPTY_AOI, EMPTY_IMAGE_COLLECTION, EMPTY_FILTERED_COLLECTION, NO_NDVI_BAND, NULL_NDVI_STAT
risk_level: medium

## Applicability

Use this pattern for the v0.1 live smoke target: compute a single mean NDVI value for Hong Kong for January 2024 and export a one-row CSV. It intentionally uses a whole-Hong-Kong AOI before the full 2024 district-level monthly workflow.

## Required Evidence

- Dataset card: `COPERNICUS/S2_SR_HARMONIZED` provides Sentinel-2 surface reflectance with `B8`, `B4`, and `SCL`.
- Operator syntax: use `filterDate`, `filterBounds`, `normalizedDifference(["B8", "B4"])`, `reduceRegion`, and `ee.batch.Export.table.toDrive`.
- Workflow order: probe AOI and image counts before export, then cloud mask with SCL, add NDVI, average the month, reduce over the AOI, and export with explicit selectors.
- Failure prevention: block export if AOI is empty, image collection is empty before or after cloud metadata filtering, monthly NDVI has no `NDVI` band, or the reducer returns null.

## Output Schema

The CSV should include `aoi_name`, `year`, `month`, `date_start`, `date_end`, `mean_ndvi`, `image_count_before_cloud_filter`, `image_count_after_cloud_filter`, `dataset_id`, `scale_m`, `crs`, `aoi_source`, and `export_description`.

## Known Failure Case

`Image.reduceRegions: Image has no bands.` indicates that the workflow attempted reduction after filters or mapping produced an image without bands. For v0.1 this must be caught in preflight as `EMPTY_IMAGE_COLLECTION`, `EMPTY_FILTERED_COLLECTION`, `NO_NDVI_BAND`, or `NULL_NDVI_STAT` before `task.start()`.
