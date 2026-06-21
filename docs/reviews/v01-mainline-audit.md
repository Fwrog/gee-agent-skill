# v0.1 Mainline Repository Audit

Date: 2026-06-21

Scope: inspect the current `gee-agent-skill` repository before adding the v0.1 natural-language workflow path.

## Current Repository Shape

- CLI entry point: `gee-skill` from `src/geeskill/cli.py`.
- Current exposed commands: `tools`, `search-docs`, `plan`, `validate`, `smoke-test`, `run`, `monitor-exports`, `preflight-hk-ndvi`, `live-smoke-test`, and `evaluate`.
- Core modules: RAG/indexing, Jinja2 template rendering, static and semantic validation, run traces, live Earth Engine execution, task monitoring, error taxonomy, and Hong Kong NDVI preflight.
- Templates include Sentinel-2 NDVI, Landsat LST, Sentinel-1 flood/change, generic zonal statistics, and Hong Kong NDVI smoke/monthly workflows.
- Curated resources include knowledge base markdown, generated RAG index, task YAML examples, packaged templates, and a local Hong Kong 18-district GeoJSON boundary.
- Tests cover RAG retrieval, template rendering, validation, semantic checks, execution boundaries, live boundary behavior, export monitoring traces, and Hong Kong NDVI preflight mocks.

## Confirmed Working Paths

- Editable install and project-local Python environment have been used successfully.
- `gee-skill tools` exposes the tool registry and separates installed from exposed tools.
- `gee-skill smoke-test --json` renders and validates the Hong Kong NDVI template offline.
- `gee-skill plan examples/hk_2024_monthly_ndvi/task.yaml --run-id local-audit-plan` writes a full run trace.
- `gee-skill validate outputs/scripts/hk_2024_monthly_ndvi.py --json` passes.
- `gee-skill run outputs/scripts/hk_2024_monthly_ndvi.py --dry-run --json` passes without Earth Engine contact.
- Optional live dependency installation and Earth Engine OAuth/project initialization have been verified by the user.
- `gee-skill preflight-hk-ndvi --project <verified-project> --year 2024 --month 1 --district "Central and Western" --json` passed after the boundary fix.
- `gee-skill live-smoke-test --project <verified-project> --confirm-live --smoke-month 1 --smoke-region "Central and Western" --export-folder gee_exports --run-id live-smoke-hk-2024-01-v2` created a task that later reached `COMPLETED`.

## Confirmed Failure And Diagnosis

Earlier live smoke submitted a task that failed with:

```text
Image.reduceRegions: Image has no bands.
```

This was not an authentication failure. It occurred after a live task was submitted. Live probing showed `FAO/GAUL/2015/level2` is unsuitable for Hong Kong district filtering because it exposes one Hong Kong feature with `ADM2_NAME = Administrative unit not available`; the requested district matched zero features. The current district smoke path now uses the curated Hong Kong district GeoJSON and preflight blocks doomed exports before `task.start()`.

## v0.1 Gap

The repository still lacks the requested v0.1 mainline product path:

- No `gee-skill ask` command.
- No deterministic natural-language router.
- No canonical v0.1 whole-Hong-Kong January 2024 NDVI CSV task.
- The live preflight command currently requires a district and does not expose `--scope hong-kong`.
- The current live smoke path is district-oriented; v0.1 should be whole-Hong-Kong, one month, one small CSV.
- RAG/docs/tests do not yet prove the natural-language request -> traceable plan -> validated script -> preflight -> live export path.

## Recommended Next Step

Add a narrow v0.1 path without redesigning the CLI:

1. Introduce a deterministic `ask` command for supported Hong Kong January 2024 NDVI CSV requests.
2. Add a whole-Hong-Kong v0.1 task schema and template using the curated boundary union as AOI.
3. Extend `preflight-hk-ndvi` with `--scope hong-kong` so district name is optional for v0.1.
4. Require preflight before live export in `ask --confirm-live`.
5. Add mocked tests and a final v0.1 audit report.
