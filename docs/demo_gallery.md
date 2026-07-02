# Demo Gallery

The demos in this repository are public regression examples for the harness contract. They show how a GEE task moves from request to plan, evidence, script, validation, preflight, live export, monitoring, and trace. They are not scientific products by themselves.

Personal academic demos and unpublished research workflows are intentionally not displayed in the public gallery.

## Public Demo Matrix

| Demo | Request shape | Evidence level | What it proves | What it cannot claim |
| --- | --- | --- | --- | --- |
| v0.1 minimal NDVI | January 2024 whole-AOI NDVI CSV | Golden regression | A compact Sentinel-2 NDVI request can be planned, validated, preflighted, exported, monitored, and redacted. | Vegetation-only condition, policy-ready assessment, or independent field validation. |
| v0.2 land-cover-aware NDVI | January 2024 NDVI by Dynamic World strata | Golden regression | The harness can add land-cover interpretation masks and output caveats. | Dynamic World truth, administrative boundaries, or final class-level science. |
| v0.3 HLS/MODIS NDVI product intercomparison | 2024 HLS NDVI aggregated to MODIS grid | Full-year CSV evidence; GeoTIFF verification partially complete | The harness can support scale-aware product consistency checks, Drive handoff, metrics contracts, land-cover stratification, and publication-style figures. | In-situ ground-truth accuracy, pixel-perfect product equality, or final vegetation-health conclusions. |

## How To Run A Public Demo

Offline planning and dry-run:

```bash
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --plan --json
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
```

Land-cover-aware public demo:

```bash
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
```

Live execution stays opt-in:

```bash
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml --project "$EE_PROJECT" --json
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml --project "$EE_PROJECT" --confirm-live --json
gee-skill monitor-exports --project "$EE_PROJECT" --json
```

Product-intercomparison validation demo:

```bash
python scripts/hk_ndvi_v03_export.py --mode smoke --year 2024 \
  --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

For full-year evidence, rerun the same command with `--mode full`, then use the Google Drive connector to download the CSV exports before running the local analysis and figure scripts.

## Evidence Boundary

The demos are intentionally bounded. A completed export task proves the operational harness path, not scientific correctness. Scientific interpretation needs source validation, domain assumptions, uncertainty review, and cross-product checks such as the [remote sensing validation ladder](remote_sensing_validation.md). The v0.3 product-intercomparison demo is stronger than a toy map because it tests scale matching and cross-product consistency, but it still does not provide field truth.

## Promotion Rule

A workflow should not be called live-verified until it has:

- parser coverage for the task intent;
- a reviewed plan and recipe card;
- rendered script validation;
- live preflight evidence;
- explicit `--confirm-live` export submission;
- export task completion or documented recoverable failure;
- redacted trace artifacts with no credentials or private research content.
