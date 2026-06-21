from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    installed: bool
    exposed: bool
    dangerous: bool
    requires_explicit_flags: tuple[str, ...]
    description: str


TOOLS: dict[str, ToolSpec] = {
    "search_docs": ToolSpec(
        "search_docs", True, True, False, (), "Search the local operator-aware docs index."
    ),
    "plan_workflow": ToolSpec(
        "plan_workflow", True, True, False, (), "Create a cited plan and run trace from a task."
    ),
    "review_plan": ToolSpec(
        "review_plan", True, True, False, (), "Review a saved task plan without Earth Engine contact."
    ),
    "preflight_plan": ToolSpec(
        "preflight_plan",
        True,
        True,
        False,
        ("--project",),
        "Run safe live probes for a saved task plan before export.",
    ),
    "ask": ToolSpec(
        "ask",
        True,
        True,
        False,
        (),
        "Deterministically route a supported natural-language task through RAG, planning, validation, preflight, and run trace.",
    ),
    "render_template": ToolSpec(
        "render_template", True, False, False, (), "Render approved Jinja2 workflow templates."
    ),
    "validate_script": ToolSpec(
        "validate_script", True, True, False, (), "Run static and semantic validation."
    ),
    "preflight_hk_ndvi": ToolSpec(
        "preflight_hk_ndvi",
        True,
        True,
        False,
        ("--project",),
        "Run safe live probes for the Hong Kong Sentinel-2 NDVI workflow before export.",
    ),
    "run_dry": ToolSpec(
        "run_dry", True, True, False, ("--dry-run",), "Validate and record a dry run."
    ),
    "run_live": ToolSpec(
        "run_live",
        True,
        True,
        True,
        ("--project", "--confirm-live"),
        "Execute a validated script through the Earth Engine Python API.",
    ),
    "run_plan_live": ToolSpec(
        "run_plan_live",
        True,
        True,
        True,
        ("--project", "--confirm-live"),
        "Render, validate, preflight, and execute a saved task plan.",
    ),
    "monitor_exports": ToolSpec(
        "monitor_exports",
        True,
        True,
        True,
        ("--project",),
        "Inspect Earth Engine batch export task states.",
    ),
    "write_run_trace": ToolSpec(
        "write_run_trace", True, False, False, (), "Persist reproducibility artifacts."
    ),
}


def installed_tools() -> list[dict]:
    return [spec.__dict__ for spec in TOOLS.values() if spec.installed]


def exposed_tools() -> list[dict]:
    return [spec.__dict__ for spec in TOOLS.values() if spec.exposed]


def require_flags(tool_name: str, provided: set[str]) -> None:
    spec = TOOLS[tool_name]
    missing = [flag for flag in spec.requires_explicit_flags if flag not in provided]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{tool_name} requires {joined}")
