# Governance Minutes (Documentation-led Review Meeting)

**Bank:** Harborlight Savings  
**Committee/Forum:** CECL Readiness Working Group (Finance, Credit Risk, Model Risk Management)  
**Meeting date:** 2026-02-10  
**Subject:** Q1 2026 CECL Readiness Gap Assessment - documentation-led review status

## 1. Attendees
- Finance Controller (Chair)
- Head of Credit Risk
- Model Risk Management (MRM) Lead
- CECL Program Manager
- Portfolio Analytics Manager
- Internal Audit Liaison (observer)

## 2. Purpose
Review progress and preliminary gaps identified in the documentation-led CECL gap assessment; agree scope limitations and remediation ownership.

## 3. Scope Limitation (Explicit)
The Working Group confirmed that **execution-based review is not possible at this time** due to missing artifacts, including:
- Reserve engine run package (run IDs, runtime logs, parameter snapshots)
- End-to-end data lineage evidence (source-to-target mapping, transformation code, reconciliations)

Accordingly, the package is **explicitly limited to non-execution review** (documentation adequacy, design consistency, and governance sufficiency). No reliance should be placed on this package as evidence of numerical accuracy or operational effectiveness.

## 4. Discussion Summary
### 4.1 Forecast and reversion horizon inconsistency
- Finance referenced methodology language of **8-quarter forecast** and **4-quarter reversion**.
- MRM noted the model card indicates **6-quarter forecast** and **2-quarter reversion**.
- Decision: treat as a documentation control issue requiring resolution and re-approval of the authoritative horizon.

### 4.2 Scenario narrative alignment
- Credit Risk noted the severe scenario narrative describes "prolonged contraction," but the numeric path shows partial improvement by 2027Q2, including house price growth turning positive.
- Decision: update narrative and include explicit tie-out to numeric paths and governance approval.

### 4.3 Segmentation reconciliation
- Portfolio Analytics confirmed output reporting currently produces segments: residential_mortgage, heloc, cre_investor, commercial_and_industrial.
- Finance asked where CRE Owner Occupied is represented.
- Decision: Analytics to provide a documented mapping and population reconciliation; until then, segmentation is treated as a material documentation gap.

### 4.4 Overlay cap inconsistency
- Methodology shows a **6.0 bps** overlay cap; the provided segment overlays (12-18 bps) exceed this.
- Decision: Finance to clarify cap basis and scope; MRM to require documented rationale and approvals for any overlays above stated cap.

## 5. Decisions and Actions
| Item | Decision / Action | Owner | Due date | Status |
|---|---|---|---|---|
| Horizon inconsistency | Identify authoritative forecast/reversion horizon; update documentation and obtain approval | CECL Program Manager | 2026-03-06 | Open |
| Scenario narrative | Update scenario narratives to match numeric paths; provide approval evidence | Head of Credit Risk | 2026-03-13 | Open |
| Segment mapping | Provide segment mapping including CRE Owner Occupied treatment and reconciliation to outputs | Portfolio Analytics Manager | 2026-03-06 | Open |
| Overlay governance | Clarify overlay cap definition and basis; produce overlay approval memo with bridge | Finance Controller | 2026-03-13 | Open |
| Execution artifacts | Produce reserve engine run package template; schedule a dry-run with archived inputs and logs | CECL Program Manager / Analytics | 2026-03-27 | Open |
| Data lineage | Provide source-to-target mapping and key reconciliations for one quarter | Data Management Lead | 2026-03-27 | Open |

## 6. Next Meeting
- Scheduled: 2026-03-17
- Objective: review provided mapping/overlay/scenario artifacts; determine readiness for limited execution-based testing.
