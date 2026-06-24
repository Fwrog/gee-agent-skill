# Recipe Card: sentinel1-flood-before-after

source_id: recipe-sentinel1-flood-before-after
source_type: curated-recipe-card
primary_status: curated
recipe_id: sentinel1-flood-before-after
task_type: flood_mapping
description: Compare Sentinel-1 before/after SAR windows for flood or water-change mapping.
required_inputs: aoi, before_time_range, after_time_range, output
optional_inputs: polarization, orbit_pass, threshold
candidate_datasets: COPERNICUS/S1_GRD
default_dataset_policy: Use Sentinel-1 GRD with matched instrument mode, polarization, and orbit filters.
template: sentinel1_flood_before_after
preflight_profile: sentinel1_change
validation_profile: sentinel1_flood_before_after
output_schema: aoi_name, before_start, before_end, after_start, after_end, flood_area, dataset_id
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Compare Sentinel-1 before/after SAR windows for flood or water-change mapping.

## Required Inputs

- aoi
- before_time_range
- after_time_range
- output

## Optional Inputs

- polarization
- orbit_pass
- threshold

## Dataset Policy

Use Sentinel-1 GRD with matched instrument mode, polarization, and orbit filters.

Candidate datasets: COPERNICUS/S1_GRD.

## Template and Safety

- Template: `sentinel1_flood_before_after`
- Preflight profile: `sentinel1_change`
- Validation profile: `sentinel1_flood_before_after`
- Live risk level: `medium`

## Output Schema

- aoi_name
- before_start
- before_end
- after_start
- after_end
- flood_area
- dataset_id

## Examples

- Map Sentinel-1 flood extent for a supplied AOI before and after a storm.

## Limitations

- Flood thresholds and before/after windows require event-specific domain review.
