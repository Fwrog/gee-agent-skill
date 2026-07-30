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


def test_privacy_scan_rejects_nonportable_local_paths(tmp_path, monkeypatch):
    note = tmp_path / "note.md"
    local_path = "C:" + r"\Users\researcher\private-study"
    note.write_text(f"Local checkout: {local_path}", encoding="utf-8")
    monkeypatch.setattr(release_gate_kg_rag, "_release_text_paths", lambda: [note])

    report = release_gate_kg_rag._privacy_scan()

    assert report["ok"] is False
    assert report["findings"][0]["path"] == str(note)


def test_privacy_scan_accepts_synthetic_asset_placeholders(tmp_path, monkeypatch):
    fixture = tmp_path / "fixture.py"
    fixture.write_text(
        "asset = 'projects/example/assets/private_landcover'\n"
        "aoi = 'users/example/private_aoi'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(release_gate_kg_rag, "_release_text_paths", lambda: [fixture])

    assert release_gate_kg_rag._privacy_scan()["ok"] is True
