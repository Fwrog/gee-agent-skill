# Troubleshooting

Start by confirming that you are in the repository root and that the virtual environment is active.

## Wrong directory

You must run install commands from the repository root.

macOS / Linux:

```bash
cd /path/to/gee-agent-skill
ls pyproject.toml
```

Windows PowerShell:

```powershell
cd E:\projects\gee-agent-skill
dir pyproject.toml
```

If `pyproject.toml` is missing, you are not in the project root.

## Not a Python project

Error:

```text
ERROR: file:///Users/<name> does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
```

Cause: you ran `pip install -e ".[earthengine]"` from the wrong directory, often your home directory.

Fix:

```bash
cd /path/to/gee-agent-skill
ls pyproject.toml
python -m pip install -e ".[earthengine]"
```

## Directory path typed as a command

Error:

```text
zsh: permission denied: /path/to/gee-agent-skill
```

Cause: a directory path is not a shell command.

Fix:

```bash
cd /path/to/gee-agent-skill
```

## Command not found

Error:

```text
zsh: command not found: earthengine
```

Cause: `earthengine-api` is not installed in the active environment, or the virtual environment is not active.

macOS / Linux fix:

```bash
cd /path/to/gee-agent-skill
source .venv/bin/activate
python -m pip install -e ".[earthengine]"
which python
which earthengine
```

Windows PowerShell fix:

```powershell
cd E:\projects\gee-agent-skill
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[earthengine]"
where python
where earthengine
```

The `python` and `earthengine` paths should point into the project `.venv`.

## Editable install not visible on macOS

Error:

```text
ModuleNotFoundError: No module named 'geeskill'
```

Cause: the console script exists, but the editable install is not visible to the active Python environment. On macOS, a copied or restored `.venv` can have the `hidden` file flag on `.pth` or site-packages files, so Python does not load the editable source path.

Fix from the repository root:

```bash
source .venv/bin/activate
chflags -R nohidden .venv
python -m pip install -e ".[earthengine]"
python -c "import geeskill; print(geeskill.__file__)"
```

For one-off source-tree debugging only:

```bash
PYTHONPATH=src python -m geeskill.cli info --json
```

Do not treat `PYTHONPATH=src` as the normal user install path. The normal setup path is still an activated `.venv` plus `python -m pip install -e ".[earthengine]"` from the repository root.

## Virtual environment not activated

Symptoms:

- `gee-skill` is missing;
- `earthengine` is missing;
- `python -c "import ee"` fails;
- `where python` or `which python` points outside the project.

Activate the environment again.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

## PowerShell vs zsh environment variables

Windows PowerShell:

```powershell
$env:EE_PROJECT="your-project-id"
gee-skill auth check --project $env:EE_PROJECT --json
```

macOS / Linux:

```bash
export EE_PROJECT="your-project-id"
gee-skill auth check --project "$EE_PROJECT" --json
```

Do not use `$env:EE_PROJECT` in zsh or `export EE_PROJECT=...` as a PowerShell command.

## Earth Engine authentication failures

First verify installation:

```bash
python -c "import ee; print('ee import ok')"
earthengine -h
```

`ee import ok` only proves that the Python package is installed. It does not prove that local OAuth credentials exist.

Then authenticate and initialize with a project.

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

If the Python command prints `1`, OAuth and project initialization work. It does not prove that a dataset, AOI, reducer, or export schema is valid.

### Verified macOS OAuth flow

On macOS zsh, `import ee` can succeed before local OAuth credentials exist. In that case, live initialization fails with:

```text
EEException: Please authorize access to your Earth Engine account by running

earthengine authenticate
```

Use this sequence from the repository root:

```bash
cd /path/to/gee-agent-skill
source .venv/bin/activate

which python
which earthengine
python -c "import ee; print('ee import ok')"

earthengine authenticate --auth_mode=localhost

export EE_PROJECT="your-google-cloud-project-id"
earthengine set_project "$EE_PROJECT"

python -c 'import os, ee; print("EE_PROJECT=", os.environ["EE_PROJECT"]); ee.Initialize(project=os.environ["EE_PROJECT"]); print(ee.Number(1).getInfo())'
```

