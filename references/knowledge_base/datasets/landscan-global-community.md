# Dataset Card: LandScan Population Data Global 1km

source_id: dataset-landscan-global-community
source_type: community-dataset-card
primary_status: community
dataset_id: projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL
title: LandScan Population Data Global 1km
provider: Oak Ridge National Laboratory via Awesome GEE Community Catalog
gee_url: https://developers.google.com/earth-engine/datasets/catalog/projects_sat-io_open-datasets_ORNL_LANDSCAN_GLOBAL
source_url: https://developers.google.com/earth-engine/datasets/catalog/projects_sat-io_open-datasets_ORNL_LANDSCAN_GLOBAL
temporal_coverage: catalog states 2000-2023; live collection metadata exposed 2000-2024 on 2026-07-25, so verify expected years at runtime
spatial_resolution: 30 arc-seconds; catalog display reports 1000m
bands: b1
qa_bands:
common_uses: annual population counts, population density, exposure, zonal statistics, change detection
recommended_tasks: annual_endmember_transition, zonal_statistics, change_detection, export_image
scale_notes: b1 is a population count, not density; divide by native pixel area, aggregate density area-weightedly, then multiply by target pixel area.
projection_notes: Use one explicit equal-area target CRS and affine transform; verify regional population conservation after reprojection.
license_attribution: CC BY 4.0; clearly attribute Oak Ridge National Laboratory / LandScan and the applicable annual dataset citation.
last_checked: 2026-07-25
risk_level: high

## Use

Call `ee.ImageCollection("projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL")` directly, filter one expected year at a time, and select `b1`.

## Known Limitations

- This is a community-catalog asset and is not managed by Google Earth Engine.
- Catalog prose can lag live asset metadata; persist observed image years and band names in preflight evidence.
- LandScan values are modeled population estimates.
- A resampled raster is not acceptable until population-conservation error has been checked for the study region.
