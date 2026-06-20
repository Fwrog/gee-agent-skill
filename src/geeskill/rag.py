from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
URL_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_path: str
    title: str
    text: str
    url: str | None
    metadata: dict[str, str]


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    source_path: str
    title: str
    score: float
    excerpt: str
    url: str | None
    metadata: dict[str, str]


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _metadata_from_text(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in text.splitlines()[:40]:
        if ":" not in line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key and value and len(key) <= 40:
            metadata[key] = value
    return metadata


def _split_markdown(path: Path, root: Path) -> list[Chunk]:
    raw = path.read_text(encoding="utf-8")
    rel = path.relative_to(root).as_posix()
    source_title = path.stem.replace("-", " ").title()
    url_match = URL_RE.search(raw)
    source_metadata = _metadata_from_text(raw)
    current_title = source_title
    current_lines: list[str] = []
    chunks: list[Chunk] = []

    def flush() -> None:
        if not current_lines:
            return
        text = "\n".join(current_lines).strip()
        if not text:
            return
        chunk_id = f"{rel}#{len(chunks) + 1:03d}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                source_path=rel,
                title=current_title,
                text=text,
                url=url_match.group(0).rstrip(").,") if url_match else None,
                metadata={**source_metadata, **_metadata_from_text(text)},
            )
        )

    for line in raw.splitlines():
        heading = HEADING_RE.match(line)
        if heading and current_lines:
            flush()
            current_lines = [line]
            current_title = heading.group(2).strip()
        else:
            current_lines.append(line)
            if heading:
                current_title = heading.group(2).strip()
    flush()
    return chunks


def load_markdown_chunks(docs_dir: Path) -> list[Chunk]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.rglob("*.md")):
        chunks.extend(_split_markdown(path, docs_dir))
    if not chunks:
        raise ValueError(f"No markdown files found in {docs_dir}")
    return chunks


def build_index(docs_dir: Path) -> dict:
    chunks = load_markdown_chunks(docs_dir)
    documents = []
    doc_freq: dict[str, int] = {}
    total_length = 0
    for chunk in chunks:
        terms = tokenize(chunk.text)
        total_length += len(terms)
        term_counts: dict[str, int] = {}
        for term in terms:
            term_counts[term] = term_counts.get(term, 0) + 1
        for term in term_counts:
            doc_freq[term] = doc_freq.get(term, 0) + 1
        documents.append(
            {
                "chunk_id": chunk.chunk_id,
                "source_path": chunk.source_path,
                "title": chunk.title,
                "text": chunk.text,
                "url": chunk.url,
                "metadata": chunk.metadata,
                "terms": term_counts,
                "length": len(terms),
            }
        )
    return {
        "version": 1,
        "algorithm": "bm25-lite",
        "doc_count": len(documents),
        "avg_doc_length": total_length / max(len(documents), 1),
        "doc_freq": doc_freq,
        "documents": documents,
    }


def write_index(index: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def load_index(index_path: Path) -> dict:
    if not index_path.exists():
        raise FileNotFoundError(
            f"Index not found: {index_path}. Run scripts/ingest_docs.py first."
        )
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Index is not valid JSON: {index_path}") from exc
    if index.get("version") != 1 or "documents" not in index or "doc_freq" not in index:
        raise ValueError(f"Index has an unsupported schema: {index_path}")
    return index


def _bm25_score(
    query_terms: Iterable[str],
    doc: dict,
    doc_freq: dict[str, int],
    doc_count: int,
    avg_doc_length: float,
) -> float:
    k1 = 1.5
    b = 0.75
    length = max(float(doc.get("length", 0)), 1.0)
    terms = doc.get("terms", {})
    score = 0.0
    for term in query_terms:
        tf = float(terms.get(term, 0))
        if tf == 0:
            continue
        df = float(doc_freq.get(term, 0))
        idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
        denom = tf + k1 * (1 - b + b * length / max(avg_doc_length, 1.0))
        score += idf * (tf * (k1 + 1)) / denom
    return score


def _excerpt(text: str, terms: list[str], max_chars: int = 320) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    lower = compact.lower()
    first_hit = min((lower.find(term) for term in terms if term in lower), default=0)
    start = max(first_hit - 80, 0)
    end = min(start + max_chars, len(compact))
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return f"{prefix}{compact[start:end]}{suffix}"


def search(index: dict, query: str, top_k: int = 5) -> list[SearchResult]:
    terms = tokenize(query)
    if not terms:
        raise ValueError("Query is empty after tokenization.")
    doc_count = int(index.get("doc_count") or len(index["documents"]))
    avg_doc_length = float(index.get("avg_doc_length") or 1.0)
    scored: list[SearchResult] = []
    for doc in index["documents"]:
        score = _bm25_score(terms, doc, index["doc_freq"], doc_count, avg_doc_length)
        if score <= 0:
            continue
        scored.append(
            SearchResult(
                chunk_id=doc["chunk_id"],
                source_path=doc["source_path"],
                title=doc["title"],
                score=round(score, 6),
                excerpt=_excerpt(doc["text"], terms),
                url=doc.get("url"),
                metadata=doc.get("metadata", {}),
            )
        )
    return sorted(scored, key=lambda item: (-item.score, item.source_path, item.chunk_id))[
        :top_k
    ]


def results_to_dicts(results: list[SearchResult]) -> list[dict]:
    return [
        {
            "chunk_id": item.chunk_id,
            "source_path": item.source_path,
            "title": item.title,
            "score": item.score,
            "excerpt": item.excerpt,
            "url": item.url,
            "metadata": item.metadata,
        }
        for item in results
    ]
