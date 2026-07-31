import json
from pathlib import Path

from geeskill import cli
from geeskill.promotion import (
    MANIFEST_SCHEMA_VERSION,
    load_promotion_manifest,
    review_promotion_manifest,
)


EXAMPLE = Path("examples/local_learning/promotion-manifest.example.json")


def test_example_manifest_is_review_ready_but_not_officially_promoted():
    report = review_promotion_manifest(load_promotion_manifest(EXAMPLE))

    assert report["ok"] is True
    assert report["status"] == "candidate_review_ready"
    assert report["official_promotion"] is False
    assert report["review_queue"][0]["targets"] == [
        "rule:product-comparison-target-grid"
    ]
    assert any("does not promote" in warning for warning in report["warnings"])


def test_manifest_rejects_private_fields_and_private_looking_content():
    payload = load_promotion_manifest(EXAMPLE)
    payload["items"][0]["project_alias"] = "private-study"
    payload["items"][0]["public_summary"] = (
        "Ask researcher@example.org to read C:\\Users\\researcher\\private\\result.json."
    )

    report = review_promotion_manifest(payload)

    assert report["ok"] is False
    assert report["status"] == "blocked"
    assert report["review_queue"] == []
    assert any("forbidden fields: project_alias" in error for error in report["errors"])
    assert any("private or secret-looking" in error for error in report["errors"])


def test_empty_manifest_is_valid_but_has_no_candidates():
    report = review_promotion_manifest(
        {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "created_at": "2026-07-31T00:00:00+00:00",
            "item_count": 0,
            "items": [],
        }
    )

    assert report["ok"] is True
    assert report["status"] == "no_candidates"
    assert report["official_promotion"] is False


def test_manifest_rejects_unmapped_target_and_pattern_without_unknowns():
    payload = load_promotion_manifest(EXAMPLE)
    payload["items"][0]["distill_targets"] = ["target-grid-rule"]
    payload["items"][0]["ignorance_boundary"]["omitted_or_unverified"] = []

    report = review_promotion_manifest(payload)

    assert report["ok"] is False
    assert any("<kind>:<portable-id>" in error for error in report["errors"])
    assert any("omitted_or_unverified must not be empty" in error for error in report["errors"])


def test_cli_exposes_contract_and_manifest_review(capsys):
    assert cli.main(["learning", "contract", "--json"]) == 0
    contract_payload = json.loads(capsys.readouterr().out)
    assert contract_payload["data"]["schema_version"] == MANIFEST_SCHEMA_VERSION

    assert (
        cli.main(
            [
                "learning",
                "review-manifest",
                str(EXAMPLE),
                "--json",
            ]
        )
        == 0
    )
    review_payload = json.loads(capsys.readouterr().out)
    assert review_payload["data"]["official_promotion"] is False
