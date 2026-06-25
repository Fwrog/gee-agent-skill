# Changelog

All notable changes to `gee-agent-skill` are documented here.

## Unreleased

### Release polish

- Added capability matrix columns that separate implemented, plan-only, render/validate, mocked preflight, live preflight, submitted export, completed export, and planned status.
- Added sanitized golden evidence bundles for the v0.1 and v0.2 Hong Kong NDVI workflows.
- Added a Codex transcript showing the agent-native review-before-run workflow.
- Added v0.3.0-alpha release notes and overclaim-audit documentation.
- Clarified that single-category `catalog evidence --category dataset|operator|recipe|failure` is the preferred public command form; plural aliases remain accepted.

## 0.3.0-alpha - 2026-06-25

### Added

- Productization docs that frame the project as an agent-native Google Earth Engine harness.
- Canonical agent-facing CLI groups for `aoi`, `render`, `preflight`, `trace`, `corpus coverage`, and `eval`.
- `exports watch --task-id` filtering for targeted export task inspection.
- Benchmark coverage for NDWI GeoTIFF, NDBI CSV, Landsat LST, Sentinel-1 flood planning, ambiguous requests, and unsupported requests.
- File-backed recipe registry with packaged wheel fallback.
- `gee-plan/v0.3` schema file and runtime schema checks before render/run.
- Recipe-template entrypoints under `assets/templates/recipes/`.
- Operator and failure catalog cards covering core GEE operators, task monitoring, client/server pitfalls, and preflight/export failures.
- Render/validation-ready non-golden templates for Sentinel-2 index GeoTIFF, Sentinel-2 index CSV, and Landsat LST CSV.
- Generic v0.3 preflight gates for non-golden NDWI, NDBI, Landsat LST, and Sentinel-1 plans, including placeholder AOI blocking.
- Sentinel-1 GeoTIFF template export format validation.
- Dataset catalog and knowledge-base cards for MODIS MOD11A2 LST, ERA5-Land Daily Aggregated, JRC Global Surface Water, and SRTM.
- Capability matrix separating supported, golden, partial, and planned workflow surfaces.
- Benchmark protocol for offline evaluation and optional live verification.
- Research positioning and paper draft notes.
- Case studies for the v0.1 and v0.2 Hong Kong NDVI golden examples.
- Security policy with explicit credential and live-export boundaries.
- Citation metadata for the repository.

### Clarified

- Hong Kong NDVI workflows are golden examples and regression evidence, not the full product boundary.
- Export submission is workflow evidence, not scientific validation.
- Dry-run and planning commands do not require credentials; live commands require user-owned Earth Engine access, local OAuth, a project id, preflight, and explicit `--confirm-live`.

### Verified scope

- `python -m pytest`: 117 passed in the current release-prep context.
- `gee-skill eval evals/benchmark_suite.yml --json`: 22/22 cases passed in the current release-prep context.
- Smoke-test, v0.2 plan/dry-run, v0.3 HK 16-day NDVI plan/render/validate, EVI plan/render/validate, NDWI plan/render/validate, build, wheel smoke, credential scan, and `git diff --check` passed in the current release-prep context.
- Live-export completion is claimed only for golden examples documented in `docs/capability_matrix.md`.

### Limitations

- Non-golden workflows must not be described as live verified.
- The deterministic parser is not full natural-language understanding.
- Scientific interpretation requires domain review.
- Users must bring their own Earth Engine account, Google Cloud Project, OAuth authentication, quota, and export destination.

## 0.3.0 development baseline

### Added

- `gee-plan/v0.3` editable plan workflow for the Hong Kong 2024 16-day NDVI CSV example.
- Plan rendering from YAML into an Earth Engine Python script.
- v0.3 preflight adapter for the Hong Kong 2024 16-day NDVI template.
- Parser and rules regression coverage for additional remote-sensing task families.
- README and release-readiness framing for the agent-native GEE harness.

### Notes

- The v0.3 live path is verified for the Hong Kong 2024 16-day NDVI CSV workflow only.
- New live task families need their own templates, validators, preflight adapters, and domain review.
