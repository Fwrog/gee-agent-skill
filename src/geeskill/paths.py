from __future__ import annotations

from pathlib import Path


def project_root(start: Path | None = None) -> Path:
    """Find the repository or skill root from a starting path."""
    starts = [(start or Path.cwd()).resolve(), Path(__file__).resolve()]
    for current in starts:
        candidates = [current, *current.parents]
        for candidate in candidates:
            if (candidate / "SKILL.md").exists() and (candidate / "references").exists():
                return candidate
    return Path.cwd().resolve()


def default_docs_dir(root: Path | None = None) -> Path:
    return (root or project_root()) / "references" / "knowledge_base"


def package_resources_dir() -> Path:
    return Path(__file__).resolve().parent / "resources"


def default_index_path(root: Path | None = None) -> Path:
    source_path = (root or project_root()) / "references" / "index" / "gee_docs_index.json"
    if source_path.exists():
        return source_path
    return package_resources_dir() / "index" / "gee_docs_index.json"


def default_templates_dir(root: Path | None = None) -> Path:
    source_path = (root or project_root()) / "assets" / "templates"
    if source_path.exists():
        return source_path
    return package_resources_dir() / "templates"


def default_context_path(name: str) -> Path:
    source_path = project_root() / "evals" / "contexts" / name
    if source_path.exists():
        return source_path
    return package_resources_dir() / "contexts" / name


def default_task_path(name: str) -> Path:
    source_path = project_root() / "examples" / name / "task.yaml"
    if source_path.exists():
        return source_path
    filename = f"{name}.yaml"
    return package_resources_dir() / "tasks" / filename
