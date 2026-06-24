# Dataset Card: Sentinel-2 MSI Surface Reflectance Harmonized

source_id: dataset-sentinel-2-sr-harmonized
source_type: official-dataset-card
primary_status: canonical
dataset_id: COPERNICUS/S2_SR_HARMONIZED
title: Sentinel-2 MSI Surface Reflectance Harmonized
provider: Copernicus / ESA
gee_url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
source_url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
temporal_coverage: 2017-present; check catalog for current ingestion status
spatial_resolution: 10m, 20m, and 60m bands
bands: B2, B3, B4, B8, B11, B12, SCL
qa_bands: SCL, QA60
common_uses: vegetation indices, water indices, built-up indices, zonal statistics
recommended_tasks: vegetation_index, water_index, builtup_index, zonal_statistics, export_image
scale_notes: Use 10m for B2/B3/B4/B8 index products unless the recipe requires coarser scale.
projection_notes: Set explicit CRS/scale when comparing regions or exporting rasters.
license_attribution: Copernicus Sentinel data terms apply.
last_checked: 2026-06-21
risk_level: medium

## Use

Use `COPERNICUS/S2_SR_HARMONIZED` for vegetation indices, water indices, built-up indices, zonal statistics.

## Bands

Core bands: B2, B3, B4, B8, B11, B12, SCL.

QA or mask bands: SCL, QA60.

## Recommended Tasks

- vegetation_index
- water_index
- builtup_index
- zonal_statistics
- export_image

## Scale and Projection Notes

- Use 10m for B2/B3/B4/B8 index products unless the recipe requires coarser scale.
- Set explicit CRS/scale when comparing regions or exporting rasters.

## Known Limitations

- Cloud and shadow masking are mandatory for optical analysis.
- Band resolutions differ; reducers and exports need explicit scale.

## Attribution

Copernicus Sentinel data terms apply.
