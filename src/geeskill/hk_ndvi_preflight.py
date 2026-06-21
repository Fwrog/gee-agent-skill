from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .earthengine import initialize
from .errors import error_payload
from .paths import default_boundary_path


DEFAULT_DATASET_ID = "COPERNICUS/S2_SR_HARMONIZED"
DEFAULT_LANDCOVER_DATASET_ID = "GOOGLE/DYNAMICWORLD/V1"
DEFAULT_BOUNDARY_NAME = "hk_18_districts.geojson"
DEFAULT_DISTRICT_PROPERTY = "District"
DYNAMIC_WORLD_PROBABILITY_BANDS = [
    "water",
    "trees",
    "grass",
    "flooded_vegetation",
    "crops",
    "shrub_and_scrub",
    "built",
    "bare",
    "snow_and_ice",
]
DYNAMIC_WORLD_VEGETATION_BANDS = [
    "trees",
    "grass",
    "flooded_vegetation",
    "crops",
    "shrub_and_scrub",
]


@dataclass(frozen=True)
class HKNDVIPreflightConfig:
    project: str | None
    year: int
    month: int
    scope: str = "district"
    district: str | None = None
    dataset_id: str = DEFAULT_DATASET_ID
    boundary_geojson: str | Path | None = None
    district_property: str = DEFAULT_DISTRICT_PROPERTY
    scale: int = 10
    crs: str = "EPSG:4326"
    cloudy_pixel_percentage: int = 80
    tile_scale: int = 4
    landcover: str | None = None
    landcover_dataset_id: str | None = None
    landcover_strategy: str | None = None
    dynamic_world_probability_threshold: float = 0.35


class HKNDVIProbe(Protocol):
    def initialize(self) -> None: ...

    def probe_district_source(self) -> dict[str, Any]: ...

    def select_district(self, district_name: str | None, district_names: list[str]) -> dict[str, Any]: ...

    def probe_images(self, year: int, month: int) -> dict[str, Any]: ...

    def probe_landcover(self, year: int, month: int) -> dict[str, Any]: ...


def normalize_district_name(name: str) -> str:
    text = name.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "", text)


def resolve_district_name(requested: str, district_names: list[str]) -> str | None:
    requested_norm = normalize_district_name(requested)
    for name in district_names:
        if normalize_district_name(name) == requested_norm:
            return name
    return None


def resolve_boundary_path(path: str | Path | None) -> Path:
    if path:
        candidate = Path(path)
        if candidate.exists():
            return candidate
        repo_candidate = Path.cwd() / candidate
        if repo_candidate.exists():
            return repo_candidate
    return default_boundary_path(DEFAULT_BOUNDARY_NAME)


def load_boundary_geojson(path: str | Path | None = None) -> dict[str, Any]:
    resolved = resolve_boundary_path(path)
    try:
        return json.loads(resolved.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Hong Kong district boundary GeoJSON not found: {resolved}. "
            "Use --boundary-geojson or reinstall package resources."
        ) from exc


def load_boundary_feature_collection(ee, path: str | Path | None = None):
    data = load_boundary_geojson(path)
    features = []
    for item in data.get("features", []):
        geometry = item.get("geometry")
        properties = item.get("properties", {})
        if geometry:
            features.append(ee.Feature(ee.Geometry(geometry), properties))
    return ee.FeatureCollection(features)


