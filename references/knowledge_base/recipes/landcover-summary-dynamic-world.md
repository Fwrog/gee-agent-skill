# Recipe Card: landcover-summary-dynamic-world

source_id: recipe-landcover-summary-dynamic-world
source_type: curated-recipe-card
primary_status: curated
recipe_id: landcover-summary-dynamic-world
task_type: landcover_summary
description: Summarize Dynamic World land-cover probabilities or top labels over an AOI.
required_inputs: aoi, time_range, output
optional_inputs: probability_threshold, class_groups, reducer
candidate_datasets: GOOGLE/DYNAMICWORLD/V1, ESA/WorldCover/v200
default_dataset_policy: Prefer Dynamic World for Sentinel-2-era dynamic summaries; use ESA WorldCover as static reference.
template: dynamic_world_landcover_summary
preflight_profile: landcover_stratified
validation_profile: dynamic_world_landcover
output_schema: aoi_name, date_start, date_end, class_label, area_m2, fraction
live_risk_level: medium
last_checked: 2026-06-24
risk_level: medium

## Use

Summarize Dynamic World land-cover probabilities or top labels over an AOI.

## Required Inputs

- aoi
- time_range
- output

## Optional Inputs

- probability_threshold
- class_groups
- reducer

## Dataset Policy

Prefer Dynamic World for Sentinel-2-era dynamic summaries; use ESA WorldCover as static reference.

Candidate datasets: GOOGLE/DYNAMICWORLD/V1, ESA/WorldCover/v200.

## Template and Safety

- Template: `dynamic_world_landcover_summary`
- Preflight profile: `landcover_stratified`
- Validation profile: `dynamic_world_landcover`
- Live risk level: `medium`

## Output Schema

- aoi_name
- date_start
- date_end
- class_label
- area_m2
- fraction

## Examples

- Summarize Dynamic World land cover for a GeoJSON AOI.

## Limitations

- Dynamic World probabilities need class-threshold and temporal aggregation review.
