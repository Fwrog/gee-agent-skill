from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

import yaml

from .evidence import load_evidence_cards
from .paths import default_graph_seed_path, default_kg_index_path
from .sources import load_source_registry


ValidationReport = dict[str, Any]

NODE_TYPES = {
    "Source",
    "EvidenceCard",
    "Dataset",
    "Band",
    "QAField",
    "ScaleFactor",
    "Operator",
    "Recipe",
    "Workflow",
    "ValidationDemo",
    "Metric",
    "Rule",
    "FailureCase",
    "RecoveryPattern",
    "Claim",
    "ClaimBoundary",
    "Script",
    "Test",
    "OutputArtifact",
    "EvaluationCase",
    "PlannerHint",
    "ValidatorHint",
}
EDGE_TYPES = {
    "cites_source",
    "extracted_from",
    "supports_claim",
    "limits_claim",
    "uses_dataset",
    "has_band",
    "has_qa_field",
    "requires_scale_factor",
    "uses_operator",
    "requires_rule",
    "has_failure_mode",
    "recovers_by",
    "implemented_in",
    "tested_by",
    "validated_by",
    "reports_metric",
    "depends_on",
    "contradicts",
    "generalizes_to",
    "evaluated_by",
    "derived_from",
    "grounded_by",
    "invalidates",
    "warns_about",
    "suitable_for",
    "unsuitable_for",
}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.:/-]*$")
PRIVATE_RE = re.compile(
    r"(/Users/|/Volumes/|C:\\Users\\|users/[A-Za-z0-9_.-]+/|projects/[^/\s]+/assets/[^,\s]+|AIza[0-9A-Za-z_-]{20,}|ya29\.)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GraphIndex:
    schema_version: str
    nodes: dict[str, dict[str, Any]]
    edges: list[dict[str, Any]]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "metadata": self.metadata,
            "nodes": [self.nodes[node_id] for node_id in sorted(self.nodes)],
            "edges": sorted(self.edges, key=lambda edge: (edge["source"], edge["type"], edge["target"])),
        }


def _tokenize(text: str) -> set[str]:
    return set(_normalize(text).split())


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower().replace("_", " ").replace("/", " ").replace("-", " ")))


def _node_text(node: dict[str, Any]) -> str:
    return json.dumps(node, sort_keys=True, ensure_ascii=False)


def _stable_node_id(prefix: str, raw: str) -> str:
    value = raw.lower().replace(" ", "_")
    value = re.sub(r"[^a-z0-9_.:/-]+", "_", value).strip("_")
    return f"{prefix}:{value}"


