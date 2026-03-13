# Model Overview - Redwood Regional Bank CECL Reserve Engine (Q1 2026)

## 1. Model purpose
The CECL reserve engine estimates lifetime expected credit losses for Redwood Regional Bank's commercial and retail portfolio as of Q1 2026 and supports financial reporting, risk monitoring, and governance decisioning.

## 2. Portfolio coverage and segmentation
The engine operates at loan level and aggregates to four reportable segments:
1. **Commercial Real Estate** (mix weight 0.27)
2. **Commercial & Industrial** (mix weight 0.25)
3. **Residential Mortgage** (mix weight 0.28)
4. **Consumer Unsecured** (mix weight 0.20)

Segment definitions are aligned to internal risk reporting and underwriting programs.

## 3. Core modeling structure
### 3.1 Credit loss components
The engine follows a PD/LGD/EAD structure:
- **PD:** quarterly default propensity based on borrower/loan risk factors and macroeconomic variables.
- **LGD:** segment base LGD adjusted by collateral and macro context where applicable.
- **EAD:** exposure at default driven by balance dynamics, term structure, and utilization for revolving products.

### 3.2 Macro sensitivity by segment
Macro sensitivities translate scenario paths into PD/LGD pressure. The engine uses a fixed sensitivity vector per segment:

**Commercial Real Estate**: unemployment 0.22; GDP 0.24; house price 0.06; CRE price 0.31; prime 0.12

**Commercial & Industrial**: unemployment 0.19; GDP 0.29; house price 0.04; CRE price 0.11; prime 0.15

**Residential Mortgage**: unemployment 0.15; GDP 0.12; house price 0.39; CRE price 0.02; prime 0.08

**Consumer Unsecured**: unemployment 0.33; GDP 0.17; house price 0.00; CRE price 0.00; prime 0.11

These sensitivities are applied consistently across scenarios to generate scenario-differentiated loss estimates.

## 4. Key segment anchors (intercepts and LGD bases)
The engine uses the following segment anchors:

| Segment | PD intercept (baseline index) | Base LGD |
|---|---:|---:|
| CRE | -2.90 | 0.34 |
| C&I | -2.72 | 0.30 |
| Residential Mortgage | -3.18 | 0.18 |
| Consumer Unsecured | -2.40 | 0.61 |

## 5. Scenario execution
The engine runs three macroeconomic scenarios (Baseline/Adverse/Severe) with quarterly macro inputs from 2026Q1 through 2027Q4. Scenario ordering is expected to be monotonic in aggregate (Severe ≥ Adverse ≥ Baseline) absent offsetting features (e.g., rapid recoveries, collateral effects, or overlay mechanics).

## 6. Overlay integration
Overlays are applied as bps-of-exposure add-ons at the segment/scenario level and included in final reporting. The overlay framework is intended to be conservative and disciplined via a documented cap.

## 7. Outputs
Standard outputs include:
- ACL by segment and total under Baseline/Adverse/Severe
- Overlay impact by segment/scenario
- Key driver reporting (macro contributions, risk rating/FICO stratifications)
- Directionality checks and quarter-over-quarter variance explanations

## 8. Known model risk focus areas for this review
- Alignment of documented forecast/reversion assumptions to the implemented reserve engine.
- Reasonableness of Residential Mortgage results under Severe vs. Adverse given scenario paths and overlay schedule.
- Transparency of qualitative overlay magnitude relative to narrative framing.
