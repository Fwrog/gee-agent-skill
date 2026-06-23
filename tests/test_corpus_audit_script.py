import json
import subprocess
import sys
from pathlib import Path


def test_analyze_gee_corpus_reports_pattern_groups(tmp_path):
    corpus = tmp_path / "repo"
    corpus.mkdir()
    (corpus / "example.py").write_text(
        """
import ee
ee.Initialize(project='example')
DATASET_ID = 'COPERNICUS/S2_SR_HARMONIZED'
START_DATE = '2024-01-01'
END_DATE = '2024-02-01'
SCALE = 10
image = (ee.ImageCollection(DATASET_ID)
    .filterDate(START_DATE, END_DATE)
    .filterBounds(ee.Geometry.Point([0, 0]))
    .map(lambda img: img.updateMask(img.select('SCL').neq(9)))
    .mean())
task = ee.batch.Export.image.toDrive(image=image, description='x', scale=SCALE, maxPixels=1000000)
task.start()
ee.ImageCollection(DATASET_ID).limit(1).size().getInfo()
ee.Number(1).getInfo()
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "scripts/analyze_gee_corpus.py", str(corpus)],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "gee-corpus-audit/v0.1"
    groups = payload["summary"]["aggregate_pattern_groups"]
    assert groups["collection_filters"]["hits"] >= 1
    assert groups["quality_masking"]["hits"] >= 1
    assert groups["exports"]["hits"] >= 1
    style = payload["summary"]["aggregate_style_signals"]
    assert style["explicit_temporal_scope"]["hits"] >= 1
    assert style["explicit_spatial_scope"]["hits"] >= 1
    assert style["reviewable_export_contract"]["hits"] >= 1
    assert payload["summary"]["style_exam"]["status"] == "evidence_seen"
    assert payload["summary"]["rule_implications"]["agent_script_contract"]["status"] == "evidence_seen"
