from pathlib import Path

import yaml


def test_github_gee_seed_inventory_has_review_bounds_and_harvest_policy():
    data = yaml.safe_load(Path("references/corpus/github_gee_seed_repos.yml").read_text(encoding="utf-8"))
    repos = data["repositories"]
    assert 30 <= len(repos) <= 50
    assert data["selection_policy"]["default_ingestion_level"] == "metadata_and_patterns_only"
    assert "https://github.com/giswqs" in data["selection_policy"]["priority_curators"]
    assert "https://github.com/gee-community" in data["selection_policy"]["priority_curators"]
    assert (
        data["selection_policy"]["paper_linked_repository_policy"]["default_harvest_level"]
        == "metadata_only_until_license_review"
    )
    assert all("url" in item for item in repos)
    assert all("harvest_level" in item for item in repos)
    assert any(item["full_name"] == "google/earthengine-api" for item in repos)
    assert any(item["full_name"] == "gee-community/geemap" for item in repos)
    assert any("license_review" in item["harvest_level"] for item in repos)


def test_github_gee_discovery_inventory_has_100_plus_metadata_only_candidates():
    data = yaml.safe_load(Path("references/corpus/github_gee_discovery_100.yml").read_text(encoding="utf-8"))
    repos = data["repositories"]
    assert data["schema_version"] == "gee-corpus-discovery/v0.3"
    assert len(repos) >= 100
    assert data["query"] == "topic:google-earth-engine"
    assert "seed_inventory" in data["boundary"]
    assert all(item["review_state"] == "discovered_unreviewed" for item in repos)
    assert all(item["sampling_level"] == "metadata_only_discovery" for item in repos)
    assert all("harvest_level" in item for item in repos)
    assert any(item["harvest_level"] == "metadata_only_until_license_review" for item in repos)
    assert any(item["task_tags"] for item in repos)
