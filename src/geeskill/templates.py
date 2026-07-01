from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError


class TemplateContextError(ValueError):
    """Raised when a template context is incomplete or invalid."""


TEMPLATE_SCHEMAS: dict[str, dict[str, Any]] = {
    "sentinel2_ndvi_composite": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_asset",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "sentinel2_index_image": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_asset",
            "index_name",
            "index_bands",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "sentinel2_index_table": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_name",
            "aoi_asset",
            "index_name",
            "index_bands",
            "index_output_field",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
            "output_schema",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "landsat_lst": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_asset",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "landsat_lst_table": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_name",
            "aoi_asset",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
            "output_schema",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "zonal_statistics": {
        "required": [
            "script_name",
            "image_expression",
            "zones_asset",
            "date_start",
            "date_end",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale"],
    },
    "dynamic_world_landcover_summary": {
        "required": [
            "script_name",
            "dataset_id",
            "date_start",
            "date_end",
            "aoi_name",
            "aoi_asset",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
            "output_schema",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "hk_district_monthly_ndvi": {
        "required": [
            "script_name",
            "year",
            "dataset_id",
            "boundary_geojson",
            "district_property",
            "scale",
            "crs",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale"],
    },
    "hk_district_january_ndvi_smoke": {
        "required": [
            "script_name",
            "year",
            "smoke_month",
            "smoke_region",
            "boundary_geojson",
            "district_property",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "tile_scale"],
    },
    "hk_january_2024_ndvi_csv": {
        "required": [
            "script_name",
            "year",
            "month",
            "date_start",
            "date_end",
            "aoi_name",
            "aoi_source",
            "boundary_geojson",
            "dataset_id",
            "scale",
            "crs",
            "tile_scale",
            "cloudy_pixel_percentage",
            "max_pixels",
            "export_description",
            "drive_folder",
            "file_prefix",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "hk_january_2024_ndvi_by_landcover_csv": {
        "required": [
            "script_name",
            "year",
            "month",
            "date_start",
            "date_end",
            "aoi_name",
            "aoi_source",
            "boundary_geojson",
            "dataset_id",
            "landcover_dataset_id",
            "landcover_strategy",
            "dynamic_world_probability_threshold",
            "scale",
            "crs",
            "tile_scale",
            "cloudy_pixel_percentage",
            "max_pixels",
            "export_description",
            "drive_folder",
            "file_prefix",
        ],
        "positive_numbers": ["scale", "tile_scale", "max_pixels"],
    },
    "sentinel1_flood_before_after": {
        "required": [
            "script_name",
            "before_start",
            "before_end",
            "after_start",
            "after_end",
            "aoi_asset",
            "export_description",
            "drive_folder",
        ],
        "positive_numbers": ["scale", "max_pixels"],
    },
}


def load_context(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yml", ".yaml"}:
        loaded = yaml.safe_load(text)
    else:
        loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise TemplateContextError(f"Template context must be an object: {path}")
    return loaded


def _check_iso_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise TemplateContextError(f"{field} must be an ISO date, got {value!r}") from exc


def validate_context(template_name: str, context: dict[str, Any]) -> None:
    schema = TEMPLATE_SCHEMAS.get(template_name)
    if schema is None:
        raise TemplateContextError(f"Unknown template: {template_name}")
    missing = [key for key in schema["required"] if key not in context]
    if missing:
        raise TemplateContextError(f"Missing required template context keys: {', '.join(missing)}")
    if "date_start" in context and "date_end" in context:
        start = _check_iso_date(str(context["date_start"]), "date_start")
        end = _check_iso_date(str(context["date_end"]), "date_end")
        if end <= start:
            raise TemplateContextError("date_end must be after date_start")
    if "year" in context:
        year = int(context["year"])
        if year < 1980 or year > 2100:
            raise TemplateContextError("year must be between 1980 and 2100")
    for key in schema.get("positive_numbers", []):
        if key in context and float(context[key]) <= 0:
            raise TemplateContextError(f"{key} must be positive")


def _safe_template_path(template_dir: Path, template_name: str) -> str:
    if "\\" in template_name:
        raise TemplateContextError("Template name must use POSIX-style paths.")
    if template_name.startswith("/") or any(part in {"", ".", ".."} for part in template_name.split("/")):
        raise TemplateContextError("Template path must stay under the approved template directory.")
    filename = f"{template_name}.py.j2"
    path = (template_dir / filename).resolve()
    root = template_dir.resolve()
    if root not in path.parents or not path.exists():
        raise TemplateContextError(f"Template not found under approved directory: {template_name}")
    return filename


def render_template(template_dir: Path, template_name: str, context: dict[str, Any]) -> str:
    filename = _safe_template_path(template_dir, template_name)
    validate_context(template_name, context)
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )
    try:
        rendered = env.get_template(filename).render(**context)
    except TemplateError as exc:
        raise TemplateContextError(f"Failed to render {template_name}: {exc}") from exc
    if "{{" in rendered or "{%" in rendered:
        raise TemplateContextError("Rendered script still contains unresolved Jinja tokens.")
    return rendered


TEMPLATE_SCHEMAS.update(
    {
        "recipes/vegetation_index": TEMPLATE_SCHEMAS["sentinel2_ndvi_composite"],
        "recipes/water_index": TEMPLATE_SCHEMAS["sentinel2_index_image"],
        "recipes/builtup_index": TEMPLATE_SCHEMAS["sentinel2_index_table"],
        "recipes/landsat_lst": TEMPLATE_SCHEMAS["landsat_lst_table"],
        "recipes/sentinel1_change": TEMPLATE_SCHEMAS["sentinel1_flood_before_after"],
        "recipes/zonal_statistics": TEMPLATE_SCHEMAS["zonal_statistics"],
        "recipes/export_image": TEMPLATE_SCHEMAS["sentinel2_index_image"],
        "recipes/export_table": TEMPLATE_SCHEMAS["sentinel2_index_table"],
    }
)
