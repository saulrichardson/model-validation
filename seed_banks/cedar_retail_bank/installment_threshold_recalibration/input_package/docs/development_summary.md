# Model Development Summary

## Product Context
Point-of-sale installment lending, supporting real-time credit offers at merchant partners.

## Development Timeline
- Data Mart Construction: January 2024
- Feature Engineering: February 2024
- Model Training, Initial Results: March 2024
- Calibration and UAT: April 2024

## Data and Sample
- Applicant sample: n = 1,600
- Random seed: 77
- Full split: 80% development, 20% OOT validation

## Key Changes
- Introduction of _low_cash_buffer_ as a new feature reflecting short-term liquidity risk
- Coefficient tweaks to _dti_ratio_, _thin_file_flag_, and _delinquency_12m_ strengthen sensitivity

## Technical Highlights
- Intercept raised from -2.38 (champion) to -2.21 (candidate)
- Candidate improves out-of-time AUC from 0.677 to 0.695
- New minimum approval threshold set at 0.39 to balance loss rate with booking volume

## Reason Code Review
The candidate model can trigger a new risk flag for low cash buffer, though this is not presently mapped in reason code outputs.

## Documentation Gaps
- Threshold policy documentation lags behind implementation (referencing 0.40 instead of 0.39)
- Reason code generation for new features to be addressed
