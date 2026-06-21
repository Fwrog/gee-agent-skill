# gee-agent-skill

`gee-agent-skill` is a Python-first, Earth-Engine-first research harness for reproducible Google Earth Engine workflows. It plans workflows from task YAML, retrieves local evidence, renders approved Jinja2 Python templates, validates scripts, writes complete run traces, and optionally runs live Earth Engine export tasks after explicit user confirmation.

It supports Sentinel-2 NDVI time series and zonal statistics, land-cover-aware NDVI diagnostics with Dynamic World, Landsat Collection 2 LST, Sentinel-1 before/after change workflows, CSV export monitoring, and evaluation-driven regression tests.

It does not provide Google credentials, replace Earth Engine account setup, prove scientific conclusions, or run live exports without explicit flags.

## Verified and Target Workflows

The verified v0.1 live workflow is deliberately small:

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

This routes through deterministic intent parsing, local RAG evidence, a traceable plan, the `hk_january_2024_ndvi_csv` template, validation, whole-Hong-Kong data preflight, explicit live export, export monitoring, and a run trace.

The v0.2 target workflow is plan-first and land-cover-aware:

```text
Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.
```

This workflow keeps the curated Hong Kong boundary as the AOI and uses Dynamic World only for masks, strata, and interpretation diagnostics. It reports all-surface, non-water, vegetation, built-up, and class-specific NDVI with class fractions, so low all-surface NDVI is not overinterpreted as vegetation condition.

## Quickstart

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json
gee-skill search-docs "Sentinel-2 NDVI reduceRegions export CSV"
gee-skill smoke-test
python -m pytest
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python scripts\ingest_docs.py --docs-dir references\knowledge_base --out references\index\gee_docs_index.json
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill smoke-test
python -m pytest
```

## Credentials

Live Earth Engine commands require a registered Earth Engine account, a Google Cloud Project with Earth Engine API access, and local authentication:

```bash
pip install -e ".[earthengine]"
earthengine authenticate
```

Windows PowerShell:

```powershell
$env:EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
earthengine set_project $env:EE_PROJECT
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

本仓库不提供 Google 凭据。用户需要自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

Never commit service account JSON, OAuth tokens, local credential files, or credential paths.

## Live Workflow Stages

Live Earth Engine work has three separate gates:

1. OAuth connectivity: prove local auth and project initialization work.

```bash
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

Expected output is `1`.

2. Data-aware preflight: check the whole-Hong-Kong AOI, Sentinel-2 image counts, NDVI bands, and a tiny sanity statistic before any export task is created.

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope hong-kong `
  --json
```

This writes `preflight_report.json` under `outputs/runs/<run_id>/`. The default Hong Kong workflow uses the curated official district boundary GeoJSON at `references/boundaries/hk_18_districts.geojson` as a whole-Hong-Kong AOI.

For the v0.2 land-cover-aware workflow, add Dynamic World checks:

```powershell
gee-skill preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope hong-kong `
  --landcover dynamic-world `
  --json
```

This also writes `landcover_diagnostics.json` when Dynamic World diagnostics are available.

3. Live export: start the Drive CSV task only after validation and preflight pass.

```powershell
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --project $env:EE_PROJECT `
  --confirm-live `
  --run-id hk-2024-01-ndvi-v01 `
  --json

gee-skill monitor-exports `
  --project $env:EE_PROJECT `
  --json
```

## Plan-First v0.2 Example

Plan without contacting Earth Engine:

```powershell
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." `
  --plan `
  --json
```

Review the saved plan:

```powershell
gee-skill review-plan outputs/runs/<run_id>/task_plan.yaml
```

Run safe live data probes after local authentication:

```powershell
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --json
```

Only after preflight passes, create the Drive CSV export task:

```powershell
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --confirm-live `
  --json
