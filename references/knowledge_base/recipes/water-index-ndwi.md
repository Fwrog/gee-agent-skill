# Recipe Card: water-index-ndwi

source_id: recipe-water-index-ndwi
source_type: curated-recipe-card
primary_status: curated
recipe_id: water-index-ndwi
task_type: water_index
description: Compute NDWI or MNDWI from optical imagery for water diagnostics.
required_inputs: aoi, time_range, output
optional_inputs: dataset_id, index_variant, cloud_policy
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2
default_dataset_policy: Prefer Sentinel-2 SR for 10m NDWI/MNDWI unless Landsat is requested.
template: sentinel2_index_image
preflight_profile: optical_index
validation_profile: water_index_ndwi
output_schema: aoi_name, date_start, date_end, mean_ndwi, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute NDWI or MNDWI from optical imagery for water diagnostics.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- dataset_id
- index_variant
- cloud_policy

## Dataset Policy

Prefer Sentinel-2 SR for 10m NDWI/MNDWI unless Landsat is requested.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2.

## Template and Safety

- Template: `sentinel2_index_image`
- Preflight profile: `optical_index`
- Validation profile: `water_index_ndwi`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- mean_ndwi
- dataset_id
- scale_m
- crs

## Examples

- Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF.

## Limitations

- NDWI is sensitive to built surfaces, shadows, clouds, and turbidity; thresholding requires local review.
