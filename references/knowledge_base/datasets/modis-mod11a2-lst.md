# Dataset Card: MOD11A2.061 Terra Land Surface Temperature and Emissivity 8-Day Global 1km

source_id: dataset-modis-mod11a2-lst
source_type: official-dataset-card
primary_status: canonical
dataset_id: MODIS/061/MOD11A2
title: MOD11A2.061 Terra Land Surface Temperature and Emissivity 8-Day Global 1km
provider: NASA LP DAAC / USGS EROS Center
gee_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2
source_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2
temporal_coverage: 2000-02-18-present; 8-day cadence
spatial_resolution: 1000m
bands: LST_Day_1km, LST_Night_1km, QC_Day, QC_Night, Emis_31, Emis_32
qa_bands: QC_Day, QC_Night, Clear_sky_days, Clear_sky_nights
common_uses: land surface temperature, thermal climatology, regional heat diagnostics
recommended_tasks: land_surface_temperature, zonal_statistics, export_image
scale_notes: Use 1000m unless intentionally resampling or aggregating.
projection_notes: Document coarse MODIS resolution when combining with Sentinel or Landsat products.
license_attribution: NASA LP DAAC / USGS MODIS data terms apply.
last_checked: 2026-06-24
risk_level: medium

## Use

Use `MODIS/061/MOD11A2` for land surface temperature, thermal climatology, regional heat diagnostics.

## Bands

Core bands: LST_Day_1km, LST_Night_1km, QC_Day, QC_Night, Emis_31, Emis_32.

QA or mask bands: QC_Day, QC_Night, Clear_sky_days, Clear_sky_nights.

## Recommended Tasks

- land_surface_temperature
- zonal_statistics
- export_image

## Scale and Projection Notes

- Use 1000m unless intentionally resampling or aggregating.
- Document coarse MODIS resolution when combining with Sentinel or Landsat products.

## Known Limitations

- LST bands require scale factor conversion.
- The 8-day product averages daily inputs and does not filter by specific QA bits before averaging.

## Attribution

NASA LP DAAC / USGS MODIS data terms apply.
