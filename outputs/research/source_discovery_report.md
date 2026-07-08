# Source Discovery Report

Last checked: 2026-07-09

This report records the v0.4 source-scout pass for the source-grounded GEE Research KG-RAG Engine. It is metadata-only and does not copy paper text, scraped pages, third-party code, private Drive paths, private Earth Engine assets, or unpublished claims.

## Official Tier A Sources

- Google Earth Engine documentation: `https://developers.google.com/earth-engine`
- Earth Engine Data Catalog: `https://developers.google.com/earth-engine/datasets`
- Earth Engine API reference: `https://developers.google.com/earth-engine/apidocs`
- `google/earthengine-api`: `https://github.com/google/earthengine-api`
- MOD13Q1 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1`
- HLSL30 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSL30_v002`
- HLSS30 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/NASA_HLS_HLSS30_v002`
- Resampling/reducing resolution guide: `https://developers.google.com/earth-engine/guides/resample`
- Projections guide: `https://developers.google.com/earth-engine/guides/projections`
- Scale guide: `https://developers.google.com/earth-engine/guides/scale`
- Usage/quotas guide: `https://developers.google.com/earth-engine/guides/usage`
- Code Editor guide: `https://developers.google.com/earth-engine/guides/playground`
- Sentinel-2 SR Harmonized catalog page: `https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED`
- Landsat 8 Collection 2 Level 2 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2`
- Sentinel-1 GRD catalog page: `https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD`
- Dynamic World V1 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1`
- ESA WorldCover v200 catalog page: `https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200`
- JRC Global Surface Water catalog page: `https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater`
- Hansen Global Forest Change catalog page: `https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2024_v1_12`
- MOD11A2 LST catalog page: `https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2`
- VIIRS VNP13A1 vegetation indices catalog page: `https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_001_VNP13A1`

Tier A sources are accepted for current API, dataset, band, QA, scale factor, projection, quota, and export-semantics facts.

## Research Sources

- GEE-OPs: `https://arxiv.org/abs/2412.05587`
  - Candidate Tier B source for operator knowledge-base design and RAG framing.
  - Not accepted for current API or dataset facts.
- AutoGEEval: `https://arxiv.org/abs/2505.12900`
  - Candidate Tier B source for GEE code-generation evaluation design.
  - Not accepted for current API or dataset facts.
- AutoGEEval++: `https://arxiv.org/abs/2506.10365`
  - Candidate Tier B source for multi-level GEE evaluation framing.
  - Not accepted for current API or dataset facts.
- Geo-FuB: `https://arxiv.org/abs/2410.20975`
  - Candidate Tier B source for operator-function knowledge-base construction.
  - Not accepted for current API or dataset facts.
- Gorelick et al. Earth Engine platform paper: `https://doi.org/10.1016/j.rse.2017.06.031`
  - Candidate Tier B platform research context.
- geemap JOSS paper: `https://joss.theoj.org/papers/10.21105/joss.02305`
  - Candidate Tier B software context.

Research sources remain candidate unless separately curated into evidence cards. Papers support methodology and patterns, not current dataset IDs, band names, scale factors, or API signatures.

## Community Sources

- `gee-community/geemap`: `https://github.com/gee-community/geemap`
  - Accepted Tier C for distilled patterns after MIT license check.
- `giswqs/earthengine-py-notebooks`: `https://github.com/giswqs/earthengine-py-notebooks`
  - Accepted Tier C for distilled notebook patterns after MIT license check.
- `whuhsy/geo-fub`: `https://github.com/whuhsy/geo-fub`
  - Candidate Tier C; license review required before use beyond metadata.
- `szx-0633/AutoGEEval`: `https://github.com/szx-0633/AutoGEEval`
  - Candidate Tier C; license review required before use beyond metadata.

## Policy Outcome

- Accepted sources are limited to official Tier A sources and community sources with clear license/provenance.
- Candidate research and benchmark sources are retained for future evidence curation but cannot override official facts.
- The v0.4 implementation stores metadata, citations, source URLs, short paraphrased summaries, structured facts, limitations, and links only.
- Current registry count: 31 sources; 23 accepted and 8 candidate.
