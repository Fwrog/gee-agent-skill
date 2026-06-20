# Research Note: GEE-OPs Operator Knowledge Base

source_id: research-gee-ops
source_type: research-paper
publisher: Geo-spatial Information Science
url: https://doi.org/10.1080/10095020.2025.2505556
retrieved_at: 2026-06-21
primary_status: non-canonical
ee_language: JavaScript
risk_level: medium

## How To Use This Note

Use this paper as design inspiration for retrieval structure and operator-aware prompts. Do not treat it as canonical Earth Engine API documentation because the paper targets JavaScript operator mining from public scripts and not this repository's Python templates.

## Transferable Design Ideas

GEE-OPs organizes Earth Engine operator knowledge into four complementary tables:

- Operator syntax: names, signatures, and usage forms.
- Operator relationship frequency: common pairs and relationship types observed in code.
- Operator frequent pattern: repeated operator combinations mined from scripts.
- Operator relationship chain: longer ordered usage paths that resemble workflow skeletons.

The practical lesson for this repository is to index not only prose docs, but also operator relationships such as `ImageCollection.filterDate -> filterBounds -> map -> select -> mean -> reduceRegions -> Export.table.toDrive`.

## RAG Metadata Implications

Add or preserve fields that make operator-aware retrieval possible:

- `api_namespace`
- `method_name`
- `operator_chain`
- `required_args`
- `return_type`
- `task_domain`
- `dataset_id`
- `risk_level`
- `source_type`

## Static Validation Implications

The paper uses abstract syntax tree ideas to extract operator relationships. For this Python skill, static validation should keep using Python `ast` for syntax, imports, calls, string constants, and obvious unsafe patterns. Regex-only validation is acceptable only as a narrow supplement.

## Source Risk

The paper reports results from mined JavaScript scripts and syntax documentation. This is valuable for designing retrieval and operator chains, but examples can encode outdated, non-idiomatic, or JavaScript-only practices. Official Google Earth Engine docs remain the source of truth.

