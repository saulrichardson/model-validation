# Implementation Runbook: Installment Threshold Policy Change

## Prerequisites
- Candidate scorecard (v2025.2) reviewed and approved
- Scoring pipeline updated with latest coefficients and new feature (low_cash_buffer)
- Input data mart locked (sample: n = 1,600, seed 77)

## Step-by-Step Execution

1. **Cutover Preparation**
   - Final UAT pass; verify champion/candidate scoring outputs
   - Backup of all current configuration and baseline champion (v2024.4)

2. **Configuration**
   - Update threshold parameter from 0.42 to 0.39 in approval logic
   - Verify all coefficient updates
   - Admission of _low_cash_buffer_ to scoring; reason-code mapping left unchanged at this stage

3. **Deployment**
   - Deploy candidate model to production endpoint
   - Confirm real-time scoring and reason-code output
   - Validate capture rates in first 100 live applicant records

4. **Post-Deployment Monitoring**
   - Initiate monthly and quarterly dashboards as per monitoring plan
   - Watch for unexpected drift, particularly thin-file approvals and cash buffer flagged records

5. **Documentation & Governance**
   - Circulate updated model deployment checklist
   - Log documentation lag on threshold and reason code mapping for governance visibility

## Rollback Protocol
- Revert to champion configuration and re-enable 0.42 threshold upon critical error

## Contacts
- Implementation Lead: T. Brooks
- Risk Systems: S. Vega
- Ops Escalation: L. O'Neil
