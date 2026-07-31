# Source-Tier Precedence Regression Gate

rule_id: source_tier_precedence_regression
evidence_level: reproduced-internal-regression
last_checked: 2026-07-31
importance: important_knowledge

Adding accepted evidence cards changes retrieval competition. Schema validation and successful retrieval of the new cards do not prove that source precedence is preserved.

For authority-conflict red-team queries, the regression suite must verify all three conditions:

1. the official source remains in accepted evidence;
2. the lower-tier candidate remains visible as contextual evidence;
3. the rendered prompt labels that candidate as contextual only.

The first observed failure occurred after expanding accepted cards: a fixed top-k window crowded the candidate context out of the test. The corrected test uses an explicit authority-conflict query and a reviewed retrieval budget. Future corpus growth must rerun this gate instead of assuming a formerly adequate top-k remains adequate.
