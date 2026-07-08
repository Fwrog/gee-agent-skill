from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence import load_evidence_cards, search_evidence_cards
from .kg import GraphIndex, explain_topic, load_graph, search_nodes, shortest_path
from .paths import default_evidence_cards_dir, default_index_path, default_kg_index_path
from .rag import load_index, results_to_dicts, search
from .sources import load_source_registry, source_map


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _quality_summary(cards: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "tier_a_count": 0,
        "tier_b_count": 0,
        "tier_c_count": 0,
        "tier_d_count": 0,
        "accepted_count": 0,
        "candidate_count": 0,
        "unreviewed_count": 0,
        "fresh_count": 0,
        "stale_count": 0,
        "unavailable_count": 0,
        "candidate_unverified_count": 0,
        "insufficient_evidence": False,
        "warnings": [],
    }
    for card in cards:
        tier = str(card.get("trust_tier", "")).lower()
        key = f"tier_{tier}_count"
        if key in summary:
            summary[key] += 1
        status = card.get("reviewer_status")
        if status == "accepted":
            summary["accepted_count"] += 1
        elif status == "candidate":
            summary["candidate_count"] += 1
        if status != "accepted":
            summary["unreviewed_count"] += 1
        refresh = str(card.get("source_refresh_status") or "")
        refresh_key = f"{refresh}_count"
        if refresh_key in summary:
            summary[refresh_key] += 1
    if not cards or summary["accepted_count"] == 0:
        summary["insufficient_evidence"] = True
        summary["warnings"].append("insufficient_evidence: no accepted evidence cards matched the query")
    if summary["stale_count"] or summary["unavailable_count"]:
        summary["warnings"].append("source_refresh_warning: one or more matched sources are stale or unavailable")
    if summary["candidate_count"]:
        summary["warnings"].append("candidate_evidence_present: candidate evidence is contextual only")
    return summary


def _card_bundle(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "card_id": card["card_id"],
        "title": card["title"],
        "trust_tier": card["trust_tier"],
        "confidence": card["confidence"],
        "source_id": card["source_id"],
        "source_url": card.get("source_url"),
        "allowed_use": card.get("allowed_use"),
        "last_checked": card.get("last_checked"),
        "reviewer_status": card.get("reviewer_status"),
        "source_refresh_status": card.get("source_refresh_status"),
        "facts": list(card.get("extracted_facts", [])),
        "limitations": list(card.get("limitations", [])),
        "claim_boundaries": list(card.get("claim_boundaries", [])),
        "planner_hints": list(card.get("planner_hints", [])),
        "validator_hints": list(card.get("validator_hints", [])),
    }


def _related_edges(graph: GraphIndex, node_ids: set[str], limit: int = 40) -> list[dict[str, Any]]:
    edges = [edge for edge in graph.edges if edge["source"] in node_ids or edge["target"] in node_ids]
    return sorted(edges, key=lambda edge: (edge["source"], edge["type"], edge["target"]))[:limit]


def _graph_paths_to_boundaries(graph: GraphIndex, node_ids: list[str]) -> list[list[dict[str, Any]]]:
    boundaries = [node_id for node_id, node in graph.nodes.items() if node.get("type") == "ClaimBoundary"]
    paths: list[list[dict[str, Any]]] = []
    for source_id in node_ids[:5]:
        for boundary_id in boundaries:
            path = shortest_path(graph, source_id, boundary_id)
            if path:
                paths.append(path)
                break
    return paths[:5]


def _classify_query(query: str) -> str:
    lower = query.lower()
    if any(term in lower for term in ("authoritative", "band names", "scale factor", "dataset id", "data catalog")):
        return "dataset_fact"
    if any(term in lower for term in ("validator", "validate", "semantic", "must fail", "should warn")):
        return "validator_check"
    if any(term in lower for term in ("claim boundary", "ground truth", "ground-truth", "product-level consistency", "golden")):
        return "claim_boundary"
    if any(term in lower for term in ("failure", "recover", "fallback", "directly compare", "direct compare", "can i compare", "cannot compare")):
        return "failure_recovery"
    if any(term in lower for term in ("benchmark", "paper", "evaluation design", "research context")):
        return "research_context"
    if any(term in lower for term in ("plan", "workflow", "mapping", "intercomparison", "export", "ndvi", "lst", "flood")):
        return "workflow_planning"
    return "unknown"


