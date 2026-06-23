# Agent Goal: General GEE Harness Refocus

Use this brief when continuing v0.3+ work on `gee-agent-skill`.

## Objective

Build an installable, documented, tested, agent-native command-line harness that lets Codex or another coding agent turn natural-language Google Earth Engine requests into reviewable plans, source-grounded dataset/operator choices, validated Earth Engine Python scripts, safe live preflight checks, explicit user-confirmed exports, export monitoring, and reproducible traces.

Hong Kong NDVI workflows are verified golden examples and regression tests. They must not define the whole project identity.

## Default Flow

```text
natural-language request
-> intent classification
-> dataset/operator/recipe/failure/rule retrieval
-> reviewable plan
-> user review
-> script rendering
-> static and semantic validation
-> live preflight
-> explicit confirmation
-> export task
-> monitoring
-> trace/report
```

Natural language must not directly trigger opaque live execution.

## Tool Boundaries

- CLI/API first: use `gee-skill` and the official Earth Engine Python API as the authoritative executor.
- Browser: use for official docs inspection, local preview review, or visual QA. Do not use browser automation as the normal GEE execution path.
- Computer Use: use only when no CLI, API, browser plugin, or repo-native path can complete the task. Risky UI actions require action-time confirmation.
- Image generation: use for README/homepage visuals or explanatory raster assets. Do not use generated images as scientific evidence.

## v0.3 Requirements

- Maintain golden examples:
  - `Compute January 2024 mean NDVI for Hong Kong and export CSV.`
  - `Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.`
  - `Compute 16-day NDVI for Hong Kong in 2024 and export CSV.` This must render and validate through `hk_2024_16day_ndvi_csv`, not only produce a plan.
- Keep these commands working:
  - `gee-skill info --json`
  - `gee-skill doctor --json`
  - `gee-skill observe "<request>" --json`
  - `gee-skill catalog search/show/recommend --json`
  - `gee-skill recipe list/show --json`
  - `gee-skill rules list/show --json`
  - `gee-skill plan from-text/from-yaml/review/set --json`
- Preserve deterministic JSON envelopes for new agent-facing commands:
  - `{ "ok": true, "data": ... }`
  - `{ "ok": false, "error": { "code": ..., "message": ..., "hint": ... } }`
- Keep live execution gated by `--project` and `--confirm-live`.
- Never print or commit credentials.

## Distilled Knowledge Base

The knowledge base should combine:

- official Google Earth Engine guides, API references, and data catalog pages;
- structured dataset, operator, recipe, failure, and ruleset cards;
- reviewed 30-50 pattern-only GitHub seed inventory at `references/corpus/github_gee_seed_repos.yml`;
- broad 100+ metadata-only GitHub discovery queue at `references/corpus/github_gee_discovery_100.yml`;
- explicit priority lanes for `giswqs`/OpenGeo, `gee-community`, and paper-linked GEE repositories from remote-sensing journals;
- generated RAG index with retrieval trace coverage for dataset, operator, recipe, failure, rule, and export evidence.

GitHub sources are discovery inputs, not vendored code. Promote only small, attributed operator patterns and validation implications after license and quality review.

## Corpus Exam Workflow

Use external GEE repositories as an exam set for the harness:

1. Build or refresh `references/corpus/github_gee_seed_repos.yml`.
2. Refresh `references/corpus/github_gee_discovery_100.yml` with `scripts/discover_gee_repos.py` when broad coverage needs review.
3. Add high-signal community sources from `giswqs`/OpenGeo and `gee-community` when they improve task coverage.
4. Add paper-linked repositories only after article DOI or publisher URL, license, private-asset dependency, inspected commit, and reproducibility scope are recorded.
5. Clone or checkout reviewed sources outside the repository, for example under `/tmp/gee-corpus-sample`.
6. Run `scripts/analyze_gee_corpus.py <repo1> <repo2> ... --out outputs/corpus/<run>.json`.
7. Compare observed operator/style groups with current rules.
8. Promote only pattern-level findings into `references/knowledge_base/` and semantic rules.
9. Do not copy third-party code into this repository.

The target is iterative expansion toward 100+ discovered candidates and a growing set of reviewed local source directories, not a one-time scrape.

## Test Gate

Before claiming completion, run:

```bash
python -m pytest
gee-skill info --json
gee-skill doctor --json
gee-skill auth check --json
gee-skill recipe list --json
gee-skill rules list --json
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
gee-skill smoke-test --json
gee-skill evaluate evals/benchmark_suite.yml
```

If testing from an editable checkout and the environment does not process editable `.pth` files, replace `gee-skill` with `PYTHONPATH=src python -m geeskill.cli`.

If live credentials are available, run only opt-in live smoke tests after explicit user confirmation.
