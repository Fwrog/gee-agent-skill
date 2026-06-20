# Dataset Card: Sentinel-2 SR Harmonized

source_id: dataset-s2-sr-harmonized
source_type: official-data-catalog
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
retrieved_at: 2026-06-21
primary_status: canonical
dataset_id: COPERNICUS/S2_SR_HARMONIZED
platform: Sentinel-2
sensor: MSI
risk_level: low

## Use

Collection id: `COPERNICUS/S2_SR_HARMONIZED`.

Surface reflectance bands are scaled by 10000. NDVI can be computed from `B8` and `B4`; the scale factor cancels for normalized difference. The collection includes SCL and QA bands; QA60 has documented caveats, so SCL, Cloud Probability, or Cloud Score+ should be considered.

## Workflow Notes

- Filter with `filterDate` and `filterBounds`.
- Apply cloud/quality masking before compositing.
- Use explicit scale and CRS for exports and reducers.
- Record date range, collection id, cloud mask method, and image count.

