#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = " ".join(values).lower()
    return all(str(needle).lower() in haystack for needle in needles)


def _contains_none(values: list[str], needles: list[str]) -> bool:
    haystack = " ".join(values).lower()
    return not any(str(needle).lower() in haystack for needle in needles)


def run_suite(path: Path) -> dict[str, Any]:
    _add_src_to_path()
    from geeskill.hybrid_retrieval import retrieve_hybrid

    suite = yaml.safe_load(path.read_text(encoding="utf-8"))
    kg_index = Path(suite.get("kg_index", "references/index/gee_kg_index.json"))
    results = []
    for case in suite.get("cases", []):
        bundle = retrieve_hybrid(case["query"], kg_index_path=kg_index, top_k=int(case.get("top_k", 8)))
        card_ids = [card["card_id"] for card in bundle["evidence_cards"]]
        node_ids = [node["id"] for node in bundle["graph_nodes"]]
        rules = bundle["required_rules"]
        boundaries = bundle["claim_boundaries"]
        checks = {
            "expected_card_recall": _contains_any(card_ids, case.get("expected_cards", [])),
            "expected_node_recall": _contains_any(node_ids, case.get("expected_nodes", [])),
            "required_rule_recall": _contains_any(rules, case.get("expected_rules", [])),
            "claim_boundary_presence": (not case.get("requires_claim_boundary")) or bool(boundaries),
            "source_tier_correctness": bundle["source_quality_summary"]["tier_a_count"] >= int(case.get("min_tier_a_count", 0)),
            "private_content_absence": "/Users/" not in json.dumps(bundle) and "users/" not in json.dumps(bundle).lower(),
            "deterministic_output_stability": bundle == retrieve_hybrid(case["query"], kg_index_path=kg_index, top_k=int(case.get("top_k", 8))),
            "excluded_card_absence": _contains_none(card_ids, case.get("excluded_cards", [])),
            "excluded_node_absence": _contains_none(node_ids, case.get("excluded_nodes", [])),
        }
        results.append({"id": case["id"], "query": case["query"], "ok": all(checks.values()), "checks": checks})
    return {
        "ok": all(item["ok"] for item in results),
        "schema_version": "gee-kg-rag-eval/v0.1",
        "suite": str(path),
        "case_count": len(results),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run KG-RAG retrieval evaluation suite.")
    parser.add_argument("--suite", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_suite(Path(args.suite))
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else f"{result['schema_version']} ok={result['ok']} cases={result['case_count']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
