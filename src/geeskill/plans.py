from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

V03_PLAN_REQUIRED_FIELDS = (
    "schema_version",
    "plan_id",
    "raw_user_request",
    "intent",
    "task_type",
    "aoi",
    "time_range",
    "candidate_datasets",
    "selected_datasets",
    "indices_or_variables",
    "operators",
    "masking",
    "reducers",
    "scale_crs_projection",
    "output",
    "export",
    "preflight",
    "validation",
    "limitations",
    "review_questions",
    "execution",
)

V03_SUPPORTED_TASK_TYPES = {
    "vegetation_index",
    "water_index",
    "builtup_index",
    "land_surface_temperature",
    "landcover_summary",
    "landcover_stratified_statistics",
    "zonal_statistics",
    "change_detection",
    "flood_mapping",
    "export_image",
    "export_table",
}

V03_ALLOWED_ROOT_FIELDS = set(V03_PLAN_REQUIRED_FIELDS) | {"output_schema", "before_time_range", "after_time_range"}

V03_SUPPORTED_PREFLIGHT_PROFILES = {
    "optical_index",
    "landcover_stratified",
    "landsat_lst",
    "sentinel1_change",
    "zonal_statistics",
    "export_image",
    "export_table",
}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_object(plan: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = plan.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {}
    return value


def _require_list(plan: dict[str, Any], field: str, errors: list[str], *, min_items: int = 0) -> list[Any]:
    value = plan.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    if len(value) < min_items:
        errors.append(f"{field} must contain at least {min_items} item(s)")
    return value


def _require_keys(mapping: dict[str, Any], field: str, keys: tuple[str, ...], errors: list[str]) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        errors.append(f"{field} missing required keys: {', '.join(missing)}")


def validate_v03_plan_schema(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != "gee-plan/v0.3":
        errors.append("schema_version must be gee-plan/v0.3")
    missing = [field for field in V03_PLAN_REQUIRED_FIELDS if field not in plan]
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    task_type = plan.get("task_type")
    if task_type and task_type not in V03_SUPPORTED_TASK_TYPES:
        errors.append(f"unsupported task_type: {task_type}")
    extra = sorted(set(plan) - V03_ALLOWED_ROOT_FIELDS)
    if extra:
        errors.append(f"unsupported root fields: {', '.join(extra)}")

    intent = _require_object(plan, "intent", errors)
    if intent:
        _require_keys(intent, "intent", ("metric", "recipe_id", "golden_example"), errors)
        if "metric" in intent and not _is_nonempty_string(intent["metric"]):
            errors.append("intent.metric must be a non-empty string")
        if "recipe_id" in intent and not _is_nonempty_string(intent["recipe_id"]):
            errors.append("intent.recipe_id must be a non-empty string")
        if "golden_example" in intent and not isinstance(intent["golden_example"], bool):
            errors.append("intent.golden_example must be a boolean")

    aoi = _require_object(plan, "aoi", errors)
    if aoi:
        _require_keys(aoi, "aoi", ("type", "name", "source"), errors)
        for key in ("type", "name", "source"):
            if key in aoi and not _is_nonempty_string(aoi[key]):
                errors.append(f"aoi.{key} must be a non-empty string")

    time_range = _require_object(plan, "time_range", errors)
    if time_range:
        _require_keys(time_range, "time_range", ("label", "date_start", "date_end"), errors)
        for key in ("label", "date_start", "date_end"):
            if key in time_range and not _is_nonempty_string(time_range[key]):
                errors.append(f"time_range.{key} must be a non-empty string")

    candidate = _require_list(plan, "candidate_datasets", errors)
    selected = _require_list(plan, "selected_datasets", errors, min_items=1)
    for field, values in (("candidate_datasets", candidate), ("selected_datasets", selected)):
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                errors.append(f"{field}[{index}] must be an object")
                continue
            if not _is_nonempty_string(item.get("dataset_id")):
                errors.append(f"{field}[{index}].dataset_id must be a non-empty string")

    for field in ("indices_or_variables", "operators"):
        values = _require_list(plan, field, errors, min_items=1)
        for index, item in enumerate(values):
            if not _is_nonempty_string(item):
                errors.append(f"{field}[{index}] must be a non-empty string")

    masking = _require_object(plan, "masking", errors)
    if masking:
        _require_keys(masking, "masking", ("required", "policy"), errors)
        if "required" in masking and not isinstance(masking["required"], bool):
            errors.append("masking.required must be a boolean")
        if "policy" in masking and not _is_nonempty_string(masking["policy"]):
            errors.append("masking.policy must be a non-empty string")

    _require_list(plan, "reducers", errors)

    scale_crs = _require_object(plan, "scale_crs_projection", errors)
    if scale_crs:
        _require_keys(scale_crs, "scale_crs_projection", ("scale_m", "crs", "notes"), errors)
        if "scale_m" in scale_crs and not isinstance(scale_crs["scale_m"], (int, float)):
            errors.append("scale_crs_projection.scale_m must be numeric")
        elif "scale_m" in scale_crs and float(scale_crs["scale_m"]) <= 0:
            errors.append("scale_crs_projection.scale_m must be greater than zero")
        if "crs" in scale_crs and not _is_nonempty_string(scale_crs["crs"]):
            errors.append("scale_crs_projection.crs must be a non-empty string")

    output = _require_object(plan, "output", errors)
    if output:
        _require_keys(output, "output", ("type", "destination"), errors)
        for key in ("type", "destination"):
            if key in output and not _is_nonempty_string(output[key]):
                errors.append(f"output.{key} must be a non-empty string")

    export = _require_object(plan, "export", errors)
    if export:
        _require_keys(export, "export", ("requires_confirmation", "live_execution_default", "destination", "format"), errors)
        for key in ("requires_confirmation", "live_execution_default"):
            if key in export and not isinstance(export[key], bool):
                errors.append(f"export.{key} must be a boolean")
        if "destination" in export and not _is_nonempty_string(export["destination"]):
            errors.append("export.destination must be a non-empty string")

    preflight = _require_object(plan, "preflight", errors)
    if preflight:
        _require_keys(preflight, "preflight", ("profile", "checks"), errors)
        profile = preflight.get("profile")
        if not _is_nonempty_string(profile):
            errors.append("preflight.profile must be a non-empty string")
        elif profile not in V03_SUPPORTED_PREFLIGHT_PROFILES:
            errors.append(f"unsupported preflight.profile: {profile}")
        checks = preflight.get("checks")
        if not isinstance(checks, (list, tuple)) or not checks:
            errors.append("preflight.checks must be a non-empty list")

    validation = _require_object(plan, "validation", errors)
    if validation:
        _require_keys(validation, "validation", ("rulesets", "must_pass_before_live"), errors)
        rulesets = validation.get("rulesets")
        if not isinstance(rulesets, list) or not rulesets:
            errors.append("validation.rulesets must be a non-empty list")
        if "must_pass_before_live" in validation and not isinstance(validation["must_pass_before_live"], bool):
            errors.append("validation.must_pass_before_live must be a boolean")

    _require_list(plan, "limitations", errors)
    _require_list(plan, "review_questions", errors)

    execution = _require_object(plan, "execution", errors)
    if execution:
        _require_keys(execution, "execution", ("template", "template_ready", "context", "outputs", "live_adapter_ready", "context_review_required"), errors)
        if "template_ready" in execution and not isinstance(execution["template_ready"], bool):
            errors.append("execution.template_ready must be a boolean")
        if "live_adapter_ready" in execution and not isinstance(execution["live_adapter_ready"], bool):
            errors.append("execution.live_adapter_ready must be a boolean")
        if "context_review_required" in execution and not isinstance(execution["context_review_required"], bool):
            errors.append("execution.context_review_required must be a boolean")
        if execution.get("template_ready"):
            if not _is_nonempty_string(execution.get("template")):
                errors.append("execution.template must be a non-empty string when template_ready is true")
            if not isinstance(execution.get("context"), dict):
                errors.append("execution.context must be an object when template_ready is true")
            outputs = execution.get("outputs")
            if not isinstance(outputs, dict) or not _is_nonempty_string(outputs.get("script")):
                errors.append("execution.outputs.script must be set when template_ready is true")
    return errors


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
