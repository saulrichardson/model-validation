# CECL Demo

Contained artifact-first CECL demo layer for this repo.

This demo is intentionally separate from the older generic `seed_banks/` workbench story. It is the shortest path to a convincing, stakeholder-facing CECL review demo where the assistant creates the bank package, performs the review work, and produces finished outputs.

## Workflows

1. `redwood_regional_bank_cecl_full_review_q1_2026`
   - Runnable CECL reserve engine
   - Baseline/adverse/severe scenario reruns
   - Sensitivity testing
   - Documentation cross-checking
   - Stakeholder-facing CECL review memo in LaTeX/PDF

2. `harborlight_savings_cecl_gap_assessment_q1_2026`
   - Documentation-led CECL package
   - No runnable reserve engine
   - Scenario/output consistency review
   - Evidence sufficiency and gap assessment
   - Stakeholder-facing CECL gap assessment in LaTeX/PDF

## Build

```bash
poetry run python scripts/build_cecl_demo.py --case all --authoring-mode gateway --compile-pdf
```

Use `--authoring-mode local` if the gateway is unavailable.

## Output Layout

Each case lives under `cecl_demo/cases/<case_slug>/` with:

- `input_package/`: the pseudo-bank upload
- `outputs/stakeholder/`: LaTeX source and compiled PDF
- `outputs/support/`: discovery summary, review plan, evidence ledger, findings, trace, and appendices
