from geeskill.intents import build_general_plan_from_text
from geeskill.plans import validate_v03_plan_schema


REQUEST = "Compare HLS and MODIS NDVI for a supplied AOI in 2024 and export CSV."


def test_product_intercomparison_plan_is_scale_aware_and_bounded():
    result = build_general_plan_from_text(REQUEST)

    assert result["ok"], result
    assert result["status"] == "planned"
    plan = result["plan"]
    assert plan["task_type"] == "product_intercomparison"
    assert plan["intent"]["metric"] == "NDVI_PRODUCT_INTERCOMPARISON"
    assert plan["intent"]["recipe_id"] == "hls-modis-ndvi-product-intercomparison"
    assert {item["dataset_id"] for item in plan["selected_datasets"]} == {
        "NASA/HLS/HLSL30/v002",
        "NASA/HLS/HLSS30/v002",
        "MODIS/061/MOD13Q1",
    }
    assert plan["indices_or_variables"] == ["NDVI"]
    assert plan["scale_crs_projection"]["scale_m"] == 250
    assert "MOD13Q1" in plan["scale_crs_projection"]["crs"]
    assert "product_intercomparison" in plan["validation"]["rulesets"]
    assert plan["execution"]["template_ready"] is False
    assert any("not in-situ ground-truth" in item for item in plan["limitations"])
    assert validate_v03_plan_schema(plan) == []

