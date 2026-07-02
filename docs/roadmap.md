# Roadmap And TODO

This roadmap keeps the public project honest: finished evidence, pending live checks, and future ideas are separated. Items are written as public, reusable work. Private research tasks and unpublished results do not belong here. For the compact root-level task entry point, see [../TODO.md](../TODO.md).

## 🧭 Status At A Glance

| Track | Status | Next decision |
| --- | --- | --- |
| Core harness | ✅ Stable public baseline | Keep CLI/API changes backward-compatible. |
| Public demos v0.1/v0.2 | ✅ Golden | Preserve as regression examples. |
| Public validation v0.3 | ✅ Golden | Preserve as portfolio-grade product-intercomparison evidence. |
| Skill generation v0.4 | 🚧 Planned | Generalize product-intercomparison workflows. |
| Knowledge loop | 🚧 Active | Promote only generic, source-backed, privacy-reviewed lessons. |
| Packaging and contributor UX | 🚧 Active | Turn TODOs into small, labeled GitHub issues. |

## ✅ Done

- Closed-loop harness: request -> plan -> evidence -> render -> validate -> preflight -> export -> trace.
- Public v0.1 and v0.2 Hong Kong NDVI golden regression examples.
- Generic knowledge loop for promoting only source-backed, privacy-reviewed lessons.
- v0.3 canonical HLS/MODIS NDVI product-intercomparison implementation.
- Tests for v0.3 schema, export naming, scale-aware aggregation contract, and metrics hard-fail checks.
- v0.3 full-year CSV Drive readback, annual raster/tile Drive readback, local raster QA, figures, report, and `golden_ready` readiness audit.

## 🎯 Now

These are the current near-term tasks. They should be suitable for a GitHub project board column named `Now`.

### 🧪 v0.3 Live Evidence

Last checked: 2026-07-02 05:27 HKT. The full-year v0.3 HLS/MODIS product-intercomparison loop is `Golden`: all Earth Engine tasks reached terminal state, completed CSV exports were read back from Google Drive, full-region HLS 30 m and MODIS 250 m GeoTIFFs were read back, deterministic 2x2 tiled fallbacks completed for HLS aggregated 250 m, difference, and valid-count rasters, local raster QA passed, and `scripts/hk_ndvi_v03_readiness_audit.py` returned `golden_ready`. Full-region raster replacement failures remain documented as reusable GEE engineering lessons, not open blockers. The latest task-state evidence is in `outputs/hk_ndvi_product_validation_v03/task_status_latest.json`.

