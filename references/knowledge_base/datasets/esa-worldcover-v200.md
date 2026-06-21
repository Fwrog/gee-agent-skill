# Dataset Card: ESA WorldCover v200

source_id: dataset-esa-worldcover-v200
source_type: official-data-catalog
publisher: Google Earth Engine
source_url: https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
last_checked: 2026-06-21
primary_status: optional-reference
dataset_id: ESA/WorldCover/v200
temporal_coverage: Static 2021 global map
spatial_resolution: 10 m
risk_level: medium

## Use

ESA WorldCover v200 can be used as a static sanity-check reference for land-cover interpretation. It is not time-matched to January 2024 and should not silently replace Dynamic World for a time-matched workflow.

## Workflow Notes

- Document that ESA WorldCover is static.
- Use it for cross-checking broad class plausibility, not for temporal class changes.
- Do not use land-cover pixels as administrative boundaries.

## Failure Cases

known_failure: STATIC_REFERENCE_MISMATCH

Static land-cover data can disagree with time-matched Dynamic World labels. Treat differences as diagnostic evidence, not automatic truth.
