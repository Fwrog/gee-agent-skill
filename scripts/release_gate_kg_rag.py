#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {
    ".cff",
    ".geojson",
    ".j2",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
PRIVATE_RE = re.compile(
    r"("
    r"[A-Za-z]:\\[A-Za-z0-9._-]{2,}\\|"
    r"/Users/[A-Za-z0-9._-]+/|"
    r"/Volumes/[A-Za-z0-9._-]+/|"
    r"users/(?!example/)[A-Za-z0-9_.-]+/|"
    r"projects/[A-Za-z0-9_.-]+/assets/[A-Za-z0-9_./-]+|"
    r"gs://[A-Za-z0-9][A-Za-z0-9._-]+|"
    r"AIza[0-9A-Za-z_-]{20,}|"
    r"ya29\.|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r")",
    re.IGNORECASE,
)


def _run(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def _release_text_paths() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [
        Path(value)
        for value in proc.stdout.split("\0")
        if value and Path(value).suffix.lower() in TEXT_SUFFIXES
    ]


def _privacy_scan() -> dict[str, Any]:
    findings = []
    try:
        paths = _release_text_paths()
    except RuntimeError as exc:
        return {
            "command": "privacy_scan",
            "ok": False,
            "findings": [{"path": "", "code": str(exc)}],
        }
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        scanned = re.sub(
            r"users/example/[A-Za-z0-9_./-]+",
            "synthetic_private_asset_fixture",
            text,
        )
        scanned = re.sub(
            r"projects/(?:example|demo-valid)/assets/[A-Za-z0-9_./-]+",
            "synthetic_private_asset_fixture",
            scanned,
        )
        scanned = re.sub(
            r"C:\\path\\to\\[A-Za-z0-9_.\\-]+",
            "synthetic_checkout_path",
            scanned,
            flags=re.IGNORECASE,
        )
        if PRIVATE_RE.search(scanned):
            findings.append(
                {"path": str(path), "code": "private-or-secret-looking-content"}
            )
    return {"command": "privacy_scan", "ok": not findings, "findings": findings}


def _docs_command_consistency() -> dict[str, Any]:
    docs = [Path("README.md"), Path("README.zh-CN.md"), Path("docs/cli_reference.md"), Path("docs/kg_rag_architecture.md")]
    required = [
        "gee-skill sources validate",
        "gee-skill evidence search",
        "gee-skill kg search",
        "gee-skill retrieve hybrid",
    ]
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in docs if path.exists())
    missing = [item for item in required if item not in text]
    return {"command": "docs_command_consistency", "ok": not missing, "missing": missing}


def run_release_gate() -> dict[str, Any]:
    commands = [
        [sys.executable, "scripts/validate_sources.py", "--json"],
        [sys.executable, "scripts/validate_evidence_cards.py", "--json"],
        [sys.executable, "scripts/audit_evidence_quality.py", "--json"],
        [sys.executable, "scripts/ingest_docs.py", "--docs-dir", "references/knowledge_base", "--out", "references/index/gee_docs_index.json"],
        [sys.executable, "scripts/build_kg.py", "--json"],
        [sys.executable, "scripts/validate_kg.py", "--json"],
        [sys.executable, "scripts/run_kg_rag_eval.py", "--suite", "evals/kg_rag_retrieval_suite.yml", "--json"],
        [sys.executable, "scripts/run_kg_rag_eval.py", "--suite", "evals/planner_research_grounding_suite.yml", "--json"],
        [sys.executable, "scripts/run_kg_rag_eval.py", "--suite", "evals/semantic_validator_fixture_suite.yml", "--json"],
    ]
    checks = [_run(command) for command in commands]
    checks.append(_privacy_scan())
    checks.append(_docs_command_consistency())
    checks.append(_run(["git", "diff", "--check"]))
    return {
        "ok": all(check["ok"] for check in checks),
        "schema_version": "gee-kg-rag-release-gate/v0.4.2",
        "check_count": len(checks),
        "checks": checks,
    }


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# v0.4.2 KG-RAG Release Gate Report",
        "",
        f"- Overall ok: {report['ok']}",
        f"- Check count: {report['check_count']}",
        "",
        "| Check | OK | Return code |",
        "| --- | --- | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['command']}` | {check['ok']} | {check.get('returncode', '')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the v0.4.2 KG-RAG release gate.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report", default="outputs/research/v042_release_gate_report.md")
    args = parser.parse_args(argv)
    report = run_release_gate()
    _write_markdown(report, Path(args.report))
    print(
        json.dumps(report, indent=2, ensure_ascii=False)
        if args.json
        else f"{report['schema_version']} ok={report['ok']} checks={report['check_count']}"
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
