# Evidence-to-Procedure Map: Q1 2026 CECL Allowance Review

This map shows how package artifacts and derived outputs informed specific review procedures.

## data/loan_level_snapshot.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-01, FR-02
- How used: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.

## data/overlay_schedule.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-08
- How used: Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.

## docs/methodology.md
- Artifact role: package or derived evidence
- Procedures supported: FR-01, FR-05, FR-06, FR-10
- How used: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Forecast horizon sensitivity: Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.; Reversion speed sensitivity: Assess how severe-scenario reserve responds to longer reversion periods.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.

## docs/model_overview.md
- Artifact role: package or derived evidence
- Procedures supported: FR-10
- How used: Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.

## docs/overlay_memo.md
- Artifact role: package or derived evidence
- Procedures supported: FR-04, FR-08, FR-10
- How used: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.; Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.

## docs/scenario_assumptions.md
- Artifact role: package or derived evidence
- Procedures supported: FR-04, FR-10
- How used: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.

## model/cecl_engine.py
- Artifact role: package or derived evidence
- Procedures supported: FR-01, FR-02, FR-03, FR-10
- How used: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.; Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.

## outputs/prior_baseline_reserve.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-01, FR-02
- How used: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.

## outputs/support/driver_bridge.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-09
- How used: Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.

## outputs/support/segment_reserve_comparison.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-04
- How used: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.

## outputs/support/sensitivity_results.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-05, FR-06, FR-07, FR-08
- How used: Forecast horizon sensitivity: Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.; Reversion speed sensitivity: Assess how severe-scenario reserve responds to longer reversion periods.; Macro severity sensitivity: Test whether reserve responds proportionally to macro severity scaling.; Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.

## scenarios/adverse.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-03
- How used: Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.

## scenarios/baseline.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-01, FR-03, FR-09
- How used: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.

## scenarios/severe.csv
- Artifact role: package or derived evidence
- Procedures supported: FR-03, FR-07, FR-09
- How used: Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Macro severity sensitivity: Test whether reserve responds proportionally to macro severity scaling.; Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.
