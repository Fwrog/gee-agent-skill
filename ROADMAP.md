# Roadmap

This roadmap keeps `gee-agent-skill` focused as an agent-native Google Earth Engine harness. Hong Kong NDVI stays as golden regression evidence; the broader goal is a reusable interface for reviewable, RAG-grounded, validated, and traceable Earth Engine workflows.

## Near Term

- Promote the canonical command surface: `auth / catalog / aoi / recipe / plan / render / validate / preflight / run / exports / trace / eval`.
- Keep every agent-facing command JSON-first and suitable for deterministic orchestration.
- Expand recipe-specific preflight adapters for NDWI, NDBI, Landsat LST, Sentinel-1 flood/change, and zonal statistics.
- Convert more dataset, operator, recipe, and failure cards into structured registry metadata.
- Add tests that prove non-golden workflows stop at context review unless AOI, export, and dataset choices are reviewed.

## Research And Evaluation

- Grow the benchmark suite from parse/render/validate checks into mocked preflight, trace inspection, and optional live smoke checks.
- Track retrieval coverage for each task: dataset evidence, operator evidence, export evidence, and failure evidence.
- Add paper-linked GEE repositories as metadata-only corpus candidates until license review is complete.
- Compare generated plans against high-quality community and published-workflow patterns without copying third-party code.

## Productization

- Keep beginner setup docs current for Windows PowerShell, macOS zsh, and Linux shells.
- Publish concise release notes for each capability milestone.
- Add demo GIFs or short videos for the plan-review-preflight-export loop.
- Maintain issue templates for bug reports, workflow requests, and good first issues.
- Preserve credential hygiene in traces, docs, examples, and packaging.

## Not Yet Claimed

- Universal Earth Engine automation.
- Live export support for every recipe family.
- Scientific validity for every generated output.
- Credential provisioning or Google Cloud project setup.
