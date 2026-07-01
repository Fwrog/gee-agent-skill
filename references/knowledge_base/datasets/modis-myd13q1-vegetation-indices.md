# Dataset Card: MYD13Q1.061 Aqua Vegetation Indices 16-Day Global 250m

source_id: dataset-modis-myd13q1-vegetation-indices
source_type: official-dataset-card
primary_status: canonical
dataset_id: MODIS/061/MYD13Q1
title: MYD13Q1.061 Aqua Vegetation Indices 16-Day Global 250m
provider: NASA LP DAAC / USGS EROS Center
gee_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD13Q1
source_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD13Q1
temporal_coverage: 2002-present 16-day composites; check catalog for current ingestion status
spatial_resolution: 250m
bands: NDVI, EVI, DetailedQA, sur_refl_b01, sur_refl_b02, sur_refl_b03, sur_refl_b07, ViewZenith, SolarZenith, RelativeAzimuth, DayOfYear, SummaryQA
qa_bands: DetailedQA, SummaryQA
common_uses: vegetation-index sanity checks, Terra/Aqua consistency review, coarse temporal validation
recommended_tasks: vegetation_index, zonal_statistics, change_detection
scale_notes: Use 250m or coarser summaries; pair with MOD13Q1 for Terra/Aqua consistency checks when needed.
projection_notes: Document sensor, scale, and compositing differences before interpreting mismatches.
license_attribution: NASA LP DAAC / USGS MODIS data terms apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `MODIS/061/MYD13Q1` as an Aqua MODIS companion to Terra MOD13Q1 when validating vegetation-index temporal reasonableness.

## Bands

Core bands: NDVI, EVI, DetailedQA, sur_refl_b01, sur_refl_b02, sur_refl_b03, sur_refl_b07, ViewZenith, SolarZenith, RelativeAzimuth, DayOfYear, SummaryQA.

QA or mask bands: DetailedQA, SummaryQA.

## Recommended Tasks

- vegetation_index
- zonal_statistics
- change_detection

## Scale and Projection Notes

- Apply the documented `0.0001` scale factor to NDVI and EVI.
- Use 250m or coarser summaries and interpret differences against Terra/Sentinel-2 as sensor/composite differences unless independently checked.

## Known Limitations

- Aqua timing differs from Terra and Sentinel-2 acquisition windows.
- The 250m composite is useful for aggregate checks, not high-resolution truth.
- Terra/Aqua agreement supports temporal plausibility but does not prove local class-level interpretation.

## Attribution

NASA LP DAAC / USGS MODIS data terms apply.
