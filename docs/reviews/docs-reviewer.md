# Docs Reviewer: Traceable GEE Harness

Status: docs are close, but the release path still needs sharper operator guidance before this feels self-serve.

## Findings

1. Credential guidance is directionally correct but should be more operational. README states the Earth Engine account, project, and auth requirements, and warns against committing secrets (`README.md:34`, `README.md:43`), while live smoke docs list `earthengine authenticate` (`docs/live_smoke.md:18`). Add a short "credential-safe workflow" note that says credentials stay in local Earth Engine auth only, task YAML/context/generated scripts/run traces must not contain credential paths, and `--authenticate` is available when the CLI should initialize auth during live commands.

2. Run trace interpretation is too thin. README and `docs/harness.md` list trace files (`README.md:61`, `docs/harness.md:5`), but only retrieval trace gets interpretation guidance (`docs/harness.md:26`). Add a compact reading checklist: `retrieval_trace.coverage`, `validation_report.ok` and `semantic_rulesets`, `dry_run_report.contacted_earth_engine == false`, `live_run_report.ok` or `error.category`, `export_tasks[].state/error_message`, and `final_report.md` as the reader summary.

3. Live smoke commands are runnable but should show the full safe sequence. `docs/live_smoke.md:9` through `docs/live_smoke.md:27` jumps from prerequisites into live export. Add the expected preflight order: install extras, authenticate, run `gee-skill smoke-test --json`, run `gee-skill live-smoke-test ... --confirm-live`, then monitor with `gee-skill monitor-exports --project ... --json`. Include what success and graceful failure look like in JSON, especially the `run_trace` path and `AUTH_ERROR` / `PROJECT_ERROR` categories.

4. Extension docs need contracts, not just steps. `docs/extending.md` has the right sections for recipes, dataset cards, and validators, but the recipe and validator steps are checklist-only (`docs/extending.md:3`, `docs/extending.md:22`). Add small schemas for task YAML/context fields, required trace outputs for a new recipe, dataset-card metadata expectations after index rebuild, and the validator `Finding` fields that must survive `gee-skill validate --json`.

5. Keep `SKILL.md` concise. It already delegates details to docs and references (`SKILL.md:49`, `SKILL.md:59`). Do not move long live-smoke examples, dataset-card templates, or validator schemas into `SKILL.md`; add one pointer to the new trace-interpretation checklist if needed.

## Suggested Next Docs Patch

- Add "Credential-safe live workflow" to README and `docs/live_smoke.md`.
- Expand `docs/harness.md` with "How to read a run trace".
- Expand `docs/extending.md` with mini contracts for recipe, dataset card, and semantic validator additions.
