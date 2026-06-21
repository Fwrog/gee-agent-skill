# Failure Case: Empty Collections and Images With No Bands

source_id: failure-empty-collection-no-bands
source_type: curated-failure-case
primary_status: curated
source_url: https://developers.google.com/earth-engine/guides/debugging
last_checked: 2026-06-21
known_failure: Image.reduceRegions Image has no bands
risk_level: high

## Symptoms

Errors such as `Image.reduceRegions: Image has no bands` often mean a filtered image collection became empty, a mapped band was never added, or a selected band was absent after masking/compositing.

## Required Gates

- AOI feature count and area are positive.
- Image collection count is positive before and after cloud metadata filtering.
- Expected source bands exist.
- Derived bands such as `NDVI` exist after mapping.
- Tiny reducer sanity statistics are non-null before export.

## Recovery

Return structured errors such as `EMPTY_AOI`, `EMPTY_S2_COLLECTION`, `EMPTY_DYNAMIC_WORLD_COLLECTION`, `NO_NDVI_BAND`, `NO_LANDCOVER_LABEL`, or `NO_PROBABILITY_BANDS` before creating a batch export task.
