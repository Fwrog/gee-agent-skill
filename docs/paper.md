# Paper Draft Notes

Last updated: 2026-06-24

Working title:

```text
An Agent-Native Harness for Traceable Google Earth Engine Workflows
```

## Abstract Sketch

Coding agents can generate Earth Engine scripts quickly, but uncontrolled generation creates risks: unclear dataset choices, missing validation, accidental exports, credential leakage, and weak reproducibility. `gee-agent-skill` addresses this by routing requests through a command-line harness with source-grounded planning, template rendering, validation, preflight, explicit live-export confirmation, monitoring, and trace artifacts. Hong Kong NDVI workflows are used as golden regression examples to evaluate the harness contract rather than as standalone scientific claims.

## Problem

Earth Engine workflows often combine natural-language intent, dataset selection, operator details, quotas, authentication, and export tasks. Agent-generated code can skip review steps or blur dry-run and live-execution boundaries. A harness can make those boundaries explicit and observable.

## System

The system contains:

- CLI JSON contract for agent calls;
- `gee-plan/v0.3` editable plan schema;
- dataset catalog and recipe registry;
- local RAG evidence over dataset, operator, rules, and failure cards;
- Jinja2 script templates;
- static and semantic validation;
- dry-run reports;
- live preflight checks;
- explicit `--project` and `--confirm-live` export gate;
- export monitoring and run traces.

## Case Studies

### Case Study 1: Whole-AOI Hong Kong NDVI

The v0.1 workflow computes January 2024 mean NDVI for Hong Kong and exports one CSV row. It verifies the minimal natural-language to dry-run/live-gated export path.

### Case Study 2: Land-Cover-Aware Hong Kong NDVI

The v0.2 workflow adds Dynamic World masks and land-cover strata. It verifies that the harness can distinguish administrative boundaries from interpretation layers.

### Case Study 3: 16-Day Hong Kong NDVI

The v0.3 workflow converts a year-long 16-day NDVI request into an editable plan, rendered script, validation target, live preflight adapter, confirmed export, and task monitoring path.

See `docs/case_studies/hk_ndvi_v03.md` and `docs/evidence/v03_hk_2024_16day_ndvi/`.

## Evaluation Plan

Evaluate the harness on:

- supported golden examples;
- partially supported vegetation, water, built-up, LST, and flood task prompts;
- ambiguous prompts that should request missing fields;
- unsupported prompts that should return closest recipes rather than unsafe scripts;
- credential hygiene checks over run traces.

Metrics should follow `docs/benchmark_protocol.md`.

## Claims To Avoid

- Do not claim autonomous science.
- Do not claim universal Earth Engine task support.
- Do not claim the Hong Kong NDVI CSV is vegetation-only.
- Do not claim credentials or Google Cloud projects are provided.
- Do not treat export submission as scientific validation.

## Reproducibility Package

Reader-facing reproduction should include:

- repository commit;
- Python version and OS;
- offline command list;
- generated plan and script paths;
- validation reports;
- optional live preflight/export evidence when the reviewer has their own Earth Engine access;
- explicit statement that credentials are excluded.
