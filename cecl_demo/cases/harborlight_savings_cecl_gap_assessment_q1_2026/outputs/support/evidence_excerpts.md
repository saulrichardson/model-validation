# Evidence Excerpts: Q1 2026 CECL Readiness Gap Assessment

The excerpts below are short raw snippets from uploaded materials or generated review artifacts.

## [BANK INPUT] `docs/methodology.md`
Documented forecast, reversion, segmentation, and missing-runtime boundary used in the gap assessment.

```text
# CECL Methodology

The documented CECL process for Harborlight Savings describes a 8-quarter reasonable-and-supportable period with 4 reversion quarters. Documentation states the reserve process covers the following segments:

- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial
```

## [BANK INPUT] `docs/scenario_assumptions.md`
Numeric scenario horizon and narrative-alignment discussion showing the mismatch between documented and provided scenario depth.

```text
# Scenario Assumptions

Severe is described as a uniformly harsher path than adverse across the full review horizon. Management expects house prices and unemployment to remain materially worse under severe in every quarter reviewed by governance.
```

## [BANK INPUT] `docs/overlay_memo.md`
Overlay cap language and segment overlay values that Codex challenged against the provided reserve bridge.

```text
# Overlay Memo

Qualitative overlay is described as modest and capped at 6.0 bps, pending additional governance evidence.
```

## [BANK INPUT] `docs/evidence_request_log.md`
Bank-supplied evidence request log showing the package's own acknowledgement of missing runtime and lineage support.

```text
# Evidence Request Log

- Provide the reserve engine or reproducibility notebook used to produce the supplied reserve outputs.
- Provide execution lineage linking the reserve outputs to the reviewed scenario definitions.
- Reconcile segment definitions across methodology, overview, and reserve outputs.
- Quantify qualitative overlay by segment and scenario.
```

## [CODEX OUTPUT] `outputs/support/coverage_statement.md`
Codex-generated coverage boundary showing which procedures were supported and which were blocked.

```text
# Coverage Statement

The package contains useful CECL documentation and output snapshots, but it does not contain the implementation artifacts needed for execution-based validation.

## Supported Work
- Discovery and evidence sufficiency review
- Scenario-definition consistency review
- Provided-output reconciliation
- Overlay documentation review

## Blocked Work
- Baseline reproduction
- Scenario reruns against a reserve engine
- Sensitivity testing on implementation assumptions
- Model-code review
```

## [CODEX OUTPUT] `outputs/support/documentation_crosscheck.md`
Codex-generated documentation cross-check summarizing execution blockers, scenario inconsistency, and segment-overlay reconciliation issues.

```text
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
```
