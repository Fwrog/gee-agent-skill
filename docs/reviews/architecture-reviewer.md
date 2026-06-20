# Architecture Review: Evaluation-Driven GEE Harness

Status: feasible, with live-export gating as the main release blocker.

## Boundary Review

- Keep the repository a Python package plus skill assets: `src/geeskill/` is runtime code, `assets/templates/` is code generation input, `references/knowledge_base/` is curated source material, `evals/` is benchmark input, and `outputs/` is generated evidence.
- Treat `build/`, `dist/`, egg-info, caches, and existing `outputs/` files as derived artifacts, not architecture source of truth.
- Do not broaden the upgrade into a generic GIS automation framework. The scope should remain Python-first and Earth-Engine-first: generated code should target the Earth Engine Python API, and research notes should inform retrieval and evaluation design without overriding official Earth Engine docs.

## Architecture Findings

- The current module split is clean enough to extend: `rag.py` handles retrieval, `templates.py` handles rendering and context validation, `validation.py` handles offline static checks, `earthengine.py` owns live API access, and `cli.py` wires commands.
- The current CLI and planner still hardcode command and template inference logic. The upgrade should add a separate registry for workflow templates, eval tasks, validators, exporters, and trace writers. Registry entries should declare inputs, outputs, side effects, required checks, and allowed live actions without importing Earth Engine at module import time.
- Current `run` behavior gates live execution on validation plus `--project`, but it still executes the target script with `runpy`. Since generated templates call `task.start()` inside `main()`, this is not enough for a dangerous live-export harness.
- Evaluation is currently present as task metadata and offline tests, but there is no first-class run trace tying prompt, retrieved sources, context, rendered script, validator output, dry-run result, and export task state into one immutable record.

## Required Run Trace Layout

Create one run directory per harness invocation under `outputs/runs/<timestamp>-<task-id>-<short-hash>/` with at least:

- `manifest.json`: package version, command argv, timestamp, task id, template id, registry versions, and file hashes.
- `inputs/task.yml` and `inputs/context.json`: exact task and render context used.
- `retrieval.json`: query, top-k results, scores, source paths, and source metadata.
- `plan.md`: cited plan emitted for the run.
- `rendered_script.py`: exact script under evaluation.
- `validation.json`: static validation findings.
- `dry_run.json`: execution-boundary result proving no live contact.
- `eval_report.json`: pass/fail checks, metrics, and blocking reasons.
- `live_export_request.json` and `export_tasks.json`: present only for approved live runs.
- `logs.txt`: concise operational log with secrets and credential paths redacted.

## Acceptance Criteria

- `gee-skill eval --task evals/tasks/<task>.yml --out outputs/runs/... --json` creates a complete run trace and exits nonzero on any blocking eval failure.
- Offline eval, planning, rendering, validation, and dry-run commands never import or initialize Earth Engine; tests should assert this boundary.
- Registry definitions are separated from CLI parsing and planner heuristics, are inspectable as data, and can be tested without live dependencies.
- Every eval report records source hashes for the task file, context file, template, retrieval index, and rendered script.
- Live export requires validation success, an explicit Google Cloud project, a persisted export request manifest, and a separate affirmative flag such as `--allow-live-export`.
- Generic `run` or `eval` commands must not start exports by default. Starting an export should be a distinct approved path that records task id, description, destination, state, and errors.
- Tests cover unit, combo, and theme-level checks: retrieval quality, context validation, template rendering, static validation, dry-run isolation, trace completeness, and blocked live export without approval.

## Key Risks

- `runpy` executes arbitrary Python, so static validation alone cannot prove side-effect safety. The harness should restrict live approval to generated or explicitly trusted scripts.
- Earth Engine exports create durable external side effects and can hit quota or cost-adjacent limits. Approval records must be auditable before any `task.start()`.
- Run traces can leak asset ids, local paths, project ids, or credentials if logging is not redacted.
- A broad registry can become a second framework inside the package. Keep it small, data-driven, and limited to Earth Engine research workflows.
- Eval tasks can overfit to current templates. Add negative fixtures and boundary cases, not only happy-path Hong Kong NDVI checks.
