# Evidence Request Log (Working)

**Bank:** Harborlight Savings  
**Case:** harborlight_savings_cecl_gap_assessment_q1_2026  
**Log owner:** Model Risk Management (MRM)  
**Last updated:** 2026-03-01

## Log Legend
- **Priority:** H (High), M (Medium), L (Low)
- **Status:** Open / Received / Partially received / Not available

## Evidence Requests
| Req ID | Request | Rationale / Use | Owner | Priority | Date Requested | Due Date | Status | Notes / Follow-up |
|---|---|---|---|---|---|---|---|---|
| ER-001 | Reserve engine end-to-end run package (inputs, scenario load file, configuration, run logs, outputs) for one quarter close | Required to move from documentation-led to execution-based review; supports reproducibility | Finance | H | 2026-02-19 | 2026-03-15 | Open | Finance indicated reserve engine environment "in build"; no run log available yet |
| ER-002 | Data lineage mapping from core systems to CECL input datasets (field mapping + transformation logic + QC checks) | Supports lineage and control assessment; ties to GL and reporting | Data Mgmt | H | 2026-02-19 | 2026-03-22 | Open | Provide balance reconciliation to subledger/GL by segment |
| ER-003 | Segment mapping and reconciliation: documented segments → output segments (including treatment of CRE Owner Occupied) | Required to resolve segmentation mismatch; supports reporting and governance | Credit Risk | H | 2026-02-20 | 2026-03-08 | Open | Outputs exclude `cre_owner_occupied`; needs justification for consolidation |
| ER-004 | Model card (latest approved), including horizon specification and reversion method detail | Resolve contradiction between methodology and model card; governance traceability | MRM | H | 2026-02-20 | 2026-03-05 | Partially received | Summary provided; approval page and change log missing |
| ER-005 | CECL methodology document (latest controlled version) with references to forecast/reversion and overlay cap definition | Confirm policy language and definitions; identify whether cap is portfolio or segment | Finance | H | 2026-02-20 | 2026-03-05 | Received | Version control metadata not included; request doc control header/footer |
| ER-006 | Scenario governance deck (baseline/adverse/severe narrative + selection rationale + approvals) | Align narrative to numeric paths; confirm horizon coverage | Treasury/ALM | H | 2026-02-20 | 2026-03-12 | Open | Only numeric tables received (6 quarters) |
| ER-007 | Full scenario time series for 8-quarter forecast period (if applicable) and reversion assumptions for remaining quarters | Resolve horizon mismatch; needed for methodology consistency | Treasury/ALM | H | 2026-02-24 | 2026-03-12 | Open | If 6 quarters is final, update methodology and approvals accordingly |
| ER-008 | Overlay calculation memo(s) showing driver, basis, math, and governance approvals; include any cap exceptions | Address overlay cap vs observed bps; supports auditability | Finance | H | 2026-02-20 | 2026-03-12 | Open | Current overlay bps: 12-18 vs documented cap 6 |
| ER-009 | Reserve bridge report tying modeled ACL to final ACL (including overlays) by segment and total | Traceability; aligns to financial close controls | Finance | M | 2026-02-24 | 2026-03-19 | Open | Provide template even if numbers are illustrative |
| ER-010 | Inventory of controls: QC checks, approvals, sign-offs for quarterly CECL process | Supports SOX-style control mapping; governance | Finance / IA | M | 2026-02-24 | 2026-03-22 | Open | Include evidence examples for one quarter when available |
| ER-011 | Change management log for model/process changes since last quarter | Governance; supports model risk expectations | MRM | M | 2026-02-24 | 2026-03-22 | Open | Needed to reconcile differences across artifacts |
| ER-012 | Definitions for macro variables (units, source, seasonal adjustment) used in scenario tables | Prevents misinterpretation; input control | Treasury/ALM | L | 2026-02-24 | 2026-03-26 | Open | Confirm GDP growth measure (q/q annualized vs y/y) |

## Current Blocking Status Summary
- **Blocked for execution-based review:** ER-001, ER-002 (not received)
- **Material documentation inconsistencies requiring resolution:** ER-003, ER-004/ER-005, ER-006/ER-007, ER-008
