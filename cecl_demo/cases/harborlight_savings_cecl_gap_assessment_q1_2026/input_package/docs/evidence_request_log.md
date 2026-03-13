# Evidence Request Log (Working)

**Bank:** Harborlight Savings  
**Case slug:** harborlight_savings_cecl_gap_assessment_q1_2026  
**Log owner:** Model Risk Management (MRM)  
**Last updated:** 2026-03-01

## Instructions
This log tracks evidence requested to complete the documentation-led gap assessment and to unblock any future execution-based testing. Items marked "Blocked" are prerequisites for execution-based review.

## Evidence Requests
| Req ID | Date requested | Evidence / Artifact | Purpose | Owner | Status | Follow-up notes |
|---|---|---|---|---|---|---|
| ER-001 | 2026-02-03 | CECL methodology document (current approved version) | Establish documented horizon, segmentation, overlays | CECL Program Manager | Received | Version provided lacks approval page/signature block; confirm effective date. |
| ER-002 | 2026-02-03 | Model card / model overview (current) | Confirm implemented horizon, segmentation, scenario handling | Portfolio Analytics | Received | Model card indicates 6Q forecast / 2Q reversion (conflicts with methodology). |
| ER-003 | 2026-02-05 | Scenario numeric files for Baseline/Adverse/Severe (forecast + reversion + long-run) | Validate horizon coverage and reversion mechanics | Credit Risk | Partial | Only 6 quarters provided (2026Q1-2027Q2); no reversion/long-run assumptions. |
| ER-004 | 2026-02-05 | Scenario narratives tied to numeric files and approval evidence | Governance and alignment | Credit Risk | Open | Narrative described in email but not delivered as approved artifact. |
| ER-005 | 2026-02-06 | Scenario weights memo (quarterly weights and approvals) | Confirm governance and application | Finance | Open | No evidence of committee-approved weights provided. |
| ER-006 | 2026-02-06 | Segment definition memo and mapping to output segments | Reconcile documented vs output segments | Portfolio Analytics | Open | Need explicit treatment of CRE Owner Occupied (mapped/merged/excluded). |
| ER-007 | 2026-02-07 | Data dictionary for loan-level input fields (by segment) | Confirm input completeness and definitions | Data Management | Open | Provide field definitions, source system, and refresh cadence. |
| ER-008 | 2026-02-07 | Source-to-target mapping and transformation logic (ETL specs or code excerpts) | **Blocked:** lineage and completeness | Data Management | Blocked | Not provided; required to proceed to execution-based review. |
| ER-009 | 2026-02-10 | Reconciliation: loan system balances to CECL population (as-of date) | Completeness and controls | Finance / Data | Open | Request one quarter example with exceptions list and resolution. |
| ER-010 | 2026-02-10 | Reserve engine run package (inputs archive, parameters, run IDs, logs) | **Blocked:** reproducibility and testing | Portfolio Analytics | Blocked | No run package exists in shared repository; needs template and first populated run. |
| ER-011 | 2026-02-12 | Overlay policy and cap definition (basis, scope, monitoring) | Resolve cap inconsistency | Finance | Partial | Methodology references 6.0 bps cap; basis and monitoring not described. |
| ER-012 | 2026-02-12 | Overlay calculation workbook / system output and segment attribution | Tie overlay to results | Finance | Open | Provided overlay bps by segment but no calculation support or bridge. |
| ER-013 | 2026-02-13 | Reserve bridge (modeled ACL → overlays → final ACL) by segment | Validate transparency | Finance | Open | Needed to reconcile to reported overlay levels (12-18 bps). |
| ER-014 | 2026-02-14 | Validation report / MRM review for CECL model | Governance and conceptual soundness | MRM | Open | No current validation; provide plan/timeline and any interim memos. |
| ER-015 | 2026-02-18 | Change management log (versions, parameter changes, approvals) | Control expectations | CECL Program Manager | Open | No centralized log provided. |
| ER-016 | 2026-02-20 | Close calendar / operating procedure for quarter-end | Repeatability | Finance | Open | Provide steps, owners, and evidence checklist for quarterly close. |

## Blocking Items Summary
Execution-based review remains blocked until ER-008 and ER-010 are provided (lineage evidence and reserve engine run package).
