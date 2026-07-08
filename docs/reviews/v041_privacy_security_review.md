# v0.4.1 Privacy And Security Review

Date: 2026-07-09

Checked areas: source registry, evidence cards, graph assets, review docs, evals, and release-gate scan scope.

Findings:

- No credentials, OAuth tokens, service account keys, or credential paths are intentionally added.
- No private Earth Engine asset IDs are added to public KG-RAG assets.
- Red-team private asset strings appear only in tests/evals as synthetic refusal examples.
- No private Drive folders or unpublished result values are added.

Required gate: `scripts/release_gate_kg_rag.py` includes a bounded privacy scan over KG-RAG public assets.
