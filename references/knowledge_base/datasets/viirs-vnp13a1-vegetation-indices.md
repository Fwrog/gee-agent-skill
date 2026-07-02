# Dataset Card: VIIRS VNP13A1 v002

source_id: dataset-viirs-vnp13a1-vegetation-indices
source_type: official-dataset-card
primary_status: canonical
dataset_id: NASA/VIIRS/002/VNP13A1
title: VNP13A1.002 VIIRS Vegetation Indices 16-Day 500m
provider: NASA LP DAAC / USGS EROS Center
gee_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_VIIRS_002_VNP13A1
source_url: https://developers.google.com/earth-engine/datasets/catalog/NASA_VIIRS_002_VNP13A1
temporal_coverage: 2012-present; check catalog for current ingestion status
spatial_resolution: 500m
bands: NDVI, EVI, EVI2, VI_Quality, pixel_reliability
qa_bands: VI_Quality, pixel_reliability
common_uses: secondary vegetation-index product consistency check, MODIS continuity context
recommended_tasks: vegetation_index, product_intercomparison
scale_notes: Use catalog band definitions and QA; do not mix 500m VIIRS pixels with finer products without aggregation.
projection_notes: Compare at VIIRS grid or coarser regional summaries.
license_attribution: NASA LP DAAC VIIRS data terms apply.
last_checked: 2026-07-02
risk_level: medium

## Use

Use `NASA/VIIRS/002/VNP13A1` as an optional secondary vegetation-index product check after the primary MODIS comparison works.

## Known Limitations

- VIIRS 500m products are coarser than HLS and MODIS MOD13Q1.
- This product can support product-level consistency checks, not in-situ ground-truth claims.
