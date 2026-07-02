# Failure Case: Direct Fine/Coarse Pixel Comparison

source_id: failure-fine-coarse-direct-pixel-comparison
source_type: curated-failure-case
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/resample; https://developers.google.com/earth-engine/guides/reducers_reduce_resolution; https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1
last_checked: 2026-07-02
known_failure: DIRECT_FINE_COARSE_PIXEL_COMPARISON
risk_level: high

## Symptom

A workflow compares high-resolution index pixels, such as 10m Sentinel-2 or 30m HLS NDVI, directly against coarse product pixels such as 250m MODIS or 500m VIIRS. The metric may run, but it mixes spatial supports and can report edge, coastal, urban, or mixed-pixel differences as if they were algorithm error.

## Why This Is Wrong

Fine-resolution and coarse-resolution products do not represent the same ground footprint. A single coarse pixel may contain many land-cover types, cloud-mask outcomes, water edges, slopes, or urban surfaces. Direct pixel-to-pixel comparison overstates disagreement near boundaries and can produce misleading validation claims.

## Required Gate

Before pixel-level intercomparison:

- match the product time window or compositing period;
- apply each product's documented QA and scale factors;
- aggregate the fine-resolution product to the coarse product grid with an explicit reducer such as area-aware mean;
- compare only where both products have valid observations;
- stratify or caveat mixed, built-up, coastal, and water-adjacent pixels;
- report the comparison as product-level consistency, not ground-truth accuracy.

## Recovery

Rebuild the comparison around the coarse product grid. In Earth Engine, set a valid default projection on the fine-resolution composite before `reduceResolution`, aggregate to the target projection, and export both the aggregated fine product and the coarse official product with traceable scale/CRS metadata.

## Cannot Claim

- Direct 30m-vs-250m or 10m-vs-250m pixel agreement does not validate a high-resolution workflow.
- High agreement after aggregation is still product intercomparison, not in-situ truth.
- Weak agreement does not automatically mean the workflow is wrong; QA, compositing, view geometry, mixed pixels, and class composition can be valid causes.
