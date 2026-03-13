# Internal Model Governance Committee Minutes

**Date:** 2024-05-02  
**Attendees:** S. Vega, T. Brooks, R. Chen, L. O'Neil, J. McTiernan  
**Agenda:** Review and vote on Installment Lending Threshold Policy Recalibration (Scorecard v2025.2)

---

**1. Opening**
- Committee opened with summary of existing threshold at 0.40 approval probability (per prior documentation)
- S. Vega: Emphasized importance of preserving booking targets concurrent with risk controls

**2. Model Development Update**
- T. Brooks presented candidate changes:
  - Addition of _low_cash_buffer_ as new feature
  - Updated coefficient values for thin-file and DTI risk factors
- L. O'Neil noted current documentation references threshold of 0.40, but candidate UAT applies 0.40 as cutoff (see attached packet). 

**3. Implementation & Reason Code Mapping**
- R. Chen: Raised concern on reason-code generation not covering new low_cash_buffer feature
- T. Brooks to update mapping in next cycle, not prioritized for this update

**4. Monitoring & Policy Control**
- J. McTiernan: Monitoring plan lacks granular thresholds for thin-file segment, referenced last plan as sufficient for now though flagged as 'to-do'

**5. Voting**
- Unanimous approval to advance candidate package to risk sign-off, pending implementation verification
- Noted final document refresh required pre-sign-off to align documented and operational thresholds

**6. Action Items**
- Update reason-code mapping for new features next cycle
- Refresh monitoring plan and documentation for thin-file policy thresholds

---

*Minutes submitted by L. O'Neil*
