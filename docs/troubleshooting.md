# Troubleshooting

## Authentication vs Workflow Data

`ee.Number(1).getInfo() == 1` proves OAuth and project initialization. It does not prove that an AOI, dataset, date range, masks, reducer, or export schema is valid.

If an export task is submitted and later fails with `Image.reduceRegions: Image has no bands`, that is a workflow/data preflight issue, not a login issue.

## Hong Kong Boundary Mismatch

Do not silently rely on a public administrative dataset unless its schema has been probed. The earlier GAUL level-2 approach did not expose reliable Hong Kong district names for the smoke workflow. The repository now uses a curated Hong Kong district GeoJSON with a `District` property.

Use:

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope district `
  --district "Central and Western" `
  --json
```

Inspect `sample_district_names` in `preflight_report.json` when district matching fails.

## Empty Collections

- `EMPTY_S2_COLLECTION`: no Sentinel-2 images matched AOI/date.
- `EMPTY_FILTERED_COLLECTION`: images existed before cloud metadata filtering but not after.
- `EMPTY_DYNAMIC_WORLD_COLLECTION`: Dynamic World had no images for AOI/date.
- `NO_NDVI_BAND`: NDVI was not produced after mapping B8/B4 normalized difference.
- `NO_LANDCOVER_LABEL`: expected Dynamic World label band was absent.
- `NO_PROBABILITY_BANDS`: expected Dynamic World probability bands were absent.
- `CLASS_MASK_EMPTY`: land-cover masks had no usable class fraction at the current threshold/AOI.

## Low NDVI

Low all-surface NDVI is expected in mixed urban/coastal AOIs. Compare all-surface, non-water, vegetation, built-up, water fraction, built fraction, and vegetation fraction before making ecological claims.
