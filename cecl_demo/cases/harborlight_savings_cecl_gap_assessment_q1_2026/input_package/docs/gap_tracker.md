# Gap Tracker (Documentation-Led) - Harborlight Savings CECL Readiness

**Case:** harborlight_savings_cecl_gap_assessment_q1_2026  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Prepared by:** MRM (documentation-led)  
**Last updated:** 2026-03-01

## Rating Scale
- **Severity:** Critical / High / Moderate / Low
- **Status:** Open / In progress / Closed / Deferred

## Gap Register
| Gap ID | Theme | Gap Description | Evidence / Reference | Impact | Severity | Owner | Target Date | Status | Remediation / Next Step |
|---|---|---|---|---|---|---|---|---|---|
| G-001 | Execution & Controls | Execution-based review is blocked by missing reserve engine artifacts (run logs, configuration, reproducible package). | ER-001; Governance minutes §2 | Cannot validate calculation integrity, repeatability, or QC; limits conclusions to design only. | **Critical** | Finance | 2026-03-15 | Open | Deliver one quarter run package; establish run log retention and approval evidence. |
| G-002 | Data Lineage | No end-to-end lineage from source systems to CECL inputs (field mapping, transforms, reconciliations). | ER-002 | Material risk of input errors; inability to demonstrate completeness/accuracy controls. | **Critical** | Data Mgmt | 2026-03-22 | Open | Provide lineage mapping + GL/subledger reconciliation by segment and product. |
| G-003 | Forecast/Reversion Horizon | Contradiction: methodology states **8Q forecast/4Q reversion** while model card states **6Q/2Q**; scenario tables provided cover 6 quarters only. | Methodology §3.1; Model overview §3; Scenario appendix | Inconsistent approved design; may cause implementation variance and audit challenge. | **High** | Finance / MRM | 2026-03-08 | In progress | Confirm approved horizons; update all artifacts and approvals; provide full scenario series if 8Q is required. |
| G-004 | Scenario Governance | Scenario narrative not fully aligned to numeric severe path (turning points). Approvals for scenario narrative not evidenced. | Scenario appendix §4; ER-006 | Weakens support for "reasonable and supportable" justification and governance. | **High** | Treasury/ALM | 2026-03-12 | Open | Provide approved scenario deck; create narrative-to-numeric mapping (peak/trough timing). |
| G-005 | Segmentation Reconciliation | Documented segment list includes **CRE Owner Occupied**, but outputs omit `cre_owner_occupied`. | Methodology §3.2; Model overview §1 | Inability to reconcile reserve reporting to documented pooling; potential misstatement of segment reporting. | **High** | Credit Risk | 2026-03-08 | Open | Provide mapping and aggregation rules; update documentation or outputs to align. |
| G-006 | Overlays - Policy vs Practice | Documented overlay cap **6.0 bps** conflicts with provided overlays **12-18 bps** by segment; exception governance not evidenced. | Overlay memo; ER-008 | High governance and audit risk; potential unsupported management adjustment. | **High** | Finance | 2026-03-12 | Open | Clarify cap definition; document exceptions/approvals; produce calculation memos. |
| G-007 | Overlays - Quantification Traceability | Overlay calculation steps, basis, and driver linkage are not evidenced; reserve bridge does not show overlay components. | ER-008; ER-009 | Impairs defensibility and repeatability; cannot audit overlay components. | **High** | Finance | 2026-03-19 | Open | Provide overlay component memo and bridge tying modeled ACL → final ACL by segment. |
| G-008 | Governance Artifacts | Model card approval page, change log, and version control metadata not provided (summary only). | ER-004 | Weakens governance evidence and change control story for regulators/auditors. | **Moderate** | MRM | 2026-03-05 | Partially complete | Provide controlled document with approval signatures, effective date, and change history. |
| G-009 | Definitions & Inputs | Macro variable definitions (units, frequency, seasonal adjustment, GDP measure) not evidenced. | ER-012 | Risk of misinterpretation and inconsistent implementation. | **Low** | Treasury/ALM | 2026-03-26 | Open | Provide variable definition sheet and source references; tie to scenario governance deck. |

## Expected Findings Mapping (Traceability)
- **Execution-based review blocked:** Addressed by **G-001** and **G-002**.
- **Scenario narrative misalignment:** Addressed by **G-004**.
- **Segment structure not reconciling to outputs:** Addressed by **G-005**.
- **Overlay documentation understates magnitude:** Addressed by **G-006** and **G-007**.

## Items Deferred Until Runtime Evidence Available
- End-to-end re-performance testing
- Sensitivity testing and benchmarking
- Monitoring/backtesting effectiveness assessment

**Condition to lift deferral:** receipt of ER-001 and ER-002 with a reproducible quarterly run package and lineage reconciliation.