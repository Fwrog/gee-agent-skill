# Capability Matrix

Last updated: 2026-06-25

This matrix describes the repository as an agent-native Google Earth Engine harness. Hong Kong NDVI workflows are golden examples and regression evidence, not the full product boundary.

## Status Legend

| Status | Meaning |
| --- | --- |
| Supported | Implemented and covered by tests or documented reproduction commands. |
| Golden | Supported path used as regression evidence for the harness contract. |
| Partial | Some parser, recipe, catalog, or validation coverage exists, but end-to-end live export is not verified. |
| Planned | Described as future work; do not claim support. |

## Harness Capabilities

| Capability | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| CLI JSON contract | Supported | `gee-skill info --json`, `doctor --json`, catalog, recipe, rules, plan commands | JSON shape is for agent use; schema may still evolve before a stable public API. |
| Natural-language planning | Supported | `gee-skill plan from-text ... --json` | Deterministic support is strongest for known task patterns. |
| Editable plan schema | Supported | `gee-plan/v0.3` plans | Plans must be reviewed before live use. |
| Local RAG evidence | Supported | dataset, operator, recipe, rules, and failure cards; `catalog evidence --category ... --json` | Official Earth Engine docs remain canonical. |
| Retrieval coverage checks | Supported | `gee-skill eval evals/benchmark_suite.yml --json` | Coverage proves local evidence availability, not that every retrieved source is sufficient for publication. |
| Template rendering | Supported | `gee-skill plan from-yaml ... --script-out ... --json` | Only approved templates should be rendered. |
| Static and semantic validation | Supported | `gee-skill validate ... --json`, pytest coverage | Validation reduces risk but does not prove scientific correctness. |
| Dry runs without credentials | Supported | `gee-skill smoke-test --json`, dry-run commands | Dry run must not contact Earth Engine. |
| Generic preflight blocking | Supported | placeholder AOI/export context tests and mocked empty-collection benchmark | This proves safety blocking, not live export readiness for every recipe. |
| Live preflight | Supported for golden adapters | `preflight-hk-ndvi`, `preflight-plan` for v0.3 HK 16-day NDVI | Preflight contacts Earth Engine but must not start exports. |
| Confirmed live export | Supported for golden adapters | `run-plan --project <id> --confirm-live` | Requires user-owned Earth Engine access, OAuth, project id, quota review, and explicit confirmation. |
| Export monitoring | Supported | `monitor-exports --project <id> --json` | Monitoring reports task state; it does not validate scientific outputs. |
| Run traces | Supported | `outputs/runs/<run_id>/` contract | Traces must not contain credentials or local secret paths. |

## Workflow Coverage

| Workflow | Status | Current Evidence | Not A Claim Of |
| --- | --- | --- | --- |
| HK January 2024 whole-AOI NDVI CSV | Golden | `examples/hk_2024_01_ndvi_v01/task.yaml`, `docs/v01_hk_january_ndvi.md` | Vegetation-only or district-level scientific product. |
| HK January 2024 land-cover-aware NDVI CSV | Golden | `examples/hk_2024_01_ndvi_landcover_v02/task.yaml`, `docs/v02_landcover_aware_ndvi.md` | Perfect land-cover classification or policy-ready vegetation assessment. |
| HK 2024 16-day NDVI CSV | Golden | `examples/hk_2024_16day_ndvi/task.yaml`, `docs/v03_hk_2024_16day_ndvi.md` | Universal time-series product or optimized remote-sensing methodology. |
| EVI CSV workflow | Partial | v0.3 parser, Sentinel-2 expression render path, semantic validation, and benchmark coverage | Live export verification. |
| NDWI GeoTIFF workflow | Partial | v0.3 parser, template render, semantic validation, generic preflight gate, and context-review block tests | Live export verification. |
| NDBI CSV workflow | Partial | v0.3 parser, template render, semantic validation, generic preflight gate, and context-review block tests | Live export verification. |
| Landsat LST CSV workflow | Partial | v0.3 parser, template render, semantic validation, generic preflight gate, and context-review block tests | Live export verification. |
| Sentinel-1 before/after flood GeoTIFF workflow | Partial | v0.3 parser, template render, semantic validation, generic preflight gate, and context-review block tests | Live export verification or disaster-response readiness. |
| Dynamic World land-cover summary | Partial | v0.3 parser, dataset/recipe cards, template render, semantic rules, and benchmark coverage | Live export verification or final classification methodology. |
| Zonal statistics CSV workflow | Partial | v0.3 parser, recipe card, table-export template, and benchmark coverage | Fully inferred image-expression planning or live export verification. |
| Standalone image GeoTIFF export | Partial | v0.3 parser, export-image recipe card, semantic rules, and unknown-dataset guard | A universal image-export adapter for arbitrary Earth Engine expressions. |
| District monthly HK NDVI | Planned | `examples/hk_2024_monthly_ndvi/task.yaml` | Verified v0.3 live path. |

## Security Boundary

The repository does not provide Google accounts, Earth Engine credentials, Google Cloud projects, OAuth tokens, service account JSON, private keys, or credential paths. Live commands require local user-controlled authentication and must keep `--confirm-live` as an explicit gate.
