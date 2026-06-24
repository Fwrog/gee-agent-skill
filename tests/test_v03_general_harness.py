import json
import sys
import types
from pathlib import Path

import yaml

import geeskill.cli as cli
from geeskill.intents import build_general_plan_from_text
from geeskill.semantic import validate_semantics
from geeskill.templates import load_context, render_template
from geeskill.validation import validate_script


HK_2024_16DAY_REQUEST = "Compute 16-day NDVI for Hong Kong in 2024 and export CSV."


def _payload(capsys):
    return json.loads(capsys.readouterr().out)


def _write_v03_hk_plan(tmp_path, capsys):
    plan_path = tmp_path / "hk_2024_16day_ndvi.yaml"
    script_path = tmp_path / "hk_2024_16day_ndvi_csv.py"
    rc = cli.main(["plan", "from-text", HK_2024_16DAY_REQUEST, "--out", str(plan_path), "--json"])
    assert rc == 0
    capsys.readouterr()
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["execution"]["outputs"]["script"] = str(script_path)
    plan["execution"]["context"]["export_description"] = "test_hk_2024_16day_ndvi"
    plan["execution"]["context"]["drive_folder"] = "test_gee_exports"
    plan["execution"]["context"]["file_prefix"] = "test_hk_2024_16day_ndvi"
    plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return plan_path


def _write_general_plan(tmp_path, capsys, request: str, name: str) -> Path:
    plan_path = tmp_path / f"{name}.yaml"
    rc = cli.main(["plan", "from-text", request, "--out", str(plan_path), "--json"])
    assert rc == 0
    capsys.readouterr()
    return plan_path


