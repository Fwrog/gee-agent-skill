# Capability Matrix

Last updated: 2026-06-25

This matrix is the public overclaim guard for `gee-agent-skill`. It separates the general harness from the Hong Kong NDVI golden examples and distinguishes planning, rendering, validation, preflight, and live export evidence.

## Status Key

| Value | Meaning |
| --- | --- |
| Yes | Implemented and covered by tests, committed examples, or documented reproduction commands. |
| Golden | Verified golden example used as regression evidence for the harness contract. |
| Partial | Implemented for a narrower path, generic adapter, or non-final template; review is required before stronger claims. |
| Blocks | Safety gate intentionally stops execution, usually because AOI/export context is still a placeholder. |
| No | Not implemented or not verified for that workflow. |
| Planned | Roadmap item only; do not claim current support. |

## Workflow Status

| Workflow / Surface | Implemented | Plan-only | Render / validate | Mocked preflight | Live preflight | Live export submitted | Live export completed | Planned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HK Jan 2024 NDVI CSV | Golden | Yes | Yes | Yes | Yes | Yes | Yes | No |
| HK Jan 2024 land-cover-aware NDVI CSV | Golden | Yes | Yes | Yes | Yes | Yes | Yes | No |
| HK 2024 16-day NDVI CSV | Golden | Yes | Yes | Yes | Yes | Yes | Yes | No |
| EVI CSV | Partial | Yes | Yes | Partial | No | No | No | Recipe-specific live preflight |
| NDWI GeoTIFF | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Recipe-specific live preflight |
| NDBI CSV | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Recipe-specific live preflight |
| Landsat LST CSV / image | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Recipe-specific live preflight |
| Sentinel-1 flood/change GeoTIFF | Partial | Yes | Yes | Blocks placeholder context | No | No | No | Recipe-specific live preflight |
| Dynamic World summary CSV | Partial | Yes | Yes | No | No | No | No | Live preflight adapter |
| Generic zonal statistics CSV | Partial | Yes | No | No | No | No | No | Template/context completion |
| Image GeoTIFF export utility | Partial | Yes | Partial | No | No | No | No | Safer generic image adapter |
| Table CSV export utility | Partial | Yes | Partial | No | No | No | No | Broader table adapter coverage |

## Harness Capability Status

| Capability | Status | Current evidence | Boundary |
| --- | --- | --- | --- |
| Agent-facing CLI contract | Implemented | `gee-skill info --json`, `doctor --json`, `recipe list --json`, catalog, plan, render, validate, preflight, run, exports, trace, eval commands | JSON shape may still evolve before a stable public API. |
| Natural-language planning | Implemented | `gee-skill plan from-text ... --json`; 22-case benchmark suite | Deterministic parser covers known task patterns, not open-ended natural language. |
| Editable `gee-plan/v0.3` schema | Implemented | `schemas/gee-plan-v0.3.schema.json` and runtime schema checks | Plans require review before live work. |
| Dataset/operator/failure evidence | Implemented | `gee-skill catalog evidence --category dataset|operator|failure --json` | Local cards are distilled guidance; official Earth Engine docs remain canonical. |
| Recipe registry | Implemented | `gee-skill recipe list --json`; source and packaged registry files | Registry presence does not imply live export verification. |
| Static and semantic validation | Implemented | `gee-skill validate <script.py> --json`; pytest coverage | Validation reduces risk but does not prove scientific correctness. |
| Dry-run without credentials | Implemented | `gee-skill smoke-test --json`; v0.2 dry-run; v0.3 render/validate | Dry-run must not contact Earth Engine. |
| Mocked preflight blockers | Implemented | Placeholder AOI and empty-collection tests | Blocking behavior is safety evidence, not live readiness. |
| Live preflight | Golden only | HK v0.1/v0.2/v0.3 evidence | Non-golden workflows need recipe-specific live adapters and domain review. |
| Live export submission | Golden only | HK golden examples with explicit `--confirm-live` | Requires user-owned account, OAuth, project, quota review, and confirmation. |
| Export completion evidence | Golden only | Sanitized task metadata and CSV evidence for verified examples | Completion is workflow evidence, not scientific validation. |
| Export monitoring | Implemented | `gee-skill exports list/watch --project <id> --json`; compatibility `monitor-exports` | Monitoring reports task state and errors; it does not inspect Google Drive contents. |
| Trace inspection | Implemented | `gee-skill trace list/inspect --json`; `outputs/runs/<run_id>/` contract | Traces must not include credentials or local secret paths. |
| Benchmarking | Implemented | `gee-skill eval evals/benchmark_suite.yml --json` | Current benchmark is small and local; it is not AutoGEEval-scale coverage. |

## Evidence Boundary

Live-verified means a workflow has passed live Earth Engine preflight, submitted at most one explicitly confirmed export in the verified run, and produced observed export-task completion evidence. Render/validate means the harness can create and check a script locally; it does not mean the workflow was run in Earth Engine. Planned means the idea appears in the roadmap or registry direction only.

The repository does not provide Google accounts, Google Cloud projects, OAuth tokens, service account JSON, private keys, credential paths, or quota. Live commands must remain opt-in and user-owned.
