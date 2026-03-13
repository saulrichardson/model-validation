# Procedure Run Log: Q1 2026 CECL Readiness Gap Assessment

This log records the granular review actions that the platform is intended to automate.

## EVT-01 - Inventory uploaded package
- Phase: discovery
- Related procedure: GA-01
- Action: Enumerated the documentation package and checked whether a reserve engine, reproducibility notebook, and execution lineage were present.
- Inputs: input_package/docs/*.md, input_package/scenarios/*.csv, input_package/outputs/*.csv
- Outputs: outputs/support/discovery_summary.md, outputs/support/evidence_ledger.json
- Result: Case classified as documentation-led CECL gap assessment because runtime artifacts were not supplied.

## EVT-02 - Define supported and blocked review lanes
- Phase: planning
- Related procedure: GA-01
- Action: Separated executable documentation-led checks from blocked runtime procedures before deeper review work.
- Inputs: outputs/support/discovery_summary.md, input_package/docs/evidence_request_log.md, input_package/docs/gap_tracker.md
- Outputs: outputs/support/review_plan.md, outputs/support/review_strategy.md, outputs/support/coverage_statement.md
- Result: Evidence sufficiency, scenario consistency, output reconciliation, and overlay review retained; baseline reproduction and sensitivities blocked.

## EVT-03 - Assess execution readiness and lineage
- Phase: documentation_challenge
- Related procedure: GA-02
- Action: Reviewed governance and evidence-request materials to determine whether the package could support model execution or reproduction.
- Inputs: input_package/docs/evidence_request_log.md, input_package/docs/gap_tracker.md, input_package/docs/governance_minutes.md
- Outputs: outputs/support/coverage_statement.md, outputs/support/documentation_crosscheck.md
- Result: Confirmed that no reserve engine, reproducibility notebook, or lineaged runbook was available.

## EVT-04 - Compare scenario narrative to numeric scenario files
- Phase: documentation_challenge
- Related procedure: GA-03
- Action: Compared the severe scenario narrative to quarter-by-quarter severe and adverse scenario tables.
- Inputs: input_package/docs/scenario_assumptions.md, input_package/scenarios/adverse.csv, input_package/scenarios/severe.csv
- Outputs: outputs/support/documentation_crosscheck.md, outputs/support/findings_register.json
- Result: Found severe house-price growth less severe than adverse in 4 quarter(s): 2026Q3, 2026Q4, 2027Q1, 2027Q2.

## EVT-05 - Reconcile horizon and reversion descriptions
- Phase: documentation_challenge
- Related procedure: GA-04
- Action: Compared methodology, model overview, and scenario package to determine whether one consistent forecast and reversion structure was evidenced.
- Inputs: input_package/docs/methodology.md, input_package/docs/model_overview.md, input_package/docs/scenario_assumptions.md
- Outputs: outputs/support/documentation_crosscheck.md, outputs/support/findings_register.json
- Result: Identified inconsistent 8Q/4Q and 6Q/2Q horizon descriptions with only six numeric quarters provided.

## EVT-06 - Reconcile documented segments to output segments
- Phase: documentation_challenge
- Related procedure: GA-05
- Action: Compared documented segment taxonomy to the segments used in the provided reserve output files.
- Inputs: input_package/docs/methodology.md, input_package/docs/model_overview.md, input_package/outputs/provided_segment_reserves.csv
- Outputs: outputs/support/findings_register.json
- Result: Documentation lists 5 segments while provided outputs reconcile to 4 segments.

## EVT-07 - Reconcile documented overlay cap to provided overlay bridge
- Phase: documentation_challenge
- Related procedure: GA-06
- Action: Compared the documented overlay cap and governance description to the segment overlay values in the provided bridge.
- Inputs: input_package/docs/overlay_memo.md, input_package/outputs/provided_overlay_bridge.csv
- Outputs: outputs/support/findings_register.json
- Result: Documented overlay cap of 6.0 bps did not reconcile to provided overlay values reaching 18.0 bps.

## EVT-08 - Record blocked baseline reproduction
- Phase: blocked_work
- Related procedure: GA-07
- Action: Evaluated whether baseline reproduction could be performed and formally logged why it was not executed.
- Inputs: input_package/outputs/provided_reserve_summary.csv, input_package/docs/evidence_request_log.md
- Outputs: outputs/support/coverage_statement.md, outputs/support/evidence_request_list.md
- Result: Baseline reproduction blocked because no reserve engine or reproducibility notebook was supplied.

## EVT-09 - Record blocked scenario reruns and sensitivity testing
- Phase: blocked_work
- Related procedure: GA-08
- Action: Evaluated whether scenario reruns and sensitivity tests could be performed and formally logged why they were not executed.
- Inputs: input_package/scenarios/*.csv, input_package/docs/gap_tracker.md
- Outputs: outputs/support/coverage_statement.md, outputs/support/evidence_request_list.md
- Result: Sensitivity testing blocked because no model implementation, controllable parameters, or runbook support was supplied.

## EVT-10 - Assemble internal gap-assessment pack
- Phase: synthesis
- Related procedure: GA-09
- Action: Combined discovery, coverage boundary, documentation findings, and evidence requests into the final internal gap-assessment report pack.
- Inputs: outputs/support/review_strategy.md, outputs/support/procedure_run_log.md, outputs/support/findings_register.json, outputs/support/evidence_request_list.md
- Outputs: outputs/stakeholder/cecl_gap_assessment.tex, outputs/stakeholder/cecl_gap_assessment.pdf
- Result: Produced a comprehensive CECL gap assessment showing both executed documentation-led work and blocked runtime work.
