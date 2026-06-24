# v0.3 Evidence: Hong Kong 2024 16-Day NDVI

This folder is a sanitized, commit-addressable evidence bundle for the v0.3 golden workflow:

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

It is intentionally not a credential or account artifact. It does not include a Google Cloud project id, credential path, OAuth token, service account JSON, refresh token, or local Earth Engine credential file.

## Workflow Evidence

- Plan schema: `gee-plan/v0.3`
- Template: `hk_2024_16day_ndvi_csv`
- Dataset: `COPERNICUS/S2_SR_HARMONIZED`
- AOI source: Home Affairs Department Hong Kong administrative district boundary GeoJSON
- Scale: 10 m
- CRS: `EPSG:4326`
- Temporal cadence: 16 days
- Expected rows: 23
- Export description: `hk_2024_16day_ndvi`
- Drive folder: `gee_exports`
- File prefix: `hk_2024_16day_ndvi`

## Public Task Metadata

The local live trace observed a matching Earth Engine task after script execution:

| Field | Value |
| --- | --- |
| task id | `6VQOYD567CL4HVSEON6GOMMC` |
| description | `hk_2024_16day_ndvi` |
| observed state | `READY` |
| creation timestamp ms | `1782200432930` |
| creation time UTC | `2026-06-23T07:40:32.930000+00:00` |
| error message | `null` |

The task metadata proves task submission was observed. It does not prove scientific correctness or Google Drive delivery by itself.

## CSV Evidence

- File: `hk_2024_16day_ndvi.csv`
- SHA-256: `f1a8502b64026f621ed8dd96af9dae80f2abe32494796b2af88d15a8f5d80475`
- Rows including header: 24
- Data rows: 23

The NDVI values are whole-Hong-Kong all-surface means over the curated administrative geometry. Water and dense built-up pixels are included. Treat this output as workflow proof and demo data, not as a scientific vegetation conclusion.
