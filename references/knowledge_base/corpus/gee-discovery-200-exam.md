# Corpus Card: 200-Project GEE Discovery Exam

source_id: corpus-gee-discovery-200-exam
source_type: curated-corpus-distillation
primary_status: curated
source_url: references/corpus/github_gee_discovery_200.yml
last_checked: 2026-07-31
method_name: GitHub Search API, multi-lane quality screening, metadata-only discovery
operator_chain: multi-lane discovery -> quality screen -> data/paper hints -> seed promotion review -> mistake lab -> rule updates
risk_level: medium

## Purpose

The 200-project discovery inventory is a broad exam queue for Google Earth Engine corpus expansion. It asks which task and data families are covered, which paper-linked hints deserve verification, and which sources deserve deeper local pattern audits.

It is not a code, data, or paper approval list. The generated discovery snapshot keeps every selected record at `quality_screened_unreviewed`; completed deep reviews are recorded as a separate, auditable overlay in `references/corpus/github_gee_reviewed_batch_01.yml`.

## Current Snapshot

The current file `references/corpus/github_gee_discovery_200.yml` was generated from three GitHub metadata lanes: the GEE topic, DOI/paper hints, and research-workflow hints.

Discovery-snapshot statistics:

- 200 candidates have direct GEE metadata evidence; forks, archived repositories, and search-lane-only matches are excluded.
- 89 are high-signal metadata candidates and 111 are qualified metadata candidates under the recorded score.
- 152 declare a license; 48 still show `NOASSERTION` and require license review before pattern-level sampling.
- 44 meet the metadata paper-candidate floor. This remains a routing hint, not verified publication linkage.

Deep-review overlay:

- 21 of the 200 discovery records have been reviewed at exact repository revisions; 179 remain in the queue.
- 3 additional anchor repositories were reviewed for comparison, for 24 total deep reviews.
- 17 reviews produced reusable, source-backed pattern cards; 7 deliberately produced no new promotion.
- 9 repository-paper pairs were checked; 7 supplied bounded patterns and 2 remained general context.

The first expanded inventory failed this exam: broad README matches admitted unrelated high-star API, OSINT, job-list, and general-resource repositories. The reproducible correction is the `domain_relevance_gate`: direct GEE metadata evidence is required before scoring. Star count, license presence, or README-search rank cannot substitute for domain relevance.

## Promotion Rules

A discovered repository can become an evidence source only when it improves coverage or quality and passes:

- license/provenance review;
- private-asset and credential scan;
- freshness or durable educational-value review;
- task-family coverage check;
- compatibility check against official Earth Engine API behavior.
- for paper-linked repositories, article DOI or publisher URL, inspected commit or release, journal/venue, and reproducibility scope.
- for data-using repositories, dataset version, bands/variables, scale/offset, QA/masking, projection/resampling, temporal coverage, access/license, asset stability, and private dependencies.

Even after promotion, do not vendor code into this repository. Extract only factual/operator patterns, validation implications, task prompts, and failure modes.

The deep-review record must pin the reviewed revision and inspected surfaces, complete the eight-field data contract, state the promotion or non-promotion decision, and preserve unknowns rather than inferring them.

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
