# Dataset Card: Global Accessibility to Cities 2015

source_id: dataset-accessibility-to-cities-2015
source_type: official-dataset-card
primary_status: canonical
dataset_id: Oxford/MAP/accessibility_to_cities_2015_v1_0
title: Global Accessibility to Cities 2015
provider: University of Oxford Malaria Atlas Project
gee_url: https://developers.google.com/earth-engine/datasets/catalog/Oxford_MAP_accessibility_to_cities_2015_v1_0
source_url: https://developers.google.com/earth-engine/datasets/catalog/Oxford_MAP_accessibility_to_cities_2015_v1_0
temporal_coverage: 2015 static surface
spatial_resolution: approximately 1km
bands: accessibility
qa_bands:
common_uses: accessibility covariate, travel time to cities, regional context, zonal statistics
recommended_tasks: zonal_statistics, export_image
scale_notes: Use approximately 1km or coarser aggregation; document transformations such as inverse travel time.
projection_notes: Use explicit CRS/scale when combining with annual rasters or administrative summaries.
license_attribution: Accessibility to Cities / MAP terms and citation requirements apply.
last_checked: 2026-07-01
risk_level: medium

## Use

Use `Oxford/MAP/accessibility_to_cities_2015_v1_0` for static 2015 travel-time context when the study design accepts a non-time-varying accessibility covariate.

## Bands

Core bands: accessibility.

QA or mask bands: none listed in this card.

## Recommended Tasks

- zonal_statistics
- export_image

## Scale and Projection Notes

- Use approximately 1km or coarser aggregation.
- Document transformations such as inverse travel time.

## Known Limitations

- Static 2015 travel-time surface is not a time-varying accessibility series.
- The catalog marks this source as deprecated, so new analyses should record the reason for using it or choose the replacement asset.

## Attribution

Accessibility to Cities / MAP terms and citation requirements apply.
