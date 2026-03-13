# Validation Test Plan: Installment Refresh 2025 Q1

## Sample and Methods
- Holdout sample: 1,800 anonymized retail applications from 2024 (including legacy segment distribution)
- Both champion (2024.9) and candidate (2025.1) models run on identical data
- Direct comparison: AUC, Gini, approval/denial rates, and reason code frequencies

## Tests
1. **Score Distribution Analysis:** Empirical logit and Kolmogorov-Smirnov distance for score shift
2. **Threshold Sensitivity:** Analyze performance and coverage across: 0.37, 0.39, 0.41, 0.43, 0.45
3. **Segmented Approval Trends:** Assess thin-file, low cash buffer, short-tenure, and combined segment impact
4. **Reason-Code Integrity:** Map observed denials back to reason code assignment per bank mapping
5. **Stability Analysis:** Check missingness, outlier impact, and potential bias introduction for new/changed variables

## Pass Criteria
- Minimum coverage ratio: 0.85 at candidate threshold
- AUC must not deteriorate vs. champion
- Reason code coverage for LOW_CASH_BUFFER maintained >90% accuracy in system extracts
- No unexplained adverse shift in segment approval rates
