# Recipe Card: Water Index NDWI

source_id: recipe-water-index-ndwi
source_type: curated-recipe-card
primary_status: curated
source_url: https://developers.google.com/earth-engine/apidocs/ee-image-normalizeddifference
last_checked: 2026-06-23
recipe_id: water-index-ndwi
task_type: water_index
dataset_id: COPERNICUS/S2_SR_HARMONIZED
method_name: ee.Image.normalizedDifference
operator_chain: AOI -> filterDate -> filterBounds -> cloud mask -> normalizedDifference -> composite -> Export.image.toDrive or Export.table.toDrive
risk_level: medium

## Required Inputs

- AOI: named place, GeoJSON, EE asset, or bounding box.
- Time range: month, season, year, or explicit date range.
- Output: GeoTIFF image when spatial water pattern matters; CSV/table when summary statistics are requested.

## Default Policy

Use Sentinel-2 SR Harmonized for 10 m NDWI/MNDWI unless the request asks for Landsat. NDWI commonly uses green and NIR; MNDWI commonly uses green and SWIR. The plan must record which variant was selected.

## Example

```text
Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF.
```

The parser should infer `task_type: water_index`, `output.format: GeoTIFF`, and recommend Sentinel-2 SR. If AOI is absent, return `AMBIGUOUS_TASK` with `missing_fields: [aoi]`.

## Failure Cases

known_failure: BAND_NOT_FOUND

The semantic rules must reject NDWI plans or scripts that lack a green band and a NIR/SWIR counterpart.
