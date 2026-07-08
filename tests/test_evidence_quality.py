from pathlib import Path

from scripts.audit_evidence_quality import audit_evidence_quality


def test_evidence_quality_audit_passes_for_public_cards():
    report = audit_evidence_quality(Path("references/evidence_cards"), Path("references/sources/source_registry.yml"))
    assert report["ok"] is True
    assert report["accepted_count"] >= 30


def test_evidence_cards_have_v041_retrieval_metadata():
    report = audit_evidence_quality(Path("references/evidence_cards"), Path("references/sources/source_registry.yml"))
    assert not [error for error in report["errors"] if error["code"].startswith("missing-canonical_terms")]
