# Development Summary

## Background
The 2025 Q1 refresh targets incremental improvements in discrimination and policy alignment by adding a new liquidity variable (low_cash_buffer), recalibrating intercepts, and running formal threshold sensitivity tests. Core variables and legacy segmentation are preserved for continuity, with some reweighting evident in the coefficients.

## Changes
- Addition: **low_cash_buffer** feature (coefficient 0.68)
- Thin-file flag and short-tenure weights increased for better visibility of risk among newcomers
- Slightly lower intercept (from -2.54 to -2.42), and revised threshold (0.41 from 0.43)
- Reason-code logic expanded for liquidity risk origins

## Testing Framework
- Performance tested on the historical dataset (1,800 records)
- All candidate variables validated for missingness, drift, and stability
- Challenger-to-champion analysis performed with identical reason code export

*Both old and new scorecards are fully runnable and simulation results are archived within the internal model library.*
