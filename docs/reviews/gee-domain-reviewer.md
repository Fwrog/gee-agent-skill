# GEE Domain Review: Dataset Semantics

Scope: Sentinel-2 NDVI monthly zonal statistics, Landsat Collection 2 LST, Sentinel-1 before/after flood mapping, and Drive CSV table exports.

## Semantic Validation Expectations

- Sentinel-2 monthly NDVI: use `COPERNICUS/S2_SR_HARMONIZED`, compute NDVI from `B8` and `B4` after per-pixel quality masking, and define months as calendar windows `[month_start, next_month_start)`. Zonal outputs should carry `dataset_id`, month, date range, cloud-mask method, `image_count`, reducer, scale, CRS, and a valid-pixel count or coverage field so null or sparse months are not interpreted as stable vegetation signal.
- Zonal statistics: `reduceRegions` should use an explicit scale and CRS, preserve stable zone identifiers, and keep reducer output names aligned with CSV selectors. For district means, note that a simple pixel mean is not area-weighted unless an area-weighted reducer is intentionally implemented.
- Landsat LST: use a Collection 2 Level-2 collection matching the sensor. `ST_B10` with `multiply(0.00341802).add(149.0).subtract(273.15)` is appropriate for Landsat 8/9 L2 surface temperature; Landsat 4/5/7 workflows need the correct sensor-specific ST band, commonly `ST_B6`. Mask `QA_PIXEL` fill, dilated cloud, cirrus where present, cloud, cloud shadow, and snow before compositing.
- Sentinel-1 flood change: compare homogeneous SAR observations from `COPERNICUS/S1_GRD`: same instrument mode, polarization, orbit pass, resolution, and comparable incidence geometry. Apply speckle control and compute change consistently: dB subtraction is a log-ratio, while linear ratios require converting dB back to power first.
- Table export CSV: Python scripts should use `ee.batch.Export.table.toDrive` with `fileFormat="CSV"`, stable `description`, `folder`, `fileNamePrefix`, and explicit `selectors`. Export only scalar properties needed for review unless geometries are intentional and vertex limits are handled.

## Likely Dataset Pitfalls

- `CLOUDY_PIXEL_PERCENTAGE` is scene metadata, not a pixel mask; SCL, Cloud Probability, or Cloud Score+ choices can materially change monthly Sentinel-2 means. QA60-only recipes are risky because the catalog documents QA60 continuity caveats.
- Empty or low-coverage Sentinel-2 monthly collections can export null or biased means. Treat `image_count` as necessary but insufficient; include valid-pixel coverage or count by zone where possible.
- `FAO/GAUL/2015/level2` is a 2015 administrative boundary product. It may be acceptable for a benchmark, but current district reporting should verify boundary names and geometry against the intended authority.
- Landsat C2 L2 scale factors must not be applied to TOA/L1 thermal bands or to the wrong ST band. Surface-temperature availability and masks can vary by scene, so exported LST should include date range, sensor collection, composite reducer, and QA policy.
- Sentinel-1 darkening can indicate open water, but also radar shadow, smooth non-water surfaces, crop/soil moisture change, or acquisition-geometry effects. Before/after flood thresholds need local validation and should normally exclude permanent water and terrain-shadow artifacts.
- Current or recent flood events should confirm that the chosen Earth Engine collection has scenes for both before and after windows before planning exports.
- CSV selectors must match actual reducer property names, for example `mean` for a single-band mean reducer in the current templates. Missing selectors silently break reviewability even when the export task starts.
