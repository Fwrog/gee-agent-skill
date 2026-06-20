from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import default_index_path, default_templates_dir
from .rag import load_index, search
from .semantic import validate_semantics
from .templates import load_context, render_template
from .validation import validate_script


def run_benchmark_suite(path: Path) -> dict[str, Any]:
    suite = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(suite, dict):
        raise ValueError(f"Benchmark suite must be a mapping: {path}")
    index = load_index(Path(suite.get("index", default_index_path())))
    templates_dir = Path(suite.get("templates_dir", default_templates_dir()))
    results = []
    for task in suite.get("tasks", []):
        kind = task.get("kind")
        status = "passed"
        details: dict[str, Any] = {}
        try:
            if kind == "retrieval":
                hits = search(index, task["query"], top_k=int(task.get("top_k", 3)))
                details["hits"] = [hit.source_path for hit in hits]
                expected = task.get("expected_source_contains")
                if expected and not any(expected in hit.source_path for hit in hits):
                    status = "failed"
            elif kind == "render_validate":
                context = load_context(Path(task["context"]))
                if "context" in context and isinstance(context["context"], dict):
                    context = context["context"]
                rendered = render_template(templates_dir, task["template"], context)
                out = Path("outputs/evals") / f"{task['id']}.py"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(rendered, encoding="utf-8")
                report = validate_script(out)
                semantic = [item.__dict__ for item in validate_semantics(out)]
                details = {"script": str(out), "validation": report.to_dict(), "semantic": semantic}
                if not report.ok or any(item["severity"] == "error" for item in semantic):
                    status = "failed"
            elif kind == "expected_failure":
                report = validate_script(Path(task["script"]))
                details["validation"] = report.to_dict()
                expected_code = task.get("expected_code")
                if report.ok or (
                    expected_code
                    and not any(item.code == expected_code for item in report.findings)
                ):
                    status = "failed"
            else:
                status = "failed"
                details["error"] = f"Unknown benchmark kind: {kind}"
        except Exception as exc:
            status = "failed"
            details["error"] = str(exc)
        results.append({"id": task.get("id"), "kind": kind, "status": status, "details": details})
    return {
        "suite": suite.get("id", path.stem),
        "ok": all(item["status"] == "passed" for item in results),
        "results": results,
    }
