from geeskill.cli import main


def test_evaluate_benchmark_suite_runs(capsys):
    rc = main(["evaluate", "evals/benchmark_suite.yml"])
    assert rc == 0
    assert "gee_harness_benchmark_v0.3" in capsys.readouterr().out
