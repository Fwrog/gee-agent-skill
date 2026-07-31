from pathlib import Path
import re

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


def test_github_gee_discovery_inventory_has_200_quality_screened_candidates():
    data = yaml.safe_load(Path("references/corpus/github_gee_discovery_200.yml").read_text(encoding="utf-8"))
    repos = data["repositories"]
    assert data["schema_version"] == "gee-corpus-discovery/v0.5"
    assert len(repos) == 200
    assert data["snapshot_summary"] == {
        "repository_count": len(repos),
        "direct_domain_evidence_count": sum(
            item["domain_relevance"]["status"] == "direct_metadata_evidence"
            for item in repos
        ),
        "high_signal_metadata_count": sum(
            item["quality_band"] == "high_signal_metadata" for item in repos
        ),
        "qualified_metadata_candidate_count": sum(
            item["quality_band"] == "qualified_metadata_candidate" for item in repos
        ),
        "declared_license_count": sum(item["license"] != "NOASSERTION" for item in repos),
        "license_noassertion_count": sum(item["license"] == "NOASSERTION" for item in repos),
    }
    assert {item["name"] for item in data["queries"]} == {"gee_topic", "paper_linkage", "research_workflow"}
    assert "seed_inventory" in data["boundary"]
    assert "review_overlay" in data["boundary"]
    assert all(item["review_state"] == "quality_screened_unreviewed" for item in repos)
    assert all(item["sampling_level"] == "metadata_only_discovery" for item in repos)
    assert all(item["quality_score"] >= data["quality_policy"]["minimum_score"] for item in repos)
    assert all(not item["archived"] and not item["fork"] for item in repos)
    assert all(item["domain_relevance"]["status"] == "direct_metadata_evidence" for item in repos)
    assert all(item["domain_relevance"]["evidence"] for item in repos)
    assert not {
        "public-apis/public-apis",
        "public-api-lists/public-api-lists",
        "Jieyab89/OSINT-Cheat-sheet",
        "DahnJ/EO-jobs",
    } & {item["full_name"] for item in repos}
    assert all("harvest_level" in item for item in repos)
    assert any(item["harvest_level"] == "metadata_only_until_license_review" for item in repos)
    assert any(item["task_tags"] for item in repos)
    assert any(item["data_usage_signals"] for item in repos)
    assert data["quality_policy"]["paper_candidate_count"] >= data["quality_policy"]["paper_candidate_floor"]
    assert all(item["paper_linkage"]["status"].endswith(("unverified", "detected")) for item in repos)


def test_reviewed_batch_is_evidence_backed_and_separate_from_discovery_screening():
    discovery = yaml.safe_load(
        Path("references/corpus/github_gee_discovery_200.yml").read_text(encoding="utf-8")
    )
    ledger = yaml.safe_load(
        Path("references/corpus/github_gee_reviewed_batch_01.yml").read_text(encoding="utf-8")
    )
    records = ledger["records"]
    progress = ledger["progress"]
    discovery_names = {item["full_name"] for item in discovery["repositories"]}
    reviewed_discovery_names = {
        item["full_name"] for item in records if item["in_discovery_inventory"]
    }
    anchor_names = {
        item["full_name"] for item in records if not item["in_discovery_inventory"]
    }

    assert ledger["schema_version"] == "gee-corpus-reviewed/v0.1"
    assert len(records) == progress["total_deep_review_records"] == 24
    assert len(reviewed_discovery_names) == progress["discovery_records_reviewed"] == 21
    assert progress["discovery_records_remaining"] == len(discovery_names - reviewed_discovery_names) == 179
    assert len(anchor_names) == progress["additional_anchor_records_reviewed"] == 3
    assert reviewed_discovery_names <= discovery_names
    assert not anchor_names & discovery_names

    required_data_fields = {
        "identity_and_revision",
        "bands_or_variables",
        "scale_and_offset",
        "qa_and_mask",
        "grid_projection_resampling",
        "temporal",
        "access_license_asset_stability",
        "private_dependencies",
    }
    states = [item["decision"]["state"] for item in records]
    assert states.count("reviewed_pattern_source") == progress["reviewed_pattern_sources"] == 17
    assert states.count("reviewed_no_new_promotion") == progress["reviewed_no_new_promotion"] == 7

    for item in records:
        assert re.fullmatch(r"[0-9a-f]{40}", item["reviewed_ref"]), item["full_name"]
        assert len(item["checked_surfaces"]) >= 2, item["full_name"]
        assert any(
            surface["path"].lower().startswith("license")
            or "license" in surface["purpose"].lower()
            for surface in item["checked_surfaces"]
        )
        assert all(re.fullmatch(r"[0-9a-f]{40}", surface["blob_sha"]) for surface in item["checked_surfaces"])
        assert required_data_fields == set(item["data_contract"]), item["full_name"]
        assert item["important_findings"], item["full_name"]
        assert item["claim_boundary"], item["full_name"]
        if item["decision"]["state"] == "reviewed_pattern_source":
            assert item["decision"]["promoted_to"], item["full_name"]
        else:
            assert not item["decision"]["promoted_to"]
            assert item["decision"]["reason"]


def test_paper_linked_projects_are_revision_and_boundary_reviewed():
    data = yaml.safe_load(
        Path("references/corpus/paper_linked_gee_projects.yml").read_text(encoding="utf-8")
    )
    pairs = data["pairs"]
    assert data["schema_version"] == "gee-paper-linked-projects/v0.2"
    assert len(pairs) == 9
    assert sum(item["review_state"] == "reviewed_pattern_source" for item in pairs) == 7
    assert sum(item["review_state"] == "reviewed_no_new_promotion" for item in pairs) == 2
    for item in pairs:
        assert item["repository"].startswith("https://github.com/")
        assert item["paper"].startswith("https://")
        assert re.fullmatch(r"[0-9a-f]{40}", item["reviewed_ref"])
        assert item["repository_license"]
        assert item["reusable_pattern"]
        assert item["data_boundary"]
