from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class DatasetCard:
    dataset_id: str
    title: str
    provider: str
    gee_url: str
    temporal_coverage: str
    spatial_resolution: str
    bands: tuple[str, ...]
    qa_bands: tuple[str, ...]
    common_uses: tuple[str, ...]
    recommended_tasks: tuple[str, ...]
    known_limitations: tuple[str, ...]
    scale_notes: str
    projection_notes: str
    license_attribution: str
    last_checked: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "title": self.title,
            "provider": self.provider,
            "gee_url": self.gee_url,
            "temporal_coverage": self.temporal_coverage,
            "spatial_resolution": self.spatial_resolution,
            "bands": list(self.bands),
            "qa_bands": list(self.qa_bands),
            "common_uses": list(self.common_uses),
            "recommended_tasks": list(self.recommended_tasks),
            "known_limitations": list(self.known_limitations),
            "scale_notes": self.scale_notes,
            "projection_notes": self.projection_notes,
            "license_attribution": self.license_attribution,
            "last_checked": self.last_checked,
        }


DATASETS: tuple[DatasetCard, ...] = (
    DatasetCard(
        dataset_id="COPERNICUS/S2_SR_HARMONIZED",
        title="Sentinel-2 MSI Surface Reflectance Harmonized",
        provider="Copernicus / ESA",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
        temporal_coverage="2017-present; check catalog for current ingestion status",
        spatial_resolution="10m, 20m, and 60m bands",
        bands=("B2", "B3", "B4", "B8", "B11", "B12", "SCL"),
        qa_bands=("SCL", "QA60"),
        common_uses=("vegetation indices", "water indices", "built-up indices", "zonal statistics"),
        recommended_tasks=("vegetation_index", "water_index", "builtup_index", "zonal_statistics", "export_image"),
        known_limitations=(
            "Cloud and shadow masking are mandatory for optical analysis.",
            "Band resolutions differ; reducers and exports need explicit scale.",
        ),
        scale_notes="Use 10m for B2/B3/B4/B8 index products unless the recipe requires coarser scale.",
        projection_notes="Set explicit CRS/scale when comparing regions or exporting rasters.",
        license_attribution="Copernicus Sentinel data terms apply.",
        last_checked="2026-06-21",
    ),
    DatasetCard(
        dataset_id="LANDSAT/LC08/C02/T1_L2",
        title="Landsat 8 Collection 2 Tier 1 Level 2",
        provider="USGS / NASA",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2",
        temporal_coverage="2013-present; check catalog for current ingestion status",
        spatial_resolution="30m optical and thermal-derived products",
        bands=("SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10"),
        qa_bands=("QA_PIXEL", "QA_RADSAT"),
        common_uses=("land surface temperature", "vegetation indices", "change detection"),
        recommended_tasks=("land_surface_temperature", "vegetation_index", "change_detection"),
        known_limitations=("Surface temperature requires scale/offset conversion.", "QA_PIXEL masking is required."),
        scale_notes="Use 30m for Collection 2 Level 2 products.",
        projection_notes="Use explicit projection or scale in reducers and exports.",
        license_attribution="USGS Landsat data policy applies.",
        last_checked="2026-06-21",
    ),
    DatasetCard(
        dataset_id="LANDSAT/LC09/C02/T1_L2",
        title="Landsat 9 Collection 2 Tier 1 Level 2",
        provider="USGS / NASA",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2",
        temporal_coverage="2021-present; check catalog for current ingestion status",
        spatial_resolution="30m optical and thermal-derived products",
        bands=("SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10"),
        qa_bands=("QA_PIXEL", "QA_RADSAT"),
        common_uses=("land surface temperature", "vegetation indices", "change detection"),
        recommended_tasks=("land_surface_temperature", "vegetation_index", "change_detection"),
        known_limitations=("Use consistent scaling with Landsat 8 when merging sensors.",),
        scale_notes="Use 30m for Collection 2 Level 2 products.",
        projection_notes="Use explicit projection or scale in reducers and exports.",
        license_attribution="USGS Landsat data policy applies.",
        last_checked="2026-06-23",
    ),
    DatasetCard(
        dataset_id="COPERNICUS/S1_GRD",
        title="Sentinel-1 SAR GRD",
        provider="Copernicus / ESA",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD",
        temporal_coverage="2014-present; check catalog for current ingestion status",
        spatial_resolution="10m, 25m, or 40m depending on mode/product",
        bands=("VV", "VH", "HH", "HV", "angle"),
        qa_bands=(),
        common_uses=("flood mapping", "before/after change detection", "water extent"),
        recommended_tasks=("flood_mapping", "change_detection"),
        known_limitations=("Speckle, orbit direction, polarization, and incidence angle affect interpretation.",),
        scale_notes="Use recipe-specific scale and filter by instrumentMode/polarization.",
        projection_notes="Compare before/after images with matched filters and consistent reducer scale.",
        license_attribution="Copernicus Sentinel data terms apply.",
        last_checked="2026-06-21",
    ),
    DatasetCard(
        dataset_id="GOOGLE/DYNAMICWORLD/V1",
        title="Dynamic World V1",
        provider="Google / World Resources Institute",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1",
        temporal_coverage="2015-present; check catalog for current ingestion status",
        spatial_resolution="10m",
        bands=("label", "water", "trees", "grass", "flooded_vegetation", "crops", "shrub_and_scrub", "built", "bare", "snow_and_ice"),
        qa_bands=(),
        common_uses=("land-cover summary", "land-cover-stratified statistics", "interpretation diagnostics"),
        recommended_tasks=("landcover_summary", "landcover_stratified_statistics"),
        known_limitations=("Probabilistic classes need confidence thresholds and null-tolerant outputs.",),
        scale_notes="Use 10m with class probability thresholds documented in output metadata.",
        projection_notes="Use as masks/strata, not as an administrative boundary.",
        license_attribution="Dynamic World terms apply.",
        last_checked="2026-06-21",
    ),
    DatasetCard(
        dataset_id="ESA/WorldCover/v200",
        title="ESA WorldCover 10m v200",
        provider="ESA",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200",
        temporal_coverage="2021 static product",
        spatial_resolution="10m",
        bands=("Map",),
        qa_bands=(),
        common_uses=("static land-cover reference", "sanity-check land-cover masks"),
        recommended_tasks=("landcover_summary", "landcover_stratified_statistics"),
        known_limitations=("Static 2021 map is not time-matched to arbitrary analysis windows.",),
        scale_notes="Use 10m for class summaries unless coarsening for large AOIs.",
        projection_notes="Document when using static land cover with non-2021 imagery.",
        license_attribution="ESA WorldCover license terms apply.",
        last_checked="2026-06-21",
    ),
    DatasetCard(
        dataset_id="MODIS/061/MOD11A2",
        title="MOD11A2.061 Terra Land Surface Temperature and Emissivity 8-Day Global 1km",
        provider="NASA LP DAAC / USGS EROS Center",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A2",
        temporal_coverage="2000-02-18-present; 8-day cadence",
        spatial_resolution="1000m",
        bands=("LST_Day_1km", "LST_Night_1km", "QC_Day", "QC_Night", "Emis_31", "Emis_32"),
        qa_bands=("QC_Day", "QC_Night", "Clear_sky_days", "Clear_sky_nights"),
        common_uses=("land surface temperature", "thermal climatology", "regional heat diagnostics"),
        recommended_tasks=("land_surface_temperature", "zonal_statistics", "export_image"),
        known_limitations=(
            "LST bands require scale factor conversion.",
            "The 8-day product averages daily inputs and does not filter by specific QA bits before averaging.",
        ),
        scale_notes="Use 1000m unless intentionally resampling or aggregating.",
        projection_notes="Document coarse MODIS resolution when combining with Sentinel or Landsat products.",
        license_attribution="NASA LP DAAC / USGS MODIS data terms apply.",
        last_checked="2026-06-24",
    ),
    DatasetCard(
        dataset_id="ECMWF/ERA5_LAND/DAILY_AGGR",
        title="ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis",
        provider="ECMWF / Copernicus Climate Data Store",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_DAILY_AGGR",
        temporal_coverage="1950-present with near-real-time lag; check catalog availability",
        spatial_resolution="11132m",
        bands=("temperature_2m", "total_precipitation_sum", "surface_pressure", "u_component_of_wind_10m", "v_component_of_wind_10m"),
        qa_bands=(),
        common_uses=("climate covariates", "temperature and precipitation summaries", "hydrometeorological context"),
        recommended_tasks=("zonal_statistics", "change_detection", "export_table", "export_image"),
        known_limitations=(
            "Coarse reanalysis pixels are not a substitute for local station observations.",
            "Some evaporation variables have known swapped-value issues in the source data.",
            "Some precipitation and flow aggregates can contain small negative or excessive values.",
        ),
        scale_notes="Use coarse regional scales near 11132m; avoid mixing with 10m optical outputs without aggregation.",
        projection_notes="Document reanalysis grid assumptions and aggregation windows.",
        license_attribution="ECMWF/Copernicus attribution and citation requirements apply.",
        last_checked="2026-06-24",
    ),
    DatasetCard(
        dataset_id="JRC/GSW1_4/GlobalSurfaceWater",
        title="JRC Global Surface Water Mapping Layers v1.4",
        provider="EC JRC / Google",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater",
        temporal_coverage="1984-03-16 to 2022-01-01 static mapping layers",
        spatial_resolution="30m",
        bands=("occurrence", "change_abs", "change_norm", "seasonality", "recurrence", "transition", "max_extent"),
        qa_bands=("max_extent",),
        common_uses=("surface water occurrence", "water change context", "water masks"),
        recommended_tasks=("water_index", "change_detection", "flood_mapping", "zonal_statistics"),
        known_limitations=(
            "Historical mapping layers are not time-matched to arbitrary current flood windows.",
            "The occurrence band mask can mirror partial occurrence values and needs careful interpretation.",
        ),
        scale_notes="Use 30m for summaries unless coarsening for large regions.",
        projection_notes="Use as reference/context; document when combining with current Sentinel observations.",
        license_attribution="Copernicus Programme attribution required; cite EC JRC/Google where used.",
        last_checked="2026-06-24",
    ),
    DatasetCard(
        dataset_id="USGS/SRTMGL1_003",
        title="NASA SRTM Digital Elevation 30m",
        provider="NASA / USGS / JPL-Caltech",
        gee_url="https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003",
        temporal_coverage="2000-02-11 to 2000-02-22 static DEM",
        spatial_resolution="30m",
        bands=("elevation",),
        qa_bands=(),
        common_uses=("terrain covariates", "slope", "elevation masks", "topographic context"),
        recommended_tasks=("zonal_statistics", "export_image", "change_detection"),
        known_limitations=("Static terrain layer; not a time-varying surface observation.",),
        scale_notes="Use 30m for terrain-derived products such as slope unless intentionally aggregating.",
        projection_notes="Use explicit scale when reducing or exporting terrain covariates.",
        license_attribution="NASA/JPL SRTM citation and use terms apply.",
        last_checked="2026-06-24",
    ),
)


