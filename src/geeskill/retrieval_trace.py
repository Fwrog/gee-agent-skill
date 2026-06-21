from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .rag import SearchResult


def _evidence_type(result: SearchResult) -> str:
    source = result.source_path.lower()
    title = result.title.lower()
    if "datasets/" in source or "dataset" in title:
        return "dataset_card"
    if "failure" in source or "failure" in title or "error" in title or "risk" in title:
        return "known_failure_case"
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
    if evidence_type == "operator_relationship_chain":
        return "Selected to guide ordering of Earth Engine operators in generated workflow code."
    if evidence_type == "operator_syntax_note":
        return "Selected to confirm method names, arguments, and safe operator usage."
    if evidence_type == "known_failure_case":
        return "Selected to expose likely failure modes and recovery hints for this task."
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
    return {
        "query": query,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence,
        "coverage": {
            "dataset_cards": sum(1 for item in evidence if item["evidence_type"] == "dataset_card"),
            "operator_notes": sum(
                1
                for item in evidence
                if item["evidence_type"] in {"operator_syntax_note", "operator_relationship_chain"}
            ),
            "workflow_patterns": sum(
                1 for item in evidence if item["evidence_type"] == "common_workflow_pattern"
            ),
            "known_failures": sum(
                1 for item in evidence if item["evidence_type"] == "known_failure_case"
            ),
            "export_guidance": sum(
                1
                for item in evidence
                if "export" in (
                    f"{item['source_path']} {item['title']} {item['excerpt']}"
                ).lower()
            ),
        },
    }


def _influence_from_type(evidence_type: str) -> str:
    return {
        "dataset_card": "Dataset selection, band checks, scaling, QA, and caveats.",
        "operator_syntax_note": "Method names, required arguments, and syntax constraints.",
        "operator_relationship_chain": "Operator ordering and workflow skeleton.",
        "common_workflow_pattern": "Reducer/export/aggregation design.",
        "known_failure_case": "Validation rules, error taxonomy, and recovery hints.",
        "documentation_chunk": "General workflow grounding.",
    }[evidence_type]