```

The expected CSV schema includes `all_surface_mean_ndvi`, `non_water_mean_ndvi`, `vegetation_mean_ndvi`, class-specific NDVI fields, class fractions, Sentinel-2 image counts, Dynamic World image count, probability threshold, scale, CRS, and dataset IDs.

## Template-Driven Example

The template benchmark task is:

```text
Compute 2024 monthly mean NDVI for Hong Kong districts and export CSV.
```

Run the offline planning and trace workflow:

```bash
gee-skill plan examples/hk_2024_monthly_ndvi/task.yaml
gee-skill validate outputs/scripts/hk_2024_monthly_ndvi.py --json
gee-skill run outputs/scripts/hk_2024_monthly_ndvi.py --dry-run --json
```

This writes a run directory under `outputs/runs/<run_id>/` with `task.yaml`, `retrieval_trace.json`, `plan.md`, `generated_script.py`, `validation_report.json`, `dry_run_report.json`, `environment.json`, and `final_report.md`.

## Private Live Smoke Test

For v0.1, prefer the `ask` command shown above. The older one-district command remains available for boundary-specific smoke testing:

```bash
gee-skill live-smoke-test \
  --project your-google-cloud-project \
  --confirm-live \
  --smoke-month 1 \
  --smoke-region "Central and Western" \
  --export-folder gee_exports
```

This computes January 2024 NDVI mean for one Hong Kong district and creates a CSV export task. It records `preflight_report.json`, `live_run_report.json`, and `export_tasks.json`. Without credentials or project access, it fails gracefully with `AUTH_ERROR` or `PROJECT_ERROR` guidance. If data preflight fails, it returns a structured preflight error before `task.start()`.

## Commands

- `gee-skill tools`: inspect installed vs exposed harness tools.
- `gee-skill ask "<natural-language task>" --plan --json`: create a reviewable plan only; no Earth Engine contact.
- `gee-skill ask "<natural-language task>" --dry-run --json`: plan, render, validate, and trace offline.
- `gee-skill ask "<natural-language task>" --project <id> --confirm-live --json`: preflight and submit a supported live export after explicit confirmation.
- `gee-skill review-plan outputs/runs/<run_id>/task_plan.yaml`: inspect interpreted intent, datasets, output schema, checks, and limitations.
- `gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml --project <id> --json`: run safe live probes for a saved plan.
- `gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml --project <id> --confirm-live --json`: render, validate, preflight, and submit export.
- `gee-skill search-docs "<query>"`: search the local operator-aware docs index.
- `gee-skill plan examples/.../task.yaml`: create a cited plan, generated script, retrieval trace, and run trace.
- `gee-skill validate path/to/script.py --json`: run static and semantic validation.
- `gee-skill preflight-hk-ndvi --project <id> --year 2024 --month 1 --scope hong-kong --json`: run live data probes before export.
- `gee-skill preflight-hk-ndvi --project <id> --year 2024 --month 1 --scope hong-kong --landcover dynamic-world --json`: add Dynamic World diagnostics.
- `gee-skill preflight-hk-ndvi --project <id> --year 2024 --month 1 --scope district --district "Central and Western" --json`: run district-specific probes.
- `gee-skill smoke-test`: run offline retrieval/render/validation checks.
- `gee-skill run path/to/script.py --dry-run --json`: validate and write a dry-run trace.
- `gee-skill run path/to/script.py --project <id> --confirm-live`: execute a validated script live.
- `gee-skill monitor-exports --project <id> --json`: inspect batch task states.
- `gee-skill evaluate evals/benchmark_suite.yml`: run the offline benchmark suite.

## Documentation

- [Harness trace model](docs/harness.md)
- [Live smoke test protocol](docs/live_smoke.md)
- [How to start](docs/how_to_start.md)
- [Concepts](docs/concepts.md)
- [v0.1 Hong Kong January NDVI workflow](docs/v01_hk_january_ndvi.md)
- [v0.2 land-cover-aware NDVI workflow](docs/v02_landcover_aware_ndvi.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Error taxonomy](docs/error_taxonomy.md)
- [Extending workflows](docs/extending.md)
- [Skill guidelines applied](docs/trae_skill_guidelines.md)
- [Cross-agent review notes](docs/reviews/)

## Repository Layout

```text
SKILL.md                         Concise skill entrypoint
assets/templates/                Jinja2 Earth Engine Python workflow templates
examples/                        Task YAML examples
references/knowledge_base/       Curated docs, dataset cards, operator chains, failure cases
references/boundaries/            Curated Hong Kong district boundary GeoJSON
references/index/                Generated local retrieval index
src/geeskill/                    CLI, registry, RAG, validation, runtime, trace code
evals/                           Benchmark suite and contexts
tests/                           Offline regression tests
outputs/runs/                    Generated run traces
```
