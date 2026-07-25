# Dataset Card: External Annual Categorical Land Cover

source_id: dataset-external-annual-categorical-landcover
source_type: external-asset-contract
primary_status: user-supplied
dataset_id: external/annual-categorical-landcover
title: External annual categorical land-cover asset
provider: User-supplied; record the actual producer in the private study manifest
gee_url: https://developers.google.com/earth-engine/guides/manage_assets
source_url: https://developers.google.com/earth-engine/guides/manage_assets
temporal_coverage: User-declared expected years; verify every year against live asset metadata
spatial_resolution: Product-specific; record native grid and pixel size
bands: User-declared categorical class band
qa_bands: Product-specific
common_uses: stable endpoint selection, annual class fractions, land-mix diagnostics, change detection
recommended_tasks: annual_endmember_transition, landcover_summary, change_detection
scale_notes: Never bilinearly resample class codes; aggregate reviewed binary class masks to area fractions or use nearest-neighbour semantics.
projection_notes: Preserve the native categorical grid until class masks are constructed, then align derived fractions to one explicit target grid.
license_attribution: Product-specific; record and enforce source license, citation, and redistribution restrictions.
last_checked: 2026-07-25
risk_level: high

## Required Manifest

Record source, version, license, expected years, asset band, class map, native grid, checksum or asset manifest, access scope, and aggregation semantics.

## Privacy and Export Boundary

Keep real private asset IDs outside public cards and examples. Export only derived outputs unless the source license and asset owner explicitly authorize redistribution.
