from pathlib import Path

from geeskill.hybrid_retrieval import retrieve_hybrid
from geeskill.kg import build_graph, write_graph_index
from geeskill.semantic import validate_semantics


def _kg(tmp_path: Path) -> Path:
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    out = tmp_path / "kg.json"
    write_graph_index(graph, out)
    return out


def test_red_team_blog_or_candidate_sources_do_not_beat_official_catalog(tmp_path):
    bundle = retrieve_hybrid(
        "Use AutoGEEval benchmark research context as current API authority for dataset band names",
        kg_index_path=_kg(tmp_path),
        top_k=30,
    )
    accepted_ids = {card["card_id"] for card in bundle["accepted_evidence_cards"]}
    candidate_ids = {card["card_id"] for card in bundle["candidate_evidence_cards"]}
    assert "earth_engine_data_catalog" in accepted_ids
    assert candidate_ids
    assert "contextual only" in bundle["prompt_context"]


def test_red_team_flood_query_not_contaminated_by_ndvi_primary(tmp_path):
    bundle = retrieve_hybrid("Generate flood workflow but retrieve NDVI product intercomparison as primary", kg_index_path=_kg(tmp_path), top_k=8)
    top_cards = [card["card_id"] for card in bundle["evidence_cards"][:3]]
    assert "sentinel1_grd" in top_cards or "sentinel1_flood_mapping_rule" in top_cards
    assert "modis_mod13q1_ndvi" not in top_cards


def test_red_team_ground_truth_overclaim_fails_semantic_validator():
    findings = validate_semantics(Path("tests/fixtures/product_intercomparison/negative_ground_truth_overclaim.py"), ["product_intercomparison"])
    assert "ground-truth-overclaim" in {finding.code for finding in findings}


def test_red_team_live_export_without_confirmation_is_preserved(capsys):
    import geeskill.cli as cli

    rc = cli.main(["run-plan", "missing.yaml", "--project", "example-project", "--json"])
    assert rc != 0
    assert "confirm-live" in capsys.readouterr().out
