# v0.2 Land-Cover-Aware Release Audit

Date: 2026-06-21

Project id is intentionally redacted as `<verified-project>`. No credentials, OAuth tokens, service account JSON, refresh tokens, private keys, or local credential paths are recorded here.

## Summary

PASS. v0.2 adds a plan-first, reviewable, land-cover-aware Earth Engine workflow while preserving v0.1 behavior. The repository now supports deterministic natural-language planning for:

```text
Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.
```

The v0.2 live preflight passed and a live export task was created. The task was monitored to `COMPLETED`.

## Implemented Features

- Canonical task plan object and saved `task_plan.yaml`.
- `gee-skill ask --plan`, `review-plan`, `preflight-plan`, and `run-plan --confirm-live`.
- Dynamic World land-cover-aware preflight with `landcover_diagnostics.json`.
- v0.2 Jinja2 template for whole-Hong-Kong January 2024 NDVI by land-cover class.
- Semantic validation rules for Dynamic World land-cover-aware NDVI.
- Wider GEE knowledge base: client/server, scale/CRS, reducers, joins, exports/tasks, quotas/debugging, workflow patterns, dataset cards, and failure cases.
- v0.2 tests and benchmark case.
- GitHub project files and updated README/SKILL/docs.

## Offline Commands

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Result: `54 passed in 6.05s`.

```powershell
.\.venv\Scripts\gee-skill.exe smoke-test --json
```

Result: validation passed for the smoke-rendered `hk_district_monthly_ndvi.py`.

```powershell
.\.venv\Scripts\gee-skill.exe search-docs "Sentinel-2 NDVI reduceRegions export CSV" --json
```

Result: returned workflow/operator evidence, including `workflows/landcover-aware-ndvi.md` and `operator-chains/sentinel2-ndvi-monthly-zonal.md`.

```powershell
.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json --run-id release-v02-plan-check-relpath
```

Result: wrote `outputs/runs/release-v02-plan-check-relpath/task_plan.yaml` with selected datasets `COPERNICUS/S2_SR_HARMONIZED` and `GOOGLE/DYNAMICWORLD/V1`.

```powershell
.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json --run-id release-v02-dry-run-check
```

Result: rendered `outputs/scripts/hk_2024_01_ndvi_by_landcover_csv.py`; validation passed with semantic rules `sentinel2_ndvi_monthly_zonal`, `export_table_csv`, and `dynamic_world_landcover_ndvi`.

```powershell
.\.venv\Scripts\gee-skill.exe evaluate evals\benchmark_suite.yml
```

Result: benchmark suite `gee_harness_benchmark_v0.2` passed.

## Packaging

```powershell
.\.venv\Scripts\python.exe -m build --sdist --wheel
```

Result: built `gee_agent_skill-0.2.0.tar.gz` and `gee_agent_skill-0.2.0-py3-none-any.whl`.

Wheel contents included packaged resources:

- `geeskill/resources/templates/hk_january_2024_ndvi_by_landcover_csv.py.j2`
- `geeskill/resources/contexts/hk_2024_01_ndvi_landcover_v02.json`
- `geeskill/resources/tasks/hk_2024_01_ndvi_landcover_v02.yaml`
- `geeskill/resources/index/gee_docs_index.json`
- `geeskill/resources/boundaries/hk_18_districts.geojson`

Installed the wheel in `tmp/wheel-v02-check` and ran the v0.2 dry-run command successfully.

## Credential Safety

Credential scan excluded `.git`, `.venv`, `tmp`, `build`, `dist`, `outputs`, `.pytest_cache`, and `__pycache__`.

Matches were limited to `.gitignore` safeguards, validation/test regexes, and the prior audit document's scan commands. No committed source file contains actual private keys, tokens, service account JSON, refresh tokens, client secrets, or hard-coded Google Cloud project IDs.

README contains the required credential warning:

```text
本仓库不提供 Google 凭据。用户需要自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.
```

## Live Preflight

```powershell
.\.venv\Scripts\gee-skill.exe preflight-hk-ndvi --project <verified-project> --year 2024 --month 1 --scope hong-kong --landcover dynamic-world --json --run-id release-v02-live-preflight
```

Result: PASS.

Key values:

- Sentinel-2 image count before cloud filtering: `68`
- Sentinel-2 image count after cloud filtering: `49`
- NDVI bands: `["NDVI"]`
- Dynamic World image count: `35`
- Dynamic World bands: `water`, `trees`, `grass`, `flooded_vegetation`, `crops`, `shrub_and_scrub`, `built`, `bare`, `snow_and_ice`, `label`
- Water fraction: `0.6067`
- Built fraction: `0.0828`
- Vegetation fraction: `0.2551`
- All-surface NDVI probe: `0.0619`
- Non-water NDVI probe: `0.6148`
- Vegetation NDVI probe: `0.7557`

Interpretation: the low all-surface NDVI is consistent with mixed surfaces and high water fraction; it should not be treated as vegetation-only NDVI.

## Plan Preflight

```powershell
.\.venv\Scripts\gee-skill.exe preflight-plan outputs\runs\release-v02-plan-check-relpath\task_plan.yaml --project <verified-project> --json --run-id release-v02-preflight-plan
```

Result: PASS. The trace includes `preflight_report.json` and `landcover_diagnostics.json`.

## Live Export

```powershell
.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --project <verified-project> --confirm-live --run-id hk-2024-01-ndvi-landcover-v02 --json
```

Result: PASS. Export description `hk_2024_01_ndvi_landcover_v02`; matching Earth Engine task initially reached `RUNNING`, with no immediate `FAILED` state.

```powershell
.\.venv\Scripts\gee-skill.exe monitor-exports --project <verified-project> --json --run-id release-v02-monitor
```

Result: current v0.2 task `hk_2024_01_ndvi_landcover_v02` reached `COMPLETED`. Prior v0.1 task `hk_2024_01_ndvi_v01` remained `COMPLETED`.

## Remaining Limitations

- `run-plan --confirm-live` is implemented and covered by mocked refusal tests, but the live export in this audit used `ask --confirm-live` to avoid submitting duplicate tasks after `preflight-plan` passed.
- Dynamic World class thresholds are configurable in the plan context but remain a research choice; scientific interpretation still requires domain review.
