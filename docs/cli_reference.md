# CLI Reference

`gee-skill` is the primary interface for this repository. Commands return JSON with `--json` for agent orchestration.

## Inspect

```bash
gee-skill info --json
gee-skill doctor --json
gee-skill tools --json
gee-skill recipe list --json
gee-skill catalog evidence --category dataset --json
```

## Plan

```bash
gee-skill plan from-text "Compute NDVI for a supplied AOI in March 2024 and export CSV." \
  --out outputs/plans/ndvi_supplied_aoi.yaml \
  --json

gee-skill plan review outputs/plans/ndvi_supplied_aoi.yaml --json
gee-skill plan set outputs/plans/ndvi_supplied_aoi.yaml export.destination drive --json
```

## Render And Validate

```bash
gee-skill render outputs/plans/ndvi_supplied_aoi.yaml \
  --script-out outputs/scripts/ndvi_supplied_aoi.py \
  --json

gee-skill validate outputs/scripts/ndvi_supplied_aoi.py --json
```

## Preflight And Live Run

Live Earth Engine work requires a user-owned Google Cloud Project and explicit confirmation.

```bash
export EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost

gee-skill preflight outputs/plans/ndvi_supplied_aoi.yaml --project "$EE_PROJECT" --json
gee-skill run outputs/plans/ndvi_supplied_aoi.yaml --project "$EE_PROJECT" --confirm-live --json
```

If a plan still contains placeholder AOI/export context, preflight should block with `V03_CONTEXT_REVIEW_REQUIRED`.

## Exports And Trace

```bash
gee-skill exports list --project "$EE_PROJECT" --json
gee-skill exports watch --project "$EE_PROJECT" --task-id "<task-id>" --json
gee-skill trace list --json
gee-skill trace inspect <run_id> --json
```

Compatibility aliases such as `ask`, `review-plan`, `preflight-plan`, `run-plan`, and `monitor-exports` remain available for existing public examples.
