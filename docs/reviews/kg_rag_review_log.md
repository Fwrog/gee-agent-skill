# KG-RAG Review Log

Date: 2026-07-09

## source-scout

Reviewed official Earth Engine docs, Data Catalog, API reference, official GitHub repo, HLS/MODIS catalog pages, scale/projection/reduceResolution guidance, GEE-OPs, AutoGEEval, AutoGEEval++, Geo-FuB, Gorelick 2017, geemap JOSS, geemap, and Earth Engine notebooks. Official sources were accepted; research sources remain candidates unless separately curated.

## source-policy-review

Approved Tier A official sources for current API/dataset facts. Approved MIT-licensed community repos only for distilled patterns. Kept research papers and benchmark repos as candidate/metadata-only where licensing or claim review is incomplete.

## evidence-curator

Accepted evidence cards cite accepted sources and include trust tier, allowed use, last checked date, claim boundaries, validator hints, and private-content risk. Candidate research cards contain metadata/pattern framing only.

## ontology-architect

Created a lightweight local ontology covering sources, evidence cards, datasets, bands, QA fields, scale factors, operators, workflows, rules, failure cases, recovery patterns, claims, claim boundaries, scripts, tests, artifacts, and eval cases.

## kg-engineer

Implemented deterministic graph build, validation, search, neighbors, shortest path, topic explanation, and Mermaid export with no graph database dependency.

## hybrid-rag-engineer

Implemented hybrid retrieval over BM25 text, evidence cards, graph nodes/edges/paths, rules, failure cases, claim boundaries, planner hints, validator hints, and source-tier counts.

## cli-engineer

Added offline JSON commands for source validation, evidence card search, KG build/query/explain, and hybrid retrieval.

## planner-validator-engineer

Added semantic validator hooks for product intercomparison: MODIS scale factor, MODIS QA, HLS Fmask, fine/coarse aggregation, reduceResolution projection handling, claim boundary, and Golden evidence requirements.

## remote-sensing-review

Approved conservative framing: HLS/MODIS intercomparison supports product-level consistency only. It does not claim in-situ ground-truth accuracy. Scale, projection, QA, temporal matching, and mixed-pixel risks are explicit.

## software-architecture-review

Approved local JSON/YAML/Markdown architecture. No Neo4j, hosted vector database, LangChain, external LLM API, Earth Engine credentials, or live export is required for KG-RAG retrieval.

## privacy-security-review

New validators scan source registry, evidence cards, and graph nodes for private-looking paths, private asset ids, and secret-like strings. No private sources are intentionally added.

## copyright-license-review

The implementation stores metadata, source URLs, structured facts, short paraphrased summaries, limitations, and links only. No long paper excerpts or third-party code are copied.

## red-team-review

Adversarial cases are covered by retrieval/eval/validator behavior: invented dataset facts should defer to Tier A sources; direct fine/coarse comparison retrieves a failure case; unreviewed research remains candidate; live export remains behind existing confirmation gates.
