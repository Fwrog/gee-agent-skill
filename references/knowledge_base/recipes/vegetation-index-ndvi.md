# Recipe Card: Vegetation Index NDVI

source_id: recipe-vegetation-index-ndvi
source_type: curated-recipe-card
primary_status: curated
source_url: https://developers.google.com/earth-engine/apidocs/ee-image-normalizeddifference
last_checked: 2026-06-23
recipe_id: vegetation-index-ndvi
task_type: vegetation_index
dataset_id: COPERNICUS/S2_SR_HARMONIZED
method_name: ee.Image.normalizedDifference
operator_chain: AOI -> filterDate -> filterBounds -> cloud mask -> normalizedDifference -> composite -> reducer/export
risk_level: medium

## Required Inputs

- AOI: named place, GeoJSON, EE asset, or bounding box.
- Time range: month, season, year, or explicit date range.
- Output: CSV/table, GeoTIFF/image, or preview.

## Default Policy

Use Sentinel-2 SR Harmonized for 10 m regional NDVI unless the request asks for Landsat continuity. NDVI uses NIR and red bands. For Sentinel-2 this means `B8` and `B4`; for Landsat Collection 2 this means `SR_B5` and `SR_B4`.

## Example: Hong Kong 2024 16-Day NDVI

User intent:

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

The plan should set:

- `task_type: vegetation_index`
- `indices_or_variables: [NDVI]`
- `aoi.name: Hong Kong`
- `time_range.date_start: 2024-01-01`
- `time_range.date_end: 2025-01-01`
- `execution.temporal_cadence: 16-day`
- `execution.template: hk_2024_16day_ndvi_csv`
- `validation.rulesets: [global_safety, vegetation_index_ndvi]`

The rendered script should export one CSV row per 16-day period. Required output fields are `aoi_name`, `year`, `period_index`, `date_start`, `date_end`, `temporal_cadence_days`, `mean_ndvi`, `image_count_before_cloud_filter`, `image_count_after_cloud_filter`, `dataset_id`, `scale_m`, `crs`, `aoi_source`, and `export_description`.

## Failure Cases

known_failure: EMPTY_COLLECTION

Cloud masks, small AOIs, winter vegetation, and strict date windows can produce empty or low-valid-pixel composites. Preflight must check collection count, expected bands, derived NDVI band, and a tiny sanity statistic before export.
