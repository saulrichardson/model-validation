# Redwood Regional Bank - CECL Methodology Summary

## Purpose and scope
This methodology describes the Current Expected Credit Loss (CECL) allowance estimation approach used for **Redwood Regional Bank** for the **Q1 2026 CECL Allowance Review**, covering the bank's **regional commercial and retail loan portfolio**. The approach is designed to generate segment-level lifetime expected credit losses through a PD/LGD framework with macroeconomic conditioning and management overlays.

## Portfolio segmentation
The allowance is produced for four segments (mix weights shown for context):

- **Commercial Real Estate (CRE)** - 27%
- **Commercial and Industrial (C&I)** - 25%
- **Residential Mortgage** - 28%
- **Consumer Unsecured** - 20%

Segmentation is intended to align with risk drivers and available risk attributes (e.g., FICO, LTV, DTI/DSCR, utilization, risk ratings, remaining term).

## Modeling approach (PD/LGD with macro conditioning)
### Probability of default (PD)
- Segment-level PD is produced from a logistic-style risk score framework anchored by a **segment base intercept** and adjusted by borrower/loan attributes and macroeconomic drivers.
- Macro drivers used across segments:
  - **Unemployment rate**
  - **GDP growth**
  - **House price growth**
  - **CRE price growth**
  - **Prime rate**
- Each segment applies distinct macro sensitivities (relative emphasis differs by segment; e.g., CRE is more sensitive to CRE price growth; Residential Mortgage is more sensitive to house price growth; Consumer Unsecured is more sensitive to unemployment).

### Loss given default (LGD)
- LGD is modeled at the segment level using a **base LGD** parameter and is applied to defaulted exposure to generate loss severity.
- Collateral-driven segments (Residential Mortgage, CRE) incorporate collateral sensitivity primarily through LTV and collateral price indices.

### Exposure and timing
- Expected losses are produced over remaining contractual life (subject to CECL adjustments for expected prepayments, if applicable per internal configuration) and then discounted/aggregated per the bank's CECL reporting conventions.

## Economic scenarios and weighting
The methodology supports three internally applied macroeconomic scenarios:

- **Baseline**
- **Adverse**
- **Severe**

Each scenario provides quarterly paths for the macro variables listed above for eight quarters (2026Q1-2027Q4). Scenario weights are governed by management's quarterly CECL governance process (documented in governance minutes).

## Documented forecast and reversion framework (policy)
The CECL policy documentation specifies:

- **Documented forecast period:** **4 quarters**
- **Documented reversion period:** **4 quarters**

Per documentation, the model is expected to:
1. Apply scenario macro paths explicitly for the first **4 quarters** (reasonable and supportable period).
2. Revert key macro variables (or modeled PD/LGD outputs, per implementation design) back to long-run levels over the subsequent **4 quarters**.

This documented horizon and reversion is intended to be consistently applied across segments and scenarios to ensure comparability and stable model behavior.

## Qualitative overlays (management adjustments)
- Management overlays are applied as additive **basis point (bps)** adjustments at the segment level, by scenario.
- A **documented overlay cap of 5.0 bps** is maintained as a governance constraint.
- Overlay intent is to address limitations not fully captured by the quantitative model (e.g., emerging risk, known data gaps, idiosyncratic portfolio changes).

## Known limitations and model risk considerations
- The approach is sensitive to:
  - Scenario design and timing of macro deterioration/recovery.
  - Collateral index behavior (house price vs. CRE price).
  - Segment overlay posture (especially in stress scenarios).
- Directional reasonableness checks (e.g., severe vs. adverse ordering) are required at each quarter-end, with exceptions documented and escalated.
