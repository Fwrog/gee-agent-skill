# Workflow Pattern: Adaptive Browser-Backed Knowledge Loop

source_id: workflow-adaptive-browser-backed-knowledge-loop
source_type: curated-workflow-pattern
primary_status: curated
source_url: https://developers.google.com/earth-engine/datasets/; https://developers.google.com/earth-engine/guides
last_checked: 2026-07-01
operator_chain: user task -> local retrieval -> gap classification -> browser verification -> generic knowledge update -> validation -> private/public boundary review
risk_level: high

## Pattern

Use concrete user tasks to improve the harness without hard-coding private projects. Start with the local catalog and knowledge base, then classify gaps into reusable public knowledge, task-specific private notes, or unsupported claims.

When a gap depends on current dataset availability, band names, API behavior, upload workflow, quota limits, or official guidance, verify it with browser-backed primary sources before adding a card or rule.

## Update Targets

- Add dataset cards for reusable public Earth Engine datasets, including bands, temporal coverage, scale, caveats, and `last_checked`.
- Add failure-case cards when a task reveals a recurring overclaim, validation gap, runtime error, or privacy boundary.
- Add recipe or template constraints only after the pattern repeats or clearly generalizes beyond one private project.
- Add private project notes outside the public repository when the content includes unpublished research framing, region lists, draft text, custom assets, or preliminary conclusions.

## Required Gates

- Every public knowledge update must name a source URL and state what the dataset or rule cannot support.
- Browser-derived facts must be compressed into reusable guidance, not copied as long source text.
- Generated public rules must not contain private research questions, region whitelists, unpublished result values, or draft manuscript wording.
- After updating cards, rebuild the local index and run targeted retrieval or catalog tests.
- Defer structural simplification until a project retrospective identifies repeated friction across real tasks.

## Generalization Checklist

When a user problem reveals a gap, classify it before editing the public skill:

1. Extract the reusable issue: dataset fact, API behavior, export failure, validation rule, claim boundary, or workflow order.
2. Remove task-specific identifiers: private AOI lists, unpublished results, draft manuscript language, local Drive paths, private asset ids, and credentials.
3. Verify drifting facts with official docs, dataset catalog pages, or live read-only checks.
4. Choose one public target:
   - dataset card for bands, coverage, scale, QA, and caveats;
   - rule card for mandatory behavior;
   - failure case for errors and recovery;
   - workflow card for repeated multi-step patterns.
5. Add `source_url`, `last_checked`, scope, known limitations, and `cannot claim` language.
6. Rebuild RAG index and add retrieval/catalog tests for the new reusable knowledge.
7. Run a privacy keyword scan before finalizing public repo changes.

If the lesson only makes sense with the user's private research context, write it to the private workspace instead of this repository.

## Simplification Policy

Do not simplify the skill during the middle of a private research run unless the current structure blocks progress. At the end of a project, summarize repeated steps, repeated validation failures, redundant cards, and stale public claims, then simplify the skill around the stable patterns that survived real use.

## Failure Cases

known_failure: UNVERIFIED_BROWSER_FACT
known_failure: PRIVATE_CONTEXT_IN_PUBLIC_CARD
known_failure: PREMATURE_SKILL_ABSTRACTION
known_failure: STALE_DATASET_CARD

Treat these as validation or review blockers when generating public repository changes from private research tasks.
