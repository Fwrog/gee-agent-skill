# Core Guide: Scale, Projection, and CRS

source_id: core-scale-projection-crs
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/scale
last_checked: 2026-06-21
risk_level: medium

## Use

Earth Engine reducers and exports need explicit spatial scale for reproducibility. A dataset's native projection may differ from the requested output CRS; generated scripts should record `scale`, `crs`, reducer strategy, and any `bestEffort` or `tileScale` use.

## Operator Notes

- Pass `scale` to `reduceRegion`, `reduceRegions`, and table/image exports.
- Pass `crs` when cross-region reproducibility matters.
- Use `tileScale` to reduce memory pressure for large reducers.
- Use `bestEffort` only when acceptable and document the tradeoff.

## Failure Cases

known_failure: REDUCER_SCALE_ERROR

Typical symptoms include too many pixels, memory errors, null results from mismatched scale, or slow tasks. Recovery: coarsen scale, split AOI, increase `tileScale`, or use explicit projection.
