from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .earthengine import EarthEngineUnavailable, execute_script, monitor_tasks, render_map_preview
from .errors import classify_exception, error_payload
from .evaluation import run_benchmark_suite
from .paths import default_context_path, default_index_path, default_task_path, default_templates_dir, project_root
from .planner import build_plan
from .rag import load_index, results_to_dicts, search
from .retrieval_trace import build_retrieval_trace
from .run_trace import RunTrace, dry_run_report
from .task import load_task, task_to_context
from .templates import TemplateContextError, load_context, render_template
from .tool_registry import exposed_tools, installed_tools, require_flags
from .validation import report_to_json, validate_script


def _print_error(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def _print_harness_error(exc: Exception, as_json: bool = False) -> int:
    payload = classify_exception(exc).to_dict()
    if as_json:
        print(json.dumps({"ok": False, "error": payload}, indent=2, ensure_ascii=False))
    else:
        print(f"error: [{payload['category']}] {payload['message']}", file=sys.stderr)
        print(f"hint: {payload['suggested_fix']}", file=sys.stderr)
    return 2


def cmd_tools(args: argparse.Namespace) -> int:
    payload = {
        "installed_tools": installed_tools(),
        "exposed_tools": exposed_tools(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_search_docs(args: argparse.Namespace) -> int:
    try:
        index = load_index(Path(args.index))
        results = search(index, args.query, top_k=args.top_k)
    except Exception as exc:
        return _print_error(str(exc))
    if args.json:
        print(json.dumps({"query": args.query, "results": results_to_dicts(results)}, indent=2))
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
    supplements = search(
        index,
        "known failure cases Earth Engine AUTH_ERROR EMPTY_COLLECTION "
        "EXPORT_TASK_ERROR CLIENT_SERVER_MISUSE recovery",
        top_k=3,
    )
    by_chunk = {item.chunk_id: item for item in results}
    for item in supplements:
        if "failure" in item.source_path.lower() or "error" in item.title.lower():
            by_chunk.setdefault(item.chunk_id, item)
    return list(by_chunk.values())


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
    report = validate_script(Path(args.script), semantic_rulesets=rules)
    if args.json:
        print(report_to_json(report))
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
            print(json.dumps(payload, indent=2))
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
    report = validate_script(script).to_dict()
    if not report["ok"]:
        _write_run_trace(script, report, run_id=args.run_id)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else "Validation failed; refusing to run.")
        return 1
    if args.dry_run:
        trace = _write_run_trace(script, report, run_id=args.run_id)
        payload = {"dry_run": True, "script": str(script), "validation": report, "run_trace": str(trace.run_dir)}
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
        return _print_error(str(exc))
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
            print(json.dumps({"ok": False, "run_trace": str(trace.run_dir), "error": classify_exception(exc).to_dict()}, indent=2, ensure_ascii=False))
            return 2
        return _print_harness_error(exc)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else f"Executed: {script}")
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
        return _print_error("Monitoring live exports requires --project <google-cloud-project-id>.")
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
        print(json.dumps({"tasks": summaries, "count": len(summaries)}, indent=2, ensure_ascii=False))
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


def cmd_live_smoke_test(args: argparse.Namespace) -> int:
    for flag, value in {
        "--project": args.project,
        "--smoke-month": args.smoke_month,
        "--smoke-region": args.smoke_region,
        "--export-folder": args.export_folder,
    }.items():
        if not value:
            return _print_error(f"live-smoke-test requires {flag}.")
    if not args.confirm_live:
        return _print_error("live-smoke-test requires --confirm-live.")
    task = load_task(default_task_path("hk_january_ndvi_smoke"))
    context = task_to_context(task)
    context["smoke_month"] = args.smoke_month
    context["smoke_region"] = args.smoke_region
    context["drive_folder"] = args.export_folder
    context["export_description"] = args.export_description or f"hk_2024_{args.smoke_month:02d}_ndvi_smoke"
    context["file_prefix"] = context["export_description"]
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
        result = execute_script(script_path, project=args.project, authenticate=args.authenticate)
        tasks = monitor_tasks(project=args.project, authenticate=False, timeout_seconds=0)
        live = {"ok": True, **result, "tasks": [_task_summary(task) for task in tasks]}
        trace.write_json("live_run_report.json", live)
        trace.write_json("export_tasks.json", live["tasks"])
        trace.write_final_report("Live Smoke Test", {"Status": "Live export task requested.", "Live Run": live})
        print(json.dumps({"ok": True, "run_trace": str(trace.run_dir), "live_run": live}, indent=2, ensure_ascii=False))
        return 0
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


def build_parser() -> argparse.ArgumentParser:
    root = project_root()
    parser = argparse.ArgumentParser(prog="gee-skill")
    parser.add_argument("--version", action="version", version="gee-agent-skill 0.2.0")
    sub = parser.add_subparsers(dest="command", required=True)

    tools_parser = sub.add_parser("tools", help="List installed and exposed harness tools.")
    tools_parser.set_defaults(func=cmd_tools)

    search_parser = sub.add_parser("search-docs", help="Search the local Earth Engine docs index.")
    search_parser.add_argument("query")
    search_parser.add_argument("--index", default=str(default_index_path(root)))
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(func=cmd_search_docs)

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
    live_smoke.add_argument("--run-id")
    live_smoke.set_defaults(func=cmd_live_smoke_test)

    eval_parser = sub.add_parser("evaluate", help="Run offline benchmark suite.")
    eval_parser.add_argument("suite")
    eval_parser.add_argument("--out")
    eval_parser.set_defaults(func=cmd_evaluate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