class EarthEngineHKNDVIProbe:
    def __init__(self, config: HKNDVIPreflightConfig):
        self.config = config
        self.ee = None
        self.districts = None
        self.selected = None

    def initialize(self) -> None:
        self.ee = initialize(project=self.config.project, authenticate=False)

    def _ee(self):
        if self.ee is None:
            raise RuntimeError("Earth Engine has not been initialized.")
        return self.ee

    def _districts(self):
        if self.districts is None:
            self.districts = load_boundary_feature_collection(
                self._ee(), self.config.boundary_geojson
            )
        return self.districts

    def probe_district_source(self) -> dict[str, Any]:
        ee = self._ee()
        districts = self._districts()
        count = int(districts.size().getInfo())
        property_names: list[str] = []
        district_names: list[str] = []
        if count > 0:
            first = ee.Feature(districts.first())
            property_names = first.toDictionary().keys().getInfo()
            district_names = (
                districts.aggregate_array(self.config.district_property)
                .distinct()
                .sort()
                .getInfo()
            )
        return {
            "district_source": str(resolve_boundary_path(self.config.boundary_geojson)),
            "district_source_type": "local_geojson",
            "district_property": self.config.district_property,
            "district_feature_count": count,
            "admin_property_names": property_names[:30],
            "sample_district_names": district_names[:30],
            "all_district_names_count": len(district_names),
        }

    def select_district(self, district_name: str | None, district_names: list[str]) -> dict[str, Any]:
        districts = self._districts()
        canonical = None
        selected = districts
        if district_name:
            canonical = resolve_district_name(district_name, district_names)
            if canonical is None:
                self.selected = districts.filter(
                    self._ee().Filter.eq(self.config.district_property, district_name)
                )
            else:
                self.selected = districts.filter(
                    self._ee().Filter.eq(self.config.district_property, canonical)
                )
            selected = self.selected
        else:
            self.selected = districts
        selected_count = int(selected.size().getInfo())
        area_m2 = None
        if selected_count > 0:
            area_m2 = float(selected.geometry().area(1).getInfo())
        return {
            "requested_district": district_name,
            "selected_district_name": canonical or district_name,
            "selected_district_count": selected_count,
            "selected_geometry_area_m2": area_m2,
        }

    def probe_images(self, year: int, month: int) -> dict[str, Any]:
        ee = self._ee()
        if self.selected is None:
            raise RuntimeError("District selection has not been probed.")
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, "month")
        aoi = self.selected.geometry()
        base = (
            ee.ImageCollection(self.config.dataset_id)
            .filterDate(start, end)
            .filterBounds(aoi)
        )
        filtered = base.filter(
            ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.config.cloudy_pixel_percentage)
        )
        image_count = int(base.size().getInfo())
        filtered_count = int(filtered.size().getInfo())
        first_band_names: list[str] = []
        ndvi_band_names: list[str] = []
        sanity_stat: dict[str, Any] = {}
        if filtered_count > 0:
            with_ndvi = filtered.map(_mask_sentinel2_scl).map(_add_ndvi)
            first_band_names = ee.Image(with_ndvi.first()).bandNames().getInfo()
            monthly_ndvi = with_ndvi.select("NDVI").mean()
            ndvi_band_names = monthly_ndvi.bandNames().getInfo()
            if "NDVI" in ndvi_band_names:
                sanity_stat = monthly_ndvi.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=aoi,
                    scale=max(self.config.scale, 100),
                    crs=self.config.crs,
                    bestEffort=True,
                    maxPixels=100000000,
                    tileScale=self.config.tile_scale,
                ).getInfo()
        return {
            "date_start": f"{year}-{month:02d}-01",
            "date_end": _next_month_date(year, month),
            "s2_image_count": image_count,
            "s2_cloud_filtered_image_count": filtered_count,
            "first_image_band_names_after_ndvi": first_band_names,
            "monthly_ndvi_band_names": ndvi_band_names,
            "sanity_stat": sanity_stat,
        }

    def probe_landcover(self, year: int, month: int) -> dict[str, Any]:
        ee = self._ee()
        if self.selected is None:
            raise RuntimeError("District selection has not been probed.")
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, "month")
        aoi = self.selected.geometry()
        dataset_id = self.config.landcover_dataset_id or DEFAULT_LANDCOVER_DATASET_ID
        threshold = float(self.config.dynamic_world_probability_threshold)
        dw = ee.ImageCollection(dataset_id).filterDate(start, end).filterBounds(aoi)
        count = int(dw.size().getInfo())
        band_names: list[str] = []
        diagnostics: dict[str, Any] = {
            "landcover_dataset_id": dataset_id,
            "landcover_strategy": self.config.landcover_strategy or "dynamic_world_time_matched_probability_masks",
            "dynamic_world_probability_threshold": threshold,
            "dynamic_world_image_count": count,
            "dynamic_world_band_names": band_names,
            "missing_probability_bands": list(DYNAMIC_WORLD_PROBABILITY_BANDS),
            "has_label_band": False,
            "class_fractions": {},
            "ndvi_probes": {},
            "warnings": [],
        }
        if count == 0:
            return diagnostics

        first = ee.Image(dw.first())
        band_names = first.bandNames().getInfo()
        diagnostics["dynamic_world_band_names"] = band_names
        diagnostics["has_label_band"] = "label" in band_names
        missing = [band for band in DYNAMIC_WORLD_PROBABILITY_BANDS if band not in band_names]
        diagnostics["missing_probability_bands"] = missing
        if missing:
            return diagnostics

        s2 = (
            ee.ImageCollection(self.config.dataset_id)
            .filterDate(start, end)
            .filterBounds(aoi)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.config.cloudy_pixel_percentage))
            .map(_mask_sentinel2_scl)
            .map(_add_ndvi)
        )
        ndvi = s2.select("NDVI").mean().rename("NDVI")
        probabilities = dw.select(DYNAMIC_WORLD_PROBABILITY_BANDS).mean()
        masks = _dynamic_world_masks(ee, probabilities, threshold)

        class_fractions = ee.Dictionary(
            {
                key: _mask_fraction(ee, mask, aoi, self.config)
                for key, mask in masks.items()
            }
        ).getInfo()
        ndvi_probes = ee.Dictionary(
            {
                "all_surface_mean_ndvi": _masked_ndvi_mean(ee, ndvi, None, aoi, self.config),
                "non_water_mean_ndvi": _masked_ndvi_mean(ee, ndvi, masks["non_water"], aoi, self.config),
                "vegetation_mean_ndvi": _masked_ndvi_mean(ee, ndvi, masks["vegetation"], aoi, self.config),
                "built_mean_ndvi": _masked_ndvi_mean(ee, ndvi, masks["built"], aoi, self.config),
                "water_mean_ndvi": _masked_ndvi_mean(ee, ndvi, masks["water"], aoi, self.config),
            }
        ).getInfo()
        diagnostics["class_fractions"] = class_fractions
        diagnostics["ndvi_probes"] = ndvi_probes
        for key in ("water", "built", "vegetation", "trees", "grass"):
            value = class_fractions.get(key)
            if value is None:
                diagnostics["warnings"].append(f"{key} fraction is null at this scale/AOI.")
            elif float(value) <= 0:
                diagnostics["warnings"].append(f"{key} fraction is zero; class NDVI may be null.")
        return diagnostics


