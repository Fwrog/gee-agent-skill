# Recipe Card: zonal-statistics-table

source_id: recipe-zonal-statistics-table
source_type: curated-recipe-card
primary_status: curated
recipe_id: zonal-statistics-table
task_type: zonal_statistics
description: Reduce an image or index product over supplied zones and export a table.
required_inputs: image_or_index, zones, time_range, output
optional_inputs: reducer, scale, selectors
candidate_datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2
default_dataset_policy: Select dataset from the index or image recipe, then reduce over explicit zones.
template: zonal_statistics
preflight_profile: zonal_statistics
validation_profile: export_table_csv
output_schema: zone_id, metric, value, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Reduce an image or index product over supplied zones and export a table.

## Required Inputs

- image_or_index
- zones
- time_range
- output

## Optional Inputs

- reducer
- scale
- selectors

## Dataset Policy

Select dataset from the index or image recipe, then reduce over explicit zones.

Candidate datasets: COPERNICUS/S2_SR_HARMONIZED, LANDSAT/LC08/C02/T1_L2.

## Template and Safety

- Template: `zonal_statistics`
- Preflight profile: `zonal_statistics`
- Validation profile: `export_table_csv`
- Live risk level: `medium`

## Output Schema

- zone_id
- metric
- value
- dataset_id
- scale_m
- crs

## Examples

- Compute zonal statistics for a supplied GeoJSON and export CSV.

## Limitations

- Zone geometry complexity and reducer scale can dominate quota and runtime behavior.
