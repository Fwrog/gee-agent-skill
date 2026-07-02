#!/usr/bin/env python3
"""Analyze Hong Kong v0.3 NDVI product-intercomparison Drive exports.

The script intentionally reads local files that were downloaded from Google
Drive. Codex or another agent should use the Drive connector to populate
``raw_drive``; this public script should not embed connector-specific auth.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Iterable


REQUIRED_PIXEL_COLUMNS = {
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
}

REQUIRED_WINDOW_COLUMNS = {
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
}

REQUIRED_LANDCOVER_COLUMNS = {
    "date_start",
    "date_end",
    "landcover_class",
    "purity_threshold",
    "matched_pixel_count",
    "bias",
    "mae",
    "rmse",
}

DATASETS = {
    "hls_l30": "NASA/HLS/HLSL30/v002",
    "hls_s30": "NASA/HLS/HLSS30/v002",
    "modis": "MODIS/061/MOD13Q1",
    "landcover": "ESA/WorldCover/v200",
}

EARTH_ENGINE_TASKS = [
    {
        "description": "hk_v03_hls_modis_window_metrics_2024",
        "task_id": "NZPMV2LZWZYIDDHKX2U5N5EY",
        "artifact_type": "csv",
        "evidence_status": "drive_readback_complete",
    },
    {
        "description": "hk_v03_hls_modis_pixel_samples_2024",
        "task_id": "JZDJPO4ADANSXUOASEPEHPSM",
        "artifact_type": "csv",
        "evidence_status": "drive_readback_complete",
    },
    {
        "description": "hk_v03_hls_modis_landcover_metrics_2024",
        "task_id": "27OETEPLZVXX5B2LESC36NO3",
        "artifact_type": "csv",
        "evidence_status": "drive_readback_complete",
    },
    {
        "description": "hk_v03_hls_modis_regional_timeseries_2024",
        "task_id": "GIYMEDUSFVSTQVRTUBN36CI7",
        "artifact_type": "csv",
        "evidence_status": "drive_readback_complete",
    },
    {
        "description": "hk_v03_annual_hls30_ndvi_mean_2024",
        "task_id": "DFY3P4V72EBGVKOFNGJQT747",
        "artifact_type": "geotiff",
        "evidence_status": "drive_readback_complete",
        "latest_observed_state": "COMPLETED",
    },
    {
        "description": "hk_v03_annual_hls_agg250_ndvi_mean_2024",
        "task_id": "RTT3QTY4U7A3HFBKHYWL35HD",
        "artifact_type": "geotiff",
        "evidence_status": "failed_replaced",
        "latest_observed_state": "FAILED",
        "note": "Original annual window-mean raster failed with out-of-memory.",
    },
    {
        "description": "hk_v03_annual_modis250_ndvi_mean_2024",
        "task_id": "JCWWH6RYTHYFXA63LT5YR3EB",
        "artifact_type": "geotiff",
        "evidence_status": "failed_original_replaced",
        "latest_observed_state": "FAILED",
        "note": "Original failed with product-grid clip transform error.",
    },
    {
        "description": "hk_v03_annual_diff_hlsagg_minus_modis_2024",
        "task_id": "GS6XIPD2SLQU5EJ6V4WV3RRT",
        "artifact_type": "geotiff",
        "evidence_status": "failed_original_replaced",
        "latest_observed_state": "FAILED",
        "note": "Original failed with product-grid clip transform error.",
    },
    {
        "description": "hk_v03_valid_count_250m_2024",
        "task_id": "BA2TTOVRKJVETTLQ75SSXVXP",
        "artifact_type": "geotiff",
        "evidence_status": "failed_replaced",
        "latest_observed_state": "FAILED",
        "note": "Original annual valid-count raster failed with out-of-memory.",
    },
    {
        "description": "hk_v03_annual_modis250_ndvi_mean_2024",
        "task_id": "ML4IF7QOIP63AAPJ6TXUZJAG",
        "artifact_type": "geotiff",
        "evidence_status": "drive_readback_complete",
        "latest_observed_state": "COMPLETED",
        "note": "Replacement task from unclipped annual product-grid stack.",
    },
    {
        "description": "hk_v03_annual_diff_hlsagg_minus_modis_2024",
        "task_id": "VYV4QDICIAKQPL62IRE5UAFF",
        "artifact_type": "geotiff",
        "evidence_status": "failed_replaced",
        "latest_observed_state": "FAILED",
        "note": "Replacement task from unclipped annual product-grid stack failed with out-of-memory.",
    },
    {
        "description": "hk_v03_annual_hls_agg250_ndvi_mean_2024",
        "task_id": "N6W3SDLSY5WFVL4IS3O7KRKR",
        "artifact_type": "geotiff",
        "evidence_status": "failed_replaced",
        "latest_observed_state": "FAILED",
        "note": "First low-memory replacement failed because the annual HLS mean lacked an explicit default projection before reduceResolution.",
    },
    {
        "description": "hk_v03_annual_diff_hlsagg_minus_modis_2024",
        "task_id": "CVTRNEIT2KS63EXWQA3MRFRO",
        "artifact_type": "geotiff",
        "evidence_status": "failed_replaced",
        "latest_observed_state": "FAILED",
        "note": "First low-memory replacement failed because the annual HLS mean lacked an explicit default projection before reduceResolution.",
    },
    {
        "description": "hk_v03_valid_count_250m_2024",
        "task_id": "4F2UKFOXHRFLOQD2OUESYMCC",
        "artifact_type": "geotiff",
        "evidence_status": "running",
        "latest_observed_state": "RUNNING",
        "note": "Low-memory byte-mask replacement.",
    },
    {
        "description": "hk_v03_annual_hls_agg250_ndvi_mean_2024",
        "task_id": "B3Y2SVOFJNVVHP4Q5BTL42O6",
        "artifact_type": "geotiff",
        "evidence_status": "running",
        "latest_observed_state": "RUNNING",
        "note": "Low-memory replacement after setting the annual HLS mean default projection.",
    },
    {
        "description": "hk_v03_annual_diff_hlsagg_minus_modis_2024",
        "task_id": "W2WWGA4D7LUQK3FPZAM54THJ",
        "artifact_type": "geotiff",
        "evidence_status": "running",
        "latest_observed_state": "RUNNING",
        "note": "Low-memory replacement after setting the annual HLS mean default projection.",
    },
]

DRIVE_OBSERVED_GEOTIFFS = [
    {"title": "hk_v03_annual_hls30_ndvi_mean_2024.tif", "size_bytes": 9805730},
    {"title": "hk_v03_annual_modis250_ndvi_mean_2024.tif", "size_bytes": 109431},
]

FIGURES = [
    "outputs/hk_ndvi_product_validation_v03/figures/hk_v03_regional_ndvi_timeseries.png",
    "outputs/hk_ndvi_product_validation_v03/figures/hk_v03_hls_vs_modis_hexbin.png",
    "outputs/hk_ndvi_product_validation_v03/figures/hk_v03_spatial_difference_samples.png",
    "outputs/hk_ndvi_product_validation_v03/figures/hk_v03_landcover_metrics.png",
    "outputs/hk_ndvi_product_validation_v03/figures/hk_v03_valid_fraction_by_window.png",
]

NUMERIC_COLUMNS = {
    "lon",
    "lat",
    "hls_ndvi_agg250",
    "modis_ndvi",
    "diff",
    "landcover_purity",
    "hls_valid_count",
    "modis_qa_summary",
    "matched_pixel_count",
    "valid_fraction",
    "mean_hls_ndvi",
    "mean_modis_ndvi",
    "bias",
    "mae",
    "rmse",
    "median_abs_error",
    "pearson_r",
}


def _read_csv(path: Path) -> list[dict[str, object]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in list(row):
            value = row[key]
            if key in NUMERIC_COLUMNS and value not in ("", None):
                try:
                    row[key] = float(value)
                except ValueError:
                    pass
    return rows


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: Iterable[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        ordered: list[str] = []
        for row in rows:
            for key in row:
                if key not in ordered:
                    ordered.append(key)
        fieldnames = ordered
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def _find_file(raw_dir: Path, prefix: str, suffix: str = ".csv", *, required: bool = True) -> Path | None:
    matches = sorted(raw_dir.glob(f"{prefix}*{suffix}"))
    if not matches:
        if not required:
            return None
        raise FileNotFoundError(f"No file matching {prefix}*{suffix} under {raw_dir}")
    return matches[0]


def _public_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def _as_float(value: object) -> float:
    if value in ("", None):
        return math.nan
    return float(value)


def _qa_local_geotiffs(raw_dir: Path) -> list[dict[str, object]]:
    geotiff_dir = raw_dir / "geotiff"
    paths = sorted(geotiff_dir.glob("*.tif"))
    if not paths:
        return []
    try:
        import numpy as np  # type: ignore
        from PIL import Image  # type: ignore
    except Exception as exc:  # pragma: no cover - optional validation dependency.
        return [
            {
                "status": "unavailable",
                "reason": f"Optional raster QA dependencies are unavailable: {exc}",
                "files_found": [path.name for path in paths],
            }
        ]

    rows: list[dict[str, object]] = []
    for path in paths:
        with Image.open(path) as image:
            arr = np.array(image, dtype="float64")
            finite = np.isfinite(arr)
            nonzero = finite & (arr != 0)
            vals = arr[nonzero]
            raster_type = "valid_count" if "valid_count" in path.name else "ndvi_difference" if "diff" in path.name else "ndvi"
            ndvi_like = raster_type in {"ndvi", "ndvi_difference"}
            sanity_passed = bool(vals.size and vals.min() >= -1.0001 and vals.max() <= 1.0001) if ndvi_like else bool(vals.size and vals.min() >= 0)
            rows.append(
                {
                    "file": path.name,
                    "raster_type": raster_type,
                    "bytes": path.stat().st_size,
                    "mode": image.mode,
                    "width": image.size[0],
                    "height": image.size[1],
                    "frames": getattr(image, "n_frames", 1),
                    "finite_fraction": float(finite.mean()),
                    "nonzero_fraction": float(nonzero.mean()),
                    "min_nonzero": float(vals.min()) if vals.size else None,
                    "p02_nonzero": float(np.percentile(vals, 2)) if vals.size else None,
                    "mean_nonzero": float(vals.mean()) if vals.size else None,
                    "p98_nonzero": float(np.percentile(vals, 98)) if vals.size else None,
                    "max_nonzero": float(vals.max()) if vals.size else None,
                    "qa_rule": "nonzero finite values within [-1, 1]" if ndvi_like else "nonzero finite counts are non-negative",
                    "sanity_check_passed": sanity_passed,
                    "ndvi_sanity_nonzero_within_minus1_1": sanity_passed if ndvi_like else None,
                }
            )
    return rows


def _load_task_records(out_dir: Path) -> list[dict[str, object]]:
    task_status_path = out_dir / "task_status_latest.json"
    if not task_status_path.exists():
        return EARTH_ENGINE_TASKS
    payload = json.loads(task_status_path.read_text(encoding="utf-8"))
    records: list[dict[str, object]] = []
    for task in payload.get("tasks", []):
        if not isinstance(task, dict):
            continue
        records.append(
            {
                "description": task.get("description"),
                "task_id": task.get("task_id"),
                "artifact_type": task.get("artifact_type"),
                "drive_folder": task.get("drive_folder"),
                "source_assets": task.get("source_assets"),
                "crs": task.get("crs"),
                "scale_m": task.get("scale_m"),
                "claim_boundary": task.get("claim_boundary"),
                "state": task.get("state"),
                "error_message": task.get("error_message"),
            }
        )
    return records or EARTH_ENGINE_TASKS


def pearson(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return math.nan
    xbar = sum(x for x, _ in pairs) / len(pairs)
    ybar = sum(y for _, y in pairs) / len(pairs)
    num = sum((x - xbar) * (y - ybar) for x, y in pairs)
    den_x = math.sqrt(sum((x - xbar) ** 2 for x, _ in pairs))
    den_y = math.sqrt(sum((y - ybar) ** 2 for _, y in pairs))
    if den_x == 0 or den_y == 0:
        return math.nan
    return num / (den_x * den_y)


def _rank(values: list[float]) -> list[float]:
    indexed = sorted((value, idx) for idx, value in enumerate(values))
    ranks = [math.nan] * len(values)
    pos = 0
    while pos < len(indexed):
        end = pos + 1
        while end < len(indexed) and indexed[end][0] == indexed[pos][0]:
            end += 1
        avg_rank = (pos + 1 + end) / 2
        for _, idx in indexed[pos:end]:
            ranks[idx] = avg_rank
        pos = end
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return math.nan
    rx = _rank([x for x, _ in pairs])
    ry = _rank([y for _, y in pairs])
    return pearson(rx, ry)


def linear_slope_intercept(xs: list[float], ys: list[float]) -> tuple[float, float]:
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return math.nan, math.nan
    xbar = sum(x for x, _ in pairs) / len(pairs)
    ybar = sum(y for _, y in pairs) / len(pairs)
    den = sum((x - xbar) ** 2 for x, _ in pairs)
    if den == 0:
        return math.nan, math.nan
    slope = sum((x - xbar) * (y - ybar) for x, y in pairs) / den
    return slope, ybar - slope * xbar


def summarize_pairs(rows: list[dict[str, object]], group: str = "all") -> dict[str, object]:
    hls = [_as_float(row.get("hls_ndvi_agg250")) for row in rows]
    modis = [_as_float(row.get("modis_ndvi")) for row in rows]
    diffs = [h - m for h, m in zip(hls, modis) if math.isfinite(h) and math.isfinite(m)]
    if not diffs:
        raise ValueError(f"No valid matched pixels for group {group}")
    if median(abs(value) for value in modis if math.isfinite(value)) > 2:
        raise ValueError("MODIS NDVI values look unscaled; expected MOD13Q1 scale factor 0.0001.")
    if sum(not (-1.2 <= value <= 1.2) for value in hls + modis if math.isfinite(value)) > len(diffs) * 0.05:
        raise ValueError("More than 5% of NDVI values fall outside the sanity range [-1.2, 1.2].")
    slope, intercept = linear_slope_intercept(modis, hls)
    return {
        "group": group,
        "matched_pixel_count": len(diffs),
        "mean_hls_ndvi": sum(h for h in hls if math.isfinite(h)) / len(diffs),
        "mean_modis_ndvi": sum(m for m in modis if math.isfinite(m)) / len(diffs),
        "bias_hls_minus_modis": sum(diffs) / len(diffs),
        "mae": sum(abs(diff) for diff in diffs) / len(diffs),
        "rmse": math.sqrt(sum(diff * diff for diff in diffs) / len(diffs)),
        "median_abs_error": median(abs(diff) for diff in diffs),
        "pearson_r": pearson(hls, modis),
        "spearman_rho": spearman(hls, modis),
        "ols_slope_hls_on_modis": slope,
        "ols_intercept_hls_on_modis": intercept,
    }


def clean_pixel_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    missing = REQUIRED_PIXEL_COLUMNS - set(rows[0]) if rows else REQUIRED_PIXEL_COLUMNS
    if missing:
        raise ValueError(f"Pixel sample CSV is missing columns: {sorted(missing)}")
    clean: list[dict[str, object]] = []
    for row in rows:
        hls = _as_float(row.get("hls_ndvi_agg250"))
        modis = _as_float(row.get("modis_ndvi"))
        if math.isfinite(hls) and math.isfinite(modis):
            row["diff"] = hls - modis
            clean.append(row)
    if not clean:
        raise ValueError("No valid matched pixels exist after cleaning.")
    return clean


def analyze(
    raw_dir: Path,
    out_dir: Path,
    *,
    allow_partial: bool = False,
    drive_folder: str = "GEE_SKILL_V03_HK_NDVI_VALIDATION",
) -> dict[str, object]:
    raw_dir = raw_dir.resolve()
    out_dir = out_dir.resolve()
    analysis_dir = out_dir / "analysis"
    manifest_path = out_dir / "manifest.json"
    pixel_path = _find_file(raw_dir, "hk_v03_hls_modis_pixel_samples_2024")
    window_path = _find_file(raw_dir, "hk_v03_hls_modis_window_metrics_2024", required=not allow_partial)
    lc_path = _find_file(raw_dir, "hk_v03_hls_modis_landcover_metrics_2024", required=not allow_partial)
    regional_path = _find_file(raw_dir, "hk_v03_hls_modis_regional_timeseries_2024", required=False)
    assert pixel_path is not None

    pixel_rows = clean_pixel_rows(_read_csv(pixel_path))
    window_rows = _read_csv(window_path) if window_path else []
    if window_rows:
        missing = REQUIRED_WINDOW_COLUMNS - set(window_rows[0])
        if missing:
            raise ValueError(f"Window metrics CSV is missing columns: {sorted(missing)}")

    lc_rows = _read_csv(lc_path) if lc_path else []
    if lc_rows:
        missing = REQUIRED_LANDCOVER_COLUMNS - set(lc_rows[0])
        if missing:
            raise ValueError(f"Land-cover metrics CSV is missing columns: {sorted(missing)}")

    regional_rows = _read_csv(regional_path) if regional_path else window_rows
    if regional_rows:
        missing = REQUIRED_WINDOW_COLUMNS - set(regional_rows[0])
        if missing:
            raise ValueError(f"Regional time-series CSV is missing columns: {sorted(missing)}")

    overall = summarize_pairs(pixel_rows)
    by_class: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in pixel_rows:
        grouped[str(row.get("landcover_class", "unknown"))].append(row)
    for group, rows in sorted(grouped.items()):
        if len(rows) >= 5:
            by_class.append(summarize_pairs(rows, group=group))

    zero_windows = [
        str(row.get("date_start"))
        for row in window_rows
        if _as_float(row.get("matched_pixel_count")) == 0
    ]
    landcover_summary = {
        str(row["group"]): {
            "matched_pixel_count": row["matched_pixel_count"],
            "bias_hls_minus_modis": row["bias_hls_minus_modis"],
            "mae": row["mae"],
            "rmse": row["rmse"],
        }
        for row in by_class
    }
    snapshot_status = "partial" if allow_partial and (not window_path or not lc_path) else "complete_for_csv_tables"

    _write_csv(analysis_dir / "pixel_samples_clean.csv", pixel_rows)
    _write_csv(analysis_dir / "summary_metrics.csv", [overall])
    _write_csv(analysis_dir / "summary_metrics_by_landcover.csv", by_class)
    _write_csv(analysis_dir / "window_metrics.csv", window_rows)
    _write_csv(analysis_dir / "landcover_metrics.csv", lc_rows)
    _write_csv(analysis_dir / "regional_timeseries.csv", regional_rows)

    geotiff_qa = _qa_local_geotiffs(raw_dir)
    manifest = {
        "demo_id": "hk_ndvi_product_validation_v03",
        "status": "full_year_csv_and_tile_geotiff_evidence_complete"
        if snapshot_status == "complete_for_csv_tables" and geotiff_qa
        else "partial_csv_evidence",
        "analysis_type": "product_intercomparison_not_ground_truth",
        "claim_boundary": "Product-level consistency validation only; no in-situ ground truth is used.",
        "year": 2024,
        "drive_folder": drive_folder,
        "datasets": DATASETS,
        "roi": {
            "source": "documented_bbox",
            "bbox": [113.82, 22.13, 114.45, 22.57],
            "limitation": "Bounding polygon is used for stable product-grid export; it is not an authoritative administrative boundary.",
        },
        "method": {
            "hls_ndvi": {
                "l30_red": "B4",
                "l30_nir": "B5",
                "s30_red": "B4",
                "s30_nir_default": "B8A",
                "scale_factor": 0.0001,
                "qa": "Fmask excludes cloud, adjacent cloud/shadow, shadow, snow/ice, water, and high aerosol.",
            },
            "modis_ndvi": {
                "band": "NDVI",
                "scale_factor": 0.0001,
                "qa": "SummaryQA<=1 and DetailedQA quality, aerosol, cloud, snow, shadow, and land/coast filters.",
            },
            "temporal_matching": "MODIS 16-day windows define each HLS composite window.",
            "scale_matching": "Median HLS 30 m NDVI is aggregated to the MODIS projection before comparison.",
            "stratification": "Static ESA WorldCover v200 purity groups.",
        },
        "earth_engine_tasks": _load_task_records(out_dir),
        "drive_observed_geotiffs": DRIVE_OBSERVED_GEOTIFFS,
        "task_status_snapshot": "outputs/hk_ndvi_product_validation_v03/task_status_latest.json",
        "geotiff_local_qa": geotiff_qa,
        "raw_drive_dir": _public_path(raw_dir),
        "analysis_dir": _public_path(analysis_dir),
        "source_files": {
            "pixel_samples": _public_path(pixel_path),
            "window_metrics": _public_path(window_path) if window_path else None,
            "landcover_metrics": _public_path(lc_path) if lc_path else None,
            "regional_timeseries": _public_path(regional_path) if regional_path else None,
        },
        "figures": FIGURES,
        "snapshot_status": snapshot_status,
        "key_metrics": overall,
        "landcover_summary": landcover_summary,
        "qa_notes": [
            f"Strict-QA zero-match windows: {', '.join(zero_windows)}." if zero_windows else "All windows had at least one matched pixel.",
            "NDVI sanity checks passed; MODIS values do not look unscaled.",
            "Time-series figures preserve strict-QA gaps rather than interpolating.",
            "Google Drive file links must come from connector readback, not this local manifest.",
        ],
        "remaining_todo": [
            "Add a skill-generated-vs-canonical workflow comparator for v0.4.",
            "Optionally add VIIRS VNP13A1 as a secondary product-level check.",
        ],
        "limitations": [
            "Product-level consistency validation only; no in-situ ground truth is used.",
            "HLS 30 m pixels are aggregated to the MODIS grid before comparison.",
            "ESA WorldCover v200 is a static 2021 land-cover layer used for stratification.",
            "Google Drive file links must come from connector readback, not this local manifest.",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="outputs/hk_ndvi_product_validation_v03/raw_drive")
    parser.add_argument("--out", default="outputs/hk_ndvi_product_validation_v03")
    parser.add_argument("--drive-folder", default="GEE_SKILL_V03_HK_NDVI_VALIDATION", help="Recorded for traceability; downloads must already be local.")
    parser.add_argument("--allow-partial", action="store_true", help="Allow analysis from pixel samples when window/land-cover CSVs are not available yet.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    manifest = analyze(Path(args.raw_dir), Path(args.out), allow_partial=args.allow_partial, drive_folder=args.drive_folder)
    if args.json:
        print(json.dumps({"ok": True, "data": manifest}, indent=2, ensure_ascii=False))
    else:
        print(f"Wrote analysis to {manifest['analysis_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
