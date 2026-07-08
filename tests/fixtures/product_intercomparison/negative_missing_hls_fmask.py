import ee

CLAIM_BOUNDARY = "product-level consistency; not in-situ ground-truth accuracy"
HLS = "NASA/HLS/HLSL30/v002"
MODIS = "MODIS/061/MOD13Q1"


def main():
    hls = ee.ImageCollection(HLS).select("B5").mean()
    modis = ee.ImageCollection(MODIS).select("SummaryQA").mean()
    modis_ndvi = ee.ImageCollection(MODIS).select("NDVI").mean().multiply(0.0001)
    return hls.reduceResolution(reducer=ee.Reducer.mean()).reproject(modis_ndvi.projection()).subtract(modis_ndvi)
