# TODO

This file is the short public task entry point. The detailed roadmap and board process live in [docs/roadmap.md](docs/roadmap.md) and [docs/project_board.md](docs/project_board.md).

## Current Focus

- [x] Finish v0.3 annual GeoTIFF evidence: monitor Earth Engine tile exports, read completed files back from Google Drive, run local raster QA, and rerun the readiness audit.
- [x] Promote v0.3 to `Golden` after task completion, Drive readback, figure/report QA, and readiness audit passed.
- [x] Turn the reusable HLS/MODIS lessons into generic v0.4 `product_intercomparison` planning, validation, and recipe support.
- [x] Expand the GitHub/paper-hint discovery queue to 200 quality-screened, metadata-only candidates with explicit data-use review fields.
- [x] Add a reproducible mistake-distillation lab that separates important omissions from general knowledge and routes important misses into rules or regression cases.
- [x] Add a public contract between the versioned official knowledge base and user-owned Obsidian Skills, including sanitized candidate export and read-only review.
- [x] Reproduce and fix the privacy-gate failure caused by Git-listed files already deleted from the worktree.
- [x] Deep-review the first bounded batch: 21 of 200 discovery records plus 3 anchors, including 9 verified project-paper pairs and explicit non-promotion decisions.
- [ ] Review the next bounded batch from the remaining 179; do not promote search-lane hints without DOI, license, revision, data-contract, and reproducibility checks.
- [x] Run final release hygiene before PR/merge: full pytest, CLI smoke/eval, privacy scan, package build, and `git diff --check`.
- [ ] Keep private research tasks, unpublished results, local asset ids, and private Drive links out of public issues and docs.

## Project Board Flow

Use the lightweight GitHub board described in [docs/project_board.md](docs/project_board.md):

| Column | Purpose |
| --- | --- |
| Inbox | Raw ideas, user requests, dataset changes, or failure reports. |
| Ready | Scoped public tasks with acceptance checks and claim boundaries. |
| Now | Active work; keep this column short. |
| Review | PR exists; docs, tests, privacy, and evidence are under review. |
| Done | Merged or intentionally closed with an evidence note. |

## Issue Templates

- Use `Roadmap task` for TODO items that already belong to a roadmap track.
- Use `Workflow request` for new GEE recipes, datasets, validators, or live-export support.
- Use `Good first issue` for small docs, test, card, or fixture tasks.
- Use `Bug report` only when there is a reproducible command, trace, or failing check.

Every public task should state what it can support, what it must not claim, and which evidence would promote it to `Golden`.
