from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .rag import SearchResult


def _evidence_type(result: SearchResult) -> str:
    source = result.source_path.lower()
    title = result.title.lower()
    metadata = result.metadata or {}
    source_type = str(metadata.get("source_type") or "").lower()
    method_name = str(metadata.get("method_name") or "").lower()
    if "export" in source_type or "export" in method_name:
        return "export_guidance_card"
    if "dataset" in source_type:
        return "dataset_card"
    if "recipe" in source_type:
        return "recipe_card"
    if "failure" in source_type:
        return "known_failure_case"
    if "workflow" in source_type:
        return "common_workflow_pattern"
    if "operator-chain" in source_type:
        return "operator_relationship_chain"
    if "operator" in source_type:
        return "operator_syntax_note"
    if "recipes/" in source or "recipe" in title:
        return "recipe_card"
    if "rules/" in source or "rule" in title or "ruleset" in title:
        return "validation_rule_card"
    if "datasets/" in source or "dataset" in title:
        return "dataset_card"
    if "failure" in source or "failure" in title or "error" in title or "risk" in title:
        return "known_failure_case"
    if "export" in source or "export" in title:
        return "export_guidance_card"
    if "relationship" in title or "chain" in title or "pattern" in title:
        return "operator_relationship_chain"
    if "operator" in source or "syntax" in title:
        return "operator_syntax_note"
    if "workflow" in title or "reduce" in title or "export" in title:
        return "common_workflow_pattern"
    return "documentation_chunk"


def _reason(query: str, result: SearchResult) -> str:
    evidence_type = _evidence_type(result)
    if evidence_type == "dataset_card":
        return "Selected to verify dataset id, bands, QA caveats, and collection-specific assumptions."
    if evidence_type == "recipe_card":
        return "Selected to match the request to a reusable workflow recipe and its required inputs."
    if evidence_type == "validation_rule_card":
        return "Selected to ground validation rules and live-execution safety gates."
    if evidence_type == "operator_relationship_chain":
        return "Selected to guide ordering of Earth Engine operators in generated workflow code."
    if evidence_type == "operator_syntax_note":
        return "Selected to confirm method names, arguments, and safe operator usage."
    if evidence_type == "known_failure_case":
        return "Selected to expose likely failure modes and recovery hints for this task."
    if evidence_type == "export_guidance_card":
        return "Selected to verify export destination, schema, task lifecycle, and monitoring assumptions."
    if evidence_type == "common_workflow_pattern":
        return "Selected because it matches the workflow pattern requested by the task."
    return f"Selected by BM25 retrieval for query: {query}"


def build_retrieval_trace(query: str, results: list[SearchResult]) -> dict[str, Any]:
    evidence = []
    for result in results:
        metadata = result.metadata or {}
        evidence.append(
            {
                "chunk_id": result.chunk_id,
                "source_path": result.source_path,
                "title": result.title,
                "score": result.score,
                "evidence_type": _evidence_type(result),
                "source_url": metadata.get("source_url") or result.url,
                "last_checked": metadata.get("retrieved_at") or metadata.get("last_checked"),
                "primary_status": metadata.get("primary_status"),
                "dataset_id": metadata.get("dataset_id"),
                "method_name": metadata.get("method_name"),
                "operator_chain": metadata.get("operator_chain"),
                "known_failure": metadata.get("known_failure") or metadata.get("risk_level"),
                "reason_for_selection": _reason(query, result),
                "influence": _influence_from_type(_evidence_type(result)),
                "excerpt": result.excerpt,
            }
        )
    dataset_count = sum(1 for item in evidence if item["evidence_type"] == "dataset_card")
    recipe_count = sum(1 for item in evidence if item["evidence_type"] == "recipe_card")
    rule_count = sum(1 for item in evidence if item["evidence_type"] == "validation_rule_card")
    operator_count = sum(
        1
        for item in evidence
        if item["evidence_type"] in {"operator_syntax_note", "operator_relationship_chain"}
    )
    workflow_count = sum(1 for item in evidence if item["evidence_type"] == "common_workflow_pattern")
    failure_count = sum(1 for item in evidence if item["evidence_type"] == "known_failure_case")
    export_count = sum(
        1
        for item in evidence
        if item["evidence_type"] == "export_guidance_card"
        or "export" in (f"{item['source_path']} {item['title']} {item['excerpt']}").lower()
    )
    coverage = {
        "dataset_cards": dataset_count,
        "recipe_cards": recipe_count,
        "rule_cards": rule_count,
        "operator_notes": operator_count,
        "workflow_patterns": workflow_count,
        "known_failures": failure_count,
        "export_guidance": export_count,
        "dataset_evidence": dataset_count,
        "operator_evidence": operator_count,
        "recipe_evidence": recipe_count,
        "failure_evidence": failure_count,
        "rule_evidence": rule_count,
        "export_evidence": export_count,
    }
    return {
        "query": query,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence,
        "coverage": coverage,
    }


def _influence_from_type(evidence_type: str) -> str:
    return {
        "dataset_card": "Dataset selection, band checks, scaling, QA, and caveats.",
        "recipe_card": "Task decomposition, required inputs, default dataset policy, and output schema.",
        "validation_rule_card": "Static/semantic validation and live-execution safety gates.",
        "operator_syntax_note": "Method names, required arguments, and syntax constraints.",
        "operator_relationship_chain": "Operator ordering and workflow skeleton.",
        "common_workflow_pattern": "Reducer/export/aggregation design.",
        "known_failure_case": "Validation rules, error taxonomy, and recovery hints.",
        "export_guidance_card": "Export schema, destination metadata, task lifecycle, and monitoring.",
        "documentation_chunk": "General workflow grounding.",
    }[evidence_type]
