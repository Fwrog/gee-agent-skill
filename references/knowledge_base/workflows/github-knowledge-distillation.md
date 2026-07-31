# GitHub Knowledge Distillation Workflow

source_type: repository-governance
last_checked: 2026-07-31
risk_level: medium

## Goal

Turn public repositories and papers into small, source-backed patterns without copying project-specific code, data, identifiers, results, or unstated context.

## Mainline

1. Start with one bounded capability gap or failing evaluation case.
2. Queue candidate papers and repositories as metadata only.
3. Pin the reviewed revision and record README, license, paper, and relevant implementation or method surfaces by path and blob identifier.
4. Complete the data contract: identity/version, variables, scale/offset, QA/masks, grid/resampling, temporal scope, access/license/stability, and private dependencies.
5. Extract a generic method or operational boundary; do not copy code unless reuse was explicitly approved.
6. Recheck dataset IDs, bands, scale factors, QA, projections, and API behavior against current official Earth Engine sources.
7. Record an explicit promotion or non-promotion decision in the review ledger.
8. For an important lesson, add or update the source registry, one evidence card or rule, and at least one retrieval or behavior test. Keep general observations non-blocking.
9. Rebuild the document index and knowledge graph.
10. Run evidence quality, retrieval, benchmark, privacy, and release gates.
11. Promote the lesson only if the new tests pass without displacing higher-tier evidence.

## 200-Project Discovery Queue

Run:

```bash
python scripts/discover_gee_repos.py
```

The generated `references/corpus/github_gee_discovery_200.yml` combines GEE-topic, paper-linkage, and research-workflow lanes. Its score filters metadata only and requires direct GEE metadata evidence. Broad README-search matches without direct domain evidence are excluded.

The discovery snapshot retains `quality_screened_unreviewed` states so regeneration does not rewrite human decisions. `references/corpus/github_gee_reviewed_batch_01.yml` is the review overlay: 21 of 200 inventory records plus 3 anchors have exact revisions, checked surfaces, complete data contracts, and promotion decisions. The remaining 179 inventory records are still unreviewed.

## Mistake Loop

Run:

```bash
python scripts/run_distillation_mistake_lab.py --json
```

Each case records a plausible naive review, the required observations, and the expected misses. Important misses must map to an existing rule or evidence-card identifier; the lab fails when the target is absent. General misses stay in a corpus note unless a reproduced failure raises their impact.

Real project failures use the same loop through `references/knowledge_base/workflows/user-local-learning-overlay.md`. Private evidence remains in the authorized project workspace. The public repository receives only a generic failure signature, reproduced mechanism, scoped rule or card, claim boundary, and regression test.

## Public Ignorance Boundary

Treat private or unpublished context as deliberately absent. Do not infer it from filenames, commit history, issue discussions, neighboring files, geographic hints, or generated artifacts. A public card may describe only the reusable pattern, its source, scope, limitations, and non-claims.

## Source Roles

- Official Earth Engine sources define current platform and dataset facts.
- Papers may define evaluation taxonomies or methodological structures.
- Licensed community repositories may contribute generic implementation or operations patterns.
- Discovery-only repositories remain unreviewed metadata and cannot ground runtime guidance.

## Acceptance Record

For each promoted lesson, record the source ID, trust tier, allowed use, checked date, distilled pattern, limitations, claim boundary, and regression case. If the external benchmark suite and execution protocol were not reproduced unchanged, mark local results as non-comparable.
