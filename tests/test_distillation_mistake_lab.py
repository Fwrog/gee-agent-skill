from pathlib import Path

from scripts.run_distillation_mistake_lab import run_suite


def test_mistake_lab_reproduces_and_prioritizes_omissions():
    report = run_suite(Path("evals/distillation_mistake_suite.yml"))

    assert report["ok"], report
    assert report["summary"]["case_count"] == 17
    assert report["summary"]["passed"] == 17
    assert report["summary"]["important_misses"] > report["summary"]["general_misses"]
    assert "data_usage_promotion_contract" in report["summary"]["important_distillation_targets"]
    assert "community_dataset_asset_boundary" in report["summary"]["important_distillation_targets"]
    assert "source_tier_precedence_regression" in report["summary"]["important_distillation_targets"]
    assert "domain_relevance_gate" in report["summary"]["important_distillation_targets"]
    assert "benchmark_dataset_protocol_contract" in report["summary"]["important_distillation_targets"]
    assert "geospatial_ml_dataset_generation_contract" in report["summary"]["important_distillation_targets"]
    assert "real_project_failure_distillation_boundary" in report["summary"]["important_distillation_targets"]
    assert "nonempty_evaluation_gate" in report["summary"]["important_distillation_targets"]
    assert all(not result["missing_distillation_targets"] for result in report["results"])
    assert all(result["simulated_failure"] and result["promotion_decision"] for result in report["results"])
    assert all(result["missed_ids"] for result in report["results"])
