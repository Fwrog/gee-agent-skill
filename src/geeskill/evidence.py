from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

import yaml

from .paths import default_evidence_cards_dir
from .sources import ALLOWED_USE, SOURCE_REFRESH_STATUSES, TRUST_TIERS, load_source_registry, source_map


@dataclass(frozen=True)
class EvidenceCard:
    card_id: str
    title: str
    source_id: str
    source_url: str
    source_type: str
    trust_tier: str
    allowed_use: str
    topics: tuple[str, ...]
    extracted_facts: tuple[str, ...]
    extracted_patterns: tuple[str, ...]
    limitations: tuple[str, ...]
    claim_boundaries: tuple[str, ...]
    applicable_workflows: tuple[str, ...]
    applicable_datasets: tuple[str, ...]
    applicable_operators: tuple[str, ...]
    known_failure_modes: tuple[str, ...]
    validation_implications: tuple[str, ...]
    planner_hints: tuple[str, ...]
    validator_hints: tuple[str, ...]
    citation: str
    last_checked: str
    reviewer_status: str
    confidence: str
    private_content_risk: str
    canonical_terms: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    negative_queries: tuple[str, ...] = ()
    source_refresh_status: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = self.__dict__.copy()
        for key, value in list(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data


LIST_FIELDS = {
    "topics",
    "extracted_facts",
    "extracted_patterns",
    "limitations",
    "claim_boundaries",
    "applicable_workflows",
    "applicable_datasets",
    "applicable_operators",
    "known_failure_modes",
    "validation_implications",
    "planner_hints",
    "validator_hints",
    "canonical_terms",
    "aliases",
    "negative_queries",
}
REQUIRED_FIELDS = {
    "card_id",
    "title",
    "source_id",
    "source_url",
    "source_type",
    "trust_tier",
    "allowed_use",
    *LIST_FIELDS,
    "citation",
    "last_checked",
    "reviewer_status",
    "confidence",
    "private_content_risk",
}
OPTIONAL_FIELDS = {"canonical_terms", "aliases", "negative_queries", "source_refresh_status"}
CARD_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS
PHRASE_BOOSTS = {
    "modis scale factor": ("modis", "scale", "factor", "0.0001"),
    "hls fmask": ("hls", "fmask"),
    "fine coarse comparison": ("fine", "coarse", "comparison"),
    "product intercomparison": ("product", "intercomparison"),
    "reduceresolution projection": ("reduceresolution", "projection"),
    "ground truth validation": ("ground", "truth", "validation"),
    "sentinel-1 flood": ("sentinel", "1", "flood"),
}
PRIVATE_TEXT_RE = re.compile(r"(/Users/|/Volumes/|C:\\Users\\|users/[A-Za-z0-9_.-]+/|drive\\.google\\.com/drive/folders/)", re.IGNORECASE)


def _cards_from_file(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data:
        return []
    if isinstance(data, dict) and isinstance(data.get("cards"), list):
        return data["cards"]
    if isinstance(data, dict) and data.get("card_id"):
        return [data]
    raise ValueError(f"Evidence card file must contain a card mapping or cards list: {path}")


def load_evidence_cards(cards_dir: Path | None = None) -> list[EvidenceCard]:
    root = cards_dir or default_evidence_cards_dir()
    if not root.exists():
        raise FileNotFoundError(f"Evidence cards directory not found: {root}")
    sources = source_map(load_source_registry())
    cards: list[EvidenceCard] = []
    for path in sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml")):
        for raw in _cards_from_file(path):
            normalized = dict(raw)
            for field in LIST_FIELDS:
                value = normalized.get(field) or []
                if isinstance(value, str):
                    value = [value]
                normalized[field] = tuple(str(item) for item in value)
            source = sources.get(str(normalized.get("source_id")))
            if not normalized.get("source_refresh_status") and source:
                normalized["source_refresh_status"] = str(source.get("source_refresh_status", ""))
            payload = {field: normalized.get(field) for field in CARD_FIELDS}
            for field in OPTIONAL_FIELDS & LIST_FIELDS:
                payload.setdefault(field, ())
            payload.setdefault("source_refresh_status", "")
            cards.append(EvidenceCard(**payload))
    return cards


def validate_evidence_cards(cards_dir: Path | None = None, source_registry_path: Path | None = None) -> dict[str, Any]:
    root = cards_dir or default_evidence_cards_dir()
    registry = load_source_registry(source_registry_path)
    sources = source_map(registry)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: set[str] = set()
    raw_cards: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml")):
        for raw in _cards_from_file(path):
            raw_cards.append(raw)
            card_id = str(raw.get("card_id") or f"{path.name}:unknown")
            missing = sorted(field for field in REQUIRED_FIELDS if raw.get(field) in (None, ""))
            if missing:
                errors.append({"card_id": card_id, "code": "missing-required-fields", "message": ", ".join(missing)})
                continue
            if card_id in seen:
                errors.append({"card_id": card_id, "code": "duplicate-card-id", "message": "card_id must be unique."})
            seen.add(card_id)
            source = sources.get(str(raw["source_id"]))
            if not source:
                errors.append({"card_id": card_id, "code": "unknown-source-id", "message": str(raw["source_id"])})
                continue
            if source.get("reviewer_status") != "accepted" and raw.get("reviewer_status") == "accepted":
                errors.append({"card_id": card_id, "code": "accepted-card-from-unaccepted-source", "message": str(raw["source_id"])})
            if raw.get("trust_tier") not in TRUST_TIERS:
                errors.append({"card_id": card_id, "code": "unknown-trust-tier", "message": str(raw.get("trust_tier"))})
            if raw.get("allowed_use") not in ALLOWED_USE:
                errors.append({"card_id": card_id, "code": "unknown-allowed-use", "message": str(raw.get("allowed_use"))})
            if raw.get("trust_tier") != source.get("trust_tier"):
                warnings.append({"card_id": card_id, "code": "trust-tier-differs-from-source", "message": str(raw["source_id"])})
            if raw.get("source_url") != source.get("source_url"):
                errors.append({"card_id": card_id, "code": "source-url-differs-from-registry", "message": str(raw["source_id"])})
            if raw.get("allowed_use") != source.get("allowed_use"):
                errors.append({"card_id": card_id, "code": "allowed-use-differs-from-source", "message": str(raw["source_id"])})
            refresh_status = raw.get("source_refresh_status") or source.get("source_refresh_status")
            if refresh_status and refresh_status not in SOURCE_REFRESH_STATUSES:
                errors.append({"card_id": card_id, "code": "unknown-source-refresh-status", "message": str(refresh_status)})
            if raw.get("reviewer_status") == "accepted" and not raw.get("claim_boundaries"):
                errors.append({"card_id": card_id, "code": "missing-claim-boundary", "message": "Accepted cards need claim boundaries."})
            if raw.get("reviewer_status") == "accepted" and not raw.get("limitations"):
                errors.append({"card_id": card_id, "code": "missing-limitations", "message": "Accepted cards need limitations."})
            if raw.get("reviewer_status") == "accepted" and not (raw.get("planner_hints") or raw.get("validator_hints")):
                errors.append({"card_id": card_id, "code": "missing-hints", "message": "Accepted cards need planner or validator hints."})
            text_fields = " ".join(str(raw.get(field, "")) for field in REQUIRED_FIELDS)
            if PRIVATE_TEXT_RE.search(text_fields):
                errors.append({"card_id": card_id, "code": "private-looking-content", "message": "Evidence cards must not contain private paths or asset ids."})
            for field in ("extracted_facts", "extracted_patterns", "limitations", "claim_boundaries"):
                for value in raw.get(field, []) or []:
                    if len(str(value).split()) > 80:
                        warnings.append({"card_id": card_id, "code": "long-card-text", "message": f"{field} contains a long item; keep evidence paraphrased."})
    return {
        "ok": not errors,
        "schema_version": "gee-evidence-card/v0.1",
        "path": str(root),
        "card_count": len(raw_cards),
        "accepted_count": sum(1 for item in raw_cards if item.get("reviewer_status") == "accepted"),
        "candidate_count": sum(1 for item in raw_cards if item.get("reviewer_status") == "candidate"),
        "errors": errors,
        "warnings": warnings,
    }


def search_evidence_cards(query: str, cards: list[EvidenceCard], top_k: int = 10) -> list[dict[str, Any]]:
    terms = _tokenize(query)
    if not terms:
        raise ValueError("Query is empty after tokenization.")
    query_norm = _normalize(query)
    scored: list[tuple[int, str, EvidenceCard]] = []
    for card in cards:
        score = _score_card(query_norm, terms, card)
        if score:
            scored.append((score, card.card_id, card))
    return [
        {"score": score, **card.to_dict()}
        for score, _card_id, card in sorted(scored, key=lambda item: (-item[0], item[1]))[:top_k]
    ]


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower().replace("_", " ").replace("/", " ").replace("-", " ")))


