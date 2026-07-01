# Changelog

All notable changes to `gee-agent-skill` are documented here.

## Unreleased

### Release polish

- Reworked README and documentation around an agent-native GEE closed loop.
- Added documentation visuals for the closed loop, knowledge loop, and toolchain.
- Added tool permission guidance for Browser, Google Drive, Data Analytics, Computer Use, and imagegen.
- Added closed-loop knowledge promotion guidance for dataset cards, rule cards, failure cases, and workflow cards.
- Added public NDVI validation guidance using MODIS VI, Landsat, Dynamic World, ESA WorldCover, and JRC surface-water references.
- Kept public demo gallery limited to v0.1 and v0.2 golden regression examples.
- Removed private academic demo material from public docs, examples, evidence bundles, and packaged resources.

## 0.3.0-alpha - 2026-07-01

### Added

- Productization docs that frame the project as an agent-native Google Earth Engine harness.
- Canonical agent-facing CLI groups for `aoi`, `render`, `preflight`, `trace`, `corpus coverage`, and `eval`.
- `exports watch --task-id` filtering for targeted export task inspection.
- Benchmark coverage for NDWI GeoTIFF, NDBI CSV, Landsat LST, Sentinel-1 flood planning, ambiguous requests, and unsupported requests.
- File-backed recipe registry with packaged wheel fallback.
- `gee-plan/v0.3` schema file and runtime schema checks before render/run.
- Recipe-template entrypoints under `assets/templates/recipes/`.
- Operator and failure catalog cards covering core GEE operators, task monitoring, client/server pitfalls, and preflight/export failures.
- Render/validation-ready templates for Sentinel-2 index GeoTIFF, Sentinel-2 index CSV, Landsat LST CSV, Sentinel-1 change, Dynamic World summary, and export utilities.
- Generic v0.3 preflight gates for reviewed or placeholder contexts, including placeholder AOI blocking.
- Capability matrix separating supported, golden, partial, and planned workflow surfaces.
- Benchmark protocol for offline evaluation and optional live verification.
- Research positioning and paper draft notes.
- Case studies for the v0.1 and v0.2 Hong Kong NDVI public golden examples.
- Security policy with explicit credential and live-export boundaries.

### Clarified

- Public golden examples are regression evidence, not the full product boundary.
- Export submission is workflow evidence, not scientific validation.
- Dry-run and planning commands do not require credentials; live commands require user-owned Earth Engine access, local OAuth, a project id, preflight, and explicit `--confirm-live`.
- Private academic demos and unpublished workflows must stay outside the public repository.

### Verified scope

- Public release checks should include `python -m pytest`, `gee-skill smoke-test --json`, `gee-skill eval evals/benchmark_suite.yml --json`, documentation ingestion, privacy scans, and `git diff --check`.
- Live-export completion is claimed only for public golden examples documented in `docs/capability_matrix.md`.

### Limitations

- Non-golden workflows must not be described as live verified.
- The deterministic parser is not full natural-language understanding.
- Scientific interpretation requires domain review.
- Users must bring their own Earth Engine account, Google Cloud Project, OAuth authentication, quota, and export destination.
