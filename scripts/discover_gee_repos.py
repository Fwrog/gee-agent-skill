#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from typing import Any

import yaml


DEFAULT_LANES = (
    ("gee_topic", "topic:google-earth-engine archived:false fork:false", 220),
    ("paper_linkage", '"Google Earth Engine" DOI in:readme archived:false fork:false', 80),
    ("research_workflow", '"Google Earth Engine" research in:readme archived:false fork:false', 80),
)
USER_AGENT = "gee-agent-skill-corpus-discovery"
LICENSED_PATTERN_LEVEL = {
    "Apache-2.0",
    "MIT",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "GPL-2.0",
    "GPL-3.0",
    "LGPL-2.1",
    "LGPL-3.0",
    "MPL-2.0",
    "CC0-1.0",
    "CC-BY-4.0",
}
TASK_KEYWORDS = {
    "python": ("python", "jupyter", "notebook", "geemap"),
    "javascript_code_editor": ("javascript", "code-editor", "code editor"),
    "spectral_indices": ("ndvi", "ndwi", "index", "spectral", "vegetation"),
    "sentinel2_optical": ("sentinel-2", "sentinel2", "s2", "copernicus"),
    "sentinel1_sar": ("sentinel-1", "sentinel1", "sar", "radar"),
    "landsat_lst": ("landsat", "lst", "temperature"),
    "water_flood": ("water", "flood", "inundation"),
    "landcover_change": ("land cover", "landcover", "landtrendr", "change", "forest"),
    "production_tooling": ("cli", "package", "api", "tool", "library"),
    "education_tutorial": ("tutorial", "course", "workshop", "example", "notebook"),
}
DATA_USAGE_KEYWORDS = {
    "sentinel_2": ("sentinel-2", "sentinel2", "copernicus s2"),
    "sentinel_1_sar": ("sentinel-1", "sentinel1", "synthetic aperture radar", " sar "),
    "landsat": ("landsat",),
    "modis": ("modis",),
    "viirs": ("viirs", "nighttime light", "night light"),
    "climate_weather": ("climate", "era5", "temperature", "weather"),
    "precipitation_hydrology": ("precipitation", "rainfall", "hydrology", "flood", "water"),
    "landcover_forestry": ("land cover", "landcover", "forest", "landtrendr"),
    "coast_ocean": ("coast", "shoreline", "ocean", "marine"),
    "elevation_terrain": ("elevation", "dem", "terrain"),
    "population_urban": ("population", "urban", "built-up", "built up"),
    "catalog_or_data_access": ("catalog", "dataset", "data cube", "xarray"),
}
PAPER_URL_PATTERN = re.compile(r"https?://(?:dx\.)?(?:doi\.org|arxiv\.org)/\S+", re.IGNORECASE)
GEE_TOPICS = {"google-earth-engine", "earth-engine", "earthengine"}
GEE_TEXT_PATTERN = re.compile(r"\b(?:google\s+earth\s+engine|earth\s+engine|earthengine)\b", re.IGNORECASE)


def _github_search_url(query: str, page: int, per_page: int) -> str:
    return "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": query, "sort": "stars", "order": "desc", "per_page": per_page, "page": page}
    )


