from pathlib import Path

from geeskill.evidence import load_evidence_cards, search_evidence_cards
from geeskill.kg import build_graph, search_nodes


def test_evidence_alias_ranking_promotes_modis_scale_factor():
    cards = load_evidence_cards(Path("references/evidence_cards"))
    results = search_evidence_cards("MODIS NDVI scale factor", cards, top_k=5)
    assert results[0]["card_id"] in {"modis_mod13q1_ndvi", "modis_ndvi_scale_factor_rule"}
    assert any("MODIS scale factor" in alias for alias in results[0].get("aliases", []))


def test_evidence_negative_routing_keeps_flood_primary():
    cards = load_evidence_cards(Path("references/evidence_cards"))
    results = search_evidence_cards("Generate a GEE workflow for flood mapping", cards, top_k=5)
    ids = [result["card_id"] for result in results]
    assert "sentinel1_grd" in ids[:3]
    assert "scale_aware_product_intercomparison_rule" not in ids[:3]


def test_kg_negative_routing_keeps_product_intercomparison_out_of_flood_top_hits():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    results = search_nodes(graph, "Sentinel-1 flood mapping", top_k=8)
    ids = [result["id"] for result in results]
    assert "workflow:flood_mapping" in ids
    assert "workflow:product_intercomparison" not in ids[:5]
