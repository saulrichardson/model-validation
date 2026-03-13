# Model Card: Meridian Home Equity Line Model (2024 Q1 Refresh)

**Model Owner:** Meridian Home Equity Risk Analytics

**Model Purpose**  
This model is designed to assess applicant eligibility and risk for home equity line of credit (HELOC) products. It is part of the Q1 2024 refresh, intended to reflect updated economic conditions and recent portfolio performance.

**Product Context**  
Applies to: Home equity line underwriting decisions across Meridian’s retail mortgage arm.

**Key Features (Count: 22)**
- Credit history length
- Debt-to-income ratio
- Home value estimate
- Loan-to-value ratio
- County housing volatility
- Prior mortgage delinquencies
- Revolving utilization
- Recent inquiries
- Employment history flag
- Propensity model score
- Draw period expectation
- Cash reserve levels
- HELOC specific behaviour score
- Applicant age
- Homeownership tenure
- Verified property type
- Income normalization factor
- Missed payment episodes
- Address match validation
- Application channel
- Recent balance transfers
- Open tradelines

**Reason-Code Coverage**
- Reason codes are mapped for all eligibility-impacting features, except for: payment_shock_index, verified_income_stability, and override_propensity_score (mapping gaps to address in a future release).

## Training Sample
- Sample size: 680 loans
- Data period: 2022-2023 originations

## Performance Summary
Model performance met design targets in backtesting (AUC: 0.74; FPR at policy cut: 4.6%). External validation not yet performed at the time of this readiness upload.

## Known Documentation Gaps
- Missing runtime artifacts and baseline reproduction scripts (pending vendor release).
- No end-to-end monitoring pipeline supplied.

---
**NOTE:** The above feature count (22) differs from methodology documentation (see methodology section for rationale).

---
**Version**: Q1 2024
**Last Updated**: Mar 30, 2024
