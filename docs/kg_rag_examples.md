# KG-RAG Examples

Build and validate the graph:

```bash
python scripts/build_kg.py --json
python scripts/validate_kg.py --json
```

Search evidence:

```bash
gee-skill evidence search "MODIS NDVI scale factor" --json
gee-skill kg search "HLS MODIS product intercomparison" --json
gee-skill kg explain product_intercomparison --json
```

Retrieve a hybrid bundle:

```bash
gee-skill retrieve hybrid "Can I directly compare 30m HLS pixels with 250m MODIS pixels?" --json
```

Expected behavior:

- The bundle includes BM25 text chunks, evidence cards, graph nodes, graph edges, graph paths, rules, known failure cases, claim boundaries, source-tier counts, planner hints, validator hints, and compact prompt context.
- v0.4.1 bundles also include `query_classification`, `accepted_evidence_cards`, `candidate_evidence_cards`, source URLs, `last_checked`, reviewer status, refresh status, and `warnings`.
- Direct 30 m HLS versus 250 m MODIS pixel comparison should retrieve the fine/coarse failure case and product-intercomparison claim boundary.
- Product intercomparison should be framed as product-level consistency, not in-situ ground-truth accuracy.

Before v0.4.1, a candidate paper card and an accepted official card could appear in the same flat `evidence_cards` list. After v0.4.1, the same query keeps the backward-compatible flat list but also separates accepted and candidate evidence so planners can avoid treating candidate methodology context as current dataset/API authority.

Run the local release gate before publishing KG-RAG changes:

```bash
python scripts/release_gate_kg_rag.py --json
```
