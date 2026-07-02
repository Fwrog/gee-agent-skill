# Hong Kong NDVI Product Intercomparison Validation v0.3

Status: `Golden` public v0.3 evidence. Full-year 2024 CSV exports, annual GeoTIFF/tiled raster exports, Google Drive readback, local analysis, figures, report, and readiness audit are complete.

This report belongs to the public v0.3 validation demo for `gee-agent-skill`. It evaluates workflow reliability through product-level consistency between HLS-derived NDVI aggregated to the MODIS grid and the official MODIS MOD13Q1 NDVI product. It is not in-situ ground-truth validation.

## Scope

The repository contains:

- canonical Earth Engine export script: `scripts/hk_ndvi_v03_export.py`;
- Drive-download analysis script: `scripts/hk_ndvi_v03_analyze_drive_exports.py`;
- publication-style figure script: `scripts/hk_ndvi_v03_make_figures.py`;
- task-state monitor: `scripts/hk_ndvi_v03_monitor_tasks.py`;
- Golden-readiness audit: `scripts/hk_ndvi_v03_readiness_audit.py`;
- recipe contract: `examples/hk_ndvi_product_validation_v03/hk_ndvi_product_validation.recipe.yaml`;
- documentation: `docs/validation/hk_ndvi_product_intercomparison_v03.md`;
- schema and metrics contract tests.

The current evidence is stronger than smoke evidence because the required full-year CSV exports and annual raster outputs were read back from Google Drive and analyzed without `--allow-partial`. Full-region raster attempts exposed reusable Earth Engine memory/projection failure modes; deterministic 2x2 tiled fallbacks completed for the products that exceeded full-region memory limits. The readiness audit now returns `golden_ready`.

## Live Export Evidence

Drive folder: `GEE_SKILL_V03_HK_NDVI_VALIDATION`.

Full-year 2024 task ids submitted through the official Earth Engine Python API:

