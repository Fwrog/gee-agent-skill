from pathlib import Path

from geeskill.hybrid_retrieval import retrieve_hybrid
from geeskill.kg import build_graph, write_graph_index


def _write_test_graph(tmp_path: Path) -> Path:
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    out = tmp_path / "gee_kg_index.json"
    write_graph_index(graph, out)
    return out


def test_hybrid_retrieval_returns_scale_factor_evidence(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("MODIS NDVI scale factor", kg_index_path=kg_path, top_k=5)
    assert bundle["text_evidence"]
    assert any(card["card_id"] == "modis_mod13q1_ndvi" for card in bundle["evidence_cards"])
    assert any("0.0001" in " ".join(card["facts"]) for card in bundle["evidence_cards"])
    assert bundle["source_quality_summary"]["tier_a_count"] >= 1


def test_hybrid_retrieval_includes_claim_boundary_for_direct_comparison(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid(
        "Can I directly compare 30m HLS pixels with 250m MODIS pixels?",
        kg_index_path=kg_path,
        top_k=8,
    )
    joined = " ".join(bundle["claim_boundaries"] + bundle["known_failure_cases"] + [bundle["prompt_context"]]).lower()
    assert "product" in joined
    assert "ground-truth" in joined or "ground truth" in joined
    assert "insufficient evidence" in bundle["prompt_context"]


def test_hybrid_retrieval_mentions_official_source_precedence(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("authoritative source for dataset band names", kg_index_path=kg_path, top_k=6)
    assert any(card["card_id"] == "earth_engine_data_catalog" for card in bundle["evidence_cards"])
    assert bundle["source_quality_summary"]["tier_a_count"] >= 1


def test_hybrid_retrieval_routes_flood_mapping_to_sentinel1_not_product_intercomparison(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("Generate a GEE workflow for flood mapping", kg_index_path=kg_path, top_k=16)
    card_ids = {card["card_id"] for card in bundle["evidence_cards"]}
    node_ids = {node["id"] for node in bundle["graph_nodes"]}
    rules = " ".join(bundle["required_rules"]).lower()
    boundaries = " ".join(bundle["claim_boundaries"]).lower()
    assert {"sentinel1_grd", "sentinel1_flood_mapping_rule"}.issubset(card_ids)
    assert "workflow:flood_mapping" in node_ids
    assert "workflow:product_intercomparison" not in node_ids
    assert "do not route flood mapping to ndvi" in rules
    assert "screening" in boundaries
