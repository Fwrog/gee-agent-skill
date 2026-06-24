# Recipe Card: builtup-index-ndbi

source_id: recipe-builtup-index-ndbi
source_type: curated-recipe-card
primary_status: curated
recipe_id: builtup-index-ndbi
task_type: builtup_index
description: Compute NDBI from SWIR and NIR bands for built-up diagnostics.
required_inputs: aoi, time_range, output
optional_inputs: dataset_id, cloud_policy
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2
default_dataset_policy: Prefer Sentinel-2 SR for 10m NDBI when the AOI/time range has coverage.
template: sentinel2_index_table
preflight_profile: optical_index
validation_profile: builtup_index_ndbi
output_schema: aoi_name, date_start, date_end, mean_ndbi, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute NDBI from SWIR and NIR bands for built-up diagnostics.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- dataset_id
- cloud_policy

## Dataset Policy

Prefer Sentinel-2 SR for 10m NDBI when the AOI/time range has coverage.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2.

## Template and Safety

- Template: `sentinel2_index_table`
- Preflight profile: `optical_index`
- Validation profile: `builtup_index_ndbi`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- mean_ndbi
- dataset_id
- scale_m
- crs

## Examples

- Compute NDBI for Hong Kong in 2024 and export CSV.

## Limitations

- NDBI can confuse bare soil and built surfaces; land-cover context should be reviewed.
