# Recipe Card: image-export-geotiff

source_id: recipe-image-export-geotiff
source_type: curated-recipe-card
primary_status: curated
recipe_id: image-export-geotiff
task_type: export_image
description: Export a validated Earth Engine image product to Drive as GeoTIFF.
required_inputs: image_or_index, aoi, time_range, output
optional_inputs: scale, crs, max_pixels
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, COPERNICUS/S1_GRD
default_dataset_policy: Use the source dataset selected by the upstream image recipe.
template: recipes/export_image
preflight_profile: export_image
validation_profile: export_image_geotiff
output_schema: image, region, scale_m, crs, file_format, export_description
live_risk_level: high
last_checked: 2026-06-24
risk_level: high

## Use

Export a validated Earth Engine image product to Drive as GeoTIFF.

## Required Inputs

- image_or_index
- aoi
- time_range
- output

## Optional Inputs

- scale
- crs
- max_pixels

## Dataset Policy

Use the source dataset selected by the upstream image recipe.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, COPERNICUS/S1_GRD.

## Template and Safety

- Template: `recipes/export_image`
- Preflight profile: `export_image`
- Validation profile: `export_image_geotiff`
- Live risk level: `high`

## Output Schema

- image
- region
- scale_m
- crs
- file_format
- export_description

## Examples

- Export March 2024 NDWI for a supplied AOI as GeoTIFF.

## Limitations

- Image exports are quota-sensitive and require reviewed region, projection, scale, and maxPixels.
