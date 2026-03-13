# Model Overview - CECL Reserve Engine (Q1 2026)

## Model identification
- **Bank:** Redwood Regional Bank
- **Review name:** Q1 2026 CECL Allowance Review
- **Portfolio context:** regional bank commercial and retail loan portfolio
- **Segmentation:** CRE, C&I, Residential Mortgage, Consumer Unsecured

## Conceptual design
The CECL engine produces life-of-loan expected credit losses using a scenario-conditioned PD/LGD/EAD approach. The model is designed to be transparent at the segment level while retaining loan-level granularity for risk attributes and remaining term.

### Core components
1. **Data and segmentation**
   - Loan-level attributes mapped to one of four segments.
   - Risk attributes used for sensitivity and reasonableness checks include: FICO (where applicable), LTV, DTI, DSCR, utilization, payment shock, remaining term, and internal risk rating.

2. **Macroeconomic conditioning**
   - Scenario paths are provided quarterly for unemployment rate, GDP growth, house price growth, CRE price growth, and prime rate.
   - Each segment applies its own macro sensitivity vector, reflecting different loss drivers (e.g., house price growth is more influential for Residential Mortgage; CRE price growth more influential for CRE).

3. **Default modeling (PD)**
   - PD is driven by a segment base intercept and incremental effects from macroeconomic variables.
   - The framework supports scenario-based PD term structures over the remaining term.

4. **Severity modeling (LGD)**
   - LGD begins with a segment base LGD level and reflects collateral and segment behavior.
   - For secured portfolios, the approach is intended to be consistent with observed loss severity dynamics over collateral cycles.

5. **Exposure (EAD)**
   - For term loans, EAD is primarily current balance net of expected amortization.
   - For revolving exposures, EAD considers utilization behavior consistent with line usage patterns.

6. **Qualitative overlays**
   - Segment/scenario bps overlays are applied as a top-of-model adjustment to capture risks not fully represented in the quantitative model.
   - A documented overlay cap exists (5.0 bps), subject to governance.

## Portfolio segmentation summary (review reference)
| Segment | Mix weight | Base intercept | Base LGD |
|---|---:|---:|---:|
| Commercial Real Estate | 0.27 | -2.90 | 0.34 |
| Commercial & Industrial | 0.25 | -2.72 | 0.30 |
| Residential Mortgage | 0.28 | -3.18 | 0.18 |
| Consumer Unsecured | 0.20 | -2.40 | 0.61 |

## Expected model behavior under scenarios
- **Baseline:** stable losses with modest sensitivity to macro normalization.
- **Adverse:** higher PDs and/or severities driven by weaker GDP growth, higher unemployment, and negative asset-price growth.
- **Severe:** peak stress conditions should generally produce the highest losses, with particular sensitivity in segments linked to unemployment and collateral price indices.

## Key review emphasis areas
- **Horizon/reversion alignment:** confirm the engine's applied forecast/reversion settings align with the documented standard.
- **Scenario ordering tests:** confirm severe losses are generally ≥ adverse losses by segment absent an explainable structural feature.
- **Overlay interaction:** confirm overlays do not unintentionally invert scenario ordering or introduce non-intuitive directional results.
