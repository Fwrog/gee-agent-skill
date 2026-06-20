from __future__ import annotations

import json
import platform
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .paths import project_root


def new_run_id(prefix: str = "run") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}-{stamp}"


@dataclass
class RunTrace:
    run_id: str
    run_dir: Path

    @classmethod
    def create(cls, run_id: str | None = None, root: Path | None = None) -> "RunTrace":
        rid = run_id or new_run_id()
        run_dir = (root or project_root()) / "outputs" / "runs" / rid
        run_dir.mkdir(parents=True, exist_ok=True)
        trace = cls(rid, run_dir)
        trace.write_environment()
        return trace

    def path(self, name: str) -> Path:
        return self.run_dir / name

    def write_json(self, name: str, payload: Any) -> Path:
        path = self.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def write_text(self, name: str, text: str) -> Path:
        path = self.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_yaml(self, name: str, payload: Any) -> Path:
        path = self.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return path

    def copy_file(self, source: Path, name: str) -> Path:
        target = self.path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        return target

    def write_environment(self) -> Path:
        return self.write_json(
            "environment.json",
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "python": sys.version,
                "platform": platform.platform(),
                "geeskill_version": __version__,
                "cwd": str(Path.cwd()),
            },
        )

    def write_final_report(self, title: str, sections: dict[str, Any]) -> Path:
        lines = [f"# {title}", "", f"Run id: `{self.run_id}`", ""]
        for heading, value in sections.items():
            lines.extend([f"## {heading}", ""])
            if isinstance(value, str):
                lines.append(value)
            else:
                lines.append("```json")
                lines.append(json.dumps(value, indent=2, ensure_ascii=False))
                lines.append("```")
            lines.append("")
        return self.write_text("final_report.md", "\n".join(lines))


def dry_run_report(script: Path, validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "dry_run": True,
        "script": str(script),
        "validation_ok": bool(validation.get("ok")),
        "contacted_earth_engine": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