def list_datasets() -> list[dict[str, Any]]:
    return [card.to_dict() for card in DATASETS]


def get_dataset(dataset_id: str) -> dict[str, Any] | None:
    normalized = dataset_id.lower()
    for card in DATASETS:
        if card.dataset_id.lower() == normalized:
            return card.to_dict()
    return None


def search_datasets(query: str, top_k: int = 10) -> list[dict[str, Any]]:
    terms = [item for item in query.lower().replace("/", " ").replace("_", " ").split() if item]
    expanded_terms = list(terms)
    aliases = {
        "ndvi": ["vegetation", "indices"],
        "evi": ["vegetation", "indices"],
        "ndwi": ["water", "indices"],
        "mndwi": ["water", "indices"],
        "ndbi": ["built", "up", "indices"],
        "geotiff": ["export", "image"],
        "lst": ["land", "surface", "temperature"],
    }
    for term in terms:
        expanded_terms.extend(aliases.get(term, []))
    scored: list[tuple[int, DatasetCard]] = []
    for card in DATASETS:
        haystack = " ".join(
            [
                card.dataset_id,
                card.title,
                card.provider,
                " ".join(card.bands),
                " ".join(card.common_uses),
                " ".join(card.recommended_tasks),
            ]
        ).lower()
        score = sum(1 for term in expanded_terms if term in haystack)
        if score:
            scored.append((score, card))
    scored.sort(key=lambda item: (-item[0], item[1].dataset_id))
    return [card.to_dict() for _, card in scored[:top_k]]


