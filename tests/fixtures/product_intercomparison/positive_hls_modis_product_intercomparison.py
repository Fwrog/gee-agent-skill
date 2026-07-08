import ee

CLAIM_BOUNDARY = "product-level consistency; not in-situ ground-truth accuracy"
HLS = "NASA/HLS/HLSL30/v002"
MODIS = "MODIS/061/MOD13Q1"
CRS = "EPSG:4326"


def mask_hls(image):
    fmask = image.select("Fmask")
    return image.updateMask(fmask.eq(0))


def mask_modis(image):
    qa = image.select("SummaryQA")
    return image.updateMask(qa.lte(1))


def main():
    hls = ee.ImageCollection(HLS).map(mask_hls).select("B5").mean()
    modis = ee.ImageCollection(MODIS).map(mask_modis).select("NDVI").mean().multiply(0.0001)
    modis_projection = modis.projection()
    hls_aggregated = hls.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=1024).reproject(modis_projection)
    return hls_aggregated.subtract(modis).rename("product_consistency_delta").set("claim_boundary", CLAIM_BOUNDARY)
