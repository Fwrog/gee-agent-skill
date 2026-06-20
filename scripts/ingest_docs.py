from __future__ import annotations

import argparse
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
    from geeskill.rag import build_index, write_index

    parser = argparse.ArgumentParser(description="Build the local Earth Engine docs index.")
    parser.add_argument("--docs-dir", default="references/knowledge_base")
    parser.add_argument("--out", default="references/index/gee_docs_index.json")
    args = parser.parse_args(argv)

    docs_dir = Path(args.docs_dir)
    out_path = Path(args.out)
    try:
        index = build_index(docs_dir)
        write_index(index, out_path)
        package_out = Path("src/geeskill/resources/index/gee_docs_index.json")
        if package_out.parent.exists() and out_path.resolve() != package_out.resolve():
            package_out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(out_path, package_out)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"indexed {index['doc_count']} chunks -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
