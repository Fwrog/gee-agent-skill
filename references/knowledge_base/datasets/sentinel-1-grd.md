# Dataset Card: Sentinel-1 SAR GRD

source_id: dataset-sentinel-1-grd
source_type: official-dataset-card
primary_status: canonical
dataset_id: COPERNICUS/S1_GRD
title: Sentinel-1 SAR GRD
provider: Copernicus / ESA
gee_url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
source_url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
temporal_coverage: 2014-present; check catalog for current ingestion status
spatial_resolution: 10m, 25m, or 40m depending on mode/product
bands: VV, VH, HH, HV, angle
qa_bands: none
common_uses: flood mapping, before/after change detection, water extent
recommended_tasks: flood_mapping, change_detection
scale_notes: Use recipe-specific scale and filter by instrumentMode/polarization.
projection_notes: Compare before/after images with matched filters and consistent reducer scale.
license_attribution: Copernicus Sentinel data terms apply.
last_checked: 2026-06-21
risk_level: medium

## Use

Use `COPERNICUS/S1_GRD` for flood mapping, before/after change detection, water extent.

## Bands

Core bands: VV, VH, HH, HV, angle.

QA or mask bands: none.

## Recommended Tasks

- flood_mapping
- change_detection

## Scale and Projection Notes

- Use recipe-specific scale and filter by instrumentMode/polarization.
- Compare before/after images with matched filters and consistent reducer scale.

## Known Limitations

- Speckle, orbit direction, polarization, and incidence angle affect interpretation.

## Attribution

Copernicus Sentinel data terms apply.
