from __future__ import annotations

import ast
import json
from pathlib import Path

from geeskill.catalog import get_dataset
from geeskill.kg import build_graph
from geeskill.plans import validate_v03_plan_schema
from geeskill.recipes import get_recipe
from geeskill.semantic import validate_semantics
from geeskill.templates import render_template


TEMPLATE_CONTEXT = {
    "script_name": "annual_transition_example",
    "years": [2019, 2020, 2021, 2022],
    "aoi_asset": "projects/example/assets/reviewed_aoi",
    "annual_landcover_asset": "projects/example/assets/annual_landcover",
    "activity_collection_id": "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG",
    "activity_band": "avg_rad",
    "accessibility_image_id": "projects/example/assets/accessibility",
    "landcover_band": "classification",
    "impervious_class_codes": [8],
    "cropland_class_codes": [1],
    "ecological_class_codes": [2, 3, 4, 5, 6],
    "target_crs": "EPSG:6933",
    "target_crs_transform": [1000, 0, 0, 0, -1000, 0],
    "stable_year_min": 3,
    "urban_impervious_threshold": 0.6,
    "rural_cropland_threshold": 0.6,
    "urban_activity_threshold": 2.0,
    "rural_activity_threshold": 0.5,
    "samples_per_class": 100,
    "trees": 500,
    "min_leaf_population": 5,
    "random_seed": 3407,
    "drive_folder": "gee_exports",
    "file_prefix": "annual_transition_example",
    "max_pixels": 10_000_000_000_000,
}


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "workflow.py"
    path.write_text(text, encoding="utf-8")
    return path


def test_recipe_is_registered_without_schema_bump() -> None:
    recipe = get_recipe("annual-endmember-transition")
    assert recipe is not None
    assert recipe["task_type"] == "change_detection"
    assert recipe["template"] == "recipes/annual_endmember_transition"
    assert recipe["validation_profile"] == "annual_endmember_transition"


def test_template_renders_parseable_script_and_passes_annual_rules(tmp_path: Path) -> None:
    for template_dir in (
        Path("assets/templates"),
        Path("src/geeskill/resources/templates"),
    ):
        rendered = render_template(
            template_dir,
            "recipes/annual_endmember_transition",
            TEMPLATE_CONTEXT,
        )
        ast.parse(rendered)
        path = _write(tmp_path, rendered)
        errors = [
            finding
            for finding in validate_semantics(path, ["annual_endmember_transition"])
            if finding.severity == "error"
        ]
        assert not errors
        for marker in (
            "NASA/HLS/HLSL30/v002",
            "NASA/HLS/HLSS30/v002",
            "projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL",
            "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG",
            "ee.Classifier.smileRandomForest",
            "urban_probability",
            "model_uncertainty",
            "endpoint_samples",
            "coverage",
            "GEE_CRS_OVERRIDES",
            'AUTHORITY["EPSG","6933"]',
            "HLS_REFLECTANCE_SCALE_POLICY",
            "gee_catalog_float_no_0_0001_multiplier",
            'setOutputMode("MULTIPROBABILITY")',
            "arrayFlatten",
            "setDefaultProjection",
        ):
            assert marker in rendered
        assert ".multiply(0.0001)" not in rendered


def test_public_and_packaged_annual_templates_are_identical() -> None:
    public_template = Path(
        "assets/templates/recipes/annual_endmember_transition.py.j2"
    ).read_text(encoding="utf-8")
    packaged_template = Path(
        "src/geeskill/resources/templates/recipes/annual_endmember_transition.py.j2"
    ).read_text(encoding="utf-8")
    assert packaged_template == public_template


def test_v03_selected_dataset_metadata_is_typed_without_version_change() -> None:
    plan = json.loads(Path("schemas/gee-plan-v0.3.schema.json").read_text(encoding="utf-8"))
    dataset_properties = plan["$defs"]["datasetChoice"]["properties"]
    assert plan["properties"]["schema_version"]["const"] == "gee-plan/v0.3"
    for field in (
        "catalog_status",
        "license",
        "source_role",
        "private_asset",
        "expected_years",
        "aggregation_semantics",
    ):
        assert field in dataset_properties


