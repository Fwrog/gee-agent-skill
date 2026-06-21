# v0.2 Cross-Agent Review Notes

## v0.2 Repository Auditor

Keep v0.1 live export behavior stable. Generalize the harness through plan-first commands, task plans, stronger trace artifacts, and land-cover-aware diagnostics without redesigning the entire CLI.

## Product / GitHub Project Engineer

README and docs must present the project as a real open-source Earth Engine research harness, with clear quickstart, authentication boundary, dry-run/preflight/live stages, and explicit credential warnings.

## Plan-First Workflow Architect

The canonical flow is `ask --plan`, `review-plan`, `preflight-plan`, then `run-plan --confirm-live`. Plan files are reviewable YAML and are copied into run traces.

## Natural-Language Router Engineer

Routing remains deterministic and offline. v0.2 land-cover-aware Hong Kong NDVI variants resolve to one supported intent; unsupported or ambiguous tasks return structured errors.

## Land-Cover Data Engineer

Dynamic World V1 is the primary time-matched land-cover source. ESA WorldCover v200 is documented as an optional static reference. Land-cover data defines masks and strata, not AOI boundaries.

## General GEE Knowledge Engineer

The retrieval corpus must be broader than Dynamic World and WorldCover. v0.2 adds core client/server, scale/projection, reducers, joins, exports/tasks, quotas/debugging, workflow, and failure-case notes.

## v0.2 Template Engineer

The v0.2 template exports a compact wide CSV with all-surface, non-water, vegetation, built, bare, trees, grass, shrub/scrub NDVI diagnostics and class fractions.

## Live Preflight Engineer

Preflight must block export before `task.start()` when AOI, Sentinel-2, NDVI, Dynamic World collection, label band, probability bands, or core class fractions are unavailable.

## Result Diagnostics Engineer

Low all-surface NDVI should be interpreted alongside water, built, and vegetation fractions. The harness must not overclaim ecological meaning from aggregate all-surface NDVI.

## Validation and Safety Engineer

Semantic validation checks Dynamic World dataset use, label/probability bands, probability threshold, class fractions, diagnostic NDVI fields, explicit selectors, and preflight-required marker.

## Test and Evaluation Engineer

Offline tests cover v0.2 routing, plan generation, dry-run rendering, semantic validation, retrieval trace coverage, land-cover preflight failure categories, and export refusal after failed preflight.