- [x] Submit nine smoke export tasks to Earth Engine for `GEE_SKILL_V03_HK_NDVI_VALIDATION`.
- [x] Use the Google Drive connector to confirm the export folder exists.
- [x] Read back the completed pixel-sample CSV from Drive.
- [x] Download the pixel-sample CSV to `outputs/hk_ndvi_product_validation_v03/raw_drive/`.
- [x] Run `scripts/hk_ndvi_v03_analyze_drive_exports.py --allow-partial` on Drive-downloaded samples.
- [x] Run `scripts/hk_ndvi_v03_make_figures.py` on partial analysis outputs.
- [x] Update `outputs/hk_ndvi_product_validation_v03/VALIDATION_REPORT.md` with smoke evidence, then full-year CSV metrics and evidence boundaries.
- [x] Submit the full-year 2024 export set to Earth Engine.
- [x] Read back `window_metrics`, `pixel_samples`, `landcover_metrics`, and `regional_timeseries` CSV exports from Drive.
- [x] Rerun analysis without `--allow-partial` after all required CSVs are available.
- [x] Add time-series, scatter/hexbin, spatial sample, land-cover metric, and valid-fraction figures.
- [x] Update `outputs/hk_ndvi_product_validation_v03/VALIDATION_REPORT.md` with full-year CSV metrics and evidence boundaries.
- [x] Record and fix the product-grid clip transform failure observed in the original MODIS annual and difference GeoTIFF exports.
- [x] Read back completed full-year `hls30` and replacement `modis250` annual GeoTIFFs from Drive.
- [x] Download completed GeoTIFFs to ignored `raw_drive/geotiff/` and run lightweight NDVI sanity QA.
- [x] Add `scripts/hk_ndvi_v03_monitor_tasks.py` and `task_status_latest.json` for durable task-state evidence.
- [x] Submit low-memory replacement GeoTIFF tasks for failed `hls_agg250`, `diff`, and `valid_count` annual rasters.
- [x] Add `scripts/hk_ndvi_v03_readiness_audit.py` to block Golden promotion until task completion, Drive readback, local GeoTIFF QA, figures, and claim-boundary checks all pass.
- [x] Add optional `--tile-grid ROWSxCOLS` fallback for annual GeoTIFF image exports if the full-region replacement tasks fail.
- [x] Submit 2x2 tiled fallback tasks for `hls_agg250` after the projected low-memory full-region replacement failed with out-of-memory.
- [x] Submit 2x2 tiled fallback tasks for `valid_count` after the low-memory full-region replacement failed with out-of-memory.
- [x] Submit 2x2 tiled fallback tasks for `diff` after the projected low-memory full-region replacement failed with out-of-memory.
- [x] Monitor replacement annual GeoTIFF export tasks until terminal state: tiled `hls_agg250`, tiled `diff`, and tiled `valid_count`.
- [x] Read back remaining annual GeoTIFF outputs from Drive using task id/created-time evidence to distinguish replacement files from older same-prefix attempts.
- [x] Promote v0.3 to `Golden` after GeoTIFF verification, Drive readback, analysis, report QA, and readiness audit passed.

#### Current Full-Year CSV Metrics

These numbers come from Drive-read full-year CSV exports. They are product-intercomparison evidence, not in-situ ground-truth validation. The demo is now `Golden` because the CSV evidence, raster/tile Drive readback, local QA, figures, report, and readiness audit are complete.

| Metric | Value |
| --- | ---: |
| Matched samples | 5,575 |
| Mean HLS aggregated NDVI | 0.662 |
| Mean MODIS NDVI | 0.687 |
| Bias, HLS - MODIS | -0.025 |
| MAE | 0.073 |
| RMSE | 0.111 |
| Pearson r | 0.870 |
| Spearman rho | 0.859 |

### 🧹 Release Hygiene

- [x] Confirm README, README.zh-CN, capability matrix, validation docs, and output report all use the same v0.3 status label.
- [ ] Run release checks: `python -m pytest -q`, `gee-skill smoke-test --json`, `gee-skill eval evals/benchmark_suite.yml --json`, and `git diff --check`.
- [ ] Run privacy scan over public docs, examples, references, scripts, tests, and committed outputs.
- [ ] Ensure raw Drive exports and intermediate analysis files remain ignored.
- [ ] Open or draft small issues for unfinished v0.4 items instead of burying them in prose.

## 🔜 Next

These tasks are good candidates for a project board column named `Next`: scoped, public, and useful, but not required for the completed v0.3 evidence package.

### 🚧 v0.4 Skill Generation Gap

- [ ] Add a generic `product_intercomparison` task type to the plan schema.
- [ ] Add an HLS/MODIS NDVI product-intercomparison recipe card after the canonical v0.3 script has live evidence.
- [ ] Teach the planner to generate scale-aware comparison plans with temporal windows and grid matching.
- [ ] Add semantic validators for MODIS scale factor, HLS `Fmask`, MODIS `SummaryQA`/`DetailedQA`, and `reduceResolution` before coarse-grid comparison.
- [ ] Add an automated comparator that checks skill-generated workflows against canonical v0.3 expectations.
- [ ] Add optional VIIRS VNP13A1 secondary comparison once the primary MODIS path is stable.

### 📚 Knowledge Base TODO

