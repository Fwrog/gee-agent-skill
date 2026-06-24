# Recipe Registry

The recipe registry maps natural-language task intent to datasets, templates, validation rules, preflight profiles, and output schemas. It is a harness contract, not a promise that every recipe has live export support.

The executable registry is file-backed:

- source-of-truth for readers: `references/recipes/registry.yaml`;
- packaged wheel fallback: `src/geeskill/resources/recipes/registry.yaml`;
- CLI surface: `gee-skill recipe list --json` and `gee-skill recipe show <recipe_id> --json`.

The Python module keeps a fallback registry only so broken local files do not make the package unusable during development.

## Readiness Levels

| Level | Meaning |
| --- | --- |
| Plan ready | The deterministic parser can produce a reviewable `gee-plan/v0.3`. |
| Render ready | A template can render a Python script that passes validation. |
| Mock preflight ready | Tests exercise preflight decisions without contacting Earth Engine. |
| Live preflight ready | The command can safely contact Earth Engine and block/allow export. |
| Live export verified | A user-confirmed export has been submitted and monitored. |

See [Capability matrix](capability_matrix.md) for current status by workflow.

## Registered Families

| Recipe | Task type | Current status |
| --- | --- | --- |
| `vegetation-index-ndvi` | `vegetation_index` | Plan/render/validate ready; HK golden examples are live verified. |
| `vegetation-index-evi` | `vegetation_index` | Plan/render/validate ready for Sentinel-2 CSV; live export not yet verified. |
| `water-index-ndwi` | `water_index` | Plan/render/validate ready for Sentinel-2 GeoTIFF; generic preflight gate exists; live export not yet verified. |
| `builtup-index-ndbi` | `builtup_index` | Plan/render/validate ready for Sentinel-2 CSV; generic preflight gate exists; live export not yet verified. |
| `landcover-stratified-ndvi` | `landcover_stratified_statistics` | Golden v0.2 path. |
| `landsat-lst` | `land_surface_temperature` | Plan/render/validate ready for Landsat LST CSV/image; generic preflight gate exists; live export not yet verified. |
| `sentinel1-flood-before-after` | `flood_mapping` | Plan/render/validate ready for Sentinel-1 before/after GeoTIFF; generic preflight gate exists; live export not yet verified. |
| `landcover-summary-dynamic-world` | `landcover_summary` | Plan/render/validate ready for Dynamic World area/fraction CSV; live export not yet verified. |
| `zonal-statistics-table` | `zonal_statistics` | Render/validation template exists. |
| `image-export-geotiff` | `export_image` | Validation rules for region, scale, CRS, and `maxPixels`. |
| `table-export-csv` | `export_table` | Validation rules for selectors and CSV export metadata. |

## Inspecting Recipes

```bash
gee-skill recipe list --json
gee-skill recipe show vegetation-index-ndvi --json
gee-skill catalog recommend --task-type water_index --metric NDWI --json
gee-skill catalog evidence --category recipes --json
```

## Adding A Recipe

A new recipe should define:

- recipe id and task type;
- required and optional inputs;
- candidate datasets and default dataset policy;
- template name or `null` when plan-only;
- preflight profile and validation profile;
- output schema and live risk level;
- examples and limitations.

Before documenting a recipe as live-ready, add parser tests, render/validation tests, mocked preflight tests, and an explicit opt-in live verification note.
