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

For v0.4 product-intercomparison checks, semantic validation can include the KG-RAG-informed ruleset:

```bash
gee-skill validate outputs/scripts/hls_modis_product_intercomparison.py \
  --semantic-rules product_intercomparison \
  --json
```

## v0.4 KG-RAG

These commands are offline after indexes are built. They do not require Earth Engine credentials and do not submit live exports.

```bash
gee-skill sources discover --json
gee-skill sources validate --json

gee-skill evidence list --json
gee-skill evidence show modis_mod13q1_ndvi --json
gee-skill evidence search "MODIS NDVI scale factor" --json

gee-skill kg build --json
gee-skill kg validate --json
gee-skill kg search "HLS MODIS product intercomparison" --json
gee-skill kg neighbors validation_demo:hk_2024_hls_modis_ndvi_v03 --json
gee-skill kg path validation_demo:hk_2024_hls_modis_ndvi_v03 claim_boundary:product_intercomparison_not_ground_truth --json
gee-skill kg explain product_intercomparison --json

gee-skill retrieve hybrid "Can I directly compare 30m HLS pixels with 250m MODIS pixels?" --json
```

The hybrid retrieval payload includes BM25 text evidence, evidence cards, graph nodes, graph edges, graph paths, required rules, failure cases, claim boundaries, source-tier counts, planner hints, validator hints, and compact prompt context.

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