def _prompt_context(
    query: str,
    accepted_cards: list[dict[str, Any]],
    candidate_cards: list[dict[str, Any]],
    required_rules: list[str],
    failures: list[str],
    boundaries: list[str],
    warnings: list[str],
) -> str:
    lines = [
        f"Query: {query}",
        "Use only the evidence ids below. Do not invent dataset IDs, band names, QA bits, scale factors, validation metrics, or result values.",
        "Accepted evidence may ground plans. Candidate or unreviewed evidence is contextual only and cannot establish current API or dataset facts.",
        "If accepted evidence is missing or stale, say insufficient evidence.",
    ]
    if accepted_cards:
        lines.append("Accepted evidence cards:")
        for card in accepted_cards[:8]:
            lines.append(
                f"- {card['card_id']} (Tier {card['trust_tier']}, {card['confidence']}, checked {card.get('last_checked')}): {card['title']}"
            )
    else:
        lines.append("Accepted evidence cards: none.")
    if candidate_cards:
        lines.append("Candidate evidence cards:")
        for card in candidate_cards[:5]:
            lines.append(f"- {card['card_id']} (candidate, Tier {card['trust_tier']}): {card['title']}")
    if required_rules:
        lines.append("Required rules: " + "; ".join(required_rules))
    if failures:
        lines.append("Known failure cases: " + "; ".join(failures))
    if boundaries:
        lines.append("Claim boundaries: " + "; ".join(boundaries))
    if warnings:
        lines.append("Warnings: " + "; ".join(warnings))
    return "\n".join(lines)


def retrieve_hybrid(
    query: str,
    *,
    docs_index_path: Path | None = None,
    evidence_cards_dir: Path | None = None,
    kg_index_path: Path | None = None,
    top_k: int = 8,
) -> dict[str, Any]:
    docs_index = load_index(docs_index_path or default_index_path())
    text_results = search(docs_index, query, top_k=top_k)
    cards = load_evidence_cards(evidence_cards_dir or default_evidence_cards_dir())
    sources = source_map(load_source_registry())
    card_hits = search_evidence_cards(query, cards, top_k=top_k)
    for card in card_hits:
        source = sources.get(str(card.get("source_id")))
        if source:
            card.setdefault("source_refresh_status", source.get("source_refresh_status"))
            card.setdefault("source_url", source.get("source_url"))
    graph = load_graph(kg_index_path or default_kg_index_path())
    graph_hits = search_nodes(graph, query, top_k=top_k)
    graph_node_ids = [node["id"] for node in graph_hits]
    graph_edges = _related_edges(graph, set(graph_node_ids))
    graph_paths = _graph_paths_to_boundaries(graph, graph_node_ids)
    explanation = explain_topic(graph, query)

    required_rules = _unique(
        [node["title"] for node in graph_hits if node.get("type") == "Rule"]
        + [
            graph.nodes[node_id]["title"]
            for edge in graph_edges
            for node_id in (edge["source"], edge["target"])
            if node_id in graph.nodes and graph.nodes[node_id].get("type") == "Rule"
        ]
        + [hint for card in card_hits for hint in card.get("validation_implications", [])]
    )
    failures = _unique(
        [node["title"] for node in graph_hits if node.get("type") == "FailureCase"]
        + [failure for card in card_hits for failure in card.get("known_failure_modes", [])]
    )
    boundaries = _unique(
        [node["title"] for node in explanation.get("claim_boundaries", [])]
        + [boundary for card in card_hits for boundary in card.get("claim_boundaries", [])]
    )
    planner_hints = _unique([hint for card in card_hits for hint in card.get("planner_hints", [])])
    validator_hints = _unique([hint for card in card_hits for hint in card.get("validator_hints", [])])
    evidence_cards = [_card_bundle(card) for card in card_hits]
    accepted_evidence_cards = [card for card in evidence_cards if card.get("reviewer_status") == "accepted"]
    candidate_evidence_cards = [card for card in evidence_cards if card.get("reviewer_status") != "accepted"]
    source_quality_summary = _quality_summary(card_hits)
    warnings = list(source_quality_summary.get("warnings", []))
    query_lower = query.lower()
    if "users/" in query_lower or "projects/" in query_lower:
        warnings.append("insufficient_evidence: private Earth Engine asset requests cannot be grounded in the public KG-RAG index")
        source_quality_summary["insufficient_evidence"] = True
    if ("prove" in query_lower or "ground truth" in query_lower or "accuracy" in query_lower) and any(
        term in query_lower for term in ("crop yield", "one ndvi", "product intercomparison")
    ):
        warnings.append("insufficient_evidence: public KG-RAG evidence does not support the requested ground-truth accuracy claim")
        source_quality_summary["insufficient_evidence"] = True
    if not graph_hits:
        warnings.append("insufficient_graph_evidence: no graph nodes matched the query")
    source_quality_summary["warnings"] = _unique(warnings)
    return {
        "query": query,
        "query_classification": _classify_query(query),
        "text_evidence": results_to_dicts(text_results),
        "evidence_cards": evidence_cards,
        "accepted_evidence_cards": accepted_evidence_cards,
        "candidate_evidence_cards": candidate_evidence_cards,
        "graph_nodes": graph_hits,
        "graph_edges": graph_edges,
        "graph_paths": graph_paths,
        "required_rules": required_rules,
        "known_failure_cases": failures,
        "claim_boundaries": boundaries,
        "source_quality_summary": source_quality_summary,
        "planner_hints": planner_hints,
        "validator_hints": validator_hints,
        "warnings": _unique(warnings),
        "prompt_context": _prompt_context(query, accepted_evidence_cards, candidate_evidence_cards, required_rules, failures, boundaries, _unique(warnings)),
    }
