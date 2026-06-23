# Release Readiness

Last updated: 2026-06-23

This document records the current evidence for making `gee-agent-skill` a publishable, agent-native Google Earth Engine CLI harness rather than only a Hong Kong NDVI demo.

## Current Position

The repository is ready for local review as a v0.3 general harness candidate:

- product identity is CLI-first, plan-first, source-grounded, and traceable;
- v0.1 and v0.2 Hong Kong workflows remain golden regression examples;
- v0.3 adds the Hong Kong 2024 16-day NDVI CSV example;
- the knowledge base is file-backed Markdown/YAML plus generated JSON indexes;
- live Earth Engine execution remains gated by `--project` and `--confirm-live`;
- v0.3 live export now has a template-specific plan adapter for the Hong Kong 2024 16-day NDVI CSV workflow;
- beginner setup docs distinguish Windows PowerShell and macOS/Linux shells.

It is not yet a universal GEE automation claim. New task families still need recipe-specific templates, live preflight coverage, and domain review.

## Homepage And Visual Assets

Project-bound imagegen assets:

- `assets/images/gee-agent-social-preview-dark.png`: selected dark GitHub homepage/social-preview image. This is the current README lead image.
- `assets/images/gee-agent-social-preview.png`: GitHub homepage/social-preview style image generated with built-in imagegen. It has no text, logos, credentials, or scientific claims.
- `assets/images/gee-agent-harness-hero.png`: agent harness workflow visual for the README.
- `assets/images/hk-2024-16day-ndvi-workflow.png`: Hong Kong 2024 16-day NDVI workflow visual.

Generation prompt used for the social-preview variants:

```text
Create a polished raster hero visual showing an agent-native geospatial workflow for satellite remote sensing: satellite imagery tiles over Hong Kong coastline, a subtle command-line interface panel, plan-review checkpoints, export trace lines, and NDVI green vegetation signal overlays. No readable text, no logos, no brand names.
```

These images support project communication only. They are not scientific evidence and should not be used to validate geospatial results.

## Tool Boundaries

The goal explicitly allows Browser, Computer Use, and imagegen, but the project should keep execution authority in the CLI and Earth Engine Python API.

- Browser: use for official docs inspection, local previews, GitHub README visual QA, or rendered documentation checks.
- Computer Use: use only when no CLI, API, browser plugin, or repo-native path can complete a local Mac UI task.
- Image generation: use for README/homepage visuals or explanatory raster assets; save project-bound outputs under `assets/images/`.
- Live export: never submit through browser or UI automation when a CLI/API path exists.

Risky UI actions still require action-time confirmation under the Browser/Computer Use policies.

## Agent CLI Contract

Agent-facing commands should return deterministic JSON envelopes:

```json
{ "ok": true, "data": {} }
```

or:

```json
{ "ok": false, "error": { "code": "...", "message": "...", "hint": "..." } }
```

Current v0.3 surfaces:

```bash
gee-skill info --json
gee-skill doctor --json
gee-skill catalog search "Sentinel-2 NDVI" --json
gee-skill catalog show COPERNICUS/S2_SR_HARMONIZED --json
gee-skill catalog recommend --task-type vegetation_index --metric NDVI --json
gee-skill recipe list --json
gee-skill recipe show vegetation-index-ndvi --json
gee-skill rules list --json
gee-skill rules show export_table_csv --json
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

Compatibility commands for v0.1/v0.2 remain part of the golden path:

```bash
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
```

## Hong Kong 2024 16-Day NDVI Example

The v0.3 example is:

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

Required evidence:

- parser recognizes Hong Kong, NDVI, 2024, 16-day cadence, and CSV output;
- plan uses `schema_version: gee-plan/v0.3`;
- execution template is `hk_2024_16day_ndvi_csv`;
- context sets `date_start: 2024-01-01`, `date_end: 2025-01-01`, and `temporal_cadence_days: 16`;
- rendered script validates with static and semantic checks;
- live export remains opt-in and runs only after v0.3 preflight passes.

Offline reproduction:

```bash
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

Live v0.3 verification evidence:

- `preflight-plan outputs/plans/hk_2024_16day_ndvi.yaml --project <project-id> --json`: passed.
- Anchor months checked: January and July 2024.
- Expected export rows: 23.
- `run-plan outputs/plans/hk_2024_16day_ndvi.yaml --project <project-id> --confirm-live --run-id hk-2024-16day-ndvi-v03-live-export-check --json`: submitted one export.
- Export description: `hk_2024_16day_ndvi`.
- Drive folder: `gee_exports`.
- File prefix: `hk_2024_16day_ndvi`.
- Task id observed through `monitor-exports`: `6VQOYD567CL4HVSEON6GOMMC`.
- Task state immediately after submission: `READY`, then `RUNNING`.

CSV sanity check from the first exported file:

```text
rows: 23
date coverage: 2024-01-01 to 2025-01-01
mean_ndvi range: -0.066 to 0.358
mean of period means: 0.109
minimum image_count_after_cloud_filter: 2
low-image-count periods: 5, 8
null mean_ndvi rows: 0
```

