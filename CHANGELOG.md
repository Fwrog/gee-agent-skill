# Changelog

All notable changes to `gee-agent-skill` are documented here.

## Unreleased

## 0.4.3 - 2026-07-31

### Added

- Added generic HLS/MODIS NDVI `product_intercomparison` planning with explicit temporal matching, QA, target-grid, validation, and claim-boundary contracts.
- Added a seven-case unit/combination/theme quick-reference benchmark adapted from AutoGEEval++ with explicit external-score non-comparability.
- Added a 200-project direct-domain-evidence discovery queue and a separate deep-review ledger covering 21 queue records plus 3 anchors.
- Added 9 reviewed project-paper pairs, 10 accepted pattern cards, and explicit non-promotion decisions for sources that added no mainline rule.
- Added a 17-case mistake-distillation lab whose important targets must exist.
- Added a two-layer learning architecture that keeps versioned official knowledge separate from user-owned Obsidian Skills and accepts only sanitized candidate manifests through `learning contract` and the read-only `learning review-manifest` gate.

### Changed

- Refreshed official HLS, MOD13Q1, projection, and resolution sources and promoted GEE-OPs and AutoGEEval++ as bounded methodology references.
- Kept `SKILL.md` concise while adding knowledge-distillation routing and an explicit public ignorance boundary for omitted private context.
- Excluded search-lane-only false positives and added a regression gate for direct GEE domain evidence.
- Rejected zero-case benchmark runs and directed case-based KG-RAG fixtures to their dedicated evaluator.
- Documented the local-to-official promotion contract in both READMEs and kept official releases from overwriting user-owned learning state.

### Fixed

- Kept the privacy release gate operational when `git ls-files` reports a tracked path that has already been deleted from the worktree, without weakening scans of files that still exist.

## 0.4.2 - 2026-07-30

### Added

- Added a generic annual endpoint-transition recipe with fixed-grid, tile-filtering, categorical-fraction, and bounded-export safeguards.
- Added reusable private-raster ingestion guidance that resumes agent-owned validation after the minimum human authority checkpoint.

### Changed

- Compressed `SKILL.md` to the reusable execution path, safety boundaries, and on-demand references.
- Compressed the bilingual GitHub project showcase and aligned package, CLI, citation, and release metadata.
- Generalized privacy regression tests so they detect non-portable identifiers without embedding project-specific values.

### Privacy and release hygiene

- Ignore generated research outputs, local datasets, GIS rasters, private manifests, workspaces, and manuscript drafts by default.
- Keep public examples limited to reviewed regression evidence and label the annual transition recipe as render-and-validate capability rather than live scientific evidence.

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
