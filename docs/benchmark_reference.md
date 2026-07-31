# Benchmark Reference

The project uses two external works as design references, not as imported leaderboards.

## Operator-Knowledge Reference

[GEE-OPs](https://doi.org/10.1080/10095020.2025.2505556) motivates syntax, operator relationships, frequent patterns, and longer operator chains. The local knowledge base uses those structures for retrieval metadata while keeping current API and dataset facts subordinate to official Earth Engine sources.

## Evaluation Reference

[AutoGEEval++](https://doi.org/10.1080/20964471.2025.2581425) reports unit, combination, and theme task levels plus boundary cases and execution-oriented evaluation. The local quick suite adapts only that structure:

```bash
gee-skill eval evals/benchmark_quick_reference.yml --json
```

The local suite contains seven deterministic offline cases. It does not include the paper's cases, live execution judge, resource protocol, or model leaderboard, so its pass rate is not externally comparable.

## Local Promotion Rule

A distilled paper or GitHub pattern can enter the knowledge base only after source review, official-fact reconciliation, an evidence card, and a regression case. GitHub code is not copied by default; the accepted local artifacts are short paraphrased patterns with explicit limitations.

The maintenance benchmark also includes a reproducible mistake lab:

```bash
python scripts/run_distillation_mistake_lab.py --json
```

It compares deliberately incomplete reviews with explicit data and reproducibility contracts, then separates important omissions from general knowledge. This is a regression tool for the repository's review process, not a model reasoning score.
