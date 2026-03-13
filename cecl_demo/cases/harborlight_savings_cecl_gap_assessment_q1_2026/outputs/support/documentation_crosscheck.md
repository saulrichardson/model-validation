# Documentation Cross-Check

## Execution readiness
The package supports narrative and prior-output review only. It does not support baseline reproduction or scenario reruns.

- Evidence: docs/evidence_request_log.md, docs/gap_tracker.md, outputs/provided_reserve_summary.csv
- No reserve engine was supplied.
- No reproducibility notebook or execution runbook was supplied.

## Scenario definition review
The scenario narrative and numeric scenario tables are not perfectly aligned.

- Evidence: docs/scenario_assumptions.md, scenarios/adverse.csv, scenarios/severe.csv
- Quarters with severe house-price growth less severe than adverse: 4

## Segment and overlay reconciliation
The documented segment structure and overlay posture do not reconcile cleanly to the supplied reserve outputs.

- Evidence: docs/methodology.md, docs/model_overview.md, docs/overlay_memo.md, outputs/provided_segment_reserves.csv, outputs/provided_overlay_bridge.csv
- Documented segments: 5
- Output segments: 4
- Documented overlay cap: 6.0 bps
- Provided overlay cap: 18.0 bps
