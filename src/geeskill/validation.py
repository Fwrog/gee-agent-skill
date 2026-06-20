from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .errors import ERROR_HINTS


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None
    hint: str | None = None
    category: str | None = None
    rule_id: str | None = None
    ruleset: str | None = None
    retryable: bool | None = None
    likely_cause: str | None = None
    suggested_fix: str | None = None
    user_action_required: bool | None = None

    def to_dict(self) -> dict:
        payload = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "hint": self.hint,
            "category": self.category,
            "rule_id": self.rule_id,
            "ruleset": self.ruleset,
            "retryable": self.retryable,
            "likely_cause": self.likely_cause,
            "suggested_fix": self.suggested_fix,
            "user_action_required": self.user_action_required,
        }
        if self.category and self.category in ERROR_HINTS:
            defaults = ERROR_HINTS[self.category]
            payload["retryable"] = self.retryable if self.retryable is not None else defaults["retryable"]
            payload["likely_cause"] = self.likely_cause or defaults["likely_cause"]
            payload["suggested_fix"] = self.suggested_fix or self.hint or defaults["suggested_fix"]
            payload["user_action_required"] = (
                self.user_action_required
                if self.user_action_required is not None
                else defaults["user_action_required"]
            )
        return payload


@dataclass(frozen=True)
class ValidationReport:
    path: str
    ok: bool
    findings: list[Finding]
    semantic_rulesets: list[str] | None = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "ok": self.ok,
            "semantic_rulesets": self.semantic_rulesets or [],
            "findings": [item.to_dict() for item in self.findings],
        }


JINJA_RE = re.compile(r"({[{%#].*?[}%]})")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SENSITIVE_RE = re.compile(
    r"(service_account|private_key|client_secret|refresh_token|credentials\.json)",
    re.IGNORECASE,
)


def _has_call(tree: ast.AST, attr_name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == attr_name:
                return True
            if isinstance(func, ast.Name) and func.id == attr_name:
                return True
    return False


def _call_lines(tree: ast.AST, attr_name: str) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == attr_name:
                lines.append(getattr(node, "lineno", 0))
    return lines


def _string_assignments(tree: ast.AST) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = node.value.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Constant):
            if isinstance(node.target, ast.Name) and isinstance(node.value.value, str):
                assignments[node.target.id] = node.value.value
    return assignments


def _numeric_assignments(tree: ast.AST) -> dict[str, float]:
    assignments: dict[str, float] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, (int, float)):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = float(node.value.value)
    return assignments


