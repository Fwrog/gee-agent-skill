# General Corpus Review Observations

source_type: mistake-lab-general-knowledge
last_checked: 2026-07-31
risk_level: low

These observations improve discovery or review ergonomics but do not independently block execution:

- Record catalogue version and migration notices so maintainers know when to schedule a refresh.
- Record whether an example requires interactive notebook or GUI review so it is not mistaken for unattended automation.
- Record monitor-specific refresh behavior as a tool note; terminal-state and output-readback requirements remain the important, tool-independent rules.

These notes stay searchable as `general_knowledge`. Promote them to blocking rules only if a reproduced failure shows an effect on correctness, authorization, reproducibility, data integrity, or claims.
