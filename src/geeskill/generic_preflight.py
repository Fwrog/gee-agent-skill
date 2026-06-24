from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .earthengine import initialize
from .errors import classify_exception, error_payload


@dataclass(frozen=True)
class GenericV03PreflightConfig:
    project: str | None
    schema_version: str | None
    plan_id: str | None
    profile: str
    template: str
    dataset_id: str
    date_start: str
    date_end: str
    aoi_asset: str
    aoi_name: str | None = None
    scale: int = 30
    crs: str = "EPSG:4326"
    max_pixels: int = 10000000000000
    required_bands: tuple[str, ...] = ()
    qa_bands: tuple[str, ...] = ()
    index_name: str | None = None
    index_bands: tuple[str, ...] = ()
    cloud_property: str | None = None
    cloudy_pixel_percentage: int | None = None
    before_start: str | None = None
    before_end: str | None = None
    after_start: str | None = None
    after_end: str | None = None
    polarization: str | None = None
    orbit_pass: str | None = None
    export_description: str | None = None
    drive_folder: str | None = None
    file_prefix: str | None = None
    output_format: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


PLACEHOLDER_MARKERS = (
    "<",
    ">",
    "your-project",
    "supplied_aoi",
    "reviewed_aoi",
    "example",
)


def is_placeholder_asset(value: str | None) -> bool:
    if not value:
        return True
    lower = value.lower()
    return any(marker in lower for marker in PLACEHOLDER_MARKERS)


def _fail(config: GenericV03PreflightConfig, category: str, message: str, checks: dict[str, Any]) -> dict[str, Any]:
    critical = error_payload(category, message)
    return {
        **_base_report(config),
        "ok": False,
        "decision": "block_export",
        "critical_error": critical,
        "errors": [critical],
        "warnings": [],
        "checks": checks,
    }


def _base_report(config: GenericV03PreflightConfig) -> dict[str, Any]:
    return {
        "schema_version": config.schema_version,
        "plan_id": config.plan_id,
        "profile": config.profile,
        "template": config.template,
        "project": config.project,
        "aoi_name": config.aoi_name,
        "aoi_asset": config.aoi_asset,
        "dataset_id": config.dataset_id,
        "date_start": config.date_start,
        "date_end": config.date_end,
        "scale": config.scale,
        "crs": config.crs,
        "max_pixels": config.max_pixels,
        "export_description": config.export_description,
        "drive_folder": config.drive_folder,
        "file_prefix": config.file_prefix,
        "output_format": config.output_format,
    }


def _band_check(available: list[str], required: tuple[str, ...], category: str) -> tuple[bool, dict[str, Any] | None]:
    missing = [band for band in required if band not in available]
    if missing:
        return False, error_payload(category, f"Missing required bands: {', '.join(missing)}.")
    return True, None


def _collection_count(collection: Any) -> int:
    return int(collection.size().getInfo())


def _band_names(image: Any) -> list[str]:
    return [str(item) for item in image.bandNames().getInfo()]


def _aoi_checks(ee: Any, config: GenericV03PreflightConfig) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    aoi_fc = ee.FeatureCollection(config.aoi_asset)
    count = int(aoi_fc.size().getInfo())
    area_m2 = float(aoi_fc.geometry().area(1).getInfo()) if count > 0 else 0.0
    pixel_estimate = area_m2 / float(config.scale * config.scale) if config.scale > 0 else None
    check = {
        "ok": count > 0 and area_m2 > 0,
        "asset": config.aoi_asset,
        "feature_count": count,
        "area_m2": area_m2,
        "estimated_pixels_at_scale": pixel_estimate,
    }
    errors: list[dict[str, Any]] = []
    if count <= 0 or area_m2 <= 0:
        errors.append(error_payload("EMPTY_AOI", "AOI asset returned no usable features or area."))
    if pixel_estimate is not None and pixel_estimate > config.max_pixels:
        check["ok"] = False
        errors.append(
            error_payload(
                "REDUCER_SCALE_ERROR",
                f"Estimated pixel count {pixel_estimate:.0f} exceeds maxPixels {config.max_pixels}.",
            )
        )
    return aoi_fc.geometry(), check, errors


def _collection_for_profile(ee: Any, config: GenericV03PreflightConfig, aoi: Any) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    if config.profile == "sentinel1_change":
        return _sentinel1_collection_checks(ee, config, aoi)

    collection = ee.ImageCollection(config.dataset_id).filterDate(config.date_start, config.date_end).filterBounds(aoi)
    count_before = _collection_count(collection)
    filtered = collection
    if config.cloud_property and config.cloudy_pixel_percentage is not None:
        filtered = collection.filter(ee.Filter.lt(config.cloud_property, int(config.cloudy_pixel_percentage)))
    count_after = _collection_count(filtered)
    check = {
        "ok": count_before > 0 and count_after > 0,
        "count_before_filter": count_before,
        "count_after_filter": count_after,
        "cloud_property": config.cloud_property,
        "cloudy_pixel_percentage": config.cloudy_pixel_percentage,
    }
    errors: list[dict[str, Any]] = []
    if count_before <= 0:
        errors.append(error_payload("EMPTY_IMAGE_COLLECTION", "Image collection is empty for the requested AOI/date range."))
    elif count_after <= 0:
        errors.append(error_payload("EMPTY_FILTERED_COLLECTION", "No images remain after preflight metadata filters."))
    return filtered, check, errors