def _imports_ee(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == "ee" for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == "ee":
            return True
    return False


def _finding(
    severity: str,
    code: str,
    message: str,
    *,
    line: int | None = None,
    hint: str | None = None,
    category: str | None = None,
    rule_id: str | None = None,
    ruleset: str | None = None,
    retryable: bool | None = None,
) -> Finding:
    return Finding(
        severity,
        code,
        message,
        line=line,
        hint=hint,
        category=category,
        rule_id=rule_id,
        ruleset=ruleset,
        retryable=retryable,
    )


def _validate_dates(assignments: dict[str, str], findings: list[Finding]) -> None:
    candidates = [
        ("START_DATE", "END_DATE"),
        ("DATE_START", "DATE_END"),
        ("date_start", "date_end"),
    ]
    for start_key, end_key in candidates:
        if start_key in assignments and end_key in assignments:
            start_text = assignments[start_key]
            end_text = assignments[end_key]
            if not ISO_DATE_RE.match(start_text) or not ISO_DATE_RE.match(end_text):
                findings.append(
                    _finding(
                        "error",
                        "date-format",
                        f"{start_key}/{end_key} must use YYYY-MM-DD ISO dates.",
                        category="VALIDATION_ERROR",
                    )
                )
                return
            start = date.fromisoformat(start_text)
            end = date.fromisoformat(end_text)
            if end <= start:
                findings.append(
                    _finding(
                        "error",
                        "date-order",
                        f"{end_key} must be after {start_key}.",
                        category="VALIDATION_ERROR",
                    )
                )
            return
    findings.append(
        _finding(
            "warning",
            "date-constants",
            "No START_DATE/END_DATE constants detected.",
            hint="Use explicit date constants so reviewers can reproduce filtering.",
        )
    )


def validate_script(path: Path, semantic_rulesets: list[str] | None = None) -> ValidationReport:
    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    if JINJA_RE.search(text):
        findings.append(
            _finding(
                "error",
                "unresolved-template-token",
                "Script contains unresolved Jinja template tokens.",
                category="VALIDATION_ERROR",
            )
        )
    if SENSITIVE_RE.search(text):
        findings.append(
            _finding(
                "error",
                "credential-material",
                "Script appears to contain credential-related material.",
                hint="Remove secrets and load credentials only through local Earth Engine auth.",
                category="AUTH_ERROR",
            )
        )
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        findings.append(
            _finding(
                "error",
                "syntax-error",
                exc.msg,
                line=exc.lineno,
                hint="Fix Python syntax.",
                category="VALIDATION_ERROR",
            )
        )
        return ValidationReport(str(path), False, findings, semantic_rulesets or [])

    if not _imports_ee(tree):
        findings.append(
            _finding(
                "error",
                "missing-ee-import",
                "Script must import the Earth Engine Python API.",
                category="VALIDATION_ERROR",
            )
        )
    if not _has_call(tree, "filterDate"):
        findings.append(
            _finding(
                "error",
                "missing-filter-date",
                "Script must explicitly filter by date.",
                category="VALIDATION_ERROR",
            )
        )
    if not (_has_call(tree, "filterBounds") or "region=" in text or "geometry=" in text):
        findings.append(
            _finding(
                "error",
                "missing-region-filter",
                "Script must explicitly filter by region or pass an export region.",
                category="GEOMETRY_ERROR",
            )
        )
    if "cloud" not in text.lower() and "qa_pixel" not in text.lower() and "scl" not in text.lower():
        findings.append(
            _finding(
                "warning",
                "missing-cloud-mask",
                "No cloud or QA masking logic detected.",
                hint="Optical workflows should document and apply a cloud policy.",
                category="EMPTY_COLLECTION",
                retryable=True,
            )
        )
    if "scale=" not in text and "SCALE" not in text:
        findings.append(
            _finding("error", "missing-scale", "Reducer/export scale is required.", category="REDUCER_SCALE_ERROR")
        )
    if "crs=" not in text and "CRS" not in text:
        findings.append(
            _finding(
                "warning",
                "missing-crs",
                "No explicit CRS detected.",
                hint="Specify CRS when reproducibility across regions matters.",
                category="REDUCER_SCALE_ERROR",
                retryable=True,
            )
        )
    if "Export." not in text and "ee.batch.Export" not in text:
        findings.append(_finding("warning", "missing-export", "No Earth Engine export call detected."))
    if "description=" not in text:
        findings.append(_finding("warning", "missing-export-description", "No export description detected.", category="EXPORT_TASK_ERROR"))
    if "maxPixels" not in text and "max_pixels" not in text and "MAX_PIXELS" not in text:
        findings.append(
            _finding(
                "warning",
                "missing-max-pixels",
                "No maxPixels/max_pixels setting detected for export safety.",
                category="QUOTA_OR_TIMEOUT",
                retryable=True,
            )
        )
    for line in _call_lines(tree, "getInfo"):
        findings.append(
            _finding(
                "warning",
                "getinfo-call",
                "Avoid unnecessary getInfo() calls in production scripts.",
                line=line,
                hint="Prefer server-side operations and export server-side objects.",
                category="CLIENT_SERVER_MISUSE",
            )
        )
    assignments = _string_assignments(tree)
    _validate_dates(assignments, findings)
    numbers = _numeric_assignments(tree)
    if "SCALE" in numbers and numbers["SCALE"] <= 0:
        findings.append(_finding("error", "invalid-scale", "SCALE must be positive.", category="REDUCER_SCALE_ERROR"))
    if "TILE_SCALE" in numbers and numbers["TILE_SCALE"] <= 0:
        findings.append(_finding("error", "invalid-tile-scale", "TILE_SCALE must be positive.", category="REDUCER_SCALE_ERROR"))

    selected_rules = semantic_rulesets or []
    try:
        from .semantic import infer_semantic_rulesets, validate_semantics

        selected_rules = selected_rules or infer_semantic_rulesets(text)
        findings.extend(validate_semantics(path, selected_rules))
    except Exception as exc:
        findings.append(_finding("warning", "semantic-validation-unavailable", f"Semantic validation did not run: {exc}"))

    ok = not any(item.severity == "error" for item in findings)
    if ok:
        findings.insert(0, Finding("info", "validation-ok", "No blocking validation errors."))
    return ValidationReport(str(path), ok, findings, selected_rules)


def report_to_json(report: ValidationReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
