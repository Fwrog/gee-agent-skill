# Dataset Card: Dynamic World V1

source_id: dataset-dynamic-world-v1
source_type: official-data-catalog
publisher: Google Earth Engine
source_url: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
last_checked: 2026-06-21
primary_status: canonical
dataset_id: GOOGLE/DYNAMICWORLD/V1
temporal_coverage: Near-real-time Sentinel-2 era observations
spatial_resolution: 10 m
classes: water, trees, grass, flooded_vegetation, crops, shrub_and_scrub, built, bare, snow_and_ice
risk_level: medium

## Use

Dynamic World V1 provides per-class probabilities and a `label` band for Sentinel-2-aligned land-cover interpretation. For NDVI diagnostics, use it as masks, strata, and interpretation groups; do not use it as an administrative boundary.

## Workflow Notes

- Filter by the same date range and AOI as the Sentinel-2 NDVI workflow.
- Check image count, `label`, and all expected probability bands before export.
- Use a documented probability threshold such as 0.35 and export the threshold.
- Sparse classes should return null statistics plus warnings, not fabricated values.

## Failure Cases

known_failure: EMPTY_DYNAMIC_WORLD_COLLECTION

No Dynamic World images or missing probability bands should block export before `task.start()`.
