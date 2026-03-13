# Control Process Note - CECL Reserve Production and Reproducibility (Q1 2026)

## Purpose
This control note describes Redwood Regional Bank's practices for reproducible CECL reserve production, change management, and reporting controls supporting the Q1 2026 allowance process.

## Reserve production controls
### 1) Data controls and lineage
- Loan-level input files are sourced from the servicing and general ledger systems and are subject to reconciliation checks (record counts, total balances, and key field completeness).
- Segment assignment logic is controlled through standard mapping tables maintained by Credit Risk Analytics.
- Exceptions (missing FICO/LTV/DTI/DSCR, out-of-range fields) are logged and resolved or defaulted per established rules, with counts reported in the quarter-end package.

### 2) Model run configuration and parameter governance
- Scenario inputs (baseline/adverse/severe) are stored as versioned quarterly tables and locked for quarter-end production after governance review.
- Key model parameters (segment intercepts, LGD bases, macro sensitivities) are maintained in controlled parameter files with approval history.
- Run settings (forecast and reversion configuration, scenario selection, overlay tables) are intended to be captured in a run manifest to support reruns.

### 3) Reproducibility expectations
- Production runs are designed to be reproducible from:
  1. input loan tape snapshot,
  2. scenario table version,
  3. parameter set version,
  4. overlay table version, and
  5. run configuration settings.
- Independent rerun testing is performed on a sample basis to confirm stable outputs when inputs are unchanged (review sample size reference: 1,200 loans; RNG seed: 23).

### 4) Overlay controls
- Overlays are maintained in a segment-by-scenario table with documented rationale and an approval log.
- The documented overlay cap is monitored as part of quarter-end review; exceptions require documented governance acknowledgement.

## Reporting and review controls
### 1) Standard reporting package
Quarter-end outputs include:
- Segment allowance rates and totals
- Scenario results and key driver summaries
- Quarter-over-quarter attribution
- Overlay detail (bps and dollar impact)
- Reasonableness checks (scenario ordering, concentration movements, outlier exposures)

### 2) Review and sign-off
- Credit Risk Analytics prepares the reserve package and performs first-line validation checks.
- Finance performs reconciliation to general ledger and validates reporting consistency.
- MRM provides second-line challenge and documents key observations and required actions.
- Final approvals are recorded in CECL Governance Committee minutes and retained with the quarter-end archive.

## Known control enhancements requested (Q1 2026)
- **Run manifest completeness:** Add an explicit configuration extract showing the forecast horizon and reversion settings used by the production engine to facilitate reconciliation to documented methodology.
- **Scenario ordering control:** Add an automated check highlighting any segment where severe results are more favorable than adverse, requiring documented rationale and approval.

## Record retention
All quarter-end artifacts (input snapshots, scenario versions, parameter files, overlay tables, run logs, outputs, and governance approvals) are retained in accordance with the bank's record retention schedule and are available for audit and regulatory review.
