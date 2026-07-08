# Privacy And Security Review

Date: 2026-07-09

Finding: pass.

The v0.4 source registry, evidence cards, and KG files avoid private Drive paths, private Earth Engine asset ids, credentials, unpublished result values, private AOIs, and account identifiers. Validators scan public KG/evidence/source data for private-looking paths, asset ids, and secret-like tokens.

Reviewed safeguards:

- Source registry stores public URLs and metadata only.
- Evidence cards store short paraphrased facts, limitations, hints, and claim boundaries.
- KG validation rejects private-looking paths, asset ids, and common token patterns.
- Live Earth Engine behavior is unchanged and still requires explicit `--project` plus `--confirm-live`.

Residual risk: future evidence promotion must repeat the privacy scan before committing new cards.