def test_plan_from_text_accepts_ndwi_geotiff(capsys):
    rc = cli.main(["plan", "from-text", "Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF.", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    plan = payload["data"]["plan"]
    assert plan["schema_version"] == "gee-plan/v0.3"
    assert plan["task_type"] == "water_index"
    assert plan["intent"]["recipe_id"] == "water-index-ndwi"
    assert plan["output"]["format"] == "GeoTIFF"
    assert plan["execution"]["template"] == "sentinel2_index_image"
    assert plan["execution"]["template_ready"] is True
    assert plan["execution"]["live_adapter_ready"] is False
    assert plan["validation"]["rulesets"] == ["global_safety", "water_index_ndwi", "export_image_geotiff"]


def test_plan_from_text_recognizes_this_aoi_and_named_city(capsys):
    rc = cli.main(["plan", "from-text", "Compute NDWI for this AOI in March 2024 and export GeoTIFF.", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["plan"]["aoi"]["type"] == "user_supplied"

    rc = cli.main(["plan", "from-text", "Calculate NDBI for Tokyo in summer 2024.", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    plan = payload["data"]["plan"]
    assert plan["aoi"]["name"] == "Tokyo"
    assert plan["output"]["type"] == "csv"
    assert plan["output"]["inferred"] is True
    assert plan["execution"]["template_ready"] is True


def test_observe_summarizes_natural_language_request(capsys):
    rc = cli.main(["observe", "Compute 16-day NDVI for Hong Kong in 2024 and export CSV.", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    summary = payload["data"]["summary"]
    assert summary["task_type"] == "vegetation_index"
    assert summary["metric"] == "NDVI"
    assert summary["template_ready"] is True
    commands = [step["command"] for step in payload["data"]["next_steps"]]
    assert any("plan from-text" in command for command in commands)


def test_auth_check_reports_missing_earthengine_api(monkeypatch, capsys):
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: None if name == "ee" else None)
    rc = cli.main(["auth", "check", "--json"])
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "EARTHENGINE_API_MISSING"


def test_auth_check_discovers_project_without_live_init(monkeypatch, capsys):
    calls = []
    fake_ee = types.SimpleNamespace(
        Initialize=lambda **kwargs: calls.append(kwargs),
        Number=lambda value: types.SimpleNamespace(getInfo=lambda: value),
    )
    monkeypatch.setitem(sys.modules, "ee", fake_ee)
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: object() if name == "ee" else None)
    monkeypatch.setattr(cli, "_gcloud_project", lambda: {"source": "gcloud_config", "available": False, "project": None})
    monkeypatch.setenv("EE_PROJECT", "example-project")

    rc = cli.main(["auth", "check", "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["initialized"] is False
    assert payload["data"]["project_sources"] == [{"source": "env:EE_PROJECT", "project": "example-project"}]
    assert "gee-skill auth check --project example-project --json" in payload["data"]["next_commands"]
    assert calls == []


def test_auth_check_can_use_discovered_project(monkeypatch, capsys):
    calls = []
    fake_ee = types.SimpleNamespace(
        Initialize=lambda **kwargs: calls.append(kwargs),
        Number=lambda value: types.SimpleNamespace(getInfo=lambda: value),
    )
    monkeypatch.setitem(sys.modules, "ee", fake_ee)
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: object() if name == "ee" else None)
    monkeypatch.setattr(cli, "_gcloud_project", lambda: {"source": "gcloud_config", "available": False, "project": None})
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "discovered-project")

    rc = cli.main(["auth", "check", "--use-discovered-project", "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["initialized"] is True
    assert payload["data"]["project"] == "discovered-project"
    assert payload["data"]["project_source"] == "env:GOOGLE_CLOUD_PROJECT"
    assert calls == [{"project": "discovered-project"}]


def test_plan_from_text_accepts_hk_2024_16day_ndvi():
    result = build_general_plan_from_text("Compute 16-day NDVI for Hong Kong in 2024 and export CSV.")
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "vegetation_index"
    assert plan["intent"]["golden_example"] is True
    assert plan["execution"]["template"] == "hk_2024_16day_ndvi_csv"
    assert plan["execution"]["context"]["temporal_cadence_days"] == 16
    assert plan["execution"]["temporal_cadence"] == "16-day"
    assert plan["aoi"]["name"] == "Hong Kong"
    assert plan["time_range"]["date_start"] == "2024-01-01"
    assert plan["time_range"]["date_end"] == "2025-01-01"


def test_plan_from_text_reports_missing_aoi(capsys):
    rc = cli.main(["plan", "from-text", "Compute NDWI in March 2024 and export GeoTIFF.", "--json"])
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "AMBIGUOUS_TASK"
    assert "aoi" in payload["data"]["missing_fields"]


def test_plan_from_text_accepts_ndbi_csv():
    result = build_general_plan_from_text("Compute NDBI for Hong Kong in 2024 and export CSV.")
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "builtup_index"
    assert plan["intent"]["metric"] == "NDBI"
    assert plan["intent"]["recipe_id"] == "builtup-index-ndbi"
    assert plan["execution"]["template"] == "sentinel2_index_table"
    assert plan["execution"]["template_ready"] is True
    assert plan["validation"]["rulesets"] == ["global_safety", "builtup_index_ndbi", "export_table_csv"]
    assert plan["selected_datasets"][0]["dataset_id"] == "COPERNICUS/S2_SR_HARMONIZED"


def test_plan_from_text_accepts_landsat_lst_csv():
    result = build_general_plan_from_text("Compute Landsat LST for Hong Kong in summer 2024 and export CSV.")
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "land_surface_temperature"
    assert plan["intent"]["metric"] == "LST"
    assert plan["intent"]["recipe_id"] == "landsat-lst"
    assert plan["execution"]["template"] == "landsat_lst_table"
    assert plan["execution"]["template_ready"] is True
    assert plan["validation"]["rulesets"] == ["global_safety", "landsat_lst", "export_table_csv"]
    assert plan["selected_datasets"][0]["dataset_id"] == "LANDSAT/LC08/C02/T1_L2"
    assert plan["time_range"]["date_start"] == "2024-06-01"
    assert plan["time_range"]["date_end"] == "2024-09-01"


def test_plan_from_text_accepts_sentinel1_flood_before_after():
    result = build_general_plan_from_text(
        "Map Sentinel-1 flood extent for a supplied AOI before June 2024 and after July 2024 and export GeoTIFF."
    )
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "flood_mapping"
    assert plan["intent"]["metric"] == "flood_extent"
    assert plan["intent"]["recipe_id"] == "sentinel1-flood-before-after"
    assert plan["execution"]["template"] == "sentinel1_flood_before_after"
    assert plan["execution"]["template_ready"] is True
    assert plan["validation"]["rulesets"] == ["global_safety", "sentinel1_flood_before_after", "export_image_geotiff"]
    assert plan["selected_datasets"][0]["dataset_id"] == "COPERNICUS/S1_GRD"
    assert plan["before_time_range"]["date_start"] == "2024-06-01"
    assert plan["after_time_range"]["date_start"] == "2024-07-01"
    assert plan["output"]["format"] == "GeoTIFF"
    assert "filterMetadata" in plan["operators"]


def test_plan_from_text_accepts_dynamic_world_landcover_summary():
    result = build_general_plan_from_text(
        "Summarize Dynamic World land cover for a supplied GeoJSON AOI in 2024 and export CSV."
    )
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "landcover_summary"
    assert plan["intent"]["metric"] == "landcover"
    assert plan["intent"]["recipe_id"] == "landcover-summary-dynamic-world"
    assert plan["selected_datasets"][0]["dataset_id"] == "GOOGLE/DYNAMICWORLD/V1"
    assert plan["execution"]["template"] == "dynamic_world_landcover_summary"
    assert plan["execution"]["template_ready"] is True
    assert plan["validation"]["rulesets"] == ["global_safety", "dynamic_world_landcover", "export_table_csv"]


def test_plan_from_text_accepts_zonal_statistics_as_reviewable_plan():
    result = build_general_plan_from_text("Compute zonal statistics for supplied GeoJSON zones in March 2024 and export CSV.")
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "zonal_statistics"
    assert plan["intent"]["metric"] == "zonal_mean"
    assert plan["intent"]["recipe_id"] == "zonal-statistics-table"
    assert plan["execution"]["template"] == "zonal_statistics"
    assert plan["execution"]["template_ready"] is False
    assert plan["validation"]["rulesets"] == ["global_safety", "export_table_csv"]


def test_plan_from_text_accepts_standalone_image_export_as_reviewable_plan():
    result = build_general_plan_from_text("Export image for a supplied AOI in March 2024 as GeoTIFF.")
    assert result["ok"] is True
    plan = result["plan"]
    assert plan["task_type"] == "export_image"
    assert plan["intent"]["metric"] == "image_export"
    assert plan["intent"]["recipe_id"] == "image-export-geotiff"
    assert plan["execution"]["template_ready"] is False
    assert plan["validation"]["rulesets"] == ["global_safety", "export_image_geotiff"]


def test_plan_from_text_reports_missing_flood_windows(capsys):
    rc = cli.main(
        [
            "plan",
            "from-text",
            "Map Sentinel-1 flood extent for a supplied AOI before and after a storm and export GeoTIFF.",
            "--json",
        ]
    )
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "AMBIGUOUS_TASK"
    assert payload["data"]["missing_fields"] == ["before_time_range", "after_time_range"]


def test_plan_from_text_reports_unsupported_task_with_closest_recipes(capsys):
    rc = cli.main(["plan", "from-text", "Estimate crop yield for Hong Kong in 2024 and export CSV.", "--json"])
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "UNSUPPORTED_TASK"
    assert payload["data"]["closest_recipes"]
    assert payload["data"]["slots"]["aoi"]["name"] == "Hong Kong"


def test_plan_from_text_rejects_unknown_dataset_id(capsys):
    rc = cli.main(
        [
            "plan",
            "from-text",
            "Compute NDVI for Hong Kong in 2024 using NASA/MADE_UP/DATASET and export CSV.",
            "--json",
        ]
    )
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "UNKNOWN_DATASET_ID"
    assert payload["data"]["candidate_datasets"]


def test_catalog_recipe_rules_envelopes(capsys):
    rc = cli.main(["catalog", "search", "NDWI GeoTIFF", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["results"]

    rc = cli.main(["catalog", "recommend", "--task-type", "water_index", "--metric", "NDWI", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["results"][0]["dataset_id"] == "COPERNICUS/S2_SR_HARMONIZED"

    rc = cli.main(["catalog", "evidence", "--category", "operators", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["schema_version"] == "gee-cli/v0.3"
    assert payload["data"]["cards"]
    assert {item["category"] for item in payload["data"]["cards"]} == {"operators"}
    client_server_card = next(item for item in payload["data"]["cards"] if item["source_path"] == "core/client-server-deferred-execution.md")
    assert "UNSAFE_GETINFO" in client_server_card["known_failures"]

    rc = cli.main(["catalog", "evidence", "--category", "failures", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["data"]["cards"]
    assert any("PREFLIGHT_REQUIRED" in item["known_failures"] for item in payload["data"]["cards"])

    rc = cli.main(["recipe", "show", "water-index-ndwi", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["task_type"] == "water_index"

    rc = cli.main(["rules", "show", "export_image_geotiff", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert "maxPixels" in " ".join(payload["data"]["checks"])

    rc = cli.main(["rules", "show", "landsat_lst", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["ruleset_id"] == "landsat_lst"


def test_canonical_aoi_and_corpus_commands(capsys):
    rc = cli.main(["aoi", "resolve", "Compute NDVI for Hong Kong in January 2024.", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["command"] == "aoi resolve"
    assert payload["data"]["aoi"]["name"] == "Hong Kong"

    rc = cli.main(["corpus", "coverage", "--task-type", "vegetation_index", "--metric", "NDVI", "--output", "CSV", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["command"] == "corpus coverage"
    assert payload["data"]["coverage"]["dataset_cards"] >= 1
    assert payload["data"]["coverage"]["known_failures"] >= 1


def test_canonical_render_and_preflight_aliases(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)
    script_path = tmp_path / "rendered.py"

    rc = cli.main(["render", str(plan_path), "--script-out", str(script_path), "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["script"] == str(script_path)
    assert payload["data"]["validation"]["ok"] is True

    monkeypatch.setattr(
        cli,
        "run_hk_ndvi_preflight",
        lambda config: {
            "ok": True,
            "decision": "allow_export",
            "project": config.project,
            "year": config.year,
            "month": config.month,
            "scope": config.scope,
            "aoi_name": "Hong Kong",
            "dataset_id": config.dataset_id,
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {"fake": {"ok": True}},
        },
    )

    rc = cli.main(["preflight", str(plan_path), "--project", "example-project", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["schema_version"] == "gee-plan/v0.3"
    assert payload["preflight"]["decision"] == "allow_export"


def test_non_golden_v03_recipes_render_validate_and_require_reviewed_preflight_context(tmp_path, capsys):
    cases = [
        (
            "Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF.",
            "ndwi",
            "sentinel2_index_image",
            "water_index_ndwi",
            "Export.image.toDrive",
        ),
        (
            "Compute NDBI for Hong Kong in 2024 and export CSV.",
            "ndbi",
            "sentinel2_index_table",
            "builtup_index_ndbi",
            "Export.table.toDrive",
        ),
        (
            "Compute EVI for a supplied AOI in March 2024 and export CSV.",
            "evi",
            "sentinel2_index_table",
            "optical_index",
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
        ),
        (
            "Compute Landsat LST for Hong Kong in summer 2024 and export CSV.",
            "lst",
            "landsat_lst_table",
            "landsat_lst",
            "Export.table.toDrive",
        ),
        (
            "Summarize Dynamic World land cover for a GeoJSON AOI in 2024 and export CSV.",
            "dynamic_world",
            "dynamic_world_landcover_summary",
            "dynamic_world_landcover",
            "GOOGLE/DYNAMICWORLD/V1",
        ),
        (
            "Map Sentinel-1 flood extent for a supplied AOI before June 2024 and after July 2024 and export GeoTIFF.",
            "flood",
            "sentinel1_flood_before_after",
            "sentinel1_flood_before_after",
            "Export.image.toDrive",
        ),
    ]
    for request, name, template, ruleset, script_snippet in cases:
        plan_path = _write_general_plan(tmp_path, capsys, request, name)
        script_path = tmp_path / f"{name}.py"
        plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
        assert plan["execution"]["template"] == template
        assert plan["execution"]["template_ready"] is True
        assert plan["execution"]["live_adapter_ready"] is False

        rc = cli.main(["render", str(plan_path), "--script-out", str(script_path), "--json"])
        assert rc == 0
        payload = _payload(capsys)
        assert payload["ok"] is True
        assert payload["data"]["validation"]["ok"] is True
        assert ruleset in payload["data"]["validation"]["semantic_rulesets"]
        assert script_snippet in script_path.read_text(encoding="utf-8")

    blocked_plan = tmp_path / "ndwi.yaml"
    rc = cli.main(["preflight", str(blocked_plan), "--project", "example-project", "--json"])
    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["preflight"]["decision"] == "block_export"
    assert payload["preflight"]["critical_error"]["category"] == "V03_CONTEXT_REVIEW_REQUIRED"


def test_non_golden_v03_preflight_dispatches_to_generic_adapter(monkeypatch, tmp_path, capsys):
    plan_path = _write_general_plan(
        tmp_path,
        capsys,
        "Compute NDWI for projects/example/assets/reviewed_aoi in March 2024 and export GeoTIFF.",
        "ndwi_reviewed",
    )
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["execution"]["context"]["aoi_asset"] = "projects/example/assets/reviewed_aoi"
    plan["execution"]["context"]["export_description"] = "ndwi_reviewed_preflight"
    plan["execution"]["context"]["drive_folder"] = "gee_exports"
    plan["execution"]["context"]["file_prefix"] = "ndwi_reviewed_preflight"
    plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
    calls = []

    def fake_generic_preflight(config):
        calls.append(config)
        return {
            "ok": True,
            "decision": "allow_export",
            "schema_version": config.schema_version,
            "plan_id": config.plan_id,
            "profile": config.profile,
            "template": config.template,
            "project": config.project,
            "aoi_asset": config.aoi_asset,
            "dataset_id": config.dataset_id,
            "required_bands": list(config.required_bands),
            "qa_bands": list(config.qa_bands),
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {"adapter": {"ok": True}},
        }

    monkeypatch.setattr(cli, "run_generic_v03_preflight", fake_generic_preflight)

    rc = cli.main(["preflight", str(plan_path), "--project", "example-project", "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["preflight"]["decision"] == "allow_export"
    assert payload["preflight"]["template"] == "sentinel2_index_image"
    assert payload["preflight"]["required_bands"] == ["B3", "B8"]
    assert payload["preflight"]["qa_bands"] == ["SCL"]
    assert len(calls) == 1
    assert calls[0].project == "example-project"
    assert calls[0].aoi_asset == "projects/example/assets/reviewed_aoi"


def test_canonical_exports_watch_filters_task_id(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "monitor_tasks",
        lambda project, authenticate=False, timeout_seconds=0, poll_seconds=15: [
            {"id": "task-1", "description": "first", "state": "READY"},
            {"id": "task-2", "description": "second", "state": "COMPLETED"},
        ],
    )

    rc = cli.main(["exports", "watch", "--project", "example-project", "--task-id", "task-2", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["command"] == "exports watch"
    assert payload["data"]["count"] == 1
    assert payload["data"]["tasks"][0]["id"] == "task-2"


def test_trace_inspect_and_eval_alias(tmp_path, capsys):
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()
    for name in [
        "environment.json",
        "task.yaml",
        "retrieval_trace.json",
        "plan.md",
        "validation_report.json",
        "dry_run_report.json",
        "final_report.md",
    ]:
        (trace_dir / name).write_text("{}", encoding="utf-8")

    rc = cli.main(["trace", "inspect", str(trace_dir), "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["command"] == "trace inspect"
    assert payload["data"]["complete_core_trace"] is True

    rc = cli.main(["eval", "evals/benchmark_suite.yml", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["command"] == "eval"
    assert payload["data"]["suite"] == "gee_harness_benchmark_v0.3"


def test_water_and_builtup_rules_reject_wrong_bands(tmp_path):
    script = tmp_path / "bad_index.py"
    script.write_text(
        """
import ee
START_DATE = '2024-03-01'
END_DATE = '2024-04-01'
SCALE = 10
CRS = 'EPSG:4326'
def build():
    aoi = ee.Geometry.Point([0, 0])
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(START_DATE, END_DATE).filterBounds(aoi)
    return collection.map(lambda image: image.normalizedDifference(['B8', 'B4']).rename('NDWI')).mean()
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["water_index_ndwi"])
    assert any(item.code == "ndwi-green-band" for item in findings)


def test_export_image_geotiff_requires_region_and_maxpixels(tmp_path):
    script = tmp_path / "bad_export.py"
    script.write_text(
        """
import ee
START_DATE = '2024-03-01'
END_DATE = '2024-04-01'
SCALE = 10
CRS = 'EPSG:4326'
def export():
    image = ee.Image(1)
    return ee.batch.Export.image.toDrive(image=image, description='x', scale=SCALE, fileFormat='GeoTIFF')
""",
        encoding="utf-8",
    )
    findings = validate_semantics(script, ["export_image_geotiff"])
    codes = {item.code for item in findings}
    assert "image-export-region" in codes
    assert "image-export-maxpixels" in codes


def test_plan_from_text_can_write_editable_yaml(tmp_path, capsys):
    out = tmp_path / "plan.yaml"
    rc = cli.main(["plan", "from-text", "Compute 16-day NDVI for Hong Kong in 2024 and export CSV.", "--out", str(out), "--json"])
    assert rc == 0
    assert out.exists()
    capsys.readouterr()
    rc = cli.main(["plan", "set", str(out), "export.destination", "drive", "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert "schema_version: gee-plan/v0.3" in out.read_text(encoding="utf-8")


def test_hk_2024_16day_template_renders_and_validates(tmp_path):
    context = load_context(Path("evals/contexts/hk_2024_16day_ndvi.json"))
    rendered = render_template(Path("assets/templates"), "hk_2024_16day_ndvi_csv", context)
    assert "CADENCE_DAYS = 16" in rendered
    assert "EXPORT_SELECTORS" in rendered
    assert "build_16day_statistics" in rendered
    script = tmp_path / "hk_2024_16day_ndvi.py"
    script.write_text(rendered, encoding="utf-8")
    report = validate_script(script).to_dict()
    assert report["ok"] is True
    assert "agent_script_contract" in report["semantic_rulesets"]


def test_plan_from_yaml_renders_v03_hk_16day_plan(tmp_path, capsys):
    plan_path = tmp_path / "hk_16day_plan.yaml"
    script_path = tmp_path / "hk_16day.py"
    rc = cli.main(
        [
            "plan",
            "from-text",
            "Compute 16-day NDVI for Hong Kong in 2024 and export CSV.",
            "--out",
            str(plan_path),
            "--json",
        ]
    )
    assert rc == 0
    capsys.readouterr()
    rc = cli.main(["plan", "from-yaml", str(plan_path), "--script-out", str(script_path), "--json"])
    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["data"]["script"] == str(script_path)
    assert payload["data"]["validation"]["ok"] is True
    assert "CADENCE_DAYS = 16" in script_path.read_text(encoding="utf-8")


def test_plan_review_accepts_v03_plan_without_task_id(tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)

    rc = cli.main(["plan", "review", str(plan_path), "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["schema_version"] == "gee-plan/v0.3"
    assert payload["plan"]["plan_id"] == "vegetation-index-ndvi-hong-kong-2024"
    assert payload["task"]["template"] == "hk_2024_16day_ndvi_csv"
    assert "Live execution requires explicit confirmation" in payload["review"]


def test_preflight_plan_runs_v03_anchor_month_adapter(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)
    calls = []

    def fake_preflight(config):
        calls.append(config)
        return {
            "ok": True,
            "decision": "allow_export",
            "project": config.project,
            "year": config.year,
            "month": config.month,
            "scope": config.scope,
            "aoi_name": "Hong Kong",
            "dataset_id": config.dataset_id,
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {"fake": {"ok": True}},
        }

    monkeypatch.setattr(cli, "run_hk_ndvi_preflight", fake_preflight)

    rc = cli.main(["preflight-plan", str(plan_path), "--project", "example-project", "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    report = payload["preflight"]
    assert report["schema_version"] == "gee-plan/v0.3"
    assert report["decision"] == "allow_export"
    assert report["preflight_months"] == [1, 7]
    assert report["expected_export_rows"] == 23
    assert [config.month for config in calls] == [1, 7]
    assert {config.project for config in calls} == {"example-project"}


def test_preflight_plan_retries_retryable_v03_anchor_failure(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)
    calls = []

    def fake_preflight(config):
        calls.append(config.month)
        if config.month == 1 and calls.count(1) == 1:
            raise cli.EarthEngineUnavailable(
                "Earth Engine initialization failed. Original error: HTTPSConnectionPool("
                "host='oauth2.googleapis.com', port=443): Max retries exceeded with url: /token"
            )
        return {
            "ok": True,
            "decision": "allow_export",
            "project": config.project,
            "year": config.year,
            "month": config.month,
            "scope": config.scope,
            "aoi_name": "Hong Kong",
            "dataset_id": config.dataset_id,
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {"fake": {"ok": True}},
        }

    monkeypatch.setattr(cli, "run_hk_ndvi_preflight", fake_preflight)
    monkeypatch.setattr(cli.time, "sleep", lambda seconds: None)

    rc = cli.main(["preflight-plan", str(plan_path), "--project", "example-project", "--json"])

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert calls == [1, 1, 7]
    january = payload["preflight"]["monthly_reports"][0]
    assert january["ok"] is True
    assert january["retry_attempts"][0]["ok"] is False
    assert january["retry_attempts"][1]["ok"] is True


def test_run_plan_v03_refuses_export_when_preflight_blocks(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)
    execute_calls = []

    monkeypatch.setattr(
        cli,
        "_preflight_from_v03_plan",
        lambda args, plan, context: {
            "ok": False,
            "decision": "block_export",
            "schema_version": "gee-plan/v0.3",
            "critical_error": {"category": "TEST_PREFLIGHT_FAILED", "message": "blocked"},
            "errors": [{"category": "TEST_PREFLIGHT_FAILED", "message": "blocked"}],
            "warnings": [],
            "checks": {},
        },
    )
    monkeypatch.setattr(cli, "execute_script", lambda *args, **kwargs: execute_calls.append((args, kwargs)))

    rc = cli.main(
        [
            "run-plan",
            str(plan_path),
            "--project",
            "example-project",
            "--confirm-live",
            "--json",
        ]
    )

    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["schema_version"] == "gee-plan/v0.3"
    assert payload["preflight"]["decision"] == "block_export"
    assert payload["data"]["preflight"]["decision"] == "block_export"
    assert execute_calls == []


def test_run_plan_v03_missing_confirm_live_is_json(tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)

    rc = cli.main(["run", str(plan_path), "--project", "example-project", "--json"])

    assert rc == 2
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["command"] == "run-plan"
    assert payload["error"]["code"] == "CONFIRM_LIVE_REQUIRED"


def test_run_plan_v03_success_executes_script_once(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)
    execute_calls = []

    monkeypatch.setattr(
        cli,
        "_preflight_from_v03_plan",
        lambda args, plan, context: {
            "ok": True,
            "decision": "allow_export",
            "schema_version": "gee-plan/v0.3",
            "export_description": context["export_description"],
            "drive_folder": context["drive_folder"],
            "file_prefix": context["file_prefix"],
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {},
        },
    )

    def fake_execute(script_path, project, authenticate=False):
        execute_calls.append({"script_path": str(script_path), "project": project, "authenticate": authenticate})
        return {"script": str(script_path), "system_exit_code": 0}

    monkeypatch.setattr(cli, "execute_script", fake_execute)
    monkeypatch.setattr(
        cli,
        "monitor_tasks",
        lambda project, authenticate=False, timeout_seconds=0: [
            {
                "id": "task-1",
                "description": "test_hk_2024_16day_ndvi",
                "state": "READY",
                "creation_timestamp_ms": 1,
                "update_timestamp_ms": 1,
            }
        ],
    )

    rc = cli.main(
        [
            "run-plan",
            str(plan_path),
            "--project",
            "example-project",
            "--confirm-live",
            "--json",
        ]
    )

    assert rc == 0
    payload = _payload(capsys)
    assert payload["ok"] is True
    assert payload["schema_version"] == "gee-plan/v0.3"
    assert payload["live_run"]["export_description"] == "test_hk_2024_16day_ndvi"
    assert payload["data"]["live_run"]["export_description"] == "test_hk_2024_16day_ndvi"
    assert payload["live_run"]["matching_tasks"][0]["id"] == "task-1"
    assert len(execute_calls) == 1
    assert execute_calls[0]["project"] == "example-project"


def test_run_plan_v03_does_not_claim_success_without_observed_export_task(monkeypatch, tmp_path, capsys):
    plan_path = _write_v03_hk_plan(tmp_path, capsys)

    monkeypatch.setattr(
        cli,
        "_preflight_from_v03_plan",
        lambda args, plan, context: {
            "ok": True,
            "decision": "allow_export",
            "schema_version": "gee-plan/v0.3",
            "export_description": context["export_description"],
            "drive_folder": context["drive_folder"],
            "file_prefix": context["file_prefix"],
            "critical_error": None,
            "errors": [],
            "warnings": [],
            "checks": {},
        },
    )
    monkeypatch.setattr(
        cli,
        "execute_script",
        lambda script_path, project, authenticate=False: {"script": str(script_path), "system_exit_code": 0},
    )
    monkeypatch.setattr(cli, "monitor_tasks", lambda project, authenticate=False, timeout_seconds=0: [])

    rc = cli.main(
        [
            "run-plan",
            str(plan_path),
            "--project",
            "example-project",
            "--confirm-live",
            "--json",
        ]
    )

    assert rc == 1
    payload = _payload(capsys)
    assert payload["ok"] is False
    assert payload["live_run"]["script_executed"] is True
    assert payload["data"]["live_run"]["script_executed"] is True
    assert payload["live_run"]["export_task_observed"] is False
    assert payload["live_run"]["error"]["code"] == "EXPORT_TASK_NOT_OBSERVED"
