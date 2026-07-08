# Existing Harness Audit

Date: 2026-07-09

The repository already had an agent-native GEE harness. v0.4 does not rebuild it.

Existing control-plane components preserved:

- `src/geeskill/cli.py`: deterministic CLI commands and JSON envelopes.
- `src/geeskill/rag.py`: local Markdown BM25-style retrieval.
- `src/geeskill/planner.py`: Markdown plan generation from local retrieval.
- `src/geeskill/templates.py` and `assets/templates/`: template rendering.
- `src/geeskill/validation.py` and `src/geeskill/semantic.py`: static and semantic validation.
- `src/geeskill/generic_preflight.py` and specific preflight modules: offline/live boundary checks.
- `src/geeskill/run_trace.py`: run trace artifacts.
- `src/geeskill/evaluation.py` and `evals/`: local benchmark flow.
- `references/knowledge_base/`: public reusable GEE knowledge cards.
- `docs/validation/hk_ndvi_product_intercomparison_v03.md`: v0.3 HLS/MODIS public product-intercomparison evidence.

Preserved safety gates:

- schema validation before rendering;
- static and semantic validation before execution;
- dry-run behavior before live Earth Engine calls;
- explicit Earth Engine project for live preflight/run;
- explicit `--confirm-live` for live execution;
- trace output for review and reuse.

v0.4 strengthens the knowledge plane around this harness with a source registry, evidence cards, deterministic KG, hybrid retrieval, planner hints, validator hints, eval fixtures, and review artifacts.
