# Benchmark Protocol

This protocol checks public harness behavior, not scientific validity.

## Offline Checks

```bash
gee-skill smoke-test --json
gee-skill eval evals/benchmark_suite.yml --json
python -m pytest -q
```

The benchmark suite covers:

- dataset/operator/failure retrieval;
- plan generation for NDWI, EVI, NDBI, LST, Sentinel-1 change, Dynamic World, zonal statistics, and export utilities;
- ambiguous prompt handling;
- unsupported task handling;
- render/validate for approved public templates;
- placeholder-context preflight blocking.

## Plan/Render Spot Check

Use a reviewed or placeholder-supplied AOI depending on whether live preflight is expected:

```bash
gee-skill plan from-text "Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF." \
  --out outputs/plans/ndwi_supplied_aoi.yaml \
  --json

gee-skill render outputs/plans/ndwi_supplied_aoi.yaml \
  --script-out outputs/scripts/ndwi_supplied_aoi.py \
  --json

gee-skill validate outputs/scripts/ndwi_supplied_aoi.py --json
```

With a placeholder AOI, preflight should block rather than export:

```bash
gee-skill preflight-plan outputs/plans/ndwi_supplied_aoi.yaml --project "$EE_PROJECT" --json
```

## Claims

- Passing benchmark cases supports harness behavior.
- Passing render/validate supports local script generation only.
- Passing mocked or blocking preflight supports safety behavior only.
- Live verification requires explicit confirmed export and observed task completion for a public workflow listed in `docs/capability_matrix.md`.
- Private academic demos are not benchmark evidence for the public repository.
