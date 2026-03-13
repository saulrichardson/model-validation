# Evidence Excerpts: Q1 2026 CECL Allowance Review

The excerpts below are short raw snippets from uploaded materials or generated review artifacts.

## [BANK INPUT] `docs/methodology.md`
Documented CECL forecast and reversion assumptions cited in the horizon mismatch finding.

```text
# CECL Methodology

## Objective
Review the Q1 2026 CECL Allowance Review CECL reserve process for Redwood Regional Bank. The documented methodology states a 4-quarter reasonable-and-supportable forecast period followed by 4 quarters of straight-line reversion to long-run loss behavior.

## Segments
- Commercial Real Estate
- Commercial and Industrial
- Residential Mortgage
- Consumer Unsecured

## Key Drivers
- Unemployment rate
- GDP growth
- House price growth
- CRE price growth
- Prime rate

## Overlay Treatment
Qualitative overlays are documented as targeted adjustments capped at 5.0 bps and are not expected to change scenario ordering at segment level.
```

## [BANK INPUT] `model/cecl_engine.py`
Implemented reserve-engine constants and overlay schedule that Codex compared to the methodology and overlay memo.

```text
"cre_price_growth": 0.0,
      "prime_rate": 0.11
    }
  }
}
OVERLAYS = {
  "baseline": {
    "commercial_real_estate": 2.0,
    "commercial_and_industrial": 2.0,
    "residential_mortgage": 1.0,
    "consumer_unsecured": 3.0
  },
  "adverse": {
    "commercial_real_estate": 5.0,
    "commercial_and_industrial": 4.0,
    "residential_mortgage": 2.0,
    "consumer_unsecured": 6.0
  },
  "severe": {
    "commercial_real_estate": 8.0,
    "commercial_and_industrial": 7.0,
    "residential_mortgage": -9.0,
    "consumer_unsecured": 9.0
  }
}
FORECAST_QUARTERS = 6
REVERSION_QUARTERS = 2


def build_projection(frame: pd.DataFrame) -> pd.DataFrame:
    long_run = {
        "unemployment_rate": 4.7,
        "gdp_growth": 1.7,
        "house_price_growth": 1.9,
        "cre_price_growth": 1.4,
        "prime_rate": 5.0,
    }
    forecast = frame.iloc[:FORECAST_QUARTERS].copy()
    last = forecast.iloc[-1].copy()
    reversion_rows = []
    for step in range(1, REVERSION_QUARTERS + 1):
        weight = step / REVERSION_QUARTERS
        row = {"quarter": f"reversion_{step}"}
        for key, long_run_value in long_run.items():
            row[key] = round(float(last[key]) + (long_run_value - float(last[key])) * weight, 4)
        reversion_rows.append(row)
```

## [BANK INPUT] `docs/overlay_memo.md`
Documented overlay cap and severe overlay posture used in the overlay-governance challenge.

```text
# Overlay Memo

Management overlays are described as targeted and modest, capped at 5.0 bps by segment-scenario combination. The documented intent is to preserve scenario ordering while capturing qualitative risks not fully represented in the core reserve engine.
```

## [BANK INPUT] `docs/scenario_assumptions.md`
Documented scenario narrative that Codex challenged against quantitative reserve behavior and the packaged scenario definitions.

```text
# Scenario Assumptions

Baseline, adverse, and severe scenarios were prepared by Finance. Severe is described as a uniformly harsher path than adverse, with higher unemployment, lower GDP growth, and weaker real-estate prices across the modeled horizon.

The review should therefore expect total reserve and segment reserve ordering to be baseline, then adverse, then severe, absent a clearly documented exception.
```

## [CODEX OUTPUT] `outputs/support/documentation_crosscheck.md`
Codex-generated documentation challenge summarizing the forecast, reversion, overlay, and segment-level inconsistencies identified during the review.

```text
# Documentation Cross-Check

## Methodology versus implementation
The written methodology and model overview describe a different forecast and reversion treatment than the reserve engine actually uses.

- Evidence: docs/methodology.md, docs/model_overview.md, model/cecl_engine.py
- Documented forecast quarters: 4
- Implemented forecast quarters: 6
- Documented reversion quarters: 4
- Implemented reversion quarters: 2

## Overlay posture
The overlay memo understates the magnitude of the overlay table used in the actual scenario runs.

- Evidence: docs/overlay_memo.md, data/overlay_schedule.csv, outputs/support/sensitivity_results.csv
- Documented overlay cap: 5.0 bps
- Actual overlay cap in schedule: 9.0 bps

## Scenario reasonableness
Overall reserve monotonicity is intact, but one segment behaves oddly under the severe scenario.

- Evidence: outputs/support/segment_reserve_comparison.csv, docs/scenario_assumptions.md, docs/overlay_memo.md
- Overall reserve ordering: baseline 4876841.47, adverse 7132021.97, severe 8287703.47
- Anomaly segment: residential_mortgage
- Adverse versus severe segment delta: -109988.30
```

## [CODEX OUTPUT] `outputs/support/review_strategy.md`
Codex-generated planning record showing how the review questions and procedures were selected from the discovered evidence.

```text
## Review Questions
1. Does the package contain enough evidence to support a full execution-based CECL review rather than a documentation-only assessment?
2. Can the supplied baseline reserve be reproduced from the packaged reserve engine, portfolio data, and baseline scenario?
3. Do reserve outputs move directionally and materially across Baseline, Adverse, and Severe scenarios both overall and by major segment?
4. How sensitive are reserves to forecast horizon, reversion speed, macro severity, and overlay magnitude assumptions?
5. Do the methodology, scenario, and overlay documents faithfully describe the behavior observed in the implemented CECL process, especially for Residential Mortgage?
```
