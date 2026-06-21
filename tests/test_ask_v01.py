import json
import re
from pathlib import Path

import geeskill.cli as cli
from geeskill.ask import route_request
from geeskill.errors import error_payload
from geeskill.templates import load_context, render_template
from geeskill.validation import validate_script


def _payload(capsys):
    return json.loads(capsys.readouterr().out)


def test_route_request_recognizes_v01_variants():
    variants = [
        "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
        "Calculate Hong Kong NDVI for January 2024.",
        "Export January 2024 Hong Kong NDVI as CSV.",
        "2024 Jan Hong Kong NDVI CSV",
    ]
    for variant in variants:
        route = route_request(variant)
        assert route["ok"] is True
        assert route["intent"] == "hk_january_2024_ndvi_csv"
        assert route["task"]["template"] == "hk_january_2024_ndvi_csv"


def test_route_request_rejects_full_year_district_v02_scope():
    route = route_request("Compute 2024 monthly mean NDVI for Hong Kong districts and export CSV.")
    assert route["ok"] is False
    assert route["error"]["category"] == "UNSUPPORTED_TASK"
    assert "v0.2" in route["error"]["message"]


def test_route_request_reports_ambiguous_task():
    route = route_request("Compute NDVI for Hong Kong.")
    assert route["ok"] is False
    assert route["error"]["category"] == "AMBIGUOUS_TASK"


def test_ask_dry_run_writes_trace_and_required_artifacts(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
            "--dry-run",
            "--json",
            "--run-id",
            "test-ask-v01-dry-run",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["validation"]["ok"] is True
    trace = Path(payload["run_trace"])
    for name in [
        "task.yaml",
        "retrieval_trace.json",
        "plan.md",
        "generated_script.py",
        "validation_report.json",
        "dry_run_report.json",
        "environment.json",
        "final_report.md",
    ]:
        assert (trace / name).exists(), name
    assert Path("outputs/scripts/hk_2024_01_ndvi_csv.py").exists()


def test_ask_retrieval_trace_has_v01_coverage(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
            "--dry-run",
            "--json",
            "--run-id",
            "test-ask-v01-retrieval",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)
    trace = Path(payload["run_trace"])
    retrieval = json.loads((trace / "retrieval_trace.json").read_text(encoding="utf-8"))
    coverage = retrieval["coverage"]
    assert coverage["dataset_cards"] >= 1
    assert coverage["operator_notes"] >= 1
    assert coverage["workflow_patterns"] >= 1
    assert coverage["known_failures"] >= 1
    assert coverage["export_guidance"] >= 1


def test_v01_template_renders_and_validates(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_01_ndvi_v01.json"))
    rendered = render_template(Path("assets/templates"), "hk_january_2024_ndvi_csv", context)
    assert "normalizedDifference([\"B8\", \"B4\"])" in rendered
    assert "ee.batch.Export.table.toDrive" in rendered
    out = tmp_path / "hk_2024_01_ndvi_csv.py"
    out.write_text(rendered, encoding="utf-8")
    report = validate_script(out)
    assert report.ok


def test_ask_live_refuses_export_when_preflight_fails(monkeypatch, capsys):
    def fake_preflight(config):
        return {
            "ok": False,
            "decision": "block_export",
            "critical_error": error_payload("EMPTY_IMAGE_COLLECTION", "No Sentinel-2 images."),
            "errors": [error_payload("EMPTY_IMAGE_COLLECTION", "No Sentinel-2 images.")],
            "checks": {},
        }

    def fail_execute(*args, **kwargs):
        raise AssertionError("execute_script should not run after failed preflight")

    monkeypatch.setattr(cli, "run_hk_ndvi_preflight", fake_preflight)
    monkeypatch.setattr(cli, "execute_script", fail_execute)
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
            "--project",
            "example-project",
            "--confirm-live",
            "--json",
            "--run-id",
            "test-ask-v01-live-preflight-block",
        ]
    )
    assert rc == 1
    payload = _payload(capsys)
    assert payload["error"]["category"] == "EMPTY_IMAGE_COLLECTION"


def test_ask_trace_does_not_write_credential_material(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
            "--dry-run",
            "--json",
            "--run-id",
            "test-ask-v01-credential-scan",
        ]
    )
    assert rc == 0
    payload = _payload(capsys)
    trace = Path(payload["run_trace"])
    combined = "\n".join(path.read_text(encoding="utf-8") for path in trace.glob("*") if path.is_file())
    assert not re.search(
        r"(private_key|client_secret|refresh_token|service_account|credentials\.json)",
        combined,
        re.IGNORECASE,
    )
