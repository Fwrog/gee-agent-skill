# Workflow: Private Raster Ingestion Handoff

source_id: workflow-private-raster-ingestion-handoff
source_type: curated-workflow
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/image_upload
last_checked: 2026-07-26
risk_level: high

## Contents

1. Goal
2. Authority split
3. State machine
4. Minimum non-secret checkpoint
5. Raster-semantic contract
6. Safe staged-ingestion pattern
7. Post-upload continuation
8. Failure and retry rules
9. Location constraint boundary
10. Claim boundary
11. Official sources

## Goal

Move user-controlled GeoTIFFs into Earth Engine without making the user operate every later step and without exposing credentials, publishing restricted data, or silently creating cost-bearing resources.

The reusable pattern is:

```text
local files
  -> local audit
  -> human authority checkpoint
  -> Cloud Storage staging
  -> Earth Engine ingestion tasks
  -> asset-semantic audit
  -> workflow preflight
  -> agent-owned analysis continuation
```

The checkpoint is a boundary of authority, not a permanent handoff of technical work.

## Authority Split

| Decision or action | Default owner | Reason |
| --- | --- | --- |
| Inspect local rasters, dimensions, CRS, transform, dtype, class map, no-data, and checksums | Agent | Read-only and reproducible. |
| Select account, billing project, organization policy, storage region, retention, or lifecycle | Human | Ownership, policy, and possible cost. |
| Decide whether the data license permits cloud storage, collaboration, export, or redistribution | Human, with agent-prepared evidence | Legal/contractual authority remains human. |
| Complete interactive OAuth or approve a browser consent screen | Human | Credentials must remain private. |
| Create or change a bucket, IAM policy, public-access setting, or lifecycle rule | Human approval required | External state, cost, and access scope can change. |
| Upload local files when no safe authenticated CLI/API surface is available to the agent | Human | The local picker or credential boundary is unavailable. |
| Generate checksums, object manifest, ingestion manifest, and copyable commands | Agent | Deterministic code work. |
| Submit ingestion to an already-approved asset root with authenticated CLI/API | Agent, when explicitly authorized | Normal scoped implementation step. |
| Monitor tasks, inspect assets, and retry only missing/failed years | Agent | Read-only or bounded continuation. |
| Run semantic preflight and downstream feature/model jobs | Agent | Code and analysis work after the asset contract is satisfied. |
| Overwrite/delete an existing asset, use `--force`, publish objects, or broaden IAM | Human approval required | Destructive or access-broadening action. |

## State Machine

Use explicit states so a pause does not erase progress:

```text
LOCAL_AUDITED
  -> HUMAN_SETUP_REQUIRED
  -> OBJECTS_STAGED
  -> INGESTION_SUBMITTED
  -> ASSETS_READY
  -> PREFLIGHT_PASSED
  -> DOWNSTREAM_READY
```

- `LOCAL_AUDITED`: checksums and raster semantics are persisted.
- `HUMAN_SETUP_REQUIRED`: only authority-dependent fields are missing.
- `OBJECTS_STAGED`: expected object URIs exist or the user confirms the upload.
- `INGESTION_SUBMITTED`: task IDs are persisted; do not submit the same batch again blindly.
- `ASSETS_READY`: every expected asset exists and has passed metadata checks.
- `PREFLIGHT_PASSED`: coverage, metadata, projection, privacy, and aggregation checks pass; warnings are explicitly accepted or resolved.
- `DOWNSTREAM_READY`: feature construction or modelling may continue without another upload conversation.

If a user reports `PREFLIGHT_PASSED`, do not send them back to the upload UI unless a later audit identifies a specific missing or invalid asset.

## Minimum Non-Secret Checkpoint

Request only fields needed for the next state:

```yaml
project_id: "<cloud-project-id>"
bucket: "<bucket-name-or-null-after-ingestion>"
gcs_prefix: "<object-prefix-or-null>"
asset_root: "projects/<project-id>/assets/<folder>"
asset_pattern: "<generic-year-pattern>"
expected_years: [2019, 2020, 2021]
task_ids: ["<task-id>"]
ingestion_status: "objects_staged|submitted|assets_ready|preflight_passed"
preflight_report_path: "<local-path-or-null>"
redistribution_allowed: false
```

Do not request or persist:

- OAuth files or authorization codes;
- API keys, private keys, refresh tokens, or service-account JSON;
- credential file paths or their contents;
- personal email, phone, or unrelated account details;
- full console screenshots when structured identifiers are enough.

Project IDs, bucket names, object URIs, asset IDs, and task IDs are operational identifiers, not authentication secrets. Keep study-specific values in the private workspace and replace them with placeholders before promoting a lesson publicly.

## Raster-Semantic Contract

Audit each source before staging and each asset after ingestion:

- expected file/year inventory and SHA256;
- GeoTIFF readability, dimensions, bounds, CRS, affine transform, and native resolution;
- band count, band name, integer/float dtype, class map, and valid range;
- no-data and mask semantics;
- observation start and exclusive end time for annual products;
- native projection preservation unless a reviewed conversion is necessary;
- pyramiding policy appropriate to band semantics;
- source/version/license/provenance properties;
- expected-year coverage and access scope.

For categorical rasters:

