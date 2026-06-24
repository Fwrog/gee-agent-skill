# Dataset Card: ESA WorldCover 10m v200

source_id: dataset-esa-worldcover-v200
source_type: official-dataset-card
primary_status: canonical
dataset_id: ESA/WorldCover/v200
title: ESA WorldCover 10m v200
provider: ESA
gee_url: https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
source_url: https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
temporal_coverage: 2021 static product
spatial_resolution: 10m
bands: Map
qa_bands: none
common_uses: static land-cover reference, sanity-check land-cover masks
recommended_tasks: landcover_summary, landcover_stratified_statistics
scale_notes: Use 10m for class summaries unless coarsening for large AOIs.
projection_notes: Document when using static land cover with non-2021 imagery.
license_attribution: ESA WorldCover license terms apply.
last_checked: 2026-06-21
risk_level: medium

## Use

Use `ESA/WorldCover/v200` for static land-cover reference, sanity-check land-cover masks.

## Bands

Core bands: Map.

QA or mask bands: none.

## Recommended Tasks

- landcover_summary
- landcover_stratified_statistics

## Scale and Projection Notes

- Use 10m for class summaries unless coarsening for large AOIs.
- Document when using static land cover with non-2021 imagery.

## Known Limitations

- Static 2021 map is not time-matched to arbitrary analysis windows.

## Attribution

ESA WorldCover license terms apply.