def _request_json(url: str, token: str | None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return yaml.safe_load(response.read().decode("utf-8"))


def _task_tags(item: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(value or "")
        for value in [
            item.get("full_name"),
            item.get("name"),
            item.get("description"),
            item.get("language"),
            " ".join(item.get("topics") or []),
        ]
    ).lower()
    return [tag for tag, keywords in TASK_KEYWORDS.items() if any(keyword in text for keyword in keywords)]


def _quality_flags(item: dict[str, Any], license_id: str) -> list[str]:
    flags: list[str] = []
    full_name = item["full_name"]
    stars = int(item.get("stargazers_count") or 0)
    updated_at = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
    if full_name.startswith(("google/", "gee-community/", "giswqs/", "opengeos/")):
        flags.append("known_gee_org_or_maintainer")
    if license_id and license_id != "NOASSERTION":
        flags.append("declares_license")
    if stars >= 100:
        flags.append("high_star")
    if updated_at >= datetime.now(tz=UTC) - timedelta(days=1095):
        flags.append("updated_within_3y")
    if item.get("archived"):
        flags.append("archived")
    if item.get("fork"):
        flags.append("fork")
    return flags


def _quality_score(item: dict[str, Any], license_id: str, lanes: list[str]) -> int:
    score = 0
    stars = int(item.get("stargazers_count") or 0)
    updated_at = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
    if item["full_name"].startswith(("google/", "gee-community/", "giswqs/", "opengeos/")):
        score += 2
    if license_id and license_id != "NOASSERTION":
        score += 2
    if stars >= 100:
        score += 3
    elif stars >= 20:
        score += 2
    elif stars >= 5:
        score += 1
    if updated_at >= datetime.now(tz=UTC) - timedelta(days=1095):
        score += 1
    if item.get("description"):
        score += 1
    if _task_tags(item):
        score += 1
    if "paper_linkage" in lanes or _paper_linkage(item, lanes)["status"] != "none_detected":
        score += 1
    return score


def _data_usage_signals(item: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(value or "")
        for value in [
            item.get("full_name"),
            item.get("description"),
            " ".join(item.get("topics") or []),
        ]
    ).lower()
    padded = f" {text} "
    return [
        signal
        for signal, keywords in DATA_USAGE_KEYWORDS.items()
        if any(keyword in padded for keyword in keywords)
    ]


def _paper_linkage(item: dict[str, Any], lanes: list[str]) -> dict[str, Any]:
    homepage = str(item.get("homepage") or "")
    description = str(item.get("description") or "")
    match = PAPER_URL_PATTERN.search(f"{homepage} {description}")
    if match:
        return {
            "status": "external_reference_url_unverified",
            "url": match.group(0).rstrip(".,;)"),
        }
    if "paper_linkage" in lanes:
        return {"status": "search_lane_hint_unverified", "url": None}
    if "research_workflow" in lanes:
        return {"status": "research_lane_hint_unverified", "url": None}
    return {"status": "none_detected", "url": None}


def _domain_relevance(item: dict[str, Any], lanes: list[str]) -> dict[str, Any]:
    evidence: list[str] = []
    topics = {str(topic).lower() for topic in item.get("topics") or []}
    text = " ".join(
        str(value or "") for value in (item.get("full_name"), item.get("name"), item.get("description"))
    )
    if "gee_topic" in lanes:
        evidence.append("github_google_earth_engine_topic_query")
    if topics & GEE_TOPICS:
        evidence.append("repository_topic")
    if GEE_TEXT_PATTERN.search(text):
        evidence.append("name_or_description")
    return {
        "status": "direct_metadata_evidence" if evidence else "search_lane_only_unverified",
        "evidence": sorted(set(evidence)),
    }


def _harvest_level(license_id: str, archived: bool, fork: bool) -> str:
    if archived or fork:
        return "metadata_only_until_maintainer_review"
    if license_id in LICENSED_PATTERN_LEVEL:
        return "metadata_and_patterns_only_candidate"
    return "metadata_only_until_license_review"


def _discover_lane(query: str, limit: int, per_page: int, token: str | None) -> tuple[list[dict[str, Any]], int | None]:
    items: list[dict[str, Any]] = []
    total_count = None
    page = 1
    while len(items) < limit:
        payload = _request_json(_github_search_url(query, page=page, per_page=per_page), token=token)
        total_count = payload.get("total_count", total_count)
        page_items = payload.get("items") or []
        if not page_items:
            break
        items.extend(page_items[: limit - len(items)])
        page += 1
    return items, total_count


def discover(
    lanes: tuple[tuple[str, str, int], ...],
    min_candidates: int,
    max_candidates: int,
    per_page: int,
    min_quality_score: int,
    min_paper_candidates: int,
    token: str | None,
) -> dict[str, Any]:
    by_name: dict[str, dict[str, Any]] = {}
    lane_records: list[dict[str, Any]] = []
    for lane_name, query, limit in lanes:
        items, total_count = _discover_lane(query, limit=limit, per_page=per_page, token=token)
        lane_records.append(
            {
                "name": lane_name,
                "query": query,
                "query_url": _github_search_url(query, page=1, per_page=min(per_page, 100)),
                "requested_limit": limit,
                "returned_count": len(items),
                "total_count_reported": total_count,
            }
        )
        for item in items:
            full_name = item["full_name"]
            if full_name not in by_name:
                by_name[full_name] = {"item": item, "lanes": []}
            by_name[full_name]["lanes"].append(lane_name)

    screened: list[dict[str, Any]] = []
    for record in by_name.values():
        item = record["item"]
        lanes_for_item = sorted(set(record["lanes"]))
        if item.get("archived") or item.get("fork"):
            continue
        relevance = _domain_relevance(item, lanes_for_item)
        if relevance["status"] != "direct_metadata_evidence":
            continue
        license_id = ((item.get("license") or {}).get("spdx_id") or "NOASSERTION").strip()
        score = _quality_score(item, license_id, lanes_for_item)
        if score < min_quality_score:
            continue
        screened.append(
            {
                "full_name": item["full_name"],
                "url": item["html_url"],
                "description": item.get("description") or "",
                "homepage": item.get("homepage") or None,
                "language": item.get("language") or "unknown",
                "license": license_id,
                "stars": int(item.get("stargazers_count") or 0),
                "forks": int(item.get("forks_count") or 0),
                "updated_at": item["updated_at"],
                "pushed_at": item.get("pushed_at"),
                "archived": False,
                "fork": False,
                "topics": item.get("topics") or [],
                "task_tags": _task_tags(item),
                "data_usage_signals": _data_usage_signals(item),
                "data_usage_review_state": "metadata_inferred_unverified",
                "paper_linkage": _paper_linkage(item, lanes_for_item),
                "domain_relevance": relevance,
                "discovery_lanes": lanes_for_item,
                "quality_score": score,
                "quality_band": "high_signal_metadata" if score >= 7 else "qualified_metadata_candidate",
                "quality_flags": _quality_flags(item, license_id),
                "review_state": "quality_screened_unreviewed",
                "sampling_level": "metadata_only_discovery",
                "harvest_level": _harvest_level(license_id, False, False),
            }
        )

    screened.sort(key=lambda item: (-item["quality_score"], -item["stars"], item["full_name"].lower()))
    paper_candidates = [item for item in screened if item["paper_linkage"]["status"] != "none_detected"]
    selected = paper_candidates[:min_paper_candidates]
    selected_names = {item["full_name"] for item in selected}
    selected.extend(item for item in screened if item["full_name"] not in selected_names)
    repositories = selected[:max_candidates]
    if len(repositories) < min_candidates:
        raise RuntimeError(
            f"only {len(repositories)} repositories passed quality_score >= {min_quality_score}; "
            f"expected at least {min_candidates}"
        )
    paper_candidate_count = sum(item["paper_linkage"]["status"] != "none_detected" for item in repositories)
    if paper_candidate_count < min_paper_candidates:
        raise RuntimeError(
            f"only {paper_candidate_count} paper/research candidates were selected; "
            f"expected at least {min_paper_candidates}"
        )
    return {
        "schema_version": "gee-corpus-discovery/v0.5",
        "created_at": datetime.now().date().isoformat(),
        "source": "GitHub Search API",
        "queries": lane_records,
        "purpose": (
            "Quality-screened 200-repository discovery inventory for pattern-only GEE corpus exams, "
            "data-usage review, and paper-linkage review. Do not copy third-party code."
        ),
        "snapshot_summary": {
            "repository_count": len(repositories),
            "direct_domain_evidence_count": sum(
                item["domain_relevance"]["status"] == "direct_metadata_evidence"
                for item in repositories
            ),
            "high_signal_metadata_count": sum(
                item["quality_band"] == "high_signal_metadata" for item in repositories
            ),
            "qualified_metadata_candidate_count": sum(
                item["quality_band"] == "qualified_metadata_candidate"
                for item in repositories
            ),
            "declared_license_count": sum(
                item["license"] != "NOASSERTION" for item in repositories
            ),
            "license_noassertion_count": sum(
                item["license"] == "NOASSERTION" for item in repositories
            ),
        },
        "quality_policy": {
            "minimum_score": min_quality_score,
            "excluded": ["archived", "fork"],
            "domain_relevance_required": "direct_metadata_evidence",
            "search_lane_only_matches_are_excluded": True,
            "paper_candidate_floor": min_paper_candidates,
            "paper_candidate_count": paper_candidate_count,
            "review_boundary": "Metadata quality screening is not repository, code, data, or paper review.",
            "data_contract_required_before_promotion": [
                "dataset_id_and_version",
                "bands_or_variables",
                "scale_factor_and_offset",
                "qa_and_mask_policy",
                "spatial_grid_projection_and_resampling",
                "temporal_coverage_and_cadence",
                "access_license_and_asset_stability",
                "private_asset_dependency",
            ],
        },
        "boundary": {
            "seed_inventory": "references/corpus/github_gee_seed_repos.yml remains the 30-50 reviewed candidate set.",
            "discovery_inventory": "This file is metadata-only and does not imply code, data, or paper review approval.",
            "review_overlay": (
                "Deep-review decisions are recorded separately in "
                "references/corpus/github_gee_reviewed_batch_01.yml; discovery records retain "
                "their snapshot-level quality_screened_unreviewed state."
            ),
            "promotion_rule": "Promote only factual/operator patterns after license, provenance, and official-doc compatibility review.",
        },
        "repositories": repositories,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover 200 quality-screened Google Earth Engine repository candidates.")
    parser.add_argument("--query", help="Optional single custom query; otherwise use the audited multi-lane search.")
    parser.add_argument("--min-candidates", type=int, default=200)
    parser.add_argument("--max-candidates", type=int, default=200)
    parser.add_argument("--min-quality-score", type=int, default=4)
    parser.add_argument("--min-paper-candidates", type=int, default=20)
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--out", default="references/corpus/github_gee_discovery_200.yml")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    lanes = (("custom", args.query, max(args.max_candidates, args.min_candidates)),) if args.query else DEFAULT_LANES
    min_paper_candidates = 0 if args.query else args.min_paper_candidates
    payload = discover(
        lanes=lanes,
        min_candidates=args.min_candidates,
        max_candidates=args.max_candidates,
        per_page=args.per_page,
        min_quality_score=args.min_quality_score,
        min_paper_candidates=min_paper_candidates,
        token=token,
    )
    out = args.out
    if out == "-":
        yaml.safe_dump(payload, sys.stdout, sort_keys=False, allow_unicode=True)
    else:
        from pathlib import Path

        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"{payload['schema_version']} {len(payload['repositories'])} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
