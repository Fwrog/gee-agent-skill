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
    "QUOTA_OR_TIMEOUT": {
        "likely_cause": "Request exceeded memory, time, pixel, concurrent task, or queue limits.",
        "retryable": True,
        "suggested_fix": "Reduce AOI/date range, coarsen scale, split exports, or retry after tasks finish.",
        "user_action_required": True,
    },
    "CLIENT_SERVER_MISUSE": {
        "likely_cause": "Client-side calls such as getInfo() are used where server-side operations are safer.",
        "retryable": False,
        "suggested_fix": "Replace blocking client fetches with server-side reducers, properties, or exports.",
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
        return {
            "category": self.category,
            "message": self.message,
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
    elif "getinfo" in lower:
        category = "CLIENT_SERVER_MISUSE"
    else:
        category = "UNKNOWN_ERROR"
    return HarnessError(category=category, message=text, original=type(exc).__name__)


def error_payload(category: str, message: str, original: str | None = None) -> dict[str, Any]:
    return HarnessError(category=category, message=message, original=original).to_dict()
