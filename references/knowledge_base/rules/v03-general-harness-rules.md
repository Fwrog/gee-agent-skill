# Ruleset Card: v0.3 General Harness Rules

source_id: rules-v03-general-harness
source_type: curated-ruleset-card
primary_status: curated
source_url: docs/agent_goal.md; https://developers.google.com/earth-engine/guides/exporting; https://developers.google.com/earth-engine/apidocs/export-image-todrive; https://developers.google.com/earth-engine/apidocs/export-table-todrive
last_checked: 2026-07-01
ruleset_id: agent_script_contract, global_safety, optical_index, vegetation_index_ndvi, water_index_ndwi, builtup_index_ndbi, landsat_lst, sentinel1_flood_before_after, export_table_csv, export_image_geotiff, dynamic_world_landcover
method_name: geeskill.validation.validate_script, geeskill.semantic.validate_semantics
operator_chain: parse plan -> render script -> static validation -> semantic validation -> preflight -> confirmed export
risk_level: medium

## Global Safety

Every generated script must avoid unresolved template tokens, credential material, missing Earth Engine import, missing date filters, missing region filters, invalid scale, and accidental large `getInfo()` calls.

## Agent Script Contract

Corpus sampling from official and high-quality community examples showed recurring use of initialization, collection filters, masks, reducers, exports, task lifecycle calls, scale budgets, joins, and bounded client fetches. For agent-generated scripts this becomes a stricter contract:

- Do not call `ee.Authenticate()` inside generated scripts.
- Prefer CLI/runtime initialization over inline `ee.Initialize()`.
- Expose dates, dataset IDs, scale, CRS, and export description as constants.
- For CSV table exports, expose selectors so the schema is reviewable.
- For image exports, expose `maxPixels` or an equivalent max pixel budget.
- For image exports, cast or verify all exported bands have one numeric dtype before `Export.image.toDrive`.
- For live exports, smoke-test CRS/projection choices before scaling to multi-year or large-AOI batches.
- Put `task.start()` behind a guarded `main()` entrypoint.
- Treat `getInfo()` as a warning unless used in bounded preflight/debug probes.

The 8-source local corpus exam also promotes style signals into review expectations:

- Filter temporal and spatial scope before expensive `map`, reducer, or export work.
- Apply quality/cloud/water masks before interpreting index values.
- Use server-side date sequences or mapped collections for repeated cadences such as 16-day periods.
- Make scale, CRS/projection, `tileScale`, and `maxPixels` explicit when they affect cost or interpretation.
- Keep export contracts reviewable through descriptions, selectors, region, file format, and schema properties.
- Record live task id, description, output folder, source assets, CRS, scale, and terminal state before claiming completion.
- Validate boundary dataset field names and sample values before filtering by administrative names; if the boundary is a public substitute, block authoritative county-scale wording.
- Separate Browser/Computer Use observation from CLI/API execution and live task submission.

## Task Rules

- `agent_script_contract`: require generated-script structure and live-execution review surfaces.
- `vegetation_index_ndvi`: require NIR/red bands and NDVI output naming.
- `water_index_ndwi`: require green plus NIR/SWIR bands.
- `builtup_index_ndbi`: require SWIR plus NIR bands.
- `landsat_lst`: require `ST_B10`, Collection 2 scale/offset, and `QA_PIXEL`.
- `sentinel1_flood_before_after`: require Sentinel-1 GRD, IW mode, polarization, before/after windows, and change metric.
- `export_table_csv`: require table export, CSV format, description, and selectors.
- `export_image_geotiff`: require image export, GeoTIFF format, region, scale, and maxPixels.
- `dynamic_world_landcover`: require Dynamic World label/probability bands, probability threshold, and class fractions.

## Recovery

Return deterministic JSON errors with stable codes, categories, messages, and hints. Do not start live exports until validation and preflight pass and the user supplies explicit confirmation.
