from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ERROR_HINTS: dict[str, dict[str, Any]] = {
    "AUTH_ERROR": {
        "likely_cause": "Earth Engine credentials are missing, expired, or inaccessible.",
        "retryable": True,
        "suggested_fix": "Run earthengine authenticate, confirm the account has Earth Engine access, then retry.",
        "user_action_required": True,
    },
    "PROJECT_ERROR": {
        "likely_cause": "A Google Cloud project was not supplied or does not have Earth Engine enabled.",
        "retryable": True,
        "suggested_fix": "Pass --project <project-id> and confirm Earth Engine API/IAM access.",
        "user_action_required": True,
    },
    "NETWORK_ERROR": {
        "likely_cause": "A transient network, TLS, or OAuth token endpoint request failed during live initialization.",
        "retryable": True,
        "suggested_fix": "Retry the live preflight/run after confirming normal internet access; do not reauthenticate unless failures persist.",
        "user_action_required": False,
    },
    "DATASET_NOT_FOUND": {
        "likely_cause": "The Earth Engine dataset id is missing, misspelled, or unavailable to the account.",
        "retryable": False,
        "suggested_fix": "Check the dataset id against the Earth Engine Data Catalog.",
        "user_action_required": True,
    },
    "BAND_NOT_FOUND": {
        "likely_cause": "The script selects a band not present in the chosen dataset.",
        "retryable": False,
        "suggested_fix": "Check dataset bands and update the workflow template or task context.",
        "user_action_required": True,
    },
    "EMPTY_COLLECTION": {
        "likely_cause": "Date, region, cloud mask, or dataset filters removed all images.",
        "retryable": True,
        "suggested_fix": "Widen the date range/AOI, relax cloud filters, or verify collection coverage.",
        "user_action_required": True,
    },
    "EMPTY_AOI": {
        "likely_cause": "The administrative boundary source or AOI filter returned no usable features.",
        "retryable": False,
        "suggested_fix": "Inspect the boundary source schema and use the curated Hong Kong district GeoJSON or a valid user boundary.",
        "user_action_required": True,
    },
    "V03_CONTEXT_REVIEW_REQUIRED": {
        "likely_cause": "The v0.3 plan still contains placeholder or unreviewed execution context.",
        "retryable": False,
        "suggested_fix": "Review the plan YAML, replace placeholder AOI/assets/export fields with real values, then rerun preflight.",
        "user_action_required": True,
    },
    "V03_PREFLIGHT_UNSUPPORTED": {
        "likely_cause": "The selected v0.3 template does not yet have a live preflight adapter.",
        "retryable": False,
        "suggested_fix": "Keep the workflow at plan/render/validate or add a recipe-specific preflight adapter before live export.",
        "user_action_required": True,
    },
    "AOI_SCHEMA_ERROR": {
        "likely_cause": "The AOI source exists but does not expose the expected properties or geometry schema.",
        "retryable": False,
        "suggested_fix": "Inspect preflight_report.json and update the boundary source or property names.",
        "user_action_required": True,
    },
    "DISTRICT_NOT_FOUND": {
        "likely_cause": "The requested district name does not match the boundary source district-name field.",
        "retryable": False,
        "suggested_fix": "Use one of the sampled district names from preflight_report.json.",
        "user_action_required": True,
    },
    "EMPTY_IMAGE_COLLECTION": {
        "likely_cause": "Dataset, date, AOI, or cloud metadata filters returned zero candidate images.",
        "retryable": True,
        "suggested_fix": "Check the AOI/date range, relax cloud filtering, or verify dataset coverage before exporting.",
        "user_action_required": True,
    },
    "EMPTY_S2_COLLECTION": {
        "likely_cause": "Sentinel-2 date, AOI, or cloud filters returned zero images.",
        "retryable": True,
        "suggested_fix": "Check AOI/date coverage or relax cloud filtering before running NDVI export.",
        "user_action_required": True,
    },
    "EMPTY_DYNAMIC_WORLD_COLLECTION": {
        "likely_cause": "Dynamic World has no images for the requested AOI and time range.",
        "retryable": True,
        "suggested_fix": "Check Dynamic World temporal coverage, AOI overlap, and date filters.",
        "user_action_required": True,
    },
    "EMPTY_FILTERED_COLLECTION": {
        "likely_cause": "Images exist before cloud filtering but none remain after the cloud metadata threshold.",
        "retryable": True,
        "suggested_fix": "Relax the cloud threshold, change month, or inspect source imagery availability.",
        "user_action_required": True,
    },
    "NO_NDVI_BAND": {
        "likely_cause": "NDVI was not produced because source bands are missing or the mapped collection is empty.",
        "retryable": False,
        "suggested_fix": "Confirm Sentinel-2 B8/B4 bands exist and the add_ndvi mapping runs on a non-empty collection.",
        "user_action_required": True,
    },
    "NO_REQUIRED_BAND": {
        "likely_cause": "The selected image collection does not expose one or more bands required by the recipe.",
        "retryable": False,
        "suggested_fix": "Review dataset choice, band names, and recipe template before live export.",
        "user_action_required": True,
    },
    "NO_QA_BAND": {
        "likely_cause": "The selected image collection does not expose the QA or mask band expected by the preflight profile.",
        "retryable": False,
        "suggested_fix": "Choose a dataset with the required QA band or update the masking/preflight profile.",
        "user_action_required": True,
    },
    "NO_LANDCOVER_LABEL": {
        "likely_cause": "The selected land-cover dataset does not expose the expected class label band.",
        "retryable": False,
        "suggested_fix": "Confirm the land-cover dataset id and expected label band before export.",
        "user_action_required": True,
    },
    "NO_PROBABILITY_BANDS": {
        "likely_cause": "The selected probabilistic land-cover dataset is missing expected class probability bands.",
        "retryable": False,
        "suggested_fix": "Use Dynamic World V1 or update the template/preflight for the selected land-cover schema.",
        "user_action_required": True,
    },
    "CLASS_MASK_EMPTY": {
        "likely_cause": "Land-cover class masks contain no usable pixels after confidence, AOI, and NDVI overlap filters.",
        "retryable": True,
        "suggested_fix": "Lower the probability threshold, use a larger AOI/time window, or accept nulls for sparse classes.",
        "user_action_required": True,
    },
    "EXPORT_REFUSED_BY_PREFLIGHT": {
        "likely_cause": "Validation or live data preflight blocked export before task.start().",
        "retryable": True,
        "suggested_fix": "Inspect preflight_report.json and landcover_diagnostics.json, fix blocking checks, then rerun.",
        "user_action_required": True,
    },
    "NULL_NDVI_STAT": {
        "likely_cause": "The NDVI image exists but the sanity reducer returned no usable mean value for the AOI.",
        "retryable": True,
        "suggested_fix": "Inspect cloud masks, AOI geometry, scale, and valid-pixel coverage.",
        "user_action_required": True,
    },
    "GEOMETRY_ERROR": {
        "likely_cause": "AOI geometry, asset id, or administrative filter is invalid or empty.",
        "retryable": True,
        "suggested_fix": "Validate the AOI asset/filter and use a smaller geometry for smoke tests.",
        "user_action_required": True,
    },
    "REDUCER_SCALE_ERROR": {
        "likely_cause": "Reducer scale, CRS, tileScale, or pixel budget is inappropriate for the AOI.",
        "retryable": True,
        "suggested_fix": "Use explicit scale/CRS, increase tileScale, coarsen scale, or split regions.",
        "user_action_required": True,
    },
    "EXPORT_TASK_ERROR": {
        "likely_cause": "Earth Engine export task creation or execution failed.",
        "retryable": True,
        "suggested_fix": "Inspect task status/error_message, destination permissions, selectors, and quotas.",
        "user_action_required": True,
    },
    "NO_EXPORT_TARGET": {
        "likely_cause": "The plan does not contain enough export destination metadata.",
        "retryable": False,
        "suggested_fix": "Set export description, Drive folder or destination, and file prefix before live preflight/run.",
        "user_action_required": True,
    },
    "EXPORT_TASK_FAILED": {
        "likely_cause": "A submitted Earth Engine export task reached FAILED state.",
        "retryable": True,
        "suggested_fix": "Inspect export_tasks.json, fix the root workflow/data issue, then submit a new task.",
        "user_action_required": True,
    },
    "EXPORT_TASK_NOT_OBSERVED": {
        "likely_cause": "The script ran, but the expected Earth Engine export task was not visible in the task list.",
        "retryable": True,
        "suggested_fix": "Check the export description, Earth Engine Tasks page, and Drive destination before claiming submission success or rerunning.",
        "user_action_required": True,
    },
    "AMBIGUOUS_TASK": {
        "likely_cause": "The natural-language request is missing date, metric, AOI, or output intent.",
        "retryable": False,
        "suggested_fix": "Use a supported request such as: Compute January 2024 mean NDVI for Hong Kong and export CSV.",
        "user_action_required": True,
    },
    "UNSUPPORTED_TASK": {
        "likely_cause": "The request is outside the currently registered deterministic recipes.",
        "retryable": False,
        "suggested_fix": "Use a supported recipe such as NDVI, NDWI, NDBI, Landsat LST, Sentinel-1 flood mapping, CSV export, or GeoTIFF export.",
        "user_action_required": True,
    },
    "UNKNOWN_DATASET_ID": {
        "likely_cause": "The request names a dataset that is not in the reviewed local dataset catalog.",
        "retryable": False,
        "suggested_fix": "Use a cataloged dataset ID or add a reviewed dataset card before planning live work.",
        "user_action_required": True,
    },
    "QUOTA_OR_TIMEOUT": {
        "likely_cause": "Request exceeded memory, time, pixel, concurrent task, or queue limits.",
        "retryable": True,
        "suggested_fix": "Reduce AOI/date range, coarsen scale, split exports, or retry after tasks finish.",
        "user_action_required": True,
    },
    "UNSAFE_GETINFO": {
        "likely_cause": "Generated production code attempts to materialize Earth Engine server objects locally with getInfo().",
        "retryable": False,
        "suggested_fix": "Keep large computations server-side and use exports or bounded harness preflight probes instead of getInfo().",
        "user_action_required": True,
    },
    "CLIENT_SERVER_MISUSE": {
        "likely_cause": "Client-side calls such as getInfo() are used where server-side operations are safer.",
        "retryable": False,
        "suggested_fix": "Replace blocking client fetches with server-side reducers, properties, or exports.",
        "user_action_required": True,
    },
    "PREFLIGHT_REQUIRED": {
        "likely_cause": "A live Earth Engine export path was requested before validation and preflight gates were completed.",
        "retryable": True,
        "suggested_fix": "Run plan review, validation, and preflight first; submit live export only with --confirm-live after those checks pass.",
        "user_action_required": True,
    },
    "VALIDATION_ERROR": {
        "likely_cause": "Offline validation found blocking script or task issues.",
        "retryable": False,
        "suggested_fix": "Fix validation findings before live execution.",
        "user_action_required": True,
    },
    "UNKNOWN_ERROR": {
        "likely_cause": "The failure did not match a known harness category.",
        "retryable": False,
        "suggested_fix": "Read the original error and inspect the run trace artifacts.",
        "user_action_required": True,
    },
}


@dataclass
class HarnessError(Exception):
    category: str
    message: str
    original: str | None = None

    def to_dict(self) -> dict[str, Any]:
        base = ERROR_HINTS.get(self.category, ERROR_HINTS["UNKNOWN_ERROR"])
        suggested_fix = base["suggested_fix"]
        return {
            "code": self.category,
            "category": self.category,
            "message": self.message,
            "hint": suggested_fix,
            "original": self.original,
            **base,
        }

    def __str__(self) -> str:
        payload = self.to_dict()
        return (
            f"[{payload['category']}] {self.message} "
            f"Suggested fix: {payload['suggested_fix']}"
        )


def classify_exception(exc: Exception) -> HarnessError:
    text = str(exc)
    lower = text.lower()
    if "earthengine-api is not installed" in lower:
        category = "AUTH_ERROR"
    elif (
        "oauth2.googleapis.com" in lower
        or "/token" in lower
        or "max retries exceeded" in lower
        or "ssleoferror" in lower
        or "ssl:" in lower
        or "httpsconnectionpool" in lower
    ):
        category = "NETWORK_ERROR"
    elif "project" in lower:
        category = "PROJECT_ERROR"
    elif "credential" in lower or "authenticate" in lower or "permission" in lower:
        category = "AUTH_ERROR"
    elif "collection" in lower and ("not found" in lower or "asset" in lower):
        category = "DATASET_NOT_FOUND"
    elif "band" in lower:
        category = "BAND_NOT_FOUND"
    elif "empty" in lower or "no images" in lower:
        category = "EMPTY_COLLECTION"
    elif "geometry" in lower or "bounds" in lower:
        category = "GEOMETRY_ERROR"
    elif "scale" in lower or "pixels" in lower:
        category = "REDUCER_SCALE_ERROR"
    elif "quota" in lower or "timed out" in lower or "timeout" in lower or "memory" in lower:
        category = "QUOTA_OR_TIMEOUT"
    elif "task" in lower or "export" in lower:
        category = "EXPORT_TASK_ERROR"
    elif "preflight" in lower and ("required" in lower or "before" in lower):
        category = "PREFLIGHT_REQUIRED"
    elif "getinfo" in lower:
        category = "UNSAFE_GETINFO"
    else:
        category = "UNKNOWN_ERROR"
    return HarnessError(category=category, message=text, original=type(exc).__name__)


def error_payload(category: str, message: str, original: str | None = None) -> dict[str, Any]:
    return HarnessError(category=category, message=message, original=original).to_dict()
