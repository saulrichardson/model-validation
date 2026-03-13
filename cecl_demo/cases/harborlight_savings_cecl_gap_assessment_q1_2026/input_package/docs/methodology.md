# CECL Gap Assessment Methodology

**Bank:** Harborlight Savings  
**Engagement:** Q1 2026 CECL Readiness Gap Assessment  
**Scope:** Consumer and real-estate portfolio reserve process  
**Workflow:** Documentation-led gap assessment (non-execution)

## 1. Objective
Assess the design and documentation completeness of Harborlight Savings' CECL methodology, including governance, data, segmentation, forecast/reversion approach, scenario framework, overlays, and reporting artifacts. The objective is to identify gaps that prevent a defensible implementation and to define remediation actions and evidence requirements.

## 2. Review Approach (Documentation-Led)
The review is performed using artifacts provided by Management (policies, model documentation, sample reports, scenario decks, overlay memos, and reserve bridge narratives). **No independent model execution, reserve engine re-performance, or code review** is performed under this package due to missing runtime evidence and lineage artifacts.

### 2.1 Workstreams
1. **Methodology design & CECL accounting alignment** (ASC 326, reasonable and supportable forecast, reversion, data treatment).
2. **Segmentation & pooling** (documented segments, output segments, reconciliation to GL/FR Y-9C call-report lines as applicable).
3. **Scenario framework** (baseline/adverse/severe, scenario selection, narrative alignment, and variable definitions).
4. **Forecast & reversion mechanics** (term structure, horizon, reversion method).
5. **Overlay framework** (governance, caps/limits, quantification, traceability to reserve bridge).
6. **Controls & governance** (model risk governance, approvals, change control, monitoring).

## 3. Key Methodology Specifications (Per Documentation)
### 3.1 Forecast and Reversion Horizons
- **Reasonable & supportable forecast horizon:** **8 quarters**.
- **Reversion period:** **4 quarters**.
- **Total modeled horizon:** life-of-loan, with macro-driven path applied through forecast and reversion periods.

> Note: This methodology states 8+4 quarters as the implemented horizon in the CECL framework documentation.

### 3.2 Segmentation (Documented)
Documented segments used for CECL estimation and reporting:
- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial

### 3.3 Scenario Set and Variables
Three scenarios are included:
- Baseline
- Adverse
- Severe

Variables referenced in the scenario package:
- Unemployment rate
- GDP growth
- House price growth
- CRE price growth
- Prime rate

Scenario paths provided cover **2026Q1-2027Q2** (6 quarters) for each scenario.

### 3.4 Overlay Policy Constraint (Documented)
- **Documented overlay cap:** **6.0 bps** (portfolio-level cap as described in the overlay policy section).

## 4. Testing Procedures and Evidence Standards
### 4.1 Design Assessment Procedures
- Trace each major methodological choice (segmentation, horizons, scenarios, reversion) to a controlled document (policy, model methodology, governance minutes).
- Confirm internal consistency between: model card, methodology paper, scenario narrative/deck, overlay memo, and management reporting.
- Identify required operational controls for production use (data lineage, model run logs, change control).

### 4.2 Execution-Based Procedures (Not Performed)
The following procedures are **explicitly out of scope** for this package due to missing evidence:
- Reserve engine re-run / independent calculation
- Data lineage reconciliation from source systems to model inputs
- Parameter estimation re-performance
- End-to-end backtesting in production-equivalent environment

## 5. Deliverables
- Methodology and model overview summaries
- Scenario assumptions appendix (numeric paths and narrative observations)
- Overlay memo (documentation-led critique and required remediation)
- Prior review note (blocking items and contradictions)
- Governance minutes (non-execution limitation noted)
- Evidence request log (open items and due dates)
- Gap tracker (issues, severity, owners, and remediation plan)
