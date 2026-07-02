#!/usr/bin/env python3
"""Monitor Earth Engine tasks for the Hong Kong v0.3 NDVI validation demo.

This script records task-state evidence for the public v0.3 validation loop.
It does not inspect Google Drive files; Drive readback remains a separate
connector-mediated step.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


DEFAULT_OUT = Path("outputs/hk_ndvi_product_validation_v03")
DEFAULT_MANIFEST = DEFAULT_OUT / "manifest.json"
DRIVE_FOLDER = "GEE_SKILL_V03_HK_NDVI_VALIDATION"
SOURCE_ASSETS = [
    "NASA/HLS/HLSL30/v002",
    "NASA/HLS/HLSS30/v002",
    "MODIS/061/MOD13Q1",
    "ESA/WorldCover/v200",
]

FALLBACK_TASKS = [
    {"description": "hk_v03_hls_modis_window_metrics_2024", "task_id": "NZPMV2LZWZYIDDHKX2U5N5EY", "artifact_type": "csv", "scale_m": 250, "crs": "MODIS native projection per 16-day window"},
    {"description": "hk_v03_hls_modis_pixel_samples_2024", "task_id": "JZDJPO4ADANSXUOASEPEHPSM", "artifact_type": "csv", "scale_m": 250, "crs": "MODIS native projection per 16-day window"},
    {"description": "hk_v03_hls_modis_landcover_metrics_2024", "task_id": "27OETEPLZVXX5B2LESC36NO3", "artifact_type": "csv", "scale_m": 250, "crs": "MODIS native projection per 16-day window"},
    {"description": "hk_v03_hls_modis_regional_timeseries_2024", "task_id": "GIYMEDUSFVSTQVRTUBN36CI7", "artifact_type": "csv", "scale_m": 250, "crs": "MODIS native projection per 16-day window"},
    {"description": "hk_v03_annual_hls30_ndvi_mean_2024", "task_id": "DFY3P4V72EBGVKOFNGJQT747", "artifact_type": "geotiff", "scale_m": 30, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_hls_agg250_ndvi_mean_2024", "task_id": "RTT3QTY4U7A3HFBKHYWL35HD", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_modis250_ndvi_mean_2024", "task_id": "ML4IF7QOIP63AAPJ6TXUZJAG", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_diff_hlsagg_minus_modis_2024", "task_id": "VYV4QDICIAKQPL62IRE5UAFF", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_valid_count_250m_2024", "task_id": "BA2TTOVRKJVETTLQ75SSXVXP", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_hls_agg250_ndvi_mean_2024", "task_id": "N6W3SDLSY5WFVL4IS3O7KRKR", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_diff_hlsagg_minus_modis_2024", "task_id": "CVTRNEIT2KS63EXWQA3MRFRO", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_valid_count_250m_2024", "task_id": "4F2UKFOXHRFLOQD2OUESYMCC", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_hls_agg250_ndvi_mean_2024", "task_id": "B3Y2SVOFJNVVHP4Q5BTL42O6", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    {"description": "hk_v03_annual_diff_hlsagg_minus_modis_2024", "task_id": "W2WWGA4D7LUQK3FPZAM54THJ", "artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
]
TASK_METADATA_BY_DESCRIPTION = {task["description"]: task for task in FALLBACK_TASKS}
TILE_METADATA_PREFIXES = {
    "hk_v03_annual_hls_agg250_ndvi_mean_2024_tile_": {"artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    "hk_v03_annual_diff_hlsagg_minus_modis_2024_tile_": {"artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
    "hk_v03_valid_count_250m_2024_tile_": {"artifact_type": "geotiff", "scale_m": 250, "crs": "EPSG:4326"},
}


def _metadata_for_description(description: str) -> dict[str, Any]:
    exact = TASK_METADATA_BY_DESCRIPTION.get(description)
    if exact:
        return exact
    for prefix, metadata in TILE_METADATA_PREFIXES.items():
        if description.startswith(prefix):
            return metadata
    return {}


def _import_ee() -> Any:
    try:
        import ee  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised only without EE.
        raise RuntimeError("earthengine-api is required. Install with pip install -e '.[earthengine]'.") from exc
    return ee


def _tasks_from_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_tasks = manifest.get("earth_engine_tasks") or manifest.get("tasks") or []
    tasks: list[dict[str, Any]] = []
    for item in raw_tasks:
        task_id = item.get("task_id") or item.get("id")
        description = item.get("description")
        if task_id and description:
            fallback = _metadata_for_description(str(description))
            tasks.append(
                {
                    "description": str(description),
                    "task_id": str(task_id),
                    "artifact_type": str(item.get("artifact_type", fallback.get("artifact_type", "unknown"))),
                    "scale_m": item.get("scale_m", fallback.get("scale_m")),
                    "crs": str(item.get("crs", fallback.get("crs", "unknown"))),
                }
            )
    return tasks


def _load_tasks(manifest_path: Path) -> list[dict[str, Any]]:
    tasks = _tasks_from_manifest(manifest_path)
    if manifest_path == DEFAULT_MANIFEST and DEFAULT_OUT.exists():
        for extra_manifest in sorted(DEFAULT_OUT.glob("*/manifest.json")):
            tasks.extend(_tasks_from_manifest(extra_manifest))
    if not tasks:
        return FALLBACK_TASKS
    known_ids = {task["task_id"] for task in tasks}
    for fallback in FALLBACK_TASKS:
        if fallback["task_id"] not in known_ids:
            tasks.append(fallback)
    deduped: dict[str, dict[str, Any]] = {}
    for task in tasks:
        task_id = task["task_id"]
        previous = deduped.get(task_id)
        if previous is None:
            deduped[task_id] = task
            continue
        if previous.get("artifact_type") == "unknown" and task.get("artifact_type") != "unknown":
            deduped[task_id] = task
    return list(deduped.values())


def _initialize_ee(project: str | None) -> Any:
    ee = _import_ee()
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()
    return ee


def monitor(manifest_path: Path, out_dir: Path, *, project: str | None = None, write: bool = True) -> dict[str, Any]:
    ee = _initialize_ee(project)
    tasks = _load_tasks(manifest_path)
    checked_utc = dt.datetime.now(dt.UTC).isoformat()
    rows: list[dict[str, Any]] = []
    for task in tasks:
        status = ee.data.getTaskStatus(task["task_id"])[0]
        rows.append(
            {
                "description": task["description"],
                "task_id": task["task_id"],
                "artifact_type": task["artifact_type"],
                "drive_folder": DRIVE_FOLDER,
                "source_assets": SOURCE_ASSETS,
                "crs": task.get("crs"),
                "scale_m": task.get("scale_m"),
                "claim_boundary": "Product-level consistency validation; not in-situ ground-truth validation.",
                "state": status.get("state"),
                "error_message": status.get("error_message"),
                "creation_timestamp_ms": status.get("creation_timestamp_ms"),
                "update_timestamp_ms": status.get("update_timestamp_ms"),
            }
        )
    states = {}
    for row in rows:
        state = str(row.get("state"))
        states[state] = states.get(state, 0) + 1
    pending = [row for row in rows if row.get("state") in {"READY", "RUNNING"}]
    failed = [row for row in rows if row.get("state") == "FAILED"]
    payload = {
        "demo_id": "hk_ndvi_product_validation_v03",
        "checked_utc": checked_utc,
        "drive_folder": DRIVE_FOLDER,
        "claim_boundary": "Task completion evidence only; Drive readback and product validation are separate checks.",
        "summary": {
            "total": len(rows),
            "states": states,
            "pending_count": len(pending),
            "failed_count": len(failed),
            "all_terminal": not pending,
        },
        "tasks": rows,
    }
    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        latest = out_dir / "task_status_latest.json"
        stamped = out_dir / f"task_status_{checked_utc.replace(':', '').replace('-', '').replace('+', 'Z')}.json"
        latest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        stamped.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        payload["written_files"] = [str(latest), str(stamped)]
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Manifest containing Earth Engine task ids.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Directory for task status JSON snapshots.")
    parser.add_argument("--project", default=None, help="Google Cloud project for ee.Initialize(project=...).")
    parser.add_argument("--no-write", action="store_true", help="Print status without writing JSON snapshots.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    payload = monitor(Path(args.manifest), Path(args.out), project=args.project, write=not args.no_write)
    if args.json:
        print(json.dumps({"ok": True, "data": payload}, indent=2, ensure_ascii=False))
    else:
        summary = payload["summary"]
        print(f"Checked {summary['total']} tasks; states={summary['states']}; pending={summary['pending_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
