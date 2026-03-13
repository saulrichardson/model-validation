# Gap Tracker - Harborlight Savings CECL Readiness Gap Assessment (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Tracking owner:** Model Risk Management  
**Last updated:** 2026-02-25

> Severity scale: **High** (blocks review or indicates material governance/control deficiency), **Medium** (significant documentation/control weakness), **Low** (clarification or enhancement).

| Gap ID | Category | Finding / Gap Statement | Evidence Observed | Impact | Severity | Owner | Target Date | Status | Link to Evidence Request |
|---|---|---|---|---|---|---|---|---|---|
| GAP-001 | Execution readiness | Execution-based review is blocked by missing reserve engine artifacts and end-to-end data lineage. | No reserve engine runbook/config snapshot; no lineage diagrams; no reproducible run package. | Cannot validate implementation, runtime controls, or numerical accuracy; review limited to documentation-led assessment. | High | CECL Program Lead / IT Data Team | 2026-04-05 | Open | ER-010, ER-011, ER-012 |
| GAP-002 | Forecast horizon governance | Forecast/reversion horizons are inconsistent across documents (methodology: 8Q/4Q; model card: 6Q/2Q). | Conflicting statements; no approval artifact. | Unclear approved horizon; risk of inconsistent application and audit challenge. | High | CECL Program Lead | 2026-03-15 | Open | ER-001 |
| GAP-003 | Scenario completeness | Scenario tables provided include 6 quarters only; not reconciled to documented horizon needs and no extension rule documented. | Baseline/adverse/severe numeric tables end at 2027Q2. | Potential mismatch between documented process and implemented forecast horizon; increased model governance risk. | Medium | CECL Program Lead / Treasury | 2026-03-22 | Open | ER-002, ER-004 |
| GAP-004 | Scenario narrative alignment | Scenario narrative is not fully aligned to the numeric severe scenario path (timing and persistence of stress not explicitly described). | Numeric severe peaks in 2026Q3; CRE price growth remains negative through 2027Q2; narrative memo not provided. | Governance challenge; reduced interpretability and potential audit criticism. | Medium | Treasury | 2026-03-15 | In Progress | ER-003 |
| GAP-005 | Segmentation reconciliation | Documented segment structure does not reconcile to supplied reserve outputs; CRE Owner Occupied is documented but not present as an output segment. | Documented segments list includes CRE Owner Occupied; output segments list excludes it; no mapping table. | Risk of incomplete reporting, misallocation of overlays, and governance confusion over segment-level results. | High | Data Governance | 2026-03-22 | Open | ER-005, ER-006 |
| GAP-006 | Overlay cap inconsistency | Overlay documentation references a 6.0 bps cap while provided segment overlays are 12-18 bps, with no exception documentation. | Cap cited as 6.0 bps; overlays provided exceed cap across all output segments. | Potential policy breach or misstatement of cap definition; auditability concern. | High | Controller | 2026-03-22 | Open | ER-007, ER-008, ER-009 |
| GAP-007 | Overlay transparency | Overlay bridge support (base vs base+overlay) and allocation logic are not provided. | Segment overlay bps provided; no bridge, no quantitative support, no approval trail. | Weakness in explainability and governance; cannot validate reasonableness of overlays. | Medium | Controller | 2026-03-22 | Open | ER-007 |
| GAP-008 | Reporting definitions | Output segment definitions/report dictionary not provided, limiting traceability to financial reporting. | Output segment names only. | Increased risk of inconsistent interpretation across Finance/Credit; reporting control weakness. | Medium | Finance | 2026-03-29 | Open | ER-013 |

## Summary of expected findings (as validated in tracker)
- Execution-based review is blocked by missing reserve engine and lineage evidence. (GAP-001)
- Scenario narrative is not fully aligned to the numeric severe scenario path. (GAP-004)
- Documented segment structure does not reconcile to the supplied reserve outputs. (GAP-005)
- Overlay documentation understates the magnitude implied by the reserve bridge / provided overlays. (GAP-006, GAP-007)

## Next checkpoint
- 2026-03-18: evidence review for ER-001 to ER-005; confirm whether gaps can be downgraded or require escalation to CECL Steering Committee.