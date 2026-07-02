# Rule Card: Validation Claim Boundaries

source_id: rule-validation-claim-boundaries
source_type: curated-rule-card
primary_status: curated
source_url: docs/remote_sensing_validation.md; references/knowledge_base/workflows/ndvi-demo-validation-ladder.md
last_checked: 2026-07-02
ruleset_id: validation_claim_boundary
risk_level: high

## Rule

Every validation demo, report, README section, and manifest must state what kind of evidence it provides and what it cannot support.

## Evidence Levels

| Evidence level | Supports | Must not claim |
| --- | --- | --- |
| Rendered script | Template and contract structure. | Live Earth Engine success. |
| Preflight passed | Basic AOI, dataset, band, and export checks. | Completed export or scientific validity. |
| Live task completed | Earth Engine accepted and completed a task. | Connector readback or analysis correctness. |
| Drive readback | Export handoff can be retrieved. | Metric validity without schema and range QA. |
| Product intercomparison | Cross-product workflow reasonableness under matched scale, time, and QA. | In-situ ground-truth accuracy. |
| Field/reference validation | Accuracy against independent reference observations. | General validity outside the reference scope. |

## Required Fields

Validation artifacts should include:

- claim boundary;
- dataset IDs and source URLs;
- AOI source and fallback status;
- date range and compositing windows;
- scale factors and QA masks;
- grid/projection matching method;
- export task ids and Drive artifact names;
- known limitations;
- status label such as `Partial` or `Golden`.

## Cannot Claim

- A smoke test is not full-year validation.
- A public boundary fallback is not an authoritative administrative result.
- A product-level check is not in-situ truth.
- A completed table export does not prove all raster exports completed.
