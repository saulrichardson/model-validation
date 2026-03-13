# Methodology

## Objective
To revalidate the Atlas Community Bank's installment underwriting model following a material refresh: (a) recalibrated threshold, (b) introduction of a liquidity feature, and (c) revised reason-code logic. This process aims to ensure robust, transparent, and fair credit decisioning for the retail unsecured installment lending portfolio.

## Process
- Data sample of 1,800 anonymized applicants from Q2-Q4 2024
- Updated logistic regression model (champion v2024.9 vs. candidate v2025.1)
- Assessment of coefficient shifts, implication of new feature (low_cash_buffer), and threshold sensitivity
- Reason-code generation mapped by candidate coefficients
- Performance segmentation: overall, thin-file, liquidity-constrained

## Key Inputs
- Champion and candidate scorecards implemented and auto-tested
- Thresholds: champion at 0.43, candidate at 0.41, with performance reviewed across the 0.37–0.45 sensitivity range
- Reason code outputs reviewed pre- and post-refresh

## Validation Items
- Model discrimination (AUC, Gini)
- Approval rate analysis by segment (notably thin file and liquidity)
- Backtesting and stability across coverage ratio min. 0.85
- Reason code monitoring recommendations
