import json
from pathlib import Path

import geeskill.cli as cli


def test_ask_plan_writes_hybrid_bundle_sidecars(capsys):
    rc = cli.main(
        [
            "ask",
            "Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",
            "--plan",
            "--json",
            "--run-id",
            "test-v041-ask-plan-hybrid",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    trace = Path(payload["run_trace"])
    assert (trace / "retrieval_trace.json").exists()
    assert (trace / "hybrid_retrieval_bundle.json").exists()
    assert (trace / "source_quality_summary.json").exists()
    bundle = json.loads((trace / "hybrid_retrieval_bundle.json").read_text(encoding="utf-8"))
    assert bundle["query_classification"] in {"workflow_planning", "dataset_fact"}
    assert "accepted_evidence_cards" in bundle
    assert json.loads((trace / "source_quality_summary.json").read_text(encoding="utf-8"))["accepted_count"] >= 1
