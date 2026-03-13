# Artifact Provenance: Q1 2026 CECL Allowance Review

Conventions:
- `[BANK INPUT]` means a file that was part of the pseudo-bank upload package.
- `[CODEX OUTPUT]` means a file generated during the review workflow or final report rendering.

## Bank-Uploaded Input Package
- E001 [BANK INPUT] `data/data_dictionary.csv`
  - Kind: dataset
  - Detail: CSV artifact with 13 data row(s)
  - Review use: Generated as part of the Codex review record for this case.
- E002 [BANK INPUT] `data/loan_level_snapshot.csv`
  - Kind: dataset
  - Detail: CSV artifact with 1200 data row(s)
  - Review use: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.
- E003 [BANK INPUT] `data/overlay_schedule.csv`
  - Kind: dataset
  - Detail: CSV artifact with 12 data row(s)
  - Review use: Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.
- E004 [BANK INPUT] `docs/control_process_note.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Generated as part of the Codex review record for this case.
- E005 [BANK INPUT] `docs/governance_minutes.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Generated as part of the Codex review record for this case.
- E006 [BANK INPUT] `docs/methodology.md`
  - Kind: document
  - Detail: Text artifact with 20 line(s)
  - Review use: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Forecast horizon sensitivity: Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.; Reversion speed sensitivity: Assess how severe-scenario reserve responds to longer reversion periods.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- E007 [BANK INPUT] `docs/model_overview.md`
  - Kind: document
  - Detail: Text artifact with 7 line(s)
  - Review use: Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- E008 [BANK INPUT] `docs/overlay_memo.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.; Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- E009 [BANK INPUT] `docs/prior_review_note.md`
  - Kind: document
  - Detail: Text artifact with 3 line(s)
  - Review use: Generated as part of the Codex review record for this case.
- E010 [BANK INPUT] `docs/scenario_assumptions.md`
  - Kind: document
  - Detail: Text artifact with 5 line(s)
  - Review use: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- E011 [BANK INPUT] `model/cecl_engine.py`
  - Kind: code
  - Detail: Text artifact with 177 line(s)
  - Review use: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.; Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Methodology and documentation alignment review: Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.
- E012 [BANK INPUT] `outputs/prior_baseline_reserve.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 1200 data row(s)
  - Review use: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Baseline reproduction: Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.
- E013 [BANK INPUT] `outputs/prior_scenario_summary.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 3 data row(s)
  - Review use: Generated as part of the Codex review record for this case.
- E014 [BANK INPUT] `outputs/prior_segment_reserves.csv`
  - Kind: packaged output table
  - Detail: CSV artifact with 12 data row(s)
  - Review use: Generated as part of the Codex review record for this case.
- E015 [BANK INPUT] `scenarios/adverse.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 8 data row(s)
  - Review use: Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.
- E016 [BANK INPUT] `scenarios/baseline.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 8 data row(s)
  - Review use: Package inventory and case classification: Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.; Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.
- E017 [BANK INPUT] `scenarios/severe.csv`
  - Kind: scenario table
  - Detail: CSV artifact with 8 data row(s)
  - Review use: Portfolio-level scenario reruns: Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.; Macro severity sensitivity: Test whether reserve responds proportionally to macro severity scaling.; Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.

## Codex-Generated Review Record
- E018 [CODEX OUTPUT] `outputs/support/discovery_summary.json`
  - Kind: json artifact
  - Detail: Text artifact with 81 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E019 [CODEX OUTPUT] `outputs/support/discovery_summary.md`
  - Kind: document
  - Detail: Text artifact with 31 line(s)
  - Purpose: Summarizes what Codex identified in the uploaded package during discovery.
- E020 [CODEX OUTPUT] `outputs/support/case_understanding.md`
  - Kind: document
  - Detail: Text artifact with 25 line(s)
  - Purpose: Records Codex's synthesized view of the CECL process, assumptions, and constraints.
- E021 [CODEX OUTPUT] `outputs/support/review_plan.md`
  - Kind: document
  - Detail: Text artifact with 27 line(s)
  - Purpose: Captures the planned review procedures before detailed execution.
- E022 [CODEX OUTPUT] `outputs/support/review_strategy.md`
  - Kind: document
  - Detail: Text artifact with 81 line(s)
  - Purpose: Explains why specific procedures were selected from the discovered evidence.
- E023 [CODEX OUTPUT] `outputs/support/executed_test_matrix.md`
  - Kind: document
  - Detail: Text artifact with 14 line(s)
  - Purpose: Registers which procedures were executed, blocked, and what each procedure concluded.
- E024 [CODEX OUTPUT] `outputs/support/executed_test_matrix.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 10 data row(s)
  - Purpose: Machine-readable form of the executed procedure register.
