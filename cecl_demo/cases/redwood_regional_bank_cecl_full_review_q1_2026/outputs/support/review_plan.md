# Review Plan: Q1 2026 CECL Allowance Review

The review plan below is the work Codex would perform against the discovered package.

## Baseline reproduction
Reproducing the supplied baseline reserve is the first check on whether the package is internally coherent and executable.

- Evidence: model/cecl_engine.py, data/loan_level_snapshot.csv, outputs/prior_baseline_reserve.csv
- Planned checks: rerun baseline reserve, compare total reserve, compare segment reserve

## Scenario review
Baseline, adverse, and severe reruns show whether reserves move directionally and materially in line with scenario severity.

- Evidence: scenarios/baseline.csv, scenarios/adverse.csv, scenarios/severe.csv, docs/scenario_assumptions.md
- Planned checks: rerun scenarios, compare total reserve, compare segment ordering

## Sensitivity testing
Forecast horizon, reversion speed, macro severity, and overlay magnitude are core CECL assumptions that should have understandable reserve impact.

- Evidence: docs/methodology.md, docs/overlay_memo.md, data/overlay_schedule.csv
- Planned checks: horizon sensitivity, reversion sensitivity, overlay sensitivity, driver bridge

## Documentation cross-check
Documentation should describe the same horizon, reversion, scenario, and overlay behavior that the implementation actually exhibits.

- Evidence: docs/methodology.md, docs/model_overview.md, docs/overlay_memo.md, model/cecl_engine.py
- Planned checks: horizon mismatch, overlay cap mismatch, scenario anomaly review
