#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()
    from geeskill.evidence import validate_evidence_cards

    parser = argparse.ArgumentParser(description="Validate evidence cards.")
    parser.add_argument("--cards-dir", default="references/evidence_cards")
    parser.add_argument("--registry", default="references/sources/source_registry.yml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_evidence_cards(Path(args.cards_dir), Path(args.registry))
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text if args.json else f"{report['schema_version']} ok={report['ok']} cards={report['card_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