def recommend_datasets(task_type: str | None = None, metric: str | None = None) -> list[dict[str, Any]]:
    task = (task_type or "").lower()
    metric_name = (metric or "").lower()
    recommendations: list[DatasetCard] = []
    for card in DATASETS:
        if task and task in card.recommended_tasks:
            recommendations.append(card)
            continue
        if metric_name and metric_name in " ".join((*card.common_uses, *card.bands)).lower():
            recommendations.append(card)
    if not recommendations and metric_name in {"ndvi", "evi", "ndwi", "mndwi", "ndbi"}:
        recommendations.append(DATASETS[0])
    if not recommendations and metric_name == "lst":
        recommendations.extend([card for card in DATASETS if card.dataset_id.startswith("LANDSAT/")])
    return [card.to_dict() for card in recommendations]


KNOWLEDGE_CARD_PREFIXES: dict[str, tuple[str, ...]] = {
    "datasets": ("datasets/",),
    "operators": ("operators/", "operator-chains/", "core/", "cloud-masking.md", "reducers-zonal-statistics.md"),
    "recipes": ("recipes/",),
    "failures": ("failure-cases/",),
    "research": ("research/", "corpus/"),
}


def _card_category(source_path: str) -> str:
    for category, prefixes in KNOWLEDGE_CARD_PREFIXES.items():
        if any(source_path == prefix or source_path.startswith(prefix) for prefix in prefixes):
            return category
    return "general"


