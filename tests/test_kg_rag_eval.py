import subprocess
import sys
from pathlib import Path

from scripts.run_kg_rag_eval import run_suite
from geeskill.kg import build_graph, write_graph_index


def test_kg_rag_eval_suite_passes_after_building_index(tmp_path):
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    Path("references/index").mkdir(parents=True, exist_ok=True)
    write_graph_index(graph, Path("references/index/gee_kg_index.json"))
    result = run_suite(Path("evals/kg_rag_retrieval_suite.yml"))
    assert result["ok"], result


def test_kg_rag_eval_script_json():
    subprocess.run([sys.executable, "scripts/build_kg.py", "--json"], check=True, text=True, capture_output=True)
    result = subprocess.run(
        [sys.executable, "scripts/run_kg_rag_eval.py", "--suite", "evals/kg_rag_retrieval_suite.yml", "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    assert '"ok": true' in result.stdout
