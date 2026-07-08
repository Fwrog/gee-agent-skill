from pathlib import Path

from scripts.run_kg_rag_eval import run_suite


def test_v041_retrieval_eval_suite_runs():
    report = run_suite(Path("evals/kg_rag_retrieval_suite.yml"))
    assert report["case_count"] >= 10
    assert report["ok"] is True


def test_v041_planner_grounding_eval_suite_runs():
    report = run_suite(Path("evals/planner_research_grounding_suite.yml"))
    assert report["case_count"] >= 4
    assert report["ok"] is True


def test_v041_semantic_fixture_eval_suite_runs():
    report = run_suite(Path("evals/semantic_validator_fixture_suite.yml"))
    assert report["case_count"] >= 8
    assert report["ok"] is True
