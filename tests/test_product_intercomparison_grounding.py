from pathlib import Path

from geeskill.hybrid_retrieval import retrieve_hybrid
from geeskill.kg import build_graph, write_graph_index
from geeskill.planner import build_plan
from geeskill.rag import SearchResult


def _write_test_graph(tmp_path: Path) -> Path:
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    out = tmp_path / "gee_kg_index.json"
    write_graph_index(graph, out)
    return out


def test_product_intercomparison_plan_contains_kg_rag_grounding_hints(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("HLS MODIS product intercomparison", kg_index_path=kg_path, top_k=10)
    plan = build_plan(
        "Plan a source-grounded HLS MODIS product intercomparison",
        [
            SearchResult(
                chunk_id="doc:test",
                score=1.0,
                title="Product intercomparison reference",
                source_path="references/knowledge_base/workflows/test.md",
                url="https://example.com/source",
                excerpt="Use scale-aware aggregation before comparing products.",
                metadata={},
            )
        ],
        hybrid_bundle=bundle,
    )
    body = plan.body.lower()
    assert "kg-rag grounding hints" in body
    assert "scale-aware product intercomparison" in body
    assert "fmask" in body
    assert "0.0001" in body
    assert "not in-situ ground-truth accuracy" in body or "not ground-truth accuracy" in body


def test_product_intercomparison_bundle_routes_planner_and_validator_hints(tmp_path):
    kg_path = _write_test_graph(tmp_path)
    bundle = retrieve_hybrid("HLS MODIS product intercomparison", kg_index_path=kg_path, top_k=10)
    joined_planner = " ".join(bundle["planner_hints"]).lower()
    joined_validator = " ".join(bundle["validator_hints"]).lower()
    assert "modis" in joined_planner
    assert "hls" in joined_planner
    assert "qa" in joined_planner
    assert "scale" in joined_validator or "aggregation" in joined_validator
    assert bundle["claim_boundaries"]
