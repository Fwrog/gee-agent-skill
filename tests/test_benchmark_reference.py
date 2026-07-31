from pathlib import Path

import yaml

from geeskill.evaluation import run_benchmark_suite


SUITE = Path("evals/benchmark_quick_reference.yml")


def test_quick_reference_suite_declares_non_comparability():
    data = yaml.safe_load(SUITE.read_text(encoding="utf-8"))
    reference = data["reference"]
    assert reference["source_id"] == "autogeeval-plus-paper"
    assert reference["comparable_to_external_scores"] is False
    assert {task["level"] for task in data["tasks"]} == {"unit", "combination", "theme"}
    assert any(task.get("boundary") for task in data["tasks"])


def test_quick_reference_suite_passes_by_level():
    result = run_benchmark_suite(SUITE)
    assert result["ok"], result
    assert result["summary"]["levels"] == {
        "combination": {"count": 2, "passed": 2},
        "theme": {"count": 2, "passed": 2},
        "unit": {"count": 3, "passed": 3},
    }
    assert result["summary"]["boundary_count"] == 2
