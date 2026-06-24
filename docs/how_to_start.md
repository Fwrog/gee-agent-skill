# How To Start

This guide is for a first-time user who wants to install `gee-agent-skill`, run a local dry-run, and then run a live Earth Engine export after setting up Google access.

## What the project does

`gee-agent-skill` turns natural-language Earth Engine requests into reviewable plans, validated Python scripts, preflight checks, export tasks, and trace files. It is CLI-first. Browser and UI tools are optional helpers, not the default execution path.

The first safe test does not require Google credentials. Live export requires a registered Earth Engine account, a Google Cloud Project with Earth Engine API access, and local OAuth authentication.

本仓库不提供 Google 账号。需要用户自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

## Before live GEE

You need:

1. a local checkout of this repository;
2. Python 3.10 or newer;
3. an activated virtual environment created inside the repository;
4. Earth Engine API installed with `python -m pip install -e ".[earthengine]"`;
5. a Google Cloud Project id stored as `EE_PROJECT`;
6. `earthengine authenticate --auth_mode=localhost` completed locally.

Never paste credentials into chat. Never commit local credential files.

## Windows setup

Open Windows PowerShell, then run:

```powershell
cd E:\projects\gee-agent-skill

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

where python
where earthengine
python -c "import ee; print('ee import ok')"
earthengine -h
```

The first `python` and `earthengine` paths should point into `E:\projects\gee-agent-skill\.venv\Scripts\`.

## macOS setup

Open Terminal with zsh or bash, then run:

```bash
cd /Users/yikai/Documents/GitHub/gee-agent-skill
# or:
# cd ~/Documents/GitHub/gee-agent-skill

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

which python
which earthengine
python -c "import ee; print('ee import ok')"
earthengine -h
```

The paths should look like:

```text
.../gee-agent-skill/.venv/bin/python
.../gee-agent-skill/.venv/bin/earthengine
```

## Dry-run example

Dry-runs and plan/render commands do not contact Earth Engine. Start with the v0.3 editable-plan workflow:

```bash
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json

gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json

gee-skill plan review outputs/plans/hk_2024_16day_ndvi.yaml --json

gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml \
  --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py \
  --json
```

Local smoke checks are also safe without credentials:

```bash
gee-skill tools
gee-skill smoke-test --json
```

Compatibility examples for the older golden `ask` path:

```bash
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
```

The compatibility `--plan` command writes a saved plan under `outputs/runs/<run_id>/task_plan.yaml`. The v0.3 path above writes `outputs/plans/hk_2024_16day_ndvi.yaml`.

## Live preflight

Set your project id first.

Windows PowerShell:

```powershell
$env:EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
earthengine set_project $env:EE_PROJECT
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

macOS / Linux:

```bash
export EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
earthengine set_project "$EE_PROJECT"
python -c 'import os, ee; ee.Initialize(project=os.environ["EE_PROJECT"]); print(ee.Number(1).getInfo())'
```

On macOS zsh, `python -c "import ee; print('ee import ok')"` can pass before OAuth credentials exist. If initialization asks you to run `earthengine authenticate`, complete the localhost OAuth flow, set the project, and rerun the final Python check. The final check should print `1`.

Then preflight the saved v0.3 plan:

```bash
gee-skill preflight-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --json
```

A passing v0.3 preflight reports `expected_export_rows: 23` and checks January and July anchor months.

Compatibility preflight commands for `outputs/runs/<run_id>/task_plan.yaml`:

Windows PowerShell:

```powershell
gee-skill preflight-plan outputs\runs\<run_id>\task_plan.yaml `
  --project $env:EE_PROJECT `
  --json
```

macOS / Linux:

```bash
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml \
  --project "$EE_PROJECT" \
  --json
```

Preflight should run before every live export. It checks live data availability and workflow assumptions before an export task is created.

## Live export

After reviewing the plan and passing preflight, submit the export.

For the v0.3 16-day NDVI plan:

```bash
gee-skill run-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --run-id hk-2024-16day-ndvi-v03-live-export-check \
  --json
```

Monitor exports:

```bash
gee-skill monitor-exports --project "$EE_PROJECT" --json
```

PowerShell monitor command:

```powershell
gee-skill monitor-exports --project $env:EE_PROJECT --json
```

Compatibility run commands for `outputs/runs/<run_id>/task_plan.yaml`:

Windows PowerShell:

```powershell
gee-skill run-plan outputs\runs\<run_id>\task_plan.yaml `
  --project $env:EE_PROJECT `
  --confirm-live `
  --json
```

macOS / Linux:

```bash
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

## Where outputs are written

Local trace files are written under:

```text
outputs/runs/<run_id>/
```

Typical files include:

- `task_plan.yaml`
- `retrieval_trace.json`
- `generated_script.py`
- `validation_report.json`
- `dry_run_report.json`
- `preflight_report.json`
- `live_run_report.json`
- `export_tasks.json`
- `final_report.md`

The actual CSV export is created by Earth Engine as a Google Drive export task, usually in the Drive folder requested by the template or command.

## Inspect Google Drive exports

After `monitor-exports` reports a completed task:

1. open Google Drive in the same Google account used for Earth Engine authentication;
2. check the export folder, commonly `gee_exports`;
3. search Drive for the run id or CSV description shown in `export_tasks.json`;
4. if the task completed but no CSV is visible, wait a few minutes and refresh Drive;
5. if it still does not appear, inspect the task state and error message with `gee-skill monitor-exports --project "$EE_PROJECT" --json`.
