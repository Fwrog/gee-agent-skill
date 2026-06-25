# Research Positioning

Last updated: 2026-06-25

## Core Claim

`gee-agent-skill` is an agent-native Google Earth Engine harness that turns natural-language geospatial tasks into reviewable, RAG-grounded, validated, and traceable Earth Engine workflows.

The project is not a new NDVI method or a universal Earth Engine autopilot. Its contribution is an operations and reproducibility layer for agent-assisted geospatial computing:

```text
natural language -> plan -> RAG evidence -> render -> validate -> preflight -> confirmed export -> monitor -> trace
```

## Problem

LLMs can produce Earth Engine code quickly, but uncontrolled generation is risky in geospatial workflows:

- dataset IDs may be hallucinated or outdated;
- band names, QA masks, scale, projection, reducers, and export selectors may be wrong;
- client-side calls such as unsafe `getInfo()` can block or fail at scale;
- empty image collections and missing bands may only fail after a live request;
- dry-run, preflight, and live export boundaries are often blurred;
- task state, export metadata, and source evidence are hard to audit after the fact.

For researchers and students, the hardest part is not only Python syntax. It is connecting data semantics, Earth Engine execution rules, validation, quota-sensitive exports, and reproducibility.

## Solution

The harness makes agent execution explicit:

- CLI commands return deterministic JSON for agent orchestration.
- Natural-language prompts are converted into editable `gee-plan/v0.3` YAML.
- Dataset, operator, recipe, and failure cards provide local RAG evidence.
- Approved templates render Earth Engine Python scripts.
- Static and semantic validators check unsafe patterns before live use.
- Preflight checks authentication, AOI, collection size, required bands, and export metadata.
- Live export requires `--project` and explicit `--confirm-live`.
- Export monitoring records task status.
- Run traces preserve plan, evidence, validation, preflight, export metadata, and final notes without credentials.

## Contributions

1. **General GEE agent harness**: a CLI command surface for `auth / catalog / aoi / recipe / plan / render / validate / preflight / run / exports / trace / eval`.
2. **Dataset/operator/failure knowledge base**: distilled cards for datasets, operators, recipes, safety rules, and known failure modes.
3. **Reviewable plan schema**: `gee-plan/v0.3` makes user intent, AOI, time range, datasets, operators, outputs, and execution context inspectable before code execution.
4. **Semantic validation and preflight**: validators and preflight gates reduce unsafe exports, missing-band failures, empty-collection failures, and placeholder-context execution.
5. **Golden live examples**: Hong Kong NDVI workflows serve as compact regression evidence for live preflight, confirmed export, monitoring, and trace behavior.
6. **Benchmark suite**: local benchmark cases test supported planning, ambiguous prompts, unsupported requests, render/validation paths, RAG evidence coverage, and mocked safety blocks.

## Target Audience

- geospatial researchers who need auditable Earth Engine workflows;
- urban informatics researchers using remote-sensing indicators as reproducible evidence;
- AI agent tool builders designing safe CLI contracts for external systems;
- remote-sensing students learning how dataset choice, masking, scale, reducers, exports, and authentication interact.

## Golden Examples

Hong Kong NDVI is intentionally demoted to evidence, not promoted as the project scope:

- v0.1: January 2024 whole-AOI NDVI CSV;
- v0.2: January 2024 land-cover-aware NDVI CSV;
- v0.3: 2024 16-day NDVI CSV.

These examples exercise AOI handling, Sentinel-2 imagery, cloud filtering, index computation, reducers, table export, preflight, task monitoring, and trace hygiene. They do not prove universal GEE task automation or final scientific interpretation.

## Evaluation Framing

Credible evaluation should report:

- plan-field correctness for supported prompt families;
- evidence coverage for dataset/operator/recipe/failure/export categories;
- render and validation outcomes for approved templates;
- dry-run behavior without Earth Engine credentials;
- mocked preflight blockers for missing AOI or placeholder export context;
- optional live preflight and export completion only for explicitly verified golden examples;
- trace completeness and credential hygiene.

Do not use export completion as a proxy for scientific validity. A task can complete and still require domain review, independent validation, or methodological revision.

## Limitations

- The deterministic parser is not full natural-language understanding.
- Live verification is limited to golden examples listed in `docs/capability_matrix.md`.
- Non-golden EVI, NDWI, NDBI, Landsat LST, Sentinel-1, Dynamic World, zonal statistics, GeoTIFF, and generic table paths should be described at their actual status: plan-only, render/validate, mocked preflight, or planned.
- Scientific interpretation requires domain review, uncertainty analysis, and source-data validation beyond the harness.
- Users must provide their own Earth Engine account, Google Cloud Project, local OAuth authentication, quota, and export destination.
- The local knowledge base improves grounding but does not replace official Earth Engine documentation or current dataset catalog checks.

## Paper Direction

A defensible paper or technical report title is:

```text
An Agent-Native Harness for Traceable Google Earth Engine Workflows
```

The strongest scope is a systems and reproducibility report. The Hong Kong workflows are evaluated golden cases, while the broader contribution is the CLI contract, knowledge base, plan schema, validators, preflight gates, export monitoring, trace artifacts, and benchmark protocol.
