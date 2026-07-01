# Tool Permissions

`gee-agent-skill` is API-first. Extra tools are useful, but they should not replace the Earth Engine Python API or the local CLI when those paths can complete the task.

## Permission Matrix

| Tool or permission | Useful for | Default posture | Boundary |
| --- | --- | --- | --- |
| Earth Engine Python API / `gee-skill` CLI | Planning, rendering, validation, preflight, export, task monitoring, traces | Primary path | Requires user-owned Earth Engine account, Google Cloud Project, local OAuth, and explicit `--confirm-live` for exports. |
| Browser | Official docs lookup, dataset catalog verification, rendered README/docs preview, visual QA | Use for verification | Do not use browser automation to submit exports when the API can do it. |
| Google Drive | Reading back export handoff files, sharing zip/report/CSV/figure outputs, checking uploaded artifacts | Use for file lifecycle | Use connector-returned links only; never synthesize Drive URLs. |
| Data Analytics | Chart/report QA, data-quality checks, KPI-style evidence review, dashboard/report handoff | Use after data exists | It validates presentation and evidence quality; it does not replace remote-sensing domain review. |
| Computer Use | Local GUI actions when no CLI/API/plugin path exists | Last resort | Avoid for credentials, destructive UI actions, or live export submission when API/CLI is available. |
| imagegen | README hero images and explanatory raster visuals | Optional visual polish | Generated images are communication assets, not scientific evidence. |

## Recommended Tool Order

1. Use `gee-skill` and the Earth Engine Python API for all GEE execution.
2. Use Browser to verify current dataset/API facts from official sources.
3. Use local validation and tests before live export.
4. Use Google Drive only for file handoff and readback.
5. Use Data Analytics only after a table, chart, or report exists.
6. Use Computer Use only when the system has no safer programmatic surface.

## Security Rules

- Never paste or commit OAuth tokens, service account JSON, private keys, credential paths, or refresh tokens.
- Live exports require both a project id and `--confirm-live`.
- Browser and Computer Use permissions should not silently broaden execution authority.
- Public docs should describe tool boundaries generically and should not include private project names, unpublished findings, or private asset ids.
