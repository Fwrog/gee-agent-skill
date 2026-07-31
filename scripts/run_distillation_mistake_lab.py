#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def run_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    root = path.parent.parent
    known_targets: set[str] = set()
    for card_path in (root / "references" / "evidence_cards").glob("*.yml"):
        card_data = yaml.safe_load(card_path.read_text(encoding="utf-8")) or {}
        known_targets.update(str(card["card_id"]) for card in card_data.get("cards", []))
    for rule_path in (root / "references" / "knowledge_base" / "rules").glob("*.md"):
        for line in rule_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("rule_id:"):
                known_targets.add(line.split(":", 1)[1].strip())
    results = []
    important_misses = 0
    general_misses = 0
    targets: set[str] = set()

    for case in data["cases"]:
        observed = set(case["naive_observations"])
        missed = [item for item in case["required_observations"] if item["id"] not in observed]
        actual_ids = [item["id"] for item in missed]
        expected_ids = case["expected_missed_ids"]
        important = [item for item in missed if item["importance"] == "important_knowledge"]
        general = [item for item in missed if item["importance"] == "general_knowledge"]
        missing_targets = sorted(
            {
                item["distill_to"]
                for item in important
                if item["distill_to"] not in known_targets
            }
        )
        important_misses += len(important)
        general_misses += len(general)
        targets.update(item["distill_to"] for item in important)
        results.append(
            {
                "id": case["id"],
                "status": "passed" if actual_ids == expected_ids and not missing_targets else "failed",
                "simulated_failure": case["simulated_failure"],
                "promotion_decision": case["promotion_decision"],
                "missed_ids": actual_ids,
                "important_misses": [item["id"] for item in important],
                "general_misses": [item["id"] for item in general],
                "missing_distillation_targets": missing_targets,
            }
        )

    return {
        "ok": all(item["status"] == "passed" for item in results),
        "schema_version": "gee-distillation-mistake-report/v0.1",
        "suite": data["id"],
        "summary": {
            "case_count": len(results),
            "passed": sum(item["status"] == "passed" for item in results),
            "important_misses": important_misses,
            "general_misses": general_misses,
            "important_distillation_targets": sorted(targets),
            "known_distillation_target_count": len(known_targets),
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the reproducible knowledge-distillation mistake lab.")
    parser.add_argument("--suite", default="evals/distillation_mistake_suite.yml")
    parser.add_argument("--out")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = run_suite(Path(args.suite))
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text if args.json else f"{report['schema_version']} ok={report['ok']} cases={report['summary']['case_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
