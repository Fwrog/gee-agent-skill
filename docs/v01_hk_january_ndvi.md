# v0.1 Hong Kong January NDVI CSV

The v0.1 release target is a small end-to-end live workflow:

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

It proves the main product path without requiring full district-level production output:

```text
natural language -> RAG -> plan -> template -> validation -> preflight -> live export -> monitor -> trace
```

## Why Whole Hong Kong

The previous district workflow exposed a live data failure, `Image.reduceRegions: Image has no bands.` The root cause was workflow/data preflight, not authentication. v0.1 avoids blocking on district naming by using the curated Hong Kong district GeoJSON as a whole-Hong-Kong AOI and exporting one CSV row. Full 2024 monthly district-level NDVI is planned for v0.2.

## Offline Dry Run

```powershell
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --dry-run `
  --json
```

This writes a run trace and `outputs/scripts/hk_2024_01_ndvi_csv.py` without contacting Earth Engine.

## Live Preflight

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope hong-kong `
  --json
```

Preflight must pass before live export. It reports AOI count/area, Sentinel-2 image counts, NDVI bands, a safe mean NDVI probe, and the final export decision.

## Live Export

```powershell
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --project $env:EE_PROJECT `
  --confirm-live `
  --run-id hk-2024-01-ndvi-v01 `
  --json
```

The generated CSV schema is:

```text
aoi_name, year, month, date_start, date_end, mean_ndvi,
image_count_before_cloud_filter, image_count_after_cloud_filter,
dataset_id, scale_m, crs, aoi_source, export_description
```

## Failure Boundary

If AOI, imagery, NDVI band creation, or the sanity reducer fails, the command returns a structured error before `task.start()`. Do not treat an unauthenticated failure as live workflow success, and do not treat export submission as scientific validation of the result.
