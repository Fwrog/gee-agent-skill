# Case Study: Hong Kong January 2024 Land-Cover-Aware NDVI

Last updated: 2026-06-24

## Role In The Project

This v0.2 case study is a golden regression example for the general `gee-agent-skill` harness. It extends the v0.1 whole-AOI workflow by adding land-cover masks and strata. It is not the full scope of the project.

## Request

```text
Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.
```

## Harness Behavior Under Test

- plan-first workflow;
- distinction between AOI boundaries and land-cover interpretation layers;
- Sentinel-2 and Dynamic World dataset selection;
- land-cover-aware template rendering;
- preflight checks for both optical imagery and land-cover data;
- structured CSV schema for all-surface, non-water, land-only, vegetation, built, bare, and class-fraction diagnostics.

## Data And Output

- AOI: curated Hong Kong boundary GeoJSON.
- NDVI source: `COPERNICUS/S2_SR_HARMONIZED`.
- Land-cover source: `GOOGLE/DYNAMICWORLD/V1`.
- Optional static reference: `ESA/WorldCover/v200`, documented but not primary for time-matched masking.
- Output: one CSV row with aggregate NDVI, class-specific NDVI, class fractions, and image-count diagnostics.

## Reproduction

Offline plan and dry run:

```bash
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
```

Live preflight and export require a user-owned Earth Engine account, Google Cloud project, local OAuth, quota review, and explicit confirmation. Do not run live commands without user approval.

## Interpretation Boundary

Dynamic World is probabilistic. Low-confidence or sparse classes may produce null class-specific NDVI. Class fractions and preflight warnings should be reviewed before interpreting values. This case study proves that the harness can carry land-cover-aware workflow structure; it does not prove policy-ready vegetation conclusions.

## Regression Value

This example catches regressions in plan review, land-cover dataset handling, output-schema stability, and the boundary between administrative geometry and thematic interpretation.
