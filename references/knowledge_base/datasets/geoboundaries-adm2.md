# Dataset Card: geoBoundaries ADM2 Administrative Boundaries

source_id: dataset-geoboundaries-adm2
source_type: official-dataset-card
primary_status: canonical
dataset_id: WM/geoLab/geoBoundaries/600/ADM2
title: geoBoundaries ADM2 Administrative Boundaries
provider: William & Mary geoLab
gee_url: https://developers.google.com/earth-engine/datasets/catalog/WM_geoLab_geoBoundaries_600_ADM2
source_url: https://developers.google.com/earth-engine/datasets/catalog/WM_geoLab_geoBoundaries_600_ADM2
temporal_coverage: Static boundary compilation; check catalog version metadata before use
spatial_resolution: Vector administrative boundaries
bands:
qa_bands:
common_uses: administrative boundaries, zonal statistics, public boundary substitute, regional filtering
recommended_tasks: zonal_statistics, export_table
scale_notes: Reducer scale comes from the raster being summarized, not the vector boundary dataset.
projection_notes: Validate geometry validity, simplify only intentionally, and preserve boundary-source metadata in outputs.
license_attribution: geoBoundaries license and citation terms apply.
last_checked: 2026-07-01
risk_level: high

## Use

Use `WM/geoLab/geoBoundaries/600/ADM2` when a public administrative boundary substitute is acceptable for filtering or exploratory zonal statistics.

## Bands

Core bands: none; this is a FeatureCollection.

QA or mask bands: none.

## Recommended Tasks

- zonal_statistics
- export_table

## Scale and Projection Notes

- Reducer scale comes from the raster being summarized, not the vector boundary dataset.
- Preserve boundary-source metadata in outputs.

## Known Limitations

- Public boundary compilations may not match authoritative legal boundaries or local county definitions.
- Do not claim official county-scale results unless the boundary source is authority-matched for the study.

## Attribution

geoBoundaries license and citation terms apply.
