from pathlib import Path

import pytest

from geeskill.rag import build_index, search
from geeskill.retrieval_trace import build_retrieval_trace


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


def test_retrieval_trace_reports_recipe_and_rule_coverage():
    index = build_index(Path("references/knowledge_base"))
    results = search(index, "NDWI GeoTIFF recipe export image rule", top_k=8)
    trace = build_retrieval_trace("NDWI GeoTIFF recipe export image rule", results)
    assert trace["coverage"]["recipe_cards"] >= 1
    assert trace["coverage"]["rule_cards"] >= 1
    assert trace["coverage"]["export_guidance"] >= 1


def test_rag_retrieves_adaptive_browser_learning_loop():
    index = build_index(Path("references/knowledge_base"))
    results = search(index, "browser backed knowledge loop private research source fidelity", top_k=6)
    assert results
    joined = " ".join(item.source_path for item in results)
    assert "adaptive-browser-backed-knowledge-loop" in joined
    assert "source-fidelity-and-private-research-boundaries" in joined


def test_rag_retrieves_live_export_contract_failures():
    index = build_index(Path("references/knowledge_base"))
    results = search(index, "Earth Engine live export image dtype CRS boundary schema Drive CSV fetch", top_k=8)
    assert results
    joined = " ".join(item.source_path for item in results)
    assert "gee-live-export-contract-failures" in joined


def test_rag_retrieves_ndvi_demo_validation_ladder():
    index = build_index(Path("references/knowledge_base"))
    results = search(index, "NDVI validation MODIS Terra Aqua Landsat Dynamic World water strata", top_k=8)
    assert results
    joined = " ".join(item.source_path for item in results)
    assert "ndvi-demo-validation-ladder" in joined
    assert "modis-mod13q1-vegetation-indices" in joined or "modis-myd13q1-vegetation-indices" in joined
