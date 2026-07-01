---
name: gee-agent-skill
description: Build traceable, auditable, evaluation-driven Google Earth Engine Python research workflows with local RAG evidence, Jinja2 templates, static and semantic validation, run traces, dry runs, live export gating, export monitoring, and benchmark tests for NDVI, LST, zonal statistics, and change detection.
---

# GEE Agent Skill

## Purpose

Use this skill for reproducible Google Earth Engine workflows that need a CLI-first, source-grounded, validated, traceable, and failure-aware path from user intent to plan, script, preflight, export, and run trace.

This is an agent-native GEE harness, not a GUI controller. Prefer `gee-skill` commands and the official Earth Engine Python API. Use Browser only for docs inspection, local previews, or visual QA. Use Google Drive for file handoff and readback. Use Data Analytics for report/chart/data-quality validation after data exists. Use Computer Use only when no CLI/API/plugin surface can complete the task, and follow action-time confirmation rules for risky UI actions.

## Standard Flow

0. Before setup or troubleshooting, confirm the user is in the repository root. Ask them to run `pwd`/`ls pyproject.toml` on macOS/Linux or `Get-Location`/`dir pyproject.toml` in Windows PowerShell when the directory is unclear.
1. Before telling users to install anything, tell them to `cd` into the repository checkout. Do not present `pip install -e ".[earthengine]"` as a standalone command from an unspecified directory.
2. Distinguish Windows PowerShell from macOS/Linux zsh or bash in every OS-specific instruction. PowerShell uses `$env:EE_PROJECT`; macOS/Linux shells use `export EE_PROJECT=...`.
3. Inspect capabilities and current public boundaries:
   `gee-skill info --json`, `gee-skill doctor --json`, `gee-skill recipe list --json`, `gee-skill rules list --json`, and `docs/capability_matrix.md`.
4. Create a reviewable plan from user intent:
   `gee-skill plan from-text "<request>" --json`.
5. If the request is underspecified, return the exact `AMBIGUOUS_TASK` missing fields to the user.
6. Choose recipes by registry evidence, not by model memory alone:
   `gee-skill recipe list --json`, then `gee-skill recipe show <recipe-id> --json`.
7. Retrieve distilled evidence:
   `gee-skill catalog recommend --task-type <type> --metric <metric> --json`, `gee-skill catalog evidence --category <dataset|operator|recipe|failure|research> --json`, and `gee-skill search-docs "<dataset operator failure query>" --json`.
   The plural category aliases (`datasets`, `operators`, `recipes`, `failures`) are accepted, but prefer the singular forms in new documentation.
8. Review or edit the saved plan before execution:
   `gee-skill plan review <plan.yaml> --json` and `gee-skill plan set <plan.yaml> <key> <value> --json`.
9. Resolve or summarize AOIs before live work when the AOI is unclear:
   `gee-skill aoi resolve "<request>" --json` or `gee-skill aoi summarize <geojson-or-plan> --json`.
10. Prefer plan, render, validate, and dry-run commands before live export.
11. Render and validate only approved templates or task YAML workflows:
   `gee-skill render <plan.yaml> --script-out <script.py> --json` and `gee-skill validate <script.py> --json`.
12. Run preflight before any live export:
   `gee-skill preflight <plan.yaml> --project <project-id> --json`.
13. If preflight returns `V03_CONTEXT_REVIEW_REQUIRED`, ask for or set reviewed AOI/export context in the plan; do not treat it as an auth problem and do not run export.
14. Execute live only with a project and explicit confirmation:
   `gee-skill run <plan.yaml> --project <project-id> --confirm-live --json`.
15. Monitor exports:
   `gee-skill exports list --project <project-id> --json`, `gee-skill exports watch --project <project-id> --task-id <id> --json`, or the compatibility command `gee-skill monitor-exports --project <project-id> --json`.
