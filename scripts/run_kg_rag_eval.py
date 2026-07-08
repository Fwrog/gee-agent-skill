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


def _run_retrieval_suite(path: Path, suite: dict[str, Any]) -> dict[str, Any]:
    _add_src_to_path()
    from geeskill.hybrid_retrieval import retrieve_hybrid

    kg_index = Path(suite.get("kg_index", "references/index/gee_kg_index.json"))
    results = []
    for case in suite.get("cases", []):
        bundle = retrieve_hybrid(case["query"], kg_index_path=kg_index, top_k=int(case.get("top_k", 8)))
        card_ids = [card["card_id"] for card in bundle["evidence_cards"]]
        accepted_card_ids = [card["card_id"] for card in bundle.get("accepted_evidence_cards", [])]
        node_ids = [node["id"] for node in bundle["graph_nodes"]]
        rules = bundle["required_rules"]
        boundaries = bundle["claim_boundaries"]
        scanned_bundle = {
            key: value
            for key, value in bundle.items()
            if key not in {"query", "prompt_context", "warnings"}
        }
        bundle_text = json.dumps(scanned_bundle, sort_keys=True, ensure_ascii=False)
        checks = {
            "expected_card_recall": _contains_any(card_ids, case.get("expected_cards", [])),
            "expected_node_recall": _contains_any(node_ids, case.get("expected_nodes", [])),
            "required_rule_recall": _contains_any(rules, case.get("expected_rules", [])),
            "claim_boundary_presence": (not case.get("requires_claim_boundary")) or bool(boundaries),
            "source_tier_correctness": bundle["source_quality_summary"]["tier_a_count"] >= int(case.get("min_tier_a_count", 0)),
            "accepted_evidence_presence": (not case.get("requires_accepted_evidence")) or bool(accepted_card_ids),
            "query_classification": (not case.get("expected_query_classification")) or bundle.get("query_classification") == case.get("expected_query_classification"),
            "bundle_quality_fields": all(field in bundle for field in case.get("required_bundle_fields", [])),
            "insufficient_evidence_warning": (not case.get("requires_insufficient_evidence_warning")) or any("insufficient_evidence" in item for item in bundle.get("warnings", [])),
            "private_content_absence": "/Users/" not in bundle_text and "users/" not in bundle_text.lower(),
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


def _run_planner_grounding_suite(path: Path, suite: dict[str, Any]) -> dict[str, Any]:
    _add_src_to_path()
    from geeskill.hybrid_retrieval import retrieve_hybrid
    from geeskill.planner import build_plan
    from geeskill.rag import load_index, search

    docs_index = load_index(Path(suite.get("docs_index", "references/index/gee_docs_index.json")))
    kg_index = Path(suite.get("kg_index", "references/index/gee_kg_index.json"))
    results = []
    for case in suite.get("cases", []):
        query = case["query"]
        hits = search(docs_index, query, top_k=int(case.get("top_k", 8)))
        bundle = retrieve_hybrid(query, kg_index_path=kg_index, top_k=int(case.get("top_k", 8)))
        plan = build_plan(query, hits, hybrid_bundle=bundle).body
        combined = "\n".join([plan, bundle.get("prompt_context", ""), json.dumps(bundle, ensure_ascii=False)])
        checks = {
            "must_include": _contains_any([combined], case.get("must_include", [])),
            "must_not_include": _contains_none([combined], case.get("must_not_include", [])),
            "source_quality_summary": bool(bundle.get("source_quality_summary")),
            "required_rules": bool(bundle.get("required_rules")) or not case.get("requires_rules"),
            "claim_boundaries": bool(bundle.get("claim_boundaries")) or not case.get("requires_claim_boundary"),
            "no_excluded_workflow_contamination": _contains_none([combined], case.get("excluded_terms", [])),
        }
        results.append({"id": case["id"], "query": query, "ok": all(checks.values()), "checks": checks})
    return {
        "ok": all(item["ok"] for item in results),
        "schema_version": str(suite.get("schema_version", "gee-planner-grounding-eval/v0.1")),
        "suite": str(path),
        "case_count": len(results),
        "results": results,
    }


def _run_semantic_fixture_suite(path: Path, suite: dict[str, Any]) -> dict[str, Any]:
    _add_src_to_path()
    from geeskill.semantic import validate_semantics

    results = []
    for case in suite.get("cases", []):
        findings = validate_semantics(Path(case["fixture"]), list(case.get("rulesets", ["product_intercomparison"])))
        codes = [finding.code for finding in findings]
        checks = {
            "expected_error_codes": _contains_any(codes, case.get("expected_error_codes", [])),
            "absent_error_codes": _contains_none(codes, case.get("absent_error_codes", [])),
            "ok_expected": (not case.get("expect_ok")) or ("semantic-validation-ok" in codes and not [finding for finding in findings if finding.severity == "error"]),
        }
        results.append({"id": case["id"], "fixture": case["fixture"], "ok": all(checks.values()), "codes": codes, "checks": checks})
    return {
        "ok": all(item["ok"] for item in results),
        "schema_version": str(suite.get("schema_version", "gee-semantic-fixture-eval/v0.1")),
        "suite": str(path),
        "case_count": len(results),
        "results": results,
    }


def run_suite(path: Path) -> dict[str, Any]:
    suite = yaml.safe_load(path.read_text(encoding="utf-8"))
    schema = str(suite.get("schema_version", ""))
    if "planner-grounding" in schema:
        return _run_planner_grounding_suite(path, suite)
    if "semantic-fixture" in schema:
        return _run_semantic_fixture_suite(path, suite)
    return _run_retrieval_suite(path, suite)


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
