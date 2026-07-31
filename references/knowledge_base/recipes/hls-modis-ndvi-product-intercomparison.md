# HLS/MODIS NDVI Product Intercomparison

task_type: product_intercomparison
recipe_id: hls-modis-ndvi-product-intercomparison
evidence_level: plan-and-validation-contract
last_checked: 2026-07-31
required_inputs: [aoi, time_range, output]
candidate_datasets: [NASA/HLS/HLSL30/v002, NASA/HLS/HLSS30/v002, MODIS/061/MOD13Q1]
template: null
preflight_profile: optical_index
validation_profile: product_intercomparison
output_schema: [time_window, sample_count, mean_hls_ndvi, mean_modis_ndvi, bias_hls_minus_modis, mae, rmse, pearson_r, target_scale_m, target_crs, claim_boundary]
live_risk_level: high
limitations:
  - This is a plan-and-validation contract, not a generic live implementation.
  - Product consistency is not in-situ ground-truth validation.

## Contract

Compare quality-filtered HLSL30 and HLSS30 NDVI with quality-filtered MOD13Q1 NDVI after explicit temporal matching and aggregation to a reviewed MODIS target grid.

## Required Boundaries

- Apply HLS Fmask policies before compositing.
- Apply the MOD13Q1 NDVI scale factor and QA policy before metrics.
- Aggregate 30 m HLS observations to the selected 250 m MODIS grid; never compare native-resolution pixels directly.
- Record the temporal matching window, valid sample count, target scale, target projection, and dataset IDs.
- Describe results as satellite-product consistency, not in-situ ground-truth validation.

## Current Readiness

The generic planner and validation contract are implemented. The registry intentionally has no generic live template, so generated plans remain reviewable and non-executable until a study-specific temporal and export context is approved.
