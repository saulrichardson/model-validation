# Monitoring Plan: Meridian HELOC Underwriting Model (Q1 2024)

## Objective
Establish initial monitoring proposal for deployed HELOC model. Tracking efficacy, fairness, and operational drift post-launch.

## Monitoring Metrics
- **Score distribution shifts**: Monthly KS, mean, and quantile drift
- **Approval rate change**: Rolling quarterly lookback
- **Population stability index (PSI):** Monthly, by region
- **Model performance:** FPR, AUC, and observed default rates against development expectations
- **Resilience reason code utilization:** Monitor impact of unmapped variables on adverse outcomes.

## Data and Runtime Artifacts
Monitoring designs reference automated runtime dashboards and baseline alert triggers. However, these artifacts are not included in the current readiness package and will be delivered post-vendor handover.

## Escalation Procedures
Material deviation from model expectations, particularly due to unmapped features (payment_shock_index, verified_income_stability), to prompt urgent review and temporary override until addressed.

## Next Steps
- Onboard production monitoring scripts upon availability of vendor implementation.
- Populate first-quarter monitoring report following two full calendar months of operation.

*Note: Full monitoring pipeline is not within this package. Evidence requested for future validation milestone.*
