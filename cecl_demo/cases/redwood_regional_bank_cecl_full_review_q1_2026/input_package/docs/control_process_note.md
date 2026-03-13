# Control Process Note - CECL Production, Reproducibility, and Reporting

## Purpose
This note summarizes key controls supporting reproducibility, data lineage, and reporting integrity for Redwood Regional Bank's CECL production process for the Q1 2026 allowance cycle.

## End-to-end process overview
1. **Data extraction and staging**
   - Loan-level snapshots are extracted from source systems as of the quarter-end cut-off.
   - Standard validation checks are performed (record counts by segment, missing critical fields, out-of-range attribute checks).

2. **Segmentation and attribute preparation**
   - Loans are assigned to CECL segments using documented business rules.
   - Key risk attributes (e.g., FICO, LTV, DTI/DSCR, utilization, remaining term, risk rating) are standardized and audited for completeness.

3. **Scenario ingestion**
   - Baseline/Adverse/Severe macroeconomic paths are loaded with quarter identifiers.
   - A control check reconciles the loaded values to the approved scenario package (unemployment, GDP growth, house price growth, CRE price growth, prime rate).

4. **Reserve engine execution**
   - The CECL engine is executed using version-controlled configuration files.
   - Run metadata captured includes: run date/time, configuration version, scenario set identifier, and any override flags.

5. **Overlay application and consolidation**
   - Overlays are applied as bps adjustments by segment and scenario per management approval.
   - A post-application reconciliation ties the overlay inputs to the final allowance output tables.

6. **Reporting and financial close**
   - Segment outputs roll to portfolio totals and are reconciled to general ledger and CECL reporting packages.
   - Variance explanations are documented for quarter-over-quarter changes.

## Reproducibility controls
- **Deterministic sampling/testing:** Review testing uses a fixed seed (**rng_seed = 23**) for sampling and repeatable diagnostics.
- **Configuration management:** Engine parameter files (including horizon settings) are maintained under controlled access with change logging.
- **Run record retention:** Inputs (loan snapshot, scenarios, overlay schedules) and outputs (segment ECL, allowance totals, reasonableness checks) are archived for the quarter.

## Key production checks
- **Completeness and integrity checks:**
  - Record counts by segment reconcile to servicing/GL reports.
  - Missing-value thresholds and outlier rules produce exception reports.
- **Reasonableness checks:**
  - Scenario ordering checks at segment level (baseline ≤ adverse ≤ severe expected unless explained).
  - Sensitivity checks for key macro drivers (unemployment, house price growth, CRE price growth).
- **Overlay validation:**
  - Overlay tables reconciled to governance-approved values.
  - Policy constraints (e.g., documented overlay cap of **5.0 bps**) are reviewed and exceptions are escalated through the issue log.

## Issue management and escalation
- Control exceptions (e.g., horizon setting discrepancies, overlay cap variances, unusual scenario ordering) are documented in the CECL issue log.
- Items with potential financial reporting impact are escalated to the CECL Governance Committee and tracked to closure with accountable owners and due dates.

## Auditability and evidence
- The quarter-end package retains:
  - Source extracts and transformation logs
  - Scenario approval package and loaded scenario files
  - Engine configuration and run logs
  - Overlay approvals and applied overlay tables
  - Reconciliation workpapers and variance explanations

## Known control focus area (Q1 2026)
- Management identified the need to strengthen explicit control evidence that production horizon settings align to CECL policy documentation (documented **4-quarter forecast / 4-quarter reversion**) and to ensure any interim deviations are approved, quantified, and clearly disclosed in reporting.
