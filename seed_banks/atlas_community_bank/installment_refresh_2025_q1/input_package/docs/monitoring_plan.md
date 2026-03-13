# Monitoring Plan: Installment Refresh 2025 Q1

**Scope:** Post-implementation performance and governance for credit underwriting model v2025.1

## Key Monitoring Items
- Approval rate, denial rate, and adverse action reason codes, by overall and segment (notably thin-file and low-cash-buffer exposed)
- AUC and Gini to be tracked quarterly
- Special focus: Uptick in "LOW_CASH_BUFFER" reason code, especially under downturn macro conditions

## Alerts and Escalation
- Material directional drift in approval/discrimination rates triggers Model Risk Committee notification
- Emerging pattern: If "LOW_CASH_BUFFER" becomes top 2 reason code in any month, flag for model owner

## Data
- Monthly, automated extract from origination/servicing systems
- Monitoring dashboards refreshed quarterly, with escalation protocol for significant shift

## Coverage
- Minimum coverage ratio (0.85) enforced in all routine monitoring
- Segment monitoring aligned to last revalidation findings
