# RAG Engineer Review: Operator-Aware Retrieval Trace

## Summary

The local markdown index already has useful source metadata in the curated notes: dataset cards include `source_id`, `source_type`, `url`, `retrieved_at`, `primary_status`, `dataset_id`, and `risk_level`, while the operator research note names syntax, relationship frequency, frequent patterns, and relationship chains. The missing layer is an auditable retrieval trace that explains why each chunk was selected and how it supports a workflow plan.

Recommendation: keep the current markdown-first corpus, but add a normalized trace envelope around retrieved chunks. The trace should preserve source authority, expose operator and dataset matches, record time-sensitive provenance, and make non-canonical research notes visibly subordinate to official API and Data Catalog sources.

## Proposed Trace Fields

Each retrieved item should expose:

```json
{
  "chunk_id": "datasets/sentinel-2-sr-harmonized.md#001",
  "source_path": "datasets/sentinel-2-sr-harmonized.md",
  "title": "Dataset Card: Sentinel-2 SR Harmonized",
  "score": 12.34,
  "source_id": "dataset-s2-sr-harmonized",
  "source_type": "official-data-catalog",
  "primary_status": "canonical",
  "source_urls": ["https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED"],
  "retrieved_at": "2026-06-21",
  "last_checked": "2026-06-21",
  "dataset_ids": ["COPERNICUS/S2_SR_HARMONIZED"],
  "operators": ["ImageCollection.filterDate", "ImageCollection.filterBounds", "ImageCollection.map", "Image.normalizedDifference", "Image.reduceRegions", "Export.table.toDrive"],
  "operator_chain": "ImageCollection.filterDate -> filterBounds -> map -> select/normalizedDifference -> composite -> reduceRegions -> Export.table.toDrive",
  "workflow_patterns": ["optical-cloud-mask-before-composite", "zonal-statistics-table-export"],
  "known_failures": ["qa60-discontinuity", "missing-scale-or-crs", "empty-image-collection", "quota-memory-risk"],
  "reason_for_selection": [
    "query matched dataset_id COPERNICUS/S2_SR_HARMONIZED",
    "query matched NDVI and cloud mask workflow terms",
    "canonical source selected over non-canonical operator note"
  ]
}
```

## Metadata Design

- Dataset cards should remain the primary carrier for `dataset_id`, platform, sensor, scale factors, quality bands, source URL, `retrieved_at`, `last_checked`, caveats, and source authority.
- Operator syntax notes should use stable fields such as `api_namespace`, `method_name`, `signature`, `required_args`, `return_type`, `python_usage`, `source_url`, `retrieved_at`, and `last_checked`.
- Operator relationship chains should be first-class metadata, not only prose. Store short ordered chains for common workflows such as Sentinel-2 NDVI zonal export, Landsat LST image export, Sentinel-1 change detection, and generic `reduceRegions`.
- Workflow patterns should label reusable decisions: cloud mask before composite, reducer with explicit scale and CRS, export selectors for table order, dry-run before live execution, and task monitoring with timeout.
- Known failures should be normalized into searchable tags and copied into traces when they affect a selected source: auth missing, empty collection, QA band caveat, projection ambiguity, memory/quota risk, export polling timeout, and client-side `getInfo()` misuse.

## Selection Logic

Retrieval should rank by text relevance, then annotate with structured reasons. Strong reasons include exact dataset id match, API/operator match, workflow pattern match, failure-risk match, and canonical source priority. Research notes may contribute operator chains and evaluation ideas, but should not be used as authority for API behavior when an official guide or Data Catalog card is also retrieved.

`reason_for_selection` should be deterministic and brief. It should be generated from explainable signals, not model prose: matched query tokens, matched metadata keys, chain overlap, source authority boost, and diversity fill such as "included to cover export failure handling".

## Output Contract

Plans and JSON search output should include a `retrieval_trace` block separate from citations. Citations answer "where did this come from"; the trace answers "why was this source used, what operator/workflow claim does it support, how fresh is it, and what risks remain".

Minimum acceptance checks:

- Search for `Sentinel-2 NDVI cloud mask export table` returns a dataset card, cloud masking note, reducer/export source, and operator-chain support.
- Each returned item has `source_urls`, `retrieved_at` or `last_checked`, `primary_status`, and `reason_for_selection`.
- Dataset-card matches outrank non-canonical research notes for dataset/API facts.
- Operator-chain queries retrieve both the chain note and the canonical sources needed to validate every API step.
- Known-failure queries such as `QA60`, `getInfo`, `quota`, or `empty collection` produce traces that name the failure tag and the supporting source.