- do not bilinearly interpolate class codes;
- use `sample` or `mode` for the ingested image pyramid as appropriate;
- construct per-class masks on the native categorical grid;
- aggregate class areas or fractions to the analysis grid;
- align derived continuous fractions to the explicit target CRS/grid.

The first successful representative year is a schema probe. Inspect it before submitting the remaining years. This catches wrong band names, default `MEAN` pyramiding, incorrect no-data, missing time metadata, and unexpected projection changes before they multiply.

## Safe Staged-Ingestion Pattern

Prefer a generated script or manifest over repeated UI entry. Keep all targets explicit and omit force/overwrite behavior.

PowerShell shape:

```powershell
$ee = ".\.venv\Scripts\earthengine.exe"
$project = "<project-id>"
$bucket = "<bucket-name>"
$assetRoot = "projects/$project/assets/<folder>"

& $ee --project $project create folder $assetRoot

& $ee --project $project upload image `
  --asset_id="$assetRoot/<asset-id>" `
  --nodata_value=<reviewed-value> `
  --pyramiding_policy=sample `
  --bands=<band-name> `
  --time_start="<year>-01-01" `
  --time_end="<next-year>-01-01" `
  --property="dataset=<dataset-version>" `
  --property="year=<year>" `
  "gs://$bucket/<prefix>/<file>.tif"
```

POSIX shell shape:

```bash
earthengine --project "$PROJECT_ID" upload image \
  --asset_id="projects/$PROJECT_ID/assets/<folder>/<asset-id>" \
  --nodata_value=<reviewed-value> \
  --pyramiding_policy=sample \
  --bands=<band-name> \
  --time_start="<year>-01-01" \
  --time_end="<next-year>-01-01" \
  --property="dataset=<dataset-version>" \
  --property="year=<year>" \
  "gs://<bucket>/<prefix>/<file>.tif"
```

The official CLI supports project-scoped commands, Cloud Storage image ingestion, task inspection, no-data, pyramiding policy, and asset properties. Do not copy placeholder values without first auditing the actual raster.

## Post-Upload Continuation

After objects are staged or tasks are submitted, the agent should:

1. Persist the object-to-asset-to-year mapping and task IDs.
2. Inspect task state with project-scoped CLI/API calls.
3. Avoid resubmitting tasks that are running or already succeeded.
4. Inspect a representative asset, then every expected asset, for the raster-semantic contract.
5. Compare the completed asset set with expected years; retry only the failed or missing subset.
6. Run the workflow preflight and save the JSON report.
7. Treat a saved passing preflight as the authoritative resume point.
8. Continue feature construction, model fitting, export planning, and trace generation within the approved project and asset scope.

The user should not need to relay the entire task-list output if the agent can query it. If the agent cannot access the project, request task IDs or the saved task/preflight report, not credentials.

## Failure And Retry Rules

- `asset exists`: inspect it; do not overwrite automatically.
- task is `RUNNING` or `READY`: monitor; do not duplicate.
- task is `FAILED`: record the exact error, correct the manifest or source, and retry that item only.
- expected asset absent and no task exists: generate a scoped submission for that item.
- categorical asset shows `MEAN`: stop downstream work and re-ingest with reviewed categorical pyramiding.
- year/time metadata mismatch: fix metadata or re-ingest before annual filtering.
- asset listing shows an odd client timestamp: inspect canonical asset metadata and task state before declaring failure; UI/CLI display artifacts are not scientific evidence.
- preflight reports a private-export warning only: retain the private boundary; a governance warning is not a data-semantic failure.

Never add `--force` as a generic recovery step. Never delete a successful asset merely to make a batch script idempotent.

## Location Constraint Boundary

Google explicitly requires the US multi-region, a US dual-region including `US-CENTRAL1`, or `US-CENTRAL1` for direct Cloud Storage reads and Cloud GeoTIFF-backed Earth Engine assets. Standard storage is required for the documented COG-backed asset path.

Do not state that this exact location rule is proven for every ordinary ingestion path merely because ingestion also stages files in Cloud Storage. Selecting a compatible US location is a conservative interoperability choice when the same bucket may support direct COG reads or COG-backed assets, but document the actual path used:

- ingested internal Earth Engine asset;
- external COG-backed asset; or
- direct `ee.Image.loadGeoTIFF`.

Bucket location is immutable at creation in ordinary use, so resolve this choice before upload. Bucket creation and retention can incur cost and remain human-authority decisions.

## Claim Boundary

Successful ingestion proves that Earth Engine accepted the files under the declared manifest. It does not prove:

- scientific validity of the source product;
- correctness of the class map;
- positional accuracy;
- license permission for redistribution;
- correctness of downstream aggregation or modelling.

Promote only this generic workflow and its official-source facts to a public skill. Keep real project IDs, bucket names, object prefixes, asset IDs, task IDs, source files, and study results private.

## Official Sources

- Earth Engine command-line tool: https://developers.google.com/earth-engine/guides/command_line
- Importing raster data: https://developers.google.com/earth-engine/guides/image_upload
- Managing assets: https://developers.google.com/earth-engine/guides/manage_assets
- Cloud GeoTIFF-backed assets: https://developers.google.com/earth-engine/Earth_Engine_asset_from_cloud_geotiff
- Cloud Storage bucket creation: https://cloud.google.com/storage/docs/creating-buckets
- Cloud Storage bucket locations: https://cloud.google.com/storage/docs/bucket-locations