def _tokenize(text: str) -> set[str]:
    return set(_normalize(text).split())


def _field_score(terms: set[str], values: list[str] | tuple[str, ...], weight: int) -> int:
    text = _normalize(" ".join(str(value) for value in values))
    if not text:
        return 0
    return weight * sum(1 for term in terms if term in text)


def _phrase_score(query_norm: str, card: EvidenceCard) -> int:
    score = 0
    card_text = _normalize(
        " ".join(
            [
                card.card_id,
                card.title,
                " ".join(card.topics),
                " ".join(card.canonical_terms),
                " ".join(card.aliases),
                " ".join(card.extracted_facts),
                " ".join(card.known_failure_modes),
            ]
        )
    )
    for phrase, required_terms in PHRASE_BOOSTS.items():
        phrase_norm = _normalize(phrase)
        if phrase_norm in query_norm and all(term in card_text for term in required_terms):
            score += 75
    return score


def _negative_penalty(query_norm: str, card: EvidenceCard) -> int:
    penalty = 0
    for negative in card.negative_queries:
        negative_norm = _normalize(negative)
        if negative_norm and negative_norm in query_norm:
            penalty += 200
    topics = {_normalize(topic) for topic in card.topics}
    workflows = {_normalize(workflow) for workflow in card.applicable_workflows}
    if "flood" in query_norm and ("product intercomparison" in workflows or "ndvi" in topics):
        penalty += 320 if "flood workflow" in query_norm or "flood mapping" in query_norm else 180
    if "product intercomparison" in query_norm and ("flood mapping" in workflows or "flood" in topics):
        penalty += 120
    return penalty


