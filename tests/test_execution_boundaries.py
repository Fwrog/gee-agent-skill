from pathlib import Path

from geeskill.cli import main
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

