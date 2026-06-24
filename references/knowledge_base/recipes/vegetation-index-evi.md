# Recipe Card: vegetation-index-evi

source_id: recipe-vegetation-index-evi
source_type: curated-recipe-card
primary_status: curated
recipe_id: vegetation-index-evi
task_type: vegetation_index
description: Compute EVI from optical reflectance bands with explicit coefficients.
required_inputs: aoi, time_range, output
optional_inputs: dataset_id, cloud_policy, scale
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2
default_dataset_policy: Prefer Sentinel-2 for current 10m analyses; use Landsat for long historical continuity.
template: sentinel2_index_table
preflight_profile: optical_index
validation_profile: optical_index
output_schema: aoi_name, date_start, date_end, mean_evi, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute EVI from optical reflectance bands with explicit coefficients.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- dataset_id
- cloud_policy
- scale

## Dataset Policy

Prefer Sentinel-2 for current 10m analyses; use Landsat for long historical continuity.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2.

## Template and Safety

- Template: `sentinel2_index_table`
- Preflight profile: `optical_index`
- Validation profile: `optical_index`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- mean_evi
- dataset_id
- scale_m
- crs

## Examples

- Compute EVI for a supplied AOI in March 2024 and export CSV.

## Limitations

- EVI coefficient and band scaling choices must be reviewed for each sensor.
