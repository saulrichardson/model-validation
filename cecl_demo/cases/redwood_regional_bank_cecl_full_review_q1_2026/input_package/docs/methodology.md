# Redwood Regional Bank - Q1 2026 CECL Allowance Review

## 1. Purpose and scope
This methodology describes the quantitative and qualitative approach used for the **Q1 2026 CECL Allowance Review** for Redwood Regional Bank's **regional bank commercial and retail loan portfolio**. The review covers model design, segmentation, macroeconomic forecasting, PD/LGD/EAD framework, scenario application, and qualitative adjustments (overlays) for the ACL estimate.

**Population / sample context.** The review package references an analytic sample of **1,200 loans** for benchmarking, sensitivity testing, and reproducibility checks.

## 2. Portfolio segmentation
The allowance framework is segmented to align risk drivers and loss dynamics. Segment weights reflect the portfolio mix used in reporting and rollups.

| Segment | Mix weight | Primary risk attributes considered |
|---|---:|---|
| Commercial Real Estate (CRE) | 0.27 | Risk rating, DSCR, LTV, utilization, payment shock, term |
| Commercial & Industrial (C&I) | 0.25 | Risk rating, DSCR, utilization, payment shock, term |
| Residential Mortgage | 0.28 | FICO, LTV, DTI, payment shock, term |
| Consumer Unsecured | 0.20 | FICO, DTI, utilization, payment shock, term |

## 3. Data inputs and feature construction
### 3.1 Loan-level inputs
The reserve engine uses loan-level attributes consistent with segment characteristics, including:
- Exposure measures: current balance and utilization
- Credit quality: risk rating (commercial), FICO (retail)
- Repayment capacity: DSCR and DTI (as applicable)
- Collateral/structure: LTV (secured), remaining term
- Interest-rate sensitivity proxy: payment shock

### 3.2 Macroeconomic variables
The quantitative framework uses a common macro set across segments:
- Unemployment rate
- GDP growth
- House price growth
- CRE price growth
- Prime rate

Segment-level macro sensitivities are applied to translate scenario paths into changes in loss expectations.

## 4. Scenario framework
### 4.1 Scenarios
The ACL is evaluated under three internally-defined paths:
- **Baseline**: moderate growth, stable unemployment, modest asset-price growth, gradual rate normalization.
- **Adverse**: rising unemployment, temporary negative GDP growth, sustained declines in house/CRE prices, higher rates early.
- **Severe**: larger near-term shock to unemployment and GDP, deeper price declines followed by partial recovery.

Scenario paths are defined at a quarterly frequency for **2026Q1 through 2027Q4** and applied consistently across segments.

### 4.2 Scenario application
The reserve engine produces segment-level expected credit losses by applying scenario-specific macro paths to PD and LGD components through documented segment sensitivities. Results are aggregated to the total ACL through segment weighting and exposure rollups.

## 5. Core quantitative approach (PD/LGD/EAD)
### 5.1 PD framework
For each segment, default propensity is modeled with a logistic-style structure combining:
- A segment-specific baseline intercept
- Loan-level risk drivers (e.g., risk rating/FICO, DSCR, LTV/DTI, utilization, payment shock, remaining term)
- Macro adjustments using the segment macro sensitivity vector

The methodology assumes macro variables act as additive drivers to the latent credit index and therefore shift quarterly PDs in a scenario-consistent manner.

### 5.2 LGD framework
LGD is modeled using a segment base LGD with sensitivity to collateral-linked macro factors where applicable:
- Secured portfolios (CRE, Residential Mortgage) incorporate house/CRE price growth effects implicitly through the macro sensitivity structure and collateral metrics.
- Unsecured portfolios (Consumer Unsecured) are driven more heavily by unemployment and utilization.

Base LGD anchors by segment:
- CRE: 0.34
- C&I: 0.30
- Residential Mortgage: 0.18
- Consumer Unsecured: 0.61

### 5.3 EAD considerations
For amortizing exposures, EAD follows contractual balance run-off assumptions and remaining term. For revolving exposures, utilization is used as an exposure proxy and may be stressed through scenario response where applicable.

## 6. Documented forecast and reversion approach (must be applied as stated)
The **documented** CECL methodology for macroeconomic incorporation is:

- **Forecast horizon:** **4 quarters** of explicit macroeconomic forecasts.
- **Reversion period:** **4 quarters** of linear reversion from the end of the forecast horizon to long-run macro conditions.

Accordingly, the methodology requires:
1. Quarters **1-4**: scenario macro paths applied explicitly.
2. Quarters **5-8**: macro variables **revert linearly** from the quarter-4 level to long-run levels.
3. Thereafter: macro variables held at long-run levels for remaining contractual life calculations.

This horizon and reversion structure is a key model governance assumption and is expected to be implemented consistently across scenarios and segments.

## 7. Qualitative adjustments (overlays)
### 7.1 Overlay intent
Overlays are applied to address known model limitations, emerging risks, and factors not fully captured in historical performance or model structure (e.g., idiosyncratic concentrations, recent underwriting shifts, operational frictions, or data gaps).

### 7.2 Overlay measurement convention
Overlays are expressed as **basis points (bps) of segment exposure**, applied by scenario and segment, and then rolled up to the total ACL impact.

### 7.3 Documented overlay cap
The **documented overlay cap is 5.0 bps**, intended to limit the magnitude of qualitative adjustments absent explicit executive approval and formal documentation.

## 8. Model outputs and reporting
Key outputs produced for management reporting and governance:
- Segment ECL and total ACL by scenario
- Key driver decompositions (macro vs. idiosyncratic)
- Overlay impacts by segment and scenario
- Reasonableness checks (directionality, stability, quarter-over-quarter movements)

## 9. Model limitations (methodology-level)
- The framework relies on stable relationships between macro variables and credit losses; regime changes may not be fully captured.
- Segment sensitivity vectors are simplified representations and may not capture non-linearities or threshold effects.
- Directional checks are required to confirm scenario ordering and internal consistency, especially where macro paths include partial recoveries.

## 10. Governance and change control expectations
Any changes to forecast horizon, reversion period, scenario definitions, overlay cap usage, or segmentation must be:
- documented,
- tested,
- approved through the appropriate governance committee,
- and implemented with full reproducibility controls (versioning, parameter archiving, and independent review).
