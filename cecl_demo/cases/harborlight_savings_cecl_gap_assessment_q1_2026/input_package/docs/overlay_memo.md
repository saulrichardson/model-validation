# Overlay Memo (Documentation-Led Review)

**Bank:** Harborlight Savings  
**Topic:** Management Overlays - Design, Governance, and Traceability  
**Period:** Q1 2026 readiness review

## 1. Executive Summary
Management overlays are evidenced in provided outputs at **12-18 bps** by segment. Documentation reviewed to date states a **6.0 bps overlay cap**, creating a material inconsistency between policy/methodology and observed overlay magnitudes. In addition, overlay rationale, quantification method, and linkage to model limitations are not sufficiently traceable in the artifacts provided.

This memo documents gaps and required remediation to support a defensible overlay framework under CECL and to align overlay governance with practice.

## 2. Overlay Policy vs. Observed Application
### 2.1 Documented Policy Constraint
- **Overlay cap (documented): 6.0 bps** (stated as a cap/limit within the methodology/policy narrative).

### 2.2 Overlay Magnitudes Evidenced in Outputs
Provided overlay bps by output segment:
- `residential_mortgage`: **12.0 bps**
- `heloc`: **16.0 bps**
- `cre_investor`: **18.0 bps**
- `commercial_and_industrial`: **14.0 bps**

**Implication:** If the 6.0 bps is intended as an enforceable cap, then the observed overlay magnitudes indicate a breach requiring documented exception approval and rationale. If the 6.0 bps is not intended as a cap (e.g., an illustrative threshold, portfolio-level cap, or a legacy parameter), the policy language must be revised for clarity.

## 3. Traceability to Reserve Bridge
### 3.1 Required Traceability Elements (Not Fully Evidenced)
For each overlay component, documentation should include:
- identified model limitation or risk not captured quantitatively
- portfolio/segment exposure basis (UPB/EAD, balance, or ACL base)
- calculation steps to arrive at bps add-on
- governance approvals (committee minutes / sign-offs)
- controls: repeatability, versioning, and change control

### 3.2 Current State Observations
- Reserve bridge narrative indicates overlays contribute materially to the final ACL; however, the package lacks a **component-level overlay bridge** tying overlays to drivers and quantification.
- No evidence of **overlay exception process** is included despite overlays exceeding the documented cap.

## 4. Segmentation and Overlay Application
- Documented segments include **CRE Owner Occupied**, but outputs and overlays are provided only for `cre_investor` and do not evidence a distinct owner-occupied segment.
- Without segment mapping and reconciliation, overlay reasonableness cannot be assessed consistently across documented segments.

## 5. Remediation Actions (Required)
1. **Policy alignment:** Clarify whether 6.0 bps is (a) portfolio-level cap, (b) segment-level cap, (c) threshold requiring escalation, or (d) obsolete. Update documentation accordingly.
2. **Overlay calculation memo:** Produce a standardized overlay calculation template including basis, formulae, and support.
3. **Governance evidence:** Provide committee approvals for overlay amounts and any cap exceptions.
4. **Bridge reconciliation:** Provide a reserve bridge that reconciles modeled ACL to final ACL including overlay by segment and in total.

## 6. Reviewer Conclusion (Documentation-Led)
Given the observed overlay magnitudes relative to the documented cap and insufficient traceability, overlays represent a **high-risk documentation and governance gap**. Execution review is not possible under this package due to missing runtime evidence; therefore, conclusions are limited to design and documentation sufficiency.
