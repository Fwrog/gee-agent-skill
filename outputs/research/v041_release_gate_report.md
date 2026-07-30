# v0.4.1 KG-RAG Release Gate Report

- Overall ok: True
- Check count: 12

| Check | OK | Return code |
| --- | --- | --- |
| `python scripts/validate_sources.py --json` | True | 0 |
| `python scripts/validate_evidence_cards.py --json` | True | 0 |
| `python scripts/audit_evidence_quality.py --json` | True | 0 |
| `python scripts/ingest_docs.py --docs-dir references/knowledge_base --out references/index/gee_docs_index.json` | True | 0 |
| `python scripts/build_kg.py --json` | True | 0 |
| `python scripts/validate_kg.py --json` | True | 0 |
| `python scripts/run_kg_rag_eval.py --suite evals/kg_rag_retrieval_suite.yml --json` | True | 0 |
| `python scripts/run_kg_rag_eval.py --suite evals/planner_research_grounding_suite.yml --json` | True | 0 |
| `python scripts/run_kg_rag_eval.py --suite evals/semantic_validator_fixture_suite.yml --json` | True | 0 |
| `privacy_scan` | True |  |
| `docs_command_consistency` | True |  |
| `git diff --check` | True | 0 |
