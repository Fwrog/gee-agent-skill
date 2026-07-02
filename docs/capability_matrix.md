# Capability Matrix

Last updated: 2026-07-02

This matrix is the public overclaim guard for `gee-agent-skill`. It separates public golden regression examples from generic plan/render/validate capability and withheld private academic workflows.

## Status Key

| Value | Meaning |
| --- | --- |
| Golden | Public regression example with committed trace/evidence artifacts. |
| Yes | Implemented and covered by tests or documented commands. |
| Partial | Implemented for a narrower path, generic adapter, or non-final template. |
| Blocks | Safety gate intentionally stops execution, usually because context still needs review. |
| No | Not implemented or not verified. |
| Planned | Roadmap item only. |

## Workflow Status

| Workflow / Surface | Implemented | Plan-only | Render / validate | Mocked preflight | Live preflight | Live export submitted | Live export completed | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HK Jan 2024 NDVI CSV | Golden | Yes | Yes | Yes | Yes | Yes | Yes | Public harness regression, not scientific conclusion. |
| HK Jan 2024 land-cover-aware NDVI CSV | Golden | Yes | Yes | Yes | Yes | Yes | Yes | Dynamic World strata are interpretation masks. |
| HK 2024 HLS/MODIS NDVI product intercomparison | Golden | Yes | Canonical script | No | Yes | Yes | CSV tables, annual rasters, 2x2 fallback tiles, Drive readback, local QA, figures, report, and readiness audit complete | Product-level consistency validation only; no in-situ ground truth. |
| EVI CSV | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Needs reviewed AOI/export context and live evidence. |
| NDWI GeoTIFF | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Generic preflight blocks placeholders. |
| NDBI CSV | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Bare soil and built-up interpretation need review. |
| Landsat LST CSV / image | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Thermal interpretation requires QA and scale/offset review. |
| Sentinel-1 flood/change GeoTIFF | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Event windows and thresholds require domain review. |
| Dynamic World summary CSV | Partial | Yes | Yes | No | No | No | No | Probability thresholds need review. |
| Generic zonal statistics CSV | Partial | Yes | No | No | No | No | No | Template/context completion needed. |
| Image GeoTIFF export utility | Partial | Yes | Partial | No | No | No | No | Region, CRS, dtype, and maxPixels need review. |
| Table CSV export utility | Partial | Yes | Partial | No | No | No | No | Selectors and task state must be explicit. |

Private academic demos are not public capability evidence and should not appear in this matrix.

## Harness Capability Status

| Capability | Status | Current evidence | Boundary |
| --- | --- | --- | --- |
| Agent-facing CLI contract | Implemented | `gee-skill info --json`, `doctor --json`, `recipe list --json`, catalog, plan, render, validate, preflight, run, exports, trace, eval commands | JSON shape may evolve before a stable public API. |
| Natural-language planning | Implemented | `gee-skill plan from-text ... --json`; benchmark suite | Deterministic parser covers known patterns, not open-ended natural language. |
| Editable `gee-plan/v0.3` schema | Implemented | `schemas/gee-plan-v0.3.schema.json` and runtime schema checks | Plans require review before live work. |
| Dataset/operator/failure evidence | Implemented | `gee-skill catalog evidence --category dataset|operator|failure --json` | Local cards are distilled guidance; official Earth Engine docs remain canonical. |
| Recipe registry | Implemented | `gee-skill recipe list --json` | Registry presence does not imply live export verification. |
| Static and semantic validation | Implemented | `gee-skill validate <script.py> --json`; pytest coverage | Validation reduces risk but does not prove scientific correctness. |
| Dry-run without credentials | Implemented | `gee-skill smoke-test --json`; public demo dry-runs | Dry-run must not contact Earth Engine. |
| Mocked preflight blockers | Implemented | Placeholder AOI and empty-collection tests | Blocking behavior is safety evidence, not live readiness. |
| Live export submission | Golden only | Public v0.1/v0.2 examples with explicit `--confirm-live` | Requires user-owned account, OAuth, project, quota review, and confirmation. |
| Export monitoring | Implemented | `gee-skill exports list/watch --project <id> --json` | Monitoring reports task state; it does not inspect Google Drive contents. |
| Trace inspection | Implemented | `gee-skill trace list/inspect --json` | Traces must not include credentials or local secret paths. |
| Benchmarking | Implemented | `gee-skill eval evals/benchmark_suite.yml --json` | Current benchmark is compact and local. |

## Evidence Boundary

Live-verified means a workflow has passed live Earth Engine preflight, submitted an explicitly confirmed export, and produced observed export-task completion evidence. Render/validate means the harness can create and check a script locally. Planned means the idea appears in the roadmap or registry only.

The repository does not provide Google accounts, Google Cloud projects, OAuth tokens, service account JSON, private keys, credential paths, or quota. Live commands must remain opt-in and user-owned.
