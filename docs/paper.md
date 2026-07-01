# Paper Draft Notes

Last updated: 2026-06-25

Working title:

```text
An Agent-Native Harness for Traceable Google Earth Engine Workflows
```

## Abstract Sketch

Coding agents can draft Google Earth Engine scripts from natural language, but unrestricted code generation creates practical risks: hallucinated datasets, invalid operators, missing masks, unsafe client-side calls, accidental live exports, weak task monitoring, and poor reproducibility. `gee-agent-skill` addresses this by exposing Earth Engine workflows through an agent-native CLI harness. The system converts requests into editable plans, retrieves local dataset/operator/failure evidence, renders approved Python templates, validates scripts, performs live preflight checks, gates export behind explicit confirmation, monitors Earth Engine tasks, and writes trace artifacts. Hong Kong NDVI workflows are used as golden examples and regression evidence; the paper contribution is the harness design and evaluation protocol, not a new vegetation-index method.

## Problem Statement

LLM-generated Earth Engine code often fails for reasons that are domain-specific rather than syntactic:

- dataset and band identifiers must match the Earth Engine catalog;
- optical, SAR, thermal, and land-cover workflows require different masks and scale assumptions;
- reducers and exports need explicit geometry, scale, CRS, selectors, and `maxPixels`;
- `getInfo()` and other client-side calls can block or break large workflows;
- export tasks are asynchronous and need monitoring;
- live execution requires authenticated user credentials and a Google Cloud Project;
- generated code needs an audit trail before researchers can trust or revise it.

## System Overview

The proposed system is:

```text
natural language -> plan -> RAG evidence -> render -> validate -> preflight -> confirmed export -> monitor -> trace
```

Components:

- deterministic CLI JSON contract for agent calls;
- `gee-plan/v0.3` editable plan schema;
- dataset catalog and recipe registry;
- local RAG evidence over dataset, operator, recipe, rule, and failure cards;
- Jinja2 Earth Engine Python templates;
- static and semantic validation;
- dry-run reports;
- live preflight checks;
- explicit `--project` and `--confirm-live` export gate;
- export monitoring;
- run traces and sanitized golden evidence bundles;
- benchmark suite for parse, plan, render, validation, evidence coverage, safety blocks, and public golden workflows.

## Contributions

1. A general, agent-native GEE harness with structured commands and traceable state.
2. A distilled knowledge base for datasets, operators, recipes, and failure modes.
3. A reviewable plan schema that separates user intent from executable code.
4. Semantic validation and preflight gates for safer Earth Engine exports.
5. Golden live examples that demonstrate end-to-end export and monitoring boundaries.
6. A compact benchmark suite that tests supported, ambiguous, unsupported, and safety-critical task cases.

## Case Studies

### Case Study 1: Whole-AOI Hong Kong NDVI

The v0.1 workflow computes January 2024 mean NDVI for Hong Kong and exports one CSV. It verifies the minimal path from natural-language request to reviewable plan, validation, preflight, confirmed export, and monitoring.

### Case Study 2: Land-Cover-Aware Hong Kong NDVI

The v0.2 workflow adds Dynamic World interpretation strata. It verifies that the harness can preserve the distinction between administrative AOI, land-cover masks, all-surface means, non-water means, and vegetation-like class summaries.

### Private Academic Workflows

More complex academic demos are intentionally excluded from the public paper notes. Reusable lessons from those workflows should appear only as generic dataset, rule, failure, or workflow cards after privacy review.

## Evaluation Plan

Report:

- `python -m pytest` result;
- benchmark pass/fail count for `evals/benchmark_suite.yml`;
- smoke-test result;
- render/validate outcomes for EVI, NDWI, and other non-golden templates;
- mocked preflight blockers such as `V03_CONTEXT_REVIEW_REQUIRED`;
- live preflight/export completion only for workflows listed as live completed in `docs/capability_matrix.md`;
- wheel build and wheel-smoke results;
- secret scan result;
- overclaim audit result.

Metrics should follow `docs/benchmark_protocol.md`.

## Claims To Avoid

- Do not claim autonomous science.
- Do not claim universal Earth Engine task support.
- Do not claim production-ready coverage for every GEE dataset or operator.
- Do not claim non-golden workflows are live-export verified.
- Do not claim the Hong Kong NDVI CSV is vegetation-only.
- Do not claim credentials, Google accounts, or Google Cloud projects are provided.
- Do not treat export submission or completion as scientific validation.

## Reproducibility Package

A reviewer-facing package should include:

- repository commit;
- Python version and OS;
- install command from repository root;
- offline command list;
- generated plan and script paths;
- validation and dry-run reports;
- optional live preflight/export evidence when the reviewer has their own Earth Engine access;
- sanitized golden artifacts under `examples/golden/`;
- explicit statement that credentials, OAuth tokens, refresh tokens, service account JSON, private keys, and local credential paths are excluded.

## Limitations

- The parser is deterministic and pattern-oriented, not full natural-language understanding.
- Live validation is narrow and limited to golden examples.
- Non-golden workflows are valuable for plan/render/validate and safety-gate evidence, but require recipe-specific preflight and domain review before live claims.
- Scientific interpretation requires independent remote-sensing review beyond the harness.
