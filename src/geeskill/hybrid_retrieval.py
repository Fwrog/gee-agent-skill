from __future__ import annotations

from pathlib import Path
from typing import Any

from .evidence import load_evidence_cards, search_evidence_cards
from .kg import GraphIndex, explain_topic, load_graph, search_nodes, shortest_path
from .paths import default_evidence_cards_dir, default_index_path, default_kg_index_path
from .rag import load_index, results_to_dicts, search


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _quality_summary(cards: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "tier_a_count": 0,
        "tier_b_count": 0,
        "tier_c_count": 0,
        "tier_d_count": 0,
        "unreviewed_count": 0,
    }
    for card in cards:
        tier = str(card.get("trust_tier", "")).lower()
        key = f"tier_{tier}_count"
        if key in summary:
            summary[key] += 1
        if card.get("reviewer_status") != "accepted":
            summary["unreviewed_count"] += 1
    return summary


def _card_bundle(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "card_id": card["card_id"],
        "title": card["title"],
        "trust_tier": card["trust_tier"],
        "confidence": card["confidence"],
        "source_id": card["source_id"],
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


def _prompt_context(query: str, cards: list[dict[str, Any]], required_rules: list[str], failures: list[str], boundaries: list[str]) -> str:
    lines = [
        f"Query: {query}",
        "Use only the evidence ids below. Do not invent dataset IDs, band names, QA bits, scale factors, validation metrics, or result values.",
        "If the evidence is missing or unreviewed, say insufficient evidence.",
    ]
    if cards:
        lines.append("Evidence cards:")
        for card in cards[:8]:
            lines.append(f"- {card['card_id']} (Tier {card['trust_tier']}, {card['confidence']}): {card['title']}")
    else:
        lines.append("Evidence cards: none.")
    if required_rules:
        lines.append("Required rules: " + "; ".join(required_rules))
    if failures:
        lines.append("Known failure cases: " + "; ".join(failures))
    if boundaries:
        lines.append("Claim boundaries: " + "; ".join(boundaries))
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
    card_hits = search_evidence_cards(query, cards, top_k=top_k)
    graph = load_graph(kg_index_path or default_kg_index_path())
    graph_hits = search_nodes(graph, query, top_k=top_k)
    graph_node_ids = [node["id"] for node in graph_hits]
    graph_edges = _related_edges(graph, set(graph_node_ids))
    graph_paths = _graph_paths_to_boundaries(graph, graph_node_ids)
    explanation = explain_topic(graph, query)

    required_rules = _unique(
        [node["title"] for node in graph_hits if node.get("type") == "Rule"]
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
    return {
        "query": query,
        "text_evidence": results_to_dicts(text_results),
        "evidence_cards": evidence_cards,
        "graph_nodes": graph_hits,
        "graph_edges": graph_edges,
        "graph_paths": graph_paths,
        "required_rules": required_rules,
        "known_failure_cases": failures,
        "claim_boundaries": boundaries,
        "source_quality_summary": _quality_summary(card_hits),
        "planner_hints": planner_hints,
        "validator_hints": validator_hints,
        "prompt_context": _prompt_context(query, evidence_cards, required_rules, failures, boundaries),
    }
