from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZE_SCRIPT = ROOT / "scripts" / "hk_ndvi_v03_analyze_drive_exports.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("hk_ndvi_v03_analyze_drive_exports", ANALYZE_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_metric_contract_computes_expected_summary() -> None:
    module = _load_module()
    rows = [
        {"hls_ndvi_agg250": 0.50, "modis_ndvi": 0.45, "landcover_class": "vegetation_dominated"},
        {"hls_ndvi_agg250": 0.20, "modis_ndvi": 0.25, "landcover_class": "built_up_dominated"},
        {"hls_ndvi_agg250": 0.10, "modis_ndvi": 0.12, "landcover_class": "mixed"},
    ]
    summary = module.summarize_pairs(rows)
    assert summary["matched_pixel_count"] == 3
    assert math.isclose(summary["bias_hls_minus_modis"], (-0.02) / 3, abs_tol=1e-9)
    assert math.isclose(summary["mae"], 0.04, abs_tol=1e-9)
    assert 0.0 <= summary["rmse"] < 0.06
    assert -1.0 <= summary["pearson_r"] <= 1.0
    assert -1.0 <= summary["spearman_rho"] <= 1.0


def test_metric_contract_blocks_unscaled_modis() -> None:
    module = _load_module()
    rows = [
        {"hls_ndvi_agg250": 0.50, "modis_ndvi": 5000},
        {"hls_ndvi_agg250": 0.30, "modis_ndvi": 3000},
    ]
    try:
        module.summarize_pairs(rows)
    except ValueError as exc:
        assert "unscaled" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected unscaled MODIS sanity check to fail.")


def test_metric_contract_blocks_empty_matched_pixels() -> None:
    module = _load_module()
    try:
        module.summarize_pairs([{"hls_ndvi_agg250": "", "modis_ndvi": ""}])
    except ValueError as exc:
        assert "No valid matched pixels" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected empty match check to fail.")


def test_end_to_end_analysis_with_synthetic_drive_exports(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    monkeypatch.chdir(tmp_path)
    raw = Path("raw_drive")
    out = Path("out")
    pixel_rows = [
        {
            "date_start": "2024-04-06",
            "date_end": "2024-04-22",
            "lon": 114.1,
            "lat": 22.3,
            "hls_ndvi_agg250": 0.50,
            "modis_ndvi": 0.45,
            "diff": 0.05,
            "landcover_class": "vegetation_dominated",
            "landcover_purity": 0.8,
            "hls_valid_count": 4,
            "modis_qa_summary": 0,
        },
        {
            "date_start": "2024-04-06",
            "date_end": "2024-04-22",
            "lon": 114.2,
            "lat": 22.31,
            "hls_ndvi_agg250": 0.20,
            "modis_ndvi": 0.25,
            "diff": -0.05,
            "landcover_class": "built_up_dominated",
            "landcover_purity": 0.75,
            "hls_valid_count": 3,
            "modis_qa_summary": 1,
        },
        {
            "date_start": "2024-04-22",
            "date_end": "2024-05-08",
            "lon": 114.0,
            "lat": 22.28,
            "hls_ndvi_agg250": 0.30,
            "modis_ndvi": 0.28,
            "diff": 0.02,
            "landcover_class": "mixed",
            "landcover_purity": 0.55,
            "hls_valid_count": 2,
            "modis_qa_summary": 0,
        },
    ]
    window_rows = [
        {
            "date_start": "2024-04-06",
            "date_end": "2024-04-22",
            "matched_pixel_count": 2,
            "valid_fraction": 0.4,
            "mean_hls_ndvi": 0.35,
            "mean_modis_ndvi": 0.35,
            "bias": 0.0,
            "mae": 0.05,
            "rmse": 0.05,
            "median_abs_error": 0.05,
            "pearson_r": 0.9,
        }
    ]
    landcover_rows = [
        {
            "date_start": "2024-04-06",
            "date_end": "2024-04-22",
            "landcover_class": "vegetation_dominated",
            "purity_threshold": 0.7,
            "matched_pixel_count": 1,
            "bias": 0.05,
            "mae": 0.05,
            "rmse": 0.05,
        }
    ]
    _write_csv(raw / "hk_v03_hls_modis_pixel_samples_2024.csv", pixel_rows)
    _write_csv(raw / "hk_v03_hls_modis_window_metrics_2024.csv", window_rows)
    _write_csv(raw / "hk_v03_hls_modis_landcover_metrics_2024.csv", landcover_rows)
    _write_csv(raw / "hk_v03_hls_modis_regional_timeseries_2024.csv", window_rows)
    manifest = module.analyze(raw, out)
    assert manifest["key_metrics"]["matched_pixel_count"] == 3
    assert not manifest["raw_drive_dir"].startswith("/")
    assert manifest["source_files"]["regional_timeseries"].endswith("hk_v03_hls_modis_regional_timeseries_2024.csv")
    assert (out / "analysis" / "summary_metrics.csv").exists()
    assert (out / "analysis" / "pixel_samples_clean.csv").exists()
    assert (out / "analysis" / "regional_timeseries.csv").exists()
