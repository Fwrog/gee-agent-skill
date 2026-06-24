from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import default_index_path, default_templates_dir
from .generic_preflight import GenericV03PreflightConfig
from . import generic_preflight as generic_preflight_module
from .intents import build_general_plan_from_text
from .rag import load_index, search
from .retrieval_trace import build_retrieval_trace
from .semantic import validate_semantics
from .templates import load_context, render_template
from .validation import validate_script


def _coverage_search(index: dict[str, Any], query: str, required: dict[str, Any], top_k: int) -> tuple[list[Any], dict[str, Any]]:
    hits = search(index, query, top_k=top_k)
    trace = build_retrieval_trace(query, hits)
    missing = {
        key
        for key, expected in required.items()
        if int((trace.get("coverage") or {}).get(key, 0)) < int(expected)
    }
    lower_query = query.lower()
    dataset_query = f"{query} dataset data catalog bands temporal coverage"
    if any(term in lower_query for term in ("ndvi", "ndwi", "mndwi", "ndbi", "sentinel-2", "sentinel 2")):
        dataset_query = "COPERNICUS/S2_SR_HARMONIZED Sentinel-2 SR Harmonized dataset bands SCL QA"
    elif "landsat" in lower_query or "lst" in lower_query:
        dataset_query = "LANDSAT/LC08/C02/T1_L2 Landsat Collection 2 Level 2 dataset ST_B10 QA_PIXEL"
    elif "sentinel-1" in lower_query or "sentinel 1" in lower_query or "flood" in lower_query:
        dataset_query = "COPERNICUS/S1_GRD Sentinel-1 GRD dataset polarization orbit flood"
    supplements = {
        "dataset_evidence": dataset_query,
        "operator_evidence": f"{query} operator filterDate filterBounds reducer export",
        "recipe_evidence": f"{query} recipe required inputs output schema",
        "failure_evidence": f"{query} failure empty collection no bands quota auth",
        "export_evidence": f"{query} Export table image Drive task monitoring",
    }
    for key in sorted(missing):
        supplemental_query = supplements.get(key)
        if supplemental_query:
            hits.extend(search(index, supplemental_query, top_k=4))
    deduped = []
    seen = set()
    for hit in hits:
        if hit.chunk_id in seen:
            continue
        seen.add(hit.chunk_id)
        deduped.append(hit)
    return deduped[: max(top_k, len(deduped))], build_retrieval_trace(query, deduped)


class _FakeNumber:
    def __init__(self, value: int | float):
        self.value = value

    def getInfo(self) -> int | float:
        return self.value


class _FakeGeometry:
    def area(self, _max_error: int) -> _FakeNumber:
        return _FakeNumber(10000)


class _FakeFeatureCollection:
    def size(self) -> _FakeNumber:
        return _FakeNumber(1)

    def geometry(self) -> _FakeGeometry:
        return _FakeGeometry()


class _FakeImageCollection:
    def filterDate(self, *_args: Any) -> "_FakeImageCollection":
        return self

    def filterBounds(self, *_args: Any) -> "_FakeImageCollection":
        return self

    def filter(self, *_args: Any) -> "_FakeImageCollection":
        return self

    def size(self) -> _FakeNumber:
        return _FakeNumber(0)


class _FakeFilter:
    @staticmethod
    def lt(*_args: Any) -> object:
        return object()

    @staticmethod
    def eq(*_args: Any) -> object:
        return object()

    @staticmethod
    def listContains(*_args: Any) -> object:
        return object()


class _FakeEmptyCollectionEE:
    Filter = _FakeFilter

    @staticmethod
    def FeatureCollection(_asset: str) -> _FakeFeatureCollection:
        return _FakeFeatureCollection()

    @staticmethod
    def ImageCollection(_dataset_id: str) -> _FakeImageCollection:
        return _FakeImageCollection()


