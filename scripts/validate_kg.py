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
    from geeskill.kg import load_graph, validate_graph

    parser = argparse.ArgumentParser(description="Validate the deterministic GEE KG index.")
    parser.add_argument("--index", default="references/index/gee_kg_index.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_graph(load_graph(Path(args.index)))
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else f"{report['schema_version']} ok={report['ok']} nodes={report['node_count']} edges={report['edge_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
