from pathlib import Path

from geeskill.errors import error_payload
from geeskill.semantic import validate_semantics
from geeskill.templates import load_context, render_template


def test_semantic_validator_accepts_hk_monthly_ndvi(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    script = tmp_path / "hk.py"
    script.write_text(
        render_template(Path("assets/templates"), "hk_district_monthly_ndvi", context),
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["sentinel2_ndvi_monthly_zonal", "export_table_csv"])
    assert not [item for item in findings if item.severity == "error"]


def test_semantic_validator_rejects_wrong_ndvi_bands(tmp_path):
    script = tmp_path / "bad.py"
    script.write_text(
        """
import ee
START_DATE = '2024-01-01'
END_DATE = '2024-02-01'
SCALE = 10
CRS = 'EPSG:4326'
def f():
    aoi = ee.Geometry.Point([0, 0])
    c = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(START_DATE, END_DATE).filterBounds(aoi)
    return c.map(lambda image: image.normalizedDifference(['B3', 'B2']).rename('NDVI')).mean()
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["sentinel2_ndvi_monthly_zonal"])
    assert any(item.code == "s2-ndvi-bands" for item in findings)


def test_error_payload_has_recovery_fields():
    payload = error_payload("AUTH_ERROR", "missing credentials")
    assert payload["retryable"] is True
    assert payload["user_action_required"] is True
    assert "authenticate" in payload["suggested_fix"].lower()


def test_semantic_error_serializes_taxonomy_fields(tmp_path):
    script = tmp_path / "bad.py"
    script.write_text(
        """
import ee
START_DATE = '2024-01-01'
END_DATE = '2024-02-01'
SCALE = 10
CRS = 'EPSG:4326'
def f():
    aoi = ee.Geometry.Point([0, 0])
    c = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(START_DATE, END_DATE).filterBounds(aoi)
    return c.mean()
""",
        encoding="utf-8",
    )
    from geeskill.validation import validate_script

    report = validate_script(script, semantic_rulesets=["sentinel2_ndvi_monthly_zonal"]).to_dict()
    error = next(item for item in report["findings"] if item["severity"] == "error")
    assert error["category"]
    assert error["rule_id"]
    assert error["ruleset"] == "sentinel2_ndvi_monthly_zonal"
    assert error["suggested_fix"]
    assert error["user_action_required"] is True


def test_agent_script_contract_rejects_inline_authenticate_and_missing_constants(tmp_path):
    script = tmp_path / "bad_agent_script.py"
    script.write_text(
        """
import ee
ee.Authenticate()
def run():
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate('2024-01-01', '2024-02-01')
    task = ee.batch.Export.image.toDrive(image=collection.mean(), description='x')
    task.start()
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["agent_script_contract"])
    codes = {item.code for item in findings}
    assert "no-inline-authenticate" in codes
    assert "date-window-constants" in codes
    assert "dataset-id-constant" in codes
    assert "scale-constant" in codes
    assert "main-guard-for-task-start" in codes


def test_agent_script_contract_accepts_table_export_without_maxpixels(tmp_path):
    script = tmp_path / "table_agent_script.py"
    script.write_text(
        """
import ee

START_DATE = '2024-01-01'
END_DATE = '2024-02-01'
DATASET_ID = 'COPERNICUS/S2_SR_HARMONIZED'
SCALE = 10
CRS = 'EPSG:4326'
EXPORT_DESCRIPTION = 'table_export'


def main():
    aoi = ee.Geometry.Point([0, 0]).buffer(1000)
    collection = ee.ImageCollection(DATASET_ID).filterDate(START_DATE, END_DATE).filterBounds(aoi)
    table = ee.FeatureCollection([ee.Feature(None, {'count': collection.size()})])
    task = ee.batch.Export.table.toDrive(
        collection=table,
        description=EXPORT_DESCRIPTION,
        fileFormat='CSV',
        selectors=['count'],
    )
    task.start()


if __name__ == '__main__':
    raise SystemExit(main())
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["agent_script_contract"])
    assert not [item for item in findings if item.severity == "error"]


def test_agent_script_contract_accepts_rendered_hk_template(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_01_ndvi_v01.json"))
    script = tmp_path / "hk.py"
    script.write_text(
        render_template(Path("assets/templates"), "hk_january_2024_ndvi_csv", context),
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["agent_script_contract"])
    assert not [item for item in findings if item.severity == "error"]
