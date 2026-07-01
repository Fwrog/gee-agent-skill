import re
from pathlib import Path


IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def test_project_markdown_image_links_resolve():
    for markdown_path in [
        Path("README.md"),
        Path("README.zh-CN.md"),
        Path("docs/demo_gallery.md"),
        Path("docs/tool_permissions.md"),
        Path("docs/closed_loop.md"),
        Path("docs/release_readiness.md"),
    ]:
        text = markdown_path.read_text(encoding="utf-8")
        for target in IMAGE_LINK_RE.findall(text):
            if "://" in target:
                continue
            resolved = (markdown_path.parent / target).resolve()
            assert resolved.exists(), f"{markdown_path} references missing image {target}"


def test_release_readiness_documents_project_bound_imagegen_asset():
    text = Path("docs/release_readiness.md").read_text(encoding="utf-8")
    assert "assets/images/gee-agent-closed-loop-hero.png" in text
    assert "assets/images/gee-agent-knowledge-loop.png" in text
    assert "assets/images/gee-agent-toolchain.png" in text
    assert "built-in imagegen" in text
