from pathlib import Path

from geeskill.evidence import load_evidence_cards, search_evidence_cards, validate_evidence_cards


def test_evidence_cards_validate():
    report = validate_evidence_cards(Path("references/evidence_cards"), Path("references/sources/source_registry.yml"))
    assert report["ok"], report
    assert report["accepted_count"] >= 6


def test_modis_scale_factor_card_retrievable():
    cards = load_evidence_cards(Path("references/evidence_cards"))
    hits = search_evidence_cards("MODIS NDVI scale factor SummaryQA", cards, top_k=3)
    assert hits
    assert hits[0]["card_id"] == "modis_mod13q1_ndvi"
    assert any("0.0001" in fact for fact in hits[0]["extracted_facts"])


def test_all_accepted_cards_have_claim_boundaries():
    cards = load_evidence_cards(Path("references/evidence_cards"))
    accepted = [card for card in cards if card.reviewer_status == "accepted"]
    assert accepted
    assert all(card.claim_boundaries for card in accepted)