| Description | Task id | Evidence status |
| --- | --- | --- |
| `hk_v03_hls_modis_window_metrics_2024` | `NZPMV2LZWZYIDDHKX2U5N5EY` | CSV read back from Drive |
| `hk_v03_hls_modis_pixel_samples_2024` | `JZDJPO4ADANSXUOASEPEHPSM` | CSV read back from Drive |
| `hk_v03_hls_modis_landcover_metrics_2024` | `27OETEPLZVXX5B2LESC36NO3` | CSV read back from Drive |
| `hk_v03_hls_modis_regional_timeseries_2024` | `GIYMEDUSFVSTQVRTUBN36CI7` | CSV read back from Drive |
| `hk_v03_annual_hls30_ndvi_mean_2024` | `DFY3P4V72EBGVKOFNGJQT747` | COMPLETED; Drive readback observed |
| `hk_v03_annual_hls_agg250_ndvi_mean_2024` | `RTT3QTY4U7A3HFBKHYWL35HD` | FAILED with out-of-memory; replacement submitted |
| `hk_v03_annual_modis250_ndvi_mean_2024` | `JCWWH6RYTHYFXA63LT5YR3EB` | FAILED with product-grid clip transform error |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` | `GS6XIPD2SLQU5EJ6V4WV3RRT` | FAILED with product-grid clip transform error |
| `hk_v03_valid_count_250m_2024` | `BA2TTOVRKJVETTLQ75SSXVXP` | FAILED with out-of-memory; replacement submitted |
| `hk_v03_annual_modis250_ndvi_mean_2024` replacement | `ML4IF7QOIP63AAPJ6TXUZJAG` | COMPLETED; Drive readback observed |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` replacement | `VYV4QDICIAKQPL62IRE5UAFF` | FAILED with out-of-memory; projected low-memory replacement submitted |
| `hk_v03_annual_hls_agg250_ndvi_mean_2024` low-memory replacement | `N6W3SDLSY5WFVL4IS3O7KRKR` | FAILED because annual HLS mean lacked explicit default projection |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` low-memory replacement | `CVTRNEIT2KS63EXWQA3MRFRO` | FAILED because annual HLS mean lacked explicit default projection |
| `hk_v03_valid_count_250m_2024` low-memory replacement | `4F2UKFOXHRFLOQD2OUESYMCC` | FAILED with out-of-memory |
| `hk_v03_annual_hls_agg250_ndvi_mean_2024` projected low-memory replacement | `B3Y2SVOFJNVVHP4Q5BTL42O6` | FAILED with out-of-memory |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` projected low-memory replacement | `W2WWGA4D7LUQK3FPZAM54THJ` | FAILED with out-of-memory |
| `hk_v03_annual_hls_agg250_ndvi_mean_2024` 2x2 tiled fallback | `JWEFLQ56F57CBT2EIEM5IPIY`, `Q7RA3R3RJTN7LDVAY4RLD67O`, `3ROL7PQUDP2P5JNAAMYN6R3Z`, `H4VT6D3DHYNIVSJ7DLPDAXMF` | Completed; Drive readback and local QA complete |
| `hk_v03_valid_count_250m_2024` 2x2 tiled fallback | `BQOB3OZUNMASJ7ZWIYZ6RXPC`, `6T2PFEWTKXACVYLLLAYNNHPQ`, `HYZ2O63YUG7ZKBL4X6XO6UNO`, `GDVLYGQHUCCPGJLPP2EL2XC4` | Completed; Drive readback and local QA complete |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` 2x2 tiled fallback | `GMJJTJJ2IDXSNL4FK6XL2SH2`, `7MNVLVPL6KQVZI4AZXKVKPZH`, `YZHKISDDJCP6CCZ5CNWPV33M`, `M6PKMTHMK73NYXYMOBZI7ROC` | Completed; Drive readback and local QA complete |

The replacement tasks were submitted after removing per-window `clip(roi)` from product-grid annual raster inputs, relying on `Export.image.toDrive(region=...)` for output bounds, and using a lower-memory annual raster strategy for failed HLS aggregated and valid-count rasters. The latest task-state evidence is recorded in `outputs/hk_ndvi_product_validation_v03/task_status_latest.json`.

Drive-downloaded CSV files analyzed locally:

| File | Rows including header | Use |
| --- | ---: | --- |
| `hk_v03_hls_modis_window_metrics_2024.csv` | 24 | MODIS 16-day window metrics |
| `hk_v03_hls_modis_pixel_samples_2024.csv` | 5,576 | Matched pixel-sample metrics |
| `hk_v03_hls_modis_landcover_metrics_2024.csv` | 277 | Land-cover stratified metrics |
| `hk_v03_hls_modis_regional_timeseries_2024.csv` | 24 | Regional mean time series |

Drive-observed and locally downloaded full-year GeoTIFF files:

| File | Size | Local QA |
| --- | ---: | --- |
| `hk_v03_annual_hls30_ndvi_mean_2024.tif` | 9,805,730 bytes | downloaded to ignored `raw_drive/geotiff/`; nonzero NDVI range -0.404 to 0.993 |
| `hk_v03_annual_modis250_ndvi_mean_2024.tif` | 109,431 bytes | downloaded to ignored `raw_drive/geotiff/`; nonzero NDVI range -0.200 to 0.997 |
| `hk_v03_annual_hls_agg250_ndvi_mean_2024` 2x2 tiles | 23,503 to 47,025 bytes | downloaded to ignored `raw_drive/geotiff/`; nonzero NDVI tile ranges remain within [-1, 1] |
| `hk_v03_annual_diff_hlsagg_minus_modis_2024` 2x2 tiles | 20,848 to 44,564 bytes | downloaded to ignored `raw_drive/geotiff/`; nonzero difference tile ranges remain within [-1, 1] |
| `hk_v03_valid_count_250m_2024` 2x2 tiles | 4,468 to 7,527 bytes | downloaded to ignored `raw_drive/geotiff/`; nonzero counts are non-negative |

All downloaded GeoTIFFs passed lightweight raster sanity checks. NDVI and difference rasters have nonzero finite values within [-1, 1], valid-count rasters have non-negative counts, and the rasters are not empty.

## Full-Year Metrics

Metrics are computed from Drive-downloaded CSVs under `outputs/hk_ndvi_product_validation_v03/raw_drive/`.

| Metric | Value |
| --- | ---: |
| Matched samples | 5,575 |
| Mean HLS aggregated NDVI | 0.662 |
| Mean MODIS NDVI | 0.687 |
| Bias, HLS - MODIS | -0.025 |
| MAE | 0.073 |
| RMSE | 0.111 |
| Median absolute error | 0.046 |
| Pearson r | 0.870 |
| Spearman rho | 0.859 |
| OLS slope, HLS on MODIS | 0.882 |
| OLS intercept | 0.056 |

Land-cover-stratified summary:

| Group | Samples | Bias | MAE | RMSE | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| vegetation_dominated | 3,654 | -0.020 | 0.055 | 0.082 | strongest agreement |
| built_up_dominated | 600 | -0.061 | 0.086 | 0.120 | weaker due to urban mixtures and low vegetation signal |
| mixed | 692 | -0.046 | 0.100 | 0.134 | weaker due to class mixing |
| coastal_or_water_adjacent | 629 | 0.009 | 0.133 | 0.193 | weakest due to water/coast adjacency and mixed pixels |

Four strict-QA windows had zero matched pixels and are intentionally left as gaps in time-series figures: 2024-02-18, 2024-04-22, 2024-05-24, and 2024-06-09. The workflow reports those gaps rather than interpolating or relaxing QA silently.

## Generated Figures

Small derived PNGs are committed as public validation evidence:

- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_regional_ndvi_timeseries.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_hls_vs_modis_hexbin.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_spatial_difference_samples.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_landcover_metrics.png`
- `outputs/hk_ndvi_product_validation_v03/figures/hk_v03_valid_fraction_by_window.png`

