import json
from pathlib import Path

from geeskill.cli import main
from geeskill.kg import build_graph, write_graph_index


def _ensure_kg_index():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    Path("references/index").mkdir(parents=True, exist_ok=True)
    write_graph_index(graph, Path("references/index/gee_kg_index.json"))


def test_cli_sources_validate_json(capsys):
    rc = main(["sources", "validate", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "sources validate"


def test_cli_evidence_search_json(capsys):
    rc = main(["evidence", "search", "MODIS NDVI scale factor", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["results"]
    assert payload["data"]["results"][0]["card_id"] in {"modis_mod13q1_ndvi", "modis_ndvi_scale_factor_rule"}


def test_cli_kg_search_and_explain_json(capsys):
    _ensure_kg_index()
    rc = main(["kg", "search", "HLS MODIS product intercomparison", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["results"]
    rc = main(["kg", "explain", "product_intercomparison", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["nodes"]


def test_cli_retrieve_hybrid_json(capsys):
    _ensure_kg_index()
    rc = main(["retrieve", "hybrid", "Can I directly compare 30m HLS pixels with 250m MODIS pixels?", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "retrieve hybrid"
    assert payload["data"]["claim_boundaries"]
