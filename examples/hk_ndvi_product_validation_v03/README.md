# Hong Kong NDVI Product Intercomparison Validation v0.3

This example is a portfolio-grade validation demo for `gee-agent-skill`. It tests whether the harness can support a scale-aware remote-sensing product-consistency workflow, not whether Hong Kong vegetation is measured with in-situ ground-truth accuracy.

## Purpose

The experiment compares 30 m HLS-derived NDVI, aggregated to the MODIS grid, against the official MODIS MOD13Q1 250 m NDVI product over Hong Kong for 2024. Agreement supports workflow reliability; disagreement is interpreted through QA, scale, land-cover purity, clouds, and coastal mixed pixels.

## Datasets

| Role | Dataset | Key use |
| --- | --- | --- |
| High-resolution source | `NASA/HLS/HLSL30/v002` | Landsat HLS NDVI, red `B4`, NIR `B5`. |
| High-resolution source | `NASA/HLS/HLSS30/v002` | Sentinel-2 HLS NDVI, red `B4`, NIR `B8A` by default. |
| Official VI product | `MODIS/061/MOD13Q1` | 16-day Terra NDVI at 250 m, scaled by `0.0001`. |
| Land-cover strata | `ESA/WorldCover/v200` | Static 2021 class purity at the MODIS grid. |

## Reproduction

Smoke mode starts with April-June 2024:

```bash
python scripts/hk_ndvi_v03_export.py \
  --mode smoke \
  --year 2024 \
  --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

Full-year mode uses all 2024 MODIS windows:

```bash
python scripts/hk_ndvi_v03_export.py \
  --mode full \
  --year 2024 \
  --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

If an annual GeoTIFF export repeatedly fails with memory pressure, submit only
the affected image exports as deterministic bbox tiles. This is a fallback for
Drive evidence and QA; it does not change the default canonical file names:

```bash
python scripts/hk_ndvi_v03_export.py \
  --mode full \
  --year 2024 \
  --images-only \
  --image-exports hls_agg250,diff,valid_count \
  --tile-grid 2x2 \
  --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

Monitor Earth Engine task states and write a durable task-status snapshot:

```bash
python scripts/hk_ndvi_v03_monitor_tasks.py \
  --manifest outputs/hk_ndvi_product_validation_v03/manifest.json \
  --out outputs/hk_ndvi_product_validation_v03 \
  --json
```

After Earth Engine tasks complete, use the Google Drive connector to download the exported files into:

```text
outputs/hk_ndvi_product_validation_v03/raw_drive/
```

Then analyze and plot:

```bash
python scripts/hk_ndvi_v03_analyze_drive_exports.py \
  --raw-dir outputs/hk_ndvi_product_validation_v03/raw_drive \
  --out outputs/hk_ndvi_product_validation_v03 \
  --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION \
  --json

python scripts/hk_ndvi_v03_make_figures.py \
  --input outputs/hk_ndvi_product_validation_v03/analysis \
  --out outputs/hk_ndvi_product_validation_v03/figures \
  --json
```

## Expected Artifacts

CSV exports:

- `hk_v03_hls_modis_window_metrics_2024`
- `hk_v03_hls_modis_pixel_samples_2024`
- `hk_v03_hls_modis_landcover_metrics_2024`
- `hk_v03_hls_modis_regional_timeseries_2024`

GeoTIFF exports:

- `hk_v03_annual_hls30_ndvi_mean_2024`
- `hk_v03_annual_hls_agg250_ndvi_mean_2024`
- `hk_v03_annual_modis250_ndvi_mean_2024`
- `hk_v03_annual_diff_hlsagg_minus_modis_2024`
- `hk_v03_valid_count_250m_2024`

## Skill Reliability Checklist

The recipe file in this directory is the canonical contract. A skill-generated workflow should match it on:

- HLS dataset IDs and NDVI band choices;
- MODIS dataset ID, `NDVI` band, and `0.0001` scale factor;
- HLS `Fmask` and MODIS `SummaryQA`/`DetailedQA` masking;
- MODIS 16-day temporal windows;
- HLS-to-MODIS grid aggregation before comparison;
- deterministic Google Drive folder and export prefixes;
- pixel sample schema and claim boundary wording.

If a generated workflow misses one of those items, the demo report should call it a v0.4 gap rather than hiding it.

## Current Status

Status: `Partial`: full-year CSV evidence complete; annual GeoTIFF verification partially complete.

The Google Drive connector has read back the required full-year CSV exports from `GEE_SKILL_V03_HK_NDVI_VALIDATION`. Local analysis on those Drive-downloaded tables produced:

| Metric | Value |
| --- | ---: |
| Matched samples | 5,575 |
| Bias, HLS - MODIS | -0.025 |
| MAE | 0.073 |
| RMSE | 0.111 |
| Pearson r | 0.870 |
| Spearman rho | 0.859 |

Land-cover stratification is available from the full-year export: vegetation-dominated pixels have the strongest agreement, while coastal/water-adjacent pixels have the weakest agreement. Some annual GeoTIFF attempts exposed reusable GEE engineering failures: product-grid transform errors, out-of-memory annual stacks, and missing default projections before `reduceResolution`. Replacement tasks are tracked in `outputs/hk_ndvi_product_validation_v03/task_status_latest.json`. The demo should become `Golden` only after the replacement annual GeoTIFF exports are verified through terminal Earth Engine state and Drive readback.
