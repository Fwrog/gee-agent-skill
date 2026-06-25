# Trace Summary

Workflow: `hk_2024_01_ndvi_v01`

Status: golden example, live export completed.

The trace demonstrates the minimal harness path:

1. User request is mapped to a reviewable task plan.
2. Sentinel-2 SR Harmonized is selected for NDVI.
3. Required bands and export metadata are checked.
4. Export is gated behind explicit live confirmation.
5. Export task metadata is monitored and redacted for public evidence.

Redactions:

- Google Cloud project id
- Earth Engine task id
- local repository path
- any credential or token material

Limitations:

- The result is a whole-AOI engineering demo and includes water and built-up surfaces.
- No independent scientific validation is included.
- Completion of an Earth Engine export is not the same as peer-reviewed remote-sensing interpretation.
