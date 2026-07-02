from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_STATUS_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "docs" / "roadmap.md",
    ROOT / "docs" / "capability_matrix.md",
    ROOT / "docs" / "validation" / "hk_ndvi_product_intercomparison_v03.md",
    ROOT / "outputs" / "hk_ndvi_product_validation_v03" / "VALIDATION_REPORT.md",
]


def test_hk_ndvi_v03_public_status_is_consistently_golden_after_geotiff_readback() -> None:
    for path in PUBLIC_STATUS_FILES:
        text = path.read_text(encoding="utf-8")
        assert "v0.3" in text or "V03" in text, path
        assert "Golden" in text or "golden_ready" in text, path
        assert "GeoTIFF" in text, path


def test_hk_ndvi_v03_public_docs_ground_golden_status_in_evidence() -> None:
    for path in PUBLIC_STATUS_FILES:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert (
            "drive readback" in lowered
            or "read back from google drive" in lowered
            or "google drive readback" in lowered
            or "google drive 回读" in lowered
        ), path
        assert "readiness audit" in lowered or "golden_ready" in lowered, path
        assert (
            "local qa" in lowered
            or "raster qa" in lowered
            or "raster sanity" in lowered
            or "sanity checks" in lowered
            or "本地 qa" in lowered
        ), path


def test_hk_ndvi_v03_public_docs_keep_validation_claim_boundary() -> None:
    for path in PUBLIC_STATUS_FILES:
        text = path.read_text(encoding="utf-8").lower()
        assert "product" in text, path
        assert "ground-truth" in text or "ground truth" in text, path
        assert (
            "not in-situ" in text
            or "rather than in-situ" in text
            or "no in-situ" in text
            or "不是 in-situ" in text
            or "不是 ground-truth" in text
        ), path
