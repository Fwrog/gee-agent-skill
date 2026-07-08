#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()
    from geeskill.kg import build_graph, validate_graph, write_graph_index

    parser = argparse.ArgumentParser(description="Build the deterministic GEE KG index.")
    parser.add_argument("--registry", default="references/sources/source_registry.yml")
    parser.add_argument("--cards-dir", default="references/evidence_cards")
    parser.add_argument("--seed", default="references/graph/seed_graph.yml")
    parser.add_argument("--out", default="references/index/gee_kg_index.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    graph = build_graph(
        source_registry_path=Path(args.registry),
        evidence_cards_dir=Path(args.cards_dir),
        seed_graph_path=Path(args.seed),
    )
    report = validate_graph(graph)
    if report["ok"]:
        out = Path(args.out)
        write_graph_index(graph, out)
        package_out = Path("src/geeskill/resources/index/gee_kg_index.json")
        if package_out.parent.exists() and out.resolve() != package_out.resolve():
            package_out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(out, package_out)
    payload = {"ok": report["ok"], "path": args.out, **report}
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else f"gee-kg/v0.1 ok={payload['ok']} nodes={payload['node_count']} edges={payload['edge_count']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
