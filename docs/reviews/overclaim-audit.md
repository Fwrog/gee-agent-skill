# Overclaim Audit

Date: 2026-06-25

Scope: `README.md`, `SKILL.md`, `docs/`, `examples/`, and source comments/docstrings where they affect public claims.

Search pattern used:

```bash
rg -n -i "\b(supports|supported|general|verified|live|completed|automatic|universal|production-ready|all|any|agent)\b" \
  README.md SKILL.md docs examples src \
  --glob '*.md' --glob '*.py' --glob '*.yaml' --glob '*.yml'
```

## Audit Results

| Claim / wording | Location | Action | Reason |
| --- | --- | --- | --- |
| "`gee-agent-skill` is an agent-native command-line harness..." | `README.md`, `SKILL.md`, research docs | Kept | The CLI contract, JSON envelopes, plan schema, validation, preflight gates, exports, traces, and eval commands support this positioning. |
| "full agent-native Earth Engine harness" | `README.md` | Softened to "core architecture of an agent-native Earth Engine harness" | "Full" implied broader live coverage than the capability matrix supports. |
| "Supported recipe families" | `README.md` | Softened to "Recipe families" | Registry/render coverage is not the same as live workflow support. |
| "live preflight checks" in the headline capability quote | `README.md` | Softened to "golden live preflight checks" | Live preflight is verified for golden paths, not every recipe family. |
| "non-demo Google Earth Engine workflow" | `docs/v03_hk_2024_16day_ndvi.md` | Removed | Hong Kong 16-day NDVI is a golden example and demo/proof workflow, not the whole product. |
| "main product path" | `docs/v01_hk_january_ndvi.md` | Softened to "main harness path" | The project is the harness, not a single NDVI product. |
| "Full 2024 monthly district-level NDVI is planned for v0.2" | `docs/v01_hk_january_ndvi.md` | Removed and replaced with a future-extension note | This was stale after the v0.2 land-cover-aware path. |
| "Live export verified" | `docs/recipes.md`, `docs/capability_matrix.md`, release notes | Kept with matrix boundary | The phrase is allowed only where the workflow is marked live export completed. |
| "Non-golden recipe families can produce reviewable plans and validated scripts" | `README.md`, docs | Kept | Tests and benchmark coverage support plan/render/validate for listed non-golden paths. |
| "generic preflight gate blocks placeholder context" | `README.md`, release docs | Kept | Mocked/placeholder preflight blockers are tested and explicitly not described as live export readiness. |
| "universal Earth Engine task automation" | review docs | Kept only as a negative claim | The docs explicitly say the project does not prove universal support. |
| "production-ready" | release/review docs | Kept only as a negative or future-readiness warning | No public claim states the project is production-ready for all GEE workflows. |
| "completed" export | golden evidence and capability matrix | Kept with redaction and scientific limitation | Completed task metadata is workflow evidence, not scientific validation. |
| "all-surface" | demo docs | Kept | It is a scientific limitation note, not a broad support claim. |

## Final Claim Policy

Use these labels:

- **Live export completed**: only for workflows marked completed in `docs/capability_matrix.md`.
- **Live preflight**: only when a workflow has a live adapter and observed preflight evidence.
- **Mocked preflight**: for safety-blocking tests or placeholder-context gates that do not prove live readiness.
- **Render/validate**: for workflows that produce scripts and pass static/semantic checks but have no live export evidence.
- **Plan-only**: for workflows with parser/plan coverage but no approved render path.
- **Planned**: for roadmap work only.
- **Experimental**: for exploratory paths that are not yet benchmarked or live verified.

## Remaining Limitations To Preserve

- The deterministic parser is not full natural-language understanding.
- The knowledge base is distilled guidance and does not replace official Earth Engine documentation.
- Live verification is limited to golden examples.
- Non-golden workflows need recipe-specific preflight, domain review, and live evidence before promotion.
- Export completion is not scientific validation.
- Users must provide their own Earth Engine account, Google Cloud Project, OAuth authentication, quota, and export destination.

## Result

The release-facing docs now frame the project as a general agent-native GEE harness while keeping Hong Kong NDVI as golden evidence. Public docs distinguish live verified, dry-run verified, render/validate, mocked preflight, planned, and experimental surfaces.
