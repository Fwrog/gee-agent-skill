# Recipe Card: landsat-lst

source_id: recipe-landsat-lst
source_type: curated-recipe-card
primary_status: curated
recipe_id: landsat-lst
task_type: land_surface_temperature
description: Compute Landsat Collection 2 land surface temperature with QA_PIXEL masking.
required_inputs: aoi, time_range, output
optional_inputs: dataset_id, temperature_unit, cloud_policy
candidate_datasets: LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2
default_dataset_policy: Use Landsat Collection 2 Level 2 ST_B10 with documented scale and offset.
template: landsat_lst_table
preflight_profile: landsat_lst
validation_profile: landsat_lst
output_schema: aoi_name, date_start, date_end, mean_lst_c, dataset_id, scale_m, crs
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compute Landsat Collection 2 land surface temperature with QA_PIXEL masking.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- dataset_id
- temperature_unit
- cloud_policy

## Dataset Policy

Use Landsat Collection 2 Level 2 ST_B10 with documented scale and offset.

Candidate datasets: LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2.

## Template and Safety

- Template: `landsat_lst_table`
- Preflight profile: `landsat_lst`
- Validation profile: `landsat_lst`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- mean_lst_c
- dataset_id
- scale_m
- crs

## Examples

- Compute Landsat LST for Hong Kong in summer 2024 and export CSV.

## Limitations

- LST requires QA masking, scale/offset correctness, and thermal-domain interpretation review.