16. Inspect run trace artifacts before presenting results:
   `gee-skill trace inspect <run_id> --json`.
17. Use `gee-skill corpus coverage --task-type <type> --metric <metric> --output <format> --json` when checking whether a task has dataset, operator, recipe, failure, and export evidence coverage. Rule evidence may also appear in traces, but the core exportable-task coverage categories are dataset/operator/recipe/failure/export.
18. Use `gee-skill eval evals/benchmark_suite.yml --json` for offline benchmark evidence.
19. Treat `UNSAFE_GETINFO` and `PREFLIGHT_REQUIRED` as first-class safety categories when explaining validation/preflight failures.
20. Avoid overclaiming: say `live verified` only for workflows marked live export completed in `docs/capability_matrix.md`; say `render/validate verified`, `dry-run verified`, `mocked preflight blocked`, `planned`, or `experimental` for all other cases.
21. When a concrete task reveals a reusable lesson, classify it before editing public knowledge: dataset card, rule card, failure case, workflow card, or private-only note. Public cards must include source, `last_checked`, scope, limitations, and what they cannot claim.
22. For NDVI demo reasonableness, use a validation ladder rather than a single truth source: MODIS VI products for coarse temporal checks, Landsat for independent sensor checks, JRC water for all-surface interpretation, Dynamic World for time-matched strata, and ESA WorldCover for static class sanity.

## Golden Examples

These are verified regression paths, not the full scope of the project:

1. v0.1 HK Jan 2024 NDVI CSV:
   `gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json`.
2. v0.2 HK Jan 2024 land-cover-aware NDVI CSV:
   `gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json`.
More complex academic demos are intentionally not public golden examples. Keep them outside the repository and promote only generic lessons after privacy review.

## Do Not Use

- Do not use for non-Earth-Engine GIS work unless porting to Earth Engine.
- Do not use for destructive asset changes or bulk exports without quota and ownership review.
- Do not run live tasks without explicit user confirmation and a Google Cloud Project.
- Do not treat generated outputs as scientific conclusions without domain review and source validation.
- Do not ask users to paste credentials, tokens, service account JSON, refresh tokens, private keys, or credential file contents.
- Do not commit credentials, service account JSON, OAuth tokens, or credential paths.
- Do not tell users to commit local credential files.
- Do not copy third-party GitHub code into this repository as corpus material. Distill metadata, operator patterns, failure modes, and validation implications with attribution.

## User Setup Diagnostics

- If the user sees `file:///Users/<name> does not appear to be a Python project`, diagnose a wrong working directory first. Tell them to `cd /path/to/gee-agent-skill`, verify `pyproject.toml`, then install.
- If the user sees `command not found: earthengine`, diagnose inactive virtual environment or missing `.[earthengine]` install. Have them activate `.venv`, reinstall from the repo root, and run `which earthengine` or `where earthengine`.
- If the user sees `zsh: permission denied` after typing a folder path, explain that a directory path is not a shell command and they need `cd /path/to/gee-agent-skill`.
- If `import ee` works but `ee.Initialize(project=...)` says to run `earthengine authenticate`, explain that the package is installed but local OAuth credentials are missing. Have the user run `earthengine authenticate --auth_mode=localhost`, then `earthengine set_project "$EE_PROJECT"`, then verify that `ee.Number(1).getInfo()` prints `1`.
- If the user is on Windows, show PowerShell commands with backtick continuations and `$env:EE_PROJECT`.
- If the user is on macOS/Linux, show zsh/bash commands with backslash continuations and `export EE_PROJECT=...`.

## Inputs

Prefer task YAML with `id`, `task`, `template`, `query`, optional `outputs`, and `context`. Context should name AOI, dates, dataset id, metric, cloud policy, reducer, scale, CRS, and export target.

For v0.3 plans, prefer editable `gee-plan/v0.3` YAML with the fields documented in `schemas/gee-plan-v0.3.schema.json`. Recipe definitions come from `references/recipes/registry.yaml` with a packaged fallback under `src/geeskill/resources/recipes/`.

