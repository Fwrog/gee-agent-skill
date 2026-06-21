# Contributing

## Scope

This repository is a Python-first Google Earth Engine research harness. Keep changes focused on traceable planning, retrieval evidence, templates, validation, preflight checks, export monitoring, tests, and documentation.

Do not add credentials, local credential paths, unrelated protocol layers, or unreviewed live-export behavior.

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

Add a template, context, example task, retrieval docs, semantic validator when needed, and offline regression tests. Update docs only with behavior that is implemented and tested.
