# v0.2 Mainline Repository Audit

Date: 2026-06-21

Scope: inspect the current `gee-agent-skill` repository before implementing v0.2 plan-first, land-cover-aware workflows and broader GEE AI knowledge coverage.

## Current Verified v0.1 State

- The repository has a Python package under `src/geeskill` with CLI entry point `gee-skill`.
- v0.1 deterministic natural-language routing exists in `src/geeskill/ask.py`.
- v0.1 supported request:
  `Compute January 2024 mean NDVI for Hong Kong and export CSV.`
- v0.1 template exists in:
  - `assets/templates/hk_january_2024_ndvi_csv.py.j2`
  - `src/geeskill/resources/templates/hk_january_2024_ndvi_csv.py.j2`
- v0.1 task/context resources exist in:
  - `examples/hk_2024_01_ndvi_v01/task.yaml`
  - `evals/contexts/hk_2024_01_ndvi_v01.json`
  - packaged copies under `src/geeskill/resources/`
- v0.1 live trace exists at `outputs/runs/hk-2024-01-ndvi-v01/` with the full trace artifact set.
- The v0.1 export task completed and avoided the previous `Image.reduceRegions: Image has no bands.` failure.
- The downloaded v0.1 CSV has the expected one-row schema and a low all-surface mean NDVI, which is plausible because the whole-Hong-Kong AOI includes mixed surfaces and water.

## Current Harness Capabilities

- RAG index and retrieval trace:
  - `references/knowledge_base/`
  - `references/index/gee_docs_index.json`
  - `src/geeskill/rag.py`
  - `src/geeskill/retrieval_trace.py`
- Planning:
  - `src/geeskill/planner.py` creates markdown plans from retrieved evidence.
  - `gee-skill plan` accepts task YAML.
- Templates:
  - Sentinel-2 NDVI, Landsat LST, Sentinel-1 flood, zonal statistics, Hong Kong v0.1, and Hong Kong district NDVI templates exist.
- Validation:
  - `src/geeskill/validation.py` handles static checks and credential pattern detection.
  - `src/geeskill/semantic.py` includes workflow-specific rulesets.
- Live preflight:
  - `src/geeskill/hk_ndvi_preflight.py` checks Hong Kong AOI, Sentinel-2 image counts, NDVI band presence, and a sanity statistic.
- Live execution and monitoring:
  - `src/geeskill/earthengine.py`
  - `gee-skill run`
  - `gee-skill monitor-exports`
- Tests:
  - Offline tests cover v0.1 routing, template rendering, RAG, validation, preflight mocks, run traces, and export gating.

## What Should Stay v0.1-Specific

- The current v0.1 whole-Hong-Kong all-surface NDVI workflow should remain stable and backward compatible.
- The v0.1 template should stay focused on one AOI, one month, one NDVI mean, one CSV row.
- Existing v0.1 run trace behavior should not be broken.
- The curated Hong Kong boundary should remain the administrative AOI source for Hong Kong examples.
- v0.1 should continue to distinguish OAuth success from data-aware preflight and export completion.

## What Must Generalize for v0.2

- Natural-language routing must support multiple recognized intents, not only one v0.1 phrase.
- `ask` needs a plan-only mode that writes a reviewable canonical plan before rendering or live execution.
- A plan object should become a first-class artifact, not just markdown:
  - `task_plan.yaml`
  - optional JSON-compatible plan in the trace
  - `plan.md` as the reader-facing explanation
- The CLI should preserve a plan-first lifecycle:
  - `ask --plan`: no Earth Engine contact
  - `review-plan`: inspect plan assumptions and review questions
  - `preflight-plan`: safe live probes only
  - `run-plan --confirm-live`: export only after validation and passing preflight
- Existing `ask --dry-run` should become plan + render + validate without contacting Earth Engine.
- The run trace should show whether live execution was blocked by plan review, validation, or preflight.

