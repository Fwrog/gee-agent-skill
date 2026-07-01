# Workflow Pattern: NDVI Demo Validation Ladder

source_id: workflow-ndvi-demo-validation-ladder
source_type: curated-workflow-pattern
primary_status: curated
source_url: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1; https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD13Q1; https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2; https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2; https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1; https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200; https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater
last_checked: 2026-07-01
operator_chain: Sentinel-2 demo NDVI -> independent product lookup -> scale/QA harmonization -> aggregate comparison -> class/water sanity check -> claim-boundary review
risk_level: medium

## Pattern

Validate NDVI demos with a ladder of independent or semi-independent GEE products rather than a single absolute truth source. The goal is to show that the workflow is quantitatively reasonable, not to claim peer-reviewed vegetation monitoring from a small demo.

## Product Roles

- `MODIS/061/MOD13Q1` and `MODIS/061/MYD13Q1`: coarse 16-day NDVI/EVI reference products for aggregate temporal and range checks.
- `LANDSAT/LC08/C02/T1_L2` and `LANDSAT/LC09/C02/T1_L2`: independent 30m surface-reflectance sensors for cross-sensor NDVI checks after QA masking and scale/offset conversion.
- `JRC/GSW1_4/GlobalSurfaceWater`: surface-water occurrence reference to test whether all-surface NDVI is lower than non-water or vegetation-like strata in coastal AOIs.
- `GOOGLE/DYNAMICWORLD/V1`: time-matched probabilistic land-cover strata for the land-cover-aware demo, with confidence thresholds and null-tolerant outputs.
- `ESA/WorldCover/v200`: static 10m land-cover reference for broad class sanity checks against Dynamic World masks.

## Validation Questions

- Does Sentinel-2 all-surface NDVI fall in a plausible range after cloud and shadow masking?
- Does a coarse MODIS 16-day NDVI product show the same broad temporal direction, even if absolute values differ?
- Do Landsat 8/9 NDVI aggregates agree in sign, broad seasonal pattern, and approximate magnitude after QA masking?
- Are water and built-up strata lower than vegetation-like strata?
- Does a land-cover-aware output clearly state that strata are interpretation masks, not administrative boundaries or ground truth?

## Required Caveats

- MODIS 250m and Landsat 30m products cannot validate Sentinel-2 10m edges pixel-for-pixel.
- Dynamic World is a model output and should not be treated as independent ground truth for the same Sentinel-2 observation.
- ESA WorldCover is static and not time-matched to arbitrary analysis windows.
- Surface-water masks explain all-surface NDVI behavior but do not validate vegetation health.
- Export completion and cross-product consistency support workflow reasonableness, not final scientific claims.

## Failure Cases

known_failure: ABSOLUTE_VALUE_OVERCLAIM
known_failure: SCALE_MISMATCH_AS_TRUTH
known_failure: LANDCOVER_MASK_AS_BOUNDARY
known_failure: DYNAMIC_WORLD_AS_INDEPENDENT_TRUTH
known_failure: WATER_PIXELS_IGNORED_IN_ALL_SURFACE_NDVI
