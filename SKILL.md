---
name: gee-agent-skill
description: Plan, ground, render, validate, preflight, run, and audit reproducible Google Earth Engine Python workflows with source-backed recipes, export monitoring, and run traces. Use for GEE task planning, script generation, dataset or operator retrieval, private-raster handoffs, annual multi-source workflows, and evidence-bounded evaluation.
---

# GEE Agent Skill

Build reviewable Earth Engine workflows through the `gee-skill` CLI and the official Earth Engine Python API. Keep the normal path plan-first, source-grounded, traceable, and explicit about what was actually verified.

## Core Workflow

1. Work from the repository root. Check the installed surface with:
   `gee-skill info --json`, `gee-skill doctor --json`, `gee-skill recipe list --json`, and `gee-skill rules list --json`.
2. Convert the request into an editable plan:
   `gee-skill plan from-text "<request>" --json`.
   If it returns `AMBIGUOUS_TASK`, report the missing fields instead of guessing.
3. Select a registered recipe and retrieve evidence:
   `gee-skill recipe show <recipe-id> --json`,
   `gee-skill catalog recommend --task-type <type> --metric <metric> --json`, and
   `gee-skill search-docs "<dataset operator failure query>" --json`.
4. Review the plan and resolve an unclear AOI:
   `gee-skill plan review <plan.yaml> --json` and
   `gee-skill aoi resolve "<request>" --json`.
5. Render and validate before live work:
   `gee-skill render <plan.yaml> --script-out <script.py> --json` and
   `gee-skill validate <script.py> --json`.
6. Run preflight with an explicit project:
   `gee-skill preflight <plan.yaml> --project <project-id> --json`.
   Treat `V03_CONTEXT_REVIEW_REQUIRED` as missing reviewed context, not an authentication failure.
7. Run live only after preflight and explicit confirmation:
   `gee-skill run <plan.yaml> --project <project-id> --confirm-live --json`.
8. Monitor submitted exports:
   `gee-skill exports list --project <project-id> --json` or
   `gee-skill exports watch --project <project-id> --task-id <id> --json`.
9. Inspect the persisted trace before reporting results:
   `gee-skill trace inspect <run_id> --json`.
10. Use `gee-skill eval evals/benchmark_suite.yml --json` for offline regression evidence. Check [docs/capability_matrix.md](docs/capability_matrix.md) before assigning a readiness label.

## Evidence And Claim Boundaries

- Say `live verified` only when the capability matrix records a completed public live path. Otherwise use the exact supported level: `render/validate verified`, `dry-run verified`, `mocked preflight blocked`, `planned`, or `experimental`.
- Treat exports and model outputs as workflow artifacts, not scientific conclusions or ground truth.
- Prefer official Earth Engine documentation and Data Catalog facts. Use papers and community sources only for scoped methods or patterns.
- When promoting a reusable lesson, add a dataset, rule, failure, or workflow card with a source, `last_checked`, scope, limitations, and explicit non-claims.
- Keep real study identifiers, project and asset IDs, bucket and object names, task IDs, private source files, draft manuscripts, and unpublished results outside the public repository.

## Live And Private Data Safety

- Never request or persist OAuth files, API keys, service-account JSON, tokens, private keys, client secrets, credential paths, or credential contents.
- Require user authority for billing, organization policy, licenses, interactive authentication, access broadening, destructive asset changes, and unavailable local-to-cloud upload surfaces.
- For private raster ingestion, request only the minimum non-secret checkpoint needed to resume. Then continue task monitoring, asset-semantic checks, failed-subset retry, preflight, and downstream code without returning routine operations to the user.
- Never add `--force`, overwrite, deletion, public access, or broader IAM as a generic recovery step.
- Keep categorical rasters on reviewed class semantics: no bilinear interpolation of class codes, explicit no-data behavior, reviewed pyramiding, and declared whole-cell versus valid-area fraction denominators.

Read [references/knowledge_base/workflows/private-raster-ingestion-handoff.md](references/knowledge_base/workflows/private-raster-ingestion-handoff.md) for the private-ingestion state machine and [docs/tool_permissions.md](docs/tool_permissions.md) for tool and authority boundaries.

## Inputs And Outputs

Prefer editable `gee-plan/v0.3` YAML. Record the AOI, dates, dataset IDs, metric, cloud policy, reducer, scale, CRS, export target, validation rules, and claim limitations.

Persist each planned or executed run under `outputs/runs/<run_id>/`. The run directory should contain the plan, generated script, retrieval and validation evidence, applicable preflight or export-task records, environment metadata, and final report. See [docs/harness.md](docs/harness.md) for the artifact contract.

## Read On Demand

- Setup and command details: [docs/how_to_start.md](docs/how_to_start.md), [docs/cli_reference.md](docs/cli_reference.md), and [docs/troubleshooting.md](docs/troubleshooting.md).
- Recipes and readiness: [docs/recipes.md](docs/recipes.md), [docs/capability_matrix.md](docs/capability_matrix.md), and [docs/benchmark_protocol.md](docs/benchmark_protocol.md).
- Evidence and extension: [docs/kg_rag_architecture.md](docs/kg_rag_architecture.md), [docs/source_policy.md](docs/source_policy.md), and [docs/extending.md](docs/extending.md).
- Public examples and validation limits: [docs/demo_gallery.md](docs/demo_gallery.md) and [docs/remote_sensing_validation.md](docs/remote_sensing_validation.md).
