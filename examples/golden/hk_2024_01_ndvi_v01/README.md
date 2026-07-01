# Golden Evidence: HK Jan 2024 NDVI CSV v0.1

This directory contains sanitized golden example artifacts for the v0.1 Hong Kong January 2024 NDVI CSV workflow.

The artifacts are evidence that the harness can route a small natural-language Earth Engine task through plan, validation, preflight, confirmed export, and task monitoring. They are not a scientific vegetation assessment.

## Contents

| File | Purpose |
| --- | --- |
| `task.yaml` | Source task definition used by the compatibility workflow. |
| `task_plan.redacted.yaml` | Reviewable task plan with project IDs and local paths redacted. |
| `validation_report.json` | Static validation summary for the rendered script. |
| `preflight_report.redacted.json` | Sanitized Earth Engine preflight summary. |
| `export_tasks.redacted.json` | Sanitized export task metadata. |
| `trace_summary.md` | Human-readable trace summary and limitations. |

No credentials, OAuth tokens, service account JSON, refresh tokens, private keys, Google account identifiers, or local credential paths are included.

No CSV sample is included here because the public evidence bundle keeps v0.1 lightweight and avoids inventing values. More complex academic demos are not published as reader-facing output examples.