def _run_mocked_empty_collection_preflight(task: dict[str, Any]) -> dict[str, Any]:
    config = GenericV03PreflightConfig(
        project="mock-project",
        schema_version="gee-plan/v0.3",
        plan_id=str(task.get("id") or "mocked-empty-collection"),
        profile=str(task.get("profile", "optical_index")),
        template=str(task.get("template", "sentinel2_index_image")),
        dataset_id=str(task.get("dataset_id", "COPERNICUS/S2_SR_HARMONIZED")),
        date_start=str(task.get("date_start", "2024-03-01")),
        date_end=str(task.get("date_end", "2024-04-01")),
        aoi_asset=str(task.get("aoi_asset", "projects/demo-valid/assets/hk_aoi")),
        aoi_name=str(task.get("aoi_name", "mock AOI")),
        scale=int(task.get("scale", 10)),
        crs=str(task.get("crs", "EPSG:4326")),
        required_bands=tuple(task.get("required_bands", ["B3", "B8"])),
        qa_bands=tuple(task.get("qa_bands", ["SCL"])),
        index_name=str(task.get("index_name", "NDWI")),
        index_bands=tuple(task.get("index_bands", ["B3", "B8"])),
        export_description=str(task.get("export_description", "mock_empty_collection_preflight")),
        drive_folder=str(task.get("drive_folder", "gee_exports")),
        file_prefix=str(task.get("file_prefix", "mock_empty_collection_preflight")),
        output_format=str(task.get("output_format", "GeoTIFF")),
    )
    original_initialize = generic_preflight_module.initialize
    try:
        generic_preflight_module.initialize = lambda **_kwargs: _FakeEmptyCollectionEE()
        return generic_preflight_module.run_generic_v03_preflight(config)
    finally:
        generic_preflight_module.initialize = original_initialize


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
            elif kind == "corpus_coverage":
                required = task.get("required_coverage", {})
                hits, trace = _coverage_search(index, task["query"], required, int(task.get("top_k", 8)))
                coverage = trace.get("coverage", {})
                missing = {
                    key: expected
                    for key, expected in required.items()
                    if int(coverage.get(key, 0)) < int(expected)
                }
                details = {
                    "coverage": coverage,
                    "required_coverage": required,
                    "missing_coverage": missing,
                    "hits": [hit.source_path for hit in hits],
                }
                if missing:
                    status = "failed"
            elif kind == "plan_from_text":
                result = build_general_plan_from_text(task["request"])
                expected_status = task.get("expected_status", "planned")
                actual_status = result.get("status")
                details = {
                    "request": task["request"],
                    "expected_status": expected_status,
                    "actual_status": actual_status,
                    "ok": bool(result.get("ok")),
                }
                if actual_status != expected_status:
                    status = "failed"
                if result.get("ok"):
                    plan = result.get("plan", {})
                    expected_task_type = task.get("expected_task_type")
                    expected_recipe = task.get("expected_recipe")
                    expected_metric = task.get("expected_metric")
                    actual_task_type = plan.get("task_type")
                    actual_recipe = (plan.get("intent") or {}).get("recipe_id")
                    actual_metric = (plan.get("intent") or {}).get("metric")
                    details.update(
                        {
                            "expected_task_type": expected_task_type,
                            "actual_task_type": actual_task_type,
                            "expected_recipe": expected_recipe,
                            "actual_recipe": actual_recipe,
                            "expected_metric": expected_metric,
                            "actual_metric": actual_metric,
                            "plan_id": plan.get("plan_id"),
                            "template_ready": (plan.get("execution") or {}).get("template_ready"),
                        }
                    )
                    if expected_task_type and actual_task_type != expected_task_type:
                        status = "failed"
                    if expected_recipe and actual_recipe != expected_recipe:
                        status = "failed"
                    if expected_metric and actual_metric != expected_metric:
                        status = "failed"
                    expected_template_ready = task.get("expected_template_ready")
                    if expected_template_ready is not None and bool(plan.get("execution", {}).get("template_ready")) != bool(expected_template_ready):
                        status = "failed"
                else:
                    expected_missing = set(task.get("expected_missing_fields", []))
                    actual_missing = set(result.get("missing_fields", []))
                    details.update(
                        {
                            "expected_missing_fields": sorted(expected_missing),
                            "actual_missing_fields": sorted(actual_missing),
                            "expected_error_code": task.get("expected_error_code"),
                            "actual_error_code": (result.get("error") or {}).get("category"),
                            "closest_recipes": [item.get("recipe_id") for item in result.get("closest_recipes", [])],
                        }
                    )
                    if expected_missing and expected_missing != actual_missing:
                        status = "failed"
                    expected_code = task.get("expected_error_code")
                    actual_code = (result.get("error") or {}).get("category")
                    if expected_code and expected_code != actual_code:
                        status = "failed"
            elif kind == "mocked_preflight_block":
                result = build_general_plan_from_text(task["request"])
                details = {"request": task["request"], "plan_ok": bool(result.get("ok"))}
                if not result.get("ok"):
                    status = "failed"
                    details["error"] = result.get("error")
                else:
                    plan = result["plan"]
                    context = (plan.get("execution") or {}).get("context") or {}
                    context_review_required = bool(context.get("review_required"))
                    details.update(
                        {
                            "plan_id": plan.get("plan_id"),
                            "template": (plan.get("execution") or {}).get("template"),
                            "context_review_required": context_review_required,
                            "expected_error_code": task.get("expected_error_code", "V03_CONTEXT_REVIEW_REQUIRED"),
                            "trace_artifacts_created": False,
                            "validation_passed": None,
                        }
                    )
                    if not context_review_required:
                        status = "failed"
            elif kind == "mocked_generic_empty_collection":
                report = _run_mocked_empty_collection_preflight(task)
                critical = report.get("critical_error") or {}
                expected_code = task.get("expected_error_code", "EMPTY_IMAGE_COLLECTION")
                details = {
                    "preflight": report,
                    "expected_error_code": expected_code,
                    "actual_error_code": critical.get("category"),
                }
                if report.get("ok") or critical.get("category") != expected_code:
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
                details = {
                    "script": str(out),
                    "validation": report.to_dict(),
                    "semantic": semantic,
                    "trace_artifacts_created": False,
                    "validation_passed": bool(report.ok and not any(item["severity"] == "error" for item in semantic)),
                }
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
    failed = [item["id"] for item in results if item["status"] != "passed"]
    return {
        "suite": suite.get("id", path.stem),
        "ok": all(item["status"] == "passed" for item in results),
        "summary": {
            "count": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "failures": failed,
        },
        "results": results,
    }
