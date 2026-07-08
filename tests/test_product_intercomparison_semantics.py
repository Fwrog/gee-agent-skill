from pathlib import Path

from geeskill.semantic import validate_semantics


FIXTURES = Path("tests/fixtures/product_intercomparison")


def _codes(name: str) -> set[str]:
    return {finding.code for finding in validate_semantics(FIXTURES / name, ["product_intercomparison"])}


def test_positive_product_intercomparison_fixture_passes():
    codes = _codes("positive_hls_modis_product_intercomparison.py")
    assert "semantic-validation-ok" in codes
    assert not {
        "modis-ndvi-scale-factor",
        "modis-qa-policy",
        "hls-fmask-policy",
        "fine-coarse-aggregation-required",
        "reduce-resolution-projection",
        "claim-boundary-required",
        "ground-truth-overclaim",
    }.intersection(codes)


def test_negative_product_intercomparison_fixtures_fail_expected_rules():
    expected = {
        "negative_missing_modis_scale_factor.py": "modis-ndvi-scale-factor",
        "negative_missing_modis_qa.py": "modis-qa-policy",
        "negative_missing_hls_fmask.py": "hls-fmask-policy",
        "negative_direct_fine_coarse.py": "fine-coarse-aggregation-required",
        "negative_reduce_resolution_no_projection.py": "reduce-resolution-projection",
        "negative_missing_claim_boundary.py": "claim-boundary-required",
        "negative_ground_truth_overclaim.py": "ground-truth-overclaim",
    }
    for fixture, code in expected.items():
        assert code in _codes(fixture), fixture


def test_product_intercomparison_ignores_comment_only_scale_factor(tmp_path):
    script = tmp_path / "comment_only.py"
    script.write_text(
        '''
import ee
# apply 0.0001 scale factor and SummaryQA and Fmask and reproject in the real script
CLAIM_BOUNDARY = "product-level consistency; not in-situ ground-truth accuracy"
HLS = "NASA/HLS/HLSL30/v002"
MODIS = "MODIS/061/MOD13Q1"
def main():
    hls = ee.ImageCollection(HLS).select("B5").mean()
    modis = ee.ImageCollection(MODIS).select("NDVI").mean()
    return hls.subtract(modis)
''',
        encoding="utf-8",
    )
    codes = {finding.code for finding in validate_semantics(script, ["product_intercomparison"])}
    assert "modis-ndvi-scale-factor" in codes
    assert "modis-qa-policy" in codes
    assert "hls-fmask-policy" in codes
