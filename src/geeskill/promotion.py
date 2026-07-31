from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_VERSION = "mistake-promotion-manifest/v0.1"
REVIEW_SCHEMA_VERSION = "gee-local-learning-review/v0.1"

TOP_LEVEL_FIELDS = {"schema_version", "created_at", "item_count", "items"}
ITEM_FIELDS = {
    "id",
    "title",
    "failure_class",
    "source_tier",
    "public_boundary",
    "public_summary",
    "missed_checks",
    "distill_targets",
    "regression_ids",
    "ignorance_boundary",
}
IGNORANCE_FIELDS = {
    "omitted_or_unverified",
    "project_alias_excluded",
    "raw_evidence_refs_excluded",
    "note_body_excluded",
}
SOURCE_TIERS = {
    "official",
    "paper",
    "reviewed_community",
    "candidate",
    "internal",
}
PUBLIC_BOUNDARIES = {"pattern_only", "public"}
TARGET_KINDS = {
    "dataset",
    "evidence",
    "eval",
    "failure",
    "operator",
    "rule",
    "skill",
    "workflow",
}
PORTABLE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
PRIVATE_OR_SECRET_RE = re.compile(
    r"("
    r"[A-Za-z]:\\(?!path\\to\\)|"
    r"/Users/[^/\s]+/|"
    r"/home/[^/\s]+/|"
    r"/Volumes/[^/\s]+/|"
    r"projects/(?!example/)[A-Za-z0-9_.-]+/assets/|"
    r"users/(?!example/)[A-Za-z0-9_.-]+/|"
    r"gs://[A-Za-z0-9][A-Za-z0-9._-]+|"
    r"https?://drive\.google\.com/|"
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"AIza[0-9A-Za-z_-]{20,}|"
    r"ya29\.|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r")",
    re.IGNORECASE,
)


def promotion_contract() -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "relationship": {
            "official_layer": "Versioned public GEE knowledge, rules, and regressions.",
            "user_layer": "User-owned Obsidian notes, local configuration, and private evidence.",
            "bridge": "Explicit public-safe candidate manifest; no automatic synchronization.",
        },
        "allowed_target_kinds": sorted(TARGET_KINDS),
        "required_item_fields": sorted(ITEM_FIELDS),
        "boundaries": [
            "A passing manifest review does not promote knowledge.",
            "The official repository never reads the raw vault or private evidence.",
            "Official releases do not overwrite the user-owned learning layer.",
            "Promotion requires independent source review, reproduction, regression, maintainer approval, and a versioned release.",
        ],
    }


def load_promotion_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("promotion manifest must be a JSON object")
    return payload


def _nonempty_string(
    value: Any,
    field: str,
    errors: list[str],
) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value.strip()


