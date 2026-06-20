# Live Smoke Test Protocol

The canonical live smoke test is intentionally small:

```text
Compute January 2024 NDVI mean for one Hong Kong district and create a CSV export task.
```

Prerequisites:

- Register for Earth Engine.
- Configure a Google Cloud Project with Earth Engine API access.
- Authenticate locally.
- Install live dependencies.

```bash
pip install -e ".[earthengine]"
earthengine authenticate
gee-skill live-smoke-test \
  --project your-google-cloud-project \
  --confirm-live \
  --smoke-month 1 \
  --smoke-region "Central and Western" \
  --export-folder gee_exports
```

The command writes a run trace. If live access is missing, it fails with structured `AUTH_ERROR` or `PROJECT_ERROR` guidance and does not require credentials in the repository.

Monitor tasks:

```bash
gee-skill monitor-exports --project your-google-cloud-project --json
```

