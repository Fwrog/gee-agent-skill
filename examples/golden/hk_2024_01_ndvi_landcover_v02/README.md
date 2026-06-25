# Golden Evidence: HK Jan 2024 Land-Cover-Aware NDVI CSV v0.2

This directory contains sanitized golden example artifacts for the v0.2 Hong Kong January 2024 land-cover-aware NDVI CSV workflow.

The artifacts show that the harness can combine a primary optical index workflow with land-cover interpretation strata, validation, preflight, confirmed export, and task monitoring. They are not a claim that Dynamic World classes are perfect or policy-ready for Hong Kong vegetation assessment.

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

No CSV sample is included here because the public evidence bundle keeps v0.2 lightweight and avoids implying that land-cover-stratified values are final scientific findings.