Interpretation boundary: the v0.3 output is an all-surface whole-AOI engineering demo, not a vegetation-only scientific result. Low or negative period means are plausible because the Hong Kong administrative geometry includes water and dense built-up surfaces, and some periods have few images after cloud filtering.

See [v0.3 Hong Kong 2024 16-day NDVI workflow](v03_hk_2024_16day_ndvi.md).

## Distilled Knowledge Database

The database remains source-controlled and auditable:

- dataset cards under `references/knowledge_base/datasets/`;
- operator cards under `references/knowledge_base/operators/`;
- recipe cards under `references/knowledge_base/recipes/`;
- failure cards under `references/knowledge_base/failure-cases/`;
- ruleset cards under `references/knowledge_base/rules/`;
- corpus policy, discovery inventories, and pattern notes under `references/knowledge_base/corpus/`;
- generated indexes under `references/index/` and `src/geeskill/resources/index/`.

Corpus expansion policy:

- official Earth Engine docs remain canonical for API behavior;
- `giswqs`/OpenGeo and `gee-community` are priority community review lanes;
- paper-linked repositories from TGRS, ISPRS, JAG, RSE, and similar venues are high-value but default to `metadata_only_until_license_review`;
- no third-party code is copied into this repository by default;
- only operator patterns, validation implications, failure modes, and natural-language task prompts are promoted.

## GitHub Publish Hygiene

Repository-local ignore rules are configured for publish-time cleanup:

- Python environments and caches: `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.ipynb_checkpoints/`;
- build and package artifacts: `build/`, `dist/`, `*.egg-info/`, wheels, and source archives;
- generated local outputs: `outputs/`, `tmp/`, `preview/`, `site/`, and logs;
- internal agent scratch and historical review notes: `docs/agent_reviews/` and `docs/reviews/`;
- local editor and OS metadata: `.DS_Store`, `.vscode/`, `.idea/`;
- credentials and secrets: `.env`, Earth Engine credentials, Google application-default credentials, OAuth/client-secret/token JSON, private keys, PEM, and P12 files.

Source-controlled JSON/YAML cards under `references/`, `evals/`, and `src/geeskill/resources/` remain intentionally tracked; ignore rules avoid broad `*.json` or `*.yaml` patterns.

Pre-release cleanup keeps the reader-facing documentation tree focused:

- historical internal review notes under `docs/agent_reviews/` and `docs/reviews/` were removed from the publishable docs tree;
- current release evidence lives in this file, `README.md`, `SKILL.md`, and `references/knowledge_base/**`;
- local `.DS_Store`, cache, build, package, and generated output artifacts are ignored and should not be committed.

## Validation Gate

Run before claiming a publishable v0.3 state:

```bash
python -m pytest
gee-skill smoke-test --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json
gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --dry-run --json
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
python -m build --sdist --wheel
```

Recent local evidence:

- `python -m pytest -q`: passed.
- `gee-skill smoke-test --json`: passed.
- v0.2 plan and dry-run commands: passed.
- v0.3 parser/rules regressions cover NDWI GeoTIFF, NDBI CSV, Landsat LST CSV, Sentinel-1 before/after flood GeoTIFF, ambiguous flood windows, and unsupported-task recovery with closest recipes.
- v0.3 live adapter tests cover review, preflight, retryable network preflight failure, preflight-blocked no-export behavior, and single-execute success behavior.
- `python -m build --sdist --wheel`: passed after allowing isolated build dependency download.
- `git diff --check`: passed.

Browser visual QA evidence:

- Rendered `README.md` to a local GFM-like HTML preview and inspected it with the in-app Browser.
- Confirmed the README has one H1, the dark social-preview lead image loads, and all README images resolve.
- Confirmed the table of contents includes Quick Start, Configuration checklist, Installation, Earth Engine authentication, v0.1/v0.2 examples, plan-first workflow, Common mistakes, references, and security.
- Confirmed the Configuration checklist renders the repository-root check, directory-path warning, `.venv` activation checks, `which/where earthengine`, PowerShell `$env:EE_PROJECT`, macOS/Linux `export EE_PROJECT`, and live `--confirm-live` boundary.
- Confirmed the 2024 Hong Kong 16-day NDVI commands render in the plan-first section.
- Rendered `docs/release_readiness.md` and confirmed it includes the homepage asset inventory, Browser/Computer Use boundaries, v0.3 CLI contract, 16-day example, validation gate, and remaining limitations.

## Remaining Limitations

- Windows PowerShell commands are documented against the known workflow, but this Mac run did not execute them on a Windows host.
- v0.3 live export has been verified for the Hong Kong 2024 16-day NDVI template only. New v0.3 templates need their own preflight adapter before live export is allowed.
- Live use still requires a user-controlled Google account, Earth Engine access, project id, local OAuth, preflight, and `--confirm-live`.
- The current v0.3 CSV is all-surface and whole-AOI; more refined demos should add land/water masks, district outputs, land-cover strata, and chart-ready QA.
- Paper-linked repository sampling is now policy-backed, but the next deep audit should add actual DOI-linked candidates and local read-only pattern counts.
- Browser visual QA of a rendered GitHub README is useful before publishing, but not required for CLI correctness.
