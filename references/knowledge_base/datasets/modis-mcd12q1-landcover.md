# Dataset Card: MCD12Q1.061 MODIS Land Cover Type Yearly Global 500m

source_id: dataset-modis-mcd12q1-landcover
source_type: official-dataset-card
primary_status: canonical
dataset_id: MODIS/061/MCD12Q1
title: MCD12Q1.061 MODIS Land Cover Type Yearly Global 500m
provider: NASA LP DAAC / USGS EROS Center
gee_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1
source_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1
temporal_coverage: 2001-2024 annual product; check catalog for current ingestion status
spatial_resolution: 500m
bands: LC_Type1, LC_Type2, LC_Type3, LC_Type4, LC_Type5, QC, LW
qa_bands: QC, LW
common_uses: annual land-cover summaries, coarse land-cover change, global land-cover context
recommended_tasks: landcover_summary, zonal_statistics, change_detection, export_image
scale_notes: Use 500m or coarser analytical grids unless intentionally resampling for alignment.
projection_notes: Use explicit CRS/scale for reducers and exports; document when aggregating to equal-area grids.
license_attribution: NASA LP DAAC / USGS MODIS data terms apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `MODIS/061/MCD12Q1` when a public, annual, global land-cover backbone is acceptable and the analysis can tolerate 500m resolution.

## Bands

Core bands: LC_Type1, LC_Type2, LC_Type3, LC_Type4, LC_Type5, QC, LW.

QA or mask bands: QC, LW.

## Recommended Tasks

- landcover_summary
- zonal_statistics
- change_detection
- export_image

## Scale and Projection Notes

- Use 500m or coarser analytical grids unless intentionally resampling for alignment.
- Use explicit CRS/scale for reducers and exports.

## Known Limitations

- The 500m product is a coarse public land-cover backbone and must not be described as 10m or 30m mapping.
- Class systems differ by LC_Type band; document the selected classification scheme.

## Attribution

NASA LP DAAC / USGS MODIS data terms apply.
