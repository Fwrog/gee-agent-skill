from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


SLUG_OVERRIDES = {
    "COPERNICUS/S2_SR_HARMONIZED": "sentinel-2-sr-harmonized",
    "LANDSAT/LC08/C02/T1_L2": "landsat-lc08-c2-l2",
    "LANDSAT/LC09/C02/T1_L2": "landsat-lc09-c2-l2",
    "COPERNICUS/S1_GRD": "sentinel-1-grd",
    "GOOGLE/DYNAMICWORLD/V1": "dynamic-world-v1",
    "ESA/WorldCover/v200": "esa-worldcover-v200",
    "MODIS/061/MOD11A2": "modis-mod11a2-lst",
    "ECMWF/ERA5_LAND/DAILY_AGGR": "era5-land-daily-aggr",
    "JRC/GSW1_4/GlobalSurfaceWater": "jrc-global-surface-water",
    "USGS/SRTMGL1_003": "srtm-gl1-003",
}


def _slug(dataset_id: str) -> str:
    if dataset_id in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[dataset_id]
    slug = re.sub(r"[^a-z0-9]+", "-", dataset_id.lower())
    return slug.strip("-")


def _csv(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- none"


def _card_markdown(card: dict) -> str:
    slug = _slug(card["dataset_id"])
    return f"""# Dataset Card: {card["title"]}

source_id: dataset-{slug}
source_type: official-dataset-card
primary_status: canonical
dataset_id: {card["dataset_id"]}
title: {card["title"]}
provider: {card["provider"]}
gee_url: {card["gee_url"]}
source_url: {card["gee_url"]}
temporal_coverage: {card["temporal_coverage"]}
spatial_resolution: {card["spatial_resolution"]}
bands: {_csv(card["bands"])}
qa_bands: {_csv(card["qa_bands"])}
common_uses: {_csv(card["common_uses"])}
recommended_tasks: {_csv(card["recommended_tasks"])}
scale_notes: {card["scale_notes"]}
projection_notes: {card["projection_notes"]}
license_attribution: {card["license_attribution"]}
last_checked: {card["last_checked"]}
risk_level: medium

## Use

Use `{card["dataset_id"]}` for {", ".join(card["common_uses"])}.

## Bands

Core bands: {_csv(card["bands"])}.

QA or mask bands: {_csv(card["qa_bands"])}.

## Recommended Tasks

{_bullets(card["recommended_tasks"])}

## Scale and Projection Notes

- {card["scale_notes"]}
- {card["projection_notes"]}

## Known Limitations

{_bullets(card["known_limitations"])}

## Attribution

{card["license_attribution"]}
"""


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()
    from geeskill.catalog import list_datasets

    parser = argparse.ArgumentParser(description="Generate RAG-visible dataset cards from the structured catalog.")
    parser.add_argument("--out-dir", default="references/knowledge_base/datasets")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for card in list_datasets():
        path = out_dir / f"{_slug(card['dataset_id'])}.md"
        path.write_text(_card_markdown(card), encoding="utf-8")
    print(f"wrote {len(list_datasets())} dataset cards -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
