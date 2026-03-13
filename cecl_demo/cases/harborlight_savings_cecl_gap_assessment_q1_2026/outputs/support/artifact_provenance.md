# Artifact Provenance: Q1 2026 CECL Readiness Gap Assessment

Conventions:
- `[BANK INPUT]` means a file that was part of the pseudo-bank upload package.
- `[CODEX OUTPUT]` means a file generated during the review workflow or final report rendering.

## Bank-Uploaded Input Package
- E001 [BANK INPUT] `data/data_dictionary.csv`
  - Kind: dataset
  - Detail: CSV artifact with 13 data row(s)
  - Review use: Generated as part of the Codex review record for this case.
- E002 [BANK INPUT] `data/sample_rollforward.csv`
  - Kind: dataset
  - Detail: CSV artifact with 4 data row(s)
  - Review use: Generated as part of the Codex review record for this case.
- E003 [BANK INPUT] `docs/evidence_request_log.md`
  - Kind: document
  - Detail: Text artifact with 6 line(s)
  - Review use: Package inventory and coverage classification: Determine whether the upload supports execution-based review or only a documentation-led assessment.; Execution readiness and lineage assessment: Establish whether the package includes the artifacts required for baseline reproduction and scenario reruns.; Baseline reproduction: Reproduce the baseline reserve from the implementation and baseline scenario.; Evidence request and remediation planning: Translate identified blockers and inconsistencies into a prioritized request list for a future execution-based review.
- E004 [BANK INPUT] `docs/gap_tracker.md`
  - Kind: document
  - Detail: Text artifact with 7 line(s)
  - Review use: Package inventory and coverage classification: Determine whether the upload supports execution-based review or only a documentation-led assessment.; Execution readiness and lineage assessment: Establish whether the package includes the artifacts required for baseline reproduction and scenario reruns.; Scenario reruns and sensitivity testing: Rerun scenarios and challenge reserve sensitivity to key assumptions.
- E005 [BANK INPUT] `docs/governance_minutes.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Execution readiness and lineage assessment: Establish whether the package includes the artifacts required for baseline reproduction and scenario reruns.
- E006 [BANK INPUT] `docs/methodology.md`
  - Kind: document
  - Detail: Text artifact with 9 line(s)
  - Review use: Horizon and reversion consistency review: Test whether documented forecast and reversion descriptions reconcile across methodology, model overview, and supplied scenario files.; Segment taxonomy reconciliation: Compare documented segment definitions to the segment structure in the provided reserve outputs.
- E007 [BANK INPUT] `docs/model_overview.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Horizon and reversion consistency review: Test whether documented forecast and reversion descriptions reconcile across methodology, model overview, and supplied scenario files.; Segment taxonomy reconciliation: Compare documented segment definitions to the segment structure in the provided reserve outputs.
- E008 [BANK INPUT] `docs/overlay_memo.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Overlay magnitude reconciliation: Compare documented overlay posture to the reserve bridge included in the package.
- E009 [BANK INPUT] `docs/prior_review_note.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Generated as part of the Codex review record for this case.
- E010 [BANK INPUT] `docs/scenario_assumptions.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Scenario narrative versus table comparison: Test whether the severe scenario narrative matches the supplied numeric scenario path.; Horizon and reversion consistency review: Test whether documented forecast and reversion descriptions reconcile across methodology, model overview, and supplied scenario files.
- E011 [BANK INPUT] `outputs/provided_overlay_bridge.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 4 data row(s)
  - Review use: Overlay magnitude reconciliation: Compare documented overlay posture to the reserve bridge included in the package.
- E012 [BANK INPUT] `outputs/provided_reserve_summary.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 3 data row(s)
  - Review use: Package inventory and coverage classification: Determine whether the upload supports execution-based review or only a documentation-led assessment.; Baseline reproduction: Reproduce the baseline reserve from the implementation and baseline scenario.
- E013 [BANK INPUT] `outputs/provided_segment_reserves.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 12 data row(s)
  - Review use: Segment taxonomy reconciliation: Compare documented segment definitions to the segment structure in the provided reserve outputs.
- E014 [BANK INPUT] `scenarios/adverse.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 6 data row(s)
  - Review use: Scenario narrative versus table comparison: Test whether the severe scenario narrative matches the supplied numeric scenario path.; Scenario reruns and sensitivity testing: Rerun scenarios and challenge reserve sensitivity to key assumptions.
- E015 [BANK INPUT] `scenarios/baseline.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 6 data row(s)
  - Review use: Scenario reruns and sensitivity testing: Rerun scenarios and challenge reserve sensitivity to key assumptions.