- E025 [CODEX OUTPUT] `outputs/support/evidence_map.md`
  - Kind: document
  - Detail: Text artifact with 73 line(s)
  - Purpose: Maps uploaded and derived artifacts to the procedures they supported.
- E026 [CODEX OUTPUT] `outputs/support/agentic_review_log.md`
  - Kind: document
  - Detail: Text artifact with 43 line(s)
  - Purpose: Readable stage-level summary of the intended Codex review flow.
- E027 [CODEX OUTPUT] `outputs/support/procedure_run_log.md`
  - Kind: document
  - Detail: Text artifact with 99 line(s)
  - Purpose: Chronological log of granular review actions and outputs.
- E028 [CODEX OUTPUT] `outputs/support/procedure_run_log.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 12 data row(s)
  - Purpose: Machine-readable chronology of granular review actions.
- E029 [CODEX OUTPUT] `outputs/support/evidence_excerpts.md`
  - Kind: document
  - Detail: Text artifact with 144 line(s)
  - Purpose: Collects raw excerpts from uploaded materials and review outputs used in the writeup.
- E030 [CODEX OUTPUT] `outputs/support/baseline_reproduction.json`
  - Kind: json artifact
  - Detail: Text artifact with 37 line(s)
  - Purpose: Stores baseline reproduction metrics used in the full-review conclusion.
- E031 [CODEX OUTPUT] `outputs/support/scenario_results.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 3 data row(s)
  - Purpose: Stores Codex-produced portfolio scenario rerun results.
- E032 [CODEX OUTPUT] `outputs/support/segment_reserve_comparison.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 4 data row(s)
  - Purpose: Segment-level reasonableness review: Test whether scenario ordering remains directionally sensible at the segment level.
- E033 [CODEX OUTPUT] `outputs/support/sensitivity_results.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 12 data row(s)
  - Purpose: Forecast horizon sensitivity: Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.; Reversion speed sensitivity: Assess how severe-scenario reserve responds to longer reversion periods.; Macro severity sensitivity: Test whether reserve responds proportionally to macro severity scaling.; Overlay magnitude sensitivity: Assess the reserve effect of removing or amplifying qualitative overlays.
- E034 [CODEX OUTPUT] `outputs/support/driver_bridge.csv`
  - Kind: generated review table
  - Detail: CSV artifact with 6 data row(s)
  - Purpose: Reserve driver bridge: Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.
- E035 [CODEX OUTPUT] `outputs/support/documentation_crosscheck.md`
  - Kind: document
  - Detail: Text artifact with 25 line(s)
  - Purpose: Stores documentation-versus-implementation and output cross-check observations.
- E036 [CODEX OUTPUT] `outputs/support/findings_register.json`
  - Kind: json artifact
  - Detail: Text artifact with 44 line(s)
  - Purpose: Registers findings, severity, and supporting evidence references.
- E037 [CODEX OUTPUT] `outputs/support/analysis_summary.json`
  - Kind: json artifact
  - Detail: Text artifact with 7 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E038 [CODEX OUTPUT] `outputs/support/evidence_ledger.json`
  - Kind: json artifact
  - Detail: Text artifact with 364 line(s)
  - Purpose: Generated as part of the Codex review record for this case.
- E039 [CODEX OUTPUT] `outputs/support/coverage_statement.md`
  - Kind: document
  - Detail: Text artifact with 13 line(s)
  - Purpose: States supported versus blocked review coverage.
- E040 [CODEX OUTPUT] `outputs/support/codex_trace.md`
  - Kind: document
  - Detail: Text artifact with 33 line(s)
  - Purpose: Readable execution trace of discovery, planning, execution, and synthesis.

## Uploaded Package Tree
```text
input_package/
  data/
    data_dictionary.csv
    loan_level_snapshot.csv
    overlay_schedule.csv
  docs/
    control_process_note.md
    governance_minutes.md
    methodology.md
    model_overview.md
    overlay_memo.md
    prior_review_note.md
    scenario_assumptions.md
  model/
    cecl_engine.py
  outputs/
    prior_baseline_reserve.csv
    prior_scenario_summary.csv
    prior_segment_reserves.csv
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
    baseline_reproduction.json
    case_understanding.md
    codex_trace.md
    coverage_statement.md
    discovery_summary.json
    discovery_summary.md
    documentation_crosscheck.md
    driver_bridge.csv
    evidence_excerpts.md
    evidence_ledger.json
    evidence_map.md
    executed_test_matrix.csv
    executed_test_matrix.md
    findings_register.json
    procedure_run_log.csv
    procedure_run_log.md
    review_plan.md
    review_strategy.md
    scenario_results.csv
    segment_reserve_comparison.csv
    sensitivity_results.csv
```
