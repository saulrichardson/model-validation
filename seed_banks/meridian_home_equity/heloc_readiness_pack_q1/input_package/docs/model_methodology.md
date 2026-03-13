# Model Methodology: Meridian HELOC Underwriting Model (Q1 2024)

**Development Overview**
- The model was constructed atop a logistic regression framework, using industry best practices for feature selection, regularization, and sampling bias correction.
- Home equity origination data (n=680) was extracted from the 2022-2023 Meridian booking repository, post-cleaning.
- Features were shortlisted based on statistical relevance, business interpretability, and resilience to macroeconomic stress.

**Feature Coverage (Count: 18)**
- Debt-to-income ratio
- Credit history length
- Loan-to-value ratio
- Recent inquiries
- Home value estimate
- Prior mortgage delinquencies
- Income normalization factor
- Revolving utilization
- Applicant age
- Verified property type
- Cash reserve levels
- Employment history flag
- Draw period expectation
- Address match validation
- Application channel
- Homeownership tenure
- County housing volatility
- Propensity model score

> **Note:** Four features present in the model card (open tradelines, recent balance transfers, missed payment episodes, and HELOC-specific behaviour score) were evaluated but not retained in the final trained model.

**Reason-Code Assignment**
- All 18 in-scope features have assigned reason codes, with exceptions noted for payment_shock_index, verified_income_stability, and override_propensity_score—these were initially intended for inclusion but remain unmapped.

**Sampling and Validation**
- Stratified random sample: 680 records
- Internal cross-validation (5-fold)

**Known Issues and Gaps**
- No reproducibility script or model code included.
- Final deployment depends on third-party vendor module release.
