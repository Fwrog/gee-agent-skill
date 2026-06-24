import json
from pathlib import Path

from geeskill.cli import main


def test_cli_help(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    assert "search-docs" in out
    assert "monitor-exports" in out


def test_cli_tools_json_envelope(capsys):
    rc = main(["tools", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "tools"
    assert payload["schema_version"] == "gee-cli/v0.3"
    assert payload["data"]["exposed_tools"]


def test_cli_search_docs_offline(capsys):
    rc = main(["search-docs", "Sentinel-2 cloud mask", "--top-k", "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Sentinel" in out or "cloud" in out


def test_cli_search_docs_json_envelope(capsys):
    rc = main(["search-docs", "Sentinel-2 cloud mask", "--top-k", "1", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "search-docs"
    assert payload["schema_version"] == "gee-cli/v0.3"
    assert payload["data"]["results"]


def test_cli_smoke_test_offline(capsys):
    rc = main(["smoke-test"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "validation_ok=True" in out


def test_cli_smoke_test_json_envelope(capsys):
    rc = main(["smoke-test", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "smoke-test"
    assert payload["schema_version"] == "gee-cli/v0.3"
    assert payload["data"]["validation"]["ok"] is True
