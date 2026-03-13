# Gap Tracker (Working)

**Bank:** Harborlight Savings  
**Case slug:** harborlight_savings_cecl_gap_assessment_q1_2026  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Last updated:** 2026-03-01

## Rating Scale
- **High:** likely to be cited in audit/regulatory review; impacts reliability or governance
- **Medium:** material documentation/control weakness; remediable with defined actions
- **Low:** documentation enhancement; does not change core results but improves defensibility

## Gap Register
| Gap ID | Theme | Description (Condition) | Criteria / Expectation | Impact | Severity | Evidence | Owner | Target date | Status |
|---|---|---|---|---|---|---|---|---|---|
| G-001 | Execution evidence | Execution-based review cannot be performed; missing reserve engine run package (run IDs, logs, parameter snapshots, archived inputs). | Repeatability and audit trail; reproducible quarter-end runs. | Inability to substantiate results or controls; limits reliance. | **High** | ER-010 Blocked | Portfolio Analytics | 2026-03-27 | Open |
| G-002 | Data lineage | End-to-end data lineage and transformation documentation not provided (source-to-target mappings, ETL logic, reconciliations). | Traceability of inputs and completeness controls. | Elevated risk of population/field errors; weak auditability. | **High** | ER-008 Blocked; ER-009 Open | Data Management | 2026-03-27 | Open |
| G-003 | Horizon inconsistency | Methodology states 8Q forecast/4Q reversion; model card states 6Q forecast/2Q reversion; numeric scenarios provided only 6 quarters. | Single source of truth; documented implementation alignment. | Governance deficiency; potential misstatement of methodology. | **High** | Methodology vs model card; ER-003 Partial | CECL Program Manager | 2026-03-06 | Open |
| G-004 | Scenario narrative alignment | Severe scenario narrative described as "prolonged contraction," but numeric path shows partial improvement by 2027Q2 (e.g., house price growth turns positive). | Narrative must tie to numeric path and be approved. | Weak support for scenario rationale; challengeability risk. | **Medium** | ER-004 Open | Credit Risk | 2026-03-13 | Open |
| G-005 | Scenario governance | Scenario weights and approvals not evidenced; no documented refresh cadence and version controls for scenario files. | Committee approvals and documented weighting policy. | Governance and control weakness; inconsistent application risk. | **High** | ER-005 Open | Finance / Credit Risk | 2026-03-13 | Open |
| G-006 | Segmentation reconciliation | Documented segments include CRE Owner Occupied, but reserve outputs omit a distinct segment; mapping not evidenced. | Documented segmentation must reconcile to reporting outputs and populations. | Misclassification risk; incomplete reserve reporting by segment. | **High** | ER-006 Open | Portfolio Analytics | 2026-03-06 | Open |
| G-007 | Overlay cap inconsistency | Documentation states overlay cap of 6.0 bps; provided overlays by segment range 12-18 bps; basis/scope not defined. | Overlay policy must reflect practice and define basis; cap monitoring evidence. | Potential policy non-compliance; audit/regulatory challenge. | **High** | ER-011 Partial; ER-012/013 Open | Finance Controller | 2026-03-13 | Open |
| G-008 | Overlay documentation | No overlay calculation support, bridge, or approval memo provided (by segment and driver). | Overlay must be transparent, repeatable, and approved. | Reduced interpretability; heightened model risk and control risk. | **High** | ER-012/013 Open | Finance | 2026-03-13 | Open |
| G-009 | Validation / independent review | No current validation report or documented MRM conclusions provided for the CECL model. | Independent review commensurate with risk; documented findings and remediation. | Governance gap; inability to demonstrate effective challenge. | **Medium** | ER-014 Open | MRM | 2026-04-10 | Open |
| G-010 | Change management | No centralized change log for model parameters, assumptions, or implementation changes. | Controlled changes with approvals and versioning. | Risk of untracked changes impacting ACL. | **Medium** | ER-015 Open | CECL Program Manager | 2026-03-27 | Open |

## Notes / Linkage to Expected Findings
- G-001 and G-002 support: **Execution-based review is blocked by missing reserve engine and lineage evidence.**
- G-004 supports: **Scenario narrative not fully aligned to numeric severe path.**
- G-006 supports: **Documented segment structure does not reconcile to supplied reserve outputs.**
- G-007 and G-008 support: **Overlay documentation understates magnitude implied by reserve bridge / outputs.**

## Next Steps (Working)
1) Resolve horizon and scenario path coverage (authoritative horizon + full forecast/reversion numeric files).
2) Provide segment mapping and population reconciliation, including CRE Owner Occupied treatment.
3) Deliver overlay bridge and approvals; clarify cap basis and compliance.
4) Deliver minimum execution package and lineage artifacts to enable a limited re-performance test.