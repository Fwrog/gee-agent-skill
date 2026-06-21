# Core Guide: Quotas, Usage, and Debugging

source_id: core-quotas-usage-debugging
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/usage
last_checked: 2026-06-21
risk_level: medium

## Use

Earth Engine execution is quota-bound. Research harnesses should keep live smoke tests small, preflight before export, and monitor batch task states instead of assuming a submitted task succeeded.

## Operator Notes

- Inspect batch task state, description, timestamps, and error messages.
- Keep smoke tests to one AOI and one month when validating credentials/data flow.
- For large research workflows, split by date, region, or class and make task descriptions stable.
- Debug data availability before export: check AOI count, image count, band names, and tiny reducer statistics.

## Failure Cases

known_failure: QUOTA_OR_TIMEOUT

Quota and timeout failures are often retryable after reducing workload, coarsening scale, increasing `tileScale`, or waiting for queued tasks to finish.
