from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .ask import route_request
from .catalog import get_dataset, list_datasets, list_knowledge_cards, normalize_knowledge_category, recommend_datasets, search_datasets
from .earthengine import EarthEngineUnavailable, execute_script, monitor_tasks, render_map_preview
from .errors import classify_exception, error_payload
from .evaluation import run_benchmark_suite
from .generic_preflight import GenericV03PreflightConfig, run_generic_v03_preflight
from .hk_ndvi_preflight import HKNDVIPreflightConfig, run_hk_ndvi_preflight
from .intents import build_general_plan_from_text, parse_request_slots
from .paths import (
    default_boundary_path,
    default_context_path,
    default_index_path,
    default_task_path,
    default_templates_dir,
    project_root,
)
from .plans import build_task_plan, load_task_plan, plan_review_text, validate_v03_plan_schema, write_task_plan
from .planner import build_plan
from .rag import load_index, results_to_dicts, search
from .recipes import get_recipe, list_recipes
from .retrieval_trace import build_retrieval_trace
from .rules import get_ruleset, list_rulesets
from .run_trace import RunTrace, dry_run_report
from .task import load_task, task_to_context
from .templates import TemplateContextError, load_context, render_template
from .tool_registry import exposed_tools, installed_tools, require_flags
from .validation import validate_script


def _print_error(
    message: str,
    *,
    as_json: bool = False,
    code: str = "USAGE_ERROR",
    hint: str = "Review the command arguments and rerun with the required values.",
    command: str | None = None,
) -> int:
    if as_json:
        payload = _envelope_error(code, message, hint)
        if command:
            payload["command"] = command
            payload["schema_version"] = "gee-cli/v0.3"
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 2
    print(f"error: {message}", file=sys.stderr)
    return 2


def _envelope_ok(data: dict | list | str | int | bool | None) -> dict:
    return {"ok": True, "data": data}


def _envelope_error(code: str, message: str, hint: str) -> dict:
    return {"ok": False, "error": {"code": code, "message": message, "hint": hint}}


def _command_envelope(command: str, data: Any, schema_version: str = "gee-cli/v0.3") -> dict:
    return {"ok": True, "command": command, "schema_version": schema_version, "data": data}


def _with_data(payload: dict[str, Any], data: dict[str, Any] | None = None) -> dict[str, Any]:
    if "data" not in payload:
        payload["data"] = data if data is not None else {key: value for key, value in payload.items() if key not in {"ok", "error"}}
    return payload


def _print_envelope(payload: dict, *, as_json: bool = True) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False) if as_json else payload)
    return 0 if payload.get("ok") else 1


def _print_harness_error(exc: Exception, as_json: bool = False) -> int:
    payload = classify_exception(exc).to_dict()
    if as_json:
        print(json.dumps({"ok": False, "schema_version": "gee-cli/v0.3", "error": payload}, indent=2, ensure_ascii=False))
    else:
        print(f"error: [{payload['category']}] {payload['message']}", file=sys.stderr)
        print(f"hint: {payload['suggested_fix']}", file=sys.stderr)
    return 2


def _file_not_found_payload(path: Path, command: str) -> dict:
    return {
        "ok": False,
        "command": command,
        "schema_version": "gee-cli/v0.3",
        "error": {
            "code": "FILE_NOT_FOUND",
            "message": f"File not found: {path}",
            "hint": "Check the path, render the plan first, or run from the repository root.",
        },
    }


def _script_execution_ok(result: dict[str, Any]) -> bool:
    return bool(result.get("ok", result.get("system_exit_code", 0) == 0))


