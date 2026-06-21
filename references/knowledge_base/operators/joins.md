# Operator Notes: Joins and Temporal Pairing

source_id: operator-joins-temporal-pairing
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/joins_intro
last_checked: 2026-06-21
method_name: ee.Join.saveFirst, ee.Join.saveAll, ee.Filter.maxDifference
operator_chain: prepare collections -> add time properties -> join -> map paired images -> validate paired band availability
risk_level: medium

## Syntax Notes

Earth Engine joins pair images or features based on filters. Temporal pairing is useful for matching optical observations to cloud probability, land-cover observations, weather covariates, or before/after change windows.

## Workflow Notes

- Confirm join keys and time windows explicitly.
- After a join, validate that the paired object exists before selecting bands.
- Use joins for pairing collections; do not fetch collection contents client-side to match timestamps.

## Failure Cases

known_failure: MISSING_JOIN_MATCH

Pairing failures can cause missing bands or null properties. Recovery: widen the time tolerance, inspect date coverage, or add explicit guards.