- [x] Add a failure case for "direct fine/coarse pixel comparison" with recovery guidance.
- [x] Add live failure guidance for `reduceResolution` without default projection and product-grid boundary transform failures.
- [x] Add a rule card requiring explicit product scale factors for official vegetation-index products.
- [x] Add a rule card requiring a claim boundary for every validation report.
- [ ] Refresh official dataset cards on a scheduled cadence and record `last_checked`.

### 🧰 Project Polish

- [ ] Add a short release checklist for moving a demo from implementation-ready to golden.
- [ ] Add compact screenshots or figures to README only after metrics are connector-read and reproducible.
- [ ] Keep `outputs/` ignored except for intentionally small status artifacts.
- [ ] Continue using Browser for official docs verification, Drive for export handoff, Data Analytics for chart/report QA, and Computer Use only as a GUI fallback.

## 🌱 Later

These tasks are valuable, but they should stay behind the current validation and v0.4 generalization work.

- [ ] Add a small gallery page for validation patterns: index validation, product intercomparison, land-cover stratification, and export-readback QA.
- [ ] Add a machine-readable demo registry so README tables, capability matrix, and validation docs can be generated from one source.
- [ ] Add benchmark fixtures for failed live-export patterns using mocked task states and expected recovery guidance.
- [ ] Add optional dashboard/report rendering for validation outputs after the CSV and figure contracts stabilize.
- [ ] Add scheduled documentation refresh reminders for high-drift Earth Engine dataset pages.

## 🧩 Suggested Issue Backlog

Use these as ready-to-open GitHub issues. Keep each issue small enough to review in one PR.

| Title | Labels | Acceptance check |
| --- | --- | --- |
| Add product-intercomparison task type | `enhancement`, `schema`, `v0.4` | Parser/schema accepts the generic task without changing existing demos. |
| Add MODIS vegetation-index scale-factor validator | `validator`, `remote-sensing`, `good first issue` | Validation fails or warns when MODIS NDVI is used without `0.0001`. |
| Add fine-to-coarse comparison failure card | `docs`, `knowledge-base`, `good first issue` | Card explains why 30 m vs 250 m direct pixel comparison is invalid. |
| Build demo registry file | `docs`, `tooling` | README demo table can be checked against one structured source. |
| Add VIIRS optional v0.3 comparison | `validation`, `remote-sensing`, `v0.4` | VIIRS comparison is optional and cannot break the primary HLS/MODIS run. |
| Add release status consistency test | `tests`, `docs` | Done in `tests/test_docs_status_consistency.py`; keep extending it as status labels evolve. |

## 🏗️ Suggested GitHub Project Columns

For a more mature GitHub workflow, use a lightweight board. The full maintenance guide is [Project Board Guide](project_board.md).

| Column | Meaning |
| --- | --- |
| Inbox | New ideas that still need scope and claim boundaries. |
| Ready | Small, public, reviewed tasks with acceptance checks. |
| Now | The current work in progress. Keep this column short. |
| Review | PR opened; tests, docs, privacy scan, and claim wording under review. |
| Done | Merged or intentionally closed with evidence. |

## 🏷️ Status Labels

Use these labels consistently in issues, PRs, and docs:

- `Golden`: live export, Drive readback, analysis, report QA, and tests are complete.
- `Partial`: a real loop has completed, but at least one required artifact or figure is missing.
- `Implementation-ready`: code, docs, and tests exist, but live evidence has not completed.
- `Planned`: scoped but not implemented.
- `Blocked`: waiting on external task completion, credentials, quota, or upstream dataset behavior.

## Promotion Rule

A demo becomes public golden evidence only when it has:

- source-backed dataset choices;
- committed recipe or canonical script;
- tests for schema and metric contracts;
- live export task ids;
- observed task completion;
- Drive connector readback;
- reproducible local analysis;
- clear limitations and no ground-truth overclaim.
