from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .paths import default_evidence_cards_dir
from .sources import ALLOWED_USE, TRUST_TIERS, load_source_registry, source_map


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
    cards: list[EvidenceCard] = []
    for path in sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml")):
        for raw in _cards_from_file(path):
            normalized = dict(raw)
            for field in LIST_FIELDS:
                value = normalized.get(field) or []
                if isinstance(value, str):
                    value = [value]
                normalized[field] = tuple(str(item) for item in value)
            cards.append(EvidenceCard(**{field: normalized.get(field) for field in REQUIRED_FIELDS}))
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
            if raw.get("reviewer_status") == "accepted" and not raw.get("claim_boundaries"):
                errors.append({"card_id": card_id, "code": "missing-claim-boundary", "message": "Accepted cards need claim boundaries."})
            text_fields = " ".join(str(raw.get(field, "")) for field in REQUIRED_FIELDS)
            if "/Users/" in text_fields or "users/" in text_fields.lower() or "drive.google.com/drive/folders/" in text_fields:
                errors.append({"card_id": card_id, "code": "private-looking-content", "message": "Evidence cards must not contain private paths or asset ids."})
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
    terms = {term.lower() for term in query.replace("/", " ").replace("_", " ").split() if term.strip()}
    if not terms:
        raise ValueError("Query is empty after tokenization.")
    scored: list[tuple[int, str, EvidenceCard]] = []
    for card in cards:
        text = " ".join(
            [
                card.card_id,
                card.title,
                " ".join(card.topics),
                " ".join(card.extracted_facts),
                " ".join(card.extracted_patterns),
                " ".join(card.applicable_datasets),
                " ".join(card.applicable_operators),
                " ".join(card.known_failure_modes),
                " ".join(card.planner_hints),
                " ".join(card.validator_hints),
            ]
        ).lower().replace("/", " ").replace("_", " ")
        score = sum(1 for term in terms if term in text)
        if score:
            scored.append((score, card.card_id, card))
    return [
        {"score": score, **card.to_dict()}
        for score, _card_id, card in sorted(scored, key=lambda item: (-item[0], item[1]))[:top_k]
    ]
