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


def test_cli_search_docs_offline(capsys):
    rc = main(["search-docs", "Sentinel-2 cloud mask", "--top-k", "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Sentinel" in out or "cloud" in out


def test_cli_smoke_test_offline(capsys):
    rc = main(["smoke-test"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "validation_ok=True" in out

