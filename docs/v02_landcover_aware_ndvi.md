# v0.2 Land-Cover-Aware Hong Kong NDVI

## Request

```text
Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.
```

The deterministic router also recognizes equivalent requests such as "Calculate Hong Kong January 2024 NDVI by land use" and "Compare all-surface and land-only NDVI for Hong Kong January 2024."

## Data Choices

- AOI: curated Hong Kong boundary GeoJSON.
- NDVI source: `COPERNICUS/S2_SR_HARMONIZED`.
- Land-cover source: `GOOGLE/DYNAMICWORLD/V1`.
- Static reference: `ESA/WorldCover/v200`, documented as optional and not used as the primary time-matched mask.

Dynamic World is used for masks and strata, not for administrative boundaries.

## Plan-First Commands

```powershell
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." `
  --plan `
  --json

gee-skill review-plan outputs/runs/<run_id>/task_plan.yaml

gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --json

gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --confirm-live `
  --json
```

## Output Schema

The CSV is a compact one-row diagnostic table:

```text
aoi_name, year, month, date_start, date_end, dataset_id,
landcover_dataset_id, landcover_strategy, scale_m, crs,
all_surface_mean_ndvi, non_water_mean_ndvi, land_only_mean_ndvi,
vegetation_mean_ndvi, trees_mean_ndvi, grass_mean_ndvi,
shrub_and_scrub_mean_ndvi, built_mean_ndvi, bare_mean_ndvi,
water_fraction, built_fraction, vegetation_fraction, trees_fraction,
grass_fraction, s2_image_count_before_cloud_filter,
s2_image_count_after_cloud_filter, dynamic_world_image_count,
dynamic_world_probability_threshold, export_description
```

Sparse classes may return null class-specific NDVI. Interpret those with the preflight warnings and class fractions, not as zero vegetation.

## Interpretation Boundary

All-surface NDVI can be low when water, built-up, bare, and vegetation pixels are mixed. A reasonable vegetation-only NDVI alongside low all-surface NDVI suggests the aggregate is driven by mixed land cover, not necessarily poor vegetation condition.
