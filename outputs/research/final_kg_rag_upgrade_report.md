# Final KG-RAG Upgrade Report

Status: implementation complete pending downstream review
Date: 2026-07-09

## Summary

This v0.4 upgrade adds a source-grounded KG-RAG layer to `gee-agent-skill`. It keeps live Earth Engine behavior unchanged and focuses on deterministic source governance, evidence cards, graph retrieval, hybrid retrieval, semantic risk detection, and evaluation cases.

## Changed Areas

- Source registry, source policy, source discovery report, and source validation.
- Evidence cards for official platform/API behavior, datasets, operators, MODIS/HLS product intercomparison, rule cards, community patterns, and candidate research context.
- Lightweight ontology, seed graph, deterministic graph index, graph validation, graph search, neighbors, path, explain, and Mermaid export.
- Hybrid retrieval bundle combining BM25 text evidence, evidence cards, KG nodes/edges/paths, source tiers, claim boundaries, planner hints, and validator hints.
- CLI command groups for `sources`, `evidence`, `kg`, and `retrieve hybrid`.
- Product-intercomparison semantic validator hooks and planner KG-RAG grounding hints.
- README, README.zh-CN, roadmap, CLI reference, and KG-RAG docs.

## New Commands

- `gee-skill sources discover --json`
- `gee-skill sources validate --json`
- `gee-skill evidence list --json`
- `gee-skill evidence show <card_id> --json`
- `gee-skill evidence search "<query>" --json`
- `gee-skill kg build --json`
- `gee-skill kg validate --json`
- `gee-skill kg search "<query>" --json`
- `gee-skill kg neighbors <node_id> --json`
- `gee-skill kg path <source_id> <target_id> --json`
- `gee-skill kg explain <topic> --json`
- `gee-skill retrieve hybrid "<query>" --json`

## Source Tiers

Accepted Tier A sources cover official Earth Engine docs, Data Catalog, API reference, official GitHub repo, HLS/MODIS catalog pages, scale/projection/reduceResolution guidance, quotas, and Code Editor context.

Candidate research sources include GEE-OPs, AutoGEEval, AutoGEEval++, Geo-FuB, Gorelick 2017, and geemap JOSS. Candidate sources do not override official facts.

## Counts

- Sources: 31 total, 23 accepted, 8 candidate.
- Evidence cards: 43 total, 37 accepted, 6 candidate.
- Knowledge graph: 106 nodes, 105 edges.
- KG-RAG eval suite: 8 cases, all passed.

## Acceptance Results

- `python -m pytest -q`: passed.
- `python scripts/validate_sources.py --json`: passed.
- `python scripts/validate_evidence_cards.py --json`: passed.
- `python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json`: passed.
- `python scripts/build_kg.py --json`: passed.
- `python scripts/validate_kg.py --json`: passed.
- `python scripts/run_kg_rag_eval.py --suite evals/kg_rag_retrieval_suite.yml --json`: passed.
- `gee-skill sources validate --json`: passed after local editable install exposed the console script.
- `gee-skill evidence search "MODIS NDVI scale factor" --json`: passed.
- `gee-skill kg search "HLS MODIS product intercomparison" --json`: passed.
- `gee-skill kg explain product_intercomparison --json`: passed.
- `gee-skill retrieve hybrid "Can I directly compare 30m HLS pixels with 250m MODIS pixels?" --json`: passed.
- `gee-skill retrieve hybrid "Which evidence supports product-level consistency but not ground-truth accuracy?" --json`: passed.
- `gee-skill smoke-test --json`: passed.
- `git diff --check`: passed.

## Review Findings

See `docs/reviews/kg_rag_review_log.md` and the individual review files under `docs/reviews/` for simulated subagent review findings across source-scout, source-policy, evidence-curation, ontology, KG, hybrid retrieval, CLI, planner-validator, remote sensing, software architecture, privacy/security, copyright/license, and red-team passes.

## Known Limitations

- Research sources are metadata/candidate only unless later evidence-curation review promotes them.
- The KG is intentionally lightweight and local; it is not a full scientific ontology.
- Hybrid retrieval provides planner/validator hints but does not execute or modify Earth Engine workflows.
- Generic `product_intercomparison` plan schema support and automated comparator generation remain recommended follow-up PRs.
