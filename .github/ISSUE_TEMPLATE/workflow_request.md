---
name: Workflow request
about: Request a new Earth Engine recipe, dataset, validator, or preflight adapter
title: "[Workflow]: "
labels: workflow
assignees: ""
---

## Geospatial task

Describe the Earth Engine workflow in plain language.

## Expected recipe status

- [ ] Plan only
- [ ] Render and validate
- [ ] Generic preflight gate
- [ ] Recipe-specific live preflight
- [ ] Live export verification
- [ ] Product/intercomparison validation

## Inputs

- AOI:
- Time range:
- Dataset:
- Output:

## Evidence to add

List dataset cards, operator cards, failure cards, paper/community sources, or official docs that should ground this workflow.

## Safety boundary

Live export support requires reviewed AOI/export context, passing preflight, explicit `--confirm-live`, monitored task state, and no credentials in traces.

## Claim boundary

- What this workflow can support:
- What this workflow must not claim:
- Which evidence would promote it to `Golden`:
