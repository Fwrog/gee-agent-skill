from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import Finding


@dataclass(frozen=True)
class SemanticRuleSet:
    name: str
    description: str


RULESETS = {
    "sentinel2_ndvi_monthly_zonal": SemanticRuleSet(
        "sentinel2_ndvi_monthly_zonal", "Sentinel-2 NDVI monthly composite/zonal statistics."
    ),
    "landsat_c2_lst": SemanticRuleSet("landsat_c2_lst", "Landsat Collection 2 LST workflow."),
    "sentinel1_flood_before_after": SemanticRuleSet(
        "sentinel1_flood_before_after", "Sentinel-1 before/after flood workflow."
    ),
    "export_table_csv": SemanticRuleSet("export_table_csv", "Export.table.toDrive CSV export."),
}


def infer_semantic_rulesets(text: str, explicit: str | None = None) -> list[str]:
    if explicit:
        return [item.strip() for item in explicit.split(",") if item.strip()]
    lower = text.lower()
    rules: list[str] = []
    if "copernicus/s2_sr_harmonized" in lower and "ndvi" in lower:
        rules.append("sentinel2_ndvi_monthly_zonal")
    if "landsat/" in lower and ("st_b10" in lower or "lst" in lower):
        rules.append("landsat_c2_lst")
    if "copernicus/s1_grd" in lower or ("sentinel-1" in lower and "flood" in lower):
        rules.append("sentinel1_flood_before_after")
    if "export.table.todrive" in lower or "ee.batch.export.table.todrive" in lower:
        rules.append("export_table_csv")
    return rules


def validate_semantics(path: Path, rulesets: list[str] | None = None) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    selected = rulesets or infer_semantic_rulesets(text)
    findings: list[Finding] = []
    for ruleset in selected:
        if ruleset == "sentinel2_ndvi_monthly_zonal":
            findings.extend(_sentinel2_ndvi(text, lower))
        elif ruleset == "landsat_c2_lst":
            findings.extend(_landsat_lst(text, lower))
        elif ruleset == "sentinel1_flood_before_after":
            findings.extend(_sentinel1_flood(text, lower))
        elif ruleset == "export_table_csv":
            findings.extend(_export_table_csv(text, lower))
        else:
            findings.append(Finding("warning", "unknown-semantic-ruleset", f"Unknown ruleset: {ruleset}", ruleset=ruleset))
    if selected and not any(item.severity == "error" for item in findings):
        findings.append(
            Finding(
                "info",
                "semantic-validation-ok",
                f"Semantic rules passed: {', '.join(selected)}",
            )
        )
    return findings


def _require(
    condition: bool,
    ruleset: str,
    code: str,
    message: str,
    category: str,
    hint: str | None = None,
    retryable: bool = False,
) -> list[Finding]:
    if condition:
        return []
    return [
        Finding(
            "error",
            code,
            message,
            hint=hint,
            category=category,
            rule_id=f"{ruleset}.{code}",
            ruleset=ruleset,
            retryable=retryable,
        )
    ]


def _sentinel2_ndvi(text: str, lower: str) -> list[Finding]:
    ruleset = "sentinel2_ndvi_monthly_zonal"
    findings: list[Finding] = []
    findings += _require('"B8"' in text and '"B4"' in text, ruleset, "s2-ndvi-bands", "Sentinel-2 NDVI must use B8 NIR and B4 red bands.", "BAND_NOT_FOUND")
    findings += _require("filterdate" in lower, ruleset, "s2-date-filter", "Sentinel-2 workflow needs filterDate.", "VALIDATION_ERROR")
    findings += _require("filterbounds" in lower or "region=" in lower, ruleset, "s2-region-filter", "Sentinel-2 workflow needs explicit region filtering or export region.", "GEOMETRY_ERROR", retryable=True)
    findings += _require("scl" in lower or "cloud" in lower or "qa60" in lower, ruleset, "s2-cloud-mask", "Sentinel-2 NDVI workflow needs an explicit cloud masking strategy.", "EMPTY_COLLECTION", retryable=True)
    findings += _require("sequence(1, 12)" in lower or "advance(1, \"month\")" in lower or "advance(1, 'month')" in lower, ruleset, "s2-monthly-aggregation", "Monthly NDVI workflow must explicitly aggregate by month.", "VALIDATION_ERROR")
    findings += _require("scale=" in lower or "scale" in text, ruleset, "s2-scale", "Reducer/export scale is required.", "REDUCER_SCALE_ERROR", retryable=True)
    findings += _require("selectors=" in lower, ruleset, "s2-output-schema", "CSV export must define selectors for a stable output schema.", "EXPORT_TASK_ERROR")
    findings += _require("image_count" in lower, ruleset, "s2-image-count", "Monthly statistics must expose image_count for auditability.", "EMPTY_COLLECTION", retryable=True)
    if "getinfo(" in lower:
        findings.append(
            Finding(
                "error",
                "unsafe-large-getinfo",
                "Sentinel-2 workflow contains getInfo(), which is unsafe for large collections.",
                hint="Export server-side objects or write metadata properties instead.",
                category="CLIENT_SERVER_MISUSE",
                rule_id=f"{ruleset}.unsafe-large-getinfo",
                ruleset=ruleset,
                retryable=False,
            )
        )
    return findings


