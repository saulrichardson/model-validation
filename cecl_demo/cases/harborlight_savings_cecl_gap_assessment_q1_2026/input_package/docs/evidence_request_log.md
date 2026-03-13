# Evidence Request Log - Harborlight Savings CECL Gap Assessment (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Maintained by:** Model Risk Management  
**Last updated:** 2026-02-25

> Status legend: **Open**, **In Progress**, **Received**, **Deferred**

| Req ID | Date Opened | Request | Rationale / Use | Owner | Due Date | Status | Notes / Follow-up |
|---|---|---|---|---|---|---|---|
| ER-001 | 2026-02-18 | Approved forecast and reversion horizon statement (single source of truth) | Resolve methodology vs model card inconsistency; confirm governance-approved horizon | CECL Program Lead | 2026-03-15 | Open | Current docs cite 8Q/4Q; model card cites 6Q/2Q. Need committee approval artifact. |
| ER-002 | 2026-02-18 | Reversion method specification (e.g., linear, step, long-run mean) and parameter values | Determine how macro assumptions are extended beyond provided scenario quarters | CECL Program Lead | 2026-03-15 | Open | Scenario tables only cover 6 quarters. |
| ER-003 | 2026-02-18 | Scenario narrative memo aligned to numeric baseline/adverse/severe paths | Address narrative misalignment to severe numeric trajectory; clarify timing/persistence | Treasury | 2026-03-15 | In Progress | Treasury indicated draft exists; not yet circulated. |
| ER-004 | 2026-02-18 | Source and governance of scenarios (vendor/source, versioning, approvals) | Confirm scenario control environment and change governance | Treasury | 2026-03-22 | Open | No sourcing metadata included with scenario tables. |
| ER-005 | 2026-02-18 | Segment mapping table: documented segments → output segments | Reconcile missing CRE Owner Occupied output; confirm completeness | Data Governance | 2026-03-22 | Open | Required for segmentation governance and overlay allocation. |
| ER-006 | 2026-02-18 | Portfolio composition by documented segment and output segment (balances, counts) | Confirm materiality and mapping reasonableness | Finance Data Team | 2026-03-29 | Open | Needed to determine where CRE Owner Occupied is reported. |
| ER-007 | 2026-02-18 | Overlay bridge by segment (base reserve vs base+overlay) for readiness as-of date | Validate overlay magnitude and transparency; support auditability | Controller | 2026-03-22 | Open | Overlays provided exceed documented cap; need bridge evidence. |
| ER-008 | 2026-02-18 | Overlay policy clarification: definition of "6.0 bps cap" (portfolio vs segment vs approval threshold) | Resolve cap inconsistency and governance expectation | Controller | 2026-03-22 | Open | Current documentation is ambiguous; applied overlays 12-18 bps. |
| ER-009 | 2026-02-18 | Overlay approvals: committee minutes/sign-offs for overlay levels | Demonstrate governance challenge and approval | Controller | 2026-03-29 | Open | Finance stated overlays are "temporary"; no approvals provided. |
| ER-010 | 2026-02-18 | Reserve engine runbook and configuration snapshot (non-prod acceptable) | Unblock execution-based review planning; confirm implementation controls | CECL Program Lead / IT | 2026-04-05 | Open | Execution-based review currently blocked. |
| ER-011 | 2026-02-18 | Data lineage: source systems → staging → CECL data mart → reserve outputs | Control and auditability; reproducibility | IT Data Team | 2026-04-05 | Open | Required for model implementation review. |
| ER-012 | 2026-02-18 | One reproducible run package (inputs, outputs, logs) for a single as-of date | Re-performance feasibility and control testing | CECL Program Lead | 2026-04-12 | Deferred | Deferred until ER-010/ER-011 provided. |
| ER-013 | 2026-02-25 | Definition of output segments and report dictionary | Ensure consistent reporting and mapping to GL/FRY-style reporting | Finance | 2026-03-29 | Open | Output segments list provided without report definitions. |

## Reviewer notes
- The evidence set remains insufficient to support execution-based validation. Requests ER-010 and ER-011 are gating items.
- ER-001/ER-002 are required to resolve horizon inconsistencies and confirm scenario completeness.
- ER-005 and ER-006 are required to resolve segmentation reconciliation and to interpret segment overlays.
