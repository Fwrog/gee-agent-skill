# Portfolio And Research Positioning Audit

Last updated: 2026-06-24

## Bottom Line

`gee-agent-skill` should be presented as an agent-native Google Earth Engine harness, not as a Hong Kong NDVI project. The Hong Kong NDVI workflows are useful because they are small, repeatable golden examples that exercise the harness end to end.

The strongest project frame is:

```text
CLI contract + plan schema + dataset catalog + recipe registry + RAG evidence + preflight + export
```

That frame is broader than the current examples while staying honest about what has been implemented and tested.

## What The Repository Proves Today

- Natural-language Earth Engine requests can be normalized into reviewable plans.
- Local dataset, recipe, operator, rules, and failure evidence can be searched before execution.
- Jinja2 templates can render Earth Engine Python scripts with stable inputs and output schemas.
- Static and semantic validation can run before live use.
- Dry runs and plan commands can run without Earth Engine credentials.
- Live export is gated by `--project` and `--confirm-live`.
- Export tasks can be monitored and trace artifacts can be inspected after submission.

## What The Hong Kong NDVI Examples Prove

The Hong Kong workflows should be described as regression evidence:

- v0.1 proves a minimal whole-AOI January 2024 NDVI CSV path.
- v0.2 proves a land-cover-aware January 2024 NDVI CSV path with Dynamic World masks and interpretation strata.
- v0.3 proves a non-January, year-long 16-day NDVI CSV path through the editable `gee-plan/v0.3` flow.

They do not prove that the package is a universal GEE agent, a scientific Hong Kong vegetation monitoring product, or a production remote-sensing platform.

## Portfolio Narrative

Use this wording:

```text
I built an agent-native Google Earth Engine command-line harness that lets a coding agent turn a geospatial request into a source-grounded plan, rendered Python script, validation report, live preflight, confirmed export, monitored task, and reproducible run trace. The Hong Kong NDVI workflows are golden regression examples used to verify the harness contract.
```

Avoid this wording:

```text
I built a Hong Kong NDVI analysis project.
```

That undersells the system and overstates the scientific meaning of the demo outputs.

## Research Positioning

The research contribution is not a new NDVI algorithm. It is a reproducible agent operations layer for Earth Engine:

- task interpretation as a reviewable contract;
- source-grounded dataset and operator selection;
- execution boundaries that separate plan, dry run, preflight, and live export;
- trace artifacts that make agent-generated geospatial work auditable;
- benchmark cases that check whether the harness handles supported and unsupported requests predictably.

## Current Gaps

- Live v0.3 export support is template-specific to the Hong Kong 2024 16-day NDVI CSV workflow.
- Other task families have parser and recipe coverage but need their own templates, preflight adapters, and live verification.
- The v0.3 CSV is an all-surface whole-AOI engineering output, not vegetation-only science.
- Windows commands are documented, but recent validation evidence is from macOS/Linux and CI.
- The benchmark suite needs clearer metrics before it can support a paper-style evaluation claim.

## Recommended Productization Order

1. Keep README and SKILL framing centered on the harness contract.
2. Maintain Hong Kong workflows as golden regression cases.
3. Add capability and benchmark docs that separate supported, partially supported, and planned surfaces.
4. Add security and citation files so the repository looks publishable without implying credentials or live access are included.
5. Add one non-NDVI workflow only after it has the same plan, render, validation, preflight, and trace evidence.
