# TRAE Skill Guidelines Applied

Version: 0.1.0

This repository applies these skill design rules:

- Keep `SKILL.md` concise and under 500 lines.
- Put detailed Earth Engine and dataset notes in `references/knowledge_base/`.
- Put deterministic reusable operations in `scripts/` and package modules.
- Put code generation templates in `assets/templates/`.
- Keep single responsibility: reproducible Earth Engine Python workflows.
- State input and output schemas.
- State failure handling for auth, quotas, empty collections, scale/projection, cloud masking, and exports.
- Use consistent terminology: AOI, collection, reducer, scale, CRS, export target, task.
- Avoid OS-specific paths in generated scripts.
- Avoid time-sensitive instructions unless source and retrieval date are recorded.
- Do not commit credentials.

