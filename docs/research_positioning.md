# Research Positioning

Last updated: 2026-06-24

## Core Claim

`gee-agent-skill` explores how coding agents can operate Google Earth Engine through a reviewable, traceable, and safety-gated command-line harness.

The project should not be framed as a new remote-sensing method. Its contribution is an operations and reproducibility layer:

```text
natural-language request -> plan -> evidence -> template -> validation -> preflight -> confirmed export -> monitor -> trace
```

## Research Questions

1. Can agent-generated Earth Engine work be converted into a reviewable plan before code execution?
2. Can local dataset/operator evidence reduce unsupported or unsafe Earth Engine script generation?
3. Can dry-run, preflight, and live-export boundaries reduce accidental task submission?
4. Can run traces make agent-assisted geospatial workflows auditable enough for review and iteration?
5. Can golden examples serve as regression tests for an expanding library of Earth Engine workflows?

## Contribution Boundary

In scope:

- agent-native CLI contracts;
- plan schemas for geospatial task review;
- local RAG evidence and source attribution;
- validation and preflight gates;
- trace artifacts for reproducibility;
- benchmark protocols for supported and unsupported task handling.

Out of scope for current claims:

- new NDVI science;
- a GUI replacement for Earth Engine;
- autonomous bulk export;
- credential management;
- universal GEE task coverage;
- policy-grade analysis of Hong Kong vegetation.

## Why Hong Kong NDVI

Hong Kong NDVI is a compact regression target because it exercises common Earth Engine concerns:

- a real administrative AOI;
- optical imagery and cloud filtering;
- index computation;
- reducers over a geometry;
- table exports;
- land-cover interpretation boundaries;
- live task monitoring.

The examples are intentionally small. Their job is to make the harness observable and testable, not to define the full ambition of the project.

## Evaluation Framing

An honest evaluation should report:

- plan-field accuracy for supported prompts;
- validator pass/fail behavior for rendered scripts;
- dry-run no-credential behavior;
- preflight failure handling;
- export gating with `--confirm-live`;
- trace completeness and credential hygiene;
- robustness on unsupported or ambiguous prompts.

Do not report NDVI values as scientific findings unless a separate remote-sensing validation design is added.

## Paper Direction

A paper or technical report could be titled:

```text
An Agent-Native Harness for Traceable Google Earth Engine Workflows
```

The most defensible scope is a systems paper or reproducibility report, with Hong Kong NDVI as an evaluated case study and benchmark seed.
