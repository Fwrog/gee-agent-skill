# Operator Cards: Core Earth Engine Workflow Operators

source_id: operators-core-gee-workflows
source_type: operator-catalog
publisher: gee-agent-skill
source_url: https://developers.google.com/earth-engine/guides/client_server; https://developers.google.com/earth-engine/guides/ic_filtering; https://developers.google.com/earth-engine/guides/reducers_intro; https://developers.google.com/earth-engine/guides/exporting
last_checked: 2026-06-24
primary_status: derived-from-official-docs
risk_level: medium
operator_chain: filterDate -> filterBounds -> map -> mask -> index/expression -> reduceRegion/reduceRegions -> Export -> task monitoring

## Scope

These operator cards define recurring Earth Engine workflow pieces used by the v0.3 planner, validators, preflight checks, and recipe templates.

## filterDate

Use `ImageCollection.filterDate(start, end)` before expensive maps, reducers, or exports. Plans must expose `date_start` and `date_end` explicitly.

Validation implication: generated scripts should contain a date filter for image collections unless the dataset is static.

## filterBounds

Use `filterBounds(aoi)` or an equivalent geometry filter before collection reduction. AOI must be explicit and reviewable.

Validation implication: scripts should not process global collections when the task asks for an AOI-specific result.

## map

Use server-side `.map(function)` for image-level masking, scaling, and band derivation. Avoid client-side loops over large server collections.

Validation implication: repeated temporal products should stay server-side until export or bounded preflight probes.

## normalizedDifference

Use `image.normalizedDifference([band_a, band_b]).rename(index_name)` for two-band normalized indices such as NDVI, NDWI, MNDWI, and NDBI. Band order matters.

Validation implication: recipe-specific semantic checks must verify required bands and expected band order.

## expression

Use `image.expression(...)` for formulas such as EVI or custom indices where `normalizedDifference` is insufficient. Bind all input bands explicitly.

Validation implication: formulas must not hide dataset-specific scale or band assumptions.

## reduceRegion

Use `reduceRegion` for whole-AOI or single-geometry summary statistics. Always review `geometry`, `scale`, `crs` or projection, `bestEffort`, `tileScale`, and `maxPixels`.

Validation implication: reducers without explicit geometry or scale should be blocked before live export.

## reduceRegions

Use `reduceRegions` for zonal statistics over feature collections. Review zone IDs, output selectors, scale, and geometry complexity.

Validation implication: table exports should preserve stable selectors and include a zone identifier.

## reducers

Choose reducers that match the scientific question: mean for averages, sum/area for class area, count for image/pixel diagnostics, and grouped reducers only when output schema is reviewed.

Validation implication: reducer choice should be visible in the plan and trace.

## joins

Use joins for paired optical products, time-matched land-cover masks, or before/after relationships. Review temporal tolerance and missing-match behavior.

Validation implication: join workflows must guard against missing paired images or null properties.

## masks

Apply dataset-specific QA/cloud masks before index computation, compositing, reducers, or export. Do not reuse optical cloud masks for SAR.

Validation implication: required QA bands and masking policy should be part of recipe validation and live preflight.

## projections

Earth Engine images can carry different native projections. Export and reducer plans should state the intended CRS/projection or justify native projection use.

Validation implication: silently relying on default projection is risky for reproducibility.

## scale

Scale controls reducer and export sampling. Use dataset-appropriate scale and estimate pixel count during preflight when possible.

Validation implication: missing or unrealistic scale should block live execution.

## tileScale

Use `tileScale` as a quota/memory mitigation for reducers, not as a scientific parameter. Record it in trace artifacts when used.

Validation implication: memory errors can suggest `tileScale` review, but should not bypass AOI/scale sanity checks.

## Export.image.toDrive

Use for GeoTIFF/image products with explicit `image`, `description`, `folder`, `fileNamePrefix`, `region`, `scale`, `crs` when relevant, `fileFormat`, and `maxPixels`.

Validation implication: image export requires reviewed region and metadata. Preflight must never call `task.start()`.

## Export.table.toDrive

Use for CSV/table products with explicit `collection`, `description`, `folder`, `fileNamePrefix`, `fileFormat`, and `selectors`.

Validation implication: table export requires stable selectors and monitored task state.

## Task Monitoring

After a confirmed export, monitor task id, description, state, timestamps, and error messages. Task submission is workflow evidence, not proof of scientific correctness.

Validation implication: final reports should distinguish submitted, running, completed, failed, and output-inspected states.

## Client/Server And getInfo Pitfalls

Earth Engine objects are server-side and lazily evaluated. `getInfo()` blocks and should be avoided on large collections or images. Use exports for large computations and only bounded `getInfo()` probes for preflight diagnostics.

Validation implication: unsafe large `getInfo()` calls should be blocked; small scalar preflight probes must be documented.
