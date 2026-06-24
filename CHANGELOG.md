# Changelog

All notable changes to `gee-agent-skill` are documented here.

## Unreleased

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

## 0.3.0

### Added

- `gee-plan/v0.3` editable plan workflow for the Hong Kong 2024 16-day NDVI CSV example.
- Plan rendering from YAML into an Earth Engine Python script.
- v0.3 preflight adapter for the Hong Kong 2024 16-day NDVI template.
- Parser and rules regression coverage for additional remote-sensing task families.
- README and release-readiness framing for the agent-native GEE harness.

### Notes

- The v0.3 live path is verified for the Hong Kong 2024 16-day NDVI CSV workflow only.
- New live task families need their own templates, validators, preflight adapters, and domain review.
