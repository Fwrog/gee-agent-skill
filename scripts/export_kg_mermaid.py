#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()
    from geeskill.kg import graph_to_mermaid, load_graph

    parser = argparse.ArgumentParser(description="Export KG index as Mermaid.")
    parser.add_argument("--index", default="references/index/gee_kg_index.json")
    parser.add_argument("--focus-node")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    text = graph_to_mermaid(load_graph(Path(args.index)), focus_node=args.focus_node)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
