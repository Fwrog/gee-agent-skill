# Final Harness KG-RAG Upgrade Report

Status: implementation complete pending downstream review
Date: 2026-07-09

## Summary

The repository was upgraded from a lightweight BM25 Markdown RAG harness into a source-grounded GEE Research KG-RAG harness. The existing CLI-first plan/render/validate/preflight/run/monitor/trace flow remains the control plane.

## Strengthened Rather Than Rebuilt

- Existing CLI commands remain available.
- Existing live Earth Engine execution behavior is unchanged.
- Existing schema, static validation, semantic validation, preflight, explicit project, and `--confirm-live` gates remain authoritative.
- KG-RAG provides evidence bundles, planner hints, validator hints, claim boundaries, and eval fixtures; it does not generate unchecked code.

## New Assets

- Source governance: `references/sources/source_registry.yml`, `references/sources/source_policy.md`, `schemas/source-registry.schema.json`, `scripts/validate_sources.py`.
- Evidence cards: `references/evidence_cards/*.yml`, `schemas/evidence-card.schema.json`, `scripts/validate_evidence_cards.py`.
- Knowledge graph: `references/graph/ontology.yml`, `references/graph/seed_graph.yml`, `schemas/knowledge-graph.schema.json`, `src/geeskill/kg.py`, `scripts/build_kg.py`, `scripts/validate_kg.py`, `scripts/export_kg_mermaid.py`.
- Hybrid retrieval: `src/geeskill/hybrid_retrieval.py`.
- Evaluation: `evals/kg_rag_retrieval_suite.yml`, `evals/planner_research_grounding_suite.yml`, `scripts/run_kg_rag_eval.py`.
- Reviews: `docs/reviews/remote_sensing_review.md`, `software_architecture_review.md`, `privacy_security_review.md`, `copyright_license_review.md`, and `red_team_review.md`.

## Current Counts

- Sources: 31 total, 23 accepted, 8 candidate.
- Evidence cards: 43 total, 37 accepted, 6 candidate.
- Knowledge graph: 106 nodes, 105 edges.
- KG-RAG retrieval eval: 8 cases.

## Planner And Validator Integration

`gee-skill plan` can now attach a `KG-RAG Grounding Hints` section when local KG-RAG indexes are available and records the bundle in `hybrid_retrieval_bundle.json`. Semantic validation includes product-intercomparison checks for MODIS scale factor, MODIS QA, HLS Fmask, fine/coarse aggregation, projection handling, claim boundaries, and Golden evidence requirements.

## Limitations

- Research papers and unreviewed benchmark repos are not promoted as current dataset/API authorities.
- Graph search is deterministic lexical search, not semantic embedding search.
- Product intercomparison remains product-level consistency evidence, not in-situ ground-truth validation.
- Live Earth Engine runs still depend on user credentials and explicit confirmation.

## Recommended Next PRs

- Add automated comparator tests against the canonical v0.3 HLS/MODIS implementation.
- Add more product-intercomparison recipe templates after evidence review.
- Add deterministic ranking improvements for graph search.
- Expand red-team cases for newly promoted datasets and operators.
