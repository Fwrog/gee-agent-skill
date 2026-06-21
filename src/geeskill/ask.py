from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import error_payload
from .paths import default_boundary_path


SUPPORTED_EXAMPLES = [
    "Compute January 2024 mean NDVI for Hong Kong and export CSV.",
    "Calculate Hong Kong NDVI for January 2024.",
    "Export January 2024 Hong Kong NDVI as CSV.",
    "2024 Jan Hong Kong NDVI CSV",
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


def _canonical_context(export_folder: str = "gee_exports", boundary_geojson: str | None = None) -> dict[str, Any]:
    boundary = Path(boundary_geojson) if boundary_geojson else default_boundary_path()
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


def _canonical_task(query: str, export_folder: str, boundary_geojson: str | None) -> dict[str, Any]:
    return {
        "id": "hk_2024_01_ndvi_v01",
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


def route_request(
    request: str,
    *,
    export_folder: str = "gee_exports",
    boundary_geojson: str | None = None,
) -> dict[str, Any]:
    text = _normalize(request)
    if _is_full_year_district_request(text):
        return {
            "ok": False,
            "status": "unsupported",
            "error": error_payload(
                "UNSUPPORTED_TASK",
                "v0.1 supports January 2024 whole-Hong-Kong NDVI CSV. Full 2024 district-level monthly NDVI is planned for v0.2.",
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
                "Request is missing one or more v0.1 requirements: NDVI, Hong Kong AOI, and January 2024.",
            ),
            "supported_examples": SUPPORTED_EXAMPLES,
        }

    return {
        "ok": False,
        "status": "unsupported",
        "error": error_payload(
            "UNSUPPORTED_TASK",
            "The request is outside the v0.1 deterministic router.",
        ),
        "supported_examples": SUPPORTED_EXAMPLES,
    }
