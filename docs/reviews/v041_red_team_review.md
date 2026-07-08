# v0.4.1 Red-Team Review

Date: 2026-07-09

Adversarial cases covered:

- Invented or private dataset/asset requests should produce insufficient-evidence warnings or live-gate refusal.
- Blog, paper, or candidate benchmark sources must not override official catalog/API facts.
- Candidate arXiv evidence must not become accepted current-fact authority without review.
- HLS 30 m and MODIS 250 m direct pixel comparison is flagged by retrieval and semantic validation.
- Product intercomparison described as ground-truth validation fails semantic validation.
- Flood workflows should retrieve Sentinel-1 evidence before NDVI product-intercomparison evidence.
- NDVI/product-intercomparison workflows should not retrieve Sentinel-1 flood as primary evidence.
- Live exports still require `--project` and `--confirm-live`.

Blocking issues: none after v0.4.1 hardening.