def _landsat_lst(text: str, lower: str) -> list[Finding]:
    ruleset = "landsat_c2_lst"
    findings: list[Finding] = []
    findings += _require("st_b10" in lower, ruleset, "landsat-st-b10", "Landsat LST workflow must use ST_B10.", "BAND_NOT_FOUND")
    findings += _require("0.00341802" in text and "149.0" in text, ruleset, "landsat-lst-scale-offset", "Landsat Collection 2 ST_B10 needs scale 0.00341802 and offset 149.0.", "VALIDATION_ERROR")
    findings += _require("qa_pixel" in lower, ruleset, "landsat-qa-pixel", "Landsat LST workflow needs QA_PIXEL masking.", "EMPTY_COLLECTION", retryable=True)
    findings += _require("filterdate" in lower, ruleset, "landsat-date-filter", "Landsat workflow needs filterDate.", "VALIDATION_ERROR")
    findings += _require("filterbounds" in lower, ruleset, "landsat-region-filter", "Landsat workflow needs filterBounds.", "GEOMETRY_ERROR", retryable=True)
    return findings


def _sentinel1_flood(text: str, lower: str) -> list[Finding]:
    ruleset = "sentinel1_flood_before_after"
    findings: list[Finding] = []
    findings += _require("copernicus/s1_grd" in lower, ruleset, "s1-dataset", "Sentinel-1 flood workflow must use COPERNICUS/S1_GRD.", "DATASET_NOT_FOUND")
    findings += _require("instrumentmode" in lower and "iw" in lower, ruleset, "s1-iw", "Filter Sentinel-1 to IW mode.", "VALIDATION_ERROR")
    findings += _require("transmitterreceiverpolarisation" in lower and ("vv" in lower or "vh" in lower), ruleset, "s1-polarization", "Filter Sentinel-1 by VV or VH polarization.", "BAND_NOT_FOUND")
    findings += _require("before" in lower and "after" in lower, ruleset, "s1-before-after", "Flood workflow must explicitly define before and after windows.", "VALIDATION_ERROR")
    findings += _require("divide" in lower or "subtract" in lower or "ratio" in lower, ruleset, "s1-change-metric", "Flood workflow needs an explicit change metric.", "VALIDATION_ERROR")
    return findings


def _export_table_csv(text: str, lower: str) -> list[Finding]:
    ruleset = "export_table_csv"
    findings: list[Finding] = []
    findings += _require("export.table.todrive" in lower or "ee.batch.export.table.todrive" in lower, ruleset, "table-export-call", "Workflow must use Export.table.toDrive for CSV table output.", "EXPORT_TASK_ERROR")
    findings += _require("fileformat=\"csv\"" in lower or "fileformat='csv'" in lower, ruleset, "csv-format", "CSV export must set fileFormat='CSV'.", "EXPORT_TASK_ERROR")
    findings += _require("description=" in lower, ruleset, "export-description", "Export task needs a stable description.", "EXPORT_TASK_ERROR")
    findings += _require("selectors=" in lower, ruleset, "export-selectors", "CSV export should specify selectors.", "EXPORT_TASK_ERROR")
    return findings
