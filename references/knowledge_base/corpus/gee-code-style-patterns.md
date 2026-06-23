# Corpus Card: GEE Code Style Patterns

source_id: corpus-gee-code-style-patterns
source_type: curated-corpus-distillation
primary_status: curated
source_url: references/corpus/github_gee_seed_repos.yml
last_checked: 2026-06-23
method_name: ee.Initialize, ee.ImageCollection, filterDate, filterBounds, updateMask, reduceRegion, reduceRegions, Export.image.toDrive, Export.table.toDrive, Task.start, getInfo
operator_chain: corpus sample -> pattern counts -> harness comparison -> ruleset update
risk_level: medium

## Sampled Sources

This card distills pattern-only observations from local read-only samples of:

- `google/earthengine-api`: official API bindings and demos.
- `google/earthengine-community`: official community tutorials.
- `gee-community/geemap`: maintained Python package, docs, and notebooks.
- `awesome-spectral-indices/spectral`: Earth Engine spectral-index JavaScript package.
- `gee-community/geetools`: maintained Earth Engine utility package.
- `giswqs/earthengine-py-notebooks`: large Python notebook example collection.
- `davemlz/eemont`: Python extension patterns for indices and cloud masks.
- `google/Xee`: official xarray extension for Earth Engine data cubes.

No third-party code is copied into this repository. The learned output is limited to operator names, recurring workflow structure, and validation implications.

## Current 8-Source Exam Snapshot

The latest local audit scanned 1462 text files under `/tmp/gee-corpus-sample` and found broad evidence for:

- collection filters: 2880 hits across 511 files;
- quality masking: 5026 hits across 693 files;
- reducers: 362 hits across 99 files;
- exports: 76 hits across 22 files;
- scale, CRS, projection, or pixel-budget controls: 3527 hits across 349 files;
- client fetch calls: 1292 hits across 361 files.

The style exam had evidence for all tracked signals: explicit temporal scope, explicit spatial scope, quality masking before metrics, server-side mapping, explicit scale/projection review, reviewable export contracts, bounded client fetches, and guarded entrypoints.

## Observed Pattern Groups

Across the sampled sources, the recurring GEE structure is:

1. Authentication and initialization are environment-level concerns.
2. Collections are normally filtered by date and AOI before expensive work.
3. Optical workflows use quality masks before index/composite/reducer work.
4. Index workflows use `normalizedDifference` for simple normalized differences and `expression` for coefficient formulas.
5. Reducer workflows need explicit scale, CRS/projection review, and pixel-budget parameters.
6. Exports need stable descriptions, region/schema, max pixel budget, task start, and task monitoring.
7. Joins and quality mosaics are common in cloud/shadow, temporal pairing, and composite workflows.
8. `getInfo()` appears in tutorials and UI utilities, but agent-generated production scripts should keep it out of large workflow paths and use bounded preflight/debug probes instead.

## Rule Implications

The corpus sample promotes a separate `agent_script_contract` ruleset:

- No inline `ee.Authenticate()` in generated scripts.
- Prefer runtime/CLI initialization over inline `ee.Initialize()`.
- Expose date windows, dataset IDs, scale, CRS, export description, and max pixel budget as constants.
- Put `task.start()` behind a guarded `main()` entrypoint.
- Treat `getInfo()` as a warning unless it is part of bounded preflight/debug logic.
- Keep export task submission separate from completion claims; monitor task state in trace artifacts.

## Harness Gaps To Keep Testing

known_failure: UNVERIFIED_CORPUS_PATTERN

The current harness is stronger than many tutorial snippets on traceability, confirmation gates, and deterministic JSON errors. It is still weaker than a large corpus on breadth. The broad discovery inventory now tracks 125 metadata-only candidates, while deeper code-style exams should continue to compare coverage across task families:

- optical index;
- water and built-up indices;
- land surface temperature;
- Sentinel-1 flood/change;
- land cover and Dynamic World;
- joins and temporal pairing;
- exports and task monitoring;
- map previews and UI-only examples.

The next audit round should add a paper-linked sample set from remote-sensing publications and compare it against the community/tutorial sample. Treat peer-reviewed provenance as a quality signal, not as permission to copy code or skip live preflight. Promote only patterns that agree with official Earth Engine semantics and improve the current rule set.
