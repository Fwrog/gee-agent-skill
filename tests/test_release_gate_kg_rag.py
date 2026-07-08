import subprocess

from scripts import release_gate_kg_rag


def test_release_gate_reports_command_failures(monkeypatch):
    def fake_run(command, text, capture_output, check):
        return subprocess.CompletedProcess(command, 0, stdout='{"ok": true}', stderr="")

    monkeypatch.setattr(release_gate_kg_rag.subprocess, "run", fake_run)
    monkeypatch.setattr(release_gate_kg_rag, "_privacy_scan", lambda: {"command": "privacy_scan", "ok": True, "findings": []})
    report = release_gate_kg_rag.run_release_gate()
    assert report["ok"] is True
    assert any("validate_sources.py" in check["command"] for check in report["checks"])
    assert any(check["command"] == "privacy_scan" for check in report["checks"])
