# Extending The Harness

## Add A Workflow Recipe

1. Add a Jinja2 template under `assets/templates/<recipe>.py.j2`.
2. Add its schema to `src/geeskill/templates.py`.
3. Add an example task under `examples/<recipe>/task.yaml`.
4. Add semantic rules in `src/geeskill/semantic.py` if the workflow has domain-specific checks.
5. Add regression tests for rendering, validation, dry-run behavior, and trace output.

## Add A Dataset Card

1. Add markdown under `references/knowledge_base/datasets/`.
2. Include `source_id`, `source_type`, `publisher`, `url`, `retrieved_at`, `primary_status`, `dataset_id`, and `risk_level`.
3. Record bands, scale/offset, QA bands, cloud/quality policy, temporal coverage, and caveats.
4. Rebuild the index:

```bash
python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json
```

## Add A Semantic Validator

1. Add a ruleset name to `src/geeskill/semantic.py`.
2. Implement checks as `Finding` records with stable codes.
3. Map blocking failures to an error category when possible.
4. Add a positive fixture and at least one expected failure fixture.
5. Confirm `gee-skill validate <script> --json` exposes the new ruleset.

