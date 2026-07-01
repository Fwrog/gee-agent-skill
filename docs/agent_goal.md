# Agent Goal

Use this brief when continuing work on `gee-agent-skill`.

## Objective

Maintain a public, agent-native Google Earth Engine harness:

```text
request -> plan -> RAG evidence -> render -> validate -> preflight -> export -> trace -> generic knowledge
```

The repository should contain reusable infrastructure, public v0.1/v0.2 regression examples, generic dataset/rule/failure/workflow cards, and documentation. Private research tasks, unpublished academic demos, asset ids, result values, and manuscript material must stay outside the repository.

## Working Rules

- Prefer CLI and official Earth Engine Python API execution over browser or GUI control.
- Use Browser for official docs verification and visual QA.
- Use Google Drive only for handoff/readback when the user asks for Drive delivery.
- Use Data Analytics after data exists to validate charts, reports, and metric definitions.
- Use Computer Use only when no CLI/API/plugin route can complete the task.
- Use imagegen only for documentation visuals, never as scientific evidence.

## Public v0.3 Requirements

- Keep `gee-plan/v0.3` plans editable and schema-validated.
- Plans must expose AOI, time range, selected datasets, operators, scale/CRS, output schema, export metadata, validation rules, and review questions.
- Non-golden plans with placeholder AOIs must block live export with `V03_CONTEXT_REVIEW_REQUIRED`.
- Live export must require `--project` and `--confirm-live`.
- Run traces must avoid credentials, private asset ids, and unpublished research content.

## Public Regression Examples

- `gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json`
- `gee-skill ask "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV." --plan --json`

More complex academic demos are withheld from public docs and examples. If a private workflow teaches a reusable lesson, promote only the generic rule/card after privacy review.

## Validation Commands

```bash
python scripts/ingest_docs.py
python -m pytest -q
gee-skill smoke-test --json
gee-skill eval evals/benchmark_suite.yml --json
git diff --check
```
