#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PATTERN_GROUPS: dict[str, tuple[str, ...]] = {
    "auth_init": ("ee.Initialize", "ee.Authenticate"),
    "collection_filters": ("ee.ImageCollection", "filterDate", "filterBounds"),
    "index_ops": ("normalizedDifference", ".expression"),
    "quality_masking": ("updateMask", "QA_PIXEL", "SCL", "cloud", "mask"),
    "reducers": ("reduceRegion", "reduceRegions"),
    "exports": (
        "Export.image.toDrive",
        "Export.table.toDrive",
        "ee.batch.Export.image.toDrive",
        "ee.batch.Export.table.toDrive",
    ),
    "task_lifecycle": (".start()", "Task.start", "status()"),
    "scale_budget": ("scale", "maxPixels", "tileScale"),
    "joins_composites": ("ee.Join", "saveFirst", "saveAll", "qualityMosaic"),
    "projection_control": ("reproject", "setDefaultProjection", "crs"),
    "client_fetch": ("getInfo", "evaluate("),
}

STYLE_SIGNALS: dict[str, tuple[str, ...]] = {
    "explicit_temporal_scope": ("filterDate", "START_DATE", "END_DATE", "calendarRange"),
    "explicit_spatial_scope": ("filterBounds", "region=", "geometry", "aoi", "AOI"),
    "quality_mask_before_metric": ("updateMask", "QA_PIXEL", "SCL", "cloudMask", "maskCloud"),
    "server_side_mapping": (".map(", "ee.List.sequence", "ee.Date.advance"),
    "explicit_scale_or_projection": ("scale=", "SCALE", "crs=", "projection", "reproject", "setDefaultProjection"),
    "reviewable_export_contract": ("Export.", "selectors", "description=", "fileFormat", "maxPixels"),
    "bounded_client_fetch": ("limit(", "first().getInfo", "size().getInfo", "aggregate_", "sample("),
    "agent_guarded_entrypoint": ('if __name__ == "__main__"', "def main(", "task.start()"),
}

RULE_COVERAGE: dict[str, tuple[str, ...]] = {
    "agent_script_contract": ("auth_init", "collection_filters", "exports", "task_lifecycle", "scale_budget", "client_fetch"),
    "optical_index": ("collection_filters", "quality_masking", "scale_budget", "client_fetch"),
    "export_table_csv": ("exports", "task_lifecycle"),
    "export_image_geotiff": ("exports", "scale_budget", "projection_control", "task_lifecycle"),
    "sentinel1_flood_before_after": ("collection_filters", "reducers", "scale_budget"),
    "dynamic_world_landcover": ("collection_filters", "quality_masking", "reducers"),
}

TEXT_SUFFIXES = {".py", ".js", ".md", ".ipynb"}


@dataclass
class FileHit:
    file: str
    hits: dict[str, int]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _is_candidate(path: Path, max_bytes: int) -> bool:
    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= max_bytes


def analyze_path(path: Path, max_bytes: int = 3_000_000, sample_files: int = 25) -> dict[str, Any]:
    root = path.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    group_counts = {group: {"files": 0, "hits": 0} for group in PATTERN_GROUPS}
    style_counts = {signal: {"files": 0, "hits": 0} for signal in STYLE_SIGNALS}
    pattern_counts = {pattern: 0 for patterns in PATTERN_GROUPS.values() for pattern in patterns}
    hit_files: list[FileHit] = []
    scanned_files = 0

    for file_path in sorted(root.rglob("*")):
        if not _is_candidate(file_path, max_bytes=max_bytes):
            continue
        scanned_files += 1
        text = _read_text(file_path)
        relative = file_path.relative_to(root).as_posix()
        file_hits: dict[str, int] = {}
        for group, patterns in PATTERN_GROUPS.items():
            group_hit_count = 0
            for pattern in patterns:
                count = text.count(pattern)
                if count:
                    pattern_counts[pattern] += count
                    group_hit_count += count
            if group_hit_count:
                group_counts[group]["files"] += 1
                group_counts[group]["hits"] += group_hit_count
                file_hits[group] = group_hit_count
        for signal, patterns in STYLE_SIGNALS.items():
            signal_hit_count = 0
            for pattern in patterns:
                signal_hit_count += text.count(pattern)
            if signal_hit_count:
                style_counts[signal]["files"] += 1
                style_counts[signal]["hits"] += signal_hit_count
        if file_hits and len(hit_files) < sample_files:
            hit_files.append(FileHit(file=relative, hits=file_hits))

    return {
        "path": str(root),
        "scanned_files": scanned_files,
        "pattern_groups": group_counts,
        "style_signals": style_counts,
        "pattern_counts": {key: value for key, value in pattern_counts.items() if value},
        "sample_hit_files": [{"file": item.file, "hits": item.hits} for item in hit_files],
    }


def summarize_rule_gaps(repo_reports: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate = {group: {"files": 0, "hits": 0} for group in PATTERN_GROUPS}
    style_aggregate = {signal: {"files": 0, "hits": 0} for signal in STYLE_SIGNALS}
    for report in repo_reports:
        for group, counts in report["pattern_groups"].items():
            aggregate[group]["files"] += counts["files"]
            aggregate[group]["hits"] += counts["hits"]
        for signal, counts in report["style_signals"].items():
            style_aggregate[signal]["files"] += counts["files"]
            style_aggregate[signal]["hits"] += counts["hits"]
    rule_implications = {}
    for ruleset, groups in RULE_COVERAGE.items():
        observed = {group: aggregate[group] for group in groups}
        weak = [group for group, counts in observed.items() if counts["hits"] == 0]
        rule_implications[ruleset] = {
            "observed_groups": observed,
            "missing_evidence_groups": weak,
            "status": "needs_more_corpus" if weak else "evidence_seen",
        }
    style_gaps = [signal for signal, counts in style_aggregate.items() if counts["hits"] == 0]
    return {
        "aggregate_pattern_groups": aggregate,
        "aggregate_style_signals": style_aggregate,
        "style_exam": {
            "signals": list(STYLE_SIGNALS),
            "missing_signals": style_gaps,
            "status": "needs_more_corpus" if style_gaps else "evidence_seen",
        },
        "rule_implications": rule_implications,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze local GEE corpus checkouts for pattern-only rule learning.")
    parser.add_argument("paths", nargs="+", help="Local repository or tutorial directories to scan.")
    parser.add_argument("--max-bytes", type=int, default=3_000_000)
    parser.add_argument("--sample-files", type=int, default=25)
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    reports = [analyze_path(Path(path), max_bytes=args.max_bytes, sample_files=args.sample_files) for path in args.paths]
    payload = {
        "schema_version": "gee-corpus-audit/v0.1",
        "input_count": len(reports),
        "reports": reports,
        "summary": summarize_rule_gaps(reports),
        "copyright_policy": "Pattern-only analysis. Do not vendor or copy third-party code into this repository.",
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"{payload['schema_version']} {payload['input_count']} -> {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
