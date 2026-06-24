# Case Study: Hong Kong January 2024 Whole-AOI NDVI

Last updated: 2026-06-24

## Role In The Project

This v0.1 case study is a golden regression example for the general `gee-agent-skill` harness. It is not the full scope of the project and should not be presented as a standalone Hong Kong vegetation analysis product.

## Request

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

## Harness Behavior Under Test

- natural-language routing;
- local evidence retrieval;
- plan generation;
- Earth Engine Python template rendering;
- static and semantic validation;
- dry-run trace creation;
- live preflight before export;
- explicit `--confirm-live` gate;
- export monitoring.

## Data And Output

- AOI: curated Hong Kong boundary GeoJSON.
- Dataset: `COPERNICUS/S2_SR_HARMONIZED`.
- Metric: NDVI from Sentinel-2 near-infrared and red bands.
- Time range: `2024-01-01` to `2024-02-01`.
- Output: one CSV row for whole-Hong-Kong mean NDVI and image-count diagnostics.

## Reproduction

Offline dry run:

```bash
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
```

Live preflight and export require a user-owned Earth Engine account, Google Cloud project, local OAuth, quota review, and explicit confirmation. Do not run live commands without user approval.

## Interpretation Boundary

The output is an all-surface whole-AOI engineering example. Water, built-up surfaces, cloud filtering, and AOI composition can lower aggregate NDVI. Treat the result as workflow evidence unless a domain-reviewed scientific analysis is added.

## Regression Value

This example catches regressions in the smallest complete path from request to CSV export contract. It is useful because it is simple, not because it exhausts the harness capability.
