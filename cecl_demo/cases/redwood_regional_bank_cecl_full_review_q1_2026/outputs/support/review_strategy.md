# Review Strategy: Q1 2026 CECL Allowance Review

Because the package contained runnable code, scenario files, prior outputs, and core methodology documents, the review strategy prioritized execution-based challenge first and then used documentation review to test whether the written methodology and governance artifacts actually described the observed reserve behavior.

## Review Questions
1. Does the package contain enough evidence to support a full execution-based CECL review rather than a documentation-only assessment?
2. Can the supplied baseline reserve be reproduced from the packaged reserve engine, portfolio data, and baseline scenario?
3. Do reserve outputs move directionally and materially across Baseline, Adverse, and Severe scenarios both overall and by major segment?
4. How sensitive are reserves to forecast horizon, reversion speed, macro severity, and overlay magnitude assumptions?
5. Do the methodology, scenario, and overlay documents faithfully describe the behavior observed in the implemented CECL process, especially for Residential Mortgage?

## Procedure Selection Rationale
### FR-01 - Package inventory and case classification
- Status: executed
- Objective: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.
- Why selected: Runnable code, scenario tables, loan-level data, prior outputs, and methodology documents were all present.
- Evidence relied upon: model/cecl_engine.py, data/loan_level_snapshot.csv, scenarios/baseline.csv, outputs/prior_baseline_reserve.csv, docs/methodology.md
- Success or assessment criteria: Review should only proceed as execution-based if engine, data, scenarios, and prior outputs are all available.

### FR-02 - Baseline reproduction
- Status: executed
- Objective: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.
- Why selected: A packaged prior baseline reserve was supplied alongside the runnable engine and source portfolio.
- Evidence relied upon: model/cecl_engine.py, data/loan_level_snapshot.csv, outputs/prior_baseline_reserve.csv
- Success or assessment criteria: Total reserve and segment reserve should reconcile within tolerance; large deltas would undermine confidence in package integrity.

### FR-03 - Portfolio-level scenario reruns
- Status: executed
- Objective: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.
- Why selected: The package included three explicit scenario files and a model designed to consume them.
- Evidence relied upon: scenarios/baseline.csv, scenarios/adverse.csv, scenarios/severe.csv, model/cecl_engine.py
- Success or assessment criteria: Portfolio reserve should generally increase with scenario severity absent a documented exception.

### FR-04 - Segment-level reasonableness review
- Status: executed
- Objective: Test whether scenario ordering remains directionally sensible at the segment level.
- Why selected: CECL governance depends on segment-level reserve understanding, not just portfolio totals.
- Evidence relied upon: outputs/support/segment_reserve_comparison.csv, docs/scenario_assumptions.md, docs/overlay_memo.md
- Success or assessment criteria: Segment movements should generally align to scenario severity or be explicitly supported by documented assumptions.

### FR-05 - Forecast horizon sensitivity
- Status: executed
- Objective: Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.
- Why selected: The methodology makes forecast horizon a named governance assumption.
- Evidence relied upon: docs/methodology.md, outputs/support/sensitivity_results.csv
- Success or assessment criteria: Reserve movement should be understandable and documented; mismatch to stated policy must be surfaced.

### FR-06 - Reversion speed sensitivity
- Status: executed
- Objective: Assess how severe-scenario reserve responds to longer reversion periods.
- Why selected: Reversion mechanics are central to CECL governance and are explicitly documented in the package.
- Evidence relied upon: docs/methodology.md, outputs/support/sensitivity_results.csv
- Success or assessment criteria: Reserve should move directionally as reversion assumptions are extended or shortened.

### FR-07 - Macro severity sensitivity
- Status: executed
- Objective: Test whether reserve responds proportionally to macro severity scaling.
- Why selected: Scenario severity and directional reasonableness are core to CECL challenge work.
- Evidence relied upon: scenarios/severe.csv, outputs/support/sensitivity_results.csv
- Success or assessment criteria: Scaling macro severity upward should generally increase reserve; weaker response would require explanation.

### FR-08 - Overlay magnitude sensitivity
- Status: executed
- Objective: Assess the reserve effect of removing or amplifying qualitative overlays.
- Why selected: The package included a scenario-by-segment overlay schedule and an overlay governance memo.
- Evidence relied upon: data/overlay_schedule.csv, docs/overlay_memo.md, outputs/support/sensitivity_results.csv
- Success or assessment criteria: Overlay effect should be quantitatively explainable and consistent with governance statements.

### FR-09 - Reserve driver bridge
- Status: executed
- Objective: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.
- Why selected: A driver bridge makes the review more interpretable and supports reasonableness challenge.
- Evidence relied upon: outputs/support/driver_bridge.csv, scenarios/baseline.csv, scenarios/severe.csv
- Success or assessment criteria: Major reserve movement should be attributable to understandable drivers rather than unexplained residual behavior.

### FR-10 - Methodology and documentation alignment review
- Status: executed
- Objective: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- Why selected: The package contained enough documentation to support direct cross-checking against the model and results.
- Evidence relied upon: docs/methodology.md, docs/model_overview.md, docs/scenario_assumptions.md, docs/overlay_memo.md, model/cecl_engine.py
- Success or assessment criteria: Documented horizon, reversion, scenario logic, and overlay posture should match the implemented process or be clearly qualified.
