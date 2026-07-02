#!/usr/bin/env python3
"""Audit whether the Hong Kong v0.3 validation demo is ready for Golden status."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/hk_ndvi_product_validation_v03")
REQUIRED_FIGURES = [
    "figures/hk_v03_regional_ndvi_timeseries.png",
    "figures/hk_v03_hls_vs_modis_hexbin.png",
    "figures/hk_v03_spatial_difference_samples.png",
    "figures/hk_v03_landcover_metrics.png",
    "figures/hk_v03_valid_fraction_by_window.png",
]
REQUIRED_GEOTIFFS = [
    "hk_v03_annual_hls30_ndvi_mean_2024.tif",
    "hk_v03_annual_hls_agg250_ndvi_mean_2024.tif",
    "hk_v03_annual_modis250_ndvi_mean_2024.tif",
    "hk_v03_annual_diff_hlsagg_minus_modis_2024.tif",
    "hk_v03_valid_count_250m_2024.tif",
]
REQUIRED_GEOTIFF_DESCRIPTIONS = {
    "hk_v03_annual_hls30_ndvi_mean_2024.tif": "hk_v03_annual_hls30_ndvi_mean_2024",
    "hk_v03_annual_hls_agg250_ndvi_mean_2024.tif": "hk_v03_annual_hls_agg250_ndvi_mean_2024",
    "hk_v03_annual_modis250_ndvi_mean_2024.tif": "hk_v03_annual_modis250_ndvi_mean_2024",
    "hk_v03_annual_diff_hlsagg_minus_modis_2024.tif": "hk_v03_annual_diff_hlsagg_minus_modis_2024",
    "hk_v03_valid_count_250m_2024.tif": "hk_v03_valid_count_250m_2024",
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_successful_tasks(task_status: dict[str, Any]) -> dict[str, dict[str, Any]]:
    successful: dict[str, dict[str, Any]] = {}
    for task in task_status.get("tasks", []):
        if task.get("state") != "COMPLETED":
            continue
        successful[str(task.get("description"))] = task
    return successful


def _tile_descriptions(task_status: dict[str, Any], base_description: str) -> list[str]:
    prefix = f"{base_description}_tile_"
    return sorted(
        str(task.get("description"))
        for task in task_status.get("tasks", [])
        if str(task.get("description", "")).startswith(prefix)
    )


def _tile_set_completed(task_status: dict[str, Any], base_description: str) -> bool:
    tile_tasks = [
        task
        for task in task_status.get("tasks", [])
        if str(task.get("description", "")).startswith(f"{base_description}_tile_")
    ]
    return bool(tile_tasks) and all(task.get("state") == "COMPLETED" for task in tile_tasks)


def _qa_row_passed(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    if "sanity_check_passed" in row:
        return bool(row.get("sanity_check_passed"))
    return bool(row.get("ndvi_sanity_nonzero_within_minus1_1"))


def _qa_row_has_readback_evidence(row: dict[str, Any] | None) -> bool:
    if not _qa_row_passed(row):
        return False
    try:
        return (
            int(row.get("bytes", 0)) > 0
            and int(row.get("width", 0)) > 0
            and int(row.get("height", 0)) > 0
        )
    except (TypeError, ValueError):
        return False


def audit(out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    manifest_path = out_dir / "manifest.json"
    task_status_path = out_dir / "task_status_latest.json"
    report_path = out_dir / "VALIDATION_REPORT.md"
    raw_geotiff_dir = out_dir / "raw_drive" / "geotiff"
    manifest = _load_json(manifest_path)
    task_status = _load_json(task_status_path)

    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    add_check("manifest_exists", manifest_path.exists(), str(manifest_path))
    add_check("task_status_exists", task_status_path.exists(), str(task_status_path))
    add_check("report_exists", report_path.exists(), str(report_path))
    add_check(
        "claim_boundary",
        manifest.get("analysis_type") == "product_intercomparison_not_ground_truth"
        and "no in-situ ground truth" in str(manifest.get("claim_boundary", "")).lower(),
        "Manifest must state product intercomparison, not ground-truth validation.",
    )
    add_check(
        "csv_analysis_complete",
        manifest.get("snapshot_status") == "complete_for_csv_tables"
        and int(manifest.get("key_metrics", {}).get("matched_pixel_count", 0)) > 0,
        "CSV analysis must be complete and have matched pixels.",
    )
    missing_figures = [figure for figure in REQUIRED_FIGURES if not (out_dir / figure).exists()]
    add_check("figures_exist", not missing_figures, f"Missing figures: {missing_figures}")

    summary = task_status.get("summary", {})
    add_check(
        "no_pending_tasks",
        bool(summary) and int(summary.get("pending_count", 1)) == 0,
        f"Pending task count: {summary.get('pending_count')}",
    )
    completed = _latest_successful_tasks(task_status)
    missing_completed = [
        description
        for description in REQUIRED_GEOTIFF_DESCRIPTIONS.values()
        if description not in completed and not _tile_set_completed(task_status, description)
    ]
    add_check("required_geotiff_tasks_completed", not missing_completed, f"Missing completed task descriptions: {missing_completed}")

    local_geotiffs = {path.name for path in raw_geotiff_dir.glob("*.tif")} if raw_geotiff_dir.exists() else set()
    qa_rows = manifest.get("geotiff_local_qa", [])
    qa_by_file = {row.get("file"): row for row in qa_rows if isinstance(row, dict)}

    missing_readback_evidence = []
    for filename, description in REQUIRED_GEOTIFF_DESCRIPTIONS.items():
        if filename in local_geotiffs:
            continue
        tile_files = [f"{tile}.tif" for tile in _tile_descriptions(task_status, description)]
        if _qa_row_has_readback_evidence(qa_by_file.get(filename)):
            continue
        if tile_files and all(
            tile_file in local_geotiffs or _qa_row_has_readback_evidence(qa_by_file.get(tile_file))
            for tile_file in tile_files
        ):
            continue
        missing_readback_evidence.append(filename)
    add_check(
        "required_geotiff_readback_evidence",
        not missing_readback_evidence,
        "Missing local Drive-downloaded GeoTIFFs or committed manifest QA evidence: "
        f"{missing_readback_evidence}",
    )

    failed_qa = []
    for filename, description in REQUIRED_GEOTIFF_DESCRIPTIONS.items():
        if _qa_row_passed(qa_by_file.get(filename)):
            continue
        tile_files = [f"{tile}.tif" for tile in _tile_descriptions(task_status, description)]
        if not tile_files or any(not _qa_row_passed(qa_by_file.get(tile_file)) for tile_file in tile_files):
            failed_qa.append(filename)
    add_check("geotiff_local_qa_passed", not failed_qa, f"Missing or failed GeoTIFF QA rows: {failed_qa}")

    ok = all(check["ok"] for check in checks)
    return {
        "ok": ok,
        "status": "golden_ready" if ok else "not_ready",
        "claim_boundary": "Golden readiness requires task completion, Drive readback, local QA, figures, and no ground-truth overclaim.",
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = audit(Path(args.out))
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{payload['status']}: {sum(1 for check in payload['checks'] if check['ok'])}/{len(payload['checks'])} checks passed")
        for check in payload["checks"]:
            if not check["ok"]:
                print(f"- {check['name']}: {check['detail']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
