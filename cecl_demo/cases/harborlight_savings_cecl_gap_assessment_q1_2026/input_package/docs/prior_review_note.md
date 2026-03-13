# Harborlight Savings - Prior Review Note (Carry-Forward Items)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`

## 1. Context
This note summarizes issues identified in prior internal discussions and preliminary readiness checkpoints that remain unresolved in the current documentation-led upload package.

## 2. Carry-forward items
### 2.1 Execution-based review readiness
- Prior checkpoints noted that an execution-based review would require reserve engine run logs, configuration snapshots, and data lineage artifacts.
- Current package does not include reserve engine evidence or end-to-end lineage. This blocks re-performance and control testing.

**Status:** Open; carry-forward.

### 2.2 Forecast/reversion horizon governance
- Prior notes referenced inconsistent articulation of the R&S horizon and reversion methodology across documents.
- Current package includes a methodology narrative indicating **8-quarter forecast / 4-quarter reversion**, while the model card references **6-quarter forecast / 2-quarter reversion**.

**Status:** Open; carry-forward.

### 2.3 Scenario narrative alignment
- Prior notes indicated that scenario narratives were not consistently tied to the numeric macro path used for estimation.
- Current package includes numeric severe paths that show a pronounced 2026Q2-2026Q3 contraction and CRE price declines persisting into 2027, while narrative alignment evidence is incomplete.

**Status:** Open; carry-forward.

### 2.4 Segment reconciliation
- Prior notes identified a mismatch between documented segment taxonomy and reporting outputs.
- Current materials still include documented **CRE Owner Occupied** without a corresponding output segment.

**Status:** Open; carry-forward.

### 2.5 Overlay governance and cap
- Prior notes referenced an overlay cap expectation and the need for bridge support.
- Current package documents an overlay cap of **6.0 bps** but provides segment overlays **12-18 bps** without exception approvals or bridge evidence.

**Status:** Open; carry-forward.

## 3. Recommended near-term actions
- Provide reserve engine artifacts and lineage documentation to unblock execution-based review.
- Produce a single approved horizon statement (forecast and reversion) with committee approval evidence.
- Deliver a segment mapping and reporting reconciliation.
- Deliver overlay bridge and approval documentation, including cap interpretation and exceptions.
