# Dataset Card: JRC Global Surface Water Mapping Layers v1.4

source_id: dataset-jrc-global-surface-water
source_type: official-dataset-card
primary_status: canonical
dataset_id: JRC/GSW1_4/GlobalSurfaceWater
title: JRC Global Surface Water Mapping Layers v1.4
provider: EC JRC / Google
gee_url: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater
source_url: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater
temporal_coverage: 1984-03-16 to 2022-01-01 static mapping layers
spatial_resolution: 30m
bands: occurrence, change_abs, change_norm, seasonality, recurrence, transition, max_extent
qa_bands: max_extent
common_uses: surface water occurrence, water change context, water masks
recommended_tasks: water_index, change_detection, flood_mapping, zonal_statistics
scale_notes: Use 30m for summaries unless coarsening for large regions.
projection_notes: Use as reference/context; document when combining with current Sentinel observations.
license_attribution: Copernicus Programme attribution required; cite EC JRC/Google where used.
last_checked: 2026-06-24
risk_level: medium

## Use

Use `JRC/GSW1_4/GlobalSurfaceWater` for surface water occurrence, water change context, water masks.

## Bands

Core bands: occurrence, change_abs, change_norm, seasonality, recurrence, transition, max_extent.

QA or mask bands: max_extent.

## Recommended Tasks

- water_index
- change_detection
- flood_mapping
- zonal_statistics

## Scale and Projection Notes

- Use 30m for summaries unless coarsening for large regions.
- Use as reference/context; document when combining with current Sentinel observations.

## Known Limitations

- Historical mapping layers are not time-matched to arbitrary current flood windows.
- The occurrence band mask can mirror partial occurrence values and needs careful interpretation.

## Attribution

Copernicus Programme attribution required; cite EC JRC/Google where used.
