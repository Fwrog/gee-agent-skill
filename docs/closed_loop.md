# Closed Loop

The project is designed to get more useful without memorizing private research projects. Real tasks reveal missing datasets, rules, failure modes, and documentation gaps; only generic lessons are promoted into the public repository.

## Closed-Loop Flow

```text
user task
  -> intent and privacy classification
  -> local catalog / RAG retrieval
  -> official-source or browser verification for drifting facts
  -> plan / render / validate / preflight / export
  -> trace and data-quality review
  -> generic knowledge promotion
  -> RAG rebuild and tests
```

## What Can Be Promoted

| Public knowledge type | Examples |
| --- | --- |
| Dataset card | Dataset id, bands, scale, temporal coverage, QA bands, current caveats. |
| Rule card | Export images must use uniform band dtype; public boundary substitutes cannot support authoritative local claims. |
| Failure case | Unsupported CRS, empty collection, mixed export dtype, deprecated asset path, schema mismatch. |
| Workflow card | Plan-first NDVI export, land-cover summary, validation ladder, adaptive browser-backed knowledge loop. |

## What Must Stay Private

- unpublished research questions;
- private AOI lists or project-specific region whitelists;
- draft manuscript text and result values;
- private Earth Engine asset ids;
- local Drive folder organization;
- credentials, tokens, keys, and account identifiers.

## Promotion Checklist

Before a task-specific lesson enters the public repo:

- classify whether it is reusable beyond one private project;
- verify unstable dataset/API facts against official docs or live read-only checks;
- record `source_url`, `last_checked`, scope, and known limitations;
- state what the card cannot support;
- scan for private terms and private asset ids;
- rebuild the RAG index;
- add or update tests that prove retrieval/catalog coverage.

## Design Principle

The public skill should learn how to do GEE work more safely and reproducibly. It should not learn the confidential content of a user's research project.
