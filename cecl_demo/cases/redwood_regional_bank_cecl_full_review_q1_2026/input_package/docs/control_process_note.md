# Control Process Note - CECL Reserve Engine Reproducibility, Change Control, and Reporting (Q1 2026)

## 1. Purpose
This note documents key controls supporting reproducibility, traceability, and reporting integrity for the Q1 2026 CECL allowance production and review cycle.

## 2. Production run reproducibility
### 2.1 Run inputs and parameter archiving
- A quarter-specific run folder is maintained for the CECL production cycle, containing:
  - loan-level input extracts used for the run,
  - macro scenario files (Baseline/Adverse/Severe),
  - segment mapping tables,
  - model parameter tables (segment intercepts, base LGDs, macro sensitivities),
  - overlay schedule inputs.
- Inputs are stored with read-only permissions post-close and retained per record retention standards.

### 2.2 Configuration management
- The reserve engine is executed using a configuration file defining:
  - scenario selection,
  - forecast horizon and reversion settings,
  - segment definitions and mapping logic,
  - overlay toggles and bps schedules.
- Configuration files are version-controlled, and the configuration used for the production run is archived with the run outputs.

### 2.3 Deterministic sampling and testing
- For model testing and benchmarking, an analytic sample of **1,200 loans** is used.
- Sampling is executed deterministically using **rng_seed = 23** to support repeatable stratified analyses and consistent QA comparisons across reruns.

## 3. Data quality controls
- Input extract reconciliation: record counts and aggregate balances are reconciled to the general ledger and sub-ledger reports.
- Segment mapping checks: balances by segment are tied to portfolio reporting with documented variance explanations.
- Field-level reasonableness: key drivers (FICO, risk rating, LTV, DSCR, utilization, term) are reviewed for missingness, range violations, and outliers.

## 4. Calculation controls and reasonableness checks
- Scenario ordering checks are performed at total portfolio and segment level.
- Quarter-over-quarter change analysis is performed for each segment with drivers documented (mix shift, rating migration, macro updates, overlay changes).
- Overlay application checks confirm that bps inputs are applied to the correct segment and scenario and are included in final rollups.

## 5. Reporting and governance controls
- Standard close package includes:
  - scenario decks,
  - segment results,
  - overlay schedule and memo,
  - reconciliation exhibits and sign-offs.
- Committee materials are prepared by the CECL Program Manager and reviewed by Finance and Credit Risk Analytics prior to distribution.
- Final ACL figures are locked after governance approval; any post-approval change requires documented justification and re-approval.

## 6. Change management
- Model or configuration changes (including forecast horizon/reversion settings, scenario inputs, segment mapping, or overlay framework changes) require:
  - a change request ticket,
  - documented testing evidence (including benchmarking to prior quarter),
  - approval by Model Owner and Finance,
  - review by Model Risk Management where applicable,
  - and retention of pre-/post-change comparison outputs.

## 7. Known control considerations for this cycle
- The documented macro horizon/reversion assumption is **4 quarters forecast and 4 quarters linear reversion**. As part of ongoing control enhancement, the team will strengthen evidence capture (configuration snapshot and run log excerpts) demonstrating that production settings align with documentation or are formally approved if exceptions exist.

## 8. Control attestation (internal)
The preparer attests that Q1 2026 production inputs, configuration artifacts, and output files were archived in accordance with standard close procedures, and that key reconciliations and reasonableness checks described above were completed and retained for audit and model risk review.
