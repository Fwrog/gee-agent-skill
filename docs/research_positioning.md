# Research Positioning

Last updated: 2026-07-01

## Core Claim

`gee-agent-skill` is an agent-native Google Earth Engine harness that turns natural-language geospatial tasks into reviewable, RAG-grounded, validated, and traceable Earth Engine workflows.

The project is not a new NDVI method or a universal Earth Engine autopilot. Its contribution is an operations and reproducibility layer for agent-assisted geospatial computing:

```text
natural language -> plan -> RAG evidence -> render -> validate -> preflight -> confirmed export -> monitor -> trace
```

## Contributions

1. **General GEE agent harness**: a CLI command surface for `auth / catalog / aoi / recipe / plan / render / validate / preflight / run / exports / trace / eval`.
2. **Dataset/operator/failure knowledge base**: distilled cards for datasets, operators, recipes, safety rules, and known failure modes.
3. **Reviewable plan schema**: `gee-plan/v0.3` makes user intent, AOI, time range, datasets, operators, outputs, and execution context inspectable before code execution.
4. **Semantic validation and preflight**: validators and preflight gates reduce unsafe exports, missing-band failures, empty-collection failures, and placeholder-context execution.
5. **Golden public examples**: v0.1 and v0.2 NDVI workflows serve as compact regression evidence for live preflight, confirmed export, monitoring, and trace behavior.
6. **Adaptive learning loop**: reusable lessons are promoted only as dataset cards, rule cards, failure cases, or workflow cards with source, `last_checked`, scope, and claim boundaries.

## Target Audience

- geospatial researchers who need auditable Earth Engine workflows;
- urban informatics researchers using remote-sensing indicators as reproducible evidence;
- AI agent tool builders designing safe CLI contracts for external systems;
- remote-sensing students learning how dataset choice, masking, scale, reducers, exports, and authentication interact.

## Public Golden Examples

Public examples are intentionally small harness regressions:

- v0.1: January 2024 whole-AOI NDVI CSV;
- v0.2: January 2024 land-cover-aware NDVI CSV.

They exercise AOI handling, Sentinel-2 imagery, cloud filtering, index computation, reducers, table export, preflight, task monitoring, and trace hygiene. They do not prove universal GEE task automation or final scientific interpretation.

Private academic demos and unpublished workflows are not public examples. Generic lessons from them may be promoted only after privacy review and source verification.

## Evaluation Framing

Credible evaluation should report:

- plan-field correctness for supported prompt families;
- evidence coverage for dataset/operator/recipe/failure/export categories;
- render and validation outcomes for approved templates;
- dry-run behavior without Earth Engine credentials;
- mocked preflight blockers for missing AOI or placeholder export context;
- optional live preflight and export completion only for explicitly verified public golden examples;
- trace completeness and credential hygiene.

Do not use export completion as a proxy for scientific validity. A task can complete and still require domain review, independent validation, or methodological revision.

## Limitations

- The deterministic parser is not full natural-language understanding.
- Live verification is limited to public golden examples listed in `docs/capability_matrix.md`.
- Non-golden EVI, NDWI, NDBI, Landsat LST, Sentinel-1, Dynamic World, zonal statistics, GeoTIFF, and generic table paths should be described at their actual status: plan-only, render/validate, mocked preflight, or planned.
- Scientific interpretation requires domain review, uncertainty analysis, and source-data validation beyond the harness.
- Users must provide their own Earth Engine account, Google Cloud Project, local OAuth authentication, quota, and export destination.
- The local knowledge base improves grounding but does not replace official Earth Engine documentation or current dataset catalog checks.
