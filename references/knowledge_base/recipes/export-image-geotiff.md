# Recipe Card: Image Export GeoTIFF

source_id: recipe-image-export-geotiff
source_type: curated-recipe-card
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/exporting_images
last_checked: 2026-06-23
recipe_id: image-export-geotiff
task_type: export_image
method_name: Export.image.toDrive, ee.batch.Export.image.toDrive
operator_chain: validated image -> explicit region -> explicit scale/CRS -> maxPixels -> export task -> monitor task state
risk_level: high

## Required Inputs

- Server-side image expression or rendered image product.
- Explicit AOI/export region.
- Explicit scale and CRS review.
- Export destination, description, file prefix, and max pixel budget.

## Contract

GeoTIFF exports must set `region`, `scale`, `fileFormat="GeoTIFF"`, and `maxPixels` or an equivalent max pixel budget. Export task submission is not completion; the run trace must record task id, description, state, timestamps, and error message.

## Failure Cases

known_failure: EXPORT_TASK_ERROR

Large regions, tiny scale, invalid geometry, missing region, and quota limits are common failure sources. Live export must require explicit confirmation.
