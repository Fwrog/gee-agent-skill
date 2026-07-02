#!/usr/bin/env python3
"""Submit Hong Kong v0.3 HLS/MODIS NDVI validation exports to Google Drive.

This is the canonical public implementation for the v0.3 portfolio demo. It
uses the official Earth Engine Python API and writes export tasks to a
deterministic Google Drive folder. Live task submission requires
``--confirm-live``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


DRIVE_FOLDER_DEFAULT = "GEE_SKILL_V03_HK_NDVI_VALIDATION"
LOCAL_OUTPUT_DEFAULT = Path("outputs/hk_ndvi_product_validation_v03")

HLS_L30 = "NASA/HLS/HLSL30/v002"
HLS_S30 = "NASA/HLS/HLSS30/v002"
MODIS = "MODIS/061/MOD13Q1"
ESA_WORLDCOVER = "ESA/WorldCover/v200"
GAUL_LEVEL0 = "FAO/GAUL/2015/level0"
GAUL_LEVEL1 = "FAO/GAUL/2015/level1"

HK_BBOX = [113.82, 22.13, 114.45, 22.57]
WORLD_COVER_GROUPS = {
    10: "vegetation",
    20: "vegetation",
    30: "vegetation",
    40: "vegetation",
    50: "built_up",
    60: "mixed_or_sparse",
    80: "water",
    90: "vegetation",
    95: "vegetation",
}
GROUP_CODE_TO_NAME = {
    1: "vegetation_dominated",
    2: "built_up_dominated",
    3: "mixed",
    4: "coastal_or_water_adjacent",
}
IMAGE_EXPORTS = {
    "hls30": ("hk_v03_annual_hls30_ndvi_mean_", "annual_hls30", 30, "EPSG:4326"),
    "hls_agg250": ("hk_v03_annual_hls_agg250_ndvi_mean_", "annual_hlsagg", 250, "EPSG:4326"),
    "modis250": ("hk_v03_annual_modis250_ndvi_mean_", "annual_modis", 250, "EPSG:4326"),
    "diff": ("hk_v03_annual_diff_hlsagg_minus_modis_", "annual_diff", 250, "EPSG:4326"),
    "valid_count": ("hk_v03_valid_count_250m_", "valid_count", 250, "EPSG:4326"),
}

PIXEL_SELECTORS = [
    "date_start",
    "date_end",
    "lon",
    "lat",
    "hls_ndvi_agg250",
    "modis_ndvi",
    "diff",
    "landcover_class",
    "landcover_purity",
    "hls_valid_count",
    "modis_qa_summary",
]
WINDOW_SELECTORS = [
    "date_start",
    "date_end",
    "matched_pixel_count",
    "valid_fraction",
    "mean_hls_ndvi",
    "mean_modis_ndvi",
    "bias",
    "mae",
    "rmse",
    "median_abs_error",
    "pearson_r",
    "hls_image_count",
    "modis_qa_policy",
]
LANDCOVER_SELECTORS = [
    "date_start",
    "date_end",
    "landcover_class",
    "purity_threshold",
    "matched_pixel_count",
    "bias",
    "mae",
    "rmse",
]


def _import_ee():
    try:
        import ee  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised only without EE.
        raise RuntimeError("earthengine-api is required. Install with pip install -e '.[earthengine]'.") from exc
    return ee


def _date_range(mode: str, year: int) -> tuple[str, str]:
    if mode == "smoke":
        return f"{year}-04-01", f"{year}-07-01"
    return f"{year}-01-01", f"{year + 1}-01-01"


def _parse_tile_grid(tile_grid: str) -> tuple[int, int]:
    normalized = tile_grid.lower().strip()
    if normalized in {"", "none", "1", "1x1"}:
        return 1, 1
    parts = normalized.split("x")
    if len(parts) != 2:
        raise ValueError("--tile-grid must use ROWSxCOLS, for example 2x2.")
    rows, cols = (int(parts[0]), int(parts[1]))
    if rows < 1 or cols < 1:
        raise ValueError("--tile-grid rows and columns must be positive.")
    if rows * cols > 36:
        raise ValueError("--tile-grid is capped at 36 tiles to avoid accidental task floods.")
    return rows, cols


def _tile_regions(ee: Any, rows: int, cols: int) -> list[tuple[str, Any, list[float]]]:
    xmin, ymin, xmax, ymax = HK_BBOX
    width = (xmax - xmin) / cols
    height = (ymax - ymin) / rows
    tiles = []
    for row in range(rows):
        for col in range(cols):
            bounds = [
                xmin + col * width,
                ymin + row * height,
                xmin + (col + 1) * width,
                ymin + (row + 1) * height,
            ]
            suffix = "" if rows == 1 and cols == 1 else f"_tile_r{row + 1:02d}_c{col + 1:02d}"
            tiles.append((suffix, ee.Geometry.Rectangle(bounds, proj="EPSG:4326", geodesic=False), bounds))
    return tiles


def _initialize_ee(project: str | None) -> Any:
    ee = _import_ee()
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()
    return ee


def _resolve_roi(ee: Any, preferred: str) -> tuple[Any, dict[str, Any]]:
    if preferred == "auto":
        bbox = ee.Geometry.Rectangle(HK_BBOX, proj="EPSG:4326", geodesic=False)
        return bbox, {
            "source": "documented_bbox",
            "method": "default auto fallback for stable product-grid export",
            "bbox": HK_BBOX,
            "fallback": True,
            "limitation": "FAO GAUL is preferred conceptually, but the v0.3 live export defaults to a documented bounding polygon to avoid product-grid transform failures.",
        }
    if preferred == "gaul":
        filters = [
            ee.Filter.eq("ADM0_NAME", "Hong Kong"),
            ee.Filter.eq("ADM0_NAME", "Hong Kong S.A.R."),
            ee.Filter.eq("ADM0_NAME", "China, Hong Kong Special Administrative Region"),
        ]
        gaul0 = ee.FeatureCollection(GAUL_LEVEL0).filter(ee.Filter.Or(*filters))
        if gaul0.size().getInfo() > 0:
            return gaul0.geometry(), {"source": GAUL_LEVEL0, "method": "ADM0_NAME Hong Kong match", "fallback": False}
        gaul1 = ee.FeatureCollection(GAUL_LEVEL1).filter(
            ee.Filter.Or(ee.Filter.eq("ADM1_NAME", "Hong Kong"), ee.Filter.eq("ADM1_NAME", "Hong Kong SAR"))
        )
        if gaul1.size().getInfo() > 0:
            return gaul1.geometry(), {"source": GAUL_LEVEL1, "method": "ADM1_NAME Hong Kong match", "fallback": False}
    bbox = ee.Geometry.Rectangle(HK_BBOX, proj="EPSG:4326", geodesic=False)
    return bbox, {
        "source": "documented_bbox",
        "method": "Hong Kong bounding rectangle fallback",
        "bbox": HK_BBOX,
        "fallback": True,
        "limitation": "Bounding polygon is not an authoritative administrative boundary.",
    }


def _hls_ndvi_collection(ee: Any, dataset_id: str, start: Any, end: Any, roi: Any, red: str, nir: str, label: str) -> Any:
    def mask_and_ndvi(image: Any) -> Any:
        fmask = image.select("Fmask")
        clear = (
            fmask.bitwiseAnd(1 << 1)
            .eq(0)
            .And(fmask.bitwiseAnd(1 << 2).eq(0))
            .And(fmask.bitwiseAnd(1 << 3).eq(0))
            .And(fmask.bitwiseAnd(1 << 4).eq(0))
            .And(fmask.bitwiseAnd(1 << 5).eq(0))
            .And(fmask.rightShift(6).bitwiseAnd(3).lt(3))
        )
        scaled = image.select([red, nir]).multiply(0.0001)
        ndvi = scaled.normalizedDifference([nir, red]).rename("hls_ndvi")
        return ndvi.updateMask(clear).copyProperties(image, ["system:time_start"]).set("hls_source", label)

    return ee.ImageCollection(dataset_id).filterBounds(roi).filterDate(start, end).map(mask_and_ndvi)


def _modis_masked(ee: Any, image: Any) -> Any:
    ndvi = image.select("NDVI").multiply(0.0001).rename("modis_ndvi")
    summary = image.select("SummaryQA")
    detailed = image.select("DetailedQA")
    vi_quality = detailed.bitwiseAnd(3).lte(1)
    aerosol_ok = detailed.rightShift(6).bitwiseAnd(3).lt(3)
    adjacent_ok = detailed.bitwiseAnd(1 << 8).eq(0)
    mixed_cloud_ok = detailed.bitwiseAnd(1 << 10).eq(0)
    land_water = detailed.rightShift(11).bitwiseAnd(7)
    land_or_coast = land_water.eq(1).Or(land_water.eq(2))
    snow_ok = detailed.bitwiseAnd(1 << 14).eq(0)
    shadow_ok = detailed.bitwiseAnd(1 << 15).eq(0)
    mask = summary.lte(1).And(vi_quality).And(aerosol_ok).And(adjacent_ok).And(mixed_cloud_ok).And(land_or_coast).And(snow_ok).And(shadow_ok)
    return ndvi.updateMask(mask).addBands(summary.rename("modis_qa_summary"))


def _landcover_stack(ee: Any, modis_projection: Any) -> Any:
    lc = ee.ImageCollection(ESA_WORLDCOVER).first().select("Map")
    veg = lc.remap([10, 20, 30, 40, 90, 95], [1, 1, 1, 1, 1, 1], 0).rename("veg_fraction")
    built = lc.eq(50).rename("built_fraction")
    water = lc.eq(80).rename("water_fraction")
    fractions = ee.Image.cat([veg, built, water]).reduceResolution(reducer=ee.Reducer.mean(), maxPixels=2048).reproject(modis_projection)
    veg_f = fractions.select("veg_fraction")
    built_f = fractions.select("built_fraction")
    water_f = fractions.select("water_fraction")
    group = (
        ee.Image(3)
        .where(veg_f.gte(0.7), 1)
        .where(built_f.gte(0.7), 2)
        .where(water_f.gt(0.05), 4)
        .rename("landcover_group_code")
    )
    purity = veg_f.max(built_f).max(water_f).rename("landcover_purity")
    return ee.Image.cat([fractions, group, purity])


def _metric_feature(ee: Any, image: Any, roi: Any, modis_projection: Any, props: dict[str, Any]) -> Any:
    metric_image = image.addBands(image.select("diff").abs().rename("abs_diff")).addBands(image.select("diff").pow(2).rename("sq_diff"))
    count = metric_image.select("diff").reduceRegion(
        reducer=ee.Reducer.count(), geometry=roi, crs=modis_projection, scale=250, maxPixels=1e8, tileScale=4
    ).get("diff")
    total = ee.Image(1).clip(roi).reduceRegion(
        reducer=ee.Reducer.count(), geometry=roi, crs=modis_projection, scale=250, maxPixels=1e8, tileScale=4
    ).get("constant")
    means = metric_image.select(["hls_ndvi_agg250", "modis_ndvi", "diff", "abs_diff", "sq_diff"]).reduceRegion(
        reducer=ee.Reducer.mean(), geometry=roi, crs=modis_projection, scale=250, maxPixels=1e8, tileScale=4
    )
    sq_diff_mean = means.get("sq_diff")
    median_abs = metric_image.select("abs_diff").reduceRegion(
        reducer=ee.Reducer.median(), geometry=roi, crs=modis_projection, scale=250, maxPixels=1e8, tileScale=4
    ).get("abs_diff")
    corr = metric_image.select(["hls_ndvi_agg250", "modis_ndvi"]).reduceRegion(
        reducer=ee.Reducer.pearsonsCorrelation(), geometry=roi, crs=modis_projection, scale=250, maxPixels=1e8, tileScale=4
    )
    return ee.Feature(
        None,
        props
        | {
            "matched_pixel_count": count,
            "valid_fraction": ee.Number(count).divide(ee.Number(total).max(1)),
            "mean_hls_ndvi": means.get("hls_ndvi_agg250"),
            "mean_modis_ndvi": means.get("modis_ndvi"),
            "bias": means.get("diff"),
            "mae": means.get("abs_diff"),
            "rmse": ee.Algorithms.If(ee.Algorithms.IsEqual(sq_diff_mean, None), None, ee.Number(sq_diff_mean).sqrt()),
            "median_abs_error": median_abs,
            "pearson_r": corr.get("correlation"),
            "modis_qa_policy": "SummaryQA<=1; DetailedQA good/marginal; aerosol<high; no adjacent/mixed cloud/snow/shadow; land/coast only",
        },
    )


def _window_product(ee: Any, modis_image: Any, roi: Any, s30_nir: str, sample_limit: int, sample_seed: int) -> dict[str, Any]:
    start = ee.Date(modis_image.get("system:time_start"))
    end = start.advance(16, "day")
    date_start = start.format("YYYY-MM-dd")
    date_end = end.format("YYYY-MM-dd")
    modis_projection = modis_image.select("NDVI").projection()
    l30 = _hls_ndvi_collection(ee, HLS_L30, start, end, roi, "B4", "B5", "HLSL30")
    s30 = _hls_ndvi_collection(ee, HLS_S30, start, end, roi, "B4", s30_nir, f"HLSS30_{s30_nir}")
    hls = l30.merge(s30)
    hls_projection = ee.Projection("EPSG:4326").atScale(30)
    hls_count = hls.count().rename("hls_valid_count").setDefaultProjection(hls_projection)
    hls_composite_30 = hls.median().rename("hls_ndvi").setDefaultProjection(hls_projection).clip(roi)
    hls_agg = hls_composite_30.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=2048).reproject(modis_projection).rename("hls_ndvi_agg250")
    hls_count_agg = hls_count.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=2048).reproject(modis_projection).rename("hls_valid_count")
    modis = _modis_masked(ee, modis_image)
    landcover = _landcover_stack(ee, modis_projection)
    diff = hls_agg.subtract(modis.select("modis_ndvi")).rename("diff")
    paired = ee.Image.cat([hls_agg, modis.select("modis_ndvi"), diff, hls_count_agg, modis.select("modis_qa_summary"), landcover]).clip(roi)
    paired = paired.updateMask(hls_agg.mask().And(modis.select("modis_ndvi").mask()))
    hls_image_count = hls.size()
    props = {"date_start": date_start, "date_end": date_end, "hls_image_count": hls_image_count}
    metric = _metric_feature(ee, paired, roi, modis_projection, props)

    def with_lon_lat(feature: Any) -> Any:
        coords = feature.geometry().coordinates()
        group_code = ee.Number(feature.get("landcover_group_code")).format()
        group_name = ee.Dictionary({"1": "vegetation_dominated", "2": "built_up_dominated", "3": "mixed", "4": "coastal_or_water_adjacent"}).get(group_code)
        return feature.set(
            {
                "date_start": date_start,
                "date_end": date_end,
                "lon": coords.get(0),
                "lat": coords.get(1),
                "landcover_class": group_name,
            }
        )

    samples = paired.sample(
        region=roi,
        projection=modis_projection,
        scale=250,
        numPixels=sample_limit,
        seed=sample_seed,
        geometries=True,
        tileScale=4,
    ).map(with_lon_lat)

    lc_metrics = []
    for threshold in (0.5, 0.7, 0.9):
        for code, name in GROUP_CODE_TO_NAME.items():
            masked = paired.updateMask(landcover.select("landcover_group_code").eq(code).And(landcover.select("landcover_purity").gte(threshold)))
            feature = _metric_feature(
                ee,
                masked,
                roi,
                modis_projection,
                {"date_start": date_start, "date_end": date_end, "landcover_class": name, "purity_threshold": threshold},
            )
            lc_metrics.append(feature)
    valid_match = hls_agg.mask().And(modis.select("modis_ndvi").mask()).rename("valid_match").unmask(0).toByte().reproject(modis_projection)
    return {
        "date_start": date_start,
        "date_end": date_end,
        "metric": metric,
        "samples": samples,
        "landcover_metrics": ee.FeatureCollection(lc_metrics),
        "hls_30": hls_composite_30,
        "hls_agg250": hls_agg,
        # Keep annual raster inputs unclipped. Export.region clips the final
        # output, and avoiding per-window clip prevents MODIS sinusoidal ->
        # WGS84 edge-transform failures in annual GeoTIFF exports.
        "modis_250": modis.select("modis_ndvi"),
        "diff": diff,
        "valid_mask": valid_match,
    }


def _table_export(ee: Any, collection: Any, description: str, folder: str, selectors: list[str]) -> Any:
    return ee.batch.Export.table.toDrive(
        collection=collection,
        description=description,
        folder=folder,
        fileNamePrefix=description,
        fileFormat="CSV",
        selectors=selectors,
    )


def _image_export(ee: Any, image: Any, description: str, folder: str, roi: Any, scale: int, crs: str | None = None) -> Any:
    kwargs: dict[str, Any] = {
        "image": image.toFloat(),
        "description": description,
        "folder": folder,
        "fileNamePrefix": description,
        "region": roi,
        "scale": scale,
        "maxPixels": 1e13,
        "fileFormat": "GeoTIFF",
        "formatOptions": {"cloudOptimized": True},
    }
    if crs:
        kwargs["crs"] = crs
    return ee.batch.Export.image.toDrive(**kwargs)


def build_exports(args: argparse.Namespace) -> dict[str, Any]:
    ee = _initialize_ee(args.project)
    roi, roi_info = _resolve_roi(ee, args.roi_source)
    tile_rows, tile_cols = _parse_tile_grid(args.tile_grid)
    export_tiles = _tile_regions(ee, tile_rows, tile_cols)
    date_start, date_end = _date_range(args.mode, args.year)
    modis_collection = ee.ImageCollection(MODIS).filterBounds(roi).filterDate(date_start, date_end).sort("system:time_start")
    modis_count = int(modis_collection.size().getInfo())
    if modis_count == 0:
        raise RuntimeError("No MODIS MOD13Q1 windows found for the selected ROI/date range.")
    modis_list = modis_collection.toList(modis_count)
    windows = [
        _window_product(ee, ee.Image(modis_list.get(index)), roi, args.s30_nir, args.max_samples_per_window, args.seed + index)
        for index in range(modis_count)
    ]

    window_metrics = ee.FeatureCollection([item["metric"] for item in windows])
    pixel_samples = ee.FeatureCollection([item["samples"] for item in windows]).flatten()
    landcover_metrics = ee.FeatureCollection([item["landcover_metrics"] for item in windows]).flatten()
    regional_timeseries = window_metrics.select(WINDOW_SELECTORS)

    reference_modis_projection = ee.Image(modis_list.get(0)).select("NDVI").projection()
    hls_30_projection = ee.Projection("EPSG:4326").atScale(30)
    annual_hls30 = (
        ee.ImageCollection([item["hls_30"] for item in windows])
        .mean()
        .rename("hls30_ndvi_mean")
        .setDefaultProjection(hls_30_projection)
    )
    if args.annual_raster_strategy == "low_memory":
        annual_hlsagg = (
            annual_hls30.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=2048)
            .reproject(reference_modis_projection)
            .rename("hls_agg250_ndvi_mean")
        )
    else:
        annual_hlsagg = ee.ImageCollection([item["hls_agg250"] for item in windows]).mean().rename("hls_agg250_ndvi_mean")
    annual_modis = ee.ImageCollection([item["modis_250"] for item in windows]).mean().rename("modis250_ndvi_mean")
    annual_diff = annual_hlsagg.subtract(annual_modis).rename("diff_hlsagg_minus_modis")
    valid_count = ee.ImageCollection([item["valid_mask"] for item in windows]).sum().rename("valid_count_250m").toFloat()
    image_products = {
        "annual_hls30": annual_hls30,
        "annual_hlsagg": annual_hlsagg,
        "annual_modis": annual_modis,
        "annual_diff": annual_diff,
        "valid_count": valid_count,
    }

    tasks = []
    if not args.images_only:
        tasks.extend(
            [
                _table_export(ee, window_metrics, f"hk_v03_hls_modis_window_metrics_{args.year}", args.drive_folder, WINDOW_SELECTORS),
                _table_export(ee, pixel_samples, f"hk_v03_hls_modis_pixel_samples_{args.year}", args.drive_folder, PIXEL_SELECTORS),
                _table_export(ee, landcover_metrics, f"hk_v03_hls_modis_landcover_metrics_{args.year}", args.drive_folder, LANDCOVER_SELECTORS),
                _table_export(ee, regional_timeseries, f"hk_v03_hls_modis_regional_timeseries_{args.year}", args.drive_folder, WINDOW_SELECTORS),
            ]
        )
    if not args.tables_only:
        requested = {name.strip() for name in args.image_exports.split(",") if name.strip()}
        unknown = requested - set(IMAGE_EXPORTS)
        if unknown:
            raise ValueError(f"Unknown image export names: {sorted(unknown)}")
        for export_name in IMAGE_EXPORTS:
            if export_name not in requested:
                continue
            prefix, product_key, scale, crs = IMAGE_EXPORTS[export_name]
            for tile_suffix, tile_region, _bounds in export_tiles:
                tasks.append(
                    _image_export(
                        ee,
                        image_products[product_key],
                        f"{prefix}{args.year}{tile_suffix}",
                        args.drive_folder,
                        tile_region,
                        scale,
                        crs,
                    )
                )

    manifest = {
        "demo_id": "hk_ndvi_product_validation_v03",
        "created_utc": dt.datetime.now(dt.UTC).isoformat(),
        "claim_boundary": "Product-level consistency validation; not in-situ ground-truth validation.",
        "mode": args.mode,
        "year": args.year,
        "date_start": date_start,
        "date_end": date_end,
        "drive_folder": args.drive_folder,
        "roi": roi_info,
        "export_region": {"source": "documented_bbox", "bbox": HK_BBOX, "crs": "EPSG:4326"},
        "tile_grid": {
            "rows": tile_rows,
            "cols": tile_cols,
            "enabled": tile_rows * tile_cols > 1,
            "bounds": [{"suffix": suffix, "bbox": bounds} for suffix, _region, bounds in export_tiles],
            "purpose": "Optional fallback for large annual GeoTIFF exports; default 1x1 preserves canonical file names.",
        },
        "datasets": [HLS_L30, HLS_S30, MODIS, ESA_WORLDCOVER],
        "dataset_roles": {
            HLS_L30: "30 m Landsat HLS NDVI source; red B4, NIR B5",
            HLS_S30: f"30 m Sentinel-2 HLS NDVI source; red B4, NIR {args.s30_nir}",
            MODIS: "Official 250 m Terra 16-day NDVI product; NDVI scale factor 0.0001",
            ESA_WORLDCOVER: "Static 2021 land-cover stratification; not ground truth for 2024",
        },
        "masking": {
            "hls_fmask": "mask cloud, adjacent cloud/shadow, cloud shadow, snow/ice, water, and high aerosol",
            "modis_qa": "SummaryQA<=1 and DetailedQA good/marginal, no high aerosol/adjacent cloud/mixed cloud/snow/shadow",
        },
        "grid_matching": "HLS 30 m median NDVI is reduced by mean and reprojected to each MOD13Q1 image projection before comparison.",
        "modis_window_count": modis_count,
        "tables_only": args.tables_only,
        "images_only": args.images_only,
        "export_descriptions": [task.config.get("description") for task in tasks],
        "annual_raster_strategy": args.annual_raster_strategy,
        "started": False,
        "tasks": [],
    }
    return {"ee": ee, "tasks": tasks, "manifest": manifest}


def run(args: argparse.Namespace) -> dict[str, Any]:
    built = build_exports(args)
    manifest = built["manifest"]
    tasks = built["tasks"]
    if args.confirm_live:
        started = []
        for task in tasks:
            task.start()
            status = task.status()
            started.append(
                {
                    "id": status.get("id"),
                    "state": status.get("state"),
                    "description": task.config.get("description"),
                    "drive_folder": args.drive_folder,
                }
            )
        manifest["started"] = True
        manifest["tasks"] = started
    else:
        manifest["started"] = False
        manifest["tasks"] = [
            {"id": None, "state": "NOT_STARTED", "description": task.config.get("description"), "drive_folder": args.drive_folder}
            for task in tasks
        ]
        manifest["live_start_blocked"] = "Pass --confirm-live to start Earth Engine export tasks."
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--drive-folder", default=DRIVE_FOLDER_DEFAULT)
    parser.add_argument("--project", default=None, help="Google Cloud project for ee.Initialize(project=...).")
    parser.add_argument("--roi-source", choices=["auto", "gaul", "bbox"], default="auto")
    parser.add_argument("--s30-nir", choices=["B8A", "B8"], default="B8A")
    parser.add_argument("--max-samples-per-window", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=20240701)
    parser.add_argument("--out", default=str(LOCAL_OUTPUT_DEFAULT))
    parser.add_argument("--tables-only", action="store_true", help="Submit only CSV table exports, useful for metrics smoke reruns.")
    parser.add_argument("--images-only", action="store_true", help="Submit only GeoTIFF image exports, useful after table exports have completed.")
    parser.add_argument(
        "--annual-raster-strategy",
        choices=["low_memory", "window_mean"],
        default="low_memory",
        help="Use low_memory annual rasters for GeoTIFF exports, or window_mean for the original per-window aggregation strategy.",
    )
    parser.add_argument(
        "--image-exports",
        default=",".join(IMAGE_EXPORTS),
        help="Comma-separated GeoTIFF exports to submit: hls30,hls_agg250,modis250,diff,valid_count.",
    )
    parser.add_argument(
        "--tile-grid",
        default="1x1",
        help="Optional image-export fallback grid as ROWSxCOLS, for example 2x2. Default 1x1 preserves canonical filenames.",
    )
    parser.add_argument("--confirm-live", action="store_true", help="Actually start Earth Engine export tasks.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.tables_only and args.images_only:
        parser.error("--tables-only and --images-only cannot be used together.")
    manifest = run(args)
    payload = {"ok": True, "data": manifest}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Wrote manifest to {Path(args.out) / 'manifest.json'}")
        if manifest["started"]:
            print(f"Started {len(manifest['tasks'])} Earth Engine export tasks.")
        else:
            print("Live task start blocked; pass --confirm-live after reviewing the manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
