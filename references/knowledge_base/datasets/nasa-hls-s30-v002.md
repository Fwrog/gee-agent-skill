# Dataset Card: NASA HLSS30 v002

source_id: dataset-nasa-hls-s30-v002
source_type: official-dataset-card
primary_status: canonical
dataset_id: NASA/HLS/HLSS30/v002
title: HLSS30 Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m
provider: NASA LP DAAC
gee_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002
source_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002
temporal_coverage: 2015-present; check catalog for current ingestion status
spatial_resolution: 30m
bands: B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11, B12, Fmask
qa_bands: Fmask
common_uses: harmonized Sentinel-2 surface reflectance, NDVI, dense optical time series, HLS/MODIS intercomparison
recommended_tasks: vegetation_index, product_intercomparison, export_image
scale_notes: Reflectance bands should be explicitly scaled before physical range checks. Default NDVI uses red B4 and narrow NIR B8A; broad NIR B8 is a sensitivity option.
projection_notes: HLS is 30m and must be aggregated before comparison with coarser products.
license_attribution: NASA LP DAAC HLS data terms apply.
last_checked: 2026-07-02
risk_level: medium

## Use

Use `NASA/HLS/HLSS30/v002` as the Sentinel-2 HLS component for 30m NDVI and harmonized surface-reflectance workflows.

## QA

Use `Fmask` to remove cloud, adjacent cloud/shadow, cloud shadow, snow/ice, water, and high aerosol where those exclusions match the analysis question.

## Known Limitations

- S30 red-edge and NIR choices must be explicit; default to B8A for narrow-NIR HLS/MODIS comparison.
- HLS 30m outputs should not be compared directly with MODIS 250m pixels.
- Exported image bands should be cast to a uniform dtype before Drive export.
