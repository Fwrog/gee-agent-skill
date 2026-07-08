# Repo Audit

Date: 2026-07-09

The repository already had a local BM25 Markdown RAG layer, dataset/catalog helpers, semantic validators, CLI JSON envelopes, v0.3 HLS/MODIS product-intercomparison docs, and a public knowledge loop.

Relevant existing components:

- `src/geeskill/rag.py`: Markdown chunking and BM25-lite retrieval.
- `src/geeskill/planner.py`: plan text generation from BM25 search results.
- `src/geeskill/semantic.py`: static semantic rulesets.
- `src/geeskill/cli.py`: agent-facing deterministic JSON commands.
- `references/knowledge_base/`: dataset, operator, recipe, rule, workflow, and failure Markdown cards.
- `docs/roadmap.md`: already identifies v0.4 product-intercomparison generalization and semantic validators.

v0.4 adds source registry, evidence cards, a deterministic graph index, hybrid retrieval, CLI commands, semantic validator hooks, and eval fixtures without changing live Earth Engine execution behavior.
