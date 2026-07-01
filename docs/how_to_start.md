# How To Start

This guide is for a first-time user who wants to install `gee-agent-skill`, run a local dry-run, and then run a live Earth Engine export after setting up Google access.

## What The Project Does

`gee-agent-skill` turns natural-language Earth Engine requests into reviewable plans, validated Python scripts, preflight checks, export tasks, and trace files. It is CLI-first. Browser and UI tools are optional helpers, not the default execution path.

The first safe test does not require Google credentials. Live export requires a registered Earth Engine account, a Google Cloud Project with Earth Engine API access, and local OAuth authentication.

本仓库不提供 Google 账号。需要用户自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

## Mental Model

```text
request -> plan -> evidence -> render -> validate -> preflight -> export -> trace -> reusable public lesson
```

For new tasks, first decide whether the work is a public demo, a private research run, or a reusable skill improvement. Private research content should live outside this repository; generic rules, failure cases, and dataset cards can be promoted only after source verification and privacy review.

Useful orientation docs:

- [Demo Gallery](demo_gallery.md)
- [Tool Permissions](tool_permissions.md)
- [Closed Loop](closed_loop.md)
- [Remote Sensing Validation Ladder](remote_sensing_validation.md)

## Before Live GEE

You need:

1. a local checkout of this repository;
2. Python 3.10 or newer;
3. an activated virtual environment created inside the repository;
4. Earth Engine API installed with `python -m pip install -e ".[earthengine]"`;
5. a Google Cloud Project id stored as `EE_PROJECT`;
6. `earthengine authenticate --auth_mode=localhost` completed locally.

Never paste credentials into chat. Never commit local credential files.

## macOS / Linux Setup

```bash
cd /path/to/gee-agent-skill

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

which python
which earthengine
python -c "import ee; print('ee import ok')"
```

## Windows PowerShell Setup

```powershell
cd E:\projects\gee-agent-skill

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

where python
where earthengine
python -c "import ee; print('ee import ok')"
```

## Public Dry-Run Demo

Dry-runs and plan commands do not contact Earth Engine:

```bash
gee-skill tools
gee-skill smoke-test --json
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --plan --json
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
```

Land-cover-aware public demo:

```bash
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
```

## Live Preflight

Set your project id first.

macOS / Linux:

```bash
export EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
earthengine set_project "$EE_PROJECT"
python -c 'import os, ee; ee.Initialize(project=os.environ["EE_PROJECT"]); print(ee.Number(1).getInfo())'
```

Windows PowerShell:

```powershell
$env:EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
earthengine set_project $env:EE_PROJECT
python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

Then preflight the saved public task plan from `outputs/runs/<run_id>/task_plan.yaml`:

```bash
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml --project "$EE_PROJECT" --json
```

Preflight contacts Earth Engine but does not submit an export task.

## Live Export

After reviewing the plan and passing preflight, submit the export:

```bash
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json

gee-skill monitor-exports --project "$EE_PROJECT" --json
```

## Where Outputs Are Written

Local trace files are written under:

```text
outputs/runs/<run_id>/
```

Typical files include `task_plan.yaml`, `retrieval_trace.json`, `generated_script.py`, `validation_report.json`, `preflight_report.json`, `live_run_report.json`, `export_tasks.json`, `environment.json`, and `final_report.md`.

## Common Setup Problems

- If `pyproject.toml` is missing, run `cd /path/to/gee-agent-skill` first.
- If `earthengine` is not found, activate `.venv` and reinstall from the repository root.
- If `import ee` works but `ee.Initialize(...)` asks for authentication, run `earthengine authenticate --auth_mode=localhost`.
- If macOS hidden file flags break editable imports, run `chflags -R nohidden .venv` from the repository root, then reinstall.
