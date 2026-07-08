from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .paths import default_source_registry_path


TRUST_TIERS = {"A", "B", "C", "D"}
ALLOWED_USE = {
    "metadata_only",
    "summary_only",
    "distilled_patterns",
    "short_quoted_excerpt_allowed",
    "code_reuse_allowed",
    "not_allowed",
}
REVIEWER_STATUSES = {"accepted", "candidate", "rejected"}
SOURCE_REFRESH_STATUSES = {"fresh", "stale", "unavailable", "candidate_unverified"}
SOURCE_TYPES = {
    "official_docs",
    "official_data_catalog",
    "official_api_reference",
    "official_github_repo",
    "journal_paper",
    "conference_paper",
    "arxiv_paper",
    "joss_paper",
    "community_repo",
    "community_docs",
    "diagnostic_thread",
}
SECRET_RE = re.compile(
    r"(AIza[0-9A-Za-z_-]{20,}|ya29\.[0-9A-Za-z_-]+|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
PRIVATE_RE = re.compile(
    r"(/Users/|/Volumes/|C:\\Users\\|users/[A-Za-z0-9_.-]+/|projects/[^/\s]+/assets/[^,\s]+|drive\.google\.com/drive/folders/)",
    re.IGNORECASE,
)


def load_source_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or default_source_registry_path()
    if not registry_path.exists():
        raise FileNotFoundError(f"Source registry not found: {registry_path}")
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Source registry must be a mapping: {registry_path}")
    sources = data.get("sources")
    if not isinstance(sources, list):
        raise ValueError("Source registry must contain a sources list.")
    return data


def source_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("source_id")): item for item in registry.get("sources", [])}


def validate_source_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or default_source_registry_path()
    data = load_source_registry(registry_path)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: set[str] = set()
    required = {
        "source_id",
        "title",
        "source_url",
        "source_type",
        "trust_tier",
        "allowed_use",
        "last_checked",
        "reviewer_status",
        "claim_boundary",
        "private_content_risk",
        "include_reason",
        "source_refresh_status",
    }
    for idx, item in enumerate(data.get("sources", []), 1):
        location = str(item.get("source_id") or f"sources[{idx}]")
        missing = sorted(field for field in required if not item.get(field))
        if missing:
            errors.append({"source_id": location, "code": "missing-required-fields", "message": ", ".join(missing)})
            continue
        source_id = str(item["source_id"])
        if source_id in seen:
            errors.append({"source_id": source_id, "code": "duplicate-source-id", "message": "source_id must be unique."})
        seen.add(source_id)
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", source_id):
            errors.append({"source_id": source_id, "code": "unstable-source-id", "message": "Use lowercase stable ids."})
        if item["source_type"] not in SOURCE_TYPES:
            errors.append({"source_id": source_id, "code": "unknown-source-type", "message": str(item["source_type"])})
        if item["trust_tier"] not in TRUST_TIERS:
            errors.append({"source_id": source_id, "code": "unknown-trust-tier", "message": str(item["trust_tier"])})
        if item["allowed_use"] not in ALLOWED_USE:
            errors.append({"source_id": source_id, "code": "unknown-allowed-use", "message": str(item["allowed_use"])})
        if item["reviewer_status"] not in REVIEWER_STATUSES:
            errors.append({"source_id": source_id, "code": "unknown-reviewer-status", "message": str(item["reviewer_status"])})
        if item["source_refresh_status"] not in SOURCE_REFRESH_STATUSES:
            errors.append({"source_id": source_id, "code": "unknown-source-refresh-status", "message": str(item["source_refresh_status"])})
        if item["reviewer_status"] == "accepted" and item["source_refresh_status"] == "candidate_unverified":
            errors.append({"source_id": source_id, "code": "accepted-source-unverified", "message": "Accepted sources cannot be candidate_unverified."})
        if item["reviewer_status"] == "candidate" and item["source_refresh_status"] == "fresh" and item["trust_tier"] != "C":
            warnings.append({"source_id": source_id, "code": "candidate-marked-fresh", "message": "Candidate research sources should usually remain candidate_unverified."})
        if item["source_refresh_status"] in {"stale", "unavailable"} and item["reviewer_status"] == "accepted":
            warnings.append({"source_id": source_id, "code": "accepted-source-not-fresh", "message": "Accepted sources should be refreshed before relying on current facts."})
        if item["trust_tier"] == "A" and item["reviewer_status"] != "accepted":
            warnings.append({"source_id": source_id, "code": "tier-a-not-accepted", "message": "Tier A sources should be accepted after URL review."})
        if item["trust_tier"] != "A" and item["reviewer_status"] == "accepted" and item.get("allowed_use") == "code_reuse_allowed":
            warnings.append({"source_id": source_id, "code": "accepted-code-reuse", "message": "Code reuse needs explicit license review."})
        text = yaml.safe_dump(item, sort_keys=True)
        if SECRET_RE.search(text) or PRIVATE_RE.search(text):
            errors.append({"source_id": source_id, "code": "private-or-secret-looking-content", "message": "Public registry cannot contain private paths, asset ids, or secrets."})
    return {
        "ok": not errors,
        "schema_version": "gee-source-registry/v0.1",
        "path": str(registry_path),
        "source_count": len(data.get("sources", [])),
        "accepted_count": sum(1 for item in data.get("sources", []) if item.get("reviewer_status") == "accepted"),
        "candidate_count": sum(1 for item in data.get("sources", []) if item.get("reviewer_status") == "candidate"),
        "errors": errors,
        "warnings": warnings,
    }
