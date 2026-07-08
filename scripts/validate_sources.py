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
    from geeskill.sources import validate_source_registry

    parser = argparse.ArgumentParser(description="Validate the source registry.")
    parser.add_argument("--registry", default="references/sources/source_registry.yml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_source_registry(Path(args.registry))
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text if args.json else f"{report['schema_version']} ok={report['ok']} sources={report['source_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
