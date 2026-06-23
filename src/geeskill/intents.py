from __future__ import annotations

import re
from datetime import date
from typing import Any

from .ask import route_request
from .catalog import recommend_datasets
from .errors import error_payload
from .recipes import closest_recipes, default_recipe_for


MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


TASK_TYPES = {
    "ndvi": "vegetation_index",
    "evi": "vegetation_index",
    "ndwi": "water_index",
    "mndwi": "water_index",
    "ndbi": "builtup_index",
    "lst": "land_surface_temperature",
    "land surface temperature": "land_surface_temperature",
    "flood": "flood_mapping",
    "land cover": "landcover_summary",
    "landcover": "landcover_summary",
}


DATASET_ALIASES = {
    "sentinel-2": "COPERNICUS/S2_SR_HARMONIZED",
    "sentinel 2": "COPERNICUS/S2_SR_HARMONIZED",
    "s2": "COPERNICUS/S2_SR_HARMONIZED",
    "landsat 8": "LANDSAT/LC08/C02/T1_L2",
    "landsat 9": "LANDSAT/LC09/C02/T1_L2",
    "landsat": "LANDSAT/LC08/C02/T1_L2",
    "sentinel-1": "COPERNICUS/S1_GRD",
    "sentinel 1": "COPERNICUS/S1_GRD",
    "s1": "COPERNICUS/S1_GRD",
    "dynamic world": "GOOGLE/DYNAMICWORLD/V1",
    "worldcover": "ESA/WorldCover/v200",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "gee-plan"


def _month_end(year: int, month: int) -> str:
    if month == 12:
        return f"{year + 1}-01-01"
    return f"{year}-{month + 1:02d}-01"


def _extract_metric(text: str) -> tuple[str | None, str | None]:
    for metric, task_type in TASK_TYPES.items():
        if metric in text:
            normalized_metric = {
                "land surface temperature": "LST",
                "flood": "flood_extent",
                "land cover": "landcover",
                "landcover": "landcover",
            }.get(metric, metric.upper())
            return normalized_metric, task_type
    return None, None


def _extract_aoi(text: str) -> dict[str, Any] | None:
    if "hong kong" in text or "香港" in text:
        return {"type": "named_place", "name": "Hong Kong", "source": "named_place"}
    if "supplied aoi" in text or "provided aoi" in text or "user aoi" in text:
        return {"type": "user_supplied", "name": "supplied AOI", "source": "user_supplied"}
    if "geojson" in text:
        return {"type": "geojson", "name": "supplied GeoJSON", "source": "user_supplied_geojson"}
    asset_match = re.search(r"(users/[a-z0-9_./-]+|projects/[a-z0-9_./-]+)", text)
    if asset_match:
        return {"type": "ee_asset", "name": asset_match.group(1), "source": asset_match.group(1)}
    bbox_match = re.search(r"bbox\s*\[([^\]]+)\]", text)
    if bbox_match:
        return {"type": "bbox", "name": "bbox", "coordinates": bbox_match.group(1)}
    return None


def _extract_time_range(text: str) -> dict[str, Any] | None:
    year_match = re.search(r"\b(19[8-9]\d|20\d{2}|2100)\b", text)
    if not year_match:
        return None
    year = int(year_match.group(1))
    for name, month in MONTHS.items():
        if re.search(rf"\b{name}\b", text):
            return {
                "label": f"{date(year, month, 1):%B} {year}",
                "date_start": f"{year}-{month:02d}-01",
                "date_end": _month_end(year, month),
                "year": year,
                "month": month,
            }
    if "summer" in text:
        return {
            "label": f"summer {year}",
            "date_start": f"{year}-06-01",
            "date_end": f"{year}-09-01",
            "year": year,
            "season": "summer",
        }
    return {
        "label": str(year),
        "date_start": f"{year}-01-01",
        "date_end": f"{year + 1}-01-01",
        "year": year,
    }


def _extract_named_month_range(text: str, prefix: str) -> dict[str, Any] | None:
    match = re.search(rf"\b{prefix}\s+([a-z]+)\s+(19[8-9]\d|20\d{{2}}|2100)\b", text)
    if not match:
        return None
    month_name = match.group(1)
    month = MONTHS.get(month_name)
    if not month:
        return None
    year = int(match.group(2))
    return {
        "label": f"{prefix} {date(year, month, 1):%B} {year}",
        "date_start": f"{year}-{month:02d}-01",
        "date_end": _month_end(year, month),
        "year": year,
        "month": month,
    }


def _extract_flood_windows(text: str) -> dict[str, Any]:
    return {
        "before_time_range": _extract_named_month_range(text, "before"),
        "after_time_range": _extract_named_month_range(text, "after"),
    }


def _extract_output(text: str) -> dict[str, Any] | None:
    if "geotiff" in text or "geo tiff" in text or "tif" in text:
        return {"type": "geotiff", "destination": "drive", "format": "GeoTIFF"}
    if "csv" in text:
        return {"type": "csv", "destination": "drive", "format": "CSV"}
    if "table" in text:
        return {"type": "table", "destination": "drive", "format": "CSV"}
    if "preview" in text or "map" in text:
        return {"type": "preview", "destination": "local", "format": "HTML"}
    if "export" in text:
        return {"type": "unspecified_export", "destination": "drive", "format": None}
    return None


def _extract_grouping(text: str) -> dict[str, Any]:
    if "district" in text:
        return {"type": "zones", "label": "districts"}
    if "grid" in text:
        return {"type": "grid", "label": "grid"}
    if "land-cover" in text or "land cover" in text or "land use" in text or "class" in text:
        return {"type": "landcover_class", "label": "land-cover class"}
    return {"type": "whole_aoi", "label": "whole AOI"}


def _extract_dataset(text: str) -> str | None:
    upper_id = re.search(r"\b[A-Z0-9]+/[A-Z0-9_./-]+\b", text.upper())
    if upper_id:
        return upper_id.group(0)
    for alias, dataset_id in DATASET_ALIASES.items():
        if alias in text:
            return dataset_id
    return None


def _extract_temporal_cadence(text: str) -> str | None:
    if re.search(r"\b16\s*[- ]?d(?:ay)?s?\b", text) or "16天" in text:
        return "16-day"
    if "monthly" in text or "月度" in text:
        return "monthly"
    return None


def parse_request_slots(request: str) -> dict[str, Any]:
    text = _normalize(request)
    metric, task_type = _extract_metric(text)
    output = _extract_output(text)
    flood_windows = _extract_flood_windows(text)
    return {
        "raw_user_request": request,
        "metric": metric,
        "task_type": task_type,
        "aoi": _extract_aoi(text),
        "time_range": _extract_time_range(text),
        "before_time_range": flood_windows["before_time_range"],
        "after_time_range": flood_windows["after_time_range"],
        "output": output,
        "grouping": _extract_grouping(text),
        "requested_dataset": _extract_dataset(text),
        "temporal_cadence": _extract_temporal_cadence(text),
        "golden_route": route_request(request),
    }


def _missing_fields(slots: dict[str, Any]) -> list[str]:
    missing = []
    if not slots["metric"] or not slots["task_type"]:
        missing.append("metric_or_task_type")
    if not slots["aoi"]:
        missing.append("aoi")
    if slots["task_type"] == "flood_mapping":
        if not slots["before_time_range"]:
            missing.append("before_time_range")
        if not slots["after_time_range"]:
            missing.append("after_time_range")
    elif not slots["time_range"]:
        missing.append("time_range")
    if not slots["output"]:
        missing.append("output")
    return missing


def _unsupported_task_from_complete_context(slots: dict[str, Any], missing: list[str]) -> bool:
    return (
        missing == ["metric_or_task_type"]
        and bool(slots["aoi"])
        and bool(slots["time_range"])
        and bool(slots["output"])
    )


def build_general_plan_from_text(request: str) -> dict[str, Any]:
    slots = parse_request_slots(request)
    missing = _missing_fields(slots)
    if _unsupported_task_from_complete_context(slots, missing):
        return {
            "ok": False,
            "status": "unsupported",
            "error": error_payload("UNSUPPORTED_TASK", "No supported task type or metric was recognized."),
            "slots": slots,
            "closest_recipes": closest_recipes(request),
        }
    if missing:
        return {
            "ok": False,
            "status": "ambiguous",
            "error": error_payload(
                "AMBIGUOUS_TASK",
                f"Request is missing required fields: {', '.join(missing)}.",
            ),
            "missing_fields": missing,
            "slots": slots,
            "closest_recipes": closest_recipes(request),
        }

    metric = str(slots["metric"])
    task_type = str(slots["task_type"])
    output_type = slots["output"]["type"]
    recipe = default_recipe_for(task_type, metric=metric, output_type=output_type)
    if not recipe:
        return {
            "ok": False,
            "status": "unsupported",
            "error": error_payload("UNSUPPORTED_TASK", f"No recipe is registered for task type {task_type!r}."),
            "slots": slots,
            "closest_recipes": closest_recipes(request),
        }

    requested_dataset = slots["requested_dataset"]
    dataset_candidates = recommend_datasets(task_type=task_type, metric=metric)
    selected = [item for item in dataset_candidates if item["dataset_id"] == requested_dataset] if requested_dataset else dataset_candidates[:1]
    if not selected and requested_dataset:
        selected = [{"dataset_id": requested_dataset, "selection_reason": "user_requested_unverified"}]

    template, context, outputs = _execution_artifacts_for(slots, recipe, selected)
    golden_example = bool(slots["golden_route"].get("ok")) or _is_hk_2024_16day_ndvi(slots)
    plan_time_range = _planning_time_range(slots)
    plan_id = _slug(f"{task_type}-{metric}-{slots['aoi']['name']}-{plan_time_range['label']}")
    plan = {
        "schema_version": "gee-plan/v0.3",
        "plan_id": plan_id,
        "raw_user_request": request,
        "intent": {
            "metric": metric,
            "recipe_id": recipe["recipe_id"],
            "golden_example": golden_example,
        },
        "task_type": task_type,
        "aoi": slots["aoi"],
        "time_range": plan_time_range,
        "candidate_datasets": dataset_candidates,
        "selected_datasets": selected,
        "indices_or_variables": [metric],
        "operators": _operators_for(task_type, metric, output_type),
        "masking": _masking_for(task_type),
        "reducers": _reducers_for(slots["grouping"], output_type),
        "scale_crs_projection": {
            "scale_m": _default_scale(selected),
            "crs": "EPSG:4326",
            "notes": "Review scale and CRS before live export; dataset native projections may differ.",
        },
        "output": slots["output"],
        "export": {
            "requires_confirmation": True,
            "live_execution_default": False,
            "destination": slots["output"]["destination"],
            "format": slots["output"]["format"],
        },
        "preflight": {
            "profile": recipe["preflight_profile"],
            "checks": (
                "auth/project initialization",
                "AOI validity",
                "dataset coverage",
                "required bands",
                "mask overlap",
                "output existence",
            ),
        },
        "validation": {
            "rulesets": ["global_safety", recipe["validation_profile"]],
            "must_pass_before_live": True,
        },
        "limitations": _limitations_for(task_type, metric, output_type),
        "review_questions": _review_questions_for(slots, recipe),
        "execution": {
            "template": template,
            "template_ready": template is not None and context is not None,
            "context": context,
            "outputs": outputs,
            "temporal_cadence": slots["temporal_cadence"],
            "grouping": slots["grouping"],
            "notes": "This generic plan is editable and does not contact Earth Engine.",
        },
    }
    if task_type == "flood_mapping":
        plan["before_time_range"] = slots["before_time_range"]
        plan["after_time_range"] = slots["after_time_range"]
    return {"ok": True, "status": "planned", "slots": slots, "plan": plan, "recipe": recipe}


def _planning_time_range(slots: dict[str, Any]) -> dict[str, Any]:
    if slots["task_type"] == "flood_mapping":
        before = slots["before_time_range"]
        after = slots["after_time_range"]
        return {
            "label": f"{before['label']} to {after['label']}",
            "date_start": before["date_start"],
            "date_end": after["date_end"],
            "before": before,
            "after": after,
        }
    return slots["time_range"]


def _is_hk_2024_16day_ndvi(slots: dict[str, Any]) -> bool:
    return (
        slots.get("metric") == "NDVI"
        and slots.get("task_type") == "vegetation_index"
        and (slots.get("aoi") or {}).get("name") == "Hong Kong"
        and (slots.get("time_range") or {}).get("date_start") == "2024-01-01"
        and (slots.get("time_range") or {}).get("date_end") == "2025-01-01"
        and slots.get("temporal_cadence") == "16-day"
        and (slots.get("output") or {}).get("type") == "csv"
    )


def _execution_artifacts_for(
    slots: dict[str, Any],
    recipe: dict[str, Any],
    selected_datasets: list[dict[str, Any]],
) -> tuple[str | None, dict[str, Any] | None, dict[str, str]]:
    if _is_hk_2024_16day_ndvi(slots):
        dataset_id = selected_datasets[0]["dataset_id"] if selected_datasets else "COPERNICUS/S2_SR_HARMONIZED"
        context = {
            "script_name": "hk_2024_16day_ndvi_csv",
            "year": 2024,
            "date_start": "2024-01-01",
            "date_end": "2025-01-01",
            "aoi_name": "Hong Kong",
            "aoi_source": "Home Affairs Department Hong Kong administrative district boundary GeoJSON",
            "boundary_geojson": "references/boundaries/hk_18_districts.geojson",
            "dataset_id": dataset_id,
            "scale": 10,
            "crs": "EPSG:4326",
            "tile_scale": 4,
            "cloudy_pixel_percentage": 80,
            "max_pixels": 10000000000000,
            "temporal_cadence_days": 16,
            "preflight_months": [1, 7],
            "export_description": "hk_2024_16day_ndvi",
            "drive_folder": "gee_exports",
            "file_prefix": "hk_2024_16day_ndvi",
        }
        return (
            "hk_2024_16day_ndvi_csv",
            context,
            {
                "script": "outputs/scripts/hk_2024_16day_ndvi_csv.py",
                "plan": "outputs/plans/hk_2024_16day_ndvi.yaml",
            },
        )
    return recipe["template"], None, {}


def _operators_for(task_type: str, metric: str, output_type: str) -> list[str]:
    operators = ["filterDate", "filterBounds", "map", "mask", "reduceRegion"]
    if metric in {"NDVI", "NDWI", "MNDWI", "NDBI"}:
        operators.append("normalizedDifference")
    elif metric == "EVI":
        operators.append("expression")
    if output_type == "geotiff":
        operators.append("Export.image.toDrive")
    else:
        operators.append("Export.table.toDrive")
    if task_type == "flood_mapping":
        return ["filterDate", "filterBounds", "filterMetadata", "median", "divide_or_subtract", "Export.image.toDrive"]
    return operators


def _masking_for(task_type: str) -> dict[str, Any]:
    if task_type in {"vegetation_index", "water_index", "builtup_index", "land_surface_temperature"}:
        return {
            "required": True,
            "policy": "Use dataset-specific cloud/QA masks before compositing or reducing.",
        }
    if task_type == "flood_mapping":
        return {"required": False, "policy": "Use SAR-specific filtering; optical cloud masks do not apply."}
    return {"required": True, "policy": "Use dataset-specific quality masks when available."}


def _reducers_for(grouping: dict[str, Any], output_type: str) -> list[str]:
    if output_type == "geotiff":
        return []
    if grouping["type"] == "whole_aoi":
        return ["ee.Reducer.mean"]
    return ["ee.Reducer.mean", "reduceRegions"]


def _default_scale(selected_datasets: list[dict[str, Any]]) -> int:
    if not selected_datasets:
        return 30
    dataset_id = selected_datasets[0].get("dataset_id", "")
    if "S2" in dataset_id or "DYNAMICWORLD" in dataset_id:
        return 10
    if "S1_GRD" in dataset_id:
        return 10
    return 30


def _limitations_for(task_type: str, metric: str, output_type: str) -> list[str]:
    limitations = [
        "Generated plans are engineering artifacts and require user review before live export.",
        "Live Earth Engine execution requires local authentication and an explicit project.",
    ]
    if task_type in {"vegetation_index", "water_index", "builtup_index"}:
        limitations.append("Optical indices are sensitive to clouds, shadows, seasonality, and mixed pixels.")
    if output_type == "geotiff":
        limitations.append("Image exports can be quota-sensitive; review region, scale, CRS, and maxPixels.")
    if metric == "flood_extent":
        limitations.append("Flood maps require threshold calibration and domain review.")
    return limitations


def _review_questions_for(slots: dict[str, Any], recipe: dict[str, Any]) -> list[str]:
    questions = [f"Is {slots['aoi']['name']} the intended AOI?"]
    if slots["task_type"] == "flood_mapping":
        questions.append(
            f"Are {slots['before_time_range']['label']} and {slots['after_time_range']['label']} the intended before/after windows?"
        )
    else:
        questions.append(f"Is {slots['time_range']['label']} the intended time window?")
    questions.append(f"Is {recipe['recipe_id']} the intended recipe?")
    if slots["temporal_cadence"]:
        questions.append(f"Should output be aggregated at {slots['temporal_cadence']} cadence?")
    if slots["output"]["type"] == "unspecified_export":
        questions.append("Should export be CSV/table or GeoTIFF/image?")
    return questions
