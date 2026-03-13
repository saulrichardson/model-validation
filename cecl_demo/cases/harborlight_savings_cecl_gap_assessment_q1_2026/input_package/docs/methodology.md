# CECL Gap Assessment Methodology

**Bank:** Harborlight Savings  
**Engagement:** Q1 2026 CECL Readiness Gap Assessment  
**Scope:** Consumer and real-estate portfolio reserve process  
**Workflow:** Documentation-led gap assessment (non-execution)

## 1. Objective
Assess the current-state CECL design and documentation sufficiency relative to internal policy expectations and supervisory-ready practices, focusing on:
- Methodology design (segmentation, loss estimation approach, scenario framework)
- Governance and control expectations (model risk management, change control, overlays)
- Data and lineage readiness (inputs, transformations, reconciliations)
- Operational readiness for quarterly close (repeatability, evidence, sign-offs)

This package is designed to support a **documentation-led review**; execution-based testing is explicitly out of scope pending availability of reserve engine artifacts and lineage evidence.

## 2. Review Approach
### 2.1 Workstreams
1) **Design & Conceptual Soundness**  
   Review model design, segmentation logic, and expected behavior under macro scenarios.

2) **Scenario Framework & Forecasting**  
   Review scenario definitions, governance of scenario selection/weights, and mapping of macro variables to segment-level risk drivers.

3) **Operational Controls & Close Process**  
   Review process flow, roles/responsibilities, change management, and evidence standards.

4) **Overlays & Qualitative Adjustments**  
   Review overlay policy/limits, rationale, calculation method, and auditability.

5) **Data, Lineage, and Reconciliation**  
   Review data sourcing, transformations, lineage documentation, and tie-outs to GL/loan systems.

### 2.2 Evidence Standards (Documentation-led)
We evaluate whether documentation is:
- **Complete:** sufficient to support independent understanding and challenge
- **Consistent:** no unresolved contradictions across model card, methodology, and process narratives
- **Traceable:** inputs/outputs and decisions tie to artifacts with dates, owners, and approvals
- **Repeatable:** documented steps enable consistent quarter-over-quarter execution

### 2.3 Scenario Horizon & Reversion (Documented)
Per methodology documentation reviewed, the CECL scenario framework is described as:
- **Forecast horizon:** **8 quarters** of explicit macroeconomic forecast
- **Reversion horizon:** **4 quarters** of linear reversion to long-run assumptions

**Note:** This section reflects the **methodology narrative** currently on file; identified discrepancies with the model card are logged as gaps.

### 2.4 Segmentation Basis (Documented)
The segmentation framework described in documentation comprises the following segments:
- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial

Segmentation is expected to be consistently applied across:
- Data extracts and population definitions
- Model estimation and calibration artifacts
- Reserve output reporting and management review packages

### 2.5 Overlay Framework (Documented)
The methodology indicates a **portfolio overlay cap of 6.0 bps** (documentation states cap is applied to limit qualitative adjustments absent formal model redevelopment).

This package evaluates:
- Whether overlay governance exists (owner, triggers, approvals)
- Whether overlay size is reconcilable to the reserve bridge and segment-level movements
- Whether documentation accurately reflects overlay magnitude and application

## 3. Deliverables in this Upload Package
- Methodology summary (this document)
- Model overview / model card summary
- Scenario assumptions (numeric paths and narrative alignment assessment)
- Overlay memo (documentation vs provided bridge outputs)
- Prior review note (legacy items and carry-forward issues)
- Governance minutes (non-execution review limitation and decisions)
- Evidence request log (working log)
- Gap tracker (working log)

## 4. Limitations
- **No reserve engine execution testing** performed (no runtime logs, run IDs, parameter files, or reproducible reserve runs provided).
- **No end-to-end data lineage testing** performed (no source-to-target mappings, transformation code, or reconciliations to servicing/GL provided).

As a result, conclusions are limited to **documentation adequacy and design consistency**; effectiveness of controls and numerical accuracy cannot be confirmed at this stage.