PROJECT_ENV_VARS = ("EE_PROJECT", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_QUOTA_PROJECT", "CLOUDSDK_CORE_PROJECT")

V03_HK_2024_16DAY_NDVI_TEMPLATE = "hk_2024_16day_ndvi_csv"
V03_HK_2024_16DAY_NDVI_SELECTORS = [
    "aoi_name",
    "year",
    "period_index",
    "date_start",
    "date_end",
    "temporal_cadence_days",
    "mean_ndvi",
    "image_count_before_cloud_filter",
    "image_count_after_cloud_filter",
    "dataset_id",
    "scale_m",
    "crs",
    "aoi_source",
    "export_description",
]
V03_GENERIC_PREFLIGHT_TEMPLATES = {
    "sentinel2_index_image",
    "sentinel2_index_table",
    "sentinel2_ndvi_composite",
    "landsat_lst",
    "landsat_lst_table",
    "sentinel1_flood_before_after",
}


def _gcloud_project() -> dict[str, Any]:
    if not shutil.which("gcloud"):
        return {"source": "gcloud_config", "available": False, "project": None}
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        return {"source": "gcloud_config", "available": True, "project": None, "error": type(exc).__name__}
    project = result.stdout.strip()
    if not project or project == "(unset)" or result.returncode != 0:
        return {"source": "gcloud_config", "available": True, "project": None}
    return {"source": "gcloud_config", "available": True, "project": project}


def _discover_project_sources() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    discovered: list[dict[str, str]] = []
    checked: list[dict[str, Any]] = []
    for var in PROJECT_ENV_VARS:
        value = os.environ.get(var)
        checked.append({"source": f"env:{var}", "available": bool(value), "project": value or None})
        if value:
            discovered.append({"source": f"env:{var}", "project": value})
    gcloud = _gcloud_project()
    checked.append(gcloud)
    if gcloud.get("project"):
        discovered.append({"source": "gcloud_config", "project": str(gcloud["project"])})
    return discovered, checked


def _auth_next_commands(discovered: list[dict[str, str]]) -> list[str]:
    if discovered:
        project = discovered[0]["project"]
        return [
            f"gee-skill auth check --project {project} --json",
            "gee-skill auth check --use-discovered-project --json",
        ]
    return [
        "export EE_PROJECT=your-google-cloud-project-id",
        "earthengine set_project $EE_PROJECT",
        "gee-skill auth check --project $EE_PROJECT --json",
    ]


def cmd_info(args: argparse.Namespace) -> int:
    root = project_root()
    data = {
        "name": "gee-agent-skill",
        "version": __version__,
        "identity": "agent-native Google Earth Engine CLI harness",
        "project_root": str(root),
        "default_index": str(default_index_path(root)),
        "default_templates_dir": str(default_templates_dir(root)),
        "commands": {
            "auth": ["check"],
            "aoi": ["resolve", "validate", "summarize"],
            "observe": ["natural-language feedback"],
            "catalog": ["search", "show", "recommend", "evidence"],
            "recipe": ["list", "show"],
            "rules": ["list", "show"],
            "plan": ["from-text", "from-yaml", "review", "set"],
            "render": ["plan-to-script"],
            "validate": ["script"],
            "preflight": ["plan"],
            "run": ["script", "plan"],
            "exports": ["list", "watch"],
            "trace": ["list", "inspect"],
            "corpus": ["coverage"],
            "eval": ["suite"],
        },
        "golden_examples": [
            "HK Jan 2024 NDVI CSV",
            "HK Jan 2024 land-cover-aware NDVI CSV",
            "HK 2024 16-day NDVI plan",
        ],
    }
    print(json.dumps(_envelope_ok(data), indent=2, ensure_ascii=False) if args.json else data["identity"])
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = project_root()
    checks = {
        "project_root_exists": root.exists(),
        "skill_md_exists": (root / "SKILL.md").exists(),
        "readme_exists": (root / "README.md").exists(),
        "knowledge_base_exists": (root / "references" / "knowledge_base").exists(),
        "index_exists": default_index_path(root).exists(),
        "templates_dir_exists": default_templates_dir(root).exists(),
        "boundary_exists": default_boundary_path().exists(),
    }
    try:
        import ee  # type: ignore  # noqa: F401

        earthengine_api_installed = True
    except Exception:
        earthengine_api_installed = False
    data = {
        "ok": all(checks.values()),
        "checks": checks,
        "earthengine_api_installed": earthengine_api_installed,
        "credentials_checked": False,
        "credential_note": "doctor does not print credential paths or tokens.",
    }
    payload = _envelope_ok(data) if data["ok"] else _envelope_error("DOCTOR_FAILED", "One or more local harness checks failed.", "Inspect data.checks and install/build missing resources.")
    if not data["ok"]:
        payload["data"] = data
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["ok"] else 1


def cmd_auth_check(args: argparse.Namespace) -> int:
    ee_spec = importlib.util.find_spec("ee")
    if ee_spec is None:
        payload = _envelope_error(
            "EARTHENGINE_API_MISSING",
            "earthengine-api is not installed.",
            "Install with pip install -e '.[earthengine]' or pip install earthengine-api.",
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    try:
        import ee  # type: ignore
    except Exception as exc:
        payload = _envelope_error(
            "EARTHENGINE_IMPORT_ERROR",
            "earthengine-api is installed but could not be imported.",
            "Inspect the original exception and reinstall or repair the failing dependency in this Python environment.",
        )
        payload["error"]["original"] = type(exc).__name__
        payload["error"]["detail"] = str(exc)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    discovered, checked_sources = _discover_project_sources()
    project_source = "--project" if args.project else None
    project = args.project
    if not project and args.use_discovered_project and discovered:
        project = discovered[0]["project"]
        project_source = discovered[0]["source"]
    if not project:
        print(
            json.dumps(
                _envelope_ok(
                    {
                        "earthengine_api_installed": True,
                        "initialized": False,
                        "project": None,
                        "project_sources": discovered,
                        "checked_project_sources": checked_sources,
                        "credential_note": "Does not inspect Earth Engine credential files or print credential paths.",
                        "next_commands": _auth_next_commands(discovered),
                        "note": "Pass --project or --use-discovered-project to verify live initialization.",
                    }
                ),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0
    try:
        ee.Initialize(project=project)
        ee.Number(1).getInfo()
    except Exception as exc:
        payload = _envelope_error(
            "AUTH_CHECK_FAILED",
            str(exc),
            "Run earthengine authenticate and confirm the project has Earth Engine access.",
        )
        payload["data"] = {
            "earthengine_api_installed": True,
            "initialized": False,
            "project": project,
            "project_source": project_source,
            "project_sources": discovered,
            "checked_project_sources": checked_sources,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            _envelope_ok(
                {
                    "earthengine_api_installed": True,
                    "initialized": True,
                    "project": project,
                    "project_source": project_source,
                    "project_sources": discovered,
                    "checked_project_sources": checked_sources,
                }
            ),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def cmd_catalog_search(args: argparse.Namespace) -> int:
    data = {"query": args.query, "results": search_datasets(args.query, top_k=args.top_k)}
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_catalog_show(args: argparse.Namespace) -> int:
    data = get_dataset(args.dataset_id)
    if not data:
        return _print_envelope(
            _envelope_error("DATASET_NOT_FOUND", f"Unknown dataset: {args.dataset_id}", "Run gee-skill catalog search <query> --json."),
            as_json=True,
        )
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_catalog_recommend(args: argparse.Namespace) -> int:
    data = {
        "task_type": args.task_type,
        "metric": args.metric,
        "results": recommend_datasets(task_type=args.task_type, metric=args.metric),
    }
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_catalog_evidence(args: argparse.Namespace) -> int:
    try:
        index = load_index(Path(args.index))
        normalized_category = normalize_knowledge_category(args.category)
        cards = list_knowledge_cards(index, category=normalized_category, top_k=args.top_k)
    except Exception as exc:
        return _print_envelope(
            _envelope_error("CATALOG_EVIDENCE_FAILED", str(exc), "Rebuild references/index/gee_docs_index.json or choose a supported category."),
            as_json=True,
        )
    data = {
        "category": args.category,
        "normalized_category": normalized_category,
        "count": len(cards),
        "cards": cards,
    }
    return _print_envelope(_command_envelope("catalog evidence", data), as_json=args.json)


def cmd_recipe_list(args: argparse.Namespace) -> int:
    data = list_recipes()
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_recipe_show(args: argparse.Namespace) -> int:
    data = get_recipe(args.recipe_id)
    if not data:
        return _print_envelope(
            _envelope_error("RECIPE_NOT_FOUND", f"Unknown recipe: {args.recipe_id}", "Run gee-skill recipe list --json."),
            as_json=True,
        )
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_rules_list(args: argparse.Namespace) -> int:
    data = list_rulesets()
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_rules_show(args: argparse.Namespace) -> int:
    data = get_ruleset(args.ruleset_id)
    if not data:
        return _print_envelope(
            _envelope_error("RULESET_NOT_FOUND", f"Unknown ruleset: {args.ruleset_id}", "Run gee-skill rules list --json."),
            as_json=True,
        )
    return _print_envelope(_envelope_ok(data), as_json=args.json)


def cmd_plan_from_text(args: argparse.Namespace) -> int:
    result = build_general_plan_from_text(args.request)
    if not result["ok"]:
        payload = _envelope_error(
            result["error"]["category"],
            result["error"]["message"],
            result["error"]["suggested_fix"],
        )
        payload["data"] = {
            "missing_fields": result.get("missing_fields", []),
            "slots": result.get("slots", {}),
            "candidate_datasets": result.get("candidate_datasets", []),
            "closest_recipes": result.get("closest_recipes", []),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    schema_errors = validate_v03_plan_schema(result["plan"])
    if schema_errors:
        payload = _envelope_error(
            "PLAN_SCHEMA_ERROR",
            "Generated gee-plan/v0.3 failed schema checks.",
            "Fix the planner output before rendering or running this plan.",
        )
        payload["data"] = {"schema_errors": schema_errors, "plan": result["plan"]}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    if args.out:
        out = Path(args.out)
        write_task_plan(out, result["plan"])
        result["plan_path"] = str(out)
    print(json.dumps(_envelope_ok(result), indent=2, ensure_ascii=False) if args.json else plan_review_text(_legacy_plan_view(result["plan"])))
    return 0


def _observe_next_steps(result: dict) -> list[dict[str, str]]:
    if not result.get("ok"):
        missing = ", ".join(result.get("missing_fields", [])) or "unknown fields"
        return [
            {
                "kind": "ask_user",
                "command": "",
                "reason": f"Clarify missing fields before planning: {missing}.",
            },
            {
                "kind": "inspect_recipes",
                "command": "gee-skill recipe list --json",
                "reason": "Show supported task families and examples.",
            },
        ]
    plan = result["plan"]
    metric = plan.get("intent", {}).get("metric")
    task_type = plan.get("task_type")
    recipe_id = plan.get("intent", {}).get("recipe_id")
    rulesets = plan.get("validation", {}).get("rulesets", [])
    request = plan.get("raw_user_request", "")
    steps = [
        {
            "kind": "save_plan",
            "command": f'gee-skill plan from-text "{request}" --out outputs/plans/{plan["plan_id"]}.yaml --json',
            "reason": "Persist an editable plan without contacting Earth Engine.",
        },
        {
            "kind": "inspect_dataset",
            "command": f"gee-skill catalog recommend --task-type {task_type} --metric {metric} --json",
            "reason": "Review dataset candidates before rendering or live work.",
        },
        {
            "kind": "inspect_recipe",
            "command": f"gee-skill recipe show {recipe_id} --json",
            "reason": "Review required inputs, templates, preflight profile, and output schema.",
        },
    ]
    for ruleset in rulesets:
        steps.append(
            {
                "kind": "inspect_rules",
                "command": f"gee-skill rules show {ruleset} --json",
                "reason": "Review validation contract before rendering or running.",
            }
        )
    if not plan.get("execution", {}).get("template_ready"):
        steps.append(
            {
                "kind": "implementation_gap",
                "command": "",
                "reason": "No ready template is registered yet; implement or select an approved template before dry-run/live execution.",
            }
        )
    else:
        steps.append(
            {
                "kind": "dry_run",
                "command": "gee-skill plan from-yaml <saved-plan-or-task-yaml> --json",
                "reason": "Continue through review/render/validate flow before live preflight.",
            }
        )
    return steps


def cmd_observe(args: argparse.Namespace) -> int:
    result = build_general_plan_from_text(args.request)
    if result.get("ok"):
        plan = result["plan"]
        data = {
            "request": args.request,
            "status": "planned",
            "summary": {
                "plan_id": plan["plan_id"],
                "task_type": plan["task_type"],
                "metric": plan["intent"]["metric"],
                "aoi": plan["aoi"],
                "time_range": plan["time_range"],
                "output": plan["output"],
                "recipe_id": plan["intent"]["recipe_id"],
                "template_ready": plan["execution"]["template_ready"],
                "live_execution_default": plan["export"]["live_execution_default"],
            },
            "review_questions": plan.get("review_questions", []),
            "next_steps": _observe_next_steps(result),
        }
        payload = _envelope_ok(data)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Plan: {data['summary']['plan_id']}")
            print(f"Task: {data['summary']['task_type']} / {data['summary']['metric']}")
            print("Next steps:")
            for step in data["next_steps"]:
                command = f" `{step['command']}`" if step["command"] else ""
                print(f"- {step['kind']}:{command} {step['reason']}")
        return 0
    data = {
        "request": args.request,
        "status": result.get("status"),
        "missing_fields": result.get("missing_fields", []),
        "slots": result.get("slots", {}),
        "closest_recipes": result.get("closest_recipes", []),
        "next_steps": _observe_next_steps(result),
    }
    payload = _envelope_error(
        result["error"]["category"],
        result["error"]["message"],
        result["error"]["suggested_fix"],
    )
    payload["data"] = data
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else payload["error"]["message"])
    return 1


def _legacy_plan_view(plan: dict) -> dict:
    return {
        "task_id": plan.get("plan_id"),
        "interpreted_intent": {
            "name": plan.get("intent", {}).get("recipe_id"),
            "description": plan.get("raw_user_request"),
            "template": plan.get("execution", {}).get("template"),
        },
        "aoi": plan.get("aoi", {}),
        "time_range": plan.get("time_range", {}),
        "datasets": {"selected": plan.get("selected_datasets", [])},
        "output_schema": plan.get("output", {}),
        "review_questions": plan.get("review_questions", []),
    }


def cmd_plan_from_yaml(args: argparse.Namespace) -> int:
    try:
        loaded = yaml.safe_load(Path(args.path).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("YAML file must contain a mapping.")
        if loaded.get("schema_version") == "gee-plan/v0.3":
            return _cmd_plan_from_v03_yaml(args, loaded)
    except Exception as exc:
        payload = _envelope_error("PLAN_YAML_ERROR", str(exc), "Use a valid task YAML or generated gee-plan/v0.3 YAML.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    try:
        task = load_task(Path(args.path))
        plan = build_task_plan(task)
    except Exception as exc:
        payload = _envelope_error("PLAN_YAML_ERROR", str(exc), "Use a valid task YAML or generated task_plan.yaml.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps(_envelope_ok({"plan": plan}), indent=2, ensure_ascii=False) if args.json else plan_review_text(plan))
    return 0


def _cmd_plan_from_v03_yaml(args: argparse.Namespace, plan: dict) -> int:
    schema_errors = validate_v03_plan_schema(plan)
    if schema_errors:
        payload = _envelope_error(
            "PLAN_SCHEMA_ERROR",
            "gee-plan/v0.3 failed schema checks.",
            "Review the plan YAML against schemas/gee-plan-v0.3.schema.json before rendering or running.",
        )
        payload["data"] = {"schema_errors": schema_errors, "plan": plan}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    execution = dict(plan.get("execution") or {})
    template = execution.get("template")
    context = execution.get("context")
    data: dict[str, Any] = {"plan": plan}
    if not template or not context:
        payload = _envelope_ok(data)
        payload["data"]["render_status"] = "not_rendered"
        payload["data"]["render_reason"] = "Plan has no ready template/context."
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else plan_review_text(_legacy_plan_view(plan)))
        return 0
    try:
        rendered = render_template(Path(args.templates_dir), str(template), dict(context))
        outputs = dict(execution.get("outputs") or {})
        script_path = Path(args.script_out or outputs.get("script") or f"outputs/scripts/{plan['plan_id']}.py")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(rendered, encoding="utf-8")
        validation = validate_script(script_path).to_dict()
        dry = dry_run_report(script_path, validation)
    except Exception as exc:
        payload = _envelope_error("PLAN_RENDER_FAILED", str(exc), "Review execution.template and execution.context fields.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    data.update({"script": str(script_path), "validation": validation, "dry_run": dry})
    print(json.dumps(_envelope_ok(data), indent=2, ensure_ascii=False) if args.json else plan_review_text(_legacy_plan_view(plan)))
    return 0 if validation["ok"] else 1


def cmd_plan_review_v03(args: argparse.Namespace) -> int:
    return cmd_review_plan(argparse.Namespace(task_plan=args.path, json=args.json))


def cmd_plan_set(args: argparse.Namespace) -> int:
    try:
        loaded = yaml.safe_load(Path(args.path).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("Plan file must contain a mapping.")
        plan = loaded
        cursor = plan
        parts = args.key.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
            if not isinstance(cursor, dict):
                raise ValueError(f"Cannot set nested key through non-object: {part}")
        cursor[parts[-1]] = args.value
        if plan.get("schema_version") == "gee-plan/v0.3":
            schema_errors = validate_v03_plan_schema(plan)
            if schema_errors:
                raise ValueError("Updated plan failed schema checks: " + "; ".join(schema_errors))
        write_task_plan(Path(args.path), plan)
    except Exception as exc:
        payload = _envelope_error("PLAN_SET_FAILED", str(exc), "Use an existing plan path and a dotted key such as execution.context.drive_folder.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps(_envelope_ok({"path": args.path, "key": args.key, "value": args.value}), indent=2, ensure_ascii=False))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    return cmd_plan_from_yaml(
        argparse.Namespace(
            path=args.plan,
            templates_dir=args.templates_dir,
            script_out=args.script_out,
            json=args.json,
        )
    )


def cmd_preflight(args: argparse.Namespace) -> int:
    return cmd_preflight_plan(
        argparse.Namespace(
            task_plan=args.plan,
            project=args.project,
            run_id=args.run_id,
            json=args.json,
            command_name="preflight",
        )
    )


def _geojson_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = payload.get("features") if isinstance(payload, dict) else None
    coordinates: list[float] = []

    def visit(value: Any) -> None:
        if isinstance(value, list):
            if len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
                coordinates.extend([float(value[0]), float(value[1])])
                return
            for item in value:
                visit(item)

    if isinstance(payload, dict):
        visit(payload.get("geometry") or payload.get("coordinates") or payload)
    xs = coordinates[0::2]
    ys = coordinates[1::2]
    bbox = [min(xs), min(ys), max(xs), max(ys)] if xs and ys else None
    feature_count = None
    if isinstance(payload, dict):
        if isinstance(features, list):
            feature_count = len(features)
        elif payload.get("type") == "Feature":
            feature_count = 1
    return {
        "source": str(path),
        "source_type": "geojson",
        "feature_count": feature_count,
        "bbox": bbox,
        "valid": bool(bbox),
        "notes": "Offline geometry summary only; live area/pixel checks belong in preflight.",
    }


def _aoi_from_plan(path: Path) -> dict[str, Any]:
    plan = _load_yaml_mapping(path, label="AOI source plan")
    if _is_v03_plan(plan):
        return {
            "source": str(path),
            "source_type": "gee-plan/v0.3",
            "aoi": plan.get("aoi"),
            "time_range": plan.get("time_range"),
            "validation": {"valid": bool(plan.get("aoi")), "messages": [] if plan.get("aoi") else ["Plan has no AOI field."]},
        }
    task_plan, task, _review, schema = _load_plan_for_command(path)
    context = dict(task.get("context") or {})
    return {
        "source": str(path),
        "source_type": schema,
        "aoi": {
            "type": "boundary_geojson" if context.get("boundary_geojson") else "unknown",
            "name": context.get("aoi_name") or context.get("district") or "AOI from task context",
            "source": context.get("boundary_geojson"),
        },
        "validation": {"valid": bool(context.get("boundary_geojson") or context.get("aoi_name") or context.get("district"))},
        "task_plan": task_plan.get("task_id") or task_plan.get("plan_id"),
    }


def _summarize_aoi_source(source: str) -> dict[str, Any]:
    path = Path(source)
    if path.exists():
        if path.suffix.lower() in {".json", ".geojson"}:
            return _geojson_summary(path)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return _aoi_from_plan(path)
    slots = parse_request_slots(source)
    aoi = slots.get("aoi")
    return {
        "source": source,
        "source_type": "natural_language",
        "aoi": aoi,
        "validation": {
            "valid": bool(aoi),
            "messages": [] if aoi else ["No AOI recognized. Provide a named place, supplied AOI, GeoJSON, EE asset, or bbox[...] text."],
        },
    }


def cmd_aoi_resolve(args: argparse.Namespace) -> int:
    data = _summarize_aoi_source(args.source)
    ok = bool((data.get("validation") or {}).get("valid"))
    payload = _command_envelope("aoi resolve", data)
    payload["ok"] = ok
    if not ok:
        payload["error"] = {
            "code": "AMBIGUOUS_AOI",
            "message": "No usable AOI was recognized.",
            "hint": "Use a supported named place, GeoJSON path, Earth Engine asset id, bbox[...] value, or generated plan path.",
        }
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if ok else 1


def cmd_aoi_validate(args: argparse.Namespace) -> int:
    return cmd_aoi_resolve(args)


def cmd_aoi_summarize(args: argparse.Namespace) -> int:
    return cmd_aoi_resolve(args)


TRACE_EXPECTED_FILES = (
    "environment.json",
    "task.yaml",
    "retrieval_trace.json",
    "plan.md",
    "validation_report.json",
    "dry_run_report.json",
    "final_report.md",
)


def _run_trace_dir(run_id: str) -> Path:
    path = Path(run_id)
    if path.exists():
        return path
    return project_root() / "outputs" / "runs" / run_id


def _inspect_trace(run_id: str) -> dict[str, Any]:
    run_dir = _run_trace_dir(run_id)
    files = []
    for name in TRACE_EXPECTED_FILES:
        path = run_dir / name
        files.append({"path": str(path), "name": name, "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0})
    extra_files = []
    if run_dir.exists():
        extra_files = sorted(item.name for item in run_dir.iterdir() if item.is_file() and item.name not in TRACE_EXPECTED_FILES)
    missing = [item["name"] for item in files if not item["exists"]]
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "exists": run_dir.exists(),
        "complete_core_trace": run_dir.exists() and not missing,
        "missing_core_files": missing,
        "core_files": files,
        "extra_files": extra_files,
    }


def cmd_trace_inspect(args: argparse.Namespace) -> int:
    data = _inspect_trace(args.run_id)
    payload = _command_envelope("trace inspect", data)
    payload["ok"] = bool(data["exists"])
    if not data["exists"]:
        payload["error"] = {
            "code": "TRACE_NOT_FOUND",
            "message": f"Run trace {args.run_id!r} was not found.",
            "hint": "Pass a run id under outputs/runs/ or a direct trace directory path.",
        }
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["exists"] else 1


def cmd_trace_list(args: argparse.Namespace) -> int:
    runs_dir = project_root() / "outputs" / "runs"
    traces = []
    if runs_dir.exists():
        for path in sorted(runs_dir.iterdir(), key=lambda item: item.name, reverse=True):
            if path.is_dir():
                traces.append(_inspect_trace(str(path)))
    data = {"runs_dir": str(runs_dir), "traces": traces[: args.limit], "count": len(traces)}
    print(json.dumps(_command_envelope("trace list", data), indent=2, ensure_ascii=False) if args.json else json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def _coverage_contract(task_type: str | None, output: str | None) -> dict[str, int]:
    contract = {
        "dataset_evidence": 1,
        "recipe_evidence": 1,
        "operator_evidence": 1,
        "failure_evidence": 1,
    }
    if output and output.lower() in {"csv", "table", "geotiff", "image"}:
        contract["export_evidence"] = 1
    return contract


def cmd_corpus_coverage(args: argparse.Namespace) -> int:
    terms = [args.query or "", args.task_type or "", args.metric or "", args.output or ""]
    query = " ".join(item for item in terms if item).strip() or "Earth Engine dataset operator failure export"
    try:
        index = load_index(Path(args.index))
        results = _operator_aware_results(index, query, top_k=args.top_k)
        trace = build_retrieval_trace(query, results)
    except Exception as exc:
        payload = _envelope_error("CORPUS_COVERAGE_FAILED", str(exc), "Rebuild the docs index or inspect references/knowledge_base.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    coverage = dict(trace.get("coverage") or {})
    contract = _coverage_contract(args.task_type, args.output)
    missing = {key: required for key, required in contract.items() if int(coverage.get(key, 0)) < required}
    data = {
        "query": query,
        "task_type": args.task_type,
        "metric": args.metric,
        "output": args.output,
        "coverage": coverage,
        "required_coverage": contract,
        "missing_coverage": missing,
        "evidence": trace.get("evidence", [])[: args.top_k],
    }
    payload = _command_envelope("corpus coverage", data)
    payload["ok"] = not missing
    if missing:
        payload["error"] = {
            "code": "EVIDENCE_COVERAGE_INCOMPLETE",
            "message": "Retrieved evidence does not satisfy the task evidence contract.",
            "hint": "Add or improve dataset, recipe, operator, rule, failure, or export cards before treating this task as grounded.",
        }
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if not missing else 1


def cmd_tools(args: argparse.Namespace) -> int:
    data = {
        "installed_tools": installed_tools(),
        "exposed_tools": exposed_tools(),
    }
    payload = _command_envelope("tools", data)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_search_docs(args: argparse.Namespace) -> int:
    try:
        index = load_index(Path(args.index))
        results = search(index, args.query, top_k=args.top_k)
    except Exception as exc:
        return _print_error(str(exc))
    if args.json:
        payload = _command_envelope("search-docs", {"query": args.query, "results": results_to_dicts(results)})
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No matching local documentation chunks found.")
            return 0
        for item in results:
            print(f"{item.score:.3f}  {item.title}  ({item.source_path})")
            if item.url:
                print(f"  {item.url}")
            print(f"  {item.excerpt}")
    return 0


def _load_plan_inputs(args: argparse.Namespace) -> tuple[dict, str, str | None, dict | None]:
    if args.task_file:
        task = load_task(Path(args.task_file))
        return task, str(task.get("task")), task.get("template"), task_to_context(task)
    task_text = args.task
    if not task_text:
        raise ValueError("Provide a task file or --task.")
    context = load_context(Path(args.context)) if args.context else None
    return {"id": args.run_id or "ad_hoc_task", "task": task_text, "template": args.template}, task_text, args.template, context


def _operator_aware_results(index: dict, query: str, top_k: int):
    results = search(index, query, top_k=top_k)
    by_chunk = {item.chunk_id: item for item in results}
    supplement_queries = [
        "Sentinel-2 SR Harmonized B8 B4 NDVI SCL cloud mask",
        "Dynamic World V1 label probability bands land cover class mask",
        "ESA WorldCover v200 land cover class reference",
        "filterDate filterBounds normalizedDifference reduceRegion Export.table.toDrive CSV",
        "Earth Engine client server deferred execution avoid getInfo map iterate",
        "Earth Engine scale projection CRS reducer reduceRegion reduceRegions bestEffort tileScale",
        "Earth Engine joins ImageCollection temporal join saveFirst saveAll",
        "Earth Engine export tasks quotas timeout debugging",
        "Image has no bands empty image collection missing NDVI band failure recovery",
    ]
    for supplement_query in supplement_queries:
        for item in search(index, supplement_query, top_k=4):
            by_chunk.setdefault(item.chunk_id, item)
    return list(by_chunk.values())


def _write_ask_final_report(
    trace: RunTrace,
    *,
    task: dict,
    validation: dict,
    dry_run: dict,
    preflight: dict | None = None,
    live_run: dict | None = None,
) -> None:
    trace.write_final_report(
        "GEE v0.1 Natural-Language Run Trace",
        {
            "Task": task,
            "Validation": validation,
            "Dry Run": dry_run,
            "Preflight": preflight or "Not executed.",
            "Live Run": live_run or "Not executed.",
        },
    )


def _plan_query(task: dict) -> str:
    return task.get("query") or task.get("task") or ""


def _create_ask_trace_with_plan(args: argparse.Namespace, task: dict) -> tuple[RunTrace, dict, list, str]:
    trace = RunTrace.create(run_id=args.run_id)
    trace.write_yaml("task.yaml", task)
    task_plan = build_task_plan(task)
    trace.write_yaml("task_plan.yaml", task_plan)
    query = _plan_query(task)
    index = load_index(Path(args.index))
    results = _operator_aware_results(index, query, top_k=args.top_k)
    trace.write_json("retrieval_trace.json", build_retrieval_trace(query, results))
    plan = build_plan(task["task"], results, template=task["template"])
    trace.write_text("plan.md", plan.body)
    external_plan = Path(task.get("outputs", {}).get("task_plan", trace.path("task_plan.yaml")))
    write_task_plan(external_plan, task_plan)
    return trace, task_plan, results, plan.body


def _prepare_ask_artifacts(args: argparse.Namespace, task: dict) -> tuple[RunTrace, Path, dict, dict, dict]:
    trace, task_plan, results, plan_body = _create_ask_trace_with_plan(args, task)

    plan_path = Path(task.get("outputs", {}).get("plan", trace.path("plan.md")))
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan_body, encoding="utf-8")

    context = dict(task["context"])
    context["drive_folder"] = args.export_folder
    if args.boundary_geojson:
        context["boundary_geojson"] = args.boundary_geojson
    task["context"] = context
    rendered = render_template(Path(args.templates_dir), task["template"], context)
    script_path = Path(task.get("outputs", {}).get("script", "outputs/scripts/hk_2024_01_ndvi_csv.py"))
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(rendered, encoding="utf-8")
    trace.write_text("generated_script.py", rendered)

    validation = validate_script(script_path).to_dict()
    dry = dry_run_report(script_path, validation)
    trace.write_json("validation_report.json", validation)
    trace.write_json("dry_run_report.json", dry)
    return trace, script_path, validation, dry, context


def _preflight_from_v01_context(args: argparse.Namespace, context: dict) -> dict:
    landcover_dataset_id = context.get("landcover_dataset_id")
    landcover = "dynamic-world" if landcover_dataset_id == "GOOGLE/DYNAMICWORLD/V1" else None
    config = _preflight_config_from_values(
        project=args.project,
        year=int(context["year"]),
        month=int(context["month"]),
        scope="hong-kong",
        district=None,
        boundary_geojson=str(context["boundary_geojson"]),
        dataset_id=str(context["dataset_id"]),
        scale=int(context["scale"]),
        crs=str(context["crs"]),
        cloudy_pixel_percentage=int(context["cloudy_pixel_percentage"]),
        tile_scale=int(context["tile_scale"]),
        landcover=landcover,
        landcover_dataset_id=landcover_dataset_id,
        landcover_strategy=context.get("landcover_strategy"),
        dynamic_world_probability_threshold=float(context.get("dynamic_world_probability_threshold", 0.35)),
    )
    return run_hk_ndvi_preflight(config)


def _load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} must contain a mapping: {path}")
    return data


def _is_v03_plan(plan: dict[str, Any]) -> bool:
    return plan.get("schema_version") == "gee-plan/v0.3"


def _v03_output_schema(plan: dict[str, Any]) -> list[str]:
    output_schema = plan.get("output_schema")
    if isinstance(output_schema, list):
        return [str(item) for item in output_schema]
    execution = dict(plan.get("execution") or {})
    context = dict(execution.get("context") or {})
    context_schema = context.get("output_schema")
    if isinstance(context_schema, list):
        return [str(item) for item in context_schema]
    if execution.get("template") == V03_HK_2024_16DAY_NDVI_TEMPLATE:
        return list(V03_HK_2024_16DAY_NDVI_SELECTORS)
    return []


def _v03_plan_to_task(plan: dict[str, Any]) -> dict[str, Any]:
    execution = dict(plan.get("execution") or {})
    intent = dict(plan.get("intent") or {})
    return {
        "id": plan.get("plan_id"),
        "intent": intent.get("recipe_id") or intent.get("metric"),
        "task": plan.get("raw_user_request"),
        "query": plan.get("raw_user_request"),
        "template": execution.get("template"),
        "context": dict(execution.get("context") or {}),
        "outputs": dict(execution.get("outputs") or {}),
        "output_schema": _v03_output_schema(plan),
        "limitations": list(plan.get("limitations") or []),
        "version": plan.get("schema_version"),
    }


def _format_selected_dataset(item: dict[str, Any]) -> str:
    dataset_id = item.get("dataset_id") or item.get("id")
    reason = item.get("selection_reason") or item.get("role")
    return f"- {dataset_id}: {reason}" if reason else f"- {dataset_id}"


def _v03_plan_review_text(plan: dict[str, Any]) -> str:
    execution = dict(plan.get("execution") or {})
    context = dict(execution.get("context") or {})
    intent = dict(plan.get("intent") or {})
    time_range = dict(plan.get("time_range") or {})
    export = dict(plan.get("export") or {})
    output = dict(plan.get("output") or {})
    lines = [
        f"Plan: {plan.get('plan_id')}",
        f"Schema: {plan.get('schema_version')}",
        f"Request: {plan.get('raw_user_request')}",
        f"Task: {plan.get('task_type')} / {intent.get('metric')} ({intent.get('recipe_id')})",
        f"AOI: {dict(plan.get('aoi') or {}).get('name')}",
        f"Time range: {time_range.get('date_start')} to {time_range.get('date_end')}",
        "Selected datasets:",
    ]
    for item in plan.get("selected_datasets") or []:
        lines.append(_format_selected_dataset(dict(item)))
    if not plan.get("selected_datasets"):
        lines.append("- None selected.")
    lines.extend(
        [
            "Execution:",
            f"- template: {execution.get('template')}",
            f"- template_ready: {execution.get('template_ready')}",
            f"- preflight_profile: {dict(plan.get('preflight') or {}).get('profile')}",
            "Export:",
            f"- destination: {export.get('destination') or output.get('destination')}",
            f"- format: {export.get('format') or output.get('format')}",
            f"- description: {context.get('export_description')}",
            f"- Drive folder: {context.get('drive_folder')}",
            f"- file prefix: {context.get('file_prefix')}",
            "Output fields:",
        ]
    )
    for field in _v03_output_schema(plan):
        lines.append(f"- {field}")
    lines.append("Review questions:")
    for question in plan.get("review_questions") or []:
        lines.append(f"- {question}")
    lines.append("Live execution requires explicit confirmation and a template-specific v0.3 preflight adapter.")
    return "\n".join(lines)


def _load_plan_for_command(path: Path) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    raw = _load_yaml_mapping(path, label="Plan")
    if _is_v03_plan(raw):
        return raw, _v03_plan_to_task(raw), _v03_plan_review_text(raw), "gee-plan/v0.3"
    task_plan = load_task_plan(path)
    return task_plan, _task_from_task_plan(task_plan), plan_review_text(task_plan), "task-plan"


def _set_execution_context(plan: dict[str, Any], context: dict[str, Any]) -> None:
    execution = plan.setdefault("execution", {})
    if isinstance(execution, dict):
        execution["context"] = context


def _parse_iso_date(value: Any) -> date:
    year, month, day = (int(part) for part in str(value).split("-"))
    return date(year, month, day)


def _expected_period_rows(start_date: Any, end_date: Any, cadence_days: Any) -> int:
    start = _parse_iso_date(start_date)
    end = _parse_iso_date(end_date)
    cadence = int(cadence_days)
    days = (end - start).days
    if days <= 0:
        raise ValueError("date_end must be after date_start.")
    if cadence <= 0:
        raise ValueError("temporal cadence must be positive.")
    return (days + cadence - 1) // cadence


def _unsupported_v03_preflight_report(args: argparse.Namespace, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    template = dict(plan.get("execution") or {}).get("template")
    critical = error_payload(
        "V03_PREFLIGHT_UNSUPPORTED",
        f"v0.3 live preflight is not implemented for template {template!r}.",
        "Keep this plan at review/render/validate, or add a template-specific v0.3 preflight adapter before live export.",
    )
    return {
        "ok": False,
        "decision": "block_export",
        "schema_version": plan.get("schema_version"),
        "plan_id": plan.get("plan_id"),
        "profile": dict(plan.get("preflight") or {}).get("profile"),
        "template": template,
        "project": args.project,
        "aoi_name": context.get("aoi_name") or dict(plan.get("aoi") or {}).get("name"),
        "critical_error": critical,
        "errors": [critical],
        "warnings": [],
        "checks": {"template_adapter": {"ok": False, "template": template}},
    }


def _generic_v03_preflight_config(
    args: argparse.Namespace,
    plan: dict[str, Any],
    context: dict[str, Any],
) -> GenericV03PreflightConfig:
    execution = dict(plan.get("execution") or {})
    template = str(execution.get("template") or "")
    preflight = dict(plan.get("preflight") or {})
    export = dict(plan.get("export") or {})
    output = dict(plan.get("output") or {})
    profile = str(preflight.get("profile") or "generic")
    dataset_id = str(context.get("dataset_id") or _first_selected_dataset_id(plan) or "")
    date_start = str(context.get("date_start") or dict(plan.get("time_range") or {}).get("date_start") or "")
    date_end = str(context.get("date_end") or dict(plan.get("time_range") or {}).get("date_end") or "")
    required_bands: tuple[str, ...] = ()
    qa_bands: tuple[str, ...] = ()
    index_bands = tuple(str(item) for item in context.get("index_bands") or ())
    if template in {"sentinel2_index_image", "sentinel2_index_table", "sentinel2_ndvi_composite"}:
        required_bands = index_bands or ("B8", "B4")
        qa_bands = ("SCL",)
    elif template in {"landsat_lst", "landsat_lst_table"}:
        required_bands = ("ST_B10",)
        qa_bands = ("QA_PIXEL",)
    elif template == "sentinel1_flood_before_after":
        polarization = str(context.get("polarization") or "VH")
        required_bands = (polarization,)
        date_start = str(context.get("before_start") or date_start)
        date_end = str(context.get("after_end") or date_end)
    return GenericV03PreflightConfig(
        project=args.project,
        schema_version=plan.get("schema_version"),
        plan_id=plan.get("plan_id"),
        profile=profile,
        template=template,
        dataset_id=dataset_id,
        date_start=date_start,
        date_end=date_end,
        aoi_asset=str(context.get("aoi_asset") or ""),
        aoi_name=context.get("aoi_name") or dict(plan.get("aoi") or {}).get("name"),
        scale=int(context.get("scale") or dict(plan.get("scale_crs_projection") or {}).get("scale_m") or 30),
        crs=str(context.get("crs") or dict(plan.get("scale_crs_projection") or {}).get("crs") or "EPSG:4326"),
        max_pixels=int(context.get("max_pixels") or 10000000000000),
        required_bands=required_bands,
        qa_bands=qa_bands,
        index_name=context.get("index_name"),
        index_bands=index_bands,
        cloud_property="CLOUDY_PIXEL_PERCENTAGE" if template.startswith("sentinel2_") else None,
        cloudy_pixel_percentage=int(context.get("cloudy_pixel_percentage", 80)) if template.startswith("sentinel2_") else None,
        before_start=context.get("before_start"),
        before_end=context.get("before_end"),
        after_start=context.get("after_start"),
        after_end=context.get("after_end"),
        polarization=context.get("polarization"),
        orbit_pass=context.get("orbit_pass"),
        export_description=context.get("export_description"),
        drive_folder=context.get("drive_folder"),
        file_prefix=context.get("file_prefix"),
        output_format=export.get("format") or output.get("format"),
        extra={"context_review_required": context.get("review_required")},
    )


def _first_selected_dataset_id(plan: dict[str, Any]) -> str | None:
    selected = plan.get("selected_datasets") or []
    if selected and isinstance(selected[0], dict):
        return selected[0].get("dataset_id") or selected[0].get("id")
    return None


def _v03_failed_month_report(args: argparse.Namespace, context: dict[str, Any], month: int, exc: Exception) -> dict[str, Any]:
    payload = classify_exception(exc).to_dict()
    return {
        "ok": False,
        "decision": "block_export",
        "project": args.project,
        "year": context.get("year"),
        "month": int(month),
        "scope": "hong-kong",
        "aoi_name": context.get("aoi_name", "Hong Kong"),
        "dataset_id": context.get("dataset_id", "COPERNICUS/S2_SR_HARMONIZED"),
        "critical_error": payload,
        "errors": [payload],
        "warnings": [],
        "checks": {},
    }


def _run_v03_month_preflight_with_retry(
    args: argparse.Namespace,
    context: dict[str, Any],
    month: int,
    config: HKNDVIPreflightConfig,
) -> dict[str, Any]:
    attempts = []
    report: dict[str, Any] | None = None
    for attempt in (1, 2):
        try:
            report = run_hk_ndvi_preflight(config)
        except Exception as exc:
            report = _v03_failed_month_report(args, context, month, exc)
        attempts.append(
            {
                "attempt": attempt,
                "ok": bool(report.get("ok")),
                "critical_error": report.get("critical_error"),
            }
        )
        if report.get("ok"):
            break
        critical_error = report.get("critical_error") or {}
        if not critical_error.get("retryable") or attempt == 2:
            break
        time.sleep(2)
    if report is None:
        raise RuntimeError("Internal error: v0.3 preflight did not produce a report.")
    if len(attempts) > 1:
        report["retry_attempts"] = attempts
    return report


def _preflight_from_v03_plan(args: argparse.Namespace, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    execution = dict(plan.get("execution") or {})
    template = execution.get("template")
    if template != V03_HK_2024_16DAY_NDVI_TEMPLATE:
        if template in V03_GENERIC_PREFLIGHT_TEMPLATES:
            return run_generic_v03_preflight(_generic_v03_preflight_config(args, plan, context))
        return _unsupported_v03_preflight_report(args, plan, context)

    warnings: list[dict[str, Any] | str] = []
    try:
        expected_rows = _expected_period_rows(
            context.get("date_start"),
            context.get("date_end"),
            context.get("temporal_cadence_days", 16),
        )
    except Exception as exc:
        expected_rows = None
        warnings.append(
            {
                "category": "EXPECTED_ROWS_UNKNOWN",
                "message": str(exc),
                "suggested_fix": "Review date_start, date_end, and temporal_cadence_days in the v0.3 plan context.",
            }
        )

    preflight_months = context.get("preflight_months") or [1, 7]
    reports = []
    errors = []
    checks = []
    for month in preflight_months:
        try:
            config = _preflight_config_from_values(
                project=args.project,
                year=int(context["year"]),
                month=int(month),
                scope="hong-kong",
                district=None,
                boundary_geojson=str(context.get("boundary_geojson") or default_boundary_path()),
                dataset_id=str(context.get("dataset_id", "COPERNICUS/S2_SR_HARMONIZED")),
                scale=int(context.get("scale", 10)),
                crs=str(context.get("crs", "EPSG:4326")),
                cloudy_pixel_percentage=int(context.get("cloudy_pixel_percentage", 80)),
                tile_scale=int(context.get("tile_scale", 4)),
            )
        except Exception as exc:
            report = _v03_failed_month_report(args, context, int(month), exc)
        else:
            report = _run_v03_month_preflight_with_retry(args, context, int(month), config)
        reports.append(report)
        month_ok = bool(report.get("ok"))
        checks.append({"month": int(month), "ok": month_ok})
        warnings.extend(report.get("warnings") or [])
        if not month_ok:
            errors.append(
                report.get("critical_error")
                or error_payload(
                    "V03_PREFLIGHT_MONTH_FAILED",
                    f"Anchor-month preflight failed for month {int(month)}.",
                )
            )

    ok = not errors
    return {
        "ok": ok,
        "decision": "allow_export" if ok else "block_export",
        "schema_version": plan.get("schema_version"),
        "plan_id": plan.get("plan_id"),
        "profile": "hk_2024_16day_ndvi_anchor_months",
        "template": template,
        "project": args.project,
        "aoi_name": context.get("aoi_name", "Hong Kong"),
        "aoi_source": context.get("aoi_source"),
        "dataset_id": context.get("dataset_id"),
        "date_start": context.get("date_start"),
        "date_end": context.get("date_end"),
        "temporal_cadence_days": int(context.get("temporal_cadence_days", 16)),
        "preflight_months": [int(month) for month in preflight_months],
        "monthly_reports": reports,
        "expected_export_rows": expected_rows,
        "export_description": context.get("export_description"),
        "drive_folder": context.get("drive_folder"),
        "file_prefix": context.get("file_prefix"),
        "critical_error": errors[0] if errors else None,
        "errors": errors,
        "warnings": warnings,
        "checks": {"anchor_months": checks},
    }


def _task_from_task_plan(task_plan: dict) -> dict:
    execution = dict(task_plan.get("execution") or {})
    interpreted = dict(task_plan.get("interpreted_intent") or {})
    return {
        "id": task_plan.get("task_id"),
        "intent": interpreted.get("name"),
        "task": execution.get("task") or interpreted.get("description"),
        "query": execution.get("query") or task_plan.get("raw_user_request"),
        "template": execution.get("template") or interpreted.get("template"),
        "context": dict(execution.get("context") or {}),
        "outputs": dict(execution.get("outputs") or {}),
        "output_schema": list(task_plan.get("output_schema") or []),
        "limitations": list(task_plan.get("limitations") or []),
        "version": task_plan.get("version"),
    }


def _write_plan_command_trace(
    args: argparse.Namespace,
    task_plan: dict,
    task: dict,
    *,
    plan_text: str,
    retrieval_trace: dict | None = None,
    rendered: str | None = None,
    validation: dict | None = None,
    dry_run: dict | None = None,
    preflight: dict | None = None,
    live_run: dict | None = None,
) -> RunTrace:
    trace = RunTrace.create(run_id=args.run_id)
    trace.write_yaml("task.yaml", task)
    trace.write_yaml("task_plan.yaml", task_plan)
    trace.write_json("retrieval_trace.json", retrieval_trace or {"query": task.get("query"), "evidence": [], "coverage": {}})
    trace.write_text("plan.md", plan_text)
    if rendered is not None:
        trace.write_text("generated_script.py", rendered)
    trace.write_json("validation_report.json", validation or {"ok": None, "findings": [], "status": "not_rendered"})
    trace.write_json("dry_run_report.json", dry_run or {"dry_run": False, "contacted_earth_engine": False, "status": "not_rendered"})
    if preflight is not None:
        trace.write_json("preflight_report.json", preflight)
        if preflight.get("landcover_diagnostics"):
            trace.write_json("landcover_diagnostics.json", preflight["landcover_diagnostics"])
    if live_run is not None:
        trace.write_json("live_run_report.json", live_run)
        if "tasks" in live_run:
            trace.write_json("export_tasks.json", live_run["tasks"])
    trace.write_final_report(
        "GEE Plan-First Run Trace",
        {
            "Task Plan": task_plan,
            "Validation": validation or "Not rendered.",
            "Dry Run": dry_run or "Not rendered.",
            "Preflight": preflight or "Not executed.",
            "Live Run": live_run or "Not executed.",
        },
    )
    return trace


def _plan_retrieval_trace(index_path: str, task: dict, top_k: int) -> dict:
    query = task.get("query") or task.get("task") or ""
    index = load_index(Path(index_path))
    results = _operator_aware_results(index, query, top_k=top_k)
    return build_retrieval_trace(query, results)


def cmd_review_plan(args: argparse.Namespace) -> int:
    try:
        task_plan, task, review, schema = _load_plan_for_command(Path(args.task_plan))
    except (FileNotFoundError, ValueError) as exc:
        return _print_error(str(exc))
    if args.json:
        key = "plan" if schema == "gee-plan/v0.3" else "task_plan"
        payload = {"ok": True, "schema_version": schema, key: task_plan, "task": task, "review": review}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(review)
    return 0


def cmd_preflight_plan(args: argparse.Namespace) -> int:
    if not args.project:
        return _print_error(
            "preflight-plan requires --project <google-cloud-project-id>.",
            as_json=args.json,
            code="PROJECT_ERROR",
            hint="Pass --project with a Google Cloud project that has Earth Engine access.",
            command="preflight-plan",
        )
    try:
        task_plan, task, plan_text, schema = _load_plan_for_command(Path(args.task_plan))
        preflight = (
            _preflight_from_v03_plan(args, task_plan, task["context"])
            if schema == "gee-plan/v0.3"
            else _preflight_from_v01_context(args, task["context"])
        )
        trace = _write_plan_command_trace(args, task_plan, task, plan_text=plan_text, preflight=preflight)
    except Exception as exc:
        return _print_harness_error(exc, as_json=args.json)
    command_name = getattr(args, "command_name", "preflight-plan")
    payload = {
        "ok": bool(preflight.get("ok")),
        "command": command_name,
        "schema_version": schema,
        "run_trace": str(trace.run_dir),
        "preflight": preflight,
    }
    _with_data(
        payload,
        {
            "plan_schema_version": schema,
            "run_trace": str(trace.run_dir),
            "preflight": preflight,
        },
    )
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Preflight {'passed' if preflight.get('ok') else 'blocked'}: {trace.run_dir}")
    return 0 if preflight.get("ok") else 1


def cmd_run_plan(args: argparse.Namespace) -> int:
    if not args.project:
        return _print_error(
            "run-plan requires --project <google-cloud-project-id>.",
            as_json=args.json,
            code="PROJECT_ERROR",
            hint="Pass --project with a Google Cloud project that has Earth Engine access.",
            command="run-plan",
        )
    if not args.confirm_live:
        return _print_error(
            "run-plan requires --confirm-live.",
            as_json=args.json,
            code="CONFIRM_LIVE_REQUIRED",
            hint="Review validation and preflight output, then rerun with --confirm-live only when you intend to submit an export.",
            command="run-plan",
        )
    try:
        task_plan, task, plan_text, schema = _load_plan_for_command(Path(args.task_plan))
        context = dict(task["context"])
        if args.export_folder:
            context["drive_folder"] = args.export_folder
        task["context"] = context
        _set_execution_context(task_plan, context)
        rendered = render_template(Path(args.templates_dir), task["template"], context)
        script_path = Path(task.get("outputs", {}).get("script") or "outputs/scripts/plan_script.py")
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(rendered, encoding="utf-8")
        validation = validate_script(script_path).to_dict()
        dry = dry_run_report(script_path, validation)
        preflight = None
        live = None
        retrieval = _plan_retrieval_trace(args.index, task, args.top_k)
        if not validation["ok"]:
            trace = _write_plan_command_trace(
                args,
                task_plan,
                task,
                plan_text=plan_text,
                retrieval_trace=retrieval,
                rendered=rendered,
                validation=validation,
                dry_run=dry,
            )
            payload = {
                "ok": False,
                "command": "run-plan",
                "schema_version": schema,
                "run_trace": str(trace.run_dir),
                "script": str(script_path),
                "validation": validation,
            }
            _with_data(
                payload,
                {
                    "plan_schema_version": schema,
                    "run_trace": str(trace.run_dir),
                    "script": str(script_path),
                    "validation": validation,
                },
            )
            print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "Validation failed; refusing live execution.")
            return 1
        preflight = (
            _preflight_from_v03_plan(args, task_plan, context)
            if schema == "gee-plan/v0.3"
            else _preflight_from_v01_context(args, context)
        )
        if not preflight.get("ok"):
            live = {
                "ok": False,
                "error": error_payload(
                    "EXPORT_REFUSED_BY_PREFLIGHT",
                    "run-plan refused to start export because preflight failed.",
                ),
            }
            trace = _write_plan_command_trace(
                args,
                task_plan,
                task,
                plan_text=plan_text,
                retrieval_trace=retrieval,
                rendered=rendered,
                validation=validation,
                dry_run=dry,
                preflight=preflight,
                live_run=live,
            )
            payload = {
                "ok": False,
                "command": "run-plan",
                "schema_version": schema,
                "run_trace": str(trace.run_dir),
                "script": str(script_path),
                "preflight": preflight,
                "error": preflight.get("critical_error") or live["error"],
            }
            _with_data(
                payload,
                {
                    "plan_schema_version": schema,
                    "run_trace": str(trace.run_dir),
                    "script": str(script_path),
                    "preflight": preflight,
                    "live_run": live,
                },
            )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 1
        result = execute_script(script_path, project=args.project, authenticate=args.authenticate)
        tasks = [_task_summary(task) for task in monitor_tasks(project=args.project, authenticate=False, timeout_seconds=0)]
        export_description = context.get("export_description")
        matching_tasks = [item for item in tasks if item.get("description") == export_description]
        failed = [item for item in matching_tasks if item.get("state") == "FAILED"]
        task_observed = bool(matching_tasks)
        live = {
            "ok": bool(_script_execution_ok(result) and task_observed and not failed),
            **result,
            "script_executed": _script_execution_ok(result),
            "export_task_observed": task_observed,
            "export_description": export_description,
            "tasks": tasks,
            "matching_tasks": matching_tasks,
        }
        if not task_observed:
            live["error"] = error_payload(
                "EXPORT_TASK_NOT_OBSERVED",
                f"Export task {export_description!r} was not observed after script execution.",
            )
        elif failed:
            live["error"] = error_payload(
                "EXPORT_TASK_FAILED",
                f"Export task {export_description!r} reached FAILED state immediately.",
            )
        trace = _write_plan_command_trace(
            args,
            task_plan,
            task,
            plan_text=plan_text,
            retrieval_trace=retrieval,
            rendered=rendered,
            validation=validation,
            dry_run=dry,
            preflight=preflight,
            live_run=live,
        )
        payload = {
            "ok": bool(live["ok"]),
            "command": "run-plan",
            "schema_version": schema,
            "run_trace": str(trace.run_dir),
            "script": str(script_path),
            "preflight": preflight,
            "live_run": live,
        }
        _with_data(
            payload,
            {
                "plan_schema_version": schema,
                "run_trace": str(trace.run_dir),
                "script": str(script_path),
                "preflight": preflight,
                "live_run": live,
            },
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if live["ok"] else 1
    except Exception as exc:
        return _print_harness_error(exc, as_json=args.json)


def cmd_ask(args: argparse.Namespace) -> int:
    modes = [bool(args.plan), bool(args.dry_run), bool(args.confirm_live)]
    if sum(1 for item in modes if item) > 1:
        return _print_error("Choose only one of --plan, --dry-run, or --confirm-live.", as_json=args.json, command="ask")
    if not any(modes):
        return _print_error("Use --plan, --dry-run, or --confirm-live.", as_json=args.json, command="ask")
    route = route_request(
        args.request,
        export_folder=args.export_folder,
        boundary_geojson=args.boundary_geojson,
    )
    if not route.get("ok"):
        if args.json:
            print(json.dumps(route, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(route.get("error"), indent=2, ensure_ascii=False))
        return 1
    if args.confirm_live and not args.project:
        payload = {
            "ok": False,
            "error": error_payload("PROJECT_ERROR", "Live ask requires --project <google-cloud-project-id>."),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else payload["error"]["message"])
        return 2

    task = dict(route["task"])
    if args.plan:
        try:
            trace, task_plan, _results, plan_body = _create_ask_trace_with_plan(args, task)
        except (TemplateContextError, ValueError, FileNotFoundError) as exc:
            return _print_error(str(exc))
        trace.write_json("validation_report.json", {"ok": None, "findings": [], "status": "not_rendered"})
        trace.write_json("dry_run_report.json", {"dry_run": False, "contacted_earth_engine": False, "status": "plan_only"})
        trace.write_final_report(
            "GEE Plan-First Run Trace",
            {
                "Task Plan": task_plan,
                "Plan": plan_body,
                "Status": "Plan only. No script rendering and no Earth Engine contact.",
            },
        )
        payload = {
            "ok": True,
            "mode": "plan",
            "route": route,
            "run_trace": str(trace.run_dir),
            "task_plan": str(trace.path("task_plan.yaml")),
            "plan": str(trace.path("plan.md")),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"Plan written: {trace.path('task_plan.yaml')}")
        return 0

    try:
        trace, script_path, validation, dry, context = _prepare_ask_artifacts(args, task)
    except (TemplateContextError, ValueError, FileNotFoundError) as exc:
        return _print_error(str(exc))

    if not validation["ok"]:
        _write_ask_final_report(trace, task=task, validation=validation, dry_run=dry)
        payload = {
            "ok": False,
            "mode": "dry-run" if args.dry_run else "live",
            "route": route,
            "script": str(script_path),
            "run_trace": str(trace.run_dir),
            "validation": validation,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "Validation failed; refusing execution.")
        return 1

    if args.dry_run:
        _write_ask_final_report(trace, task=task, validation=validation, dry_run=dry)
        payload = {
            "ok": True,
            "mode": "dry-run",
            "route": route,
            "script": str(script_path),
            "run_trace": str(trace.run_dir),
            "validation": validation,
            "dry_run": dry,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"Dry run OK: {script_path}")
        return 0

    try:
        preflight = _preflight_from_v01_context(args, context)
        trace.write_json("preflight_report.json", preflight)
        if preflight.get("landcover_diagnostics"):
            trace.write_json("landcover_diagnostics.json", preflight["landcover_diagnostics"])
        if not preflight.get("ok"):
            _write_ask_final_report(trace, task=task, validation=validation, dry_run=dry, preflight=preflight)
            payload = {
                "ok": False,
                "mode": "live",
                "route": route,
                "script": str(script_path),
                "run_trace": str(trace.run_dir),
                "preflight": preflight,
                "error": preflight.get("critical_error"),
            }
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 1
        result = execute_script(script_path, project=args.project, authenticate=args.authenticate)
        tasks = [_task_summary(task) for task in monitor_tasks(project=args.project, authenticate=False, timeout_seconds=0)]
        export_description = context["export_description"]
        matching_tasks = [task for task in tasks if task.get("description") == export_description]
        failed = [task for task in matching_tasks if task.get("state") == "FAILED"]
        task_observed = bool(matching_tasks)
        live = {
            "ok": bool(_script_execution_ok(result) and task_observed and not failed),
            **result,
            "script_executed": _script_execution_ok(result),
            "export_task_observed": task_observed,
            "export_description": export_description,
            "tasks": tasks,
            "matching_tasks": matching_tasks,
        }
        if not task_observed:
            live["error"] = error_payload(
                "EXPORT_TASK_NOT_OBSERVED",
                f"Export task {export_description!r} was not observed after script execution.",
            )
        elif failed:
            live["error"] = error_payload(
                "EXPORT_TASK_FAILED",
                f"Export task {export_description!r} reached FAILED state immediately.",
            )
        trace.write_json("live_run_report.json", live)
        trace.write_json("export_tasks.json", tasks)
        _write_ask_final_report(trace, task=task, validation=validation, dry_run=dry, preflight=preflight, live_run=live)
        payload = {
            "ok": bool(live["ok"]),
            "mode": "live",
            "route": route,
            "script": str(script_path),
            "run_trace": str(trace.run_dir),
            "preflight": preflight,
            "live_run": live,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if live["ok"] else 1
    except Exception as exc:
        payload = classify_exception(exc).to_dict()
        trace.write_json("live_run_report.json", {"ok": False, "error": payload})
        _write_ask_final_report(trace, task=task, validation=validation, dry_run=dry, live_run={"ok": False, "error": payload})
        print(json.dumps({"ok": False, "run_trace": str(trace.run_dir), "error": payload}, indent=2, ensure_ascii=False))
        return 2


def _write_plan_trace(
    args: argparse.Namespace,
    task: dict,
    task_text: str,
    template: str | None,
    context: dict | None,
    results,
    plan_body: str,
    rendered: str | None,
) -> RunTrace:
    trace = RunTrace.create(run_id=args.run_id)
    trace.write_yaml("task.yaml", task)
    trace.write_json("retrieval_trace.json", build_retrieval_trace(task.get("query") or task_text, results))
    trace.write_text("plan.md", plan_body)
    if rendered is not None:
        trace.write_text("generated_script.py", rendered)
        generated_path = trace.path("generated_script.py")
        validation = validate_script(generated_path).to_dict()
        trace.write_json("validation_report.json", validation)
        trace.write_json("dry_run_report.json", dry_run_report(generated_path, validation))
        trace.write_final_report(
            "GEE Workflow Run Trace",
            {
                "Task": task_text,
                "Template": template or "none",
                "Validation": validation,
                "Dry Run": "No Earth Engine contact. Script rendered and validated offline.",
            },
        )
    else:
        trace.write_json("validation_report.json", {"ok": None, "findings": []})
        trace.write_json("dry_run_report.json", {"dry_run": True, "contacted_earth_engine": False})
        trace.write_final_report(
            "GEE Workflow Run Trace",
            {"Task": task_text, "Template": template or "none", "Status": "Plan only."},
        )
    return trace


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        task, task_text, template, context = _load_plan_inputs(args)
        query = task.get("query") or task_text
        index = load_index(Path(args.index))
        results = _operator_aware_results(index, query, top_k=args.top_k)
        plan = build_plan(task_text, results, template=template)
        rendered = None
        if context is not None and (template or plan.template):
            rendered = render_template(Path(args.templates_dir), template or plan.template, context)
        trace = _write_plan_trace(args, task, task_text, template or plan.template, context, results, plan.body, rendered)

        out_path = Path(args.out or task.get("outputs", {}).get("plan") or trace.path("plan.md"))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(plan.body, encoding="utf-8")
        if rendered is not None:
            script_path = Path(args.script_out or task.get("outputs", {}).get("script") or trace.path("generated_script.py"))
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(rendered, encoding="utf-8")
            print(f"Wrote script: {script_path}")
        print(f"Wrote plan: {out_path}")
        print(f"Wrote run trace: {trace.run_dir}")
    except (TemplateContextError, ValueError, FileNotFoundError) as exc:
        return _print_error(str(exc))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    rules = [item.strip() for item in args.semantic_rules.split(",") if item.strip()] if args.semantic_rules else None
    script_path = Path(args.script)
    if not script_path.exists():
        payload = _file_not_found_payload(script_path, "validate")
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"error: {payload['error']['message']}", file=sys.stdout if args.json else sys.stderr)
        return 1
    report = validate_script(script_path, semantic_rulesets=rules)
    if args.json:
        print(
            json.dumps(
                _command_envelope(
                    "validate",
                    {
                        "script": str(args.script),
                        "validation": report.to_dict(),
                    },
                )
                | {"ok": report.ok},
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        for finding in report.findings:
            location = f":{finding.line}" if finding.line else ""
            category = f" [{finding.category}]" if finding.category else ""
            print(f"{finding.severity.upper()} {finding.code}{location}{category}: {finding.message}")
            if finding.hint:
                print(f"  hint: {finding.hint}")
    if not report.ok:
        return 1
    if args.fail_on_warning and any(item.severity == "warning" for item in report.findings):
        return 1
    return 0


def cmd_smoke_test(args: argparse.Namespace) -> int:
    root = project_root()
    index_path = Path(args.index)
    templates_dir = Path(args.templates_dir)
    context_path = default_context_path("hk_2024_monthly_ndvi.json")
    try:
        index = load_index(index_path)
        results = search(index, "Sentinel-2 NDVI cloud mask export table", top_k=3)
        if not results:
            return _print_error("Smoke retrieval returned no results.")
        context = load_context(context_path)
        rendered = render_template(templates_dir, "hk_district_monthly_ndvi", context)
        tmp = root / "outputs" / "smoke" / "hk_district_monthly_ndvi.py"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(rendered, encoding="utf-8")
        report = validate_script(tmp)
        payload = {
            "retrieval_results": len(results),
            "rendered_script": str(tmp),
            "validation": report.to_dict(),
        }
        if args.json:
            output = _command_envelope("smoke-test", payload)
            output["ok"] = bool(report.ok)
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"retrieval_results={len(results)}")
            print(f"rendered_script={tmp}")
            print(f"validation_ok={report.ok}")
        return 0 if report.ok else 1
    except Exception as exc:
        return _print_error(str(exc))


def _write_run_trace(script: Path, report: dict, live_payload: dict | None = None, run_id: str | None = None) -> RunTrace:
    trace = RunTrace.create(run_id=run_id)
    trace.write_yaml("task.yaml", {"task": f"Run script {script}", "script": str(script)})
    trace.copy_file(script, "generated_script.py")
    trace.write_json("retrieval_trace.json", {"query": None, "evidence": [], "coverage": {}})
    trace.write_text("plan.md", "Run invoked directly from an existing script; no plan was generated.")
    trace.write_json("validation_report.json", report)
    trace.write_json("dry_run_report.json", dry_run_report(script, report))
    if live_payload is not None:
        trace.write_json("live_run_report.json", live_payload)
        if "tasks" in live_payload:
            trace.write_json("export_tasks.json", live_payload["tasks"])
    trace.write_final_report(
        "GEE Script Run Trace",
        {
            "Script": str(script),
            "Validation": report,
            "Live Run": live_payload or "Not executed.",
        },
    )
    return trace


def cmd_run(args: argparse.Namespace) -> int:
    script = Path(args.script)
    if script.suffix.lower() in {".yaml", ".yml"}:
        return cmd_run_plan(
            argparse.Namespace(
                task_plan=args.script,
                project=args.project,
                confirm_live=args.confirm_live,
                authenticate=args.authenticate,
                export_folder=args.export_folder,
                index=args.index,
                top_k=args.top_k,
                templates_dir=args.templates_dir,
                run_id=args.run_id,
                json=args.json,
            )
        )
    if not script.exists():
        payload = _file_not_found_payload(script, "run")
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"error: {payload['error']['message']}", file=sys.stdout if args.json else sys.stderr)
        return 1
    report = validate_script(script).to_dict()
    if not report["ok"]:
        _write_run_trace(script, report, run_id=args.run_id)
        if args.json:
            payload = _command_envelope("run", {"script": str(script), "validation": report})
            payload["ok"] = False
            payload["error"] = {
                "code": "VALIDATION_FAILED",
                "message": "Validation failed; refusing to run.",
                "hint": "Inspect data.validation.findings, edit the script or plan, then validate again.",
            }
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("Validation failed; refusing to run.")
        return 1
    if args.dry_run:
        trace = _write_run_trace(script, report, run_id=args.run_id)
        payload = _command_envelope(
            "run",
            {"dry_run": True, "script": str(script), "validation": report, "run_trace": str(trace.run_dir)},
        )
        payload.update(payload["data"])
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"Dry run OK: {script}")
        return 0
    provided = set()
    if args.project:
        provided.add("--project")
    if args.confirm_live:
        provided.add("--confirm-live")
    try:
        require_flags("run_live", provided)
    except ValueError as exc:
        return _print_error(
            str(exc),
            as_json=args.json,
            code="CONFIRM_LIVE_REQUIRED" if "--confirm-live" in str(exc) else "PROJECT_ERROR",
            hint="Live execution requires both --project and --confirm-live after review, validation, and preflight.",
            command="run",
        )
    try:
        result = execute_script(script, project=args.project, authenticate=args.authenticate)
        tasks = monitor_tasks(project=args.project, authenticate=False, timeout_seconds=0)
        result["tasks"] = tasks
        if args.display_map:
            map_path = render_map_preview(
                script,
                object_name=args.map_object,
                out_html=Path(args.map_out),
                project=args.project,
                authenticate=False,
            )
            result["map_preview"] = str(map_path)
        trace = _write_run_trace(script, report, live_payload=result, run_id=args.run_id)
        result["run_trace"] = str(trace.run_dir)
    except (EarthEngineUnavailable, Exception) as exc:
        trace = _write_run_trace(script, report, live_payload={"ok": False, "error": classify_exception(exc).to_dict()}, run_id=args.run_id)
        if args.json:
            data = {"run_trace": str(trace.run_dir), "script": str(script)}
            payload = _command_envelope("run", data)
            payload["ok"] = False
            payload["error"] = classify_exception(exc).to_dict()
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 2
        return _print_harness_error(exc)
    if args.json:
        payload = _command_envelope("run", {"script": str(script), "live_run": result, "run_trace": result.get("run_trace")})
        payload["ok"] = bool(_script_execution_ok(result))
        payload.update(result)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Executed: {script}")
    return 0


def _task_summary(task: dict) -> dict:
    return {
        "id": task.get("id") or task.get("name"),
        "description": task.get("description"),
        "state": task.get("state"),
        "creation_time": task.get("creation_timestamp_ms") or task.get("creation_time"),
        "update_time": task.get("update_timestamp_ms") or task.get("update_time"),
        "error_message": task.get("error_message"),
    }


def cmd_monitor_exports(args: argparse.Namespace) -> int:
    if not args.project:
        return _print_error(
            "Monitoring live exports requires --project <google-cloud-project-id>.",
            as_json=args.json,
            code="PROJECT_ERROR",
            hint="Pass --project with a Google Cloud project that has Earth Engine access.",
            command="monitor-exports",
        )
    try:
        tasks = monitor_tasks(
            project=args.project,
            authenticate=args.authenticate,
            timeout_seconds=args.timeout,
            poll_seconds=args.poll_seconds,
        )
    except EarthEngineUnavailable as exc:
        if args.run_id:
            trace = RunTrace.create(run_id=args.run_id)
            trace.write_yaml(
                "task.yaml",
                {
                    "task": "Monitor Earth Engine export tasks",
                    "project": args.project,
                    "timeout": args.timeout,
                    "poll_seconds": args.poll_seconds,
                },
            )
            trace.write_json("retrieval_trace.json", {"query": None, "evidence": [], "coverage": {}})
            trace.write_text("plan.md", "Monitor existing Earth Engine batch export tasks for the configured project.")
            trace.write_json("live_run_report.json", {"ok": False, "error": classify_exception(exc).to_dict()})
            trace.write_final_report(
                "GEE Export Monitor Trace",
                {"Project": args.project, "Status": "Monitoring failed.", "Error": classify_exception(exc).to_dict()},
            )
        return _print_harness_error(exc, as_json=args.json)
    summaries = [_task_summary(task) for task in tasks]
    task_id = getattr(args, "task_id", None)
    if task_id:
        summaries = [task for task in summaries if task.get("id") == task_id]
    if args.run_id:
        trace = RunTrace.create(run_id=args.run_id)
        trace.write_yaml(
            "task.yaml",
            {
                "task": "Monitor Earth Engine export tasks",
                "project": args.project,
                "timeout": args.timeout,
                "poll_seconds": args.poll_seconds,
            },
        )
        trace.write_json("retrieval_trace.json", {"query": None, "evidence": [], "coverage": {}})
        trace.write_text("plan.md", "Monitor existing Earth Engine batch export tasks for the configured project.")
        trace.write_json("export_tasks.json", summaries)
        trace.write_final_report(
            "GEE Export Monitor Trace",
            {"Project": args.project, "Task Count": len(summaries), "Tasks": summaries},
        )
    if args.json:
        payload = {"tasks": summaries, "count": len(summaries)}
        if getattr(args, "envelope", False):
            print(json.dumps(_command_envelope("exports watch" if task_id else "exports list", payload), indent=2, ensure_ascii=False))
        else:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if not summaries:
            print("No Earth Engine tasks found.")
            return 0
        for task in summaries:
            line = f"{task.get('state', 'UNKNOWN'):10} {task.get('id') or ''} {task.get('description') or ''}"
            print(line)
            if task.get("error_message"):
                print(f"  error: {task['error_message']}")
    return 0


def _preflight_config_from_values(
    *,
    project: str | None,
    year: int,
    month: int,
    scope: str = "district",
    district: str | None = None,
    boundary_geojson: str | None = None,
    dataset_id: str = "COPERNICUS/S2_SR_HARMONIZED",
    district_property: str = "District",
    scale: int = 10,
    crs: str = "EPSG:4326",
    cloudy_pixel_percentage: int = 80,
    tile_scale: int = 4,
    landcover: str | None = None,
    landcover_dataset_id: str | None = None,
    landcover_strategy: str | None = None,
    dynamic_world_probability_threshold: float = 0.35,
) -> HKNDVIPreflightConfig:
    return HKNDVIPreflightConfig(
        project=project,
        year=year,
        month=month,
        scope=scope,
        district=district,
        dataset_id=dataset_id,
        boundary_geojson=boundary_geojson or str(default_boundary_path()),
        district_property=district_property,
        scale=scale,
        crs=crs,
        cloudy_pixel_percentage=cloudy_pixel_percentage,
        tile_scale=tile_scale,
        landcover=landcover,
        landcover_dataset_id=landcover_dataset_id,
        landcover_strategy=landcover_strategy,
        dynamic_world_probability_threshold=dynamic_world_probability_threshold,
    )


def _write_preflight_trace(trace: RunTrace, config: HKNDVIPreflightConfig, report: dict) -> None:
    trace.write_yaml(
        "task.yaml",
        {
            "task": "Preflight Hong Kong Sentinel-2 NDVI workflow",
            "year": config.year,
            "month": config.month,
            "scope": config.scope,
            "district": config.district,
            "dataset_id": config.dataset_id,
            "landcover": config.landcover,
            "landcover_dataset_id": config.landcover_dataset_id,
            "landcover_strategy": config.landcover_strategy,
            "dynamic_world_probability_threshold": config.dynamic_world_probability_threshold,
            "boundary_geojson": str(config.boundary_geojson),
            "district_property": config.district_property,
        },
    )
    trace.write_json("retrieval_trace.json", {"query": None, "evidence": [], "coverage": {}})
    trace.write_text(
        "plan.md",
        "Run safe Earth Engine probes for boundary, district, image, band, and sanity-stat availability before export.",
    )
    trace.write_json("preflight_report.json", report)
    if report.get("landcover_diagnostics"):
        trace.write_json("landcover_diagnostics.json", report["landcover_diagnostics"])
    trace.write_final_report(
        "HK NDVI Preflight Trace",
        {
            "Status": "Passed." if report.get("ok") else "Blocked before export.",
            "Preflight": report,
        },
    )


def cmd_preflight_hk_ndvi(args: argparse.Namespace) -> int:
    scope = args.scope or ("district" if args.district else "hong-kong")
    config = _preflight_config_from_values(
        project=args.project,
        year=args.year,
        month=args.month,
        scope=scope,
        district=args.district,
        boundary_geojson=args.boundary_geojson,
        scale=args.scale,
        crs=args.crs,
        cloudy_pixel_percentage=args.cloudy_pixel_percentage,
        landcover=args.landcover,
        landcover_dataset_id="GOOGLE/DYNAMICWORLD/V1" if args.landcover == "dynamic-world" else None,
        landcover_strategy="dynamic_world_time_matched_probability_masks" if args.landcover == "dynamic-world" else None,
        dynamic_world_probability_threshold=args.dynamic_world_probability_threshold,
    )
    trace = RunTrace.create(run_id=args.run_id)
    try:
        report = run_hk_ndvi_preflight(config)
    except Exception as exc:
        payload = classify_exception(exc).to_dict()
        report = {
            "ok": False,
            "decision": "block_export",
            "project": config.project,
            "year": config.year,
            "month": config.month,
            "scope": config.scope,
            "aoi_name": config.district or "Hong Kong",
            "aoi_source": str(config.boundary_geojson),
            "aoi_area_m2": None,
            "dataset_id": config.dataset_id,
            "image_count_before_cloud_filter": None,
            "image_count_after_cloud_filter": None,
            "band_names": [],
            "mean_ndvi_probe": None,
            "critical_error": payload,
            "errors": [payload],
            "warnings": [],
            "checks": {},
        }
    _write_preflight_trace(trace, config, report)
    payload = {"ok": bool(report.get("ok")), "run_trace": str(trace.run_dir), "preflight": report}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        status = "passed" if report.get("ok") else "blocked"
        print(f"Preflight {status}: {trace.run_dir}")
        if report.get("critical_error"):
            print(json.dumps(report["critical_error"], indent=2, ensure_ascii=False))
    return 0 if report.get("ok") else 1


def cmd_live_smoke_test(args: argparse.Namespace) -> int:
    for flag, value in {
        "--project": args.project,
        "--smoke-month": args.smoke_month,
        "--smoke-region": args.smoke_region,
        "--export-folder": args.export_folder,
    }.items():
        if not value:
            return _print_error(
                f"live-smoke-test requires {flag}.",
                as_json=args.json,
                code="USAGE_ERROR",
                hint="Provide all private live-smoke flags only when intentionally running a live smoke export.",
                command="live-smoke-test",
            )
    if not args.confirm_live:
        return _print_error(
            "live-smoke-test requires --confirm-live.",
            as_json=args.json,
            code="CONFIRM_LIVE_REQUIRED",
            hint="Review validation and preflight output, then rerun with --confirm-live only when you intend to submit the smoke export.",
            command="live-smoke-test",
        )
    task = load_task(default_task_path("hk_january_ndvi_smoke"))
    context = task_to_context(task)
    context["smoke_month"] = args.smoke_month
    context["smoke_region"] = args.smoke_region
    context["drive_folder"] = args.export_folder
    context["export_description"] = args.export_description or f"hk_2024_{args.smoke_month:02d}_ndvi_smoke"
    context["file_prefix"] = context["export_description"]
    boundary_path = Path(args.boundary_geojson) if args.boundary_geojson else default_boundary_path()
    context["boundary_geojson"] = boundary_path.as_posix()
    context["district_property"] = "District"
    trace = RunTrace.create(run_id=args.run_id)
    trace.write_yaml("task.yaml", {**task, "context": context})
    try:
        index = load_index(Path(args.index))
        results = _operator_aware_results(index, task.get("query") or task["task"], top_k=5)
        trace.write_json("retrieval_trace.json", build_retrieval_trace(task.get("query") or task["task"], results))
        plan = build_plan(task["task"], results, template=task["template"])
        trace.write_text("plan.md", plan.body)
        rendered = render_template(Path(args.templates_dir), task["template"], context)
        script_path = trace.write_text("generated_script.py", rendered)
        validation = validate_script(script_path).to_dict()
        trace.write_json("validation_report.json", validation)
        trace.write_json("dry_run_report.json", dry_run_report(script_path, validation))
        if not validation["ok"]:
            trace.write_final_report("Live Smoke Test", {"Status": "Blocked by validation.", "Validation": validation})
            print(json.dumps({"ok": False, "run_trace": str(trace.run_dir), "validation": validation}, indent=2, ensure_ascii=False))
            return 1
        preflight_config = _preflight_config_from_values(
            project=args.project,
            year=int(context["year"]),
            month=int(context["smoke_month"]),
            scope="district",
            district=str(context["smoke_region"]),
            boundary_geojson=context["boundary_geojson"],
            dataset_id=str(context["dataset_id"]),
            district_property=str(context["district_property"]),
            scale=int(context["scale"]),
            crs=str(context["crs"]),
            cloudy_pixel_percentage=int(context["cloudy_pixel_percentage"]),
            tile_scale=int(context["tile_scale"]),
        )
        preflight = run_hk_ndvi_preflight(preflight_config)
        trace.write_json("preflight_report.json", preflight)
        if not preflight.get("ok"):
            trace.write_final_report(
                "Live Smoke Test",
                {"Status": "Blocked by live preflight before export.", "Preflight": preflight},
            )
            print(
                json.dumps(
                    {
                        "ok": False,
                        "run_trace": str(trace.run_dir),
                        "preflight": preflight,
                        "error": preflight.get("critical_error"),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 1
        result = execute_script(script_path, project=args.project, authenticate=args.authenticate)
        tasks = [_task_summary(task) for task in monitor_tasks(project=args.project, authenticate=False, timeout_seconds=0)]
        export_description = context["export_description"]
        matching_tasks = [task for task in tasks if task.get("description") == export_description]
        failed = [task for task in matching_tasks if task.get("state") == "FAILED"]
        task_observed = bool(matching_tasks)
        live = {
            "ok": bool(_script_execution_ok(result) and task_observed and not failed),
            **result,
            "script_executed": _script_execution_ok(result),
            "export_task_observed": task_observed,
            "export_description": export_description,
            "tasks": tasks,
            "matching_tasks": matching_tasks,
        }
        if not task_observed:
            live["error"] = error_payload(
                "EXPORT_TASK_NOT_OBSERVED",
                f"Export task {export_description!r} was not observed after script execution.",
            )
        elif failed:
            live["error"] = error_payload(
                "EXPORT_TASK_FAILED",
                f"Export task {export_description!r} reached FAILED state immediately.",
            )
        trace.write_json("live_run_report.json", live)
        trace.write_json("export_tasks.json", live["tasks"])
        trace.write_final_report(
            "Live Smoke Test",
            {
                "Status": "Live export task observed." if live["ok"] else "Live export task was not confirmed.",
                "Live Run": live,
            },
        )
        print(json.dumps({"ok": bool(live["ok"]), "run_trace": str(trace.run_dir), "live_run": live}, indent=2, ensure_ascii=False))
        return 0 if live["ok"] else 1
    except Exception as exc:
        payload = classify_exception(exc).to_dict()
        trace.write_json("live_run_report.json", {"ok": False, "error": payload})
        trace.write_final_report("Live Smoke Test", {"Status": "Failed gracefully.", "Error": payload})
        print(json.dumps({"ok": False, "run_trace": str(trace.run_dir), "error": payload}, indent=2, ensure_ascii=False))
        return 2


def cmd_evaluate(args: argparse.Namespace) -> int:
    try:
        result = run_benchmark_suite(Path(args.suite))
    except Exception as exc:
        return _print_error(str(exc))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


def cmd_eval(args: argparse.Namespace) -> int:
    try:
        result = run_benchmark_suite(Path(args.suite))
    except Exception as exc:
        payload = _envelope_error("EVAL_FAILED", str(exc), "Check the benchmark suite path and task definitions.")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    payload = _command_envelope("eval", result)
    payload["ok"] = bool(result.get("ok"))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    root = project_root()
    parser = argparse.ArgumentParser(prog="gee-skill")
    parser.add_argument("--version", action="version", version=f"gee-agent-skill {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    info_parser = sub.add_parser("info", help="Show agent-facing harness metadata.")
    info_parser.add_argument("--json", action="store_true")
    info_parser.set_defaults(func=cmd_info)

    doctor_parser = sub.add_parser("doctor", help="Check local harness resources without printing credentials.")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.set_defaults(func=cmd_doctor)

    auth_parser = sub.add_parser("auth", help="Earth Engine authentication helpers.")
    auth_sub = auth_parser.add_subparsers(dest="auth_command", required=True)
    auth_check = auth_sub.add_parser("check", help="Check Earth Engine API availability or project initialization.")
    auth_check.add_argument("--project")
    auth_check.add_argument("--use-discovered-project", action="store_true")
    auth_check.add_argument("--json", action="store_true")
    auth_check.set_defaults(func=cmd_auth_check)

    aoi_parser = sub.add_parser("aoi", help="Resolve, validate, or summarize AOI inputs without live export.")
    aoi_sub = aoi_parser.add_subparsers(dest="aoi_command", required=True)
    aoi_resolve = aoi_sub.add_parser("resolve", help="Resolve an AOI from natural language, GeoJSON, or plan YAML.")
    aoi_resolve.add_argument("source")
    aoi_resolve.add_argument("--json", action="store_true")
    aoi_resolve.set_defaults(func=cmd_aoi_resolve)
    aoi_validate = aoi_sub.add_parser("validate", help="Validate an AOI source enough for plan review.")
    aoi_validate.add_argument("source")
    aoi_validate.add_argument("--json", action="store_true")
    aoi_validate.set_defaults(func=cmd_aoi_validate)
    aoi_summarize = aoi_sub.add_parser("summarize", help="Summarize an AOI source.")
    aoi_summarize.add_argument("source")
    aoi_summarize.add_argument("--json", action="store_true")
    aoi_summarize.set_defaults(func=cmd_aoi_summarize)

    catalog_parser = sub.add_parser("catalog", help="Inspect and recommend distilled Earth Engine dataset cards.")
    catalog_sub = catalog_parser.add_subparsers(dest="catalog_command", required=True)
    catalog_search = catalog_sub.add_parser("search", help="Search dataset cards.")
    catalog_search.add_argument("query")
    catalog_search.add_argument("--top-k", type=int, default=10)
    catalog_search.add_argument("--json", action="store_true")
    catalog_search.set_defaults(func=cmd_catalog_search)
    catalog_show = catalog_sub.add_parser("show", help="Show a dataset card.")
    catalog_show.add_argument("dataset_id")
    catalog_show.add_argument("--json", action="store_true")
    catalog_show.set_defaults(func=cmd_catalog_show)
    catalog_recommend = catalog_sub.add_parser("recommend", help="Recommend datasets for a task or metric.")
    catalog_recommend.add_argument("--task-type")
    catalog_recommend.add_argument("--metric")
    catalog_recommend.add_argument("--json", action="store_true")
    catalog_recommend.set_defaults(func=cmd_catalog_recommend)
    catalog_evidence = catalog_sub.add_parser("evidence", help="List indexed dataset/operator/recipe/failure knowledge cards.")
    catalog_evidence.add_argument(
        "--category",
        choices=[
            "all",
            "dataset",
            "datasets",
            "operator",
            "operators",
            "recipe",
            "recipes",
            "failure",
            "failures",
            "research",
            "general",
        ],
        default="all",
    )
    catalog_evidence.add_argument("--top-k", type=int, default=50)
    catalog_evidence.add_argument("--index", default=str(default_index_path(root)))
    catalog_evidence.add_argument("--json", action="store_true")
    catalog_evidence.set_defaults(func=cmd_catalog_evidence)

    recipe_parser = sub.add_parser("recipe", help="Inspect GEE workflow recipes.")
    recipe_sub = recipe_parser.add_subparsers(dest="recipe_command", required=True)
    recipe_list = recipe_sub.add_parser("list", help="List recipes.")
    recipe_list.add_argument("--json", action="store_true")
    recipe_list.set_defaults(func=cmd_recipe_list)
    recipe_show = recipe_sub.add_parser("show", help="Show a recipe.")
    recipe_show.add_argument("recipe_id")
    recipe_show.add_argument("--json", action="store_true")
    recipe_show.set_defaults(func=cmd_recipe_show)

    rules_parser = sub.add_parser("rules", help="Inspect validation rulesets.")
    rules_sub = rules_parser.add_subparsers(dest="rules_command", required=True)
    rules_list = rules_sub.add_parser("list", help="List rulesets.")
    rules_list.add_argument("--json", action="store_true")
    rules_list.set_defaults(func=cmd_rules_list)
    rules_show = rules_sub.add_parser("show", help="Show a ruleset.")
    rules_show.add_argument("ruleset_id")
    rules_show.add_argument("--json", action="store_true")
    rules_show.set_defaults(func=cmd_rules_show)

    tools_parser = sub.add_parser("tools", help="List installed and exposed harness tools.")
    tools_parser.add_argument("--json", action="store_true")
    tools_parser.set_defaults(func=cmd_tools)

    observe_parser = sub.add_parser("observe", help="Explain a natural-language GEE request and suggest next CLI steps.")
    observe_parser.add_argument("request")
    observe_parser.add_argument("--json", action="store_true")
    observe_parser.set_defaults(func=cmd_observe)

    search_parser = sub.add_parser("search-docs", help="Search the local Earth Engine docs index.")
    search_parser.add_argument("query")
    search_parser.add_argument("--index", default=str(default_index_path(root)))
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(func=cmd_search_docs)

    ask_parser = sub.add_parser("ask", help="Route a natural-language GEE task through the v0.1 harness.")
    ask_parser.add_argument("request")
    ask_parser.add_argument("--project")
    ask_parser.add_argument("--plan", action="store_true")
    ask_parser.add_argument("--dry-run", action="store_true")
    ask_parser.add_argument("--confirm-live", action="store_true")
    ask_parser.add_argument("--run-id")
    ask_parser.add_argument("--json", action="store_true")
    ask_parser.add_argument("--authenticate", action="store_true")
    ask_parser.add_argument("--index", default=str(default_index_path(root)))
    ask_parser.add_argument("--top-k", type=int, default=8)
    ask_parser.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    ask_parser.add_argument("--export-folder", default="gee_exports")
    ask_parser.add_argument("--boundary-geojson")
    ask_parser.set_defaults(func=cmd_ask)

    plan_parser = sub.add_parser("plan", help="Create a cited Earth Engine workflow plan and run trace.")
    plan_parser.add_argument("task_file", nargs="?")
    plan_parser.add_argument("--task")
    plan_parser.add_argument("--index", default=str(default_index_path(root)))
    plan_parser.add_argument("--top-k", type=int, default=5)
    plan_parser.add_argument("--template")
    plan_parser.add_argument("--context")
    plan_parser.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    plan_parser.add_argument("--out")
    plan_parser.add_argument("--script-out")
    plan_parser.add_argument("--run-id")
    plan_parser.set_defaults(func=cmd_plan)

    render_parser = sub.add_parser("render", help="Render a reviewable plan into an Earth Engine Python script.")
    render_parser.add_argument("plan")
    render_parser.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    render_parser.add_argument("--script-out")
    render_parser.add_argument("--json", action="store_true")
    render_parser.set_defaults(func=cmd_render)

    review_plan = sub.add_parser("review-plan", help="Review a saved task_plan.yaml without Earth Engine contact.")
    review_plan.add_argument("task_plan")
    review_plan.add_argument("--json", action="store_true")
    review_plan.set_defaults(func=cmd_review_plan)

    preflight_plan = sub.add_parser("preflight-plan", help="Run safe live checks for a saved task_plan.yaml.")
    preflight_plan.add_argument("task_plan")
    preflight_plan.add_argument("--project")
    preflight_plan.add_argument("--run-id")
    preflight_plan.add_argument("--json", action="store_true")
    preflight_plan.set_defaults(func=cmd_preflight_plan)

    preflight_generic = sub.add_parser("preflight", help="Run safe live checks for a saved plan YAML without starting an export.")
    preflight_generic.add_argument("plan")
    preflight_generic.add_argument("--project")
    preflight_generic.add_argument("--run-id")
    preflight_generic.add_argument("--json", action="store_true")
    preflight_generic.set_defaults(func=cmd_preflight)

    run_plan = sub.add_parser("run-plan", help="Render, validate, preflight, and run a confirmed task_plan.yaml.")
    run_plan.add_argument("task_plan")
    run_plan.add_argument("--project")
    run_plan.add_argument("--confirm-live", action="store_true")
    run_plan.add_argument("--authenticate", action="store_true")
    run_plan.add_argument("--export-folder")
    run_plan.add_argument("--index", default=str(default_index_path(root)))
    run_plan.add_argument("--top-k", type=int, default=8)
    run_plan.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    run_plan.add_argument("--run-id")
    run_plan.add_argument("--json", action="store_true")
    run_plan.set_defaults(func=cmd_run_plan)

    validate_parser = sub.add_parser("validate", help="Validate a rendered Earth Engine Python script.")
    validate_parser.add_argument("script")
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("--fail-on-warning", action="store_true")
    validate_parser.add_argument("--semantic-rules")
    validate_parser.set_defaults(func=cmd_validate)

    smoke_parser = sub.add_parser("smoke-test", help="Run offline retrieval/render/validation checks.")
    smoke_parser.add_argument("--index", default=str(default_index_path(root)))
    smoke_parser.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    smoke_parser.add_argument("--json", action="store_true")
    smoke_parser.set_defaults(func=cmd_smoke_test)

    run_parser = sub.add_parser("run", help="Validate and execute an Earth Engine Python script.")
    run_parser.add_argument("script")
    run_parser.add_argument("--project")
    run_parser.add_argument("--authenticate", action="store_true")
    run_parser.add_argument("--dry-run", action="store_true")
    run_parser.add_argument("--confirm-live", action="store_true")
    run_parser.add_argument("--display-map", action="store_true")
    run_parser.add_argument("--map-object", default="build_composite")
    run_parser.add_argument("--map-out", default="outputs/maps/gee_preview.html")
    run_parser.add_argument("--export-folder")
    run_parser.add_argument("--index", default=str(default_index_path(root)))
    run_parser.add_argument("--top-k", type=int, default=8)
    run_parser.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    run_parser.add_argument("--run-id")
    run_parser.add_argument("--json", action="store_true")
    run_parser.set_defaults(func=cmd_run)

    monitor_parser = sub.add_parser("monitor-exports", help="Monitor Earth Engine export tasks.")
    monitor_parser.add_argument("--project")
    monitor_parser.add_argument("--authenticate", action="store_true")
    monitor_parser.add_argument("--timeout", type=int, default=0)
    monitor_parser.add_argument("--poll-seconds", type=int, default=15)
    monitor_parser.add_argument("--run-id")
    monitor_parser.add_argument("--json", action="store_true")
    monitor_parser.set_defaults(func=cmd_monitor_exports)

    exports_parser = sub.add_parser("exports", help="Inspect Earth Engine export tasks.")
    exports_sub = exports_parser.add_subparsers(dest="exports_command", required=True)
    exports_list = exports_sub.add_parser("list", help="List Earth Engine export tasks.")
    exports_list.add_argument("--project", required=True)
    exports_list.add_argument("--authenticate", action="store_true")
    exports_list.add_argument("--timeout", type=int, default=0)
    exports_list.add_argument("--poll-seconds", type=int, default=15)
    exports_list.add_argument("--run-id")
    exports_list.add_argument("--json", action="store_true")
    exports_list.set_defaults(func=cmd_monitor_exports, envelope=True, task_id=None)
    exports_watch = exports_sub.add_parser("watch", help="Watch Earth Engine export tasks.")
    exports_watch.add_argument("--project", required=True)
    exports_watch.add_argument("--task-id")
    exports_watch.add_argument("--authenticate", action="store_true")
    exports_watch.add_argument("--timeout", type=int, default=300)
    exports_watch.add_argument("--poll-seconds", type=int, default=15)
    exports_watch.add_argument("--run-id")
    exports_watch.add_argument("--json", action="store_true")
    exports_watch.set_defaults(func=cmd_monitor_exports, envelope=True)

    trace_parser = sub.add_parser("trace", help="Inspect run trace artifacts.")
    trace_sub = trace_parser.add_subparsers(dest="trace_command", required=True)
    trace_list = trace_sub.add_parser("list", help="List local run traces.")
    trace_list.add_argument("--limit", type=int, default=20)
    trace_list.add_argument("--json", action="store_true")
    trace_list.set_defaults(func=cmd_trace_list)
    trace_inspect = trace_sub.add_parser("inspect", help="Inspect one run trace by run id or directory path.")
    trace_inspect.add_argument("run_id")
    trace_inspect.add_argument("--json", action="store_true")
    trace_inspect.set_defaults(func=cmd_trace_inspect)

    corpus_parser = sub.add_parser("corpus", help="Inspect RAG evidence coverage.")
    corpus_sub = corpus_parser.add_subparsers(dest="corpus_command", required=True)
    corpus_coverage = corpus_sub.add_parser("coverage", help="Check evidence coverage for a task family.")
    corpus_coverage.add_argument("--task-type")
    corpus_coverage.add_argument("--metric")
    corpus_coverage.add_argument("--output")
    corpus_coverage.add_argument("--query")
    corpus_coverage.add_argument("--index", default=str(default_index_path(root)))
    corpus_coverage.add_argument("--top-k", type=int, default=8)
    corpus_coverage.add_argument("--json", action="store_true")
    corpus_coverage.set_defaults(func=cmd_corpus_coverage)

    preflight = sub.add_parser("preflight-hk-ndvi", help="Preflight Hong Kong Sentinel-2 NDVI before export.")
    preflight.add_argument("--project", required=True)
    preflight.add_argument("--year", type=int, required=True)
    preflight.add_argument("--month", type=int, required=True)
    preflight.add_argument("--scope", choices=["hong-kong", "district"])
    preflight.add_argument("--district")
    preflight.add_argument("--boundary-geojson")
    preflight.add_argument("--scale", type=int, default=10)
    preflight.add_argument("--crs", default="EPSG:4326")
    preflight.add_argument("--cloudy-pixel-percentage", type=int, default=80)
    preflight.add_argument("--landcover", choices=["dynamic-world"])
    preflight.add_argument("--dynamic-world-probability-threshold", type=float, default=0.35)
    preflight.add_argument("--run-id")
    preflight.add_argument("--json", action="store_true")
    preflight.set_defaults(func=cmd_preflight_hk_ndvi)

    live_smoke = sub.add_parser("live-smoke-test", help="Run the private Hong Kong one-district live smoke export.")
    live_smoke.add_argument("--project", required=True)
    live_smoke.add_argument("--confirm-live", action="store_true")
    live_smoke.add_argument("--smoke-month", type=int, required=True)
    live_smoke.add_argument("--smoke-region", required=True)
    live_smoke.add_argument("--export-folder", required=True)
    live_smoke.add_argument("--export-description")
    live_smoke.add_argument("--authenticate", action="store_true")
    live_smoke.add_argument("--index", default=str(default_index_path(root)))
    live_smoke.add_argument("--templates-dir", default=str(default_templates_dir(root)))
    live_smoke.add_argument("--boundary-geojson")
    live_smoke.add_argument("--run-id")
    live_smoke.add_argument("--json", action="store_true")
    live_smoke.set_defaults(func=cmd_live_smoke_test)

    eval_parser = sub.add_parser("evaluate", help="Run offline benchmark suite.")
    eval_parser.add_argument("suite")
    eval_parser.add_argument("--out")
    eval_parser.set_defaults(func=cmd_evaluate)

    eval_alias = sub.add_parser("eval", help="Run offline benchmark suite with agent-facing JSON envelope.")
    eval_alias.add_argument("suite")
    eval_alias.add_argument("--out")
    eval_alias.add_argument("--json", action="store_true")
    eval_alias.set_defaults(func=cmd_eval)
    return parser


def build_plan_action_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gee-skill plan")
    sub = parser.add_subparsers(dest="plan_command", required=True)

    from_text = sub.add_parser("from-text", help="Create a generic reviewable GEE plan from natural language.")
    from_text.add_argument("request")
    from_text.add_argument("--out")
    from_text.add_argument("--json", action="store_true")
    from_text.set_defaults(func=cmd_plan_from_text)

    from_yaml = sub.add_parser("from-yaml", help="Create/review a plan from task YAML.")
    from_yaml.add_argument("path")
    from_yaml.add_argument("--templates-dir", default=str(default_templates_dir(project_root())))
    from_yaml.add_argument("--script-out")
    from_yaml.add_argument("--json", action="store_true")
    from_yaml.set_defaults(func=cmd_plan_from_yaml)

    review = sub.add_parser("review", help="Review a saved task plan.")
    review.add_argument("path")
    review.add_argument("--json", action="store_true")
    review.set_defaults(func=cmd_plan_review_v03)

    set_cmd = sub.add_parser("set", help="Set a dotted key in an editable plan YAML.")
    set_cmd.add_argument("path")
    set_cmd.add_argument("key")
    set_cmd.add_argument("value")
    set_cmd.add_argument("--json", action="store_true")
    set_cmd.set_defaults(func=cmd_plan_set)
    return parser


def main(argv: list[str] | None = None) -> int:
    raw = sys.argv[1:] if argv is None else argv
    if len(raw) >= 2 and raw[0] == "plan" and raw[1] in {"from-text", "from-yaml", "review", "set"}:
        args = build_plan_action_parser().parse_args(raw[1:])
        return int(args.func(args))
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
