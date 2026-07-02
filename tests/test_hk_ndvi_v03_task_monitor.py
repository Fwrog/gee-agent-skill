from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MONITOR_SCRIPT = ROOT / "scripts" / "hk_ndvi_v03_monitor_tasks.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("hk_ndvi_v03_monitor_tasks", MONITOR_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeData:
    def __init__(self, statuses: dict[str, str]) -> None:
        self.statuses = statuses

    def getTaskStatus(self, task_id: str):
        return [
            {
                "id": task_id,
                "state": self.statuses[task_id],
                "error_message": None,
                "creation_timestamp_ms": 1,
                "update_timestamp_ms": 2,
            }
        ]


class FakeEE:
    def __init__(self, statuses: dict[str, str]) -> None:
        self.data = FakeData(statuses)
        self.initialized_project = None

    def Initialize(self, project=None) -> None:  # noqa: N802 - mirrors Earth Engine API.
        self.initialized_project = project


def test_monitor_loads_task_ids_from_manifest(tmp_path: Path) -> None:
    module = _load_module()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "earth_engine_tasks": [
                    {"description": "task_a", "task_id": "A", "artifact_type": "csv"},
                    {"description": "task_b", "task_id": "B", "artifact_type": "geotiff"},
                ]
            }
        ),
        encoding="utf-8",
    )
    tasks = module._load_tasks(manifest)
    assert {"description": "task_a", "task_id": "A", "artifact_type": "csv", "scale_m": None, "crs": "unknown"} in tasks
    assert {"description": "task_b", "task_id": "B", "artifact_type": "geotiff", "scale_m": None, "crs": "unknown"} in tasks
    assert any(task["task_id"] == "N6W3SDLSY5WFVL4IS3O7KRKR" for task in tasks)


def test_monitor_loads_default_sub_manifests(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    out = tmp_path / "outputs"
    primary = out / "manifest.json"
    primary.parent.mkdir(parents=True)
    primary.write_text(json.dumps({"tasks": [{"description": "primary", "id": "A"}]}), encoding="utf-8")
    sub = out / "tiles" / "manifest.json"
    sub.parent.mkdir(parents=True)
    sub.write_text(json.dumps({"tasks": [{"description": "tile", "id": "B"}]}), encoding="utf-8")
    monkeypatch.setattr(module, "DEFAULT_OUT", out)
    monkeypatch.setattr(module, "DEFAULT_MANIFEST", primary)
    tasks = module._load_tasks(primary)
    assert any(task["task_id"] == "A" for task in tasks)
    assert any(task["task_id"] == "B" for task in tasks)


def test_monitor_writes_status_snapshot_with_pending_summary(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "earth_engine_tasks": [
                    {"description": "task_a", "task_id": "A", "artifact_type": "csv"},
                    {"description": "task_b", "task_id": "B", "artifact_type": "geotiff"},
                    {"description": "task_c", "task_id": "C", "artifact_type": "geotiff"},
                ]
            }
        ),
        encoding="utf-8",
    )
    fallback_statuses = {task["task_id"]: "COMPLETED" for task in module.FALLBACK_TASKS}
    fake = FakeEE(fallback_statuses | {"A": "COMPLETED", "B": "RUNNING", "C": "FAILED"})
    monkeypatch.setattr(module, "_import_ee", lambda: fake)
    payload = module.monitor(manifest, tmp_path, project="demo-project")
    assert fake.initialized_project == "demo-project"
    assert payload["summary"]["states"]["RUNNING"] == 1
    assert payload["summary"]["states"]["FAILED"] == 1
    assert payload["summary"]["states"]["COMPLETED"] >= 1
    assert payload["summary"]["pending_count"] == 1
    assert payload["summary"]["failed_count"] == 1
    assert payload["summary"]["all_terminal"] is False
    latest = tmp_path / "task_status_latest.json"
    assert latest.exists()
    latest_payload = json.loads(latest.read_text(encoding="utf-8"))
    assert latest_payload["claim_boundary"].startswith("Task completion evidence only")
    assert latest_payload["tasks"][0]["drive_folder"] == "GEE_SKILL_V03_HK_NDVI_VALIDATION"
    assert "MODIS/061/MOD13Q1" in latest_payload["tasks"][0]["source_assets"]
