# Contributing

## Scope

This repository is a Python-first Google Earth Engine research harness. Keep changes focused on traceable planning, retrieval evidence, templates, validation, preflight checks, export monitoring, tests, and documentation.

Do not add credentials, local credential paths, unrelated protocol layers, or unreviewed live-export behavior.

## Capability Boundary

Treat the Hong Kong NDVI workflows as golden examples and regression evidence for the general harness, not as the full product scope.

- HK NDVI golden examples have live-verification evidence.
- Non-golden recipes may be plan/render/validate-ready and may have generic preflight gates, but do not claim live export support unless recipe-specific checks and live evidence exist.
- Preflight readiness is not export submission. Only a confirmed `--confirm-live` run and monitored Earth Engine task prove live export behavior.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts\ingest_docs.py
python -m pytest
```

Live tests are optional and must require explicit `--project` and `--confirm-live` flags.

## Adding Workflows

Add a template, context, example task, retrieval docs, semantic validator when needed, and offline regression tests. For live support, add the adapter, preflight checks, explicit run gate, mocked tests, and traceable live verification. Update docs only with behavior that is implemented and tested.

## Pull Requests

Keep PRs focused. Include the commands you ran, whether live Earth Engine was used, and which outputs or run traces support the claim. Never include OAuth tokens, service account JSON, private keys, Google project secrets, or local credential paths.
