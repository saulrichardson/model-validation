# Change Request: Installment Threshold Recalibration

## Motivation
The recent observed tightening in macroeconomic risk requires adjustment to threshold policy to maintain portfolio performance and preserve booking targets. This change request proposes:

- Lowering threshold to increase approval volumes and offset risk-shift effect
- Introducing _low_cash_buffer_ feature for additional granularity on short-term risk

## Scope of Change

- **Model release:** Scorecard v2025.2 (candidate)
- **Threshold:** Lowered from documented 0.40 to implemented 0.39
- **Feature set:** Addition of _low_cash_buffer_ (coefficient: 0.54)

## Policy and Reason Coding

Declined applicants are assigned primary reject reason codes based on highest weighted model feature. Mapping:

| Model Feature        | Reason Code            | Description                                                |
|---------------------|-----------------------|------------------------------------------------------------|
| bureau_headroom     | LOW_BUREAU_SCORE      | External credit score below minimum policy expectation.     |
| dti_ratio           | HIGH_DTI              | Debt burden exceeds current policy tolerance.               |
| utilization_rate    | HIGH_UTILIZATION      | Revolving exposure is elevated relative to policy.          |
| delinquency_12m     | RECENT_DELINQUENCY    | Recent delinquency behavior increased expected risk.        |
| inquiries_6m        | RECENT_CREDIT_SEEKING | Recent credit seeking activity is elevated.                 |
| thin_file_flag      | THIN_CREDIT_FILE      | Limited credit history reduced underwriting confidence.     |
| short_tenure        | SHORT_EMPLOYMENT_TENURE | Employment history is shorter than preferred.              |

Note: _low_cash_buffer_ is included in scoring but not mapped as a reason code in current policy.

## Implementation Plan
- UAT evidence attached
- Reference champion/candidate scoring notebooks available in package

## Requested Effective Date
- Immediate upon committee approval
