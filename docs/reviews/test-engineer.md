# Test Engineer Review: Regression And Benchmark Coverage

Status: useful smoke coverage is in place, but the regression contract is still thinner than the harness trace/audit model documented in `docs/harness.md`.

## Confirmed Coverage

- Retrieval has basic relevance and deterministic ordering checks in `tests/test_rag.py`, plus a plan trace smoke test that verifies `retrieval_trace.json` exists and each evidence item has `reason_for_selection`.
- Template rendering covers the Hong Kong monthly NDVI happy path, missing variable failure, and path traversal rejection in `tests/test_templates.py`.
- Semantic validation covers one positive Sentinel-2 monthly NDVI fixture, one wrong-band negative fixture, validation taxonomy serialization, unresolved template tokens, and bad date order.
- Dry-run boundaries are covered at the CLI level: dry run succeeds without credentials, live run refuses missing `--project`, and direct dry-run invocation writes a trace file.
- The benchmark suite has one retrieval case and two render/validate cases, and `tests/test_evaluation.py` confirms the suite can be invoked through the CLI.

## Main Gaps

1. Retrieval trace quality is only lightly asserted. Tests should lock the full evidence envelope from `docs/harness.md`: `evidence_type`, `source_url`, `last_checked`, `primary_status`, `reason_for_selection`, `influence`, non-empty excerpts, and coverage counts for dataset/operator/workflow/failure support. The current benchmark retrieval check only requires one source-path substring, so ranking or provenance regressions could pass.
2. Benchmark result semantics need assertions. `tests/test_evaluation.py` only checks the suite id appears in stdout; it should assert JSON `ok`, per-task statuses, generated eval script paths, validation details, semantic errors, and failure behavior. `run_benchmark_suite()` supports `expected_failure`, but the committed suite has no expected-failure task to prove stable failure codes or messages.
3. Template rendering coverage should include every shipped template and packaged-resource path, not only `hk_district_monthly_ndvi`. Add table-driven checks for required datasets/operators, no unresolved Jinja tokens, expected export calls, and exact `TemplateContextError` messages for missing/invalid context fields.
4. Semantic validation has good starter tests, but expected failure messages are not broad enough. Add negative fixtures for missing cloud mask, missing monthly aggregation, missing export selectors/file format, missing region/scale/CRS, client-side misuse, and unknown dataset/band cases; assert stable `code`, `category`, `rule_id`, `suggested_fix`, and user-facing CLI JSON fields.
5. Dry-run and final audit command behavior should be verified against the audit contract, not just file existence. Assert `dry_run_report.json` has `contacted_earth_engine: false`, `validation_ok`, script path, and timestamp; assert `final_report.md` includes task/script, validation, dry-run/live status, and run id. Add doc-command smoke checks for the README/SKILL audit sequence: `search-docs`, `smoke-test`, `evaluate`, `plan`, `validate --json`, and `run --dry-run --json`.

## Suggested Next Tests

- Add a `tests/test_benchmark_contract.py` that calls `run_benchmark_suite()` directly and asserts structured result payloads for retrieval, render/validate, unknown-kind, and expected-failure tasks.
- Expand `tests/test_trace_and_registry.py` to parse all trace JSON files and validate the required audit schema, not just presence.
- Add parameterized template and semantic fixtures so new templates cannot ship without render, validation, dry-run, and expected-failure coverage.
