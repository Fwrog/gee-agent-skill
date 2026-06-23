from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Recipe:
    recipe_id: str
    task_type: str
    description: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    candidate_datasets: tuple[str, ...]
    default_dataset_policy: str
    template: str | None
    preflight_profile: str
    validation_profile: str
    output_schema: tuple[str, ...]
    live_risk_level: str
    examples: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipe_id": self.recipe_id,
            "task_type": self.task_type,
            "description": self.description,
            "required_inputs": list(self.required_inputs),
            "optional_inputs": list(self.optional_inputs),
            "candidate_datasets": list(self.candidate_datasets),
            "default_dataset_policy": self.default_dataset_policy,
            "template": self.template,
            "preflight_profile": self.preflight_profile,
            "validation_profile": self.validation_profile,
            "output_schema": list(self.output_schema),
            "live_risk_level": self.live_risk_level,
            "examples": list(self.examples),
        }


RECIPES: tuple[Recipe, ...] = (
    Recipe(
        recipe_id="vegetation-index-ndvi",
        task_type="vegetation_index",
        description="Compute NDVI from optical surface reflectance and export an image or table.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("grouping", "temporal_cadence", "cloud_policy", "dataset_id"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
        default_dataset_policy="Prefer Sentinel-2 SR for 10m regional NDVI unless Landsat continuity is requested.",
        template="sentinel2_ndvi_composite",
        preflight_profile="optical_index",
        validation_profile="vegetation_index_ndvi",
        output_schema=("aoi_name", "date_start", "date_end", "mean_ndvi", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute 16-day NDVI for Hong Kong in 2024 and export CSV.",),
    ),
    Recipe(
        recipe_id="vegetation-index-evi",
        task_type="vegetation_index",
        description="Compute EVI from optical reflectance bands with explicit coefficients.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("dataset_id", "cloud_policy", "scale"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
        default_dataset_policy="Prefer Sentinel-2 for current 10m analyses; use Landsat for long historical continuity.",
        template=None,
        preflight_profile="optical_index",
        validation_profile="optical_index",
        output_schema=("aoi_name", "date_start", "date_end", "mean_evi", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute EVI for a supplied AOI in March 2024 and export CSV.",),
    ),
    Recipe(
        recipe_id="water-index-ndwi",
        task_type="water_index",
        description="Compute NDWI or MNDWI from optical imagery for water diagnostics.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("dataset_id", "index_variant", "cloud_policy"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
        default_dataset_policy="Prefer Sentinel-2 SR for 10m NDWI/MNDWI unless Landsat is requested.",
        template=None,
        preflight_profile="optical_index",
        validation_profile="water_index_ndwi",
        output_schema=("aoi_name", "date_start", "date_end", "mean_ndwi", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute NDWI for a supplied AOI in March 2024 and export GeoTIFF.",),
    ),
    Recipe(
        recipe_id="builtup-index-ndbi",
        task_type="builtup_index",
        description="Compute NDBI from SWIR and NIR bands for built-up diagnostics.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("dataset_id", "cloud_policy"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
        default_dataset_policy="Prefer Sentinel-2 SR for 10m NDBI when the AOI/time range has coverage.",
        template=None,
        preflight_profile="optical_index",
        validation_profile="builtup_index_ndbi",
        output_schema=("aoi_name", "date_start", "date_end", "mean_ndbi", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute NDBI for Hong Kong in 2024 and export CSV.",),
    ),
    Recipe(
        recipe_id="landsat-lst",
        task_type="land_surface_temperature",
        description="Compute Landsat Collection 2 land surface temperature with QA_PIXEL masking.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("dataset_id", "temperature_unit", "cloud_policy"),
        candidate_datasets=("LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
        default_dataset_policy="Use Landsat Collection 2 Level 2 ST_B10 with documented scale and offset.",
        template="landsat_lst",
        preflight_profile="landsat_lst",
        validation_profile="landsat_lst",
        output_schema=("aoi_name", "date_start", "date_end", "mean_lst_c", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute Landsat LST for Hong Kong in summer 2024 and export CSV.",),
    ),
    Recipe(
        recipe_id="sentinel1-flood-before-after",
        task_type="flood_mapping",
        description="Compare Sentinel-1 before/after SAR windows for flood or water-change mapping.",
        required_inputs=("aoi", "before_time_range", "after_time_range", "output"),
        optional_inputs=("polarization", "orbit_pass", "threshold"),
        candidate_datasets=("COPERNICUS/S1_GRD",),
        default_dataset_policy="Use Sentinel-1 GRD with matched instrument mode, polarization, and orbit filters.",
        template="sentinel1_flood_before_after",
        preflight_profile="sentinel1_change",
        validation_profile="sentinel1_flood_before_after",
        output_schema=("aoi_name", "before_start", "before_end", "after_start", "after_end", "flood_area", "dataset_id"),
        live_risk_level="medium",
        examples=("Map Sentinel-1 flood extent for a supplied AOI before and after a storm.",),
    ),
    Recipe(
        recipe_id="landcover-stratified-ndvi",
        task_type="landcover_stratified_statistics",
        description="Compute NDVI diagnostics by Dynamic World land-cover class.",
        required_inputs=("aoi", "time_range", "output"),
        optional_inputs=("probability_threshold", "class_groups", "dataset_id"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "GOOGLE/DYNAMICWORLD/V1", "ESA/WorldCover/v200"),
        default_dataset_policy="Use Dynamic World for time-matched masks and ESA WorldCover only as static reference.",
        template="hk_january_2024_ndvi_by_landcover_csv",
        preflight_profile="landcover_stratified",
        validation_profile="dynamic_world_landcover_ndvi",
        output_schema=("all_surface_mean_ndvi", "non_water_mean_ndvi", "vegetation_mean_ndvi", "class_fractions"),
        live_risk_level="medium",
        examples=("Compute January 2024 Hong Kong NDVI by land-cover class and export CSV.",),
    ),
    Recipe(
        recipe_id="zonal-statistics-table",
        task_type="zonal_statistics",
        description="Reduce an image or index product over supplied zones and export a table.",
        required_inputs=("image_or_index", "zones", "time_range", "output"),
        optional_inputs=("reducer", "scale", "selectors"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2"),
        default_dataset_policy="Select dataset from the index or image recipe, then reduce over explicit zones.",
        template="zonal_statistics",
        preflight_profile="zonal_statistics",
        validation_profile="export_table_csv",
        output_schema=("zone_id", "metric", "value", "dataset_id", "scale_m", "crs"),
        live_risk_level="medium",
        examples=("Compute zonal statistics for a supplied GeoJSON and export CSV.",),
    ),
    Recipe(
        recipe_id="image-export-geotiff",
        task_type="export_image",
        description="Export a validated Earth Engine image product to Drive as GeoTIFF.",
        required_inputs=("image_or_index", "aoi", "time_range", "output"),
        optional_inputs=("scale", "crs", "max_pixels"),
        candidate_datasets=("COPERNICUS/S2_SR_HARMONIZED", "LANDSAT/LC08/C02/T1_L2", "COPERNICUS/S1_GRD"),
        default_dataset_policy="Use the source dataset selected by the upstream image recipe.",
        template=None,
        preflight_profile="export_image",
        validation_profile="export_image_geotiff",
        output_schema=("image", "region", "scale_m", "crs", "file_format", "export_description"),
        live_risk_level="high",
        examples=("Export March 2024 NDWI for a supplied AOI as GeoTIFF.",),
    ),
    Recipe(
        recipe_id="table-export-csv",
        task_type="export_table",
        description="Export a validated feature collection to Drive as CSV with explicit selectors.",
        required_inputs=("feature_collection", "output_schema", "export"),
        optional_inputs=("drive_folder", "file_prefix"),
        candidate_datasets=(),
        default_dataset_policy="Use table output from the upstream reducer recipe.",
        template=None,
        preflight_profile="export_table",
        validation_profile="export_table_csv",
        output_schema=("selectors", "file_format", "export_description", "drive_folder"),
        live_risk_level="high",
        examples=("Export zonal statistics as CSV.",),
    ),
)


def list_recipes() -> list[dict[str, Any]]:
    return [recipe.to_dict() for recipe in RECIPES]


def get_recipe(recipe_id: str) -> dict[str, Any] | None:
    normalized = recipe_id.lower()
    for recipe in RECIPES:
        if recipe.recipe_id.lower() == normalized:
            return recipe.to_dict()
    return None


def recipes_for_task(task_type: str) -> list[dict[str, Any]]:
    normalized = task_type.lower()
    return [recipe.to_dict() for recipe in RECIPES if recipe.task_type == normalized]


def closest_recipes(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    terms = [item for item in query.lower().replace("-", " ").replace("_", " ").split() if item]
    scored: list[tuple[int, Recipe]] = []
    for recipe in RECIPES:
        haystack = " ".join(
            [
                recipe.recipe_id,
                recipe.task_type,
                recipe.description,
                " ".join(recipe.candidate_datasets),
                " ".join(recipe.examples),
            ]
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, recipe))
    scored.sort(key=lambda item: (-item[0], item[1].recipe_id))
    return [recipe.to_dict() for _, recipe in scored[:top_k]]


def default_recipe_for(task_type: str, metric: str | None = None, output_type: str | None = None) -> dict[str, Any] | None:
    task = task_type.lower()
    metric_name = (metric or "").lower()
    output = (output_type or "").lower()
    if task == "flood_mapping":
        return get_recipe("sentinel1-flood-before-after")
    if output == "geotiff":
        return get_recipe("image-export-geotiff")
    if task == "vegetation_index" and metric_name == "evi":
        return get_recipe("vegetation-index-evi")
    if task == "vegetation_index":
        return get_recipe("vegetation-index-ndvi")
    if task == "water_index":
        return get_recipe("water-index-ndwi")
    if task == "builtup_index":
        return get_recipe("builtup-index-ndbi")
    matches = recipes_for_task(task)
    return matches[0] if matches else None
