from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "examples" / "hk_ndvi_product_validation_v03" / "hk_ndvi_product_validation.recipe.yaml"
EXPORT_SCRIPT = ROOT / "scripts" / "hk_ndvi_v03_export.py"


def _load_export_module():
    spec = importlib.util.spec_from_file_location("hk_ndvi_v03_export", EXPORT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hk_ndvi_v03_recipe_contract() -> None:
    recipe = yaml.safe_load(RECIPE.read_text(encoding="utf-8"))
    assert recipe["claim_boundary"] == "product_intercomparison_not_ground_truth"
    assert recipe["drive_folder"] == "GEE_SKILL_V03_HK_NDVI_VALIDATION"
    datasets = recipe["datasets"]
    assert datasets["high_resolution"][0]["id"] == "NASA/HLS/HLSL30/v002"
    assert datasets["high_resolution"][0]["red"] == "B4"
    assert datasets["high_resolution"][0]["nir"] == "B5"
    assert datasets["high_resolution"][1]["id"] == "NASA/HLS/HLSS30/v002"
    assert datasets["high_resolution"][1]["nir_default"] == "B8A"
    assert datasets["official_product"]["id"] == "MODIS/061/MOD13Q1"
    assert datasets["official_product"]["scale_factor"] == 0.0001
    assert datasets["stratification"]["id"] == "ESA/WorldCover/v200"
    assert "No direct 30 m HLS versus 250 m MODIS pixel comparison is allowed." in recipe["quality_gates"]


def test_hk_ndvi_v03_export_script_declares_expected_prefixes_and_safety_gate() -> None:
    text = EXPORT_SCRIPT.read_text(encoding="utf-8")
    for prefix in [
        "hk_v03_hls_modis_window_metrics_",
        "hk_v03_hls_modis_pixel_samples_",
        "hk_v03_hls_modis_landcover_metrics_",
        "hk_v03_hls_modis_regional_timeseries_",
        "hk_v03_annual_hls30_ndvi_mean_",
        "hk_v03_annual_hls_agg250_ndvi_mean_",
        "hk_v03_annual_modis250_ndvi_mean_",
        "hk_v03_annual_diff_hlsagg_minus_modis_",
        "hk_v03_valid_count_250m_",
    ]:
        assert prefix in text
    assert "--confirm-live" in text
    assert "task.start()" in text
    assert "multiply(0.0001)" in text
    assert "reduceResolution" in text
    assert "reproject(modis_projection)" in text
    assert "--annual-raster-strategy" in text
    assert "--tile-grid" in text
    assert "_tile_r" in text
    assert "low_memory" in text
    assert "setDefaultProjection(hls_30_projection)" in text
    assert "Fmask" in text
    assert "SummaryQA" in text
    assert "DetailedQA" in text


def test_hk_ndvi_v03_pixel_sample_schema_is_documented() -> None:
    text = EXPORT_SCRIPT.read_text(encoding="utf-8")
    for column in [
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
    ]:
        assert f'"{column}"' in text


def test_hk_ndvi_v03_tile_grid_parser_is_bounded() -> None:
    module = _load_export_module()
    assert module._parse_tile_grid("1x1") == (1, 1)
    assert module._parse_tile_grid("2x3") == (2, 3)
    try:
        module._parse_tile_grid("7x7")
    except ValueError as exc:
        assert "capped" in str(exc)
    else:  # pragma: no cover - defensive assertion.
        raise AssertionError("large tile grids should be rejected")
