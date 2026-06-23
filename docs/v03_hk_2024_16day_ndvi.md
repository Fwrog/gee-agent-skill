# v0.3 Hong Kong 2024 16-Day NDVI

This is the v0.3 golden example for a non-January, non-demo Google Earth Engine workflow:

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

It demonstrates the general harness path from natural language to an editable plan, rendered Earth Engine Python script, offline validation report, dry-run contract, live preflight, confirmed export, and task monitoring. It does not start an Earth Engine export unless a later live command supplies a project and explicit confirmation.

![Hong Kong 2024 16-day NDVI workflow](../assets/images/hk-2024-16day-ndvi-workflow.png)

## Offline Reproduction

```bash
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json

gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json

gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml \
  --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py \
  --json

gee-skill validate outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

Expected offline result:

- The plan has `schema_version: gee-plan/v0.3`.
- The plan marks the request as a golden example.
- The selected dataset is `COPERNICUS/S2_SR_HARMONIZED`.
- The execution template is `hk_2024_16day_ndvi_csv`.
- The rendered script validates with `agent_script_contract`, `optical_index`, `sentinel2_ndvi_monthly_zonal`, `vegetation_index_ndvi`, and `export_table_csv`.
- The dry-run report has `contacted_earth_engine: false`.

## Workflow Contract

The rendered script uses:

- Curated Hong Kong boundary GeoJSON as the whole-Hong-Kong AOI.
- Sentinel-2 SR Harmonized.
- `START_DATE = "2024-01-01"` and `END_DATE = "2025-01-01"`.
- `CADENCE_DAYS = 16`, producing 23 server-side periods for leap-year 2024.
- SCL masking before NDVI compositing.
- `normalizedDifference(["B8", "B4"])`.
- Server-side `reduceRegion` for whole-AOI mean NDVI.
- Stable `Export.table.toDrive(..., fileFormat="CSV", selectors=EXPORT_SELECTORS)`.

## Live Preflight And Export

After local OAuth and project setup:

```bash
gee-skill preflight-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --json
```

The v0.3 adapter supports this template directly. It checks January and July anchor months before export and reports:

- Earth Engine initialization status;
- Hong Kong boundary feature count and area;
- Sentinel-2 image count before and after cloud metadata filtering;
- NDVI band availability;
- a small mean-NDVI sanity statistic;
- expected export rows, which should be `23` for 2024 at 16-day cadence.

Only after preflight passes:

```bash
gee-skill run-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --run-id hk-2024-16day-ndvi-v03-live-export-check \
  --json
```

Monitor without starting another task:

```bash
gee-skill monitor-exports --project "$EE_PROJECT" --timeout 0 --json
```

Expected export metadata:

```text
description: hk_2024_16day_ndvi
Drive folder: gee_exports
file prefix: hk_2024_16day_ndvi
```

## CSV Schema

The CSV export selectors are:

- `aoi_name`
- `year`
- `period_index`
- `date_start`
- `date_end`
- `temporal_cadence_days`
- `mean_ndvi`
- `image_count_before_cloud_filter`
- `image_count_after_cloud_filter`
- `dataset_id`
- `scale_m`
- `crs`
- `aoi_source`
- `export_description`

## Output Sanity Checks

A verified exported CSV should have:

- 23 data rows plus one header row;
- `period_index` from `1` through `23`;
- `date_start` beginning at `2024-01-01`;
- final `date_end` equal to `2025-01-01`;
- no missing `mean_ndvi` values;
- `dataset_id` equal to `COPERNICUS/S2_SR_HARMONIZED`;
- `export_description` equal to `hk_2024_16day_ndvi`.

The first verified CSV had this engineering sanity summary:

```text
rows: 23
date coverage: 2024-01-01 to 2025-01-01
mean_ndvi range: -0.066 to 0.358
mean of period means: 0.109
minimum image_count_after_cloud_filter: 2
low-image-count periods: 5, 8
null mean_ndvi rows: 0
```

These values can look low compared with a vegetation-only NDVI series. That is expected for this template because it computes a whole-Hong-Kong all-surface mean over the curated administrative geometry. The geometry includes water and dense built-up areas, and some 16-day periods have few usable images after cloud filtering. Treat the CSV as an engineering output and workflow proof; use land/water masks, land-cover stratification, or domain review before making scientific claims.

## Live Boundary

Live execution is intentionally separate from planning and rendering. Before starting an export, the user must authenticate locally, provide a Google Cloud project, review quota/scale/CRS/export settings, and explicitly confirm live execution. The script itself keeps `task.start()` behind a guarded `main()` entrypoint and does not call `ee.Authenticate()`.

For project-level auth verification:

```bash
gee-skill auth check --project <project-id> --json
```

For task monitoring after a live export is intentionally started:

```bash
gee-skill monitor-exports --project <project-id> --json
```
