from pathlib import Path

import pytest

from geeskill.rag import build_index, search


def test_rag_retrieves_sentinel2_docs():
    index = build_index(Path("references/knowledge_base"))
    results = search(index, "Sentinel-2 NDVI cloud mask", top_k=3)
    assert results
    joined = " ".join(item.source_path for item in results)
    assert "sentinel-2" in joined or "cloud-masking" in joined
    assert all(item.excerpt for item in results)


def test_rag_rejects_empty_query():
    index = build_index(Path("references/knowledge_base"))
    with pytest.raises(ValueError, match="empty"):
        search(index, "   ")


def test_rag_stable_ordering():
    index = build_index(Path("references/knowledge_base"))
    first = search(index, "export table drive", top_k=5)
    second = search(index, "export table drive", top_k=5)
    assert [item.chunk_id for item in first] == [item.chunk_id for item in second]


def test_rag_propagates_file_metadata_to_section_chunks():
    index = build_index(Path("references/knowledge_base"))
    chain_chunks = [
        doc
        for doc in index["documents"]
        if doc["source_path"] == "operator-chains/sentinel2-ndvi-monthly-zonal.md"
    ]
    assert chain_chunks
    for chunk in chain_chunks:
        metadata = chunk["metadata"]
        assert metadata["source_type"] == "operator-chain"
        assert metadata["retrieved_at"] == "2026-06-21"
        assert metadata["dataset_id"] == "COPERNICUS/S2_SR_HARMONIZED"