def _dynamic_world_masks(ee, probabilities, threshold: float) -> dict[str, Any]:
    water = probabilities.select("water").gte(threshold)
    trees = probabilities.select("trees").gte(threshold)
    grass = probabilities.select("grass").gte(threshold)
    flooded = probabilities.select("flooded_vegetation").gte(threshold)
    crops = probabilities.select("crops").gte(threshold)
    shrub = probabilities.select("shrub_and_scrub").gte(threshold)
    built = probabilities.select("built").gte(threshold)
    bare = probabilities.select("bare").gte(threshold)
    vegetation = trees.Or(grass).Or(flooded).Or(crops).Or(shrub)
    non_water = water.Not()
    return {
        "water": water.rename("class_mask"),
        "non_water": non_water.rename("class_mask"),
        "land_only": non_water.rename("class_mask"),
        "vegetation": vegetation.rename("class_mask"),
        "trees": trees.rename("class_mask"),
        "grass": grass.rename("class_mask"),
        "flooded_vegetation": flooded.rename("class_mask"),
        "crops": crops.rename("class_mask"),
        "shrub_and_scrub": shrub.rename("class_mask"),
        "built": built.rename("class_mask"),
        "bare": bare.rename("class_mask"),
    }


def _mask_fraction(ee, mask, aoi, config: HKNDVIPreflightConfig):
    return (
        mask.unmask(0)
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=max(config.scale, 100),
            crs=config.crs,
            bestEffort=True,
            maxPixels=100000000,
            tileScale=config.tile_scale,
        )
        .get("class_mask")
    )