def _sentinel1_collection_checks(ee: Any, config: GenericV03PreflightConfig, aoi: Any) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    def build(start: str | None, end: str | None):
        collection = ee.ImageCollection(config.dataset_id).filterDate(start, end).filterBounds(aoi)
        collection = collection.filter(ee.Filter.eq("instrumentMode", "IW"))
        if config.polarization:
            collection = collection.filter(ee.Filter.listContains("transmitterReceiverPolarisation", config.polarization))
        if config.orbit_pass:
            collection = collection.filter(ee.Filter.eq("orbitProperties_pass", config.orbit_pass))
        return collection

    before = build(config.before_start, config.before_end)
    after = build(config.after_start, config.after_end)
    before_count = _collection_count(before)
    after_count = _collection_count(after)
    check = {
        "ok": before_count > 0 and after_count > 0,
        "before_count": before_count,
        "after_count": after_count,
        "polarization": config.polarization,
        "orbit_pass": config.orbit_pass,
    }
    errors: list[dict[str, Any]] = []
    if before_count <= 0:
        errors.append(error_payload("EMPTY_COLLECTION", "Sentinel-1 before-window collection is empty."))
    if after_count <= 0:
        errors.append(error_payload("EMPTY_COLLECTION", "Sentinel-1 after-window collection is empty."))
    return before, check, errors


def _safe_sanity_stat(ee: Any, config: GenericV03PreflightConfig, collection: Any, aoi: Any) -> dict[str, Any]:
    if config.profile == "optical_index" and config.index_bands and config.index_name:
        image = collection.median().normalizedDifference(list(config.index_bands)).rename(config.index_name)
        return image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=max(int(config.scale), 100),
            crs=config.crs,
            bestEffort=True,
            maxPixels=min(int(config.max_pixels), 100000000),
        ).getInfo()
    if config.profile == "landsat_lst":
        image = collection.median().select("ST_B10").multiply(0.00341802).add(149.0).subtract(273.15).rename("LST_C")
        return image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=max(int(config.scale), 120),
            crs=config.crs,
            bestEffort=True,
            maxPixels=min(int(config.max_pixels), 100000000),
        ).getInfo()
    return {}


def run_generic_v03_preflight(config: GenericV03PreflightConfig) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "template_adapter": {"ok": True, "template": config.template, "profile": config.profile},
        "export_metadata": {
            "ok": bool(config.export_description and config.drive_folder and config.file_prefix),
            "description": config.export_description,
            "drive_folder": config.drive_folder,
            "file_prefix": config.file_prefix,
            "output_format": config.output_format,
        },
    }
    if not checks["export_metadata"]["ok"]:
        return _fail(config, "NO_EXPORT_TARGET", "Export metadata is incomplete.", checks)
    if is_placeholder_asset(config.aoi_asset):
        return _fail(config, "V03_CONTEXT_REVIEW_REQUIRED", "AOI asset is missing or still contains a placeholder.", checks)

    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    try:
        ee = initialize(project=config.project, authenticate=False)
        aoi, checks["aoi"], aoi_errors = _aoi_checks(ee, config)
        errors.extend(aoi_errors)
        collection, checks["collection"], collection_errors = _collection_for_profile(ee, config, aoi)
        errors.extend(collection_errors)
        first_band_names: list[str] = []
        if checks["collection"]["ok"]:
            first_band_names = _band_names(ee.Image(collection.first()))
        band_ok, band_error = _band_check(first_band_names, config.required_bands, "NO_REQUIRED_BAND")
        qa_ok, qa_error = _band_check(first_band_names, config.qa_bands, "NO_QA_BAND")
        checks["bands"] = {
            "ok": band_ok and qa_ok,
            "available": first_band_names,
            "required": list(config.required_bands),
            "qa": list(config.qa_bands),
        }
        if band_error:
            errors.append(band_error)
        if qa_error:
            errors.append(qa_error)
        if not errors:
            try:
                sanity_stat = _safe_sanity_stat(ee, config, collection, aoi)
            except Exception as exc:  # pragma: no cover - depends on EE backend behavior
                warnings.append(classify_exception(exc).to_dict())
                sanity_stat = {}
            checks["sanity_stat"] = {"ok": True, "value": sanity_stat}
    except Exception as exc:
        errors.append(classify_exception(exc).to_dict())

    ok = not errors
    return {
        **_base_report(config),
        "ok": ok,
        "decision": "allow_export" if ok else "block_export",
        "critical_error": errors[0] if errors else None,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
