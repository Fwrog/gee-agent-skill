# v0.4/v0.4.1 KG-RAG Architecture

v0.4 turns the local Markdown RAG layer into a source-grounded KG-RAG pipeline:

```text
official docs / papers / vetted repos
  -> source registry
  -> source policy review
  -> evidence cards
  -> deterministic KG index
  -> hybrid retrieval bundle
  -> planner hints / validator hints / eval cases
```

This is not model training, fine-tuning, or a generic chatbot layer. It is a deterministic evidence pipeline for Google Earth Engine agent workflows.

v0.4.1 hardens the same layer rather than replacing it. The hardening adds source refresh status, evidence quality audit checks, deterministic weighted lexical ranking, accepted/candidate evidence separation, query classification, trace sidecars, semantic fixtures, red-team eval cases, and a local release gate.

## Harness Planes

v0.4 preserves the existing CLI harness as the control plane and adds source-grounded retrieval around it.

1. Control plane: existing `gee-skill` commands for info, doctor, plan, render, validate, preflight, run, exports, trace, and eval.
2. Knowledge plane: source registry, evidence cards, deterministic KG, hybrid retrieval, claim boundaries, failure cases, planner hints, and validator hints.
3. Reasoning plane: optional downstream LLMs may consume evidence bundles, but no LLM output bypasses schema validation, semantic validation, or preflight.
4. Execution plane: Earth Engine Python API execution remains unchanged and still requires explicit project and live confirmation.
5. Evaluation plane: local retrieval, planner-grounding, semantic-validator, trace, privacy, copyright, and source-policy checks.

## Components

- `references/sources/source_registry.yml`: source metadata, trust tier, allowed use, review status, and claim boundary.
- `references/evidence_cards/*.yml`: short, paraphrased, auditable evidence cards.
- `references/graph/ontology.yml`: node and edge vocabulary.
- `references/graph/seed_graph.yml`: v0.3 HLS/MODIS product-intercomparison graph seed.
- `references/index/gee_kg_index.json`: built deterministic KG index.
- `src/geeskill/kg.py`: graph build, validation, search, neighbors, shortest path, explain, and Mermaid export.
- `src/geeskill/hybrid_retrieval.py`: BM25 text retrieval plus evidence cards plus graph context.
- `scripts/audit_evidence_quality.py`: v0.4.1 evidence-card quality audit.
- `scripts/release_gate_kg_rag.py`: v0.4.1 local release gate for source/evidence/KG/eval/privacy checks.

## Planner And Validator Use

KG-RAG is used as grounding, not as unchecked generation. `gee-skill plan` and plan-first ask flows can attach a KG-RAG grounding section to the Markdown plan and write `hybrid_retrieval_bundle.json`, `source_quality_summary.json`, and `claim_boundary_summary.json` into the run trace when the local indexes are available. Semantic validation remains deterministic; the `product_intercomparison` ruleset blocks or warns on MODIS NDVI without scale factor, MODIS VI without QA policy, HLS without Fmask policy, direct fine/coarse pixel comparison, missing projection handling around `reduceResolution`, missing claim boundary, weak Golden promotion evidence, and ground-truth overclaim.

## v0.4.1 Bundle Contract

`gee-skill retrieve hybrid ... --json` keeps the v0.4 fields and adds:

- `query_classification`
- `accepted_evidence_cards`
- `candidate_evidence_cards`
- `warnings`
- richer `source_quality_summary`

Accepted evidence may ground planner and validator hints. Candidate evidence is contextual only and cannot establish current API or dataset facts.

## Safety Boundaries

- Official Tier A sources override papers and community sources for current API and dataset facts.
- Papers support evaluation and methodology patterns only.
- Community repos support distilled patterns only unless license review explicitly allows more.
- Hybrid retrieval must say `insufficient evidence` when sources are missing.
- KG-RAG augments planning and validation; it does not bypass render, schema, semantic validation, preflight, `--confirm-live`, or trace gates.
- v0.4.1 remains deterministic and local; v0.5 is the future scope for typed product-intercomparison planning.
