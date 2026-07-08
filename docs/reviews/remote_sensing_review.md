# Remote Sensing Review

Date: 2026-07-09

Finding: pass with conservative scope.

The v0.4 KG-RAG layer treats official Earth Engine documentation and Data Catalog entries as authoritative for dataset ids, bands, QA fields, scale factors, projections, API behavior, quota/export behavior, and current availability. HLS/MODIS product intercomparison is framed as product-level consistency only, not in-situ ground-truth validation.

Checks covered:

- MODIS vegetation index evidence includes the 0.0001 scale factor and SummaryQA/DetailedQA requirement.
- HLS evidence includes Fmask policy requirements.
- Fine/coarse comparison retrieves and validates an aggregation-before-comparison rule.
- `reduceResolution` evidence is paired with projection/default projection handling.
- Claim-boundary evidence states that product agreement cannot support ground-truth accuracy without independent reference evidence.

Residual risk: temporal matching, mixed-pixel interpretation, BRDF/phenology effects, and sensor/product lineage remain workflow-specific scientific review items.
