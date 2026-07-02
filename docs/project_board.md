# Project Board Guide

This guide explains how to run `gee-agent-skill` like a maintained open-source project instead of a loose collection of demos. The roadmap tracks what exists; this guide explains how to turn that work into issues, reviews, releases, and evidence.

## 🧭 Board Columns

Use a small GitHub Projects board. Keep the board practical and evidence-driven.

| Column | Meaning | Exit rule |
| --- | --- | --- |
| Inbox | Raw ideas, user requests, dataset changes, or failure reports. | Scope is clear enough for a single issue. |
| Ready | Public, generic task with acceptance checks and claim boundary. | Someone starts implementation. |
| Now | Active work. Keep this short. | PR opened, blocked, or closed. |
| Review | PR exists; docs, tests, privacy, and evidence are under review. | Checks pass and reviewer concerns are addressed. |
| Done | Merged or intentionally closed with a short evidence note. | No hidden follow-up is required. |

Avoid putting private research goals, unpublished conclusions, local asset ids, credentials, or private Drive links on the public board.

## 🏷️ Labels

Suggested labels are listed below and mirrored in `.github/labels.yml` so they can be applied manually or synced with a label-management tool.

| Label | Use for |
| --- | --- |
| `roadmap` | Work that appears in `docs/roadmap.md`. |
| `workflow` | New Earth Engine workflows, recipes, templates, or validators. |
| `validation` | Product checks, metrics, reports, and evidence bundles. |
| `knowledge-base` | Dataset cards, rule cards, failure cases, or workflow cards. |
| `remote-sensing` | Domain-specific QA, scaling, masking, projections, or interpretation. |
| `docs` | README, guides, examples, release notes, or diagrams. |
| `tests` | Unit, semantic, fixture, contract, or status-consistency tests. |
| `good first issue` | Small tasks with clear acceptance checks. |
| `blocked` | Waiting on credentials, quota, external tasks, upstream data, or user input. |
| `privacy-review` | Needs a scan for private paths, asset ids, unpublished content, or sensitive links. |

## ✅ Issue Quality Bar

Every public issue should answer four questions:

- What reusable capability does this add?
- What evidence or source backs the change?
- What tests, docs, or validation outputs prove it works?
- What must this issue not claim after completion?

Use `.github/ISSUE_TEMPLATE/roadmap_task.md` for scoped TODO items and `.github/ISSUE_TEMPLATE/workflow_request.md` for new Earth Engine workflows.

## 🧾 From TODO To Issue

Use [../TODO.md](../TODO.md) as the short task list for people scanning the repository root. When an item becomes actionable, convert it into an issue with:

- one roadmap track;
- one evidence level;
- concrete acceptance checks;
- a claim boundary;
- links to the relevant report, trace, card, or script.

Keep large research goals out of a single issue. Split them into reviewable tasks such as `dataset card`, `validator`, `export fallback`, `Drive readback`, `figure QA`, and `documentation status update`.

## 🚦 Demo Promotion

Use these status labels consistently:

| Status | Meaning |
| --- | --- |
| `Planned` | Scoped idea; no implementation yet. |
| `Implementation-ready` | Code and docs are ready for live evidence. |
| `Partial` | A real loop completed, but at least one required artifact or QA step is missing. |
| `Golden` | Live task evidence, Drive readback, analysis, docs, tests, and claim boundaries all pass. |
| `Blocked` | Cannot proceed until an external condition changes. |

A demo cannot become `Golden` just because the script exists. It needs observed exports, connector readback, reproducible analysis, documented limitations, and passing tests.

## 🔁 Weekly Triage

A lightweight triage loop is enough:

- Move completed work from `Now` or `Review` to `Done`.
- Split vague items into smaller `Ready` issues.
- Check whether any `Blocked` task has new evidence.
- Verify that README, capability matrix, roadmap, and validation docs still agree on demo status.
- Promote only generic, source-backed lessons into the knowledge base.
- Run a privacy scan before public docs mention a new workflow, result, or artifact.

## 🧪 Current Focus

The current high-priority public track has moved from v0.3 evidence collection to v0.4 generalization:

- keep v0.3 preserved as `Golden` product-intercomparison evidence;
- run release hygiene before PR/merge: tests, CLI smoke/eval, privacy scan, and diff checks;
- turn reusable HLS/MODIS lessons into generic v0.4 validators, recipes, and knowledge cards;
- split product-intercomparison follow-ups into small issues with explicit claim boundaries.

The canonical TODO list remains [Roadmap and TODO](roadmap.md).
