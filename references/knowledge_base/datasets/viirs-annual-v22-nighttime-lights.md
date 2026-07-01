# Dataset Card: VIIRS Stray Light Corrected Nighttime Day/Night Band Composites V2.2

source_id: dataset-viirs-annual-v22-nighttime-lights
source_type: official-dataset-card
primary_status: canonical
dataset_id: NOAA/VIIRS/DNB/ANNUAL_V22
title: VIIRS Stray Light Corrected Nighttime Day/Night Band Composites V2.2
provider: NOAA / Earth Observation Group
gee_url: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22
source_url: https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_ANNUAL_V22
temporal_coverage: 2022-present annual composites; check catalog for current ingestion status
spatial_resolution: 15 arc-seconds
bands: average, average_masked, cf_cvg, cvg, maximum, median, median_masked, minimum
qa_bands: cf_cvg, cvg
common_uses: nighttime lights, settlement activity proxy, urban intensity proxy, change detection
recommended_tasks: zonal_statistics, change_detection, export_image
scale_notes: Use native coarse scale or aggregate to a documented analytical grid; prefer average_masked when available.
projection_notes: Use explicit CRS/scale for cross-year reducers and exports.
license_attribution: NOAA/EOG VIIRS nighttime lights terms apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `NOAA/VIIRS/DNB/ANNUAL_V22` for annual nighttime-lights summaries for years covered by VIIRS V2.2.

## Bands

Core bands: average, average_masked, cf_cvg, cvg, maximum, median, median_masked, minimum.

QA or mask bands: cf_cvg, cvg.

## Recommended Tasks

- zonal_statistics
- change_detection
- export_image

## Scale and Projection Notes

- Use native coarse scale or aggregate to a documented analytical grid.
- Prefer `average_masked` when available, with a fallback policy documented in generated code.

## Known Limitations

- Nighttime lights are an activity proxy, not a direct land-cover or population measurement.
- Document any cross-version join with VIIRS V2.1 and check band availability before rendering templates.

## Attribution

NOAA/EOG VIIRS nighttime lights terms apply.
