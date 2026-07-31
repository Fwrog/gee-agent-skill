from pathlib import Path

import yaml

from geeskill.sources import validate_source_registry


def test_source_registry_has_v041_refresh_statuses():
    report = validate_source_registry(Path("references/sources/source_registry.yml"))
    assert report["ok"] is True
    registry = yaml.safe_load(Path("references/sources/source_registry.yml").read_text(encoding="utf-8"))
    statuses = {source["source_id"]: source["source_refresh_status"] for source in registry["sources"]}
    assert statuses["google-earth-engine-data-catalog"] == "fresh"
    assert statuses["gee-catalog-mod13q1"] == "fresh"
    assert statuses["autogeeval-plus-paper"] == "fresh"
    assert statuses["gee-ops-paper"] == "fresh"
    assert all(source.get("review_notes") for source in registry["sources"])


def test_candidate_research_sources_do_not_override_official_facts():
    registry = yaml.safe_load(Path("references/sources/source_registry.yml").read_text(encoding="utf-8"))
    by_id = {source["source_id"]: source for source in registry["sources"]}
    for source_id in ("autogeeval-paper", "geofub-paper"):
        source = by_id[source_id]
        assert source["reviewer_status"] == "candidate"
        assert source["allowed_use"] == "metadata_only"
        assert "does not override" in source["claim_boundary"].lower() or "do not promote" in source["review_notes"].lower()


def test_reviewed_method_sources_remain_bounded():
    registry = yaml.safe_load(Path("references/sources/source_registry.yml").read_text(encoding="utf-8"))
    by_id = {source["source_id"]: source for source in registry["sources"]}
    for source_id in ("gee-ops-paper", "autogeeval-plus-paper"):
        source = by_id[source_id]
        assert source["reviewer_status"] == "accepted"
        assert source["allowed_use"] == "summary_only"
        assert source["trust_tier"] == "B"
        assert "official" in source["claim_boundary"].lower() or "not comparable" in source["claim_boundary"].lower()
