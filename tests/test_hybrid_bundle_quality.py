from pathlib import Path

from geeskill.hybrid_retrieval import retrieve_hybrid
from geeskill.kg import build_graph, write_graph_index


def _kg(tmp_path: Path) -> Path:
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    out = tmp_path / "kg.json"
    write_graph_index(graph, out)
    return out


def test_hybrid_bundle_splits_accepted_and_candidate_evidence(tmp_path):
    bundle = retrieve_hybrid("AutoGEEval benchmark research context", kg_index_path=_kg(tmp_path), top_k=8)
    assert bundle["query_classification"] == "research_context"
    assert "accepted_evidence_cards" in bundle
    assert "candidate_evidence_cards" in bundle
    assert bundle["candidate_evidence_cards"]
    assert "Candidate evidence cards:" in bundle["prompt_context"]


def test_hybrid_bundle_exposes_source_metadata_and_claim_paths(tmp_path):
    bundle = retrieve_hybrid("Can I directly compare 30m HLS pixels with 250m MODIS pixels?", kg_index_path=_kg(tmp_path), top_k=10)
    card = bundle["accepted_evidence_cards"][0]
    for field in ("source_url", "last_checked", "reviewer_status", "allowed_use", "source_refresh_status"):
        assert card.get(field)
    assert bundle["graph_paths"]
    assert bundle["source_quality_summary"]["accepted_count"] >= 1


def test_hybrid_bundle_warns_on_private_asset_request(tmp_path):
    bundle = retrieve_hybrid("Use private asset users/example/private_aoi for validation", kg_index_path=_kg(tmp_path), top_k=8)
    assert bundle["source_quality_summary"]["insufficient_evidence"] is True
    assert any("private Earth Engine asset" in warning for warning in bundle["warnings"])