## v0.2 Land-Cover-Aware Workflow Needs

Target request:

```text
Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.
```

Key distinction:

- Administrative boundary defines where to compute.
- Land-cover data defines masks, strata, and interpretation groups.

The v0.2 workflow should use:

- Sentinel-2 SR Harmonized for NDVI.
- Dynamic World V1 as the primary time-matched land-cover source.
- ESA WorldCover v200 as an optional static reference/cross-check, not as a boundary source.

Expected diagnostics:

- all-surface NDVI
- non-water / land-only NDVI
- vegetation NDVI
- class-specific NDVI
- water, built, vegetation, trees, and grass fractions
- image counts and probability threshold metadata
- warnings for sparse or unavailable classes

## Broader GEE AI Knowledge Gap

The current knowledge base has useful dataset cards, operator-chain notes, exports, reducers, and failure cases, but it is still narrow. v0.2 should broaden toward a generic GEE AI research harness. Dynamic World and ESA WorldCover are only validation-case sources.

Required broader knowledge spine:

- GEE platform concepts and data model.
- Client/server execution model and safe `getInfo()` boundaries.
- Images, ImageCollections, Features, FeatureCollections, geometries.
- Filtering by date, bounds, metadata, and calendar ranges.
- Masks, QA bands, cloud masking, and compositing.
- Reducers: `reduceRegion`, `reduceRegions`, grouped reducers, histograms, combined reducers.
- Scale, CRS, projection, reprojection, and pixel area.
- Joins and linking collections.
- Exports, batch tasks, selectors, Drive/GCS destinations, and monitoring.
- Quotas, timeouts, memory limits, debugging, and common error recovery.
- Dataset-card templates and source metadata expectations.
- Workflow recipes beyond Hong Kong NDVI: LST, SAR flood/change, zonal statistics, time series, classification/cross-tabulation.

Official sources checked for v0.2 planning include Google Earth Engine documentation for Dynamic World V1, ESA WorldCover v200, client/server behavior, scale, projections, reducers, filterDate/filterBounds, reduceRegion/reduceRegions, best practices, debugging, usage quotas, and Export.table.toDrive.

## Current GitHub Project Gaps

- `.gitignore`, `LICENSE`, and package metadata exist.
- GitHub-facing files still need review/addition:
  - `.github/workflows/ci.yml`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/pull_request_template.md`
  - `CONTRIBUTING.md`
- README should better separate:
  - what is implemented
  - v0.1 verified path
  - v0.2 plan-first path
  - how to authenticate
  - how to run dry-run/preflight/live
  - what the harness does not prove scientifically

## Recommended Implementation Order

1. Add a canonical plan module and plan schema.
2. Extend deterministic router with v0.2 request variants.
3. Add `ask --plan`, `review-plan`, `preflight-plan`, and `run-plan` or equivalent plan-first commands.
4. Add broader GEE knowledge-base markdown and rebuild the index.
5. Add Dynamic World and ESA WorldCover dataset cards and land-cover workflow notes.
6. Add v0.2 land-cover-aware template.
7. Add land-cover-aware preflight and diagnostics.
8. Extend validators/errors.
9. Add tests and evaluation cases.
10. Update README/SKILL/docs/GitHub files.
11. Run release audit and write `docs/reviews/v02-landcover-aware-release-audit.md`.

## Initial Risk Register

- Scope creep: v0.2 should broaden the knowledge architecture but still validate implementation through one concrete Hong Kong land-cover NDVI workflow.
- Scientific interpretation risk: all-surface NDVI should not be presented as vegetation-only NDVI.
- Land-cover uncertainty: Dynamic World labels should be probability-aware; sparse or low-confidence classes should produce nulls/warnings rather than silent conclusions.
- Live export risk: `run-plan` must refuse export when validation or preflight fails.
- Credential safety: project IDs, OAuth files, service account JSON, refresh tokens, and local credential paths must not be committed or written into trace artifacts.
