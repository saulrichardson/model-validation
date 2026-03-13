# Scenario Assumptions (Numeric Paths) and Alignment Assessment

**Bank:** Harborlight Savings  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment

## 1. Scenario Set Included in This Package
Three macroeconomic scenarios were provided in numeric form:
- Baseline
- Adverse
- Severe

The numeric paths below cover **2026Q1-2027Q2** (6 quarters). No documented path was provided for quarters beyond 2027Q2 in the materials delivered for this review.

## 2. Baseline Scenario (Numeric Path Provided)
| Quarter | Unemployment (%) | GDP growth (%) | House price growth (%) | CRE price growth (%) | Prime rate (%) |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 4.8 | 1.8 | 2.2 | 1.6 | 5.25 |
| 2026Q2 | 4.8 | 1.8 | 2.0 | 1.5 | 5.15 |
| 2026Q3 | 4.9 | 1.7 | 1.9 | 1.4 | 5.05 |
| 2026Q4 | 4.9 | 1.7 | 1.8 | 1.3 | 5.00 |
| 2027Q1 | 4.8 | 1.7 | 1.9 | 1.4 | 4.95 |
| 2027Q2 | 4.8 | 1.7 | 1.9 | 1.4 | 4.90 |

## 3. Adverse Scenario (Numeric Path Provided)
| Quarter | Unemployment (%) | GDP growth (%) | House price growth (%) | CRE price growth (%) | Prime rate (%) |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 5.5 | 0.8 | -1.8 | -2.5 | 5.55 |
| 2026Q2 | 6.0 | 0.2 | -3.6 | -4.3 | 5.70 |
| 2026Q3 | 6.3 | -0.3 | -4.5 | -5.1 | 5.70 |
| 2026Q4 | 6.1 | 0.1 | -3.9 | -4.2 | 5.55 |
| 2027Q1 | 5.7 | 0.4 | -2.1 | -2.2 | 5.35 |
| 2027Q2 | 5.3 | 0.8 | -0.8 | -1.0 | 5.15 |

## 4. Severe Scenario (Numeric Path Provided)
| Quarter | Unemployment (%) | GDP growth (%) | House price growth (%) | CRE price growth (%) | Prime rate (%) |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 6.1 | 0.0 | -2.3 | -3.8 | 5.80 |
| 2026Q2 | 6.9 | -0.9 | -4.1 | -6.0 | 5.95 |
| 2026Q3 | 7.5 | -1.4 | -3.8 | -6.4 | 5.95 |
| 2026Q4 | 7.0 | -0.7 | -2.5 | -4.8 | 5.75 |
| 2027Q1 | 6.3 | 0.0 | -0.6 | -2.5 | 5.45 |
| 2027Q2 | 5.7 | 0.5 | 0.2 | -1.2 | 5.20 |

## 5. Alignment Assessment (Narrative vs Numeric)
### 5.1 Expected alignment artifacts
For supervisory-ready documentation, we expect:
- Scenario narratives that explicitly describe the timing and severity reflected in the numeric paths
- A mapping showing which macro variables drive each segment and how they are applied
- Evidence that scenario paths align to the forecast horizon stated in methodology/model card

### 5.2 Observed issues
1) **Horizon mismatch with documentation:**
   - Methodology states an **8-quarter** forecast and **4-quarter** reversion.
   - Model card states a **6-quarter** forecast and **2-quarter** reversion.
   - Numeric scenario paths provided in this package include **6 quarters only**, and do not evidence the additional quarters or reversion mechanics.

2) **Severe scenario narrative not fully aligned:**
   - The severe path shows peak unemployment in **2026Q3 (7.5%)** with GDP trough in **2026Q3 (-1.4%)**, followed by partial improvement by 2027Q2.
   - The severe path also shows **house price growth turning slightly positive (0.2%) by 2027Q2** while **CRE price growth remains negative (-1.2%)**.
   - The narrative provided for "Severe" (as referenced in meeting notes) is described as a "prolonged contraction with sustained real estate declines." This description is not fully supported by the numeric improvement in house price growth by 2027Q2.

3) **Scenario governance evidence missing:**
   - No committee-approved scenario selection/weights memo provided.
   - No evidence of quarterly scenario refresh cadence or controls over scenario file versioning.

## 6. Open Items
- Provide scenario paths covering the full forecast horizon as implemented, including reversion quarters and long-run assumptions.
- Provide approved scenario narrative(s) tied to the numeric paths and dated committee approval.
- Provide scenario-to-segment mapping documentation (variable usage, lags, functional forms).
