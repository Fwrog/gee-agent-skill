# Extending The Harness

## Add A Workflow Recipe

1. Add a Jinja2 template under `assets/templates/<recipe>.py.j2`.
2. Add its schema to `src/geeskill/templates.py`.
3. Add an example task under `examples/<recipe>/task.yaml`.
4. Add semantic rules in `src/geeskill/semantic.py` if the workflow has domain-specific checks.
5. Add regression tests for rendering, validation, dry-run behavior, and trace output.

## Add A Dataset Card

1. Add markdown under `references/knowledge_base/datasets/`.
2. Include `source_id`, `source_type`, `publisher`, `source_url`, `last_checked`, `primary_status`, `dataset_id`, and `risk_level`.
3. Record bands, scale/offset, QA bands, cloud/quality policy, temporal coverage, and caveats.
4. Rebuild the index:

```bash
python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json
```

## Add Source-Grounded KG-RAG Evidence

1. Add or update a reviewed source in `references/sources/source_registry.yml`.
2. Run `python scripts/validate_sources.py --json`.
3. Add a short paraphrased evidence card under `references/evidence_cards/`; do not copy long source text.
4. Include allowed use, trust tier, claim boundaries, planner hints, validator hints, and private-content risk.
5. Run `python scripts/validate_evidence_cards.py --json`.
6. Add graph seed nodes or edges only when the relationship is stable and useful for retrieval.
7. Rebuild and validate the graph:

```bash
python scripts/build_kg.py --json
python scripts/validate_kg.py --json
```

8. Add a retrieval or semantic-validator test before using the evidence in planner behavior.

## Add General GEE Knowledge

Use `references/knowledge_base/core/`, `operators/`, `workflows/`, and `failure-cases/` for reusable GEE AI knowledge that is not tied to one dataset. Include source URLs, last-checked dates, operator chains, known failures, and recovery hints so retrieval traces remain auditable.

## Review A User-Local Lesson

Users may maintain a separate Obsidian or Markdown Skill with private evidence
and personal rules. Do not copy that vault into this repository.

1. Ask the user-owned Skill to export an approved public-safe manifest.
2. Validate it without mutation:

```bash
gee-skill learning review-manifest <promotion-manifest.json> --json
```

3. Treat `candidate_review_ready` as queue admission only.
4. Independently reproduce the failure and verify current platform or dataset
   facts against official sources.
5. Map each `<kind>:<portable-id>` target to a public artifact and implement the
   named regression.
6. Run the relevant tests and release gate.
7. Merge only through normal maintainer review and a versioned release.

See
[user-local-learning-overlay.md](../references/knowledge_base/workflows/user-local-learning-overlay.md)
and
[`mistake-promotion-manifest-v0.1.schema.json`](../schemas/mistake-promotion-manifest-v0.1.schema.json).

## Add Corpus Sources

1. Refresh broad candidates when needed:

```bash
python scripts/discover_gee_repos.py --min-candidates 200 --max-candidates 200 --out references/corpus/github_gee_discovery_200.yml
```

2. Promote only reviewed candidates into `references/corpus/github_gee_seed_repos.yml`.
3. Keep `harvest_level` conservative:
   - `metadata_and_patterns_only` for clear-license, high-quality sources.
   - `metadata_only_until_license_review` for unclear or unreviewed sources.
   - `links_only` for awesome lists and discovery indexes.
4. Prioritize known high-signal community sources such as `giswqs`/OpenGeo and `gee-community` before long-tail snippets.
5. For paper-linked repositories from TGRS, ISPRS, JAG, RSE, or similar venues, record article DOI or publisher URL, repository URL, inspected commit/release, license, private-asset dependency check, and reproducibility scope before promotion.
6. Clone reviewed sources outside this repository and run:

```bash
python scripts/analyze_gee_corpus.py /tmp/gee-corpus-sample/<repo> --out outputs/corpus/<audit>.json
```

7. Do not copy third-party code into this repository by default.
8. Promote only distilled operator patterns, required fields, failure cases, and validation implications into `references/knowledge_base/`.
9. Record source URL, last-checked date, risk level, and known failure codes in every promoted card.
10. Rebuild both indexes:

```bash
python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json
python scripts/ingest_docs.py --docs-dir references/knowledge_base --out src/geeskill/resources/index/gee_docs_index.json
```

## Add A Semantic Validator

1. Add a ruleset name to `src/geeskill/semantic.py`.
2. Implement checks as `Finding` records with stable codes.
3. Map blocking failures to an error category when possible.
4. Add a positive fixture and at least one expected failure fixture.
5. Confirm `gee-skill validate <script> --json` exposes the new ruleset.
