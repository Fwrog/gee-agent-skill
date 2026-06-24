# Dataset Card: NASA SRTM Digital Elevation 30m

source_id: dataset-srtm-gl1-003
source_type: official-dataset-card
primary_status: canonical
dataset_id: USGS/SRTMGL1_003
title: NASA SRTM Digital Elevation 30m
provider: NASA / USGS / JPL-Caltech
gee_url: https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003
source_url: https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003
temporal_coverage: 2000-02-11 to 2000-02-22 static DEM
spatial_resolution: 30m
bands: elevation
qa_bands: none
common_uses: terrain covariates, slope, elevation masks, topographic context
recommended_tasks: zonal_statistics, export_image, change_detection
scale_notes: Use 30m for terrain-derived products such as slope unless intentionally aggregating.
projection_notes: Use explicit scale when reducing or exporting terrain covariates.
license_attribution: NASA/JPL SRTM citation and use terms apply.
last_checked: 2026-06-24
risk_level: medium

## Use

Use `USGS/SRTMGL1_003` for terrain covariates, slope, elevation masks, topographic context.

## Bands

Core bands: elevation.

QA or mask bands: none.

## Recommended Tasks

- zonal_statistics
- export_image
- change_detection

## Scale and Projection Notes

- Use 30m for terrain-derived products such as slope unless intentionally aggregating.
- Use explicit scale when reducing or exporting terrain covariates.

## Known Limitations

- Static terrain layer; not a time-varying surface observation.

## Attribution

NASA/JPL SRTM citation and use terms apply.
