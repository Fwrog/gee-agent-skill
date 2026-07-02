# Rule Card: Vegetation Index Scale Factors

source_id: rule-vegetation-index-scale-factor
source_type: curated-rule-card
primary_status: curated
source_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1; https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD13Q1; https://developers.google.com/earth-engine/datasets/catalog/NASA_VIIRS_002_VNP13A1
last_checked: 2026-07-02
ruleset_id: vegetation_index_scale_factor
risk_level: high

## Rule

Official vegetation-index products often store NDVI/EVI as scaled integers. A generated workflow must apply the documented scale factor before interpreting values, comparing products, or exporting validation metrics.

## Validation Requirements

For MODIS vegetation-index products:

- `MODIS/061/MOD13Q1` NDVI and EVI require the documented `0.0001` scale factor.
- `MODIS/061/MYD13Q1` NDVI and EVI require the documented `0.0001` scale factor.
- Any metric contract should hard-fail if most NDVI values are outside `[-1, 1]` after masking.
- A product-intercomparison report should state the scale factor in the manifest or methods section.

For VIIRS vegetation-index products:

- Treat NDVI/EVI scale and QA as dataset-card requirements before use.
- Keep VIIRS optional in validation demos unless its data availability and QA behavior are verified for the target AOI/year.

## Failure Signal

If regional MODIS NDVI means are hundreds or thousands instead of roughly `[-1, 1]`, the scale factor was probably missed. Stop analysis and repair the export or analysis script rather than clipping the values downstream.

## Cannot Claim

- A workflow that forgets product scale factors cannot claim quantitative agreement.
- Range clipping after export is not a substitute for applying the documented scale factor.
- Product intercomparison cannot claim ground-truth vegetation accuracy without independent reference evidence.