def _masked_ndvi_mean(ee, ndvi, mask, aoi, config: HKNDVIPreflightConfig):
    image = ndvi if mask is None else ndvi.updateMask(mask)
    return image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi,
        scale=max(config.scale, 100),
        crs=config.crs,
        bestEffort=True,
        maxPixels=100000000,
        tileScale=config.tile_scale,
    ).get("NDVI")


def _mask_sentinel2_scl(image):
    scl = image.select("SCL")
    valid = (
        scl.neq(0)
        .And(scl.neq(1))
        .And(scl.neq(3))
        .And(scl.neq(7))
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )
    return image.updateMask(valid)


def _add_ndvi(image):
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def _next_month_date(year: int, month: int) -> str:
    if month == 12:
        return f"{year + 1}-01-01"
    return f"{year}-{month + 1:02d}-01"


def _base_report(config: HKNDVIPreflightConfig) -> dict[str, Any]:
    return {
        "ok": False,
        "decision": "block_export",
        "project": config.project,
        "year": config.year,
        "month": config.month,
        "scope": config.scope,
        "aoi_name": config.district or "Hong Kong",
        "aoi_source": str(resolve_boundary_path(config.boundary_geojson)),
        "aoi_area_m2": None,
        "requested_district": config.district,
        "dataset_id": config.dataset_id,
        "critical_error": None,
        "errors": [],
        "warnings": [],
        "image_count_before_cloud_filter": None,
        "image_count_after_cloud_filter": None,
        "band_names": [],
        "mean_ndvi_probe": None,
        "landcover_dataset_id": config.landcover_dataset_id,
        "landcover_strategy": config.landcover_strategy,
        "dynamic_world_probability_threshold": config.dynamic_world_probability_threshold,
        "dynamic_world_image_count": None,
        "landcover_diagnostics": None,
        "expected_export_rows": 0,
        "checks": {},
    }


def _fail(report: dict[str, Any], category: str, message: str) -> dict[str, Any]:
    report["ok"] = False
    report["decision"] = "block_export"
    report["critical_error"] = error_payload(category, message)
    report["errors"] = [report["critical_error"]]
    return report


