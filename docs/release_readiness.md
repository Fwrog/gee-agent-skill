# Release Readiness

Last updated: 2026-07-01

This checklist defines what can be published for the public `gee-agent-skill` repository. It covers the agent-native GEE harness, public v0.1/v0.2 golden regression examples, generic knowledge cards, and documentation assets. Personal academic demos, unpublished workflows, private asset ids, result values, and paper drafts must stay outside this repository.

## Current Public Scope

- v0.1 minimal January NDVI CSV remains a public golden regression example.
- v0.2 land-cover-aware January NDVI CSV remains a public golden regression example.
- More complex academic demos are withheld from public display and must not be referenced in README, docs, examples, evidence bundles, or packaged resources.
- `gee-plan/v0.3` remains a public plan schema and generic harness contract.
- Non-golden workflows should be described by their actual evidence level: planned, render/validate, mocked preflight blocker, or live verified only when listed in `docs/capability_matrix.md`.

## Homepage Assets

These project-bound raster visuals were generated with the built-in imagegen skill for documentation communication only:

- `assets/images/gee-agent-closed-loop-hero.png`
- `assets/images/gee-agent-knowledge-loop.png`
- `assets/images/gee-agent-toolchain.png`

They contain no readable text, logos, private geography, or scientific result claims. They are not scientific evidence.

## Required Public Checks

Run before publishing or opening a PR:

```bash
python scripts/ingest_docs.py
python -m pytest -q
gee-skill smoke-test --json
gee-skill eval evals/benchmark_suite.yml --json
git diff --check
```

Also run a privacy scan over public-facing content:

```bash
rg -n "private_key|client_secret|refresh_token|service_account|application_default_credentials" .
rg -n "private asset|draft manuscript|unpublished result" README.md README.zh-CN.md docs references examples src tests evals
```

Any hit must be reviewed. Generic privacy rules may appear in security guidance, but concrete private paths, asset ids, unpublished results, and withheld academic demo names must not appear.

## Claim Boundary

The repository may claim:

- agent-native plan/render/validate/preflight/export orchestration;
- local RAG evidence from dataset, operator, recipe, rule, and failure cards;
- explicit live-export gating through `--project` and `--confirm-live`;
- trace artifacts under `outputs/runs/<run_id>/`;
- public v0.1/v0.2 golden examples as harness regression evidence.

The repository must not claim:

- final scientific validity from a completed export alone;
- authoritative local or administrative conclusions from public substitute boundaries;
- private uploaded-dataset or private-asset results unless supplied and kept in a private workspace;
- live verification for workflows not listed as live verified in the capability matrix;
- unpublished academic demos as public examples.

## Remaining Limitations

- The parser is deterministic and pattern-oriented.
- Official Earth Engine documentation remains canonical for API behavior.
- Users must provide their own Earth Engine account, Google Cloud Project, local OAuth authentication, quota, and export destinations.
- Data Analytics, Browser, Google Drive, Computer Use, and imagegen are auxiliary tools with the boundaries documented in `docs/tool_permissions.md`.
