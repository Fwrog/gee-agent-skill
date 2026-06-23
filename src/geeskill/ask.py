from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import error_payload


SUPPORTED_EXAMPLES = [
    "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
    "Calculate Hong Kong NDVI for January 2024.",
    "Export January 2024 Hong Kong NDVI as CSV.",
    "2024 Jan Hong Kong NDVI CSV",
    "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
    "Calculate Hong Kong January 2024 NDVI by land use.",
    "Export land-cover-aware NDVI for Hong Kong in Jan 2024.",
    "Compare all-surface and land-only NDVI for Hong Kong January 2024.",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _mentions_january_2024(text: str) -> bool:
    return bool(re.search(r"\b(january|jan)\b", text)) and "2024" in text


def _is_full_year_district_request(text: str) -> bool:
    has_district = "district" in text or "district-level" in text
    has_full_year = (
        "full year" in text
        or "all 12" in text
        or ("monthly" in text and "2024" in text)
        or "2024 monthly" in text
    )
    return "ndvi" in text and "hong kong" in text and has_district and has_full_year


def _is_landcover_request(text: str) -> bool:
    landcover_terms = [
        "land-cover",
        "land cover",
        "landcover",
        "land-use",
        "land use",
        "land-only",
        "land only",
        "dynamic world",
        "class",
        "classes",
    ]
    compare_terms = ["all-surface", "all surface", "non-water", "non water", "vegetation", "built"]
    return (
        "ndvi" in text
        and "hong kong" in text
        and _mentions_january_2024(text)
        and (any(term in text for term in landcover_terms) or any(term in text for term in compare_terms))
    )


def _canonical_context(export_folder: str = "gee_exports", boundary_geojson: str | None = None) -> dict[str, Any]:
    boundary = Path(boundary_geojson) if boundary_geojson else Path("references/boundaries/hk_18_districts.geojson")
    return {
        "script_name": "hk_2024_01_ndvi_csv",
        "year": 2024,
        "month": 1,
        "date_start": "2024-01-01",
        "date_end": "2024-02-01",
        "aoi_name": "Hong Kong",
        "aoi_source": "Hong Kong 18 Districts GeoJSON curated in references/boundaries",
        "boundary_geojson": boundary.as_posix(),
        "dataset_id": "COPERNICUS/S2_SR_HARMONIZED",
        "scale": 10,
        "crs": "EPSG:4326",
        "tile_scale": 4,
        "cloudy_pixel_percentage": 80,
        "max_pixels": 100000000,
        "export_description": "hk_2024_01_ndvi_v01",
        "drive_folder": export_folder,
        "file_prefix": "hk_2024_01_ndvi_v01",
    }


def _landcover_context(export_folder: str = "gee_exports", boundary_geojson: str | None = None) -> dict[str, Any]:
    context = _canonical_context(export_folder=export_folder, boundary_geojson=boundary_geojson)
    context.update(
        {
            "script_name": "hk_2024_01_ndvi_by_landcover_csv",
            "landcover_dataset_id": "GOOGLE/DYNAMICWORLD/V1",
            "landcover_strategy": "dynamic_world_time_matched_probability_masks",
            "dynamic_world_probability_threshold": 0.35,
            "worldcover_dataset_id": "ESA/WorldCover/v200",
            "export_description": "hk_2024_01_ndvi_landcover_v02",
            "file_prefix": "hk_2024_01_ndvi_landcover_v02",
        }
    )
    return context


def _canonical_task(query: str, export_folder: str, boundary_geojson: str | None) -> dict[str, Any]:
    return {
        "id": "hk_2024_01_ndvi_v01",
        "intent": "hk_january_2024_ndvi_csv",
        "task": "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
        "query": query,
        "template": "hk_january_2024_ndvi_csv",
        "context": _canonical_context(export_folder=export_folder, boundary_geojson=boundary_geojson),
        "outputs": {
            "script": "outputs/scripts/hk_2024_01_ndvi_csv.py",
            "plan": "outputs/plans/hk_2024_01_ndvi_v01.md",
        },
        "version": "v0.1",
    }


def _landcover_task(query: str, export_folder: str, boundary_geojson: str | None) -> dict[str, Any]:
    output_schema = [
        "aoi_name",
        "year",
        "month",
        "date_start",
        "date_end",
        "dataset_id",
        "landcover_dataset_id",
        "landcover_strategy",
        "scale_m",
        "crs",
        "all_surface_mean_ndvi",
        "non_water_mean_ndvi",
        "land_only_mean_ndvi",
        "vegetation_mean_ndvi",
        "trees_mean_ndvi",
        "grass_mean_ndvi",
        "shrub_and_scrub_mean_ndvi",
        "built_mean_ndvi",
        "bare_mean_ndvi",
        "water_fraction",
        "built_fraction",
        "vegetation_fraction",
        "trees_fraction",
        "grass_fraction",
        "s2_image_count_before_cloud_filter",
        "s2_image_count_after_cloud_filter",
        "dynamic_world_image_count",
        "dynamic_world_probability_threshold",
        "export_description",
    ]
    return {
        "id": "hk_2024_01_ndvi_landcover_v02",
        "intent": "hk_january_2024_ndvi_by_landcover_csv",
        "task": "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
        "query": query,
        "template": "hk_january_2024_ndvi_by_landcover_csv",
        "context": _landcover_context(export_folder=export_folder, boundary_geojson=boundary_geojson),
        "outputs": {
            "script": "outputs/scripts/hk_2024_01_ndvi_by_landcover_csv.py",
            "plan": "outputs/plans/hk_2024_01_ndvi_landcover_v02.md",
        },
        "output_schema": output_schema,
        "version": "v0.2",
        "limitations": [
            "Dynamic World is probabilistic; sparse or low-confidence classes may return null statistics.",
            "Hong Kong administrative boundary defines where to compute; land-cover data defines masks and strata.",
            "All-surface NDVI includes water, built-up, bare, and vegetated pixels and should not be read as vegetation-only NDVI.",
            "ESA WorldCover v200 is documented as an optional static 2021 reference, not used as the primary time-matched mask.",
        ],
    }


def route_request(
    request: str,
    *,
    export_folder: str = "gee_exports",
    boundary_geojson: str | None = None,
) -> dict[str, Any]:
    text = _normalize(request)
    if _is_landcover_request(text):
        return {
            "ok": True,
            "status": "supported",
            "intent": "hk_january_2024_ndvi_by_landcover_csv",
            "slots": {
                "aoi": "Hong Kong",
                "year": 2024,
                "month": 1,
                "metric": "NDVI",
                "stratification": "land-cover",
                "export": "CSV",
            },
            "task": _landcover_task(request, export_folder, boundary_geojson),
        }

    if _is_full_year_district_request(text):
        return {
            "ok": False,
            "status": "unsupported",
            "error": error_payload(
                "UNSUPPORTED_TASK",
                "The legacy golden-route matcher supports the reviewed Hong Kong January 2024 NDVI CSV examples. Use the v0.3 plan command for broader requests.",
            ),
            "closest_supported_command": (
                'gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." '
                "--dry-run --json"
            ),
            "supported_examples": SUPPORTED_EXAMPLES,
        }

    core_terms = ["ndvi" in text, "hong kong" in text, _mentions_january_2024(text)]
    if all(core_terms):
        return {
            "ok": True,
            "status": "supported",
            "intent": "hk_january_2024_ndvi_csv",
            "task": _canonical_task(request, export_folder, boundary_geojson),
        }

    if "ndvi" in text or "hong kong" in text or "csv" in text:
        return {
            "ok": False,
            "status": "ambiguous",
            "error": error_payload(
                "AMBIGUOUS_TASK",
                "Request is missing one or more legacy golden-route fields: NDVI, Hong Kong AOI, and January 2024.",
            ),
            "supported_examples": SUPPORTED_EXAMPLES,
        }

    return {
        "ok": False,
        "status": "unsupported",
        "error": error_payload(
            "UNSUPPORTED_TASK",
            "The request is outside the legacy golden-route matcher. Use gee-skill plan from-text for v0.3 general planning.",
        ),
        "supported_examples": SUPPORTED_EXAMPLES,
    }
