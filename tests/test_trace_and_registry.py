import json
from pathlib import Path

from geeskill.cli import main
from geeskill.catalog import list_datasets
from geeskill.plans import validate_v03_plan_schema
from geeskill.recipes import load_recipe_registry
from geeskill.templates import render_template
from geeskill.tool_registry import exposed_tools, installed_tools


def test_recipe_registry_is_file_backed_yaml():
    registry = load_recipe_registry()
    assert registry["schema_version"] == "gee-recipes/v0.3"
    assert registry["path"].endswith("registry.yaml")
    recipes = [item.to_dict() for item in registry["recipes"]]
    assert len(recipes) >= 10
    assert {item["recipe_id"] for item in recipes} >= {
        "vegetation-index-ndvi",
        "water-index-ndwi",
        "builtup-index-ndbi",
        "landsat-lst",
        "sentinel1-flood-before-after",
        "zonal-statistics-table",
        "image-export-geotiff",
        "table-export-csv",
    }
    assert all("limitations" in item for item in recipes)
    assert all(item["template"] for item in recipes)


def test_recipe_registry_cards_are_rag_visible_markdown():
    registry = load_recipe_registry()
    recipes = [item.to_dict() for item in registry["recipes"]]
    cards = list(Path("references/knowledge_base/recipes").glob("*.md"))
    combined = {path.name: path.read_text(encoding="utf-8") for path in cards}
    for recipe in recipes:
        matches = [text for text in combined.values() if f"recipe_id: {recipe['recipe_id']}" in text]
        assert len(matches) == 1, recipe["recipe_id"]
        text = matches[0]
        for field in [
            "task_type",
            "required_inputs",
            "candidate_datasets",
            "template",
            "preflight_profile",
            "validation_profile",
            "output_schema",
            "live_risk_level",
            "limitations",
        ]:
            assert f"{field}:" in text or f"## {field.replace('_', ' ').title()}" in text, (recipe["recipe_id"], field)


def test_structured_dataset_cards_are_rag_visible_markdown():
    required_fields = {
        "dataset_id",
        "title",
        "provider",
        "gee_url",
        "temporal_coverage",
        "spatial_resolution",
        "bands",
        "qa_bands",
        "common_uses",
        "recommended_tasks",
        "scale_notes",
        "projection_notes",
        "license_attribution",
        "last_checked",
    }
    cards = list(Path("references/knowledge_base/datasets").glob("*.md"))
    combined = {path.name: path.read_text(encoding="utf-8") for path in cards}
    for dataset in list_datasets():
        matches = [text for text in combined.values() if f"dataset_id: {dataset['dataset_id']}" in text]
        assert len(matches) == 1, dataset["dataset_id"]
        text = matches[0]
        for field in required_fields:
            assert f"{field}:" in text, (dataset["dataset_id"], field)


def test_gitignore_blocks_private_research_artifacts():
    text = Path(".gitignore").read_text(encoding="utf-8")
    for pattern in [
        "*_GEE_private/",
        "*_private/",
        "private_*/",
        "private_research/",
        "paper_private/",
        "*.docx",
        "~$*.docx",
    ]:
        assert pattern in text


def test_v03_plan_schema_validator_reports_missing_fields():
    errors = validate_v03_plan_schema({"schema_version": "gee-plan/v0.3", "plan_id": "bad"})
    assert errors
    assert any("missing required fields" in error for error in errors)


def test_v03_plan_schema_validator_reports_nested_contract_errors():
    plan = {
        "schema_version": "gee-plan/v0.3",
        "plan_id": "bad-nested",
        "raw_user_request": "Compute NDVI.",
        "intent": {"metric": "NDVI", "recipe_id": "", "golden_example": "no"},
        "task_type": "vegetation_index",
        "aoi": {"type": "named_place", "name": "Hong Kong"},
        "time_range": {"label": "2024", "date_start": "2024-01-01"},
        "candidate_datasets": [{"title": "Missing id"}],
        "selected_datasets": [],
        "indices_or_variables": [],
        "operators": [],
        "masking": {"required": "yes", "policy": ""},
        "reducers": [],
        "scale_crs_projection": {"scale_m": 0, "crs": "", "notes": ""},
        "output": {"type": "csv"},
        "export": {"requires_confirmation": True, "live_execution_default": False, "destination": "drive", "format": "CSV"},
        "preflight": {"profile": "unknown_profile", "checks": []},
        "validation": {"rulesets": [], "must_pass_before_live": True},
        "limitations": [],
        "review_questions": [],
        "execution": {"template": None, "template_ready": True, "context": None, "outputs": {}, "live_adapter_ready": False, "context_review_required": True},
    }
    errors = validate_v03_plan_schema(plan)
    assert any("intent.recipe_id" in error for error in errors)
    assert any("aoi missing required keys" in error for error in errors)
    assert any("selected_datasets must contain" in error for error in errors)
    assert any("unsupported preflight.profile" in error for error in errors)
    assert any("execution.template must be" in error for error in errors)


