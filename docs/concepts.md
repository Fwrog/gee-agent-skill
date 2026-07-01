# Concepts

## Closed-Loop Agent Workflow

The project treats a GEE workflow as a controlled loop:

```text
natural language -> plan -> evidence -> render -> validate -> preflight -> export -> trace -> reusable knowledge
```

The loop is intentionally split into reviewable stages. Execution does not jump from a prompt directly to an Earth Engine export; it first records intent, evidence, assumptions, validation results, and live-readiness checks.

## Plan-First Workflow

The harness separates interpretation from execution:

```text
ask --plan -> review-plan -> preflight-plan -> run-plan --confirm-live -> monitor-exports
```

`ask --plan` is offline. It turns a supported natural-language request into a reviewable plan with AOI, date range, candidate datasets, selected datasets, masking strategy, output schema, limitations, and live confirmation requirements.

## RAG Evidence

The local knowledge base includes official dataset cards, operator notes, operator relationship chains, common workflow patterns, failure cases, and research/operator notes. `retrieval_trace.json` records why each source was selected and how it influenced the workflow.

Official Google Earth Engine documentation is treated as canonical. Research notes and curated recipes guide evaluation and failure handling but do not override official API behavior.

## Generic Learning, Not Private Memory

User projects can reveal better rules, dataset cards, and failure cases. The public repository should only receive generic, source-backed lessons:

- reusable dataset facts and caveats;
- recurring API or export failure modes;
- validation rules and claim boundaries;
- workflow constraints that apply beyond one private task.

Private research questions, region lists, unpublished results, manuscript text, and private Earth Engine asset ids stay outside the public repository. See [Closed Loop](closed_loop.md).

## Tool Boundaries

The CLI and Earth Engine Python API are the execution path. Browser helps verify official docs and rendered documentation. Google Drive helps hand off output files. Data Analytics helps validate reports and charts after data exists. Computer Use is a GUI fallback. imagegen creates communication assets, not scientific evidence. See [Tool Permissions](tool_permissions.md).

## Boundaries vs Land Cover

Boundaries define where statistics are computed. Land-cover datasets define masks, strata, and interpretation groups. The v0.2 Hong Kong workflow uses the curated Hong Kong boundary as the AOI and Dynamic World as the land-cover mask source.

## Dry Run, Preflight, Live Export

Dry run renders and validates code without contacting Earth Engine. Preflight runs small safe Earth Engine probes and should not create export tasks. Live export requires explicit confirmation and only starts after validation and preflight pass.

## Traceability

Run traces live under `outputs/runs/<run_id>/`. They are designed to answer: what task was requested, what evidence was used, what code was generated, what validation found, whether live preflight passed, what export task was created, and what environment generated it.

## Demo Validation

The Hong Kong NDVI demos are regression examples for the harness contract. Their remote-sensing reasonableness can be checked with MODIS vegetation-index products, Landsat 8/9 surface reflectance, JRC Global Surface Water, Dynamic World, and ESA WorldCover. These checks support method plausibility but do not turn a demo export into a final vegetation assessment. See [Remote Sensing Validation Ladder](remote_sensing_validation.md).