def _string_list(
    value: Any,
    field: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    if not allow_empty and not value:
        errors.append(f"{field} must not be empty")
        return []
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{field} must contain only non-empty strings")
        return []
    return [item.strip() for item in value]


def _scan_public_value(value: Any, field: str, errors: list[str]) -> None:
    if isinstance(value, str):
        if PRIVATE_OR_SECRET_RE.search(value):
            errors.append(f"{field} contains private or secret-looking content")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _scan_public_value(item, f"{field}[{index}]", errors)


def _validate_item(
    item: Any,
    index: int,
    seen_ids: set[str],
) -> tuple[list[str], list[str], dict[str, Any] | None]:
    prefix = f"items[{index}]"
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return [f"{prefix} must be an object"], warnings, None

    missing = sorted(ITEM_FIELDS - set(item))
    extra = sorted(set(item) - ITEM_FIELDS)
    if missing:
        errors.append(f"{prefix} missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix} contains forbidden fields: {', '.join(extra)}")

    item_id = _nonempty_string(item.get("id"), f"{prefix}.id", errors)
    if item_id:
        if not PORTABLE_ID_RE.fullmatch(item_id):
            errors.append(f"{prefix}.id must be a portable identifier")
        if item_id in seen_ids:
            errors.append(f"{prefix}.id is duplicated")
        seen_ids.add(item_id)

    for field in ("title", "failure_class", "public_summary"):
        _nonempty_string(item.get(field), f"{prefix}.{field}", errors)
    failure_class = item.get("failure_class")
    if isinstance(failure_class, str) and not PORTABLE_ID_RE.fullmatch(
        failure_class
    ):
        errors.append(f"{prefix}.failure_class must be a portable identifier")

    source_tier = item.get("source_tier")
    if source_tier not in SOURCE_TIERS:
        errors.append(
            f"{prefix}.source_tier must be one of {sorted(SOURCE_TIERS)}"
        )
    elif source_tier != "official":
        warnings.append(
            f"{prefix} requires an independent official-source check for current platform or dataset facts"
        )

    public_boundary = item.get("public_boundary")
    if public_boundary not in PUBLIC_BOUNDARIES:
        errors.append(
            f"{prefix}.public_boundary must be one of {sorted(PUBLIC_BOUNDARIES)}"
        )

    missed_checks = _string_list(
        item.get("missed_checks"),
        f"{prefix}.missed_checks",
        errors,
    )
    distill_targets = _string_list(
        item.get("distill_targets"),
        f"{prefix}.distill_targets",
        errors,
    )
    regression_ids = _string_list(
        item.get("regression_ids"),
        f"{prefix}.regression_ids",
        errors,
    )

    for target_index, target in enumerate(distill_targets):
        kind, separator, name = target.partition(":")
        if not separator or kind not in TARGET_KINDS or not name:
            errors.append(
                f"{prefix}.distill_targets[{target_index}] must use <kind>:<portable-id>"
            )
        elif not PORTABLE_ID_RE.fullmatch(name):
            errors.append(
                f"{prefix}.distill_targets[{target_index}] has a non-portable target id"
            )
    for regression_index, regression_id in enumerate(regression_ids):
        if not PORTABLE_ID_RE.fullmatch(regression_id):
            errors.append(
                f"{prefix}.regression_ids[{regression_index}] must be a portable identifier"
            )

    ignorance = item.get("ignorance_boundary")
    unknowns: list[str] = []
    if not isinstance(ignorance, dict):
        errors.append(f"{prefix}.ignorance_boundary must be an object")
    else:
        missing_ignorance = sorted(IGNORANCE_FIELDS - set(ignorance))
        extra_ignorance = sorted(set(ignorance) - IGNORANCE_FIELDS)
        if missing_ignorance:
            errors.append(
                f"{prefix}.ignorance_boundary missing fields: {', '.join(missing_ignorance)}"
            )
        if extra_ignorance:
            errors.append(
                f"{prefix}.ignorance_boundary contains forbidden fields: {', '.join(extra_ignorance)}"
            )
        unknowns = _string_list(
            ignorance.get("omitted_or_unverified"),
            f"{prefix}.ignorance_boundary.omitted_or_unverified",
            errors,
            allow_empty=public_boundary == "public",
        )
        for flag in (
            "project_alias_excluded",
            "raw_evidence_refs_excluded",
            "note_body_excluded",
        ):
            if ignorance.get(flag) is not True:
                errors.append(f"{prefix}.ignorance_boundary.{flag} must be true")

    for field in (
        "title",
        "failure_class",
        "public_summary",
    ):
        _scan_public_value(item.get(field), f"{prefix}.{field}", errors)
    _scan_public_value(missed_checks, f"{prefix}.missed_checks", errors)
    _scan_public_value(distill_targets, f"{prefix}.distill_targets", errors)
    _scan_public_value(regression_ids, f"{prefix}.regression_ids", errors)
    _scan_public_value(
        unknowns,
        f"{prefix}.ignorance_boundary.omitted_or_unverified",
        errors,
    )

    queue_item = None
    if item_id:
        queue_item = {
            "id": item_id,
            "targets": distill_targets,
            "regression_ids": regression_ids,
            "required_actions": [
                "Independently reproduce the failure and correction in the target repository.",
                "Verify current Earth Engine and dataset facts against official sources.",
                "Review the public summary and ignorance boundary.",
                "Implement the mapped rule, card, workflow, validator, or evaluation case.",
                "Run relevant regressions and the release gate.",
                "Obtain maintainer approval in a versioned release.",
            ],
        }
    return errors, warnings, queue_item


def review_promotion_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings = [
        "A passing review validates the transport and privacy contract only; it does not promote official knowledge."
    ]

    missing = sorted(TOP_LEVEL_FIELDS - set(payload))
    extra = sorted(set(payload) - TOP_LEVEL_FIELDS)
    if missing:
        errors.append(f"manifest missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"manifest contains forbidden fields: {', '.join(extra)}")
    if payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {MANIFEST_SCHEMA_VERSION}")

    created_at = payload.get("created_at")
    if not isinstance(created_at, str) or not created_at.strip():
        errors.append("created_at must be a non-empty ISO timestamp")
    else:
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append("created_at must be a valid ISO timestamp")

    items = payload.get("items")
    if not isinstance(items, list):
        errors.append("items must be a list")
        items = []
    item_count = payload.get("item_count")
    if not isinstance(item_count, int) or isinstance(item_count, bool):
        errors.append("item_count must be an integer")
    elif item_count != len(items):
        errors.append("item_count does not match items length")

    queue: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        item_errors, item_warnings, queue_item = _validate_item(
            item,
            index,
            seen_ids,
        )
        errors.extend(item_errors)
        warnings.extend(item_warnings)
        if queue_item is not None:
            queue.append(queue_item)

    ok = not errors
    status = "candidate_review_ready" if items else "no_candidates"
    return {
        "ok": ok,
        "schema_version": REVIEW_SCHEMA_VERSION,
        "manifest_schema_version": payload.get("schema_version"),
        "status": status if ok else "blocked",
        "official_promotion": False,
        "item_count": len(items),
        "errors": errors,
        "warnings": warnings,
        "review_queue": queue if ok else [],
    }