def _portable_source_path(path: Path) -> str:
    """Persist repository-relative provenance paths across Windows and POSIX."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_graph(path: Path | None = None) -> GraphIndex:
    graph_path = path or default_kg_index_path()
    if not graph_path.exists():
        raise FileNotFoundError(f"Knowledge graph index not found: {graph_path}. Run scripts/build_kg.py first.")
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        raise ValueError(f"Knowledge graph nodes must be a list: {graph_path}")
    return GraphIndex(
        schema_version=str(data.get("schema_version", "gee-kg/v0.1")),
        nodes={str(node["id"]): node for node in nodes},
        edges=list(data.get("edges", [])),
        metadata=dict(data.get("metadata", {})),
    )


def build_graph(
    *,
    source_registry_path: Path | None = None,
    evidence_cards_dir: Path | None = None,
    seed_graph_path: Path | None = None,
) -> GraphIndex:
    registry = load_source_registry(source_registry_path)
    cards = load_evidence_cards(evidence_cards_dir)
    seed_path = seed_graph_path or default_graph_seed_path()
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8")) if seed_path.exists() else {}
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for source in registry["sources"]:
        node_id = f"source:{source['source_id']}"
        nodes[node_id] = {
            "id": node_id,
            "type": "Source",
            "title": source["title"],
            "description": source["include_reason"],
            "tags": [source["source_type"], f"tier_{source['trust_tier'].lower()}", source["reviewer_status"]],
            "metadata": source,
        }

    for card in cards:
        node_id = f"evidence:{card.card_id}"
        nodes[node_id] = {
            "id": node_id,
            "type": "EvidenceCard",
            "title": card.title,
            "description": " ".join(card.extracted_facts[:2]),
            "tags": list(card.topics) + [card.reviewer_status, f"tier_{card.trust_tier.lower()}"],
            "metadata": card.to_dict(),
        }
        edges.append(
            {
                "source": node_id,
                "target": f"source:{card.source_id}",
                "type": "cites_source",
                "description": "Evidence card cites reviewed source metadata.",
            }
        )
        for dataset in card.applicable_datasets:
            dataset_id = _stable_node_id("dataset", dataset)
            nodes.setdefault(
                dataset_id,
                {
                    "id": dataset_id,
                    "type": "Dataset",
                    "title": dataset,
                    "description": "Dataset referenced by evidence cards.",
                    "tags": ["dataset"],
                    "metadata": {"dataset_id": dataset},
                },
            )
            edges.append({"source": node_id, "target": dataset_id, "type": "uses_dataset", "description": "Evidence applies to dataset."})

    for node in seed.get("nodes", []) or []:
        nodes[str(node["id"])] = {
            "id": str(node["id"]),
            "type": str(node["type"]),
            "title": str(node.get("title", node["id"])),
            "description": str(node.get("description", "")),
            "tags": list(node.get("tags", [])),
            "metadata": dict(node.get("metadata", {})),
        }
    for edge in seed.get("edges", []) or []:
        edges.append(
            {
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "type": str(edge["type"]),
                "description": str(edge.get("description", "")),
            }
        )

    return GraphIndex(
        schema_version="gee-kg/v0.1",
        nodes=nodes,
        edges=sorted(_dedupe_edges(edges), key=lambda edge: (edge["source"], edge["type"], edge["target"])),
        metadata={
            "source_count": len(registry["sources"]),
            "evidence_card_count": len(cards),
            "seed_path": _portable_source_path(seed_path),
        },
    )


def _dedupe_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result = []
    for edge in edges:
        key = (str(edge["source"]), str(edge["type"]), str(edge["target"]))
        if key in seen:
            continue
        seen.add(key)
        result.append(edge)
    return result


def write_graph_index(graph: GraphIndex, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_graph(graph: GraphIndex) -> ValidationReport:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for node_id, node in graph.nodes.items():
        if not ID_RE.fullmatch(node_id):
            errors.append({"node_id": node_id, "code": "unstable-node-id", "message": "Node ids must be lowercase-ish and stable."})
        if node.get("type") not in NODE_TYPES:
            errors.append({"node_id": node_id, "code": "unknown-node-type", "message": str(node.get("type"))})
        if PRIVATE_RE.search(_node_text(node)):
            errors.append({"node_id": node_id, "code": "private-or-secret-looking-content", "message": "Public graph cannot contain private paths, asset ids, or secrets."})
        if node.get("type") == "Dataset":
            grounded = any(edge["source"] == node_id and edge["type"] == "grounded_by" for edge in graph.edges) or any(
                edge["target"] == node_id and edge["type"] in {"uses_dataset", "grounded_by"} for edge in graph.edges
            )
            if not grounded:
                warnings.append({"node_id": node_id, "code": "dataset-without-grounding-edge", "message": "Dataset node should be grounded by Tier A evidence."})
    node_ids = set(graph.nodes)
    for edge in graph.edges:
        edge_ref = f"{edge.get('source')}->{edge.get('target')}"
        if edge.get("type") not in EDGE_TYPES:
            errors.append({"edge": edge_ref, "code": "unknown-edge-type", "message": str(edge.get("type"))})
        if edge.get("source") not in node_ids:
            errors.append({"edge": edge_ref, "code": "missing-edge-source", "message": str(edge.get("source"))})
        if edge.get("target") not in node_ids:
            errors.append({"edge": edge_ref, "code": "missing-edge-target", "message": str(edge.get("target"))})
    for node_id, node in graph.nodes.items():
        if node.get("type") == "EvidenceCard" and not any(edge["source"] == node_id and edge["type"] == "cites_source" for edge in graph.edges):
            errors.append({"node_id": node_id, "code": "evidence-without-source", "message": "EvidenceCard nodes must cite a Source."})
        if node.get("type") == "Claim":
            has_support = any(edge["target"] == node_id and edge["type"] == "supports_claim" for edge in graph.edges)
            has_limit = any(edge["source"] == node_id and edge["type"] in {"limits_claim", "grounded_by"} for edge in graph.edges)
            if not has_support:
                errors.append({"node_id": node_id, "code": "claim-without-support", "message": "Claim nodes need support."})
            if not has_limit:
                errors.append({"node_id": node_id, "code": "claim-without-boundary", "message": "Claim nodes need a claim boundary."})
        if node.get("type") == "ValidationDemo" and str(node.get("metadata", {}).get("status", "")).lower() == "golden":
            has_boundary = any(edge["source"] == node_id and edge["type"] in {"limits_claim", "grounded_by"} for edge in graph.edges)
            if not has_boundary:
                errors.append({"node_id": node_id, "code": "golden-demo-without-boundary", "message": "Golden demos must link to claim boundaries."})
    return {
        "ok": not errors,
        "schema_version": graph.schema_version,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "errors": errors,
        "warnings": warnings,
    }


def search_nodes(graph: GraphIndex, query: str, top_k: int = 10) -> list[dict[str, Any]]:
    query_terms = _tokenize(query)
    if not query_terms:
        raise ValueError("Query is empty after tokenization.")
    query_norm = _normalize(query)
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for node_id, node in graph.nodes.items():
        score = _score_node(query_norm, query_terms, node_id, node)
        if score:
            scored.append((score, node_id, node))
    return [{"score": score, **node} for score, _node_id, node in sorted(scored, key=lambda item: (-item[0], item[1]))[:top_k]]


def _terms_score(terms: set[str], text: str, weight: int) -> int:
    normalized = _normalize(text)
    return weight * sum(1 for term in terms if term in normalized)


def _node_negative_penalty(query_norm: str, node: dict[str, Any]) -> int:
    node_text = _normalize(_node_text(node))
    penalty = 0
    if "flood" in query_norm and ("product intercomparison" in node_text or "modis ndvi" in node_text):
        penalty += 120
    if "product intercomparison" in query_norm and "flood" in node_text:
        penalty += 120
    for negative in node.get("metadata", {}).get("negative_queries", []) or []:
        negative_norm = _normalize(str(negative))
        if negative_norm and negative_norm in query_norm:
            penalty += 200
    return penalty


def _score_node(query_norm: str, terms: set[str], node_id: str, node: dict[str, Any]) -> int:
    node_id_norm = _normalize(node_id)
    title_norm = _normalize(str(node.get("title", "")))
    metadata = node.get("metadata", {}) or {}
    score = 0
    if query_norm == node_id_norm or query_norm == title_norm:
        score += 1000
    if node_id_norm and node_id_norm in query_norm:
        score += 500
    if title_norm and (title_norm in query_norm or query_norm in title_norm):
        score += 250
    score += _terms_score(terms, " ".join(str(item) for item in metadata.get("canonical_terms", []) or []), 70)
    score += _terms_score(terms, " ".join(str(item) for item in metadata.get("aliases", []) or []), 70)
    score += _terms_score(terms, " ".join(str(item) for item in node.get("tags", []) or []), 35)
    score += _terms_score(terms, str(node.get("description", "")), 20)
    score += _terms_score(terms, json.dumps(metadata, sort_keys=True, ensure_ascii=False), 10)
    if "modis scale factor" in query_norm and "0 0001" in _normalize(_node_text(node)):
        score += 75
    if "hls fmask" in query_norm and "fmask" in _normalize(_node_text(node)):
        score += 75
    if "fine coarse comparison" in query_norm and all(term in _normalize(_node_text(node)) for term in ("fine", "coarse")):
        score += 75
    if "product intercomparison" in query_norm and "product intercomparison" in _normalize(_node_text(node)):
        score += 75
    if "reduceresolution projection" in query_norm and all(term in _normalize(_node_text(node)) for term in ("reduceresolution", "projection")):
        score += 75
    if "ground truth validation" in query_norm and ("ground truth" in _normalize(_node_text(node)) or "ground truth" in title_norm):
        score += 75
    if "sentinel 1 flood" in query_norm and all(term in _normalize(_node_text(node)) for term in ("sentinel", "flood")):
        score += 75
    if "flood" in query_norm and "mapping" in query_norm and node_id == "workflow:flood_mapping":
        score += 400
    if "direct" in query_norm and "compare" in query_norm and node.get("type") == "FailureCase":
        score += 220
    if "golden" in query_norm and str(metadata.get("status", "")).lower() == "golden":
        score += 220
    if "script" in query_norm and node.get("type") == "Script":
        score += 260
    if "v0 3" in query_norm and node.get("type") in {"Script", "ValidationDemo"}:
        score += 160
    if "sentinel 2" in query_norm and node.get("type") == "Dataset" and "copernicus s2" in _normalize(_node_text(node)):
        score += 180
    score -= _node_negative_penalty(query_norm, node)
    return max(score, 0)


def neighbors(graph: GraphIndex, node_id: str, depth: int = 1) -> dict[str, Any]:
    if node_id not in graph.nodes:
        raise KeyError(f"Unknown node: {node_id}")
    seen = {node_id}
    frontier = {node_id}
    selected_edges: list[dict[str, Any]] = []
    for _ in range(depth):
        next_frontier: set[str] = set()
        for edge in graph.edges:
            if edge["source"] in frontier or edge["target"] in frontier:
                selected_edges.append(edge)
                other = edge["target"] if edge["source"] in frontier else edge["source"]
                if other not in seen:
                    seen.add(other)
                    next_frontier.add(other)
        frontier = next_frontier
    return {"nodes": [graph.nodes[item] for item in sorted(seen)], "edges": sorted(selected_edges, key=lambda edge: (edge["source"], edge["type"], edge["target"]))}


def shortest_path(graph: GraphIndex, source_id: str, target_id: str) -> list[dict[str, Any]]:
    if source_id not in graph.nodes or target_id not in graph.nodes:
        raise KeyError("Both source_id and target_id must exist in the graph.")
    adjacency: dict[str, list[tuple[str, dict[str, Any]]]] = {node_id: [] for node_id in graph.nodes}
    for edge in graph.edges:
        adjacency[edge["source"]].append((edge["target"], edge))
        adjacency[edge["target"]].append((edge["source"], edge))
    queue = deque([(source_id, [])])
    seen = {source_id}
    while queue:
        current, path = queue.popleft()
        if current == target_id:
            return path
        for nxt, edge in sorted(adjacency[current], key=lambda item: item[0]):
            if nxt in seen:
                continue
            seen.add(nxt)
            queue.append((nxt, path + [edge]))
    return []


def explain_topic(graph: GraphIndex, topic: str) -> dict[str, Any]:
    matches = search_nodes(graph, topic, top_k=8)
    node_ids = [node["id"] for node in matches]
    topic_edges = [edge for edge in graph.edges if edge["source"] in node_ids or edge["target"] in node_ids]
    claim_boundaries = [
        graph.nodes[edge["target"]]
        for edge in topic_edges
        if edge["target"] in graph.nodes and graph.nodes[edge["target"]].get("type") == "ClaimBoundary"
    ]
    return {
        "topic": topic,
        "nodes": matches,
        "edges": sorted(topic_edges, key=lambda edge: (edge["source"], edge["type"], edge["target"]))[:30],
        "claim_boundaries": claim_boundaries,
        "summary": _topic_summary(topic, matches, claim_boundaries),
    }


def _topic_summary(topic: str, nodes: list[dict[str, Any]], boundaries: list[dict[str, Any]]) -> str:
    if not nodes:
        return f"No graph evidence found for {topic}; return insufficient evidence."
    boundary_text = "; ".join(boundary["title"] for boundary in boundaries) or "No explicit claim boundary found in top graph hits."
    return f"Graph explanation for {topic}: {len(nodes)} relevant nodes. Claim boundaries: {boundary_text}"


def graph_to_mermaid(graph: GraphIndex, focus_node: str | None = None) -> str:
    if focus_node:
        subgraph = neighbors(graph, focus_node, depth=1)
        nodes = {node["id"]: node for node in subgraph["nodes"]}
        edges = subgraph["edges"]
    else:
        nodes = graph.nodes
        edges = graph.edges[:80]
    lines = ["graph LR"]
    for node_id, node in sorted(nodes.items()):
        label = f"{node['type']}: {node['title']}".replace('"', "'")
        lines.append(f'  {node_id.replace(":", "_").replace("/", "_").replace("-", "_")}["{label}"]')
    for edge in edges:
        if edge["source"] not in nodes or edge["target"] not in nodes:
            continue
        source = edge["source"].replace(":", "_").replace("/", "_").replace("-", "_")
        target = edge["target"].replace(":", "_").replace("/", "_").replace("-", "_")
        lines.append(f'  {source} -- "{edge["type"]}" --> {target}')
    return "\n".join(lines)
