# Failure Case: Source Fidelity And Private Research Boundaries

source_id: failure-source-fidelity-private-research
source_type: curated-failure-case
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/image_upload; https://developers.google.com/earth-engine/guides/exporting
last_checked: 2026-07-01
known_failure: SOURCE_FIDELITY_OVERCLAIM
known_failure: PROXY_DATASET_OVERCLAIM
known_failure: BOUNDARY_AUTHORITY_MISMATCH
known_failure: PRIVATE_RESEARCH_LEAK
risk_level: high

## Symptoms

Generated plans or writeups overstate what a public proxy dataset can prove, describe a substitute boundary as authoritative, or place private research details in a public skill repository.

## Required Gates

- Preserve the distinction between public-data prototypes and source-specific final analyses.
- Do not call a result by the name of a private or uploaded dataset unless the plan includes the exact asset id and access status.
- Do not claim official administrative or county-scale results when the boundary source is a public substitute.
- Keep private research questions, region whitelists, draft paper text, generated exports, and unpublished conclusions outside the public repository.
- Add private paper workspaces and drafts to `.gitignore` before creating local project artifacts near the repo.

## Recovery

Downgrade wording to "public-data prototype", "proxy-based analysis", or "public boundary substitute"; move private materials to a local ignored workspace; and add a reviewed dataset card or uploaded-asset card before generating source-specific claims.