## Outputs

Every planned or executed workflow should write `outputs/runs/<run_id>/` with:

- `task.yaml`
- `task_plan.yaml` for compatibility commands that materialize reviewable task plans
- `retrieval_trace.json`
- `plan.md`
- `generated_script.py`
- `validation_report.json`
- `dry_run_report.json`
- `preflight_report.json` when live data preflight runs
- `landcover_diagnostics.json` when land-cover preflight runs
- `live_run_report.json` when live mode runs
- `export_tasks.json` when export tasks are inspected or created
- `environment.json`
- `final_report.md`

## Resource Map

- Read [docs/agent_goal.md](docs/agent_goal.md) for the reusable agent goal and tool boundaries.
- Read [docs/demo_gallery.md](docs/demo_gallery.md) for the current public golden examples and their claim boundaries.
- Read [docs/tool_permissions.md](docs/tool_permissions.md) for Browser, Google Drive, Data Analytics, Computer Use, and imagegen boundaries.
- Read [docs/closed_loop.md](docs/closed_loop.md) for the generic knowledge promotion workflow.
- Read [docs/remote_sensing_validation.md](docs/remote_sensing_validation.md) for public NDVI demo validation products and limits.
- Read [docs/harness.md](docs/harness.md) for run traces and tool registry behavior.
- Read [docs/live_smoke.md](docs/live_smoke.md) for private live smoke-test commands.
- Read [docs/how_to_start.md](docs/how_to_start.md) for the recommended user path.
- Read [docs/cli_reference.md](docs/cli_reference.md) for canonical commands and compatibility aliases.
- Read [docs/recipes.md](docs/recipes.md) for recipe readiness levels and registered workflow families.
- Read [docs/capability_matrix.md](docs/capability_matrix.md) before claiming a workflow is implemented, preflight-ready, or live-verified.
- Read [docs/benchmark_protocol.md](docs/benchmark_protocol.md) before making evaluation claims.
- Read [docs/research_positioning.md](docs/research_positioning.md) before writing portfolio or paper-facing summaries.
- Read [docs/release_readiness.md](docs/release_readiness.md) for the current publishability checklist, homepage asset inventory, and remaining limitations.
- Read [docs/concepts.md](docs/concepts.md) for plan-first, RAG, preflight, and trace concepts.
- Read [docs/v01_hk_january_ndvi.md](docs/v01_hk_january_ndvi.md) for the v0.1 release target.
- Read [docs/v02_landcover_aware_ndvi.md](docs/v02_landcover_aware_ndvi.md) for the v0.2 land-cover-aware workflow.
- Read [docs/troubleshooting.md](docs/troubleshooting.md) for common failures and boundary mismatch guidance.
- Read [docs/error_taxonomy.md](docs/error_taxonomy.md) for failure categories and recovery hints.
- Read [docs/extending.md](docs/extending.md) before adding workflow recipes, dataset cards, or semantic validators.
- Use `references/knowledge_base/` as the retrieval corpus; official Google docs are canonical, research notes are design guidance.
- Use `references/corpus/github_gee_seed_repos.yml` as the 30-50 reviewed seed inventory for pattern-only corpus expansion.
- Use `references/corpus/github_gee_discovery_100.yml` as the 100+ metadata-only discovery queue.
- Use `scripts/discover_gee_repos.py` for broad GitHub metadata refreshes and `scripts/analyze_gee_corpus.py` for local read-only style exams.

## Quality Rules

- Keep `SKILL.md` concise and below 500 lines.
- Use progressive disclosure; put detailed guidance in docs and references.
- Keep one responsibility: traceable Earth Engine Python research workflows.
- Avoid OS-specific paths in generated scripts and docs where possible.
- Avoid time-sensitive claims unless the source and retrieval date are recorded.
