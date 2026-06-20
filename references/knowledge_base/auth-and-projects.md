# Authentication And Projects

source_id: google-ee-auth
source_type: official-guide
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/guides/auth
retrieved_at: 2026-06-21
primary_status: canonical
risk_level: low

## Core Guidance

Earth Engine Python scripts require authentication and initialization before live API requests. A user must have Earth Engine access and a Google Cloud Project with the Earth Engine API enabled.

Use local authentication outside generated workflow scripts:

```python
import ee
ee.Authenticate()
ee.Initialize(project="my-project")
```

The CLI should initialize Earth Engine only for live commands such as `run` and `monitor-exports`. Offline commands such as retrieval, planning, rendering, validation, and smoke tests must not require credentials.

## Failure Hints

- If initialization fails, ask the user to confirm Earth Engine registration, API enablement, IAM access, and project id.
- Never commit credentials, service account JSON, tokens, or local credential paths.
- Prefer explicit `project` initialization for reproducible execution.

