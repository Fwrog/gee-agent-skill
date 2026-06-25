# Codex Transcript Example

Last updated: 2026-06-25

This sanitized transcript shows how a coding agent should operate `gee-agent-skill`. It is not a promise that every natural-language task can run live. The agent keeps state explicit, reviews evidence, asks for missing fields, and only submits live exports after user confirmation.

## Transcript

**User**

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

**Codex**

```text
I will use the GEE skill as a CLI harness. I will inspect the operating rules, then create a plan, validate it, run preflight, and only export if you confirm live execution.
```

**Codex inspects the skill**

```bash
sed -n '1,220p' SKILL.md
```

Codex notes:

- start from the repository root;
- use JSON commands for agent state;
- retrieve catalog and recipe evidence;
- prefer plan/render/validate before live execution;
- require `--confirm-live` for export;
- do not ask for credentials or print credential paths.

**Codex inspects the harness**

```bash
gee-skill info --json
```

Relevant output:

```json
{
  "ok": true,
  "data": {
    "identity": "agent-native Google Earth Engine CLI harness",
    "commands": {
      "catalog": ["search", "show", "recommend", "evidence"],
      "recipe": ["list", "show"],
      "plan": ["from-text", "from-yaml", "review", "set"],
      "preflight": ["plan"],
      "run": ["script", "plan"],
      "exports": ["list", "watch"],
      "trace": ["list", "inspect"]
    }
  }
}
```

**Codex inspects recipes**

```bash
gee-skill recipe list --json
```

Codex identifies the vegetation-index family and the Hong Kong 16-day NDVI golden example path. For a non-golden request, Codex would stop at the capability level recorded in `docs/capability_matrix.md`.

**Codex retrieves evidence**

```bash
gee-skill catalog evidence --category dataset --json
gee-skill catalog evidence --category operator --json
gee-skill catalog evidence --category failure --json
```

Relevant evidence:

- Sentinel-2 SR Harmonized has the bands needed for NDVI;
- cloud/shadow masking and explicit scale are required;
- unsafe `getInfo()` and missing preflight are known failure classes;
- export workflows need task monitoring rather than assuming Drive output exists immediately.

**Codex creates a plan**

```bash
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json
```

Relevant output:

```json
{
  "ok": true,
  "data": {
    "plan": {
      "schema_version": "gee-plan/v0.3",
      "task_type": "vegetation_index",
      "intent": {
        "metric": "NDVI",
        "recipe_id": "vegetation-index-ndvi",
        "golden_example": true
      },
      "aoi": {"name": "Hong Kong"},
      "time_range": {"date_start": "2024-01-01", "date_end": "2025-01-01"},
      "execution": {
        "template": "hk_2024_16day_ndvi_csv",
        "template_ready": true,
        "live_adapter_ready": true
      }
    }
  }
}
```

**Codex reviews missing fields**

For this golden example, the required AOI, date range, metric, cadence, dataset, template, export selectors, Drive folder, and file prefix are present. If a request were incomplete, Codex would report the `AMBIGUOUS_TASK` fields instead of fabricating an AOI or time range.

Example missing-field command:

```bash
gee-skill plan from-text "Compute NDWI in March 2024 and export GeoTIFF." --json
```

Expected behavior:

```json
{
  "ok": false,
  "error": {
    "code": "AMBIGUOUS_TASK",
    "message": "The task is underspecified.",
    "hint": "Ask for the missing fields before rendering or running."
  },
  "data": {
    "missing_fields": ["aoi"]
  }
}
```

**Codex renders and validates**

```bash
gee-skill render outputs/plans/hk_2024_16day_ndvi.yaml \
  --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py \
  --json

gee-skill validate outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

Codex checks that validation passes before asking about live execution.

**Codex asks for live confirmation**

```text
Preflight will contact Earth Engine but will not submit an export.
Export requires your project id and explicit confirmation. Should I run live preflight now?
```

**User**

```text
Yes, use my authenticated environment and EE_PROJECT. Do not submit export until preflight passes.
```

**Codex runs preflight**

```bash
gee-skill preflight outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --json
```

Preflight checks authentication/project initialization, AOI loading, image counts, required bands, and small sanity statistics. It must not start an export.

**Codex asks before export**

```text
Preflight passed. I can submit exactly one export with --confirm-live. Confirm?
```

**User**

```text
Confirmed. Submit one export.
```

**Codex submits only with the explicit gate**

```bash
gee-skill run outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --run-id hk-2024-16day-ndvi-v03-live-export-check \
  --json
```

Sanitized output:

```json
{
  "ok": true,
  "data": {
    "submitted": true,
    "export_description": "hk_2024_16day_ndvi",
    "drive_folder": "gee_exports",
    "file_prefix": "hk_2024_16day_ndvi",
    "task_id": "[REDACTED_TASK_ID]"
  }
}
```

**Codex monitors exports**

```bash
gee-skill exports list --project "$EE_PROJECT" --json
```

Sanitized output:

```json
{
  "ok": true,
  "data": {
    "tasks": [
      {
        "id": "[REDACTED_TASK_ID]",
        "description": "hk_2024_16day_ndvi",
        "state": "COMPLETED"
      }
    ]
  }
}
```

**Codex inspects trace**

```bash
gee-skill trace inspect hk-2024-16day-ndvi-v03-live-export-check --json
```

Codex verifies the trace contains plan, script, validation report, preflight report, export task metadata, and environment summary without credentials, OAuth tokens, service account JSON, refresh tokens, private keys, or credential paths.

**Codex summarizes without overclaiming**

```text
This was a v0.3 golden workflow. Plan/render/validate passed, live preflight passed, one confirmed export was submitted, and the Earth Engine task reached COMPLETED. The CSV is workflow evidence for the harness. It should not be interpreted as a final vegetation science result without domain review, because the AOI includes water and dense built-up surfaces and no independent validation was performed.
```
