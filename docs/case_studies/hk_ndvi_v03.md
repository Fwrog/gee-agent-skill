# Case Study: v0.3 Hong Kong 2024 16-Day NDVI

## Natural-Language Prompt

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

## What This Case Study Proves

This is the strongest current golden example for the v0.3 harness loop:

```text
natural language -> gee-plan/v0.3 -> render .py -> validate -> preflight -> confirmed export -> monitor -> trace/evidence
```

It proves the project can run a reviewable, traceable, live-gated Earth Engine workflow from a natural-language request. It does not prove scientific validity of the NDVI product.

## Generated Plan

The v0.3 plan uses:

- `schema_version: gee-plan/v0.3`
- task type: `vegetation_index`
- metric: `NDVI`
- AOI: Hong Kong
- time range: `2024-01-01` to `2025-01-01`
- temporal cadence: 16 days
- output: Drive CSV
- template: `hk_2024_16day_ndvi_csv`

The plan remains editable before execution. Live execution requires explicit project and confirmation flags.

## Dataset Choices

- Primary dataset: `COPERNICUS/S2_SR_HARMONIZED`
- Boundary: curated Hong Kong 18 Districts GeoJSON under `references/boundaries`
- NDVI bands: `B8` and `B4`
- Masking: Sentinel-2 SCL-oriented masking in the rendered template

## Preflight Checks

The live adapter checks representative anchor months before export:

- January 2024
- July 2024

The preflight verifies AOI/data availability, expected row count, export metadata, and enough image/band availability to allow export.

## Export Result

Observed export metadata:

- Export description: `hk_2024_16day_ndvi`
- Drive folder: `gee_exports`
- File prefix: `hk_2024_16day_ndvi`
- Expected CSV data rows: 23

Sanitized evidence is committed in [docs/evidence/v03_hk_2024_16day_ndvi](../evidence/v03_hk_2024_16day_ndvi/README.md).

## Failure Avoided

The workflow avoids common agent-generated GEE failures:

- no direct live execution without `--confirm-live`;
- no export before preflight passes;
- no claim of success without a monitored export task;
- no committed credentials or credential paths;
- no large `getInfo()` result used as the main computation path.

## Interpretation Limits

The CSV values are whole-Hong-Kong all-surface means. Water and dense built-up areas are included, and some periods have low usable image counts after cloud filtering. Use water masks, land-cover stratification, district-level aggregation, or domain review before treating the output as vegetation science.

## Trace Artifacts

The private local run trace writes:

- `task_plan.yaml`
- `generated_script.py`
- `validation_report.json`
- `dry_run_report.json`
- `preflight_report.json`
- `live_run_report.json`
- `export_tasks.json`
- `final_report.md`

The public evidence bundle records only sanitized task metadata and CSV output.
