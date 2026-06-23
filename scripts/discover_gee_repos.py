#!/usr/bin/env python
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from typing import Any

import yaml


DEFAULT_QUERY = "topic:google-earth-engine"
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


def _harvest_level(license_id: str, archived: bool, fork: bool) -> str:
    if archived or fork:
        return "metadata_only_until_maintainer_review"
    if license_id in LICENSED_PATTERN_LEVEL:
        return "metadata_and_patterns_only_candidate"
    return "metadata_only_until_license_review"


def discover(query: str, min_candidates: int, max_candidates: int, per_page: int, token: str | None) -> dict[str, Any]:
    repositories: list[dict[str, Any]] = []
    seen: set[str] = set()
    total_count = None
    page = 1
    while len(repositories) < max_candidates:
        url = _github_search_url(query, page=page, per_page=per_page)
        payload = _request_json(url, token=token)
        total_count = payload.get("total_count", total_count)
        items = payload.get("items") or []
        if not items:
            break
        for item in items:
            full_name = item["full_name"]
            if full_name in seen:
                continue
            seen.add(full_name)
            license_id = ((item.get("license") or {}).get("spdx_id") or "NOASSERTION").strip()
            repositories.append(
                {
                    "full_name": full_name,
                    "url": item["html_url"],
                    "description": item.get("description") or "",
                    "language": item.get("language") or "unknown",
                    "license": license_id,
                    "stars": int(item.get("stargazers_count") or 0),
                    "forks": int(item.get("forks_count") or 0),
                    "updated_at": item["updated_at"],
                    "pushed_at": item.get("pushed_at"),
                    "archived": bool(item.get("archived")),
                    "fork": bool(item.get("fork")),
                    "topics": item.get("topics") or [],
                    "task_tags": _task_tags(item),
                    "quality_flags": _quality_flags(item, license_id),
                    "review_state": "discovered_unreviewed",
                    "sampling_level": "metadata_only_discovery",
                    "harvest_level": _harvest_level(license_id, bool(item.get("archived")), bool(item.get("fork"))),
                }
            )
            if len(repositories) >= max_candidates:
                break
        page += 1
    if len(repositories) < min_candidates:
        raise RuntimeError(f"only discovered {len(repositories)} repositories; expected at least {min_candidates}")
    return {
        "schema_version": "gee-corpus-discovery/v0.3",
        "created_at": datetime.now().date().isoformat(),
        "source": "GitHub Search API",
        "query": query,
        "query_url": _github_search_url(query, page=1, per_page=min(per_page, 100)),
        "total_count_reported": total_count,
        "purpose": (
            "Broad 100+ repository discovery inventory for pattern-only GEE corpus exams. "
            "Do not copy third-party code into this repository."
        ),
        "boundary": {
            "seed_inventory": "references/corpus/github_gee_seed_repos.yml remains the 30-50 reviewed candidate set.",
            "discovery_inventory": "This file is metadata-only and does not imply code ingestion approval.",
            "promotion_rule": "Promote only factual/operator patterns after license, provenance, and official-doc compatibility review.",
        },
        "repositories": repositories,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover 100+ Google Earth Engine GitHub repository candidates.")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--min-candidates", type=int, default=100)
    parser.add_argument("--max-candidates", type=int, default=125)
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--out", default="references/corpus/github_gee_discovery_100.yml")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    payload = discover(
        query=args.query,
        min_candidates=args.min_candidates,
        max_candidates=args.max_candidates,
        per_page=args.per_page,
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
