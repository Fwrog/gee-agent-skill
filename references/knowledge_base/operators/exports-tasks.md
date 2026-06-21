# Operator Notes: Exports and Batch Tasks

source_id: operator-exports-tasks
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/exporting_tables
last_checked: 2026-06-21
method_name: Export.table.toDrive, ee.batch.Export.table.toDrive, Task.start, Task.status
operator_chain: validate -> preflight -> create export task -> start -> monitor state -> inspect error_message
risk_level: medium

## Syntax Notes

For CSV table exports, use `ee.batch.Export.table.toDrive(collection=..., description=..., folder=..., fileNamePrefix=..., fileFormat="CSV", selectors=[...])`.

## Workflow Notes

- Use stable export descriptions and file prefixes.
- Specify `selectors` to make the schema reproducible.
- Do not treat task submission as scientific success; monitor task state.
- Store task id, description, state, timestamps, and error message in the run trace.

## Failure Cases

known_failure: EXPORT_TASK_ERROR

Common causes include invalid destination, unsupported schema, huge geometry, reducer nulls, missing bands, or quota limits.
