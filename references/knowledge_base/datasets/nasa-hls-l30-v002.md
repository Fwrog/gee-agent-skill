# Dataset Card: NASA HLSL30 v002

source_id: dataset-nasa-hls-l30-v002
source_type: official-dataset-card
primary_status: canonical
dataset_id: NASA/HLS/HLSL30/v002
title: HLSL30 Landsat Operational Land Imager Surface Reflectance Daily Global 30m
provider: NASA LP DAAC
gee_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002
source_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002
temporal_coverage: 2013-present; check catalog for current ingestion status
spatial_resolution: 30m
bands: B1, B2, B3, B4, B5, B6, B7, B9, B10, B11, Fmask
qa_bands: Fmask
common_uses: harmonized Landsat surface reflectance, NDVI, annual optical features, multi-sensor time series, product intercomparison
recommended_tasks: vegetation_index, annual_endmember_transition, product_intercomparison, export_image
scale_notes: Earth Engine exposes HLS v002 reflectance as floating-point values; do not reapply the source-file 0.0001 packing factor. Verify sampled physical ranges before export. NDVI uses red B4 and NIR B5.
projection_notes: HLS is 30m and must be aggregated before comparison with coarser products.
license_attribution: NASA LP DAAC HLS data terms apply.
last_checked: 2026-07-26
risk_level: medium

## Use

Use `NASA/HLS/HLSL30/v002` as the Landsat HLS component for 30m NDVI and surface-reflectance workflows.

## QA

Use `Fmask` to remove cloud, adjacent cloud/shadow, cloud shadow, snow/ice, water, and high aerosol where those exclusions match the analysis question.

## Known Limitations

- HLS is not a ground-truth product.
- Applying `.multiply(0.0001)` to the Earth Engine v002 reflectance bands
  double-scales them; retain a bounded reflectance plausibility check.
- HLS 30m outputs should not be compared directly with MODIS 250m pixels.
- Exported image bands should be cast to a uniform dtype before Drive export.
- Annual workflows must persist per-year image counts and valid-observation rasters; catalog availability does not guarantee usable AOI coverage.
