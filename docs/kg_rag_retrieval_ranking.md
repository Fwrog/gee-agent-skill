# v0.4.1 KG-RAG Retrieval Ranking

v0.4.1 keeps retrieval deterministic and offline. It does not add embeddings, LangChain, a hosted vector database, or an external LLM API.

## Evidence Card Ranking

Evidence search uses weighted lexical scoring:

1. exact `card_id` or title match;
2. title phrase match;
3. `canonical_terms` and `aliases`;
4. topics, applicable workflows, and applicable datasets;
5. extracted facts, patterns, and known failure modes;
6. planner/validator hints, limitations, and claim boundaries;
7. lower-weight source metadata.

Common Earth Engine phrases receive deterministic boosts: MODIS scale factor, HLS Fmask, fine/coarse comparison, product intercomparison, reduceResolution projection, ground-truth validation, and Sentinel-1 flood.

## Knowledge Graph Ranking

KG node search follows the same principle over node id, title, tags, description, and metadata. It remains stable by sorting ties by node id.

## Negative Routing

The ranking layer applies conservative penalties for known workflow contamination:

- flood-mapping queries should rank Sentinel-1 flood cards and workflow nodes ahead of NDVI product-intercomparison evidence;
- HLS/MODIS product-intercomparison queries should not rank flood workflow nodes as primary evidence;
- private asset and unsupported accuracy-proof requests should surface insufficient-evidence warnings rather than treating lexical matches as support.

Negative routing is a retrieval safety mechanism only. It does not replace schema validation, semantic validation, preflight, or live execution gates.
