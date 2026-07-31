import json

from geeskill.cli import main


def test_evaluate_benchmark_suite_runs(capsys):
    rc = main(["evaluate", "evals/benchmark_suite.yml"])
    assert rc == 0
    assert "gee_harness_benchmark_v0.3" in capsys.readouterr().out


def test_eval_rejects_case_based_suite_instead_of_passing_zero_cases(capsys):
    rc = main(["eval", "evals/kg_rag_retrieval_suite.yml", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert rc == 1
    assert payload["error"]["code"] == "EVAL_FAILED"
    assert "scripts/run_kg_rag_eval.py" in payload["error"]["message"]
