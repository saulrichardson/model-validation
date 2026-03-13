# Overlay Memo (Documentation Review and Gap Assessment)

**Bank:** Harborlight Savings  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Topic:** Qualitative overlays and cap governance

## 1. Purpose
This memo documents the documentation-led review of qualitative overlays ("overlays") used within the CECL reserve process, focusing on:
- Consistency between overlay policy (caps/limits) and reported overlay magnitudes
- Segment-level overlay attribution and governance
- Auditability (traceability, rationale, approval)

## 2. Documented Overlay Policy (As Stated)
Methodology documentation indicates:
- **Overlay cap:** **6.0 bps** (portfolio cap)
- Overlays are intended to be applied in limited circumstances where model limitations exist and are supported by written rationale and approvals.

No evidence was provided demonstrating how the 6.0 bps cap is calculated (e.g., cap basis: on total ACL / amortized cost / modeled ACL) or how the cap is monitored and enforced.

## 3. Overlay Magnitudes Provided for Review
Segment-level overlay bps provided in reserve outputs:
- `residential_mortgage`: **12.0 bps**
- `heloc`: **16.0 bps**
- `cre_investor`: **18.0 bps**
- `commercial_and_industrial`: **14.0 bps**

## 4. Observations
### 4.1 Policy vs reported overlay magnitude
The provided segment overlay bps exceed the documented portfolio overlay cap of 6.0 bps. Without additional documentation, this presents a control/design inconsistency.

Potential explanations that require evidence:
- The **6.0 bps cap** is intended to apply only to a subset of portfolios (e.g., consumer only) or only to incremental overlays beyond a baseline.
- The provided overlay bps are **not on the same basis** as the documented cap (e.g., applied to modeled loss rate vs applied to exposure vs applied to ACL).
- The segment overlay bps represent **cumulative** overlays across multiple components (e.g., Q-factor plus model risk adjustment) while the 6.0 bps cap applies to only one component.

### 4.2 Overlay transparency and bridge support
The expected reserve bridge support for overlays (by segment and driver) was not provided. As a result:
- We cannot confirm the overlay is applied consistently to the correct population.
- We cannot confirm the overlay is stable and repeatable quarter-over-quarter.
- We cannot confirm the overlay is not compensating for data/segmentation issues.

### 4.3 Governance and approvals
No dated and signed overlay approval memo, committee minutes approving overlay levels, or evidence of independent review was provided.

## 5. Conclusion (Documentation-led)
Overlay documentation understates the magnitude implied by provided segment overlay bps and does not reconcile to a documented cap. The current state does not evidence a defensible overlay governance framework.

## 6. Required Remediation Artifacts (Open Requests)
- Overlay policy clarification: definition of "bps" and basis, and the cap's scope and monitoring.
- Segment-level overlay calculation workbook (or system output) and tie-out to reserve results.
- Overlay rationale memo(s) with dated approvals and sign-offs.
- Reserve bridge showing modeled ACL → overlays → final ACL, with segment attribution.
