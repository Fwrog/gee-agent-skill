# Operator Notes: Reducers and Zonal Statistics

source_id: operator-reducers-zonal-statistics
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/reducers_intro
last_checked: 2026-06-21
method_name: reduceRegion, reduceRegions, ee.Reducer.mean
operator_chain: filterDate -> filterBounds -> mask -> composite -> reduceRegion/reduceRegions -> Export.table.toDrive
risk_level: medium

## Syntax Notes

- `image.reduceRegion(reducer=..., geometry=..., scale=..., crs=..., maxPixels=..., tileScale=...)` returns one dictionary for one geometry.
- `image.reduceRegions(collection=..., reducer=..., scale=..., crs=..., tileScale=...)` attaches reducer outputs to each feature.
- For CSV exports, convert reducer outputs into feature properties and specify `selectors`.

## Relationship Chain

Cloud and QA masks should be applied before compositing and reduction. Region/date filters should happen before reducers to limit server work. Output schema should include counts or flags that reveal empty collections and sparse masks.

## Failure Cases

known_failure: NULL_REDUCER_OUTPUT

Null reducer values can mean the image has no valid pixels in the AOI/mask at the chosen scale. Recovery: inspect image count, mask coverage, band names, scale, and AOI geometry.
