# Validation Test Plan: Installment Lending Threshold Recalibration

## Scope
Full end-to-end review for revalidated candidate, including:

- Documentation completeness
- Data integrity
- Model logic, coefficients, and intercepts
- Approval threshold implementation
- Reason code generation
- Model output stability

## Test Phases

1. **Data Integrity & Sampling**
   - Confirm sample size and representativeness (n = 1,600, seed 77)
   - Check development/validation splits

2. **Model Reproduction**
   - Score consistency champion vs candidate
   - Confirm coefficient migration for _bureau_headroom_, _dti_ratio_, etc.
   - Validate addition of _low_cash_buffer_ in candidate

3. **Threshold Policy Check**
   - Approvals/declines at each threshold (0.35–0.43)
   - Implementation check: 0.39 cutoff in configured flows
   - Confirm documentation lags (0.40) do not affect ops

4. **Reason Code Review**
   - Trigger all mapped codes via negative test cases
   - Confirm _low_cash_buffer_ can be triggered, but is not mapped

5. **Monitoring Preparedness**
   - Score drift and monthly/quarterly monitoring template walkthrough
   - Thin file monitoring gap acknowledged in plan

## Acceptance Criteria
- Minimum coverage ratio: 0.72 (achieved)
- No known critical defects in scoring or threshold logic
- Documentation issues logged for stale references and incomplete mappings
