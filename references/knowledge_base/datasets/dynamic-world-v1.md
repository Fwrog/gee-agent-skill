# Dataset Card: Dynamic World V1

source_id: dataset-dynamic-world-v1
source_type: official-dataset-card
primary_status: canonical
dataset_id: GOOGLE/DYNAMICWORLD/V1
title: Dynamic World V1
provider: Google / World Resources Institute
gee_url: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
source_url: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
temporal_coverage: 2015-present; check catalog for current ingestion status
spatial_resolution: 10m
bands: label, water, trees, grass, flooded_vegetation, crops, shrub_and_scrub, built, bare, snow_and_ice
qa_bands: none
common_uses: land-cover summary, land-cover-stratified statistics, interpretation diagnostics
recommended_tasks: landcover_summary, landcover_stratified_statistics
scale_notes: Use 10m with class probability thresholds documented in output metadata.
projection_notes: Use as masks/strata, not as an administrative boundary.
license_attribution: Dynamic World terms apply.
last_checked: 2026-06-21
risk_level: medium

## Use

Use `GOOGLE/DYNAMICWORLD/V1` for land-cover summary, land-cover-stratified statistics, interpretation diagnostics.

## Bands

Core bands: label, water, trees, grass, flooded_vegetation, crops, shrub_and_scrub, built, bare, snow_and_ice.

QA or mask bands: none.

## Recommended Tasks

- landcover_summary
- landcover_stratified_statistics

## Scale and Projection Notes

- Use 10m with class probability thresholds documented in output metadata.
- Use as masks/strata, not as an administrative boundary.

## Known Limitations

- Probabilistic classes need confidence thresholds and null-tolerant outputs.

## Attribution

Dynamic World terms apply.
