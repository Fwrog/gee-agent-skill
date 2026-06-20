import json
from pathlib import Path

from geeskill.cli import main
from geeskill.tool_registry import exposed_tools, installed_tools


def test_tool_registry_separates_installed_and_exposed():
    installed = {item["name"]: item for item in installed_tools()}
    exposed = {item["name"]: item for item in exposed_tools()}
    assert "render_template" in installed
    assert "render_template" not in exposed
    assert exposed["run_live"]["dangerous"] is True
    assert "--confirm-live" in exposed["run_live"]["requires_explicit_flags"]


def test_plan_task_writes_complete_run_trace(tmp_path):
    run_id = "test-trace-plan"
    rc = main(["plan", "examples/hk_2024_monthly_ndvi/task.yaml", "--run-id", run_id])
    assert rc == 0
    run_dir = Path("outputs/runs") / run_id
    expected = [
        "task.yaml",
        "retrieval_trace.json",
        "plan.md",
        "generated_script.py",
        "validation_report.json",
        "dry_run_report.json",
        "environment.json",
        "final_report.md",
    ]
    for name in expected:
        assert (run_dir / name).exists(), name
    trace = json.loads((run_dir / "retrieval_trace.json").read_text(encoding="utf-8"))
    assert trace["evidence"]
    assert all("reason_for_selection" in item for item in trace["evidence"])
    assert "coverage" in trace
    required_evidence_keys = {
        "evidence_type",
        "source_path",
        "source_url",
        "last_checked",
        "primary_status",
        "reason_for_selection",
        "influence",
        "excerpt",
    }
    for item in trace["evidence"]:
        assert required_evidence_keys.issubset(item)
        assert item["last_checked"]
        assert item["reason_for_selection"]
        assert item["influence"]
        assert item["excerpt"]
    assert any(item["source_url"] for item in trace["evidence"])
    assert any(item["evidence_type"] == "operator_relationship_chain" for item in trace["evidence"])
    assert trace["coverage"]["known_failures"] >= 1
    validation = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert "semantic_rulesets" in validation
    dry_run = json.loads((run_dir / "dry_run_report.json").read_text(encoding="utf-8"))
    assert dry_run["contacted_earth_engine"] is False
    assert dry_run["validation_ok"] is True


def test_run_dry_writes_trace(tmp_path):
    main(["plan", "examples/hk_2024_monthly_ndvi/task.yaml", "--run-id", "test-dry-source"])
    script = Path("outputs/runs/test-dry-source/generated_script.py")
    rc = main(["run", str(script), "--dry-run", "--run-id", "test-dry-run", "--json"])
    assert rc == 0
    assert (Path("outputs/runs/test-dry-run/dry_run_report.json")).exists()
