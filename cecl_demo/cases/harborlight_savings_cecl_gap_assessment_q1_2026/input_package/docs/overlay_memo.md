# Harborlight Savings - Management Overlay Gap Memo (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment

## 1. Purpose
Assess the consistency and supportability of management overlays as documented (policy, cap, governance, allocation) versus overlays reflected in supplied segment-level overlay bps.

## 2. Overlay policy position (as documented)
- Documentation references a **portfolio overlay cap of 6.0 bps**.
- Documentation indicates overlays are intended to address limitations not captured in the base quantitative framework (e.g., data lags, emerging risk, underwriting/servicing changes) and should be:
  - Supported by quantitative and qualitative evidence,
  - Time-bound and re-evaluated quarterly,
  - Approved through an established governance committee.

## 3. Overlays provided (by output segment)
Supplied overlay bps by segment:
- `residential_mortgage`: **12.0 bps**
- `heloc`: **16.0 bps**
- `cre_investor`: **18.0 bps**
- `commercial_and_industrial`: **14.0 bps**

## 4. Key gap: cap vs applied magnitude
### 4.1 Observed inconsistency
The overlay bps supplied exceed the documented cap of **6.0 bps** for every output segment.

### 4.2 Documentation required to resolve
To support overlays above the documented cap, the package would typically include:
- A cap exception memo (including rationale, duration, and approval authority),
- A quantitative bridge showing reserve without overlay vs with overlay by segment,
- Allocation logic demonstrating how the portfolio-level cap was interpreted (if not applied at segment level), and
- Evidence of quarterly challenge and committee approval.

**None of the above exception documentation is included in this package.**

## 5. Secondary gap: segment mapping and overlay allocation
The documented segment structure includes **CRE Owner Occupied**, while overlay bps are provided only for output segments and do not include an owner-occupied CRE segment. Without a mapping table:
- It is not possible to confirm whether CRE Owner Occupied is included in `cre_investor`, netted elsewhere, or excluded.
- It is not possible to confirm overlay allocation completeness across documented segments.

## 6. Conclusion (documentation-led)
Overlay documentation understates the magnitude implied by supplied overlays and does not provide sufficient support for (i) application above the documented cap and (ii) segment-level allocation and governance approvals.

## 7. Required remediation artifacts
1. Overlay policy clarification: whether the 6.0 bps cap is portfolio-level, segment-level, or approval threshold.
2. Overlay bridge by segment for the as-of date used in readiness testing (base vs base+overlay).
3. Committee approval minutes and sign-offs for overlay amounts.
4. Segment mapping table between documented segments and reserve output segments.
