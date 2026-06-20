from __future__ import annotations

import runpy
import time
from pathlib import Path
from typing import Any


class EarthEngineUnavailable(RuntimeError):
    """Raised when live Earth Engine access cannot be initialized."""


def _import_ee():
    try:
        import ee  # type: ignore
    except ImportError as exc:
        raise EarthEngineUnavailable(
            "earthengine-api is not installed. Install live dependencies with "
            '`pip install -e ".[earthengine]"` or `pip install earthengine-api`.'
        ) from exc
    return ee


def initialize(project: str | None, authenticate: bool = False):
    ee = _import_ee()
    try:
        if authenticate:
            ee.Authenticate()
        kwargs = {"project": project} if project else {}
        ee.Initialize(**kwargs)
    except Exception as exc:  # pragma: no cover - depends on local credentials
        hint = (
            "Earth Engine initialization failed. Register for Earth Engine, enable the API "
            "on a Google Cloud Project, authenticate locally, and pass --project if needed."
        )
        raise EarthEngineUnavailable(f"{hint} Original error: {exc}") from exc
    return ee


def execute_script(script_path: Path, project: str | None, authenticate: bool = False) -> dict[str, Any]:
    initialize(project=project, authenticate=authenticate)
    namespace = runpy.run_path(str(script_path), run_name="__main__")
    return {"script": str(script_path), "namespace_keys": sorted(namespace.keys())}


def render_map_preview(
    script_path: Path,
    object_name: str,
    out_html: Path,
    project: str | None,
    authenticate: bool = False,
) -> Path:
    initialize(project=project, authenticate=authenticate)
    try:
        import geemap  # type: ignore
    except ImportError as exc:
        raise EarthEngineUnavailable(
            "geemap is not installed. Install live map dependencies with "
            '`pip install -e ".[earthengine]"` or `pip install geemap`.'
        ) from exc
    namespace = runpy.run_path(str(script_path), run_name="__gee_skill_map_preview__")
    if object_name not in namespace:
        raise EarthEngineUnavailable(
            f"Map object {object_name!r} was not found in {script_path}. "
            "Pass --map-object with a function or object defined by the script."
        )
    obj = namespace[object_name]
    layer = obj() if callable(obj) else obj
    out_html.parent.mkdir(parents=True, exist_ok=True)
    gee_map = geemap.Map()
    gee_map.addLayer(layer, {}, object_name)
    gee_map.to_html(filename=str(out_html))
    return out_html


def list_tasks(project: str | None, authenticate: bool = False) -> list[dict[str, Any]]:
    ee = initialize(project=project, authenticate=authenticate)
    tasks = ee.batch.Task.list()
    summaries: list[dict[str, Any]] = []
    for task in tasks:
        try:
            status = task.status()
        except Exception as exc:  # pragma: no cover - network dependent
            status = {"state": "UNKNOWN", "error_message": str(exc)}
        summaries.append(status)
    return summaries


def monitor_tasks(
    project: str | None,
    authenticate: bool = False,
    timeout_seconds: int = 0,
    poll_seconds: int = 15,
) -> list[dict[str, Any]]:
    deadline = time.time() + timeout_seconds if timeout_seconds else time.time()
    last: list[dict[str, Any]] = []
    while True:
        last = list_tasks(project=project, authenticate=authenticate)
        active = [task for task in last if task.get("state") in {"READY", "RUNNING"}]
        if not active or not timeout_seconds or time.time() >= deadline:
            return last
        time.sleep(max(poll_seconds, 1))
