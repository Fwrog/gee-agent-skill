# Runtime Engineer Review: Live Smoke And Export Monitoring

Status: gated, but not yet release-ready for a live smoke protocol.

## Confirmed

- `live-smoke-test` exposes the required explicit flags: `--project`, `--confirm-live`, `--smoke-month`, `--smoke-region`, and `--export-folder` (`src/geeskill/cli.py:304`, `src/geeskill/cli.py:432`).
- Generic live `run` requires both `--project` and `--confirm-live` before Earth Engine execution (`src/geeskill/cli.py:229`, `src/geeskill/tool_registry.py:32`).
- Live smoke traces are designed to write task input, retrieval trace, rendered script, validation, dry-run report, live report, final report, and `export_tasks.json` when control reaches the post-run trace block (`src/geeskill/cli.py:322`, `src/geeskill/cli.py:339`).
- No committed credential payload was found in the scanned source/config/docs set. `.gitignore` excludes common Google/Earth Engine credential files and local config folders, and validation rejects credential-looking script material (`.gitignore:11`, `src/geeskill/validation.py:50`).

## Blocking Requirements

1. Catch and normalize `SystemExit` from generated scripts before monitoring exports. `execute_script()` runs scripts as `__main__`, while generated export templates end with `raise SystemExit(main())`; a successful `task.start()` can exit before `monitor_tasks()` and before writing `live_run_report.json` or `export_tasks.json` (`src/geeskill/earthengine.py:40`, `src/geeskill/resources/templates/hk_district_january_ndvi_smoke.py.j2:123`).
2. Fix `AUTH_ERROR` and `PROJECT_ERROR` classification precedence. `initialize()` wraps all init failures with a hint containing project text, and `classify_exception()` checks `project` before credential/auth terms, so missing or expired credentials can be mislabeled as `PROJECT_ERROR` (`src/geeskill/earthengine.py:31`, `src/geeskill/errors.py:106`).
3. Persist explicit export request metadata beside task status. `_task_summary()` records id, description, state, timestamps, and error, but not project, destination folder, file prefix, smoke month, smoke region, or requested export description; `export_tasks.json` should tie external task ids back to the live smoke request (`src/geeskill/cli.py:263`, `src/geeskill/cli.py:317`).
4. Make export monitoring traces complete enough for audit. `monitor-exports --run-id` currently writes `export_tasks.json`, but should also record command inputs such as project, timeout, poll interval, authentication mode, and a final monitor report (`src/geeskill/cli.py:274`).
5. Add regression coverage for live runtime boundaries: missing `--confirm-live`, mocked `AUTH_ERROR`, mocked `PROJECT_ERROR`, successful generated-script exit followed by monitoring, and export metadata persistence.

## Documentation Cleanup

- README live examples still show `gee-skill run ... --project <project-id>` without `--confirm-live`, which conflicts with the runtime gate and will fail for a real live run (`README.md:35`, `README.md:68`).
