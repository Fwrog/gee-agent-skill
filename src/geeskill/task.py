from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_task(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Task file must contain a mapping: {path}")
    if "task" not in data:
        raise ValueError(f"Task file missing required field `task`: {path}")
    return data


def task_to_context(task: dict[str, Any]) -> dict[str, Any]:
    context = dict(task.get("context") or {})
    for key in (
        "script_name",
        "year",
        "dataset_id",
        "admin_collection",
        "admin0_name",
        "admin0_property",
        "district_property",
        "scale",
        "crs",
        "tile_scale",
        "cloudy_pixel_percentage",
        "export_description",
        "drive_folder",
        "file_prefix",
        "max_pixels",
        "month",
        "date_start",
        "date_end",
        "aoi_name",
        "aoi_source",
        "boundary_geojson",
        "smoke_month",
        "smoke_region",
        "temporal_cadence_days",
        "preflight_months",
    ):
        if key in task and key not in context:
            context[key] = task[key]
    return context
