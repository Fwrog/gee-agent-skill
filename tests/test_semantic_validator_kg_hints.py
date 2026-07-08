from pathlib import Path

from geeskill.hybrid_retrieval import retrieve_hybrid
from geeskill.kg import build_graph, write_graph_index
from geeskill.semantic import validate_semantics


def _write_test_graph(tmp_path: Path) -> Path:
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    out = tmp_path / "gee_kg_index.json"
    write_graph_index(graph, out)
    return out


def test_semantic_product_intercomparison_findings_match_kg_validator_hints(tmp_path):
    script = tmp_path / "bad_product_intercomparison.py"
    script.write_text(
        """
import ee
HLS = 'NASA/HLS/HLSL30/v002'
MODIS = 'MODIS/061/MOD13Q1'
def main():
    hls = ee.ImageCollection(HLS).select('NDVI')
    modis = ee.ImageCollection(MODIS).select('NDVI')
    return hls.mean().subtract(modis.mean())
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["product_intercomparison"])
    codes = {item.code for item in findings}
    assert {
        "modis-ndvi-scale-factor",
        "modis-qa-policy",
        "hls-fmask-policy",
        "fine-coarse-aggregation-required",
        "claim-boundary-required",
    }.issubset(codes)

    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("HLS MODIS product intercomparison validator hints", kg_index_path=kg_path, top_k=10)
    hints = " ".join(bundle["validator_hints"] + bundle["required_rules"]).lower()
    assert "0.0001" in hints
    assert "fmask" in hints
    assert "qa" in hints
    assert "aggregation" in hints or "common grid" in hints
    assert bundle["claim_boundaries"]


def test_semantic_validator_warns_reduce_resolution_without_projection(tmp_path):
    script = tmp_path / "missing_projection.py"
    script.write_text(
        """
import ee
CLAIM_BOUNDARY = 'product_intercomparison_not_ground_truth'
HLS = 'NASA/HLS/HLSL30/v002'
MODIS = 'MODIS/061/MOD13Q1'
def main():
    hls = ee.ImageCollection(HLS).select('Fmask').mean()
    modis = ee.ImageCollection(MODIS).select('SummaryQA').mean()
    modis_ndvi = ee.ImageCollection(MODIS).select('NDVI').mean().multiply(0.0001)
    return hls.reduceResolution(reducer=ee.Reducer.mean()).subtract(modis_ndvi)
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["product_intercomparison"])
    codes = {item.code for item in findings}
    assert "reduce-resolution-projection" in codes
