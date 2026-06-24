import json
from pathlib import Path

import pytest

from geeskill.cli import main
from geeskill.earthengine import execute_script
from geeskill.templates import load_context, render_template


def _valid_script(tmp_path: Path) -> Path:
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    rendered = render_template(Path("assets/templates"), "hk_district_monthly_ndvi", context)
    script = tmp_path / "hk.py"
    script.write_text(rendered, encoding="utf-8")
    return script


def test_run_dry_run_never_requires_credentials(tmp_path, capsys):
    script = _valid_script(tmp_path)
    rc = main(["run", str(script), "--dry-run"])
    assert rc == 0
    assert "Dry run OK" in capsys.readouterr().out


def test_run_live_requires_explicit_project(tmp_path, capsys):
    script = _valid_script(tmp_path)
    rc = main(["run", str(script)])
    assert rc == 2
    assert "requires --project" in capsys.readouterr().err


def test_run_live_gate_failure_is_json_when_requested(tmp_path, capsys):
    script = _valid_script(tmp_path)
    rc = main(["run", str(script), "--confirm-live", "--json"])
    assert rc == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["command"] == "run"
    assert payload["schema_version"] == "gee-cli/v0.3"
    assert payload["error"]["code"] == "PROJECT_ERROR"
    assert payload["error"]["hint"]


def test_run_live_confirm_gate_failure_is_json_when_requested(tmp_path, capsys):
    script = _valid_script(tmp_path)
    rc = main(["run", str(script), "--project", "example-project", "--json"])
    assert rc == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["command"] == "run"
    assert payload["error"]["code"] == "CONFIRM_LIVE_REQUIRED"


def test_validate_missing_script_is_json(capsys):
    rc = main(["validate", "/tmp/does-not-exist-gee-skill.py", "--json"])
    assert rc == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["command"] == "validate"
    assert payload["error"]["code"] == "FILE_NOT_FOUND"


def test_version_reports_package_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "gee-agent-skill 0.3.0" in capsys.readouterr().out


def test_execute_script_treats_system_exit_zero_as_success(tmp_path, monkeypatch):
    import geeskill.earthengine as earthengine

    monkeypatch.setattr(earthengine, "initialize", lambda project, authenticate=False: None)
    script = tmp_path / "ok.py"
    script.write_text("raise SystemExit(0)\n", encoding="utf-8")
    result = execute_script(script, project="example-project")
    assert result["system_exit_code"] == 0
