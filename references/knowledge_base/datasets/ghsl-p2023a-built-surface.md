# Dataset Card: GHSL P2023A Built-up Surface Grid

source_id: dataset-ghsl-p2023a-built-surface
source_type: official-dataset-card
primary_status: canonical
dataset_id: JRC/GHSL/P2023A/GHS_BUILT_S
title: GHSL P2023A Built-up Surface Grid
provider: European Commission Joint Research Centre
gee_url: https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S
source_url: https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S
temporal_coverage: 1975-2030 in 5-year epochs
spatial_resolution: 100m
bands: built_surface, built_surface_nres
qa_bands:
common_uses: built-up surface, non-residential built-up proxy, settlement structure, urbanization context
recommended_tasks: zonal_statistics, change_detection, export_image
scale_notes: Use 100m or coarser aggregation; document any interpolation before annual summaries.
projection_notes: Use explicit CRS/scale when aggregating to administrative zones or analytical grids.
license_attribution: European Commission JRC GHSL terms apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `JRC/GHSL/P2023A/GHS_BUILT_S` for built-up surface and non-residential built-up context at 5-year epochs.

## Bands

Core bands: built_surface, built_surface_nres.

QA or mask bands: none listed in this card.

## Recommended Tasks

- zonal_statistics
- change_detection
- export_image

## Scale and Projection Notes

- Use 100m or coarser aggregation.
- Document any interpolation before annual summaries.

## Known Limitations

- Epoch spacing is 5 years; annual analyses need an explicit interpolation or nearest-epoch policy.
- Built-up surface is not equivalent to land-cover class or building footprint truth.

## Attribution

European Commission JRC GHSL terms apply.
