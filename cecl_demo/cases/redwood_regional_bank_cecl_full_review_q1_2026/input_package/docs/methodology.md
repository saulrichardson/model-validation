# Redwood Regional Bank - Q1 2026 CECL Allowance Review

## Purpose and scope
This methodology documents the Current Expected Credit Loss (CECL) framework applied to Redwood Regional Bank's **regional bank commercial and retail loan portfolio** for the **Q1 2026 CECL Allowance Review**. The scope covers model segmentation, scenario-based macroeconomic forecasting, probability of default (PD) and loss given default (LGD) estimation, life-of-loan expected credit loss measurement, and the application of qualitative adjustments ("Q-factors" / overlays).

**Population and sampling context (for review testing):** A stratified sample of **1,200 loans** was used for independent reasonableness checks and replicate-run testing (RNG seed: **23**).

## Portfolio segmentation
The allowance is produced at the following segments, consistent with product and risk management reporting:

- **Commercial Real Estate (CRE)** (mix weight: 0.27)
- **Commercial and Industrial (C&I)** (mix weight: 0.25)
- **Residential Mortgage** (mix weight: 0.28)
- **Consumer Unsecured** (mix weight: 0.20)

Each segment uses segment-specific drivers and parameterization, including a base PD intercept and base LGD level. Key obligor/loan attributes considered in the quantitative framework include, as applicable: balance, FICO, LTV, DTI, DSCR, utilization, payment shock, remaining term, and risk rating.

## Loss measurement framework (PD/LGD/EAD)
### Overview
Expected credit losses are estimated using a lifetime approach at the loan level and aggregated to segment totals. The core structure follows:

- **PD:** quarterly (or equivalent) default likelihood derived from a segment-level logit-style specification, incorporating macroeconomic factors and risk attributes.
- **LGD:** segment-level base LGD adjusted for collateral and macro/market conditions where applicable.
- **EAD:** exposure at default based on contractual balances and utilization dynamics for revolving exposures.

Losses are discounted/accumulated over remaining term and aggregated to the reporting level.

### Segment parameterization (review reference)
The model specification uses segment-specific base intercepts and base LGDs:

- **CRE:** intercept -2.90; LGD base 0.34
- **C&I:** intercept -2.72; LGD base 0.30
- **Residential Mortgage:** intercept -3.18; LGD base 0.18
- **Consumer Unsecured:** intercept -2.40; LGD base 0.61

Macro sensitivities are applied by segment to the following drivers: unemployment rate, GDP growth, house price growth, CRE price growth, and prime rate.

## Macroeconomic scenarios
### Scenario set
The CECL process uses three internally approved macroeconomic paths (quarters 2026Q1-2027Q4):

- **Baseline**
- **Adverse**
- **Severe**

Scenarios include trajectories for: unemployment rate, GDP growth, house price growth, CRE price growth, and prime rate.

### Scenario incorporation
Segment PDs are linked to macroeconomic factors using the segment sensitivity structure. Scenario impacts flow through to lifetime loss via the forecast horizon and the reversion methodology described below.

## Forecast horizon and reversion (documented)
### Documented assumptions
For this review package, the **documented** CECL forecast and reversion approach is:

- **Documented forecast horizon:** **4 quarters** of explicit macroeconomic scenario input.
- **Documented reversion period:** **4 quarters** of straight-line reversion from the end of the forecast horizon to long-run (through-the-cycle) macro conditions / model steady-state.

Accordingly, macroeconomic inputs are expected to be applied as follows:

1. **Quarters 1-4:** use scenario macro values explicitly.
2. **Quarters 5-8:** linearly revert macro variables (and any dependent model components) to long-run levels.
3. **Thereafter:** hold at long-run levels for remaining life-of-loan.

These documented assumptions are intended to support consistent period-over-period comparisons and alignment with governance-approved modeling standards.

## Qualitative adjustments (overlays)
Qualitative overlays are applied as **basis point (bps) adjustments** by scenario and segment to address limitations not fully captured by the quantitative framework (e.g., model uncertainty, idiosyncratic portfolio risks, operational factors, emerging risk not yet present in historical data).

A governance cap is documented as:

- **Documented overlay cap:** **5.0 bps**

Overlay schedules are maintained for baseline/adverse/severe and applied at segment level.

## Model outputs and reporting
Primary outputs include:

- Segment-level and total allowance amount
- Allowance rate (bps) by segment
- Scenario-specified losses and sensitivities
- Key drivers and change analysis versus prior quarter

## Known methodological focus areas for Q1 2026 review
This review is explicitly designed to validate:

- Alignment between **documented** horizon/reversion assumptions and the reserve engine implementation.
- Directional reasonableness of scenario ordering at the segment level, particularly where macro paths and overlays interact.
- Clarity and proportionality of qualitative overlay communication relative to effect.
