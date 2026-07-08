# Copyright And License Review

Date: 2026-07-09

Finding: pass.

The repository stores source metadata, URLs, structured facts, short paraphrases, limitations, and citations. It does not copy long paper passages, full documentation pages, or third-party repository code into KG-RAG assets.

Policy checks:

- Official Google/Earth Engine sources are Tier A and accepted for factual grounding.
- Research papers are Tier B candidates or context evidence for methodology and benchmark framing, not current dataset/API facts.
- Community repositories are limited to distilled patterns unless license and need are explicitly reviewed.
- Every source registry entry has `allowed_use`.
- Evidence cards include allowed use and claim boundaries.

Residual risk: benchmark or community repositories with unclear license should remain metadata-only until reviewed.
