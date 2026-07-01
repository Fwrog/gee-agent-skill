# Remote Sensing Validation Ladder

This note explains how to reason about the public NDVI demos with independent or semi-independent GEE products. The goal is method reasonableness: the demo should behave like a plausible quantitative remote-sensing workflow. This is not a replacement for field validation or a peer-reviewed vegetation product.

## Validation Products

| Product | GEE id | Role | Main caveat |
| --- | --- | --- | --- |
| Sentinel-2 SR Harmonized | `COPERNICUS/S2_SR_HARMONIZED` | Primary high-resolution source used by the demos. | Needs cloud/shadow masking and explicit scale. |
| MODIS Terra VI | `MODIS/061/MOD13Q1` | Coarse 16-day NDVI/EVI temporal sanity check. | 250m composites cannot validate 10m edges. |
| MODIS Aqua VI | `MODIS/061/MYD13Q1` | Terra/Aqua consistency check for coarse NDVI/EVI timing. | Different overpass timing and compositing. |
| Landsat 8/9 C2 L2 | `LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2` | Independent 30m sensor check for NDVI sign, magnitude, and broad seasonal pattern. | Requires QA masking and surface-reflectance scale/offset conversion. |
| JRC Global Surface Water | `JRC/GSW1_4/GlobalSurfaceWater` | Water-mask sanity check for all-surface NDVI. | Historical/static layers are context, not current vegetation truth. |
| Dynamic World | `GOOGLE/DYNAMICWORLD/V1` | Time-matched land-cover strata for the land-cover-aware demo. | Model output, not independent ground truth. |
| ESA WorldCover | `ESA/WorldCover/v200` | Static land-cover reference for broad class sanity checks. | 2021 static map is not time-matched to every analysis date. |

## What This Can Validate

- All-surface NDVI should be lower than land-only or vegetation-like NDVI in coastal or water-rich AOIs.
- Water and built-up strata should generally have lower NDVI than tree, grass, or crop strata.
- MODIS and Landsat should agree with Sentinel-2 in sign, broad magnitude, and temporal direction after scale, QA, and resolution differences are respected.
- Dynamic World strata should be documented as interpretation masks, not boundaries or truth labels.
- A workflow can be operationally correct even when different products do not match exactly.

## What It Cannot Validate

- Pixel-perfect agreement between 10m Sentinel-2 and 250m MODIS.
- Final vegetation health conclusions without field or trusted reference data.
- Land-cover truth from Dynamic World alone.
- Administrative or policy claims from land-cover masks.

## Lightweight Product Smoke Evidence

A read-only Earth Engine smoke check on 2026-07-01 confirmed that the candidate products expose the expected January 2024 imagery or bands in GEE:

| Dataset | January 2024 global image count or asset check | Expected bands observed |
| --- | ---: | --- |
| `COPERNICUS/S2_SR_HARMONIZED` | 295605 | `B4`, `B8`, `SCL`, QA bands present |
| `MODIS/061/MOD13Q1` | 2 | `NDVI`, `EVI`, `DetailedQA`, `SummaryQA` |
| `MODIS/061/MYD13Q1` | 2 | `NDVI`, `EVI`, `DetailedQA`, `SummaryQA` |
| `LANDSAT/LC08/C02/T1_L2` | 9793 | `SR_B4`, `SR_B5`, `QA_PIXEL` |
| `LANDSAT/LC09/C02/T1_L2` | 9780 | `SR_B4`, `SR_B5`, `QA_PIXEL` |
| `GOOGLE/DYNAMICWORLD/V1` | 131876 | `water`, `trees`, `grass`, `crops`, `built`, `bare`, `label` |
| `JRC/GSW1_4/GlobalSurfaceWater` | static image asset | `occurrence`, `seasonality`, `max_extent` |
| `ESA/WorldCover/v200` | 1 | `Map` |

This smoke evidence proves product availability and band compatibility only. It does not prove zonal statistics or scientific accuracy.

## Recommended Check Sequence

1. Recompute the demo NDVI with the same AOI, dates, cloud policy, scale, and reducer.
2. Compare the same date window against MOD13Q1/MYD13Q1 after applying the `0.0001` NDVI scale factor.
3. Compare against Landsat 8/9 NDVI after QA masking and Collection 2 scale/offset conversion.
4. Split Sentinel-2 NDVI by JRC water/non-water masks.
5. Split Sentinel-2 NDVI by Dynamic World probability masks and sanity-check against ESA WorldCover broad classes.
6. Report mismatches as sensor, resolution, compositing, QA, or mask-definition differences unless additional evidence says otherwise.

## Claim Boundary

For the public demos, the strongest defensible statement is:

```text
The NDVI workflows are operationally reasonable and consistent with standard remote-sensing checks across public GEE products, but the demo outputs are regression evidence for the harness rather than final scientific vegetation assessments.
```
