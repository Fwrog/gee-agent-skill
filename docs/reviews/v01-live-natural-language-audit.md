# v0.1 Live Natural-Language Audit

Date: 2026-06-21

Scope: audit the v0.1 natural-language path for `gee-agent-skill`:

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

## Summary

PASS. The repository now supports a deterministic `gee-skill ask` command for the v0.1 Hong Kong NDVI CSV workflow. Offline tests pass, the generated script validates, the v0.1 preflight passes against the authenticated Earth Engine project, the live export task was submitted only after preflight, and monitoring reported the v0.1 task as `COMPLETED`.

## Environment Note

The ambient PATH `gee-skill` initially used a Python environment without `earthengine-api`, which produced a graceful `AUTH_ERROR`. The verified audit commands below were rerun through the project virtual environment:

```powershell
.\.venv\Scripts\python.exe
.\.venv\Scripts\gee-skill.exe
```

Do not interpret the ambient PATH `AUTH_ERROR` as a workflow/data failure.

## Changed Areas

- Natural-language routing: `src/geeskill/ask.py`, `src/geeskill/cli.py`.
- v0.1 workflow assets: `assets/templates/hk_january_2024_ndvi_csv.py.j2`, packaged template copy, `examples/hk_2024_01_ndvi_v01/task.yaml`, packaged task/context copies.
- Live preflight: `src/geeskill/hk_ndvi_preflight.py`, `preflight-hk-ndvi --scope hong-kong`, structured empty-data failures.
- RAG trace: `references/knowledge_base/operator-chains/hk-january-ndvi-v01.md`, rebuilt `references/index/gee_docs_index.json`, export coverage counter.
- Validation/tests: v0.1 template/render/validation tests, ask routing tests, preflight mock tests, live-refusal test, trace credential scan test.
- Docs: `README.md`, `SKILL.md`, `docs/live_smoke.md`, `docs/harness.md`, `docs/error_taxonomy.md`, `docs/v01_hk_january_ndvi.md`.

## Audit Results

### Offline Tests

PASS

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Short output:

```text
42 passed in 4.21s
```

### Tool Registry

PASS

```powershell
.\.venv\Scripts\gee-skill.exe tools
```

Short output:

```text
installed/exposed tools include ask, search_docs, plan_workflow, validate_script,
preflight_hk_ndvi, run_dry, run_live, monitor_exports.
run_live and monitor_exports remain dangerous/gated.
```

### Offline Smoke

PASS

```powershell
.\.venv\Scripts\gee-skill.exe smoke-test --json
```

Short output:

```text
retrieval_results=3
validation.ok=true
semantic_rulesets=[sentinel2_ndvi_monthly_zonal, export_table_csv]
```

### Natural-Language Dry Run

PASS

```powershell
.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json --run-id audit-v01-ask-dry-run-venv
```

Short output:

```text
ok=true
mode=dry-run
intent=hk_january_2024_ndvi_csv
script=outputs\scripts\hk_2024_01_ndvi_csv.py
run_trace=outputs\runs\audit-v01-ask-dry-run-venv
validation.ok=true
contacted_earth_engine=false
```

Retrieval coverage from the live v0.1 trace:

```json
{
  "dataset_cards": 3,
  "operator_notes": 5,
  "workflow_patterns": 1,
  "known_failures": 2,
  "export_guidance": 6
}
```

### Search Docs

PASS

```powershell
.\.venv\Scripts\gee-skill.exe search-docs "Sentinel-2 NDVI reduceRegions export CSV"
```

Short output:

```text
Top hits include sentinel2 monthly NDVI operator-chain evidence and the v0.1 Hong Kong NDVI workflow pattern.
```

### Generated Script Validation

PASS

```powershell
.\.venv\Scripts\gee-skill.exe validate outputs\scripts\hk_2024_01_ndvi_csv.py --json
.\.venv\Scripts\gee-skill.exe run outputs\scripts\hk_2024_01_ndvi_csv.py --dry-run --json --run-id audit-v01-script-dry-run
```

Short output:

```text
validation.ok=true
semantic rules passed: sentinel2_ndvi_monthly_zonal, export_table_csv
dry_run=true
```

### Live Connectivity

PASS

```powershell
.\.venv\Scripts\python.exe -c "import ee; ee.Initialize(project='<verified-project>'); print(ee.Number(1).getInfo())"
```

