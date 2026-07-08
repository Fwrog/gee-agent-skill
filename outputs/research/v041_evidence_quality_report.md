# v0.4.1 Evidence Quality Report

Date: 2026-07-09

Changes:

- Added alias, canonical-term, negative-query, and source-refresh metadata to evidence cards.
- Added `scripts/audit_evidence_quality.py` for source matching, accepted-card completeness, private-content scan, and long-text warnings.
- Enforced accepted-card source URL, trust tier, allowed use, limitations, claim boundaries, and actionable hints.

Quality boundary:

- Evidence cards store short paraphrased facts, limitations, claim boundaries, planner hints, and validator hints.
- Cards do not store long copied source text, full papers, third-party code, private assets, local Drive folders, credentials, or unpublished result values.

Expected check:

```bash
python scripts/audit_evidence_quality.py --json
```
