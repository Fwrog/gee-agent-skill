# Operator Chain: Sentinel-2 Monthly NDVI Zonal CSV

source_id: operator-chain-s2-monthly-ndvi-zonal
source_type: operator-chain
publisher: gee-agent-skill
source_url: https://developers.google.com/earth-engine/apidocs/ee-imagecollection-filterdate; https://developers.google.com/earth-engine/apidocs/ee-imagecollection-filterbounds; https://developers.google.com/earth-engine/apidocs/ee-imagecollection-map; https://developers.google.com/earth-engine/apidocs/ee-image-normalizeddifference; https://developers.google.com/earth-engine/apidocs/ee-image-reduceregions; https://developers.google.com/earth-engine/apidocs/export-table-todrive
retrieved_at: 2026-06-21
primary_status: derived-from-official-docs
dataset_id: COPERNICUS/S2_SR_HARMONIZED
operator_chain: ImageCollection.filterDate -> filterBounds -> filter -> map(mask_sentinel2_scl) -> map(add_ndvi) -> select -> mean -> reduceRegions -> ee.batch.Export.table.toDrive
task_domain: ndvi-zonal-statistics
known_failure: empty_collection, cloud_mask_bias, selector_mismatch
risk_level: medium

## Chain

Use this chain for monthly NDVI district statistics:

1. Build AOI feature collection.
2. For each month, filter Sentinel-2 SR Harmonized by date and AOI.
3. Apply scene-level cloud percentage filter as a coarse prefilter.
4. Apply pixel-level SCL cloud/quality masking.
5. Add NDVI from B8 and B4.
6. Aggregate monthly mean NDVI.
7. Run `reduceRegions` over zones with explicit scale, CRS, and tileScale.
8. Annotate year, month, date range, dataset id, scale, CRS, and image_count.
9. Export CSV with explicit selectors.

## Failure Cases

- Empty image collection for a month.
- Low valid-pixel coverage after cloud masking.
- CSV selectors not matching reducer property names.
- Overly large geometry causing reducer scale or quota errors.
