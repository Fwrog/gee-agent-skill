# v0.4.1 Repo Diff Audit

Date: 2026-07-09

Scope: existing v0.4 KG-RAG implementation in `Fwrog/gee-agent-skill`. This audit confirms v0.4.1 is a hardening pass, not a harness rebuild or v0.5 planner rewrite.

| Area | Done | Partial | Missing | Risk | Recommended action |
| --- | --- | --- | --- | --- | --- |
| Source registry | v0.4 registry, tiers, allowed use, review status | Refresh status was not auditable | `source_refresh_status`, changed-source notes | Stale facts could look reviewed | Add refresh status, review notes, source policy tests |
| Evidence cards | Structured cards with facts, limitations, boundaries, hints | Search metadata was lexical only | alias/canonical/negative routing metadata | Candidate evidence could look equivalent to accepted evidence | Add retrieval metadata and evidence quality audit |
| KG index | Deterministic graph build/validate/search/path/explain | Ranking was simple term matching | Weighted ranking and negative routing | Workflow contamination in top hits | Add weighted scoring and ranking tests |
| Hybrid retrieval | BM25 + cards + KG bundle | Flat evidence list | accepted/candidate split, classification, warnings | Planners may overuse candidate sources | Preserve old field and add richer bundle fields |
| Planner traces | `hybrid_retrieval_bundle.json` existed for plan path | Sidecar summaries inconsistent | source and claim summaries | Trace incomplete for review | Write additive sidecars when bundle exists |
| Semantic validator | Product-intercomparison hints existed | Mostly string-pattern checks | fixture suite, comment-only guard, overclaim check | False confidence from comments or reports | Add fixture tests and code-view checks |
| Evals | Retrieval eval existed | Planner/validator eval coverage thin | semantic fixture suite and exclusion cases | Routing regressions unnoticed | Expand eval runner and suites |
| Release gate | Separate scripts existed | No single v0.4 gate | release gate orchestrator | Manual release drift | Add `scripts/release_gate_kg_rag.py` |
| Reviews/docs | v0.4 docs/reviews existed | v0.4.1 distinction absent | ranking docs, v0.4.1 reviews | Portfolio overclaim | Update docs and reviews |

Conclusion: the control plane is preserved. v0.4.1 strengthens source governance, retrieval quality, trace completeness, validation fixtures, and release gates around the existing harness.
