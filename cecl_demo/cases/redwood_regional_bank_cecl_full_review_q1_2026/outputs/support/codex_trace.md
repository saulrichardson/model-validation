# Codex Trace: Q1 2026 CECL Allowance Review

This is a readable execution trace for the review behaviors the platform should eventually automate.

## Step 1: Discovery
Inventoried the CECL package, identified model code, scenario tables, loan-level data, prior outputs, and supporting methodology documents.

- Inputs: input_package/*
- Outputs: discovery_summary.json, evidence_ledger.json

## Step 2: Planning
Committed to baseline reproduction, scenario reruns, sensitivity testing, and documentation cross-checking based on the evidence supplied.

- Inputs: discovery_summary.json, docs/methodology.md, outputs/prior_baseline_reserve.csv
- Outputs: review_plan.md

## Step 3: Quantitative execution
Ran the reserve engine across baseline, adverse, and severe scenarios, then executed horizon, reversion, severity, and overlay sensitivities.

- Inputs: model/cecl_engine.py, data/loan_level_snapshot.csv, scenarios/*.csv
- Outputs: scenario_results.csv, segment_reserve_comparison.csv, sensitivity_results.csv, driver_bridge.csv

## Step 4: Documentation cross-checking
Compared documented horizon, reversion, scenario, and overlay assumptions to actual behavior in the reserve results.

- Inputs: docs/*.md, data/overlay_schedule.csv, segment_reserve_comparison.csv
- Outputs: documentation_crosscheck.md, findings_register.json

## Step 5: Synthesis
Drafted the stakeholder-facing CECL review memo and supporting artifact pack.

- Inputs: findings_register.json, coverage_statement.md, baseline_reproduction.json
- Outputs: cecl_review_memo.tex, cecl_review_memo.pdf
