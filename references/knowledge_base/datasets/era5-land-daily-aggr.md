# Dataset Card: ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis

source_id: dataset-era5-land-daily-aggr
source_type: official-dataset-card
primary_status: canonical
dataset_id: ECMWF/ERA5_LAND/DAILY_AGGR
title: ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis
provider: ECMWF / Copernicus Climate Data Store
gee_url: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR
source_url: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR
temporal_coverage: 1950-present with near-real-time lag; check catalog availability
spatial_resolution: 11132m
bands: temperature_2m, total_precipitation_sum, surface_pressure, u_component_of_wind_10m, v_component_of_wind_10m
qa_bands: none
common_uses: climate covariates, temperature and precipitation summaries, hydrometeorological context
recommended_tasks: zonal_statistics, change_detection, export_table, export_image
scale_notes: Use coarse regional scales near 11132m; avoid mixing with 10m optical outputs without aggregation.
projection_notes: Document reanalysis grid assumptions and aggregation windows.
license_attribution: ECMWF/Copernicus attribution and citation requirements apply.
last_checked: 2026-06-24
risk_level: medium

## Use

Use `ECMWF/ERA5_LAND/DAILY_AGGR` for climate covariates, temperature and precipitation summaries, hydrometeorological context.

## Bands

Core bands: temperature_2m, total_precipitation_sum, surface_pressure, u_component_of_wind_10m, v_component_of_wind_10m.

QA or mask bands: none.

## Recommended Tasks

- zonal_statistics
- change_detection
- export_table
- export_image

## Scale and Projection Notes

- Use coarse regional scales near 11132m; avoid mixing with 10m optical outputs without aggregation.
- Document reanalysis grid assumptions and aggregation windows.

## Known Limitations

- Coarse reanalysis pixels are not a substitute for local station observations.
- Some evaporation variables have known swapped-value issues in the source data.
- Some precipitation and flow aggregates can contain small negative or excessive values.

## Attribution

ECMWF/Copernicus attribution and citation requirements apply.
