# Benchmark Protocol

Last updated: 2026-06-25

This protocol defines how to evaluate `gee-agent-skill` as an agent-native Earth Engine harness without running live Google Earth Engine tasks by default.

The default suite is `evals/benchmark_suite.yml`. Task-family seed files live under `evals/tasks/` for parse-only, plan-only, render/validate, mocked preflight, and retrieval-coverage cases.

## Goals

The benchmark should measure whether the harness can:

- parse supported natural-language requests into reviewable plans;
- select reasonable datasets, recipes, rules, and templates from local evidence;
- recognize multiple task families, including optical indices, thermal products, SAR change, land-cover summaries, zonal statistics, and export-only workflows;
- reject or clarify ambiguous and unsupported requests;
- block unknown dataset IDs that are not present in the reviewed local catalog;
- render scripts that pass validation;
- retrieve dataset, operator, recipe, failure, and export evidence for exportable tasks;
- prove placeholder AOI/export context is blocked before live preflight;
- prove empty image collections stop at preflight rather than reaching export;
- preserve the boundary between dry run, preflight, and live export;
- keep credentials and credential paths out of traces.

It should not score scientific NDVI quality unless a separate domain-reviewed protocol is added.

## Default Offline Gate

Run from the repository root inside an activated virtual environment:

```bash
python -m pytest
gee-skill smoke-test --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
python -m build --sdist --wheel
```

These commands should not submit live Earth Engine export tasks.

## Golden Example Checks

### v0.1 Whole-AOI NDVI

Expected evidence:

- deterministic route for January 2024 Hong Kong NDVI CSV;
- generated script path under `outputs/scripts/`;
- dry-run report with no Earth Engine contact;
- output schema documented in `docs/v01_hk_january_ndvi.md`.

### v0.2 Land-Cover-Aware NDVI

Expected evidence:

- plan includes Sentinel-2 SR Harmonized and Dynamic World;
- land-cover is used for masks and strata, not boundaries;
- dry run renders a CSV workflow without submitting an export;
- interpretation warns that sparse classes can produce null values.

### v0.3 16-Day NDVI

Expected evidence:

- `schema_version: gee-plan/v0.3`;
- selected template `hk_2024_16day_ndvi_csv`;
- `date_start: 2024-01-01`, `date_end: 2025-01-01`, and `temporal_cadence_days: 16`;
- expected 23 export rows;
- validation passes before live use.

## Default Benchmark Coverage

`evals/benchmark_suite.yml` currently contains 22 offline cases:

- retrieval for Sentinel-2 and MODIS/LST evidence;
- corpus coverage for dataset, operator, recipe, failure, and export evidence;
- planning for EVI CSV, NDWI GeoTIFF, NDBI CSV, Landsat LST CSV, Sentinel-1 flood GeoTIFF, Dynamic World land-cover summary, zonal statistics CSV, and standalone image GeoTIFF export;
- ambiguity handling for missing AOI and missing time range;
- unknown-dataset blocking for a made-up dataset ID;
- unsupported-task recovery for crop yield;
- mocked preflight blocks for placeholder context and empty image collections;
- render/validate checks for v0.1, v0.2, v0.3, smoke, and monthly NDVI templates.

## Optional Live Gate

Do not run this gate unless the user explicitly asks for live Earth Engine verification and provides a project id through their own local environment.

```bash
gee-skill preflight-plan outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --json
gee-skill run-plan outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --confirm-live --json
gee-skill monitor-exports --project "$EE_PROJECT" --timeout 0 --json
```

Live preflight may contact Earth Engine. `run-plan --confirm-live` may create an export task. Treat task submission as workflow evidence only; it is not scientific validation.

## Suggested Metrics

| Metric | Measurement |
| --- | --- |
| Plan parse pass rate | Supported prompts produce `ok: true` JSON and expected plan fields. |
| Ambiguity handling | Underspecified prompts return a structured missing-field error. |
| Unsupported-task recovery | Unsupported prompts return closest supported recipes and do not render unsafe scripts. |
| Validation pass rate | Rendered scripts pass static and semantic validators. |
| Boundary compliance | Dry-run commands do not require credentials or start exports. |
| Credential hygiene | Trace files do not contain tokens, service account JSON, private keys, or credential paths. |
| Regression stability | Golden examples keep expected schema, template, and output-selector contracts. |

## Reporting Template

For each benchmark run, record:

- date, commit, Python version, and OS;
- command list;
- pass/fail summary;
- total, passed, failed, and failure id summary;
- failed cases and structured error codes;
- expected intent, missing fields, recipe, validation status, and trace-artifact status where applicable;
- whether live Earth Engine was not run, preflight-only, or export-confirmed;
- known limitations and next regression target.
