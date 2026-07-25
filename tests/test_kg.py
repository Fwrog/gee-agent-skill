from pathlib import Path

from geeskill.kg import build_graph, explain_topic, graph_to_mermaid, neighbors, search_nodes, shortest_path, validate_graph


def test_build_and_validate_graph():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    report = validate_graph(graph)
    assert report["ok"], report
    assert report["node_count"] >= 25
    assert report["edge_count"] >= 25
    assert graph.metadata["seed_path"] == "references/graph/seed_graph.yml"
    assert "\\" not in graph.metadata["seed_path"]
    assert not Path(graph.metadata["seed_path"]).is_absolute()


def test_graph_search_finds_product_intercomparison():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    hits = search_nodes(graph, "HLS MODIS product intercomparison", top_k=10)
    ids = {hit["id"] for hit in hits}
    assert "workflow:product_intercomparison" in ids or "validation_demo:hk_2024_hls_modis_ndvi_v03" in ids


def test_graph_neighbors_and_path_include_claim_boundary():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    bundle = neighbors(graph, "validation_demo:hk_2024_hls_modis_ndvi_v03", depth=1)
    assert any(node["id"] == "claim_boundary:product_intercomparison_not_ground_truth" for node in bundle["nodes"])
    path = shortest_path(
        graph,
        "validation_demo:hk_2024_hls_modis_ndvi_v03",
        "claim_boundary:product_intercomparison_not_ground_truth",
    )
    assert path


def test_graph_explain_and_mermaid():
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    explanation = explain_topic(graph, "product_intercomparison")
    assert explanation["nodes"]
    assert "claim" in explanation["summary"].lower()
    mermaid = graph_to_mermaid(graph, focus_node="workflow:product_intercomparison")
    assert "graph LR" in mermaid
