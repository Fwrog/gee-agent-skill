# Harness Trace Model

The harness turns a workflow task into auditable files under `outputs/runs/<run_id>/`.

For v0.1 natural-language execution, `gee-skill ask` performs:

```text
natural-language request -> deterministic intent routing -> canonical task schema -> RAG retrieval -> plan -> template/script -> validation -> dry run or live preflight -> live export -> export monitor -> final report
```

The supported v0.1 intent is:

```text
Compute January 2024 mean NDVI for Hong Kong and export CSV.
```

Required trace files:

- `task.yaml`: exact task definition.
- `retrieval_trace.json`: selected evidence, source URLs, last-checked dates, evidence type, reason for selection, and influence.
- `plan.md`: cited workflow plan.
- `generated_script.py`: rendered Earth Engine Python script.
- `validation_report.json`: static and semantic findings.
- `dry_run_report.json`: proof that no Earth Engine contact occurred.
- `preflight_report.json`: live data probes for boundary, image availability, NDVI bands, and export decision when preflight runs.
- `live_run_report.json`: live execution result, only when live mode runs.
- `export_tasks.json`: task ids, descriptions, states, timestamps, and errors.
- `environment.json`: Python, platform, package version, and cwd.
- `final_report.md`: reader-facing summary.

The tool registry separates installed internal tools from CLI-exposed tools. Live export tools are marked dangerous and require explicit flags such as `--project` and `--confirm-live`.

Run:

```bash
gee-skill tools
```

## Interpreting Retrieval Trace

Each evidence record includes `evidence_type`, `source_url`, `last_checked`, `reason_for_selection`, and `influence`. Evidence types include dataset cards, operator syntax notes, operator relationship chains, workflow patterns, known failure cases, and general documentation chunks.

The coverage summary includes dataset cards, operator notes, workflow patterns, known failures, and export guidance counts. A v0.1 trace should include at least one of each before live export is considered auditable.
