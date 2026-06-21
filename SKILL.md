---
name: gee-agent-skill
description: Build traceable, auditable, evaluation-driven Google Earth Engine Python research workflows with local RAG evidence, Jinja2 templates, static and semantic validation, run traces, dry runs, live export gating, export monitoring, and benchmark tests for NDVI, LST, zonal statistics, and change detection.
---

# GEE Agent Skill

## Purpose

Use this skill for reproducible Google Earth Engine Python workflows that must be source-grounded, validated, traceable, and failure-aware. Keep the scope Python-first and Earth-Engine-first.

## Use

1. For the supported v0.1 natural-language workflow, run:
   `gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json`.
2. For live v0.1, first preflight:
   `gee-skill preflight-hk-ndvi --project <project-id> --year 2024 --month 1 --scope hong-kong --json`.
3. Only after validation and preflight pass, run:
   `gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --project <project-id> --confirm-live --run-id hk-2024-01-ndvi-v01 --json`.
4. Monitor exports: `gee-skill monitor-exports --project <project-id> --json`.
5. For template-driven workflows, search evidence, plan from task YAML, validate, then dry-run or live-run with explicit flags.

## Do Not Use

- Do not use for non-Earth-Engine GIS work unless porting to Earth Engine.
- Do not use for destructive asset changes or bulk exports without quota and ownership review.
- Do not run live tasks without explicit user confirmation and a Google Cloud Project.
- Do not treat generated outputs as scientific conclusions without domain review and source validation.
- Do not commit credentials, service account JSON, OAuth tokens, or credential paths.

## Inputs

Prefer task YAML with `id`, `task`, `template`, `query`, optional `outputs`, and `context`. Context should name AOI, dates, dataset id, metric, cloud policy, reducer, scale, CRS, and export target.

## Outputs

Every planned or executed workflow should write `outputs/runs/<run_id>/` with:

- `task.yaml`
- `retrieval_trace.json`
- `plan.md`
- `generated_script.py`
- `validation_report.json`
- `dry_run_report.json`
- `preflight_report.json` when live data preflight runs
- `live_run_report.json` when live mode runs
- `export_tasks.json` when export tasks are inspected or created
- `environment.json`
- `final_report.md`

## Resource Map

- Read [docs/harness.md](docs/harness.md) for run traces and tool registry behavior.
- Read [docs/live_smoke.md](docs/live_smoke.md) for private live smoke-test commands.
- Read [docs/v01_hk_january_ndvi.md](docs/v01_hk_january_ndvi.md) for the v0.1 release target.
- Read [docs/error_taxonomy.md](docs/error_taxonomy.md) for failure categories and recovery hints.
- Read [docs/extending.md](docs/extending.md) before adding workflow recipes, dataset cards, or semantic validators.
- Use `references/knowledge_base/` as the retrieval corpus; official Google docs are canonical, research notes are design guidance.

## Quality Rules

- Keep `SKILL.md` concise and below 500 lines.
- Use progressive disclosure; put detailed guidance in docs and references.
- Keep one responsibility: traceable Earth Engine Python research workflows.
- Avoid OS-specific paths in generated scripts and docs where possible.
- Avoid time-sensitive claims unless the source and retrieval date are recorded.
