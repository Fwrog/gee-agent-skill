# Validation v0.3: Hong Kong NDVI Product Intercomparison

This validation demo evaluates whether `gee-agent-skill` can produce and check a scientifically plausible NDVI workflow across public Earth Engine products. It is a product intercomparison, not in-situ ground-truth validation.

## Analytical Question

Can a harness-generated Earth Engine workflow derive 30 m HLS NDVI, match MODIS 16-day windows, aggregate HLS to the MODIS grid, export results to Google Drive, and recover quantitative agreement metrics against the official MODIS MOD13Q1 vegetation-index product?

## Official Dataset Facts

The implementation is grounded in official Earth Engine catalog metadata:

- HLSL30 (`NASA/HLS/HLSL30/v002`) provides 30 m HLS Landsat observations with red `B4`, NIR `B5`, and `Fmask` quality bits.
- HLSS30 (`NASA/HLS/HLSS30/v002`) provides 30 m HLS Sentinel-2 observations with red `B4`, narrow NIR `B8A`, broad NIR `B8`, and the same `Fmask` bit pattern.
- MOD13Q1 (`MODIS/061/MOD13Q1`) provides 16-day 250 m NDVI with scale factor `0.0001`, plus `SummaryQA` and `DetailedQA`.
- ESA WorldCover v200 (`ESA/WorldCover/v200`) provides a static 2021 10 m `Map` band used for stratification only.

## Workflow

```text
MODIS 16-day windows
  -> HLS L30/S30 images inside each window
  -> HLS Fmask cloud/shadow/water/high-aerosol screening
  -> median HLS NDVI at 30 m
  -> mean aggregation to the MODIS projection
  -> MODIS NDVI scaling and QA screening
  -> matched valid pixels
  -> Drive CSV/GeoTIFF exports
  -> connector readback
  -> metrics, figures, report, and skill checklist
```

## Metrics

The analysis computes:

- matched pixel count and valid fraction;
- mean HLS NDVI and mean MODIS NDVI;
- bias as HLS aggregated NDVI minus MODIS NDVI;
- MAE, RMSE, and median absolute error;
- Pearson correlation and Spearman rank correlation from exported pixel samples;
- simple linear slope/intercept for HLS aggregated NDVI against MODIS NDVI;
- land-cover-stratified metrics for vegetation-dominated, built-up-dominated, mixed, and coastal/water-adjacent pixels.

## Quality Gates

- NDVI values must remain mostly inside the physical sanity range after scale and masking.
- MODIS NDVI must not look like unscaled integer values.
- Direct HLS 30 m to MODIS 250 m pixel comparison is disallowed.
- Matched valid pixels must be non-empty.
- Weak product agreement is reported as an interpretation caveat, not an automatic script failure.
- The live v0.3 `auto` ROI uses a documented Hong Kong bounding region for stable MODIS/HLS grid transforms. `--roi-source gaul` remains available for boundary experiments, but GAUL triggered transform failures in the smoke export path.

## Figure Set

The figure script creates:

- regional mean NDVI time series for HLS aggregated to 250 m versus MODIS;
- HLS-vs-MODIS matched-pixel hexbin;
- spatial sample map of HLS aggregated NDVI minus MODIS NDVI;
- land-cover-stratified MAE/RMSE/bias chart;
- valid matched-fraction chart by MODIS window.

## Current Evidence Status

The repository now contains the canonical script, recipe contract, metrics contract tests, task-state monitor, documentation, full-year 2024 CSV evidence, annual raster/tile evidence, and a readiness audit. The Google Drive connector read back the required CSV and GeoTIFF exports from `GEE_SKILL_V03_HK_NDVI_VALIDATION`; local analysis ran without `--allow-partial` and produced summary metrics, QA notes, figures, raster QA, and a `golden_ready` audit result.

| Metric | Full-year CSV value |
| --- | ---: |
| Matched samples | 5,575 |
| Mean HLS aggregated NDVI | 0.662 |
| Mean MODIS NDVI | 0.687 |
| Bias, HLS - MODIS | -0.025 |
| MAE | 0.073 |
| RMSE | 0.111 |
| Pearson r | 0.870 |
| Spearman rho | 0.859 |

Land-cover stratification shows the expected pattern: vegetation-dominated pixels have the strongest agreement (RMSE 0.082), while coastal/water-adjacent pixels have the weakest agreement (RMSE 0.193). Four strict-QA MODIS windows had zero matched pixels and are displayed as gaps rather than interpolated.

Generated figures:

- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_regional_ndvi_timeseries.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_hls_vs_modis_hexbin.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_spatial_difference_samples.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_landcover_metrics.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_valid_fraction_by_window.png`

This status is now `Golden` for the public v0.3 product-intercomparison demo. The HLS 30 m mean and replacement MODIS 250 m mean were observed in Drive as full-region GeoTIFFs. The full-region HLS aggregated 250 m, difference, and valid-count replacements failed with out-of-memory, so deterministic 2x2 tiled fallbacks were used for those products. The tiled HLS aggregated 250 m mean, tiled difference map, and tiled valid-count map are tracked in `outputs/hk_ndvi_product_validation_v03/task_status_latest.json`, downloaded through Drive readback, and covered by local raster sanity QA.

Recent live raster attempts added three reusable GEE lessons to the public skill knowledge base: avoid per-window product-grid clipping before cross-CRS annual exports, use a low-memory annual raster strategy when per-window fine-to-coarse stacks exceed worker memory, and set an explicit default projection before `reduceResolution` after `ImageCollection.mean()`.

## Claim Boundary

Supported wording:

```text
This v0.3 demo evaluates product-level consistency and remote-sensing workflow reliability by comparing HLS-derived NDVI aggregated to the MODIS grid against MOD13Q1 NDVI.
```

Avoid:

```text
The demo proves ground-truth vegetation accuracy.
```

## v0.4 Gaps To Close

- Add optional VIIRS VNP13A1 as a secondary product-level check.
- Add an automated comparator that diffs skill-rendered code against the canonical v0.3 implementation.
- Add optional S30 `B8` sensitivity export beside the default `B8A` narrow-NIR workflow.
- Add a machine-readable demo registry so README, capability matrix, and validation docs can share one status source.
- Decide whether tiny raster thumbnails/previews should be committed while keeping raw GeoTIFFs ignored.