Expected successful output includes:

```text
.../gee-agent-skill/.venv/bin/python
.../gee-agent-skill/.venv/bin/earthengine
ee import ok
Successfully saved authorization token.
Successfully saved project id
EE_PROJECT= your-google-cloud-project-id
1
```

If the final command prints `1`, local OAuth credentials and the selected Google Cloud Project are ready for live Earth Engine commands.

Do not commit or share OAuth tokens, local credential files, service account JSON files, refresh tokens, or credential paths.

## Project permission failures

Typical causes:

- the Google Cloud Project id is misspelled;
- Earth Engine API is not enabled for that project;
- the authenticated Google account does not have permission to use the project;
- billing or organization policy blocks Earth Engine use.

Check the exact project id and run:

```bash
gee-skill auth check --project "$EE_PROJECT" --json
```

PowerShell:

```powershell
gee-skill auth check --project $env:EE_PROJECT --json
```

## Transient OAuth or network failures

Error category:

```text
NETWORK_ERROR
```

Typical messages include `oauth2.googleapis.com`, `/token`, `Max retries exceeded`, `SSLEOFError`, or TLS/SSL EOF text during live initialization.

Cause: Earth Engine authentication or OAuth token refresh could not reach Google's token endpoint cleanly. This is often transient and does not necessarily mean that credentials or project permissions are wrong.

Fix:

```bash
gee-skill auth check --project "$EE_PROJECT" --json
gee-skill preflight-plan outputs/plans/ndwi_supplied_aoi.yaml --project "$EE_PROJECT" --json
```

PowerShell:

```powershell
gee-skill auth check --project $env:EE_PROJECT --json
gee-skill preflight-plan outputs\plans\ndwi_supplied_aoi.yaml --project $env:EE_PROJECT --json
```

If the same network error repeats, wait briefly and confirm normal internet access before reauthenticating. Do not treat a transient token endpoint failure as proof that the plan is valid for live export.

## `Image.reduceRegions: Image has no bands`

This is usually a workflow/data issue, not a login issue.

Common causes:

- no Sentinel-2 images matched the AOI/date filters;
- cloud masking removed every usable image;
- NDVI was not added before reduction;
- a land-cover mask removed all pixels for a class;
- a date range or AOI was parsed incorrectly.

Run preflight before export:

```bash
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml \
  --project "$EE_PROJECT" \
  --json
```

Inspect `preflight_report.json` under `outputs/runs/<run_id>/`.

## Export task failed

Use:

```bash
gee-skill monitor-exports --project "$EE_PROJECT" --json
```

PowerShell:

```powershell
gee-skill monitor-exports --project $env:EE_PROJECT --json
```

Then inspect the task error message. Common fixes are lowering region size, reducing selectors, checking Drive permissions, using an allowed folder name, or fixing an empty image collection before retrying.

## Completed task but Drive CSV not found

Check:

1. the Google Drive account matches the authenticated Earth Engine account;
2. the export folder name matches the command or template;
3. Drive search includes the export description or run id;
4. enough time has passed for Drive to show the completed file;
5. `export_tasks.json` has the expected task id, description, and state.

If the task is complete but Drive still does not show the file, rerun `gee-skill monitor-exports --project "$EE_PROJECT" --json` and inspect the task metadata before starting a new export.

## Hong Kong boundary mismatch

Do not silently rely on a public administrative dataset unless its schema has been probed. The repository uses a curated Hong Kong district GeoJSON with a `District` property.

For district checks:

```bash
gee-skill preflight-hk-ndvi \
  --project "$EE_PROJECT" \
  --year 2024 \
  --month 1 \
  --scope district \
  --district "Central and Western" \
  --json
```

Inspect `sample_district_names` in `preflight_report.json` when district matching fails.