Figure QA notes:

- The time-series figure preserves strict-QA gaps.
- The hexbin uses matched pixel samples only and includes a 1:1 reference line.
- The spatial figure is a sample diagnostic, not a publication cartographic product.
- The land-cover chart uses static ESA WorldCover v200 strata and should not be read as 2024 ground truth.
- The valid-fraction chart makes cloud/QA limitations visible.

## Live Fixes From Smoke Attempts

- First smoke attempt exposed `reduceResolution` failures because HLS collection composites did not have a valid default projection.
- Second smoke attempt exposed administrative-boundary transform failures with product grids.
- Third smoke attempt produced Drive GeoTIFFs and exposed a null-metric failure in `window_metrics` when a window has no valid matched pixels.
- Full-year raster export exposed product-grid clip transform failures for MODIS annual and difference GeoTIFFs.
- Full-year HLS aggregated and valid-count annual rasters exposed out-of-memory failures when stacking per-window annual rasters.
- The first low-memory replacement exposed another `reduceResolution` default-projection failure after `ImageCollection.mean()`.
- The canonical script now sets a default HLS projection before aggregation, defaults live `auto` ROI to a documented Hong Kong bounding polygon for stable product-grid export, guards RMSE against null reducer output, keeps annual product-grid raster inputs unclipped until `Export.image.toDrive(region=...)`, and supports a lower-memory annual raster strategy.

## Skill Reliability Checklist

| Check | Expected | Status |
| --- | --- | --- |
| HLS datasets | `NASA/HLS/HLSL30/v002`, `NASA/HLS/HLSS30/v002` | Implemented in canonical script |
| HLS NDVI bands | L30 `B4/B5`, S30 `B4/B8A` | Implemented |
| HLS QA | `Fmask` cloud, adjacent cloud/shadow, shadow, snow/ice, water, high aerosol | Implemented |
| MODIS dataset | `MODIS/061/MOD13Q1` | Implemented |
| MODIS scale | `NDVI * 0.0001` | Implemented and tested |
| MODIS QA | `SummaryQA` and `DetailedQA` masks | Implemented |
| Temporal matching | MODIS 16-day windows drive HLS collection windows | Implemented |
| Scale matching | HLS 30 m median NDVI aggregated to MODIS projection before comparison | Implemented |
| Land-cover stratification | ESA WorldCover v200 purity groups | Implemented |
| Drive handoff | deterministic folder and file prefixes | Full-year CSV evidence, full-region GeoTIFFs, and 2x2 fallback GeoTIFF tiles read back from Drive |
| Ground-truth wording | product intercomparison only | Documented |

## Review Passes

| Review angle | Assessment |
| --- | --- |
| Remote-sensing method | Defensible for product-level consistency: HLS and MODIS are temporally matched, QA masked, scale matched before comparison, and stratified by land cover. It does not support in-situ accuracy claims. |
| GEE engineering | CSV exports completed through the official Python API. Raster export exposed reusable product-grid clip, out-of-memory, and default-projection failures; the canonical script now keeps annual product-grid raster inputs unclipped, sets default projection before low-memory aggregation, and records task states. |
| Documentation | README, validation docs, example docs, roadmap, and capability matrix label v0.3 as Golden and avoid ground-truth wording. |
| Reproducibility | Deterministic Drive folder and file prefixes, manifest, task status snapshot, tests, figures, rerun commands, Drive readback, raster QA, and readiness audit are present. |

## Limitations

- This validates product-level consistency and workflow construction, not absolute vegetation truth.
- FAO GAUL is conceptually preferred, but live v0.3 `auto` mode currently uses a documented bounding polygon because GAUL geometry triggered product-grid transform failures in smoke export.
- ESA WorldCover v200 is static 2021 land cover used for stratification, not 2024 truth.
- Coastal, steep terrain, dense urban, cloud, haze, BRDF, and mixed-pixel effects can produce real differences between HLS and MODIS.
- VIIRS VNP13A1 is reserved as an optional v0.4 secondary check unless added to a completed run.

## Remaining TODO

- Decide whether annual GeoTIFFs should remain external-only or whether tiny preview rasters/thumbnails should be committed.
- Add an automated comparator that checks a skill-generated workflow against the canonical v0.3 script.
- Generalize this completed HLS/MODIS pattern into a v0.4 `product_intercomparison` recipe, validators, and knowledge cards.
- Run final release hygiene before PR/merge: full pytest, CLI smoke/eval, privacy scan, and `git diff --check`.
