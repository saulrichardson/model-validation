# Prior Review Note (Carry-forward Items and Context)

**Bank:** Harborlight Savings  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment

## 1. Background
This note summarizes prior themes that have been previously raised internally (risk management and finance working sessions) and remain relevant to the Q1 2026 documentation-led gap assessment.

## 2. Carry-forward Themes
### 2.1 Execution evidence and reproducibility
- Prior discussions indicated a target-state "reserve engine" solution and standardized run package, including run IDs, parameter snapshots, and archived input files.
- For this Q1 2026 review, those execution artifacts were not provided, limiting the review to design and documentation.

### 2.2 Segmentation reconciliation
- Prior working sessions highlighted the need to reconcile documented segment definitions to financial reporting outputs.
- The current materials still show misalignment between documented segments and provided output segments (notably `CRE Owner Occupied`).

### 2.3 Scenario governance
- Prior notes referenced the need for formal scenario governance: narratives, weights, refresh cadence, and evidence of committee approval.
- For this cycle, no scenario weight memo or committee approval artifact was provided.

### 2.4 Overlay governance
- Prior notes referenced establishing overlay triggers, caps, approval thresholds, and standardized documentation.
- The current methodology states a 6.0 bps cap; however, the provided segment overlays exceed that cap and the basis is not evidenced.

## 3. Items Noted as Partially Addressed (Documentation Only)
- Macro variable set is now consistently listed across scenarios (unemployment, GDP growth, house price growth, CRE price growth, prime rate).
- A three-scenario set is defined (Baseline/Adverse/Severe). However, the documented forecast/reversion horizons remain inconsistent across artifacts.

## 4. Implications
Absent execution artifacts and end-to-end lineage evidence, the institution remains exposed to:
- Inability to demonstrate repeatable quarterly processes
- Weak audit trail for key judgments (scenario choice/weights, overlays)
- Increased risk of segmentation and population definition errors

## 5. Recommended Next Actions (High Priority)
- Produce an execution run package template and populate it for a single quarter close dry-run.
- Produce a segment mapping and reconciliation from loan system populations to reserve output segments.
- Produce a scenario governance memo with narratives tied to numeric paths, and documented weights.
- Update overlay policy to reflect actual practice (or constrain overlays to documented caps with evidence).
