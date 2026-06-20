# Cloud Masking

source_id: gee-cloud-masking-notes
source_type: curated-best-practice
publisher: gee-agent-skill
url: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
retrieved_at: 2026-06-21
primary_status: derived-from-official-docs
risk_level: medium

## Sentinel-2

For `COPERNICUS/S2_SR_HARMONIZED`, do not rely blindly on old QA60-only recipes. The Data Catalog documents a QA60 discontinuity and reconstruction window. Prefer SCL masking for basic workflows, or document use of Cloud Probability or Cloud Score+ when stricter cloud screening is required.

Typical SCL masks exclude no data, saturated/defective pixels, cloud shadows, unclassified/cloud classes, cirrus, and snow/ice. Keep the mask method visible in plan and script constants.

## Landsat Collection 2 L2

Use `QA_PIXEL` bits to mask fill, dilated cloud, cirrus, cloud, cloud shadow, and snow when computing optical composites or land surface temperature. Surface temperature bands require scale and offset before Celsius conversion.

