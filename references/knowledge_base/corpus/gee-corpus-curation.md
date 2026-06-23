# Corpus Card: GEE Syntax And Workflow Distillation

source_id: corpus-gee-syntax-workflow-distillation
source_type: curated-corpus-policy
primary_status: curated
source_url: references/corpus/github_gee_seed_repos.yml, references/corpus/github_gee_discovery_100.yml
last_checked: 2026-06-23
method_name: filterDate, filterBounds, map, normalizedDifference, expression, reduceRegion, reduceRegions, Export.image.toDrive, Export.table.toDrive
operator_chain: official docs -> curated source inventory -> pattern extraction -> distilled cards -> validation rules -> retrieval trace
risk_level: medium

## Source Tiers

Tier 1: official Google Earth Engine guides, API references, and data catalog pages. These sources define syntax, API behavior, authentication requirements, export semantics, and dataset metadata. Rules that can block live execution should be grounded in Tier 1 whenever possible.

Tier 2: established community packages, tutorials, and maintained example repositories. These sources are useful for recurring workflow patterns, task diversity, naming conventions, and practical edge cases. Priority curators include `giswqs`/OpenGeo and `gee-community` because they maintain Python-first GEE packages, notebooks, examples, and educational material with broad community review.

Tier 3: individual research or project repositories. These sources can reveal realistic task patterns but require license, provenance, freshness, and code-quality review before any pattern is promoted. Paper-linked repositories from remote-sensing venues are high-value Tier 3 candidates, but publication status does not bypass repository review.

Discovery tier: broad GitHub metadata candidates from `topic:google-earth-engine`. Discovery records are not reviewed sources. They are used to decide what to inspect next and to measure task-family coverage.

## Official Documentation Coverage

The corpus should continue expanding cards for:

- Python authentication and initialization.
- Client/server deferred execution and `getInfo()` pitfalls.
- ImageCollection filtering with `filterDate`, `filterBounds`, metadata filters, and joins.
- Image operators such as `normalizedDifference`, `expression`, masking, projection, and scale.
- Reducers including `reduceRegion` and `reduceRegions`.
- Batch exports for images and tables, task states, and monitoring.
- Dataset catalog cards for Sentinel-2, Landsat Collection 2, Sentinel-1, Dynamic World, WorldCover, MODIS LST, ERA5 Land, JRC Global Surface Water, and SRTM.

## GitHub Repository Sampling

Use `references/corpus/github_gee_seed_repos.yml` as the curated seed inventory. Sample 30 to 50 repositories across:

- Python API basics and notebooks.
- JavaScript Code Editor examples.
- Spectral indices.
- Sentinel-2 optical workflows.
- Landsat LST and time series.
- Sentinel-1 SAR flood mapping.
- Land-cover and Dynamic World workflows.
- LandTrendr and change detection.
- Export-heavy production workflows.
- Paper-linked research workflows from venues such as IEEE TGRS, ISPRS Journal of Photogrammetry and Remote Sensing, International Journal of Applied Earth Observation and Geoinformation, Remote Sensing of Environment, and Remote Sensing.

Use `references/corpus/github_gee_discovery_100.yml` as the broad 100+ exam queue. Each entry must remain metadata-only until it has a license/provenance review and a sampling plan. Promote a repository from discovery to seed only when it improves coverage or quality beyond the existing seed set.

For paper-linked repositories, also require article DOI or publisher URL, repository URL, inspected commit or release, venue, license, private asset dependency check, and reproducibility scope. Keep them at `metadata_only_until_license_review` until those fields are recorded.

Do not copy repository code into this project by default. Extract small, attributed patterns such as:

- operator sequence names;
- required bands and QA bands;
- validation implications;
- common failure modes;
- required plan fields;
- examples as natural-language task prompts.
- publication-linked reproducibility caveats.

The corpus exam should score generated-script rules against these style signals:

- explicit temporal and spatial scope before expensive operations;
- quality masks before spectral indices or reducers;
- server-side `map`/date-sequence construction for repeated intervals;
- explicit scale, CRS/projection, `tileScale`, and `maxPixels` where relevant;
- reviewable export descriptions, selectors, regions, and file formats;
- bounded `getInfo()` or `evaluate()` use only for preflight/debug probes;
- guarded `main()` entrypoints for task submission;
- Browser or Computer Use only as observation/interaction surfaces, not as the normal execution path.

## Promotion Criteria

A pattern may be promoted into a dataset/operator/recipe/failure/rule card only when:

- it matches official Earth Engine API semantics;
- it is seen in more than one source or has strong domain justification;
- it does not depend on private assets or credentials;
- licensing allows the intended use or the result is a non-copyrightable factual/operator pattern;
- the promoted card records source URLs and last-checked dates.

## Harness Implications

known_failure: UNVERIFIED_CORPUS_PATTERN

The agent should never treat corpus-derived examples as live-execution authority. The safe flow remains:

```text
natural language -> plan -> retrieval evidence -> validation -> preflight -> explicit confirmation -> export -> trace
```

Corpus-derived cards improve recommendations and validation hints; they do not bypass review, preflight, or confirmation.
