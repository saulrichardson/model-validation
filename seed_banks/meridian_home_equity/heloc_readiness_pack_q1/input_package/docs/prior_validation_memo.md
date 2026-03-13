# Prior Validation Memo

**Date:** January 16, 2024
**From:** Model Risk Review Committee
**Subject:** Prior Validation Summary for Meridian HELOC Model (Q1 Refresh)

Key findings from the December 2023 documentation walkthrough are as follows:
- Feature selection approach is clearly articulated and in line with bank standards; however, discrepancies exist between documentation sources (feature counts conflict between methodology and model card).
- Reason code assignment is mostly complete but does not cover new resilience features as intended at initiative launch (notably, payment_shock_index and verified_income_stability are unmapped).
- Monitoring recommendations were found to reference runtime tests not included in the submission.
- No substantial code or runtime documentation provided—no model reproducibility or baseline comparison feasible at this stage.
- Use of a stratified 680-loan sample is appropriate for development, but out-of-time and out-of-sample validation is still pending.

**Action Items:**
- Request full implementation package, including scripts and executable monitoring evidence, prior to final review.
- Submit mapping for omitted reason codes targeting resilience variables.
