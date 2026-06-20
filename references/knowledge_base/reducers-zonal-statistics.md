# Reducers And Zonal Statistics

source_id: google-ee-reduce-regions
source_type: official-api
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/apidocs/ee-image-reduceregions
retrieved_at: 2026-06-21
primary_status: canonical
risk_level: low

## reduceRegions

Use `ee.Image.reduceRegions` to summarize an image over every feature in a `FeatureCollection`. Always specify the input zones, reducer, and scale. Prefer an explicit CRS for reproducibility.

Large or complex zones can require `tileScale` tuning or splitting the AOI. Include metadata such as dataset id, date range, scale, CRS, and image count in exported features.

## Common Reducers

Common choices include `ee.Reducer.mean()`, `median()`, `count()`, `sum()`, and grouped reducers. Match the reducer to the scientific question and document units.

