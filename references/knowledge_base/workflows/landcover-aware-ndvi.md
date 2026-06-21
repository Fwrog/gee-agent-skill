# Workflow Pattern: Land-Cover-Aware NDVI Diagnostics

source_id: workflow-landcover-aware-ndvi
source_type: curated-workflow-pattern
primary_status: curated
source_url: https://developers.google.com/earth-engine/tutorials/community/introduction-to-dynamic-world-pt-1
last_checked: 2026-06-21
operator_chain: AOI boundary -> Sentinel-2 filter/mask/NDVI -> Dynamic World filter/probability masks -> reducer diagnostics -> CSV export
risk_level: medium

## Pattern

Use administrative or user-supplied geometry to define where statistics are computed. Use Dynamic World probabilities to define masks and interpretation strata such as water, non-water, vegetation, built-up, trees, grass, shrub/scrub, and bare.

## Output Guidance

Export all-surface, non-water, vegetation, built-up, and class-specific NDVI statistics alongside water, built, vegetation, trees, and grass fractions. Include Sentinel-2 image counts, Dynamic World image count, probability threshold, dataset ids, scale, CRS, and export description.

## Failure Cases

known_failure: CLASS_MASK_EMPTY

Sparse or low-confidence classes should produce null class-specific NDVI and warnings. The workflow should only fail when core preflight gates fail: empty AOI, empty S2, empty Dynamic World, missing NDVI, missing label, or missing probability bands.
