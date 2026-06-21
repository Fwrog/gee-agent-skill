# Live Smoke Test Protocol

The v0.1 live smoke test is intentionally small:

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

Prerequisites:

- Register for Earth Engine.
- Configure a Google Cloud Project with Earth Engine API access.
- Authenticate locally.
- Install live dependencies.

Stage 1: OAuth connectivity

```bash
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

Expected output is `1`. This proves authentication and project initialization only; it does not prove that a geospatial workflow has valid data.

Stage 2: data-aware preflight

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope hong-kong `
  --json
```

Preflight checks initialization, the whole-Hong-Kong AOI source, feature count, area, Sentinel-2 image counts before and after cloud metadata filtering, NDVI band creation, and a tiny sanity statistic. It writes `preflight_report.json` and does not create an export task.

Stage 3: live export

```powershell
pip install -e ".[earthengine]"
earthengine authenticate --auth_mode=localhost
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --project $env:EE_PROJECT `
  --confirm-live `
  --run-id hk-2024-01-ndvi-v01 `
  --json
```

The command writes a run trace. If live access is missing, it fails with structured `AUTH_ERROR` or `PROJECT_ERROR` guidance and does not require credentials in the repository.

Monitor tasks:

```bash
gee-skill monitor-exports --project $env:EE_PROJECT --json
```

## Hong Kong Boundary Troubleshooting

`Image.reduceRegions: Image has no bands.` is not an authentication failure when the task has already been submitted. It means the workflow reached Earth Engine but the image entering a reducer had no bands, commonly because the AOI/district filter or image filters produced an empty collection.

The previous GAUL level-2 approach is unsuitable for Hong Kong district smoke tests: live probing showed one Hong Kong feature with `ADM2_NAME` equal to `Administrative unit not available`, so `Central and Western` matched zero features. The default workflow now uses `references/boundaries/hk_18_districts.geojson`, a curated official Hong Kong district boundary GeoJSON with 18 district features and the `District` property. The preflight maps `Central and Western` to the source value `Central & Western`.

For v0.1, the workflow unions all curated Hong Kong district features and exports one whole-Hong-Kong CSV row. District-level monthly output remains v0.2.

Boundary-specific probe:

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope district `
  --district "Central and Western" `
  --json
```

If preflight returns:

- `EMPTY_AOI`: the boundary file is missing, empty, or filtered to zero features.
- `DISTRICT_NOT_FOUND`: use one of the sampled `District` names in `preflight_report.json`.
- `EMPTY_IMAGE_COLLECTION`: inspect the AOI, date range, or cloud threshold.
- `EMPTY_FILTERED_COLLECTION`: images exist before cloud filtering but not after the cloud metadata threshold.
- `NO_NDVI_BAND`: verify Sentinel-2 B8/B4 bands and the NDVI mapping step.
- `NULL_NDVI_STAT`: NDVI exists but the sanity reducer returned no value; inspect cloud masks, AOI geometry, scale, and valid-pixel coverage.
