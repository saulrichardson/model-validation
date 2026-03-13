# Governance Minutes (CECL Documentation Review - Non-Execution)

**Bank:** Harborlight Savings  
**Committee:** CECL Working Group / Model Governance Working Session  
**Meeting date:** 2026-02-18  
**Meeting type:** Documentation-led readiness review (non-execution)

## 1. Attendees
- Finance (Controller's Office): A. Patel, J. Moreno
- Credit Risk: L. Chen, R. Daniels
- Treasury / ALM: S. Whitaker
- Data Management: K. Ibrahim
- Model Risk Management (MRM): T. O'Neill
- Internal Audit (observer): M. Ruiz

## 2. Purpose and Scope Limitation
The purpose of this meeting was to review CECL documentation completeness and internal consistency for readiness purposes.

**Explicit limitation:** Due to **missing reserve engine execution artifacts and missing data lineage evidence**, the working group agreed the review package is limited to **non-execution review**. No conclusions were reached regarding runtime accuracy, reproducibility, or end-to-end calculation integrity.

## 3. Materials Reviewed
- CECL methodology document (forecast/reversion, segmentation, overlays)
- Model card summary (horizons, scenarios, process description)
- Scenario tables (baseline/adverse/severe paths for 2026Q1-2027Q2)
- Reserve output extracts by segment (four output segments)
- Overlay summary (bps by segment)

## 4. Discussion Summary
### 4.1 Forecast/Reversion Horizon
- Finance noted the methodology states **8-quarter forecast / 4-quarter reversion**.
- MRM noted the model card states **6-quarter forecast / 2-quarter reversion**, and scenario tables provided also cover **6 quarters**.
- Action agreed: confirm the approved horizon and update artifacts for consistency, or provide documentation supporting different horizons across components.

### 4.2 Segmentation
- Credit Risk noted documented segments include **CRE Owner Occupied**.
- Finance confirmed outputs do not include a separate owner-occupied CRE segment.
- Action agreed: provide a segment mapping and rationale for any consolidation.

### 4.3 Scenario Narrative Alignment
- Treasury/ALM raised a concern that the severe scenario narrative described in management commentary does not clearly align with the numeric trough timing.
- Action agreed: provide the scenario governance deck and narrative used for approval and reconcile narrative statements to numeric paths.

### 4.4 Overlays
- MRM noted the documented overlay cap is **6.0 bps**; provided overlays are materially higher.
- Finance indicated overlays reflect "conservatism pending data maturation" but did not provide a quantification memo or exception approvals.
- Action agreed: develop overlay calculation memos and clarify cap definition and governance escalation requirements.

## 5. Decisions
- **Decision 1:** Proceed with a documentation-led gap assessment package for Q1 2026 readiness.
- **Decision 2:** Defer any execution-based validation, benchmarking, or re-performance until reserve engine run logs, configuration, and lineage are provided.

## 6. Action Items
| ID | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| GOV-01 | Provide reserve engine run package (inputs, configuration, run logs, outputs) | Finance / Credit Risk | 2026-03-15 | Open |
| GOV-02 | Provide data lineage mapping from source to CECL inputs; include GL/balance recon | Data Mgmt | 2026-03-22 | Open |
| GOV-03 | Confirm approved forecast/reversion horizons and update methodology/model card | Finance / MRM | 2026-03-08 | In progress |
| GOV-04 | Provide segment mapping (documented → output segments) and justification | Credit Risk | 2026-03-08 | Open |
| GOV-05 | Provide scenario governance deck and narrative alignment memo | Treasury / ALM | 2026-03-12 | Open |
| GOV-06 | Provide overlay calculation memos and cap/exception governance evidence | Finance | 2026-03-12 | Open |
