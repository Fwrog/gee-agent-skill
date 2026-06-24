import json
from pathlib import Path

import geeskill.cli as cli
from geeskill.cli import main


def test_live_smoke_missing_live_access_fails_with_structured_guidance(capsys):
    rc = main(
        [
            "live-smoke-test",
            "--project",
            "example-project",
            "--confirm-live",
            "--smoke-month",
            "1",
            "--smoke-region",
            "Central and Western",
            "--export-folder",
            "gee_exports",
        ]
    )
    assert rc in {0, 2}
    payload = json.loads(capsys.readouterr().out)
    if rc == 2:
        assert payload["error"]["category"] in {"AUTH_ERROR", "PROJECT_ERROR", "NETWORK_ERROR"}
        assert payload["error"]["suggested_fix"]
        if payload["error"]["category"] != "NETWORK_ERROR":
            assert payload["error"]["user_action_required"] is True


def test_live_smoke_requires_confirm_live_with_json(capsys):
    rc = main(
        [
            "live-smoke-test",
            "--project",
            "example-project",
            "--smoke-month",
            "1",
            "--smoke-region",
            "Central and Western",
            "--export-folder",
            "gee_exports",
            "--json",
        ]
    )
    assert rc == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["command"] == "live-smoke-test"
    assert payload["error"]["code"] == "CONFIRM_LIVE_REQUIRED"


def test_monitor_exports_writes_trace(monkeypatch, capsys):
    def fake_monitor_tasks(project, authenticate=False, timeout_seconds=0, poll_seconds=10):
        return [
            {
                "id": "task-1",
                "description": "hk_ndvi_export",
                "state": "FAILED",
                "creation_timestamp_ms": 1714521600000,
                "update_timestamp_ms": 1714525200000,
                "error_message": "Drive folder unavailable",
            }
        ]

    monkeypatch.setattr(cli, "monitor_tasks", fake_monitor_tasks)
    run_id = "test-monitor-trace"
    rc = main(["monitor-exports", "--project", "example-project", "--run-id", run_id, "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 1
    assert payload["tasks"][0]["id"] == "task-1"
    run_dir = Path("outputs/runs") / run_id
    for name in ["task.yaml", "retrieval_trace.json", "plan.md", "export_tasks.json", "environment.json", "final_report.md"]:
        assert (run_dir / name).exists(), name
    export_tasks = json.loads((run_dir / "export_tasks.json").read_text(encoding="utf-8"))
    assert export_tasks[0]["description"] == "hk_ndvi_export"
    assert export_tasks[0]["error_message"] == "Drive folder unavailable"