def test_runtime_plan_validation_accepts_dataset_metadata() -> None:
    plan = {
        "schema_version": "gee-plan/v0.3",
        "plan_id": "annual-transition",
        "raw_user_request": "Build annual endpoint probabilities.",
        "intent": {"metric": "urban_probability", "recipe_id": "annual-endmember-transition", "golden_example": False},
        "task_type": "change_detection",
        "aoi": {"type": "asset", "name": "reviewed aoi", "source": "user-controlled"},
        "time_range": {"label": "2019-2022", "date_start": "2019-01-01", "date_end": "2023-01-01"},
        "candidate_datasets": [{"dataset_id": "NASA/HLS/HLSL30/v002"}],
        "selected_datasets": [
            {
                "dataset_id": "projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL",
                "catalog_status": "community",
                "license": "CC BY 4.0",
                "source_role": "population covariate",
                "private_asset": False,
                "expected_years": [2019, 2020, 2021, 2022],
                "aggregation_semantics": "count_density_area_weighted",
            }
        ],
        "indices_or_variables": ["urban_probability"],
        "operators": ["reduceResolution", "smileRandomForest"],
        "masking": {"required": True, "policy": "HLS Fmask"},
        "reducers": ["mean", "sum"],
        "scale_crs_projection": {"scale_m": 1000, "crs": "EPSG:6933", "notes": "fixed affine transform"},
        "output": {"type": "GeoTIFF", "destination": "Drive"},
        "export": {"requires_confirmation": True, "live_execution_default": False, "destination": "Drive", "format": "GeoTIFF"},
        "preflight": {"profile": "optical_index", "checks": ["annual coverage", "asset permissions"]},
        "validation": {"rulesets": ["annual_endmember_transition"], "must_pass_before_live": True},
        "limitations": ["render-and-validate only"],
        "review_questions": ["Are class codes reviewed?"],
        "execution": {
            "template": "recipes/annual_endmember_transition",
            "template_ready": True,
            "context": TEMPLATE_CONTEXT,
            "outputs": {"script": "annual_transition.py"},
            "live_adapter_ready": False,
            "context_review_required": True,
        },
    }
    assert validate_v03_plan_schema(plan) == []


def test_each_stable_annual_validation_code_is_emitted(tmp_path: Path) -> None:
    bad_scripts = {
        "ANNUAL_COVERAGE_GAP": "annual_endmember_transition = True\n",
        "GRID_ALIGNMENT_MISMATCH": "EXPECTED_YEARS=[2020]\nfilterDate='x'\ncoverage_count=1\n",
        "COUNT_RESAMPLING_UNSAFE": "EXPECTED_YEARS=[2020]\nfilterDate='x'\ncoverage_count=1\nequal_area=True\nCRS_TRANSFORM=[]\nreproject=True\nLandScan='population_count'\n",
        "COMMUNITY_ASSET_METADATA_DRIFT": "EXPECTED_YEARS=[2020]\nfilterDate='x'\ncoverage_count=1\nequal_area=True\nCRS_TRANSFORM=[]\nreproject=True\npopulation_density=True\npixelArea=True\nreduceResolution=True\narea_weighted=True\nprojects_sat_io=True\n",
        "PRIVATE_ASSET_EXPORT_RISK": "EXPECTED_YEARS=[2020]\nfilterDate='x'\ncoverage_count=1\nequal_area=True\nCRS_TRANSFORM=[]\nreproject=True\nasset='projects/example/assets/private_landcover'\n",
        "CATEGORICAL_RESAMPLING_UNSAFE": "EXPECTED_YEARS=[2020]\nfilterDate='x'\ncoverage_count=1\nequal_area=True\nCRS_TRANSFORM=[]\nreproject=True\ncategorical=True\nlandcover_band='class'\n",
        "HLS_REFLECTANCE_DOUBLE_SCALING": (
            "EXPECTED_YEARS=[2020]\n"
            "HLS='NASA/HLS/HLSL30/v002'\n"
            "def _prepare_l30(image):\n"
            "    return image.select('B2').multiply(0.0001)\n"
        ),
    }
    for expected_code, script in bad_scripts.items():
        findings = validate_semantics(_write(tmp_path, script), ["annual_endmember_transition"])
        assert expected_code in {finding.code for finding in findings}


def test_forced_categorical_reproject_is_a_memory_warning(tmp_path: Path) -> None:
    script = """
EXPECTED_YEARS=[2020]
filterDate='x'
coverage_count=1
equal_area=True
CRS_TRANSFORM=[]
setDefaultProjection=True
categorical=True
landcover_band='class'
class_codes=[1]
PRIVATE_ASSET_EXPORT_POLICY='derived_outputs_only'
asset='projects/example/assets/private_landcover'
def class_fraction(image):
    return image.eq(1).reduceResolution().reproject('EPSG:6933')
"""
    findings = validate_semantics(_write(tmp_path, script), ["annual_endmember_transition"])
    match = [item for item in findings if item.code == "FORCED_REPROJECT_MEMORY_RISK"]
    assert len(match) == 1
    assert match[0].severity == "warning"


def test_landscan_and_external_cards_are_catalog_and_kg_visible() -> None:
    assert get_dataset("projects/sat-io/open-datasets/ORNL/LANDSCAN_GLOBAL")
    assert get_dataset("external/annual-categorical-landcover")
    graph = build_graph(
        source_registry_path=Path("references/sources/source_registry.yml"),
        evidence_cards_dir=Path("references/evidence_cards"),
        seed_graph_path=Path("references/graph/seed_graph.yml"),
    )
    assert "evidence:landscan_global_community" in graph.nodes
    assert "evidence:external_annual_categorical_landcover" in graph.nodes
