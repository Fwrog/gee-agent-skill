# TODO

This file is the short public task entry point. The detailed roadmap and board process live in [docs/roadmap.md](docs/roadmap.md) and [docs/project_board.md](docs/project_board.md).

## Current Focus

- [x] Finish v0.3 annual GeoTIFF evidence: monitor Earth Engine tile exports, read completed files back from Google Drive, run local raster QA, and rerun the readiness audit.
- [x] Promote v0.3 to `Golden` after task completion, Drive readback, figure/report QA, and readiness audit passed.
- [ ] Turn the reusable HLS/MODIS lessons into generic v0.4 `product_intercomparison` planning, validation, and recipe support.
- [ ] Run final release hygiene before PR/merge: full pytest, CLI smoke/eval, privacy scan, and `git diff --check`.
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
