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
    from geeskill.promotion import load_promotion_manifest, review_promotion_manifest

    parser = argparse.ArgumentParser(
        description="Validate a public-safe local-learning promotion manifest."
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        default="examples/local_learning/promotion-manifest.example.json",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = review_promotion_manifest(
            load_promotion_manifest(Path(args.manifest))
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "ok": False,
            "schema_version": "gee-local-learning-review/v0.1",
            "status": "blocked",
            "official_promotion": False,
            "errors": [str(exc)],
        }

    print(
        json.dumps(report, indent=2, ensure_ascii=False)
        if args.json
        else f"{report['schema_version']} ok={report['ok']} status={report['status']}"
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
