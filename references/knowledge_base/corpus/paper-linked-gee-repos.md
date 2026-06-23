# Corpus Card: Paper-Linked GEE Repository Review

source_id: corpus-paper-linked-gee-repos
source_type: curated-corpus-policy
primary_status: curated
source_url: https://github.com/giswqs; https://github.com/gee-community; references/corpus/github_gee_seed_repos.yml
last_checked: 2026-06-23
method_name: paper repository discovery, DOI provenance, license review, pattern-only distillation
operator_chain: paper search -> repository provenance -> license and private-asset review -> local read-only corpus exam -> rule update
risk_level: medium

## Purpose

Paper-linked GitHub repositories are a high-value source for realistic GEE workflows because they often encode full methods, data assumptions, validation routines, and export patterns from published remote-sensing research. They are not automatically safe to copy or execute.

Use this card to guide future corpus expansion beyond generic GitHub topic search.

## Priority Sources

Start with established community maintainers and organizations:

- `giswqs` / OpenGeo ecosystem for geemap, notebook examples, teaching material, and Python-first GEE workflows.
- `gee-community` for maintained community packages and examples such as geemap, geetools, qgis-earthengine-plugin, palettes, and example scripts.
- official Google Earth Engine repositories for canonical API behavior.

Then add paper-linked repositories from remote-sensing and geoscience publications when they pass provenance checks.

## Journal-Linked Discovery

Prioritize repositories linked from article pages, supplementary material, Zenodo records, or author project pages for venues such as:

- IEEE Transactions on Geoscience and Remote Sensing;
- ISPRS Journal of Photogrammetry and Remote Sensing;
- International Journal of Applied Earth Observation and Geoinformation;
- Remote Sensing of Environment;
- Remote Sensing.

Record the article DOI or publisher URL next to the repository URL. If there is no clear paper-to-repository link, keep the candidate in metadata-only discovery.

## Review Checklist

Before a paper-linked repository can influence rules or recipes, record:

- article DOI or publisher URL;
- repository URL and commit or release inspected;
- license and reuse boundary;
- Earth Engine language: Python, JavaScript Code Editor, R, or mixed;
- whether the workflow depends on private Earth Engine assets, local paths, or credentials;
- datasets, bands, QA masks, reducers, joins, exports, and task-family tags;
- known failure modes and quota risks;
- whether the observed pattern agrees with current official Earth Engine API docs.

## Promotion Rule

Default harvest level is `metadata_only_until_license_review`. Promote only non-copyrightable facts and small attributed patterns:

- operator chains;
- validation implications;
- natural-language task prompts;
- dataset and band requirements;
- failure modes;
- reproducibility caveats.

Do not copy paper repository code into this project by default. Do not treat publication status as proof that a script is current, license-compatible, credential-safe, or runnable in a different Earth Engine project.

## Rule Distillation Targets

Paper-linked repositories are especially useful for strengthening:

- task-specific QA masks and cloud/shadow policies;
- temporal joins, interpolation, compositing, and change metrics;
- SAR preprocessing and flood/change-detection thresholds;
- LST scale factors, emissivity assumptions, and uncertainty fields;
- export schemas used for model training or validation;
- preflight checks that catch private assets, empty collections, no-band images, and projection or scale mistakes.
