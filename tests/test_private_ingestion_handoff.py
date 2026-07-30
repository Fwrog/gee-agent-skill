import re
from pathlib import Path

import yaml


WORKFLOW = Path(
    "references/knowledge_base/workflows/private-raster-ingestion-handoff.md"
)


def test_private_ingestion_workflow_defines_minimal_checkpoint_and_resume():
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in (
        "HUMAN_SETUP_REQUIRED",
        "PREFLIGHT_PASSED",
        "Minimum Non-Secret Checkpoint",
        "Post-Upload Continuation",
        "retry only the failed or missing subset",
        "Do not request or persist",
        "Do not state that this exact location rule is proven",
    ):
        assert required in text


def test_private_ingestion_workflow_uses_only_portable_placeholders():
    text = WORKFLOW.read_text(encoding="utf-8")
    forbidden_patterns = (
        r"[A-Za-z]:\\Users\\",
        r"/Users/[^/<\s]+",
        r"gs://(?!<bucket>|\$bucket)[A-Za-z0-9][A-Za-z0-9._-]+",
        r"projects/(?!<project-id>|\$PROJECT_ID|\$project)[^/<\s]+/assets/",
        r"users/[^/<\s]+/",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, text) is None


def test_skill_and_default_prompt_require_agent_owned_continuation():
    skill = Path("SKILL.md").read_text(encoding="utf-8")
    assert "minimum non-secret checkpoint" in skill
    assert "continue task monitoring" in skill

    metadata = yaml.safe_load(Path("agents/openai.yaml").read_text(encoding="utf-8"))
    prompt = metadata["interface"]["default_prompt"]
    assert "$gee-agent-skill" in prompt
    assert "reproducible Earth Engine workflow" in prompt
    assert "validate" in prompt


def test_private_ingestion_workflow_uses_registered_official_source():
    registry = yaml.safe_load(
        Path("references/sources/source_registry.yml").read_text(encoding="utf-8")
    )
    source_ids = {source["source_id"] for source in registry["sources"]}
    assert "google-earth-engine-managing-assets" in source_ids
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "https://developers.google.com/earth-engine/guides/manage_assets" in text
    assert "https://developers.google.com/earth-engine/guides/command_line" in text
