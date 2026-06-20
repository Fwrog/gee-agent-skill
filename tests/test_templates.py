from pathlib import Path

import pytest

from geeskill.templates import TemplateContextError, load_context, render_template


TEMPLATE_DIR = Path("assets/templates")


def test_render_hk_monthly_ndvi_template_has_required_terms():
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    rendered = render_template(TEMPLATE_DIR, "hk_district_monthly_ndvi", context)
    assert "COPERNICUS/S2_SR_HARMONIZED" in rendered
    assert "filterDate(start, end)" in rendered
    assert "filterBounds(aoi)" in rendered
    assert "reduceRegions" in rendered
    assert "ee.batch.Export.table.toDrive" in rendered
    assert "{{" not in rendered


def test_render_missing_variable_fails():
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    context.pop("scale")
    with pytest.raises(TemplateContextError, match="Missing required"):
        render_template(TEMPLATE_DIR, "hk_district_monthly_ndvi", context)


def test_template_path_traversal_fails():
    context = load_context(Path("evals/contexts/hk_2024_monthly_ndvi.json"))
    with pytest.raises(TemplateContextError, match="path"):
        render_template(TEMPLATE_DIR, "../hk_district_monthly_ndvi", context)

