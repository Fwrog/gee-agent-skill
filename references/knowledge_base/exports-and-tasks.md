# Exports And Tasks

source_id: google-ee-export-table
source_type: official-api
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/apidocs/export-table-todrive
retrieved_at: 2026-06-21
primary_status: canonical
risk_level: low

## Export Tables

Use `ee.batch.Export.table.toDrive` for CSV or vector table exports from Python. Provide a stable `description`, destination folder or bucket, file name prefix, file format, and selectors when column order matters.

For image exports, include `region`, `scale` or `crsTransform`, optional `crs`, and `maxPixels` when the output can exceed default limits.

## Task Monitoring

Export calls create tasks. Scripts should call `task.start()` only after validation and initialization. Monitoring should surface task id, state, description, destination, and error message. Polling loops must have a timeout.

