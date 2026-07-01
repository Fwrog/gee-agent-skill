# Recipe Card: vegetation-index-ndvi

source_id: recipe-vegetation-index-ndvi
source_type: curated-recipe-card
primary_status: curated
recipe_id: vegetation-index-ndvi
task_type: vegetation_index
description: Compute NDVI from optical surface reflectance and export an image or table.
required_inputs: aoi, time_range, output
optional_inputs: grouping, temporal_cadence, cloud_policy, dataset_id
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2
default_dataset_policy: Prefer Sentinel-2 SR for 10m regional NDVI unless Landsat continuity is requested.
template: sentinel2_ndvi_composite
preflight_profile: optical_index
validation_profile: vegetation_index_ndvi
output_schema: aoi_name, date_start, date_end, mean_ndvi, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute NDVI from optical surface reflectance and export an image or table.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- grouping
- temporal_cadence
- cloud_policy
- dataset_id

## Dataset Policy

Prefer Sentinel-2 SR for 10m regional NDVI unless Landsat continuity is requested.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2.

## Template and Safety

- Template: `sentinel2_ndvi_composite`
- Preflight profile: `optical_index`
- Validation profile: `vegetation_index_ndvi`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- mean_ndvi
- dataset_id
- scale_m
- crs

## Examples

- Compute NDVI for a supplied AOI in March 2024 and export CSV.

## Limitations

- Optical index outputs require cloud, shadow, and water-context review before scientific interpretation.
- Public golden examples prove the harness loop, not vegetation-monitoring validity.
