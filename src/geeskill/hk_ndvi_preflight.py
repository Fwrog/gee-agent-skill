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
DEFAULT_BOUNDARY_NAME = "hk_18_districts.geojson"
DEFAULT_DISTRICT_PROPERTY = "District"


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


class HKNDVIProbe(Protocol):
    def initialize(self) -> None: ...

    def probe_district_source(self) -> dict[str, Any]: ...

    def select_district(self, district_name: str | None, district_names: list[str]) -> dict[str, Any]: ...

    def probe_images(self, year: int, month: int) -> dict[str, Any]: ...


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
        return _fail(
            report,
            "EMPTY_IMAGE_COLLECTION",
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

    report["ok"] = True
    report["decision"] = "allow_export"
    report["expected_export_rows"] = 1
    return report
