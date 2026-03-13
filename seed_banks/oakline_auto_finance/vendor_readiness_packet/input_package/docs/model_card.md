# Model Card — Oakline Vendor-Managed Auto Finance Acquisition Model

**Model Version:** v2023.08  
**Vendor:** [Redacted]  
**Reviewed By:** Oakline Model Risk  
**Intended Use:** Prioritize indirect auto applications for loan acquisition.

## Feature List
1. FICO Score
2. LTV Ratio
3. New/Used Vehicle Flag
4. Applicant Income
5. Length of Employment
6. Channel Type (Indirect)
7. Dealer Quality Band *(see Reason Code Gaps)*
8. Loan Term Length
9. Term Stretch Flag *(see Reason Code Gaps)*
10. Down Payment Amount
11. Prior Auto Loan History

## Reason Code Coverage
Partial. Missing detailed mapping for Dealer Quality Band and Loan Term Stretch Flag. Generic statements provided elsewhere.

## Monitoring Support
Vendor supplied a generic recommendation to monitor score distributions and approval rates on a quarterly basis. No monitoring metric definitions or alert thresholds supplied.

## Development Summary
No development documentation or validation evidence provided. Algorithm and training process are vendor-supplied and not independently reproducible.

## Known Limitations & Gaps
- No executable scoring assets available.  
- Reason-code mapping incomplete.  
- Monitoring approach lacks actionable specifications.