Short output:

```text
1
```

### Live Preflight

PASS

```powershell
.\.venv\Scripts\gee-skill.exe preflight-hk-ndvi --project <verified-project> --year 2024 --month 1 --scope hong-kong --json --run-id audit-v01-preflight-hk-venv
```

Short output:

```text
ok=true
decision=allow_export
aoi_name=Hong Kong
district_feature_count=18
aoi_area_m2=2761144848.944957
image_count_before_cloud_filter=68
image_count_after_cloud_filter=49
band_names=[NDVI]
mean_ndvi_probe=0.06190635248611578
expected_export_rows=1
```

### Live Export

PASS

```powershell
.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --project <verified-project> --confirm-live --run-id hk-2024-01-ndvi-v01 --json
```

Short output:

```text
ok=true
preflight.ok=true
export_description=hk_2024_01_ndvi_v01
matching task state immediately after submission: READY
task id: HAFEQ2AE64X3GJYOJXDS3X2B
```

The live run trace contains:

```text
task.yaml
retrieval_trace.json
plan.md
generated_script.py
validation_report.json
dry_run_report.json
preflight_report.json
live_run_report.json
export_tasks.json
environment.json
final_report.md
```

### Export Monitoring

PASS

```powershell
.\.venv\Scripts\gee-skill.exe monitor-exports --project <verified-project> --json --timeout 300 --poll-seconds 20 --run-id audit-v01-monitor-exports-final
```

Short output:

```text
hk_2024_01_ndvi_v01 state=COMPLETED
error_message=null
```

The previous failed task remains visible as historical evidence only:

```text
hk_2024_01_ndvi_smoke state=FAILED error="Image.reduceRegions: Image has no bands."
```

The v0.1 path did not repeat that failure.

### Packaging

PASS

```powershell
.\.venv\Scripts\python.exe -m build --sdist --wheel
```

Short output:

```text
Successfully built gee_agent_skill-0.2.0.tar.gz and gee_agent_skill-0.2.0-py3-none-any.whl
```

Wheel resource checks:

```text
geeskill/resources/templates/hk_january_2024_ndvi_csv.py.j2 included
geeskill/resources/tasks/hk_2024_01_ndvi_v01.yaml included
geeskill/resources/contexts/hk_2024_01_ndvi_v01.json included
geeskill/resources/index/gee_docs_index.json included
geeskill/resources/boundaries/hk_18_districts.geojson included
```

Installed-wheel smoke test outside the repo:

```powershell
<temp-venv>\Scripts\gee-skill.exe ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
```

Short output:

```text
ok=true
package templates/index/boundary resources resolved from site-packages
validation.ok=true
```

### Credential Safety

PASS

Text-file scan excluded `.git`, `.venv`, `build`, `dist`, `outputs`, egg-info, and cache directories.

Short output:

```text
No private keys, API keys, OAuth refresh tokens, service account JSON, client secrets, or committed project ID were found.
Remaining matches are scanner/test/policy strings in validation tests and review notes.
```

README still states that users must authenticate locally and that credentials are not provided or committed.

## Remaining Limitations

- Google Drive was not opened directly from this audit; Earth Engine task monitoring reported `COMPLETED`, but the CSV file was not visually inspected in Drive.
- v0.1 supports only the whole-Hong-Kong January 2024 NDVI CSV workflow. Full 2024 district-level monthly NDVI remains v0.2.
- The ambient PATH Python may not be the project venv. Use `.\.venv\Scripts\Activate.ps1` or explicit `.\.venv\Scripts\gee-skill.exe` for live work.

## User Commands

```powershell
$env:EE_PROJECT="your-google-cloud-project-id"

.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --dry-run `
  --json

.\.venv\Scripts\gee-skill.exe preflight-hk-ndvi `
  --project $env:EE_PROJECT `
  --year 2024 `
  --month 1 `
  --scope hong-kong `
  --json

.\.venv\Scripts\gee-skill.exe ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." `
  --project $env:EE_PROJECT `
  --confirm-live `
  --run-id hk-2024-01-ndvi-v01 `
  --json

.\.venv\Scripts\gee-skill.exe monitor-exports `
  --project $env:EE_PROJECT `
  --json
```
