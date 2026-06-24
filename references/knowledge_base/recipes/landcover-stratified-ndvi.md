# Recipe Card: landcover-stratified-ndvi

source_id: recipe-landcover-stratified-ndvi
source_type: curated-recipe-card
primary_status: curated
recipe_id: landcover-stratified-ndvi
task_type: landcover_stratified_statistics
description: Compute NDVI diagnostics by Dynamic World land-cover class.
required_inputs: aoi, time_range, output
optional_inputs: probability_threshold, class_groups, dataset_id
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, GOOGLE/DYNAMICWORLD/V1, ESA/WorldCover/v200
default_dataset_policy: Use Dynamic World for time-matched masks and ESA WorldCover only as static reference.
template: hk_january_2024_ndvi_by_landcover_csv
preflight_profile: landcover_stratified
validation_profile: dynamic_world_landcover_ndvi
output_schema: all_surface_mean_ndvi, non_water_mean_ndvi, vegetation_mean_ndvi, class_fractions
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute NDVI diagnostics by Dynamic World land-cover class.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- probability_threshold
- class_groups
- dataset_id

## Dataset Policy

Use Dynamic World for time-matched masks and ESA WorldCover only as static reference.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, GOOGLE/DYNAMICWORLD/V1, ESA/WorldCover/v200.

## Template and Safety

- Template: `hk_january_2024_ndvi_by_landcover_csv`
- Preflight profile: `landcover_stratified`
- Validation profile: `dynamic_world_landcover_ndvi`
- Live risk level: `medium`

## Output Schema

- all_surface_mean_ndvi
- non_water_mean_ndvi
- vegetation_mean_ndvi
- class_fractions

## Examples

- Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.

## Limitations

- Current live-verified path is the Hong Kong golden example; other AOIs need recipe-specific verification.
