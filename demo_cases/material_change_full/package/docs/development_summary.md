Development and Calibration Summary

The candidate refresh was fit on the 2022-Q1 through 2024-Q3 retail installment booking vintages using
logistic regression with monotonic bin review and coefficient sign constraints inherited from the approved
2024.9 champion. The refresh retained the prior champion factor set and introduced one additional liquidity
feature derived from recent_cash_buffer_mo. Coefficients were re-estimated after a stability screen on
population drift, missingness, and segment prevalence. Operating-point calibration targeted a stable manual-review
queue while preserving rank ordering relative to the champion.

Validation package scope:
- Development sample window: 2022-01 through 2024-09.
- OOT validation window: 2024-10 through 2025-01.
- Candidate liquidity feature: low_cash_buffer = clip((6 - recent_cash_buffer_mo) / 6, 0, None).
- Threshold recalibration: decline threshold moved from 0.43 to 0.41 after approval-rate sensitivity testing.
