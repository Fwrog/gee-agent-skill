#!/usr/bin/env python3
"""Create figures for the Hong Kong v0.3 NDVI product intercomparison."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else float("nan")


def make_figures(input_dir: Path, out_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    input_dir = input_dir.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    window_rows = _read_csv(input_dir / "window_metrics.csv")
    regional_rows = _read_csv(input_dir / "regional_timeseries.csv") or window_rows
    sample_rows = _read_csv(input_dir / "pixel_samples_clean.csv")
    class_rows = _read_csv(input_dir / "summary_metrics_by_landcover.csv")

    if regional_rows:
        dates = [row["date_start"] for row in regional_rows]
        hls = [_float(row, "mean_hls_ndvi") for row in regional_rows]
        modis = [_float(row, "mean_modis_ndvi") for row in regional_rows]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(dates, hls, marker="o", label="HLS aggregated to MODIS grid")
        ax.plot(dates, modis, marker="s", label="MODIS MOD13Q1")
        ax.set_ylabel("Regional mean NDVI")
        ax.set_xlabel("MODIS 16-day window")
        ax.set_title("Hong Kong 2024 NDVI product intercomparison")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        path = out_dir / "hk_v03_regional_ndvi_timeseries.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        written.append(path)

    xs = [_float(row, "modis_ndvi") for row in sample_rows]
    ys = [_float(row, "hls_ndvi_agg250") for row in sample_rows]
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    hb = ax.hexbin(xs, ys, gridsize=45, mincnt=1, cmap="viridis")
    ax.plot([-0.2, 1.0], [-0.2, 1.0], color="black", linewidth=1, linestyle="--")
    ax.set_xlim(-0.2, 1.0)
    ax.set_ylim(-0.2, 1.0)
    ax.set_xlabel("MODIS MOD13Q1 NDVI")
    ax.set_ylabel("HLS NDVI aggregated to 250 m")
    ax.set_title("Matched-pixel product agreement")
    fig.colorbar(hb, ax=ax, label="Matched pixel count")
    fig.tight_layout()
    path = out_dir / "hk_v03_hls_vs_modis_hexbin.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    lons = [_float(row, "lon") for row in sample_rows]
    lats = [_float(row, "lat") for row in sample_rows]
    diffs = [_float(row, "diff") for row in sample_rows]
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    sc = ax.scatter(lons, lats, c=diffs, s=8, cmap="RdBu", vmin=-0.3, vmax=0.3, linewidths=0)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Spatial sample:\nHLS aggregated NDVI - MODIS NDVI", fontsize=11)
    ax.set_aspect("equal", adjustable="box")
    fig.colorbar(sc, ax=ax, label="NDVI difference")
    fig.tight_layout()
    path = out_dir / "hk_v03_spatial_difference_samples.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    labels = [row["group"] for row in class_rows]
    mae = [_float(row, "mae") for row in class_rows]
    rmse = [_float(row, "rmse") for row in class_rows]
    bias = [_float(row, "bias_hls_minus_modis") for row in class_rows]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    positions = range(len(labels))
    width = 0.25
    ax.bar([p - width for p in positions], mae, width=width, label="MAE")
    ax.bar(list(positions), rmse, width=width, label="RMSE")
    ax.bar([p + width for p in positions], bias, width=width, label="Bias")
    ax.set_xticks(list(positions), labels, rotation=25, ha="right")
    ax.set_ylabel("NDVI difference metric")
    ax.set_title("Agreement metrics by land-cover group")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend()
    fig.tight_layout()
    path = out_dir / "hk_v03_landcover_metrics.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    written.append(path)

    if window_rows:
        valid = [_float(row, "valid_fraction") for row in window_rows]
        fig, ax = plt.subplots(figsize=(8, 3.8))
        ax.bar(dates, valid, color="#2563eb")
        finite_valid = [value for value in valid if value == value]
        ymax = max(finite_valid) if finite_valid else 1
        ax.set_ylim(0, min(1, max(0.05, ymax * 1.35)))
        ax.set_ylabel("Valid matched fraction")
        ax.set_xlabel("MODIS 16-day window")
        ax.set_title("Matched valid-pixel fraction by window")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        path = out_dir / "hk_v03_valid_fraction_by_window.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        written.append(path)

    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="outputs/hk_ndvi_product_validation_v03/analysis")
    parser.add_argument("--out", default="outputs/hk_ndvi_product_validation_v03/figures")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    written = make_figures(Path(args.input), Path(args.out))
    if args.json:
        import json

        print(json.dumps({"ok": True, "figures": [str(path) for path in written]}, indent=2))
    else:
        for path in written:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
