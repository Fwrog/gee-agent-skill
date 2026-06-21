from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def build_task_plan(task: dict[str, Any]) -> dict[str, Any]:
    context = dict(task.get("context") or {})
    intent = task.get("intent") or task.get("id") or "unknown"
    version = task.get("version") or "v0"
    plan = {
        "task_id": task.get("id", intent),
        "version": version,
        "raw_user_request": task.get("query") or task.get("task"),
        "interpreted_intent": {
            "name": intent,
            "description": task.get("task"),
            "template": task.get("template"),
        },
        "aoi": {
            "name": context.get("aoi_name") or "Hong Kong",
            "source": context.get("aoi_source") or context.get("boundary_geojson"),
            "boundary_geojson": context.get("boundary_geojson"),
            "role": "Administrative boundary defines where statistics are computed.",
        },
        "time_range": {
            "year": context.get("year"),
            "month": context.get("month") or context.get("smoke_month"),
            "date_start": context.get("date_start"),
            "date_end": context.get("date_end"),
        },
        "datasets": _plan_datasets(context),
        "masking_strategy": _masking_strategy(task, context),
        "landcover_strategy": _landcover_strategy(task, context),
        "output_schema": list(task.get("output_schema") or context.get("output_schema") or []),
        "preflight_checks": _preflight_checks(task),
        "live_execution_required": False,
        "requires_confirmation": True,
        "limitations": list(task.get("limitations") or _default_limitations(version)),
        "review_questions": list(task.get("review_questions") or _default_review_questions(version)),
        "execution": {
            "task": task.get("task"),
            "query": task.get("query"),
            "template": task.get("template"),
            "context": context,
            "outputs": task.get("outputs") or {},
        },
    }
    if not plan["output_schema"]:
        plan["output_schema"] = _default_output_schema(version)
    return plan


def _plan_datasets(context: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        {
            "id": context.get("dataset_id", "COPERNICUS/S2_SR_HARMONIZED"),
            "role": "Primary optical surface reflectance source for NDVI.",
            "selected": True,
        }
    ]
    if context.get("landcover_dataset_id"):
        candidates.append(
            {
                "id": context["landcover_dataset_id"],
                "role": "Primary time-matched land-cover probabilities and labels.",
                "selected": True,
            }
        )
    if context.get("worldcover_dataset_id"):
        candidates.append(
            {
                "id": context["worldcover_dataset_id"],
                "role": "Optional static land-cover sanity-check reference.",
                "selected": False,
            }
        )
    return {
        "candidate": candidates,
        "selected": [item for item in candidates if item["selected"]],
    }


def _masking_strategy(task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "sentinel2_cloud_policy": (
            "Filter by CLOUDY_PIXEL_PERCENTAGE and mask invalid SCL classes before NDVI compositing."
        ),
        "cloudy_pixel_percentage": context.get("cloudy_pixel_percentage", 80),
        "scale_m": context.get("scale", 10),
        "crs": context.get("crs", "EPSG:4326"),
        "pixel_interpretation": (
            "All-surface statistics include water, built-up, bare, and vegetated pixels; "
            "land-cover masks are used only for strata and interpretation."
        ),
    }


def _landcover_strategy(task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if "landcover_dataset_id" not in context:
        return {
            "enabled": False,
            "note": "No land-cover stratification requested for this task.",
        }
    return {
        "enabled": True,
        "primary_dataset": context.get("landcover_dataset_id"),
        "primary_role": "Time-matched class probabilities and label mode for January 2024.",
        "probability_threshold": context.get("dynamic_world_probability_threshold", 0.35),
        "class_groups": {
            "non_water": ["trees", "grass", "flooded_vegetation", "crops", "shrub_and_scrub", "built", "bare"],
            "vegetation": ["trees", "grass", "flooded_vegetation", "crops", "shrub_and_scrub"],
            "built": ["built"],
            "bare": ["bare"],
            "water": ["water"],
        },
        "optional_static_reference": context.get("worldcover_dataset_id"),
        "boundary_rule": "Land-cover data is not used as an administrative boundary.",
    }


def _preflight_checks(task: dict[str, Any]) -> list[str]:
    checks = [
        "Earth Engine initialization succeeds for the supplied project.",
        "AOI feature collection is non-empty and has positive area.",
        "Sentinel-2 collection has images before and after cloud metadata filtering.",
        "NDVI band exists after B8/B4 normalized difference mapping.",
        "A small all-surface NDVI sanity statistic is non-null.",
    ]
    if (task.get("version") or "").lower() == "v0.2":
        checks.extend(
            [
                "Dynamic World collection has images for the same AOI and month.",
                "Dynamic World label band exists.",
                "Dynamic World probability bands exist.",
                "Water, built, vegetation, trees, and grass class fractions can be estimated.",
                "Non-water and vegetation NDVI probes are non-null when masks have enough pixels.",
            ]
        )
    return checks


def _default_output_schema(version: str) -> list[str]:
    if version == "v0.2":
        return [
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
    return [
        "aoi_name",
        "year",
        "month",
        "date_start",
        "date_end",
        "mean_ndvi",
        "image_count_before_cloud_filter",
        "image_count_after_cloud_filter",
        "dataset_id",
        "scale_m",
        "crs",
        "aoi_source",
        "export_description",
    ]


def _default_limitations(version: str) -> list[str]:
    if version == "v0.2":
        return [
            "Dynamic World is probabilistic; low-confidence or sparse classes may produce null NDVI values.",
            "Class masks support diagnostics and interpretation but do not replace administrative boundaries.",
            "January NDVI is seasonal and should not be interpreted as annual vegetation condition.",
            "All-surface NDVI can be low when water, built-up, and bare surfaces are included.",
        ]
    return [
        "All-surface NDVI includes water, built-up, bare, and vegetated pixels.",
        "This is an engineering smoke workflow, not a scientific conclusion by itself.",
    ]


def _default_review_questions(version: str) -> list[str]:
    if version == "v0.2":
        return [
            "Is Dynamic World the intended primary land-cover source for this analysis?",
            "Is the probability threshold acceptable for class masks?",
            "Should sparse classes be exported as null with warnings rather than forcing values?",
            "Is whole-Hong-Kong AOI appropriate, or should a district/user AOI be supplied?",
        ]
    return [
        "Is whole-Hong-Kong all-surface NDVI the intended metric?",
        "Should a land-only or vegetation-only diagnostic be used instead?",
    ]


def write_task_plan(path: Path, plan: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def load_task_plan(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Task plan must contain a mapping: {path}")
    for key in ("task_id", "interpreted_intent", "execution"):
        if key not in data:
            raise ValueError(f"Task plan missing required field {key!r}: {path}")
    return data


def plan_review_text(plan: dict[str, Any]) -> str:
    lines = [
        f"Task plan: {plan.get('task_id')}",
        f"Intent: {plan.get('interpreted_intent', {}).get('name')}",
        f"AOI: {plan.get('aoi', {}).get('name')} ({plan.get('aoi', {}).get('source')})",
        "Time range: "
        f"{plan.get('time_range', {}).get('date_start')} to {plan.get('time_range', {}).get('date_end')}",
        "Selected datasets:",
    ]
    for item in plan.get("datasets", {}).get("selected", []):
        lines.append(f"- {item.get('id')}: {item.get('role')}")
    lines.append("Output fields:")
    for field in plan.get("output_schema", []):
        lines.append(f"- {field}")
    lines.append("Review questions:")
    for question in plan.get("review_questions", []):
        lines.append(f"- {question}")
    lines.append("Live execution requires explicit confirmation.")
    return "\n".join(lines)
