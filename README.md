# gee-agent-skill

`gee-agent-skill` is a Python-first, Earth-Engine-first research harness for reproducible Google Earth Engine workflows. It plans workflows from task YAML, retrieves local evidence, renders approved Jinja2 Python templates, validates scripts, writes complete run traces, and optionally runs live Earth Engine export tasks after explicit user confirmation.

It supports Sentinel-2 NDVI time series and zonal statistics, Landsat Collection 2 LST, Sentinel-1 before/after change workflows, CSV export monitoring, and evaluation-driven regression tests.

It does not provide Google credentials, replace Earth Engine account setup, prove scientific conclusions, or run live exports without explicit flags.

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
gee-skill smoke-test
python -m pytest
```

## Credentials

Live Earth Engine commands require a registered Earth Engine account, a Google Cloud Project with Earth Engine API access, and local authentication:

```bash
pip install -e ".[earthengine]"
earthengine authenticate
```

本仓库不提供 Google 凭据。用户需要自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

Never commit service account JSON, OAuth tokens, local credential files, or credential paths.

## Full Example

The full benchmark task is:

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

After local authentication, run a deliberately small export:

```bash
gee-skill live-smoke-test \
  --project your-google-cloud-project \
  --confirm-live \
  --smoke-month 1 \
  --smoke-region "Central and Western" \
  --export-folder gee_exports
```

This computes January 2024 NDVI mean for one Hong Kong district and creates a CSV export task. It records `live_run_report.json` and `export_tasks.json` when live mode starts. Without credentials or project access, it fails gracefully with `AUTH_ERROR` or `PROJECT_ERROR` guidance.

## Commands

- `gee-skill tools`: inspect installed vs exposed harness tools.
- `gee-skill search-docs "<query>"`: search the local operator-aware docs index.
- `gee-skill plan examples/.../task.yaml`: create a cited plan, generated script, retrieval trace, and run trace.
- `gee-skill validate path/to/script.py --json`: run static and semantic validation.
- `gee-skill smoke-test`: run offline retrieval/render/validation checks.
- `gee-skill run path/to/script.py --dry-run --json`: validate and write a dry-run trace.
- `gee-skill run path/to/script.py --project <id> --confirm-live`: execute a validated script live.
- `gee-skill monitor-exports --project <id> --json`: inspect batch task states.
- `gee-skill evaluate evals/benchmark_suite.yml`: run the offline benchmark suite.

## Documentation

- [Harness trace model](docs/harness.md)
- [Live smoke test protocol](docs/live_smoke.md)
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
references/index/                Generated local retrieval index
src/geeskill/                    CLI, registry, RAG, validation, runtime, trace code
evals/                           Benchmark suite and contexts
tests/                           Offline regression tests
outputs/runs/                    Generated run traces
```

