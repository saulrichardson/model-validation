# Harborlight Savings - CECL Readiness Gap Assessment Methodology (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Product context:** Consumer and real-estate portfolio reserve process  
**Workflow:** Gap assessment (documentation-led)

## 1. Purpose and scope
This methodology defines the documentation-led procedures used to assess Harborlight Savings' readiness for CECL governance, segmentation, forecasting, overlays, reporting, and control evidence. The objective is to identify gaps against internal policy expectations and supervisory "model risk management" documentation norms, without executing or independently recalculating reserve results.

**In-scope:**
- Method description and governance artifacts for lifetime loss estimation
- Portfolio segmentation and mapping to production outputs
- Reasonable & supportable (R&S) forecast approach, reversion approach, and scenario set documentation
- Management overlay policy, cap, and bridge support
- Data lineage narrative and control descriptions (to the extent documented)

**Out-of-scope (for this package):**
- Independent re-performance of CECL reserve calculations
- Code review, model runtime testing, or reserve engine execution
- Benchmarking against peer institutions

## 2. Review approach
### 2.1 Documentation-led gap assessment
Procedures:
1. **Inventory** provided documents and artifacts, including any "model card" summaries.
2. **Traceability checks**: confirm internal consistency among methodology narrative, segment definitions, scenario documentation, and reported output segments.
3. **Reasonableness checks** on scenario narratives vs numeric macro paths and disclosed horizon.
4. **Overlay assessment**: reconcile overlay policy (cap and governance) to overlay magnitudes implied by any reserve bridge artifacts provided.
5. **Control readiness**: confirm presence/absence of lineage, reserve engine, and execution evidence needed for an execution-based review.

### 2.2 Standards and reference expectations
- CECL documentation expectations for segmentation rationale, scenario governance, and Q-factor/overlay support.
- Model governance expectations: independent reviewability, data lineage, change control, and reproducibility.

## 3. Key design elements under review (per documentation)
### 3.1 Segmentation
**Documented segments (methodology basis):**
- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial

Expectation: documented segment structure should reconcile to reserve reporting outputs and allow a clear mapping of exposures and reserve allocations.

### 3.2 Forecast and reversion horizon (methodology basis)
**Documented R&S forecast horizon:** **8 quarters**  
**Documented reversion:** **4 quarters**  

Expectation: horizon definitions should match the model card and any governance approvals; reversion method should be specified (e.g., linear to long-run mean, immediate reversion, or stepwise).

### 3.3 Scenario framework
Three scenarios are considered for governance documentation:
- **Baseline** (6 quarters provided)
- **Adverse** (6 quarters provided)
- **Severe** (6 quarters provided)

Expectation: the scenario narrative should align to the numeric path and be clearly tied to forecast variables used in estimation.

## 4. Overlay methodology (as documented)
### 4.1 Overlay governance and cap
**Documented overlay cap:** **6.0 bps** (portfolio-level cap as described in documentation).

Expectation: overlay policy should define trigger criteria, measurement approach, approval process, and how overlays are allocated across segments.

### 4.2 Segment overlays (as supplied)
Supplied overlay bps by output segment:
- `residential_mortgage`: **12.0 bps**
- `heloc`: **16.0 bps**
- `cre_investor`: **18.0 bps**
- `commercial_and_industrial`: **14.0 bps**

Methodology expectation: overlays applied should reconcile to documented caps and be supported by bridge evidence; exceptions should be documented, approved, and time-bound.

## 5. Execution evidence requirements (to support future execution-based review)
A full execution-based review would require, at minimum:
- Reserve engine configuration and runbooks
- Data lineage from source systems to CECL staging and final reporting
- Model implementation specs (parameter files, transformations)
- A reproducible run package (inputs, outputs, logs) for at least one as-of date

**Current limitation:** runtime/engine evidence and lineage evidence are not present in this upload package; therefore, the review is restricted to documentation-led gap assessment.

## 6. Deliverables in this upload package
- Model overview summary (as represented in the model card and supporting memos)
- Scenario assumptions memo (numeric paths and narrative alignment checks)
- Overlay memo (policy vs applied magnitude reconciliation)
- Prior review note (issues carried forward)
- Governance minutes (non-execution review limitation and decisions)
- Evidence request log (open items)
- Gap tracker (findings, severity, owners, and target dates)
