# Redwood Regional Bank - CECL Model Overview (Q1 2026)

## Model identification
- **Bank:** Redwood Regional Bank
- **Portfolio/Use:** Q1 2026 CECL Allowance Review
- **Coverage:** Regional bank commercial and retail loan portfolio
- **Review sample size:** 1,200 loans (review/testing sample)
- **Random seed (sampling/repro):** 23

## Segment inventory and key risk attributes
### 1) Commercial Real Estate (CRE)
- Mix weight: **0.27**
- Typical attributes used in risk differentiation (ranges observed/used in testing context):
  - Balance: **$250k-$2.2MM**
  - FICO: **640-770**
  - LTV: **0.52-0.84**
  - DTI: **0.18-0.48**
  - DSCR: **0.95-1.65**
  - Utilization: **0.22-0.78**
  - Payment shock: **0.02-0.24**
  - Remaining term: **6-20 years**
  - Risk rating: **3-8**
- PD anchor (base intercept): **-2.9**
- LGD base: **0.34**
- Macro sensitivity emphasis: **CRE price growth (0.31)**, GDP growth (0.24), unemployment (0.22)

### 2) Commercial & Industrial (C&I)
- Mix weight: **0.25**
- Balance: **$125k-$1.8MM**; FICO **620-760**
- LTV: **0.20-0.68**; DSCR: **0.88-1.58**; Risk rating: **4-9**
- PD anchor: **-2.72**
- LGD base: **0.30**
- Macro sensitivity emphasis: **GDP growth (0.29)**, unemployment (0.19), prime rate (0.15)

### 3) Residential Mortgage
- Mix weight: **0.28**
- Balance: **$95k-$540k**; FICO **655-805**
- LTV: **0.48-0.91**; DTI **0.16-0.50**
- PD anchor: **-3.18**
- LGD base: **0.18**
- Macro sensitivity emphasis: **house price growth (0.39)**, unemployment (0.15)

### 4) Consumer Unsecured
- Mix weight: **0.20**
- Balance: **$2.5k-$32k**; FICO **585-735**
- DTI **0.20-0.62**; Utilization **0.26-0.94**
- PD anchor: **-2.40**
- LGD base: **0.61**
- Macro sensitivity emphasis: **unemployment (0.33)**, GDP growth (0.17)

## Scenario framework used in the engine
- Quarterly macro paths are provided for **Baseline**, **Adverse**, and **Severe** scenarios from **2026Q1 to 2027Q4**.
- The engine consumes unemployment, GDP growth, house price growth, CRE price growth, and prime rate each quarter.

## Implementation note (engine behavior vs. documentation)
The reserve engine's configured horizon settings materially influence outputs. The current implementation applies:

- **Implemented forecast period:** **6 quarters**
- **Implemented reversion period:** **2 quarters**

This differs from the documented policy horizon (4-quarter forecast and 4-quarter reversion) and can shift loss timing and scenario sensitivity, particularly in scenarios where stress peaks early and recovery differs across adverse vs. severe paths.

## Key review focus areas
- Horizon alignment (documented vs. implemented) and impact to allowance.
- Directional reasonableness across scenarios at segment level.
- Overlay governance, including adherence to the **5.0 bps** documented cap and transparency of effective overlay magnitude.
