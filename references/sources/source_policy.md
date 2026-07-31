# Source Policy

This repository stores source metadata, citations, short paraphrased evidence, and deterministic graph links. It does not store full papers, scraped pages, private assets, credentials, local Drive paths, private AOIs, unpublished claims, or third-party code copied for reuse.

## Trust Tiers

- `A`: official Google Earth Engine docs, Data Catalog pages, API reference, official tutorials, and `google/earthengine-api`.
- `B`: arXiv, journal, conference, and JOSS papers.
- `C`: vetted community repositories and docs with clear provenance and license.
- `D`: diagnostic sources such as forum threads, issues, blogs, and Q&A pages.

Official Tier A sources override all other sources for current dataset IDs, band names, scale factors, QA bits, projections, quotas, API behavior, and export semantics.

## Allowed Use

- `metadata_only`: store bibliographic metadata, URL, and review status only.
- `summary_only`: store short paraphrased summaries and structured facts.
- `distilled_patterns`: store generic patterns without copying code.
- `short_quoted_excerpt_allowed`: short compliant excerpts may be used with citation.
- `code_reuse_allowed`: allowed only after explicit license review and attribution.
- `not_allowed`: source must not be used.

## Promotion Rule

A source can be `accepted` only when it has a stable ID, URL, source type, trust tier, allowed use, last checked date, clear include reason, low or mitigated private-content risk, and source-policy approval.

## Refresh Status

Every source has `source_refresh_status`:

- `fresh`: public URL/source family was checked in the controlled refresh window and may be used according to trust tier and allowed use.
- `stale`: source exists in the registry but should be refreshed before current-fact use.
- `unavailable`: URL or source family could not be verified; do not rely on it.
- `candidate_unverified`: candidate source retained for metadata or research context only.

Accepted Tier A sources should be `fresh` before they ground current dataset/API facts. Accepted Tier B methodology sources and Tier C implementation patterns remain subordinate to Tier A facts. Candidate papers and repositories must not influence runtime guidance until promoted through review. An adapted local benchmark must declare whether it reproduces the external cases and protocol; otherwise its scores are not comparable.
