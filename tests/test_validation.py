from pathlib import Path

from geeskill.templates import load_context, render_template
from geeskill.validation import validate_script


def test_validate_rendered_hk_template(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    rendered = render_template(Path("assets/templates"), "hk_district_monthly_ndvi", context)
    script = tmp_path / "hk.py"
    script.write_text(rendered, encoding="utf-8")
    report = validate_script(script)
    assert report.ok, report.to_dict()


def test_validate_rejects_unresolved_template(tmp_path):
    script = tmp_path / "bad.py"
    script.write_text("import ee\nVALUE = '{{ missing }}'\n", encoding="utf-8")
    report = validate_script(script)
    assert not report.ok
    assert any(item.code == "unresolved-template-token" for item in report.findings)


def test_validate_rejects_bad_date_order(tmp_path):
    script = tmp_path / "bad_dates.py"
    script.write_text(
        "\n".join(
            [
                "import ee",
                "START_DATE = '2024-12-31'",
                "END_DATE = '2024-01-01'",
                "SCALE = 10",
                "CRS = 'EPSG:4326'",
                "def f():",
                "    return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(START_DATE, END_DATE).filterBounds(ee.Geometry.Point([0, 0]))",
            ]
        ),
        encoding="utf-8",
    )
    report = validate_script(script)
    assert not report.ok
    assert any(item.code == "date-order" for item in report.findings)

