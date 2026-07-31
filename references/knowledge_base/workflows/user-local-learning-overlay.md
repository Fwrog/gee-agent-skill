# User-Local Learning Overlay

source_id: workflow-user-local-learning-overlay
source_type: repository-governance
primary_status: curated
last_checked: 2026-07-31
risk_level: high

## Goal

Let the public GEE Skill and a user-owned learning Skill evolve without sharing
private state or silently changing each other.

```text
user-owned Obsidian notes
  -> reproduce and review locally
  -> explicit public-safe candidate manifest
  -> official manifest review
  -> independent source and regression review
  -> versioned public knowledge release
```

The public repository is authoritative only for its released knowledge, rules,
schemas, and regressions. The user remains authoritative for the private vault,
local configuration, personal rules, and project-specific evidence.

## Real-Project Failure Mainline

1. Preserve the original failure evidence only in its authorized project workspace.
2. Separate directly observed behavior from inference, hypothesis, and proposed repair.
3. Reduce the failure to the smallest generic mechanism that can be reproduced without private inputs.
4. Classify the missed knowledge:
   - important when it can change correctness, authorization, data integrity, reproducibility, or a scientific claim;
   - general when it mainly improves discovery, explanation, or ergonomics.
5. Apply the public ignorance boundary before handoff. Remove project names, locations, asset and task IDs, bucket/object names, revealing filenames, unpublished parameters or metrics, screenshots, credentials, and private links.
6. Check the generic mechanism against current official Earth Engine sources and, when useful, reviewed papers or repositories.
7. For important knowledge, name one public rule, failure card, data contract, planner/validator implication, or claim boundary and one focused regression.
8. Keep general knowledge in the private or non-blocking observation layer unless a later reproduced failure changes its classification.
9. Rebuild the index and graph, then rerun the mistake, retrieval, privacy, test, and release gates.

The public record links to the generic regression and lesson, never to the
private evidence. A successful local repair proves only the bounded mechanism
reproduced by that regression; it does not transfer project results or
scientific validity.

## Layer Contract

| Layer | May contain | Must not do |
| --- | --- | --- |
| Official GEE Skill | Public sources, reviewed patterns, rules, schemas, and regressions | Read a private vault, infer omitted context, or overwrite a user Skill |
| User learning Skill | Private evidence references, local project aliases, personal notes, and unverified mistakes | Present local notes as official knowledge or write directly into the official corpus |
| Candidate manifest | Sanitized summaries, portable target IDs, regression IDs, and explicit unknowns | Carry raw evidence, note bodies, project aliases, local paths, credentials, or private asset IDs |

There is no automatic synchronization. A user may adopt an official release
without deleting personal notes, and may keep local rules that are not suitable
for public promotion.

## Public-Safe Handoff

The transport schema is
[`schemas/mistake-promotion-manifest-v0.1.schema.json`](../../../schemas/mistake-promotion-manifest-v0.1.schema.json).
Inspect the contract and review a candidate with:

```bash
gee-skill learning contract --json
gee-skill learning review-manifest <promotion-manifest.json> --json
```

The review enforces a strict field allowlist, portable target identifiers, an
explicit ignorance boundary, and checks for private- or secret-looking content.
It never reads the source vault and never modifies the official knowledge base.

Every target uses `<kind>:<portable-id>`. Supported kinds are `dataset`,
`evidence`, `eval`, `failure`, `operator`, `rule`, `skill`, and `workflow`.

## Official Promotion Gate

`candidate_review_ready` means only that the package can enter maintainer
review. It is not an evidence grade or approval.

For each item, maintainers must:

1. separate observed facts from inference and reproduce the failure and correction in a controlled target-repository case;
2. verify current Earth Engine and dataset facts against official sources;
3. check the public summary and the omitted or unverified details;
4. map the lesson to an official rule, evidence card, workflow, validator, or
   evaluation case;
5. add or update the named regression and demonstrate the failure-before,
   pass-after behavior;
6. run the relevant benchmark, privacy, index, graph, test, and release gates;
7. approve the change through the repository's normal versioned release.

If official evidence conflicts with the local lesson, reject or narrow the
candidate. Do not lower source precedence to preserve a user note.

## Public Ignorance Boundary

The candidate manifest excludes the project alias, raw evidence references, and
note body by contract. For `pattern_only` items, `omitted_or_unverified` must be
non-empty. Reviewers must not reconstruct those details from filenames,
repository history, geographic hints, issue context, or neighboring artifacts.

The validator detects several high-risk identifier and secret patterns, but a
passing scan is not proof of complete anonymization. Human privacy and license
review remains part of promotion.

## Non-Claims

- Local capture is not reproduction.
- Local approval is not official approval.
- A structurally valid manifest is not scientific evidence.
- A regression demonstrates the bounded behavior it tests, not general
  scientific validity.
- Updating the official Skill does not update or erase the user's local Skill.