def _score_card(query_norm: str, terms: set[str], card: EvidenceCard) -> int:
    score = 0
    topics = {_normalize(topic) for topic in card.topics}
    workflows = {_normalize(workflow) for workflow in card.applicable_workflows}
    card_id_norm = _normalize(card.card_id)
    title_norm = _normalize(card.title)
    if query_norm == card_id_norm or query_norm in {card_id_norm, title_norm}:
        score += 1000
    if card_id_norm and card_id_norm in query_norm:
        score += 500
    if title_norm and (title_norm in query_norm or query_norm in title_norm):
        score += 250
    score += _field_score(terms, card.canonical_terms + card.aliases, 70)
    score += _field_score(terms, card.topics + card.applicable_workflows + card.applicable_datasets, 35)
    score += _field_score(terms, card.extracted_facts + card.extracted_patterns + card.known_failure_modes, 20)
    score += _field_score(terms, card.planner_hints + card.validator_hints + card.limitations + card.claim_boundaries, 12)
    score += _field_score(terms, (card.source_id, card.source_type, card.trust_tier, card.allowed_use), 5)
    score += _phrase_score(query_norm, card)
    if "flood" in query_norm and ("flood mapping" in workflows or "flood" in topics):
        score += 220
    score -= _negative_penalty(query_norm, card)
    return max(score, 0)
