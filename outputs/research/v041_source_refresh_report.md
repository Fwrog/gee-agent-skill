# v0.4.1 Controlled Source Refresh Report

Date: 2026-07-09

Method: controlled URL and metadata-family verification only. No full papers, documentation pages, or repository code were copied into the KG-RAG assets.

Reviewed source families included Earth Engine official guides, Data Catalog, API reference, `google/earthengine-api`, MOD13Q1, HLSL30, HLSS30, Sentinel-1 GRD, Sentinel-2 SR Harmonized, Landsat Collection 2 Level 2, Dynamic World, ESA WorldCover, JRC Global Surface Water, VIIRS VNP13A1, MODIS LST, geemap, giswqs notebooks, GEE-OPs, AutoGEEval, AutoGEEval++, Geo-FuB, and Gorelick 2017.

Representative verification URLs:

- https://developers.google.com/earth-engine
- https://developers.google.com/earth-engine/datasets
- https://developers.google.com/earth-engine/apidocs
- https://developers.google.com/earth-engine/guides/resample
- https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1
- https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
- https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
- https://github.com/google/earthengine-api
- https://github.com/giswqs/earthengine-py-notebooks
- https://arxiv.org/abs/2506.10365

Registry changes:

- Added `source_refresh_status` to each source.
- Added `review_notes` to each source.
- Kept accepted official and license-reviewed community sources as `fresh`.
- Kept candidate research papers and candidate repos as `candidate_unverified`.

Policy outcome: Tier A official sources remain authoritative for current Earth Engine dataset/API facts. Papers support methodology, benchmark, and research framing only. Community repositories support distilled patterns or metadata-only context according to license review.
