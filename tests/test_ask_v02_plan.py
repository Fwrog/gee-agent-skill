import json
from pathlib import Path

import geeskill.cli as cli
from geeskill.ask import route_request
from geeskill.errors import error_payload
from geeskill.templates import load_context, render_template
from geeskill.validation import validate_script


def _payload(capsys):
    return json.loads(capsys.readouterr().out)


def test_route_request_recognizes_v02_landcover_variants():
    variants = [
        "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
        "Calculate Hong Kong January 2024 NDVI by land use.",
        "Export land-cover-aware NDVI for Hong Kong in Jan 2024.",
        "Compare all-surface and land-only NDVI for Hong Kong January 2024.",
    ]
    for variant in variants:
        route = route_request(variant)
        assert route["ok"] is True
        assert route["intent"] == "hk_january_2024_ndvi_by_landcover_csv"
        assert route["task"]["template"] == "hk_january_2024_ndvi_by_landcover_csv"
        assert route["task"]["context"]["landcover_dataset_id"] == "GOOGLE/DYNAMICWORLD/V1"


def test_ask_plan_writes_reviewable_task_plan_without_script(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
            "--plan",
            "--json",
            "--run-id",
            "test-ask-v02-plan-only",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)
    trace = Path(payload["run_trace"])
    task_plan = trace / "task_plan.yaml"
    assert task_plan.exists()
    assert not (trace / "generated_script.py").exists()
    assert json.loads((trace / "dry_run_report.json").read_text(encoding="utf-8"))["contacted_earth_engine"] is False
    plan_text = (trace / "plan.md").read_text(encoding="utf-8")
    assert "Dynamic World" in plan_text or "land-cover" in plan_text


def test_review_plan_reads_saved_task_plan(capsys):
    plan_path = Path("outputs/runs/test-ask-v02-plan-only/task_plan.yaml")
    if not plan_path.exists():
        cli.main(
            [
                "ask",
                "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
                "--plan",
                "--json",
                "--run-id",
                "test-ask-v02-plan-only",
            ]
        )
        capsys.readouterr()
    rc = cli.main(["review-plan", str(plan_path), "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["task_plan"]["task_id"] == "hk_2024_01_ndvi_landcover_v02"


def test_ask_dry_run_v02_renders_validates_and_traces_retrieval(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
            "--dry-run",
            "--json",
            "--run-id",
            "test-ask-v02-dry-run",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)
    assert payload["validation"]["ok"] is True
    trace = Path(payload["run_trace"])
    retrieval = json.loads((trace / "retrieval_trace.json").read_text(encoding="utf-8"))
    assert retrieval["coverage"]["dataset_cards"] >= 2
    assert retrieval["coverage"]["operator_notes"] >= 1
    assert retrieval["coverage"]["known_failures"] >= 1
    assert (trace / "task_plan.yaml").exists()
    assert Path("outputs/scripts/hk_2024_01_ndvi_by_landcover_csv.py").exists()


def test_v02_template_renders_and_validates(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_01_ndvi_landcover_v02.json"))
    rendered = render_template(Path("assets/templates"), "hk_january_2024_ndvi_by_landcover_csv", context)
    assert "GOOGLE/DYNAMICWORLD/V1" in rendered
    assert "all_surface_mean_ndvi" in rendered
    assert "vegetation_fraction" in rendered
    out = tmp_path / "hk_2024_01_ndvi_by_landcover_csv.py"
    out.write_text(rendered, encoding="utf-8")
    report = validate_script(out)
    assert report.ok
    assert "dynamic_world_landcover_ndvi" in report.semantic_rulesets


def test_run_plan_refuses_export_when_preflight_fails(monkeypatch, capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
            "--plan",
            "--json",
            "--run-id",
            "test-run-plan-preflight-block-plan",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)

    def fake_preflight(config):
        return {
            "ok": False,
            "decision": "block_export",
            "critical_error": error_payload("EMPTY_DYNAMIC_WORLD_COLLECTION", "No Dynamic World images."),
            "errors": [error_payload("EMPTY_DYNAMIC_WORLD_COLLECTION", "No Dynamic World images.")],
            "checks": {},
        }

    def fail_execute(*args, **kwargs):
        raise AssertionError("execute_script should not run after failed v0.2 preflight")

    monkeypatch.setattr(cli, "run_hk_ndvi_preflight", fake_preflight)
    monkeypatch.setattr(cli, "execute_script", fail_execute)
    rc = cli.main(
        [
            "run-plan",
            payload["task_plan"],
            "--project",
            "example-project",
            "--confirm-live",
            "--json",
            "--run-id",
            "test-run-plan-preflight-block",
        ]
    )
    assert rc == 1
    payload = _payload(capsys)
    assert payload["error"]["category"] == "EMPTY_DYNAMIC_WORLD_COLLECTION"
