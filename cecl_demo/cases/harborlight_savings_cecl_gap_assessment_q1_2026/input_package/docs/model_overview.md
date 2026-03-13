# Model Overview (Current-State Summary)

**Bank:** Harborlight Savings  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Product context:** Consumer and real-estate portfolio reserve process

## 1. Model Purpose and Use
The CECL reserve process is intended to estimate the allowance for credit losses (ACL) for:
- Consumer real estate (Residential Mortgage, HELOC)
- Commercial real estate (CRE)
- Commercial and industrial (C&I)

Primary use: quarterly financial reporting and management reporting; secondary use: risk monitoring and portfolio oversight.

## 2. Model Type and Core Approach
Based on the model card summary provided for review, the current approach is described as:
- **Segment-level loss estimation** using a macro-conditioned framework, producing lifetime loss estimates aggregated to the ACL.
- Model outputs are produced by segment and rolled up for management review.

**Note on horizon (per model card):**
- **Forecast horizon:** **6 quarters** explicit forecast
- **Reversion horizon:** **2 quarters** reversion to long-run

This is not consistent with the methodology narrative indicating 8-quarter forecast and 4-quarter reversion.

## 3. Segmentation & Output Structure
### 3.1 Documented segments (policy/methodology)
- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial

### 3.2 Output segments (reserve outputs provided)
Reserve outputs provided for this gap assessment are organized as:
- `residential_mortgage`
- `heloc`
- `cre_investor`
- `commercial_and_industrial`

**Observed reconciliation issue:** `CRE Owner Occupied` appears in documentation but is not present as a distinct output segment. It is not evidenced whether this population is:
- mapped into `cre_investor`,
- mapped into another output segment, or
- excluded from modeled outputs and handled via overlay/manual process.

## 4. Scenario Framework (As Implemented per Model Card)
The model card indicates three scenarios are supported (Baseline, Adverse, Severe) with scenario application at the segment level.

**Weights and governance:** Not evidenced in the materials provided (no approved scenario weight memo, committee decision, or quarterly weight history provided).

## 5. Key Inputs and Data Dependencies (High-level)
Inputs referenced in documentation include:
- Loan-level attributes and performance history (originations, balances, delinquency, charge-off/recovery)
- Segment identifiers
- Macroeconomic variables: unemployment, GDP growth, house price growth, CRE price growth, prime rate

**Data lineage and transformations:** Not evidenced end-to-end. No source-to-target mapping, transformation logic, or reconciliations were provided sufficient to confirm completeness and accuracy.

## 6. Controls and Governance (As Observed)
- Model ownership and ongoing monitoring roles are referenced but not fully supported by current meeting minutes and approval artifacts.
- Change control evidence (versioning, parameter approvals, implementation sign-off) is not present.

## 7. Known Constraints for This Review
- Execution-based review is blocked due to missing reserve engine artifacts (run package, run IDs, parameter files, and runtime logs).
- Validation results and performance monitoring packages (backtesting, benchmarking) were not provided for this cycle.
