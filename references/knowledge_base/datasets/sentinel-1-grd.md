# Dataset Card: Sentinel-1 GRD

source_id: dataset-sentinel-1-grd
source_type: official-data-catalog
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
retrieved_at: 2026-06-21
primary_status: canonical
dataset_id: COPERNICUS/S1_GRD
platform: Sentinel-1
sensor: SAR
risk_level: low

## Use

Collection id: `COPERNICUS/S1_GRD`.

Filter by instrument mode, polarization, orbit pass, resolution, date, and AOI. The Earth Engine catalog describes preprocessing and log scaling. Avoid mixing linear and dB assumptions when doing change detection.

## Workflow Notes

- Use consistent orbit direction when comparing dates.
- Use matching polarizations, often `VV` and/or `VH`.
- Document whether change is computed in dB or converted linear space.

