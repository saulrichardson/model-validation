# Harborlight Savings - Scenario Assumptions and Narrative Alignment Memo (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment

## 1. Purpose
To document the macroeconomic scenario paths supplied for CECL readiness review and assess alignment between numeric paths and any scenario narrative statements available in the package.

## 2. Scenario inventory (numeric paths provided)
**Horizon provided in this package:** 6 quarters (2026Q1-2027Q2) for each scenario.

### 2.1 Baseline scenario (2026Q1-2027Q2)
| Quarter | Unemployment | GDP growth | HPI growth | CRE price growth | Prime rate |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 4.8 | 1.8 | 2.2 | 1.6 | 5.25 |
| 2026Q2 | 4.8 | 1.8 | 2.0 | 1.5 | 5.15 |
| 2026Q3 | 4.9 | 1.7 | 1.9 | 1.4 | 5.05 |
| 2026Q4 | 4.9 | 1.7 | 1.8 | 1.3 | 5.00 |
| 2027Q1 | 4.8 | 1.7 | 1.9 | 1.4 | 4.95 |
| 2027Q2 | 4.8 | 1.7 | 1.9 | 1.4 | 4.90 |

### 2.2 Adverse scenario (2026Q1-2027Q2)
| Quarter | Unemployment | GDP growth | HPI growth | CRE price growth | Prime rate |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 5.5 | 0.8 | -1.8 | -2.5 | 5.55 |
| 2026Q2 | 6.0 | 0.2 | -3.6 | -4.3 | 5.70 |
| 2026Q3 | 6.3 | -0.3 | -4.5 | -5.1 | 5.70 |
| 2026Q4 | 6.1 | 0.1 | -3.9 | -4.2 | 5.55 |
| 2027Q1 | 5.7 | 0.4 | -2.1 | -2.2 | 5.35 |
| 2027Q2 | 5.3 | 0.8 | -0.8 | -1.0 | 5.15 |

### 2.3 Severe scenario (2026Q1-2027Q2)
| Quarter | Unemployment | GDP growth | HPI growth | CRE price growth | Prime rate |
|---|---:|---:|---:|---:|---:|
| 2026Q1 | 6.1 | 0.0 | -2.3 | -3.8 | 5.80 |
| 2026Q2 | 6.9 | -0.9 | -4.1 | -6.0 | 5.95 |
| 2026Q3 | 7.5 | -1.4 | -3.8 | -6.4 | 5.95 |
| 2026Q4 | 7.0 | -0.7 | -2.5 | -4.8 | 5.75 |
| 2027Q1 | 6.3 | 0.0 | -0.6 | -2.5 | 5.45 |
| 2027Q2 | 5.7 | 0.5 | 0.2 | -1.2 | 5.20 |

## 3. Narrative alignment assessment (documentation-led)
### 3.1 Severe scenario narrative vs numeric path
**Expected condition:** severe scenario narrative should explicitly reflect the depth and timing of the stress in unemployment, GDP contraction, and CRE price declines.

**Numeric path highlights (severe):**
- Unemployment peaks at **7.5% (2026Q3)** and remains elevated through 2026Q4.
- GDP growth is negative in **2026Q2 (-0.9)** and **2026Q3 (-1.4)**.
- CRE price growth reaches **-6.4% (2026Q3)** with continued negative growth through 2027Q2.
- Prime rate remains relatively high through the trough period (5.95 in 2026Q2-Q3).

**Gap (alignment):** Scenario narrative materials provided in the package do not fully align to the numeric severe path, particularly regarding:
- The stated timing of peak stress (narrative references "late 2026" broadly without identifying the 2026Q3 peak), and
- The persistence of CRE price weakness into 2027 (numeric remains negative in 2027Q2).

### 3.2 Horizon completeness vs documented forecast needs
- The methodology narrative references an **8-quarter forecast** and **4-quarter reversion**.
- The model card references a **6-quarter forecast** and **2-quarter reversion**.
- The scenario tables provided include **6 quarters only**.

**Implication:** Absent additional scenario quarters or a documented extension rule (hold-last, mean reversion of macro series, or external scenario feed), the scenario package is incomplete relative to the methodology narrative and not demonstrably sufficient to support the documented horizon.

## 4. Open items
- Provide scenario narrative memo(s) tied to the numeric tables and explicitly describing the severe path timing and persistence.
- Provide governance approval evidence for the selected forecast and reversion horizons.
- Provide documentation for scenario extension beyond 2027Q2 (if required by the approved horizon).
