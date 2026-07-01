# Dataset Card: WorldPop Global Project Population Data 100m

source_id: dataset-worldpop-100m-pop
source_type: official-dataset-card
primary_status: canonical
dataset_id: WorldPop/GP/100m/pop
title: WorldPop Global Project Population Data 100m
provider: WorldPop / University of Southampton
gee_url: https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop
source_url: https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop
temporal_coverage: 2000-2021 annual population estimates
spatial_resolution: 100m
bands: population
qa_bands:
common_uses: population validation, population exposure, settlement context, zonal statistics
recommended_tasks: zonal_statistics, change_detection, export_image
scale_notes: Use 100m or coarser aggregation with population-preserving reducers such as sum.
projection_notes: Use explicit CRS/scale and document whether values are summed or averaged.
license_attribution: WorldPop terms and citation requirements apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `WorldPop/GP/100m/pop` for population context, exposure summaries, or validation checks when modeled population estimates are appropriate.

## Bands

Core bands: population.

QA or mask bands: none listed in this card.

## Recommended Tasks

- zonal_statistics
- change_detection
- export_image

## Scale and Projection Notes

- Use 100m or coarser aggregation.
- Use population-preserving reducers such as sum when summarizing counts.

## Known Limitations

- Population estimates are modeled and should be treated as validation or context unless the study design accepts WorldPop as a source metric.
- Catalog coverage ends at 2021, so later years require a different validation source or an explicit missing-data note.

## Attribution

WorldPop terms and citation requirements apply.
