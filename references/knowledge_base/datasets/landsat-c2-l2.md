# Dataset Card: Landsat Collection 2 Level-2

source_id: dataset-landsat-c2-l2
source_type: official-data-catalog
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2
retrieved_at: 2026-06-21
primary_status: canonical
dataset_id: LANDSAT/LC08/C02/T1_L2
platform: Landsat
risk_level: low

## Use

Collection 2 Level-2 scenes include surface reflectance and, when available, surface temperature. Landsat 8 and 9 thermal LST workflows commonly use `ST_B10`.

The common Kelvin conversion for `ST_B10` is:

```python
lst_kelvin = image.select("ST_B10").multiply(0.00341802).add(149.0)
lst_celsius = lst_kelvin.subtract(273.15)
```

## Quality Mask

Use `QA_PIXEL` bit masks for fill, dilated cloud, cirrus, cloud, cloud shadow, and snow. Record the exact bits and dataset page used because QA definitions are dataset-specific.

