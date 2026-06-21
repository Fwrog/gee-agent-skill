# How To Start

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts\ingest_docs.py
python -m pytest
```

For live Earth Engine access:

```powershell
python -m pip install -e ".[earthengine]"
earthengine authenticate --auth_mode=localhost
earthengine set_project $env:EE_PROJECT
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

Expected output for the connectivity check is `1`. That only proves OAuth and project initialization.

## First Offline Workflow

```powershell
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." `
  --plan `
  --json
```

This writes a plan under `outputs/runs/<run_id>/task_plan.yaml` without contacting Earth Engine.

## Review, Preflight, Run

```powershell
gee-skill review-plan outputs/runs/<run_id>/task_plan.yaml

gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --json

gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml `
  --project $env:EE_PROJECT `
  --confirm-live `
  --json
```

Do not skip preflight for live work. The command should refuse export when AOI, Sentinel-2, NDVI, Dynamic World, or class-mask gates fail.

## Credential Boundary

本仓库不提供 Google 凭据。用户需要自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

Never commit OAuth tokens, service account JSON, refresh tokens, private keys, client secrets, or local credential paths.