- E016 [BANK INPUT] `scenarios/severe.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 6 data row(s)
  - Review use: Scenario narrative versus table comparison: Test whether the severe scenario narrative matches the supplied numeric scenario path.; Scenario reruns and sensitivity testing: Rerun scenarios and challenge reserve sensitivity to key assumptions.

## Codex-Generated Review Record
- E017 [CODEX OUTPUT] `outputs/support/discovery_summary.json`
  - Kind: json artifact
  - Detail: Text artifact with 80 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E018 [CODEX OUTPUT] `outputs/support/discovery_summary.md`
  - Kind: document
  - Detail: Text artifact with 31 line(s)
  - Purpose: Summarizes what Codex identified in the uploaded package during discovery.
- E019 [CODEX OUTPUT] `outputs/support/case_understanding.md`
  - Kind: document
  - Detail: Text artifact with 27 line(s)
  - Purpose: Records Codex's synthesized view of the CECL process, assumptions, and constraints.
- E020 [CODEX OUTPUT] `outputs/support/review_plan.md`
  - Kind: document
  - Detail: Text artifact with 21 line(s)
  - Purpose: Captures the planned review procedures before detailed execution.
- E021 [CODEX OUTPUT] `outputs/support/review_strategy.md`
  - Kind: document
  - Detail: Text artifact with 75 line(s)
  - Purpose: Explains why specific procedures were selected from the discovered evidence.
- E022 [CODEX OUTPUT] `outputs/support/executed_test_matrix.md`
  - Kind: document
  - Detail: Text artifact with 13 line(s)
  - Purpose: Registers which procedures were executed, blocked, and what each procedure concluded.
- E023 [CODEX OUTPUT] `outputs/support/executed_test_matrix.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 9 data row(s)
  - Purpose: Machine-readable form of the executed procedure register.
- E024 [CODEX OUTPUT] `outputs/support/evidence_map.md`
  - Kind: document
  - Detail: Text artifact with 78 line(s)
  - Purpose: Maps uploaded and derived artifacts to the procedures they supported.
- E025 [CODEX OUTPUT] `outputs/support/agentic_review_log.md`
  - Kind: document
  - Detail: Text artifact with 43 line(s)
  - Purpose: Readable stage-level summary of the intended Codex review flow.
- E026 [CODEX OUTPUT] `outputs/support/procedure_run_log.md`
  - Kind: document
  - Detail: Text artifact with 83 line(s)
  - Purpose: Chronological log of granular review actions and outputs.
- E027 [CODEX OUTPUT] `outputs/support/procedure_run_log.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 10 data row(s)
  - Purpose: Machine-readable chronology of granular review actions.
- E028 [CODEX OUTPUT] `outputs/support/evidence_excerpts.md`
  - Kind: document
  - Detail: Text artifact with 98 line(s)
  - Purpose: Collects raw excerpts from uploaded materials and review outputs used in the writeup.
- E029 [CODEX OUTPUT] `outputs/support/documentation_crosscheck.md`
  - Kind: document
  - Detail: Text artifact with 23 line(s)
  - Purpose: Stores documentation-versus-implementation and output cross-check observations.
- E030 [CODEX OUTPUT] `outputs/support/findings_register.json`
  - Kind: json artifact
  - Detail: Text artifact with 43 line(s)
  - Purpose: Registers findings, severity, and supporting evidence references.
- E031 [CODEX OUTPUT] `outputs/support/analysis_summary.json`
  - Kind: json artifact
  - Detail: Text artifact with 5 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E032 [CODEX OUTPUT] `outputs/support/evidence_ledger.json`
  - Kind: json artifact
  - Detail: Text artifact with 346 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E033 [CODEX OUTPUT] `outputs/support/coverage_statement.md`
  - Kind: document
  - Detail: Text artifact with 15 line(s)
  - Purpose: States supported versus blocked review coverage.
- E034 [CODEX OUTPUT] `outputs/support/evidence_request_list.md`
  - Kind: document
  - Detail: Text artifact with 6 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E035 [CODEX OUTPUT] `outputs/support/provided_reserve_summary.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 3 data row(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E036 [CODEX OUTPUT] `outputs/support/provided_segment_reserves.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 12 data row(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E037 [CODEX OUTPUT] `outputs/support/provided_overlay_bridge.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 4 data row(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E038 [CODEX OUTPUT] `outputs/support/codex_trace.md`
  - Kind: document
  - Detail: Text artifact with 27 line(s)
  - Purpose: Readable execution trace of discovery, planning, execution, and synthesis.

## Uploaded Package Tree
```text
input_package/
  data/
    data_dictionary.csv
    sample_rollforward.csv
  docs/
    evidence_request_log.md
    gap_tracker.md
    governance_minutes.md
    methodology.md
    model_overview.md
    overlay_memo.md
    prior_review_note.md
    scenario_assumptions.md
  outputs/
    provided_overlay_bridge.csv
    provided_reserve_summary.csv
    provided_segment_reserves.csv
  scenarios/
    adverse.csv
    baseline.csv
    severe.csv
```

## Codex Output Tree
```text
outputs/
  support/
    agentic_review_log.md
    analysis_summary.json
    case_understanding.md
    codex_trace.md
    coverage_statement.md
    discovery_summary.json
    discovery_summary.md
    documentation_crosscheck.md
    evidence_excerpts.md
    evidence_ledger.json
    evidence_map.md
    evidence_request_list.md
    executed_test_matrix.csv
    executed_test_matrix.md
    findings_register.json
    procedure_run_log.csv
    procedure_run_log.md
    provided_overlay_bridge.csv
    provided_reserve_summary.csv
    provided_segment_reserves.csv
    review_plan.md
    review_strategy.md
```
