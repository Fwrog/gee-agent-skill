# General Agent-Native GEE Release Audit

Last updated: 2026-06-25

## Summary

This audit records the current evidence for presenting `gee-agent-skill` as an agent-native Google Earth Engine harness rather than a Hong Kong NDVI-only demo.

The current project identity is:

```text
CLI contract + plan schema + dataset catalog + recipe registry + RAG evidence + validation + preflight + export monitoring + traces
```

Hong Kong NDVI workflows remain golden examples and regression evidence. They should not be described as the full product boundary.

## Implemented In This Pass

- Added canonical CLI groups for `aoi`, `render`, `preflight`, `trace`, `corpus coverage`, and `eval`.
- Kept compatibility aliases for `ask`, `review-plan`, `preflight-plan`, `run-plan`, `monitor-exports`, and `evaluate`.
- Added `exports watch --task-id` filtering.
- Added agent-facing JSON envelopes for canonical validation, export, trace, corpus coverage, and eval commands.
- Added a file-backed recipe registry in `references/recipes/registry.yaml` with packaged fallback resources.
- Added `schemas/gee-plan-v0.3.schema.json` plus lightweight v0.3 plan schema checks.
- Added recipe-template entrypoints under `assets/templates/recipes/` and packaged mirrors.
- Added operator and failure catalog cards for core GEE workflow operators, exports, task monitoring, client/server pitfalls, and common preflight/export failures, with structured `catalog evidence` JSON.
- Expanded dataset catalog and knowledge base with MODIS LST, ERA5-Land Daily Aggregated, JRC Global Surface Water, and SRTM.
- Expanded the offline benchmark with non-HK planning cases for EVI, NDWI, NDBI, Landsat LST, Sentinel-1 flood mapping, Dynamic World land-cover summary, ambiguous requests, unsupported requests, RAG coverage checks, and mocked preflight blocking.
- Added first-class validation categories for `UNSAFE_GETINFO` and `PREFLIGHT_REQUIRED`.
- Added public docs for CLI reference, recipe registry, capability matrix, benchmark protocol, research positioning, paper outline, security, changelog, citation, and Hong Kong case studies.
- Updated CI to run a wheel-install smoke test after package build.

## Verification Results

Commands run from `/Users/yikai/Documents/GitHub/gee-agent-skill`:

```bash
.venv/bin/python -m pytest
PYTHONPATH=src .venv/bin/python -m geeskill.cli smoke-test --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli doctor --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli recipe list --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli catalog search "Sentinel-2 NDVI" --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli catalog evidence --category operators --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli catalog evidence --category failures --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli plan from-text "Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF." --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli eval evals/benchmark_suite.yml --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli render outputs/plans/hk_2024_16day_ndvi.yaml --script-out /tmp/hk_2024_16day_ndvi_check.py --json
PYTHONPATH=src .venv/bin/python -m geeskill.cli validate /tmp/hk_2024_16day_ndvi_check.py --json
.venv/bin/python -m build --sdist --wheel
```

Results:

- `pytest`: 117 passed.
- `smoke-test`: retrieval, render, and validation passed.
- `doctor`: local resources present; credential paths not printed.
- `eval`: benchmark suite passed with 22 cases covering retrieval, RAG coverage, EVI/NDWI/NDBI/LST/Sentinel-1/Dynamic World planning, mocked preflight blocking, and golden render/validate cases.
- `render` and `validate`: v0.3 HK 16-day NDVI script rendered and passed validation.
- `build`: source distribution and wheel built successfully.
- Wheel install smoke: `gee-skill info`, `recipe list`, `catalog evidence`, `plan from-text`, `render`, and `validate` worked from `/private/tmp` using package resources. Placeholder-context preflight correctly returned `V03_CONTEXT_REVIEW_REQUIRED`.
- Package hygiene: stale `build/`, `dist/`, and `src/gee_agent_skill.egg-info/` were deleted before the final build; the rebuilt wheel no longer includes duplicate metadata files.
- Credential scan: no project id, OAuth token pattern, private-key header, refresh-token field, client-secret field, or Earth Engine credential path was found outside ignored generated/env directories.
- `git diff --check`: passed.

## Current Capability Boundary

Implemented and tested:

- deterministic natural-language planning for several recipe families;
- editable `gee-plan/v0.3` plans;
- local dataset/operator/recipe/failure/export retrieval traces with coverage categories;
- file-backed recipe registry and documented v0.3 plan schema;
- approved template rendering for current templates, including non-golden EVI, NDWI, NDBI, Landsat LST, Sentinel-1, and Dynamic World land-cover summary examples;
- static and semantic validation;
- offline benchmark suite;
- v0.3 live preflight/run adapter for the Hong Kong 2024 16-day NDVI golden workflow;
- generic v0.3 preflight gates for NDWI, NDBI, Landsat LST, and Sentinel-1 plans that block placeholder context before export;
- export monitoring and trace inspection.

Partially implemented:

- deeper data-aware live preflight for NDWI/NDBI/LST/Sentinel-1 and zonal workflows beyond the current generic gate;
- recipe-driven templates for every planned family beyond the current render-ready subset;
- deeper promotion from markdown cards into typed executable registries beyond the current dataset catalog, recipe registry, rulesets, and `catalog evidence` inventory.

Not claimed:

- universal Earth Engine task automation;
- scientific validity of every generated output;
- live export verification for non-golden recipes;
- credential provisioning or Google Cloud setup.

## Credential Boundary

本仓库不提供 Google 凭据。用户需要自行注册 Earth Engine、配置 Google Cloud project，并在本地认证。不要提交 credentials.

Do not commit service account JSON files, OAuth tokens, refresh tokens, local credential files, private keys, client secrets, or credential paths.
