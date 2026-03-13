# Harborlight Savings - CECL Governance Minutes (Gap Assessment Review Session)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Meeting type:** Documentation-led gap assessment review (non-execution)  
**Date:** 2026-02-18  
**Location:** Hybrid (Finance conference room / Teams)

## 1. Attendees
- Controller (Chair)
- CECL Program Lead (Finance)
- Credit Risk Officer (Credit Administration)
- Model Risk Management (MRM) Reviewer
- Treasury Representative
- Data Governance Representative
- Internal Audit Liaison (observer)

## 2. Purpose
Review the Q1 2026 CECL readiness documentation package and agree on gap assessment findings, required evidence, and ownership for remediation.

## 3. Explicit limitation of review (non-execution)
MRM stated, and the Chair confirmed, that this session and the associated upload package are limited to a **documentation-led, non-execution review** due to missing runtime and lineage evidence, including:
- Reserve engine configuration/runbooks and execution logs
- End-to-end data lineage from source systems to reserve outputs
- Reproducible run package (inputs, outputs, and controls)

Accordingly, no conclusions were reached regarding numerical accuracy of reserve outputs, stability of implementation, or effectiveness of runtime controls.

## 4. Materials reviewed
- CECL process methodology narrative (forecast/reversion, segmentation, overlay cap)
- Model card summary (forecast/reversion horizons)
- Scenario tables (baseline/adverse/severe: 2026Q1-2027Q2)
- Segment-level overlay bps by output segment
- Prior review carry-forward note

## 5. Discussion summary
### 5.1 Forecast and reversion horizon inconsistency
- Finance referenced an 8-quarter forecast and 4-quarter reversion as "process standard."
- MRM noted the model card reflects 6-quarter forecast and 2-quarter reversion.
- No governance approval artifact was available to confirm the approved horizon.

**Decision:** Record as a gap; require a single approved horizon statement and evidence of approval.

### 5.2 Scenario narrative alignment
- Credit Risk noted the severe scenario "captures a recessionary shock."
- MRM observed that the numeric severe path indicates peak unemployment in 2026Q3 and persistent CRE price weakness into 2027Q2; narrative evidence tying to these features was not present.

**Decision:** Record as a gap; request narrative memo aligned to the numeric scenario path.

### 5.3 Segmentation reconciliation
- Documented segments include CRE Owner Occupied.
- Output segments provided exclude an owner-occupied CRE segment.
- Data Governance confirmed no mapping table was included in the package.

**Decision:** Record as a gap; request a documented segment mapping and reporting reconciliation.

### 5.4 Overlay cap vs overlay magnitudes
- Documentation references a 6.0 bps overlay cap.
- Provided segment overlays range from 12.0 to 18.0 bps.
- Finance indicated overlays were "temporary" pending enhanced data; no exception memo or approvals were produced.

**Decision:** Record as a gap; request overlay bridge, cap interpretation, and approval evidence.

## 6. Action items
1. **Horizon governance:** Provide approved forecast/reversion horizon and reversion method description; include committee approval evidence.  
   - Owner: CECL Program Lead  
   - Target: 2026-03-15
2. **Scenario narrative memo:** Provide narrative aligned to baseline/adverse/severe numeric paths and variable definitions.  
   - Owner: Treasury Representative  
   - Target: 2026-03-15
3. **Segment mapping:** Provide mapping between documented segments and reserve output segments, including treatment of CRE Owner Occupied.  
   - Owner: Data Governance Representative  
   - Target: 2026-03-22
4. **Overlay support:** Provide overlay bridge (base vs adjusted), cap policy clarification, and documented approvals/exceptions.  
   - Owner: Controller  
   - Target: 2026-03-22
5. **Execution readiness evidence:** Provide reserve engine runbook/configuration and data lineage artifacts sufficient to plan an execution-based review.  
   - Owner: CECL Program Lead / IT Data Team  
   - Target: 2026-04-05

## 7. Close
The Chair concluded that the package is suitable for a gap assessment upload but not sufficient for an execution-based validation or independent re-performance.
