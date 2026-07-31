# Data-Usage Promotion Contract

source_id: google-earth-engine-data-catalog
last_checked: 2026-07-31
risk_level: high

Before a repository-derived pattern can influence a plan, recipe, or validator, record:

- exact dataset ID and version;
- bands or variables and their physical meaning;
- scale factor, offset, units, and no-data behavior;
- QA fields and masking policy;
- native grid, projection, resolution, and resampling or aggregation semantics;
- temporal coverage, cadence, and matching window;
- access route, provider license, and asset stability;
- public, community, or private authority and any private dependency.

An unknown field stays unknown. Repository topics, filenames, examples, paper links, and stars are not substitutes for this contract.

## Importance Rule

Classify an omission as `important_knowledge` when it can change numerical correctness, authorization, reproducibility, data integrity, or a scientific claim. Turn it into a rule, failure card, or blocking evaluation.

Classify an omission as `general_knowledge` when it improves discoverability, ergonomics, or explanation without changing those outcomes. Keep it searchable, but do not let it block execution.
