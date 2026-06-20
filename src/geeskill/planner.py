from __future__ import annotations

from dataclasses import dataclass

from .rag import SearchResult


@dataclass(frozen=True)
class Plan:
    task: str
    template: str | None
    body: str


def infer_template(task: str) -> str | None:
    lower = task.lower()
    if "hong kong" in lower and "ndvi" in lower and "district" in lower:
        return "hk_district_monthly_ndvi"
    if "landsat" in lower and ("lst" in lower or "surface temperature" in lower):
        return "landsat_lst"
    if "sentinel-2" in lower and "ndvi" in lower:
        return "sentinel2_ndvi_composite"
    if "zonal" in lower or "district" in lower or "reduce" in lower:
        return "zonal_statistics"
    return None


def build_plan(task: str, results: list[SearchResult], template: str | None = None) -> Plan:
    chosen = template or infer_template(task)
    citations = []
    for idx, result in enumerate(results, 1):
        target = result.url or result.source_path
        citations.append(f"[{idx}] {result.title} - {target}")
    citation_block = "\n".join(citations) if citations else "No local supporting docs found."
    assumptions = [
        "Confirm AOI geometry and administrative attributes before live execution.",
        "Use explicit date filters, scale, CRS, cloud policy, reducer, and export target.",
        "Run static validation and a dry run before contacting Earth Engine.",
    ]
    if chosen == "hk_district_monthly_ndvi":
        assumptions.append(
            "Use GAUL level-2 features filtered to Hong Kong and export monthly district NDVI means."
        )
    body = f"""# Earth Engine Workflow Plan

## Task

{task}

## Recommended Template

{chosen or "No built-in template inferred; create a task-specific script from references."}

## Assumptions

""" + "\n".join(f"- {item}" for item in assumptions) + f"""

## Steps

1. Search local documentation for dataset, reducer, cloud mask, export, and auth details.
2. Render a template with explicit AOI, dates, dataset id, scale, CRS, reducer, and export target.
3. Validate the rendered Python script offline with `gee-skill validate`.
4. Run `gee-skill run --dry-run` to confirm execution boundary.
5. Execute with an explicit Earth Engine project only after authentication is complete.
6. Monitor export tasks and record task state, destination, and errors.

## Validation Checklist

- Date filtering is explicit and date order is valid.
- AOI filtering or export region is explicit.
- Optical datasets include a cloud or QA mask.
- Reducers/export calls include scale and preferably CRS.
- Export descriptions and formats are stable.
- Script avoids unnecessary `getInfo()` calls.

## Retrieved Sources

{citation_block}
"""
    return Plan(task=task, template=chosen, body=body)

