from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "scripts" / "hk_ndvi_v03_readiness_audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("hk_ndvi_v03_readiness_audit", AUDIT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_readiness_audit_reports_current_golden_state() -> None:
    module = _load_module()
    payload = module.audit(ROOT / "outputs" / "hk_ndvi_product_validation_v03")
    assert payload["status"] == "golden_ready"
    assert all(check["ok"] for check in payload["checks"])
    passed = {check["name"] for check in payload["checks"] if check["ok"]}
    assert "no_pending_tasks" in passed
    assert "required_geotiff_tasks_completed" in passed
    assert "required_geotiffs_downloaded" in passed
    assert "geotiff_local_qa_passed" in passed


def test_readiness_audit_can_pass_on_complete_synthetic_evidence(tmp_path: Path) -> None:
    module = _load_module()
    out = tmp_path / "demo"
    figures = out / "figures"
    figures.mkdir(parents=True)
    for figure in module.REQUIRED_FIGURES:
        (out / figure).write_bytes(b"png")
    geotiff_dir = out / "raw_drive" / "geotiff"
    geotiff_dir.mkdir(parents=True)
    for geotiff in module.REQUIRED_GEOTIFFS:
        (geotiff_dir / geotiff).write_bytes(b"tif")
    _write_json(
        out / "manifest.json",
        {
            "analysis_type": "product_intercomparison_not_ground_truth",
            "claim_boundary": "Product-level consistency validation only; no in-situ ground truth is used.",
            "snapshot_status": "complete_for_csv_tables",
            "key_metrics": {"matched_pixel_count": 10},
            "geotiff_local_qa": [
                {"file": geotiff, "ndvi_sanity_nonzero_within_minus1_1": True}
                for geotiff in module.REQUIRED_GEOTIFFS
            ],
        },
    )
    _write_json(
        out / "task_status_latest.json",
        {
            "summary": {"pending_count": 0},
            "tasks": [
                {"description": description, "state": "COMPLETED"}
                for description in [
                    "hk_v03_annual_hls30_ndvi_mean_2024",
                    "hk_v03_annual_hls_agg250_ndvi_mean_2024",
                    "hk_v03_annual_modis250_ndvi_mean_2024",
                    "hk_v03_annual_diff_hlsagg_minus_modis_2024",
                    "hk_v03_valid_count_250m_2024",
                ]
            ],
        },
    )
    (out / "VALIDATION_REPORT.md").write_text("report", encoding="utf-8")
    payload = module.audit(out)
    assert payload["status"] == "golden_ready"
    assert all(check["ok"] for check in payload["checks"])


def test_readiness_audit_accepts_complete_tile_set_for_a_required_geotiff(tmp_path: Path) -> None:
    module = _load_module()
    out = tmp_path / "demo"
    for figure in module.REQUIRED_FIGURES:
        (out / figure).parent.mkdir(parents=True, exist_ok=True)
        (out / figure).write_bytes(b"png")
    geotiff_dir = out / "raw_drive" / "geotiff"
    geotiff_dir.mkdir(parents=True)
    tiled_base = "hk_v03_annual_hls_agg250_ndvi_mean_2024"
    tile_names = [f"{tiled_base}_tile_r01_c01.tif", f"{tiled_base}_tile_r01_c02.tif"]
    for geotiff in module.REQUIRED_GEOTIFFS:
        if geotiff == f"{tiled_base}.tif":
            continue
        (geotiff_dir / geotiff).write_bytes(b"tif")
    for geotiff in tile_names:
        (geotiff_dir / geotiff).write_bytes(b"tif")
    qa_files = [geotiff for geotiff in module.REQUIRED_GEOTIFFS if geotiff != f"{tiled_base}.tif"] + tile_names
    _write_json(
        out / "manifest.json",
        {
            "analysis_type": "product_intercomparison_not_ground_truth",
            "claim_boundary": "Product-level consistency validation only; no in-situ ground truth is used.",
            "snapshot_status": "complete_for_csv_tables",
            "key_metrics": {"matched_pixel_count": 10},
            "geotiff_local_qa": [{"file": geotiff, "ndvi_sanity_nonzero_within_minus1_1": True} for geotiff in qa_files],
        },
    )
    completed_descriptions = [
        "hk_v03_annual_hls30_ndvi_mean_2024",
        "hk_v03_annual_modis250_ndvi_mean_2024",
        "hk_v03_annual_diff_hlsagg_minus_modis_2024",
        "hk_v03_valid_count_250m_2024",
        f"{tiled_base}_tile_r01_c01",
        f"{tiled_base}_tile_r01_c02",
    ]
    _write_json(
        out / "task_status_latest.json",
        {
            "summary": {"pending_count": 0},
            "tasks": [{"description": description, "state": "COMPLETED"} for description in completed_descriptions],
        },
    )
    (out / "VALIDATION_REPORT.md").write_text("report", encoding="utf-8")
    payload = module.audit(out)
    assert payload["status"] == "golden_ready"
    assert all(check["ok"] for check in payload["checks"])
