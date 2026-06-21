# Concepts

## Plan-First Workflow

The harness separates interpretation from execution:

```text
ask --plan -> review-plan -> preflight-plan -> run-plan --confirm-live -> monitor-exports
```

`ask --plan` is offline. It turns a supported natural-language request into a reviewable plan with AOI, date range, candidate datasets, selected datasets, masking strategy, output schema, limitations, and live confirmation requirements.

## RAG Evidence

The local knowledge base includes official dataset cards, operator notes, operator relationship chains, common workflow patterns, failure cases, and research/operator notes. `retrieval_trace.json` records why each source was selected and how it influenced the workflow.

Official Google Earth Engine documentation is treated as canonical. Research notes and curated recipes guide evaluation and failure handling but do not override official API behavior.

## Boundaries vs Land Cover

Boundaries define where statistics are computed. Land-cover datasets define masks, strata, and interpretation groups. The v0.2 Hong Kong workflow uses the curated Hong Kong boundary as the AOI and Dynamic World as the land-cover mask source.

## Dry Run, Preflight, Live Export

Dry run renders and validates code without contacting Earth Engine. Preflight runs small safe Earth Engine probes and should not create export tasks. Live export requires explicit confirmation and only starts after validation and preflight pass.

## Traceability

Run traces live under `outputs/runs/<run_id>/`. They are designed to answer: what task was requested, what evidence was used, what code was generated, what validation found, whether live preflight passed, what export task was created, and what environment generated it.
