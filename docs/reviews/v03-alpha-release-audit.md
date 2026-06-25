# v0.3-alpha Release Audit

Date: 2026-06-25

Scope: final release-polish and overclaim audit after reframing `gee-agent-skill` as a general, agent-native Google Earth Engine harness.

## Summary

The repository now reads as a harness-first project. Hong Kong NDVI appears as golden example evidence and regression coverage, not as the whole product. Public docs distinguish live verified, render/validate, mocked preflight, plan-only, and planned workflow surfaces.

No live export was submitted during this release-polish audit.

## Test Result

Command:

```bash
python -m pytest
```

Result:

```text
117 passed
```

## Benchmark Result

Command:

```bash
gee-skill eval evals/benchmark_suite.yml --json
```

Result:

```text
22 passed / 22 total
0 failed
```

Benchmark coverage includes retrieval/evidence checks, EVI, NDWI, NDBI, Landsat LST, Sentinel-1 flood/change, Dynamic World summary, zonal statistics, standalone image export planning, ambiguous requests, unsupported requests, mocked preflight blockers, and golden render/validate cases.

## Smoke And CLI Result

Passed:

```bash
gee-skill smoke-test --json
gee-skill info --json
gee-skill recipe list --json
gee-skill catalog evidence --category dataset --json
gee-skill catalog evidence --category operator --json
gee-skill catalog evidence --category failure --json
```

The local `.venv` initially had macOS hidden file flags on editable-install metadata, causing `gee-skill` to fail with `ModuleNotFoundError: No module named 'geeskill'`. Clearing the hidden flags on the virtual environment restored normal `.pth` processing. This was an environment metadata issue, not a repository packaging issue.

## Build Result

Command:

```bash
python -m build --sdist --wheel
```

Result:

```text
Successfully built gee_agent_skill-0.3.0.tar.gz and gee_agent_skill-0.3.0-py3-none-any.whl
```

Generated `build/`, `dist/`, `outputs/`, and `src/gee_agent_skill.egg-info/` artifacts were removed after verification because they are local build/evaluation outputs and should not be committed.

## Wheel Smoke Result

A clean temporary venv under `/private/tmp` installed the built wheel and passed:

```bash
gee-skill info --json
gee-skill recipe list --json
gee-skill catalog evidence --category dataset --json
gee-skill plan from-text "Compute January 2024 mean NDVI for Hong Kong and export CSV." --json
```

The wheel resolved packaged index, recipe, template, boundary, and task resources from `site-packages/geeskill/resources`.

## Secret Scan Result

Credential scan excluded `.git`, `.venv`, `build`, `dist`, caches, and temporary wheel-smoke directories.

The scan checked for private key blocks, OAuth access-token patterns, Google API key patterns, service-account private key JSON, refresh-token fields, client-secret fields, service-account email identifiers, application-default credential paths, and Earth Engine credential paths.

Result:

```text
No real credentials found.
```

One earlier hit was `.gitignore` intentionally ignoring the standard Google application-default credential JSON filename; it is not a credential.

## Overclaim Audit Result

Created [overclaim-audit.md](overclaim-audit.md).

Actions taken:

- softened "full harness" to "core architecture";
- changed "Supported recipe families" to "Recipe families";
- narrowed headline live-preflight language to golden live preflight checks;
- removed stale "non-demo" wording from v0.3 docs;
- replaced stale v0.1 district-monthly v0.2 planning text with a future-extension boundary;
- added a capability matrix with explicit status columns.

## Live Verified Examples

Live-verified claims are limited to workflows marked completed in [Capability matrix](../capability_matrix.md):

- HK Jan 2024 NDVI CSV;
- HK Jan 2024 land-cover-aware NDVI CSV;
- HK 2024 16-day NDVI CSV.

These are workflow proofs and regression evidence. They are not scientific validation of vegetation condition.

## Dry-Run / Render-Validate Examples

Non-golden workflows remain below live-verified status:

- EVI CSV: plan/render/validate;
- NDWI GeoTIFF: plan/render/validate plus placeholder-context preflight blocking;
- NDBI CSV: plan/render/validate plus placeholder-context preflight blocking;
- Landsat LST CSV/image: plan/render/validate plus placeholder-context preflight blocking;
- Sentinel-1 flood/change GeoTIFF: plan/render/validate plus placeholder-context preflight blocking;
- Dynamic World summary CSV: plan/render/validate;
- generic zonal statistics and standalone image/table exports: partial planning/template utility coverage, not live verified.

## Remaining Limitations

- The deterministic parser is not full natural-language understanding.
- The local knowledge base is distilled guidance and does not replace current official Earth Engine documentation.
- Non-golden workflows need recipe-specific live preflight adapters, domain review, and live evidence before promotion.
- Export completion is not scientific validation.
- Users must bring their own Earth Engine account, Google Cloud Project, OAuth authentication, quota, and export destination.
- Public CI should avoid live Earth Engine execution and should not require private credentials.

## Release Decision

The v0.3-alpha release candidate is suitable for GitHub publication as a portfolio-grade, research-grounded agent-native GEE harness, with the capability matrix preserving honest boundaries.