KNOWN_FAILURE_RE = re.compile(r"^known_failure:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def _add_known_failure(entry: dict[str, Any], value: str) -> None:
    for item in (part.strip() for part in value.split(",")):
        if item and item not in entry["known_failures"]:
            entry["known_failures"].append(item)


def list_knowledge_cards(index: dict[str, Any], category: str = "all", top_k: int = 50) -> list[dict[str, Any]]:
    """Return one structured entry per indexed knowledge-base source file."""
    if category not in {"all", *KNOWLEDGE_CARD_PREFIXES.keys(), "general"}:
        raise ValueError(
            "Unsupported knowledge category. Use one of: all, datasets, operators, recipes, failures, research, general."
        )
    grouped: dict[str, dict[str, Any]] = {}
    for doc in index.get("documents", []):
        source_path = str(doc.get("source_path") or "")
        if not source_path:
            continue
        card_category = _card_category(source_path)
        if category != "all" and category != card_category:
            continue
        metadata = dict(doc.get("metadata") or {})
        entry = grouped.setdefault(
            source_path,
            {
                "source_path": source_path,
                "category": card_category,
                "title": doc.get("title") or source_path,
                "source_id": metadata.get("source_id"),
                "source_type": metadata.get("source_type"),
                "primary_status": metadata.get("primary_status"),
                "risk_level": metadata.get("risk_level"),
                "last_checked": metadata.get("last_checked") or metadata.get("retrieved_at"),
                "source_url": metadata.get("source_url"),
                "known_failures": [],
                "chunk_count": 0,
            },
        )
        entry["chunk_count"] += 1
        for key, value in metadata.items():
            if key == "known_failure" or key.endswith("_known_failure"):
                _add_known_failure(entry, value)
        for value in KNOWN_FAILURE_RE.findall(str(doc.get("text") or "")):
            _add_known_failure(entry, value)
        for key in ("source_id", "source_type", "primary_status", "risk_level", "source_url"):
            if not entry.get(key) and metadata.get(key):
                entry[key] = metadata[key]
    return sorted(grouped.values(), key=lambda item: (item["category"], item["source_path"]))[:top_k]
