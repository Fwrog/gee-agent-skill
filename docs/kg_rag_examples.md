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
- Direct 30 m HLS versus 250 m MODIS pixel comparison should retrieve the fine/coarse failure case and product-intercomparison claim boundary.
- Product intercomparison should be framed as product-level consistency, not in-situ ground-truth accuracy.
