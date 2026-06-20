# Research Note: AutoGEEval++ Evaluation Design

source_id: research-autogeeval-plus
source_type: research-preprint
publisher: arXiv
url: https://arxiv.org/abs/2506.10365
retrieved_at: 2026-06-21
primary_status: non-canonical
ee_language: Python
risk_level: medium

## How To Use This Note

Use AutoGEEval++ as a benchmark-design reference for evaluating generated Earth Engine code. Do not use it as an API source, and do not copy benchmark data into this repository without license review.

## Transferable Evaluation Structure

AutoGEEval++ motivates three levels of tests:

- Unit tests: focused checks for single API functions or small operations.
- Combo tests: multi-operator workflows synthesized from common operator chains.
- Theme tests: end-to-end geospatial tasks grounded in real research workflows.

This repository mirrors that structure with unit tests for retrieval/rendering/validation, combo checks in `gee-skill smoke-test`, and the theme task `hk_2024_monthly_ndvi`.

## Boundary Testing

Boundary cases should be explicit. Useful examples include invalid dates, missing AOI, missing scale, missing export descriptions, unresolved template variables, no retrieval hits, no credentials for live commands, and failed task polling.

## Error Taxonomy

Validation and runtime reporting should distinguish at least these classes:

- Syntax errors.
- Parameter errors such as omitted or misspelled required arguments.
- Output-type errors such as image exports where table exports are required.
- Runtime or platform errors surfaced by Earth Engine tasks.
- Resource and quota errors such as memory, pixel count, or task queue limits.

## Metrics For Regression

Use practical repository-level metrics instead of model leaderboards:

- Retrieval top-k hit quality on curated docs.
- Template render success with strict context validation.
- Static validation error/warning precision on fixtures.
- Offline smoke-test success without credentials.
- Live execution boundary safety: dry runs never contact Earth Engine, live runs require explicit project.

## Source Risk

The paper evaluates model-generated code and includes time-sensitive model comparisons. This repository should reuse its evaluation categories and error taxonomy, not its leaderboard conclusions.

