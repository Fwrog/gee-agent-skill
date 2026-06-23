from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleSetCard:
    ruleset_id: str
    scope: str
    description: str
    checks: tuple[str, ...]
    error_categories: tuple[str, ...]
    validation_entrypoint: str
    examples: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ruleset_id": self.ruleset_id,
            "scope": self.scope,
            "description": self.description,
            "checks": list(self.checks),
            "error_categories": list(self.error_categories),
            "validation_entrypoint": self.validation_entrypoint,
            "examples": list(self.examples),
        }


RULESETS: tuple[RuleSetCard, ...] = (
    RuleSetCard(
        ruleset_id="agent_script_contract",
        scope="generated_scripts",
        description="Structure and safety contract distilled from official/community GEE examples for agent-generated scripts.",
        checks=(
            "no inline ee.Authenticate",
            "date windows exposed as constants",
            "dataset ids exposed as constants",
            "export descriptions, scale, and CRS exposed for review",
            "table exports expose selectors",
            "image exports expose maxPixels",
            "task.start behind a main() guard",
            "getInfo limited to bounded preflight/debug probes",
            "temporal and spatial filters before expensive map/reducer/export work",
            "quality masks before spectral index interpretation",
            "server-side date sequences for repeated cadences",
            "scale, CRS/projection, tileScale, and maxPixels exposed when relevant",
            "Browser and Computer Use remain observation/UI fallback surfaces, not normal execution",
        ),
        error_categories=(
            "AUTH_ERROR",
            "DATASET_NOT_FOUND",
            "VALIDATION_ERROR",
            "REDUCER_SCALE_ERROR",
            "QUOTA_OR_TIMEOUT",
            "EXPORT_TASK_ERROR",
            "CLIENT_SERVER_MISUSE",
        ),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("gee-skill validate outputs/scripts/hk_2024_01_ndvi_csv.py --semantic-rules agent_script_contract --json",),
    ),
    RuleSetCard(
        ruleset_id="global_safety",
        scope="all_scripts",
        description="Baseline script safety checks shared by every generated Earth Engine workflow.",
        checks=(
            "no unresolved Jinja tokens",
            "no credential material",
            "imports Earth Engine API",
            "explicit date filtering",
            "explicit region or export region",
            "positive scale and tileScale",
        ),
        error_categories=("AUTH_ERROR", "VALIDATION_ERROR", "GEOMETRY_ERROR", "REDUCER_SCALE_ERROR"),
        validation_entrypoint="geeskill.validation.validate_script",
        examples=("gee-skill validate outputs/scripts/hk_2024_01_ndvi_csv.py --json",),
    ),
    RuleSetCard(
        ruleset_id="optical_index",
        scope="optical_index_recipes",
        description="Common checks for Sentinel-2 and Landsat optical index workflows.",
        checks=("cloud or QA masking", "date and bounds filters", "explicit scale", "server-side reducers"),
        error_categories=("EMPTY_COLLECTION", "BAND_NOT_FOUND", "CLIENT_SERVER_MISUSE"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("NDVI", "EVI", "NDWI", "NDBI"),
    ),
    RuleSetCard(
        ruleset_id="vegetation_index_ndvi",
        scope="vegetation_index",
        description="NDVI-specific normalized difference and auditability checks.",
        checks=("NIR and red bands", "NDVI band/property naming", "image count metadata", "cloud policy"),
        error_categories=("BAND_NOT_FOUND", "EMPTY_COLLECTION", "VALIDATION_ERROR"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("sentinel2_ndvi_monthly_zonal",),
    ),
    RuleSetCard(
        ruleset_id="water_index_ndwi",
        scope="water_index",
        description="NDWI/MNDWI checks for green, NIR, and SWIR band use.",
        checks=("green band present", "NIR or SWIR band present", "cloud policy", "explicit output type"),
        error_categories=("BAND_NOT_FOUND", "EMPTY_COLLECTION", "EXPORT_TASK_ERROR"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("water-index-ndwi recipe",),
    ),
    RuleSetCard(
        ruleset_id="builtup_index_ndbi",
        scope="builtup_index",
        description="NDBI checks for SWIR/NIR band use and output audit fields.",
        checks=("SWIR band present", "NIR band present", "cloud policy", "explicit reducer scale"),
        error_categories=("BAND_NOT_FOUND", "REDUCER_SCALE_ERROR", "EMPTY_COLLECTION"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("builtup-index-ndbi recipe",),
    ),
    RuleSetCard(
        ruleset_id="landsat_lst",
        scope="land_surface_temperature",
        description="Landsat Collection 2 ST_B10 scale/offset and QA checks.",
        checks=("ST_B10 present", "scale 0.00341802", "offset 149.0", "QA_PIXEL mask"),
        error_categories=("BAND_NOT_FOUND", "VALIDATION_ERROR", "EMPTY_COLLECTION"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("landsat_c2_lst",),
    ),
    RuleSetCard(
        ruleset_id="sentinel1_flood_before_after",
        scope="flood_mapping",
        description="Sentinel-1 SAR before/after flood workflow checks.",
        checks=("COPERNICUS/S1_GRD", "IW mode", "polarization filter", "before/after windows", "change metric"),
        error_categories=("DATASET_NOT_FOUND", "BAND_NOT_FOUND", "VALIDATION_ERROR"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("sentinel1_flood_before_after",),
    ),
    RuleSetCard(
        ruleset_id="export_table_csv",
        scope="export_table",
        description="CSV table export contract checks.",
        checks=("Export.table.toDrive", "fileFormat CSV", "description", "selectors"),
        error_categories=("EXPORT_TASK_ERROR",),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("gee-skill validate script.py --semantic-rules export_table_csv --json",),
    ),
    RuleSetCard(
        ruleset_id="export_image_geotiff",
        scope="export_image",
        description="GeoTIFF image export contract checks.",
        checks=("Export.image.toDrive", "region", "scale", "maxPixels", "fileFormat GeoTIFF"),
        error_categories=("EXPORT_TASK_ERROR", "GEOMETRY_ERROR", "REDUCER_SCALE_ERROR"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("image-export-geotiff recipe",),
    ),
    RuleSetCard(
        ruleset_id="dynamic_world_landcover",
        scope="landcover_stratified_statistics",
        description="Dynamic World class label, probability band, threshold, and fraction checks.",
        checks=("label band", "probability bands", "probability threshold", "class fractions", "null-tolerant sparse classes"),
        error_categories=("NO_LANDCOVER_LABEL", "NO_PROBABILITY_BANDS", "CLASS_MASK_EMPTY"),
        validation_entrypoint="geeskill.semantic.validate_semantics",
        examples=("dynamic_world_landcover_ndvi",),
    ),
)


def list_rulesets() -> list[dict[str, Any]]:
    return [card.to_dict() for card in RULESETS]


def get_ruleset(ruleset_id: str) -> dict[str, Any] | None:
    normalized = ruleset_id.lower()
    for card in RULESETS:
        if card.ruleset_id.lower() == normalized:
            return card.to_dict()
    return None
