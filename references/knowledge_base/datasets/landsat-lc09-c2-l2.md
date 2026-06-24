# Dataset Card: Landsat 9 Collection 2 Tier 1 Level 2

source_id: dataset-landsat-lc09-c2-l2
source_type: official-dataset-card
primary_status: canonical
dataset_id: LANDSAT/LC09/C02/T1_L2
title: Landsat 9 Collection 2 Tier 1 Level 2
provider: USGS / NASA
gee_url: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
source_url: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2
temporal_coverage: 2021-present; check catalog for current ingestion status
spatial_resolution: 30m optical and thermal-derived products
bands: SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7, ST_B10
qa_bands: QA_PIXEL, QA_RADSAT
common_uses: land surface temperature, vegetation indices, change detection
recommended_tasks: land_surface_temperature, vegetation_index, change_detection
scale_notes: Use 30m for Collection 2 Level 2 products.
projection_notes: Use explicit projection or scale in reducers and exports.
license_attribution: USGS Landsat data policy applies.
last_checked: 2026-06-23
risk_level: medium

## Use

Use `LANDSAT/LC09/C02/T1_L2` for land surface temperature, vegetation indices, change detection.

## Bands

Core bands: SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7, ST_B10.

QA or mask bands: QA_PIXEL, QA_RADSAT.

## Recommended Tasks

- land_surface_temperature
- vegetation_index
- change_detection

## Scale and Projection Notes

- Use 30m for Collection 2 Level 2 products.
- Use explicit projection or scale in reducers and exports.

## Known Limitations

- Use consistent scaling with Landsat 8 when merging sensors.

## Attribution

USGS Landsat data policy applies.
