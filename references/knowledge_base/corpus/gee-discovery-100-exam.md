# Corpus Card: 100+ GEE Discovery Exam

source_id: corpus-gee-discovery-100-exam
source_type: curated-corpus-distillation
primary_status: curated
source_url: references/corpus/github_gee_discovery_100.yml
last_checked: 2026-06-23
method_name: GitHub Search API, topic:google-earth-engine, metadata-only discovery
operator_chain: broad discovery -> task tagging -> seed promotion review -> local pattern audit -> rule updates
risk_level: medium

## Purpose

The 100+ discovery inventory is a broad exam queue for Google Earth Engine corpus expansion. It answers: what kinds of GEE repositories exist now, which task families are over- or under-covered, and which sources deserve deeper local pattern audits.

It is not a code-ingestion approval list. Every record starts as `review_state: discovered_unreviewed` and `sampling_level: metadata_only_discovery`.

## Current Snapshot

The current file `references/corpus/github_gee_discovery_100.yml` was generated from GitHub metadata using `topic:google-earth-engine`.

Snapshot statistics:

- 125 repository candidates from 617 reported topic matches.
- 83 candidates have a declared license and are eligible only for metadata-and-patterns review.
- 38 candidates require license review before any pattern-level sampling.
- 4 candidates require maintainer review because they are forks or archived.
- Inferred task tags cover Python, JavaScript Code Editor examples, education/tutorials, production tooling, spectral indices, Sentinel-2 optical workflows, Landsat/LST, land-cover/change, Sentinel-1/SAR, and water/flood.

This broad topic search is only one discovery lane. A second lane should explicitly review high-signal community maintainers such as `giswqs`/OpenGeo and `gee-community`. A third lane should collect paper-linked repositories from remote-sensing journals and keep them metadata-only until DOI, license, private-asset, and reproducibility checks pass.

## Promotion Rules

A discovered repository can move into the 30-50 seed inventory only when it improves coverage or quality and passes:

- license/provenance review;
- private-asset and credential scan;
- freshness or durable educational-value review;
- task-family coverage check;
- compatibility check against official Earth Engine API behavior.
- for paper-linked repositories, article DOI or publisher URL, inspected commit or release, journal/venue, and reproducibility scope.

Even after promotion, do not vendor code into this repository. Extract only factual/operator patterns, validation implications, task prompts, and failure modes.

## Rule Distillation Targets

Use the discovery layer to find sources for these rule gaps:

- temporal joins and save-first/save-all pairing;
- SAR speckle filtering, polarization constraints, and before/after change metrics;
- projection, native scale, reprojection, and `tileScale` tradeoffs;
- image export contracts for GeoTIFF region, CRS, scale, and max pixels;
- table export contracts for selectors, schemas, feature properties, and task state;
- dataset-specific QA bands and cloud/shadow masks;
- bounded client fetches for preflight/debug probes;
- Browser and Computer Use boundaries for agent workflows.

## Agent Boundary

Browser is useful for inspecting official docs, repository pages, local previews, and UI-only examples. Computer Use is useful only when no CLI/API/plugin surface can operate the local Mac UI. Neither replaces `gee-skill`, the Earth Engine Python API, static validation, preflight probes, or explicit live-export confirmation.
