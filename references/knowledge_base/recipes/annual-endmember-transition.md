# Recipe Card: annual-endmember-transition

source_id: recipe-annual-endmember-transition
source_type: curated-recipe-card
primary_status: curated
recipe_id: annual-endmember-transition
task_type: change_detection
description: Build annual equal-area multi-source features, select stable endpoint samples, train a shared classifier, and export yearly probabilities.
required_inputs: aoi, time_range, annual_categorical_landcover, output
optional_inputs: activity_collection, population_collection, accessibility_image, grid, endpoint_rules, random_seed
candidate_datasets: NASA/HLS/HLSL30/v002, NASA/HLS/HLSS30/v002, projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL, NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG, external/annual-categorical-landcover
default_dataset_policy: Use HLS v002 for annual optical features; prefer one consistently processed monthly activity collection for multi-year aggregation; verify every community or external asset year and band before use; aggregate counts and categories with their declared semantics.
template: recipes/annual_endmember_transition
preflight_profile: optical_index
validation_profile: annual_endmember_transition
output_schema: year, feature_stack, endpoint_samples, urban_probability, model_uncertainty, valid_observation_count, export_task_description
live_risk_level: high
last_checked: 2026-07-25
risk_level: high

## Use

Use this recipe to construct a reviewable annual feature stack on one fixed equal-area grid, derive stable high-confidence endpoint samples across years, train one shared binary Random Forest, and export annual probability and uncertainty rasters.

## Safety Contract

- Declare every expected year and verify annual coverage before export.
- Pin one CRS and affine transform for all annual feature images.
- Verify that Earth Engine can parse the selected CRS identifier. In
  particular, encode EPSG:6933 with its reviewed WKT1 definition because the
  short identifier is not currently accepted by Earth Engine.
- Convert population counts to density before area-weighted aggregation; verify population conservation independently.
- Aggregate categorical land cover as per-class area fractions or with nearest-neighbour semantics, never bilinear interpolation of class codes.
- Treat community-catalog metadata as drift-prone and verify asset ID, band, year coverage, license, and image time properties.
- Prefer `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG` for a consistently processed multi-year activity series. If annual V2.1 and V2.2 products are joined, declare a cross-version policy and verify each expected year; V2.2 alone starts in 2022.
- Export only derived products from private assets unless redistribution permission is documented.

## Limitations

- This is a generic render-and-validate recipe, not a public live-verified or scientifically validated result.
- Endpoint thresholds and class mappings are study-specific inputs.
- Classifier probability near 0.5 is model ambiguity unless independent evidence supports a mixed-space interpretation.
