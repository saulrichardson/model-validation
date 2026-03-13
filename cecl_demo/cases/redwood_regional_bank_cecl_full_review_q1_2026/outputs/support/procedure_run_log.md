# Procedure Run Log: Q1 2026 CECL Allowance Review

This log records the granular review actions that the platform is intended to automate.

## EVT-01 - Inventory uploaded package
- Phase: discovery
- Related procedure: FR-01
- Action: Enumerated the input package and confirmed presence of reserve engine, loan-level data, scenarios, prior outputs, and CECL methodology documents.
- Inputs: input_package/model/cecl_engine.py, input_package/data/loan_level_snapshot.csv, input_package/scenarios/*.csv, input_package/docs/*.md
- Outputs: outputs/support/discovery_summary.md, outputs/support/evidence_ledger.json
- Result: Case classified as execution-capable CECL review with no material runtime blockers.

## EVT-02 - Select review lanes
- Phase: planning
- Related procedure: FR-01
- Action: Chose baseline reproduction, scenario reruns, sensitivity testing, reserve bridge, and documentation challenge as the primary review lanes.
- Inputs: outputs/support/discovery_summary.md, input_package/docs/methodology.md, input_package/docs/overlay_memo.md
- Outputs: outputs/support/review_plan.md, outputs/support/review_strategy.md
- Result: Ten executable procedures selected; none blocked.

## EVT-03 - Reproduce packaged baseline reserve
- Phase: execution
- Related procedure: FR-02
- Action: Reran the packaged engine under the baseline scenario and reconciled the reproduced reserve to the supplied baseline reserve file.
- Inputs: input_package/model/cecl_engine.py, input_package/data/loan_level_snapshot.csv, input_package/scenarios/baseline.csv, input_package/outputs/prior_baseline_reserve.csv
- Outputs: outputs/support/baseline_reproduction.json
- Result: Packaged reserve 4876841.47; rerun reserve 4876841.47; absolute delta 0.00.

## EVT-04 - Run baseline, adverse, and severe scenarios
- Phase: execution
- Related procedure: FR-03
- Action: Executed the reserve engine across the three supplied scenario paths and aggregated total reserve results.
- Inputs: input_package/model/cecl_engine.py, input_package/data/loan_level_snapshot.csv, input_package/scenarios/baseline.csv, input_package/scenarios/adverse.csv, input_package/scenarios/severe.csv
- Outputs: outputs/support/scenario_results.csv
- Result: Portfolio reserve moved from 4876841.47 to 7132021.97 to 8287703.47.

## EVT-05 - Check segment-level scenario ordering
- Phase: execution
- Related procedure: FR-04
- Action: Compared segment reserve amounts across baseline, adverse, and severe scenarios to test directional reasonableness by segment.
- Inputs: outputs/support/scenario_results.csv, input_package/docs/scenario_assumptions.md, input_package/docs/overlay_memo.md
- Outputs: outputs/support/segment_reserve_comparison.csv
- Result: Residential Mortgage reserve fell from 327699.21 in adverse to 217710.91 in severe.

## EVT-06 - Run forecast-horizon sensitivity
- Phase: execution
- Related procedure: FR-05
- Action: Tested baseline reserve under alternate forecast horizons to challenge the documented 4-quarter assumption versus the 6-quarter implementation.
- Inputs: input_package/docs/methodology.md, input_package/model/cecl_engine.py
- Outputs: outputs/support/sensitivity_results.csv
- Result: Changing the baseline forecast horizon from 6 quarters to 4 quarters changed reserve modestly, but confirmed a policy-versus-implementation mismatch.

## EVT-07 - Run reversion-speed sensitivity
- Phase: execution
- Related procedure: FR-06
- Action: Re-estimated severe-scenario reserve using longer reversion periods to test sensitivity to the reversion assumption.
- Inputs: input_package/docs/methodology.md, input_package/model/cecl_engine.py
- Outputs: outputs/support/sensitivity_results.csv
- Result: Extending severe reversion from 2 to 6 quarters increased reserve from 8287703.47 to 8472904.31.

## EVT-08 - Run macro-severity scaling sensitivity
- Phase: execution
- Related procedure: FR-07
- Action: Scaled severe macro stress to test whether reserve responds monotonically to harsher macro conditions.
- Inputs: input_package/scenarios/severe.csv, input_package/model/cecl_engine.py
- Outputs: outputs/support/sensitivity_results.csv
- Result: Increasing severe macro scaling from 1.00x to 1.25x increased reserve from 8287703.47 to 9803105.55.

## EVT-09 - Run overlay-magnitude sensitivity
- Phase: execution
- Related procedure: FR-08
- Action: Removed and amplified overlays to measure how much of the severe reserve outcome is attributable to overlay posture.
- Inputs: input_package/data/overlay_schedule.csv, input_package/docs/overlay_memo.md
- Outputs: outputs/support/sensitivity_results.csv
- Result: Removing severe overlays reduced reserve from 8287703.47 to 7850916.88; amplifying to 1.50x raised reserve to 8506096.88.

## EVT-10 - Build reserve-driver bridge
- Phase: execution
- Related procedure: FR-09
- Action: Constructed a simple driver bridge to attribute severe-versus-baseline reserve movement to major macro and overlay factors.
- Inputs: input_package/scenarios/baseline.csv, input_package/scenarios/severe.csv, input_package/model/cecl_engine.py
- Outputs: outputs/support/driver_bridge.csv
- Result: CRE price growth was the largest standalone driver, contributing 1108566.01 of severe-versus-baseline reserve change.

## EVT-11 - Cross-check methodology against implementation
- Phase: documentation_challenge
- Related procedure: FR-10
- Action: Compared documented forecast, reversion, scenario, and overlay assumptions to the implemented engine constants and quantitative outputs.
- Inputs: input_package/docs/methodology.md, input_package/docs/model_overview.md, input_package/docs/overlay_memo.md, input_package/model/cecl_engine.py, outputs/support/segment_reserve_comparison.csv
- Outputs: outputs/support/documentation_crosscheck.md, outputs/support/findings_register.json
- Result: Recorded horizon/reversion mismatch, overlay-cap mismatch, and severe Residential Mortgage anomaly as formal findings.

## EVT-12 - Assemble internal review pack
- Phase: synthesis
- Related procedure: FR-10
- Action: Combined discovery, planning, quantitative outputs, documentation challenge, and evidence mapping into the final internal-review report pack.
- Inputs: outputs/support/review_strategy.md, outputs/support/procedure_run_log.md, outputs/support/findings_register.json, outputs/support/evidence_map.md
- Outputs: outputs/stakeholder/cecl_review_memo.tex, outputs/stakeholder/cecl_review_memo.pdf
- Result: Produced a comprehensive internal CECL review memo with explicit provenance, raw evidence excerpts, and procedure-level detail.
