# CLI Reference

This reference describes the agent-facing command surface. Commands should be run from the repository root inside an activated virtual environment.

## JSON Contract

Canonical commands use a stable envelope:

```json
{"ok": true, "command": "...", "schema_version": "gee-cli/v0.3", "data": {}}
```

Failures use:

```json
{"ok": false, "error": {"code": "...", "message": "...", "hint": "..."}}
```

Compatibility commands may retain older output shapes where tests or docs rely on them.

## Local Capability Commands

```bash
gee-skill info --json
gee-skill doctor --json
gee-skill recipe list --json
gee-skill catalog search "Sentinel-2 NDVI" --json
gee-skill catalog evidence --category operator --json
gee-skill catalog evidence --category failure --json
gee-skill corpus coverage --task-type vegetation_index --metric NDVI --output CSV --json
```

These commands do not submit Earth Engine exports.

`catalog evidence` lists indexed knowledge cards by category (`dataset`, `operator`, `recipe`, `failure`, `research`, or `all`) so an agent can inspect the local knowledge base without scraping the docs tree. The older plural aliases (`datasets`, `operators`, `recipes`, `failures`) are still accepted.

## AOI Commands

```bash
gee-skill aoi resolve "Compute NDVI for Hong Kong in January 2024." --json
gee-skill aoi summarize references/boundaries/hk_18_districts.geojson --json
gee-skill aoi validate outputs/plans/hk_2024_16day_ndvi.yaml --json
```

AOI commands are offline checks. Live AOI validity and area checks belong in preflight.

## Plan, Render, Validate

```bash
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json

gee-skill plan review outputs/plans/hk_2024_16day_ndvi.yaml --json

gee-skill render outputs/plans/hk_2024_16day_ndvi.yaml \
  --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py \
  --json

gee-skill validate outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

`plan from-yaml` remains available as a compatibility render/review command.

The same v0.3 render/validate contract also covers non-golden recipes that are not live-export verified yet:

```bash
gee-skill plan from-text "Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF." \
  --out outputs/plans/ndwi_demo.yaml \
  --json

gee-skill render outputs/plans/ndwi_demo.yaml \
  --script-out outputs/scripts/ndwi_demo.py \
  --json

gee-skill validate outputs/scripts/ndwi_demo.py --json
```

For those non-golden recipes, `preflight` requires reviewed execution context. If the plan still contains placeholders such as `projects/<your-project>/assets/supplied_aoi`, it returns `V03_CONTEXT_REVIEW_REQUIRED` and does not contact export code. After replacing placeholders with real, user-owned Earth Engine assets, preflight may contact Earth Engine but still must not start an export.

## Live Boundary

Live Earth Engine checks require the user's own authenticated environment and project id.

```bash
gee-skill auth check --project "$EE_PROJECT" --json
gee-skill preflight outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --json
gee-skill run outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --confirm-live --json
```

`preflight` may contact Earth Engine but must not start an export. `run --confirm-live` may start an export.

## Export Monitoring

```bash
gee-skill exports list --project "$EE_PROJECT" --json
gee-skill exports watch --project "$EE_PROJECT" --task-id <task-id> --json
```

The legacy command remains:

```bash
gee-skill monitor-exports --project "$EE_PROJECT" --json
```

## Trace And Evaluation

```bash
gee-skill trace list --json
gee-skill trace inspect <run_id> --json
gee-skill eval evals/benchmark_suite.yml --json
```

Traces are local reproducibility artifacts under `outputs/runs/<run_id>/`. They must not contain credentials, service account JSON, OAuth tokens, refresh tokens, private keys, or credential paths.