def test_recipe_template_wrapper_renders_existing_template(tmp_path):
    rendered = render_template(
        Path("assets/templates"),
        "recipes/water_index",
        {
            "script_name": "ndwi_wrapper_check",
            "dataset_id": "COPERNICUS/S2_SR_HARMONIZED",
            "date_start": "2024-03-01",
            "date_end": "2024-04-01",
            "aoi_asset": "projects/example/assets/reviewed_aoi",
            "index_name": "NDWI",
            "index_bands": ["B3", "B8"],
            "scale": 10,
            "crs": "EPSG:4326",
            "export_description": "ndwi_wrapper_check",
            "drive_folder": "gee_exports",
            "tile_scale": 4,
            "max_pixels": 10000000000000,
            "cloudy_pixel_percentage": 80,
            "file_prefix": "ndwi_wrapper_check",
        },
    )
    assert "ee.batch.Export.image.toDrive" in rendered
    assert "COPERNICUS/S2_SR_HARMONIZED" in rendered


def test_golden_examples_are_available_for_regression_checks():
    golden_tasks = [
        Path("examples/golden/hk_2024_01_ndvi_v01/task.yaml"),
        Path("examples/golden/hk_2024_01_ndvi_landcover_v02/task.yaml"),
    ]
    for task_path in golden_tasks:
        assert task_path.exists(), task_path


def test_private_academic_demo_is_not_published_as_golden_evidence():
    forbidden_paths = [
        Path("docs/evidence/private_academic_demo"),
        Path("examples/golden/private_academic_demo"),
        Path("examples/private_academic_demo"),
    ]
    for path in forbidden_paths:
        assert not path.exists(), path


def test_tool_registry_separates_installed_and_exposed():
    installed = {item["name"]: item for item in installed_tools()}
    exposed = {item["name"]: item for item in exposed_tools()}
    for name in ["info", "doctor", "observe", "catalog", "recipe", "rules", "plan_general"]:
        assert name in exposed
        assert exposed[name]["dangerous"] is False
    assert "render_template" in installed
    assert "render_template" not in exposed
    assert "--project" in exposed["auth_check"]["requires_explicit_flags"]
    assert exposed["run_live"]["dangerous"] is True
    assert "--confirm-live" in exposed["run_live"]["requires_explicit_flags"]


def test_plan_task_writes_complete_run_trace(tmp_path):
    run_id = "test-trace-plan"
    rc = main(["plan", "examples/hk_2024_monthly_ndvi/task.yaml", "--run-id", run_id])
    assert rc == 0
    run_dir = Path("outputs/runs") / run_id
    expected = [
        "task.yaml",
        "retrieval_trace.json",
        "plan.md",
        "generated_script.py",
        "validation_report.json",
        "dry_run_report.json",
        "environment.json",
        "final_report.md",
    ]
    for name in expected:
        assert (run_dir / name).exists(), name
    trace = json.loads((run_dir / "retrieval_trace.json").read_text(encoding="utf-8"))
    assert trace["evidence"]
    assert all("reason_for_selection" in item for item in trace["evidence"])
    assert "coverage" in trace
    required_evidence_keys = {
        "evidence_type",
        "source_path",
        "source_url",
        "last_checked",
        "primary_status",
        "reason_for_selection",
        "influence",
        "excerpt",
    }
    for item in trace["evidence"]:
        assert required_evidence_keys.issubset(item)
        assert item["last_checked"]
        assert item["reason_for_selection"]
        assert item["influence"]
        assert item["excerpt"]
    assert any(item["source_url"] for item in trace["evidence"])
    assert any(item["evidence_type"] == "operator_relationship_chain" for item in trace["evidence"])
    assert trace["coverage"]["known_failures"] >= 1
    validation = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
    assert "semantic_rulesets" in validation
    dry_run = json.loads((run_dir / "dry_run_report.json").read_text(encoding="utf-8"))
    assert dry_run["contacted_earth_engine"] is False
    assert dry_run["validation_ok"] is True


def test_run_dry_writes_trace(tmp_path):
    main(["plan", "examples/hk_2024_monthly_ndvi/task.yaml", "--run-id", "test-dry-source"])
    script = Path("outputs/runs/test-dry-source/generated_script.py")
    rc = main(["run", str(script), "--dry-run", "--run-id", "test-dry-run", "--json"])
    assert rc == 0
    assert (Path("outputs/runs/test-dry-run/dry_run_report.json")).exists()
