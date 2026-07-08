from pathlib import Path

from geeskill.sources import load_source_registry, validate_source_registry


def test_source_registry_validates():
    report = validate_source_registry(Path("references/sources/source_registry.yml"))
    assert report["ok"], report
    assert report["accepted_count"] >= 7


def test_official_sources_are_tier_a_accepted():
    registry = load_source_registry(Path("references/sources/source_registry.yml"))
    official = [item for item in registry["sources"] if item["source_type"].startswith("official")]
    assert official
    assert all(item["trust_tier"] == "A" for item in official)
    assert all(item["reviewer_status"] == "accepted" for item in official)


def test_autogeeval_stays_candidate_until_license_review():
    registry = load_source_registry(Path("references/sources/source_registry.yml"))
    autogeeval = next(item for item in registry["sources"] if item["source_id"] == "autogeeval-paper")
    assert autogeeval["reviewer_status"] == "candidate"
    assert autogeeval["allowed_use"] == "metadata_only"
