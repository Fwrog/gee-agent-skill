---
name: gee-agent-skill
description: Build traceable, auditable, evaluation-driven Google Earth Engine Python research workflows with local RAG evidence, Jinja2 templates, static and semantic validation, run traces, dry runs, live export gating, export monitoring, and benchmark tests for NDVI, LST, zonal statistics, and change detection.
---

# GEE Agent Skill

## Purpose

Use this skill for reproducible Google Earth Engine Python workflows that must be source-grounded, validated, traceable, and failure-aware. Keep the scope Python-first and Earth-Engine-first.

## Use

1. Search local evidence: `gee-skill search-docs "<query>"`.
2. Plan from task YAML: `gee-skill plan examples/hk_2024_monthly_ndvi/task.yaml`.
3. Inspect `outputs/runs/<run_id>/retrieval_trace.json`, `plan.md`, and `generated_script.py`.
4. Validate: `gee-skill validate outputs/scripts/hk_2024_monthly_ndvi.py --json`.
5. Dry-run: `gee-skill run outputs/scripts/hk_2024_monthly_ndvi.py --dry-run --json`.
6. Use live mode only with user-owned credentials, `--project`, and `--confirm-live`.
7. Monitor exports: `gee-skill monitor-exports --project <project-id> --json`.

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
- `live_run_report.json` when live mode runs
- `export_tasks.json` when export tasks are inspected or created
- `environment.json`
- `final_report.md`

## Resource Map

- Read [docs/harness.md](docs/harness.md) for run traces and tool registry behavior.
- Read [docs/live_smoke.md](docs/live_smoke.md) for private live smoke-test commands.
- Read [docs/error_taxonomy.md](docs/error_taxonomy.md) for failure categories and recovery hints.
- Read [docs/extending.md](docs/extending.md) before adding workflow recipes, dataset cards, or semantic validators.
- Use `references/knowledge_base/` as the retrieval corpus; official Google docs are canonical, research notes are design guidance.

## Quality Rules

- Keep `SKILL.md` concise and below 500 lines.
- Use progressive disclosure; put detailed guidance in docs and references.
- Keep one responsibility: traceable Earth Engine Python research workflows.
- Avoid OS-specific paths in generated scripts and docs where possible.
- Avoid time-sensitive claims unless the source and retrieval date are recorded.