def run_hk_ndvi_preflight(
    config: HKNDVIPreflightConfig,
    probe: HKNDVIProbe | None = None,
) -> dict[str, Any]:
    if not (1 <= int(config.month) <= 12):
        report = _base_report(config)
        return _fail(report, "VALIDATION_ERROR", f"Month must be 1..12, got {config.month}.")

    report = _base_report(config)
    live_probe = probe or EarthEngineHKNDVIProbe(config)
    live_probe.initialize()
    report["checks"]["ee_initialize"] = {"ok": True}

    district_info = live_probe.probe_district_source()
    report["checks"]["district_source"] = district_info
    if int(district_info.get("district_feature_count") or 0) == 0:
        return _fail(report, "EMPTY_AOI", "Hong Kong district source returned zero features.")

    district_names = list(district_info.get("sample_district_names") or [])
    selected_name = None if config.scope == "hong-kong" else config.district
    selected_info = live_probe.select_district(selected_name, district_names)
    report["checks"]["selected_district"] = selected_info
    report["aoi_name"] = selected_info.get("selected_district_name") or "Hong Kong"
    report["aoi_area_m2"] = selected_info.get("selected_geometry_area_m2")
    if int(selected_info.get("selected_district_count") or 0) == 0:
        sampled = ", ".join(district_names[:20])
        return _fail(
            report,
            "DISTRICT_NOT_FOUND",
            f"District {config.district!r} was not found. Sample district names: {sampled}",
        )
    if not selected_info.get("selected_geometry_area_m2"):
        return _fail(report, "EMPTY_AOI", "Selected district geometry is empty.")

    image_info = live_probe.probe_images(config.year, config.month)
    report["checks"]["sentinel2"] = image_info
    report["image_count_before_cloud_filter"] = image_info.get("s2_image_count")
    report["image_count_after_cloud_filter"] = image_info.get("s2_cloud_filtered_image_count")
    report["band_names"] = image_info.get("monthly_ndvi_band_names") or []
    report["mean_ndvi_probe"] = (image_info.get("sanity_stat") or {}).get("NDVI")
    if int(image_info.get("s2_image_count") or 0) == 0:
        category = "EMPTY_S2_COLLECTION" if config.landcover_dataset_id else "EMPTY_IMAGE_COLLECTION"
        return _fail(
            report,
            category,
            "Sentinel-2 SR Harmonized has zero images for this month and AOI before cloud filtering.",
        )
    if int(image_info.get("s2_cloud_filtered_image_count") or 0) == 0:
        return _fail(
            report,
            "EMPTY_FILTERED_COLLECTION",
            "Sentinel-2 SR Harmonized has zero images after cloud metadata filtering.",
        )
    first_bands = set(image_info.get("first_image_band_names_after_ndvi") or [])
    ndvi_bands = set(image_info.get("monthly_ndvi_band_names") or [])
    if "NDVI" not in first_bands or "NDVI" not in ndvi_bands:
        return _fail(report, "NO_NDVI_BAND", "NDVI band is absent after mapping add_ndvi.")
    if report["mean_ndvi_probe"] is None:
        return _fail(report, "NULL_NDVI_STAT", "NDVI sanity reducer returned no mean value.")

    landcover_dataset = config.landcover_dataset_id
    if config.landcover == "dynamic-world" and landcover_dataset is None:
        landcover_dataset = DEFAULT_LANDCOVER_DATASET_ID
    if landcover_dataset:
        if not hasattr(live_probe, "probe_landcover"):
            return _fail(report, "VALIDATION_ERROR", "The configured preflight probe cannot inspect land-cover data.")
        landcover_info = live_probe.probe_landcover(config.year, config.month)
        report["checks"]["landcover"] = landcover_info
        report["landcover_dataset_id"] = landcover_info.get("landcover_dataset_id") or landcover_dataset
        report["landcover_strategy"] = landcover_info.get("landcover_strategy") or config.landcover_strategy
        report["dynamic_world_probability_threshold"] = landcover_info.get(
            "dynamic_world_probability_threshold",
            config.dynamic_world_probability_threshold,
        )
        report["dynamic_world_image_count"] = landcover_info.get("dynamic_world_image_count")
        report["landcover_diagnostics"] = landcover_info
        if int(landcover_info.get("dynamic_world_image_count") or 0) == 0:
            return _fail(
                report,
                "EMPTY_DYNAMIC_WORLD_COLLECTION",
                "Dynamic World has zero images for this month and AOI.",
            )
        if not landcover_info.get("has_label_band"):
            return _fail(report, "NO_LANDCOVER_LABEL", "Dynamic World label band is absent.")
        missing_probability_bands = list(landcover_info.get("missing_probability_bands") or [])
        if missing_probability_bands:
            return _fail(
                report,
                "NO_PROBABILITY_BANDS",
                "Dynamic World probability bands are missing: " + ", ".join(missing_probability_bands),
            )
        fractions = landcover_info.get("class_fractions") or {}
        core_fraction_values = [
            fractions.get("water"),
            fractions.get("built"),
            fractions.get("vegetation"),
            fractions.get("trees"),
            fractions.get("grass"),
        ]
        if not any(value is not None for value in core_fraction_values):
            return _fail(
                report,
                "CLASS_MASK_EMPTY",
                "Dynamic World class fractions were all null for water/built/vegetation probes.",
            )
        report["warnings"].extend(landcover_info.get("warnings") or [])
        probes = landcover_info.get("ndvi_probes") or {}
        if probes.get("non_water_mean_ndvi") is None:
            report["warnings"].append("Non-water NDVI probe is null; check water mask or valid-pixel overlap.")
        if probes.get("vegetation_mean_ndvi") is None:
            report["warnings"].append("Vegetation NDVI probe is null; vegetation may be sparse or low-confidence.")

    report["ok"] = True
    report["decision"] = "allow_export"
    report["expected_export_rows"] = 1
    return report
