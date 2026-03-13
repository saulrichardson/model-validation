# Policy Exception Memo — Meridian Home Equity Line Model (Q1 2024)

**To:** Model Risk Management, Credit Policy  
**From:** Risk Analytics  
**Date:** March 1, 2024

**Subject:** Request for Policy Exception — Reason-Code Coverage and Implementation Evidence

Per current model risk standards, new/revised models must provide: (i) complete reason-code mapping for all decision-impacting features, and (ii) full runtime documentation for reproducibility and monitoring. 

As of this readiness review, the HELOC Q1 2024 documentation package lacks:
- Reason-code assignment for payment_shock_index, verified_income_stability, override_propensity_score (feature coverage gap)
- Runtime package and executable scripts for model and monitoring (pending vendor release)

**Exception Request**
We request a temporary exception, permitting Q1 readiness approval based on documentation review alone, subject to the following undertakings:
1. All reason-code mapping gaps will be closed prior to any model move to production.
2. Complete implementation and monitoring artifacts will be submitted upon vendor handover, prior to execution-based validation.

This exception is sought to avoid undue project delay while allowing conceptual review to proceed.

**Requested by:**  
_Head of Analytics, Home Equity Line — Meridian_

**Endorsement:**
_Reviewed by Model Risk, Conditional upon stated undertakings_ 

---
*Exception valid through readiness review phase only. Execution/production approval is not in scope until all gaps are closed.*
