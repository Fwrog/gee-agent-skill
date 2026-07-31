# Domain-Relevance Gate For Corpus Discovery

rule_id: domain_relevance_gate
evidence_level: reproduced-internal-regression
last_checked: 2026-07-31
importance: important_knowledge

A GitHub README search match, star count, or declared repository license does not establish that a repository is a Google Earth Engine project.

The 200-project inventory must require direct domain evidence in repository metadata: a Google Earth Engine topic-query match, a matching repository topic, or an explicit Earth Engine phrase in the repository name or description. Search-lane-only matches remain outside the inventory until a human review establishes relevance.

Regression checks name known false positives from the earlier inventory so a broad README query cannot silently reintroduce unrelated API lists, OSINT lists, job lists, or general geospatial collections.
