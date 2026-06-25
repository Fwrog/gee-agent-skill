# Trace Summary

Workflow: `hk_2024_01_ndvi_landcover_v02`

Status: golden example, live export completed.

The trace demonstrates the land-cover-aware harness path:

1. User request is mapped to a reviewable task plan.
2. Sentinel-2 SR Harmonized provides NDVI inputs.
3. Dynamic World provides time-matched probabilistic interpretation masks.
4. Validation checks export selectors, threshold fields, dataset IDs, and required bands.
5. Preflight verifies collections and export metadata before live run.
6. Export is gated behind explicit live confirmation.
7. Export task metadata is monitored and redacted for public evidence.

Redactions:

- Google Cloud project id
- Earth Engine task id
- local repository path
- any credential or token material

Limitations:

- Land-cover strata are probabilistic and require domain review.
- The workflow distinguishes all-surface, non-water, land-only, and vegetation-like outputs, but it is still a demo/regression artifact.
- Completion of an Earth Engine export is not a peer-reviewed scientific result.
