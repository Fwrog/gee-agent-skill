#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


PRIVATE_RE = re.compile(
    r"(/Users/|/Volumes/|C:\\Users\\|users/[A-Za-z0-9_.-]+/|projects/[^/\s]+/assets/[^,\s]+|drive\.google\.com/drive/folders/)",
    re.IGNORECASE,
)


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _cards_from_file(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("cards", []))


def audit_evidence_quality(cards_dir: Path, registry_path: Path) -> dict[str, Any]:
    _add_src_to_path()
    from geeskill.evidence import validate_evidence_cards
    from geeskill.sources import load_source_registry, source_map

    schema_report = validate_evidence_cards(cards_dir, registry_path)
    sources = source_map(load_source_registry(registry_path))
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    card_count = 0
    accepted_count = 0

    for path in sorted(cards_dir.glob("*.yml")) + sorted(cards_dir.glob("*.yaml")):
        for card in _cards_from_file(path):
            card_count += 1
            card_id = str(card.get("card_id") or f"{path.name}:unknown")
            source = sources.get(str(card.get("source_id")))
            if card.get("reviewer_status") == "accepted":
                accepted_count += 1
                for field in ("last_checked", "limitations", "claim_boundaries", "canonical_terms"):
                    if not card.get(field):
                        errors.append({"card_id": card_id, "code": f"missing-{field}", "message": f"Accepted cards need {field}."})
                if not (card.get("planner_hints") or card.get("validator_hints")):
                    errors.append({"card_id": card_id, "code": "missing-actionable-hints", "message": "Accepted cards need planner or validator hints."})
                if not source or source.get("reviewer_status") != "accepted":
                    errors.append({"card_id": card_id, "code": "accepted-card-unaccepted-source", "message": str(card.get("source_id"))})
                elif source.get("source_refresh_status") in {"stale", "unavailable", "candidate_unverified"}:
                    errors.append({"card_id": card_id, "code": "accepted-card-unfresh-source", "message": str(card.get("source_id"))})
            if source:
                for field in ("source_url", "trust_tier", "allowed_use"):
                    if card.get(field) != source.get(field):
                        errors.append({"card_id": card_id, "code": f"{field}-mismatch", "message": str(card.get("source_id"))})
                if card.get("source_refresh_status") and card.get("source_refresh_status") != source.get("source_refresh_status"):
                    warnings.append({"card_id": card_id, "code": "source-refresh-status-differs", "message": str(card.get("source_id"))})
            text = yaml.safe_dump(card, sort_keys=True, allow_unicode=True)
            if PRIVATE_RE.search(text):
                errors.append({"card_id": card_id, "code": "private-looking-content", "message": "Card contains private-looking paths, assets, or folders."})
            for field in ("extracted_facts", "extracted_patterns", "limitations", "claim_boundaries"):
                for item in card.get(field, []) or []:
                    if len(str(item).split()) > 80:
                        warnings.append({"card_id": card_id, "code": "long-evidence-item", "message": field})

    return {
        "ok": schema_report["ok"] and not errors,
        "schema_version": "gee-evidence-quality-audit/v0.4.1",
        "cards_dir": str(cards_dir),
        "registry": str(registry_path),
        "card_count": card_count,
        "accepted_count": accepted_count,
        "schema_report_ok": schema_report["ok"],
        "errors": schema_report.get("errors", []) + errors,
        "warnings": schema_report.get("warnings", []) + warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit v0.4.1 KG-RAG evidence-card quality.")
    parser.add_argument("--cards-dir", default="references/evidence_cards")
    parser.add_argument("--registry", default="references/sources/source_registry.yml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = audit_evidence_quality(Path(args.cards_dir), Path(args.registry))
    print(
        json.dumps(report, indent=2, ensure_ascii=False)
        if args.json
        else f"{report['schema_version']} ok={report['ok']} cards={report['card_count']}"
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
