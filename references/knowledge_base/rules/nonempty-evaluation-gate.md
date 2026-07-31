# Nonempty Evaluation Gate

rule_id: nonempty_evaluation_gate
evidence_level: reproduced-internal-regression
last_checked: 2026-07-31
importance: important_knowledge

A successful process exit or top-level `ok` value is not evaluation evidence when zero cases were executed.

Every evaluator must reject an absent or empty native case/task collection. Callers must use the evaluator that matches the fixture schema and verify a positive executed-case count plus the expected case identifiers before reporting a pass.

The observed failure came from sending a `cases`-based KG-RAG fixture to the generic `tasks`-based benchmark command. It returned `ok=true` with a count of zero. The generic evaluator now fails early and points to `scripts/run_kg_rag_eval.py`; the release gate uses that dedicated runner.
