# Prior Review Note (Blocking Items and Contradictions)

**Bank:** Harborlight Savings  
**Engagement:** Harborlight Savings CECL Gap Assessment (Q1 2026)  
**Prepared for:** Internal documentation-led review upload package

## 1. Purpose
This note summarizes issues identified during initial intake and document review that (a) block execution-based testing and (b) indicate material inconsistencies across CECL artifacts.

## 2. Blocking Items (Preventing Execution-Based Review)
1. **Reserve engine evidence not provided**
   - Missing: end-to-end run package (inputs, configuration, run logs, output files).
   - Missing: model execution controls (job schedule evidence, rerun reproducibility, exception handling).
2. **Data lineage evidence not provided**
   - Missing: lineage from core systems to CECL input datasets (field-level mapping, transformations, QC checks).
   - Missing: reconciliation of balances/exposures to GL/subledger.

**Impact:** Review is limited to non-execution documentation assessment and cannot provide re-performance assurance.

## 3. Documented vs. Evidenced Contradictions
1. **Forecast and reversion horizons**
   - Methodology documentation: **8-quarter forecast** and **4-quarter reversion**.
   - Model card: **6-quarter forecast** and **2-quarter reversion**.
   - Scenario data provided: **6 quarters** for each scenario.

2. **Segmentation mismatch**
   - Documented segments include **CRE Owner Occupied**.
   - Output segments provided exclude a corresponding `cre_owner_occupied` output.
   - Reserve outputs list: `residential_mortgage`, `heloc`, `cre_investor`, `commercial_and_industrial`.

3. **Scenario narrative vs. numeric severe path**
   - Severe numeric scenario: peak stress in 2026Q3 with partial improvement thereafter.
   - Scenario narrative references (per management summary): deterioration "through 2026 year-end," not aligned to numeric trajectory.

4. **Overlay cap vs. overlay magnitude**
   - Documented overlay cap: **6.0 bps**.
   - Provided overlays: **12-18 bps** by segment.

## 4. Immediate Next Steps (Evidence Requests)
- Provide reserve engine run artifacts and execution controls.
- Provide end-to-end data lineage and reconciliation.
- Provide segment mapping between documented segments and output segments.
- Provide scenario governance pack (narrative, selection rationale) and confirm horizon.
- Provide overlay calculation memo(s), approval evidence, and any cap exception documentation.

## 5. Risk Statement
Until the blocking items and contradictions are resolved, Harborlight Savings faces elevated risk of (i) inconsistent CECL methodology application, (ii) inadequate governance support for overlays, and (iii) inability to demonstrate repeatability and control in financial reporting.
