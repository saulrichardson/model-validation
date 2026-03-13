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

## [BANK INPUT] `scenarios/adverse.csv + scenarios/severe.csv`
Numeric adverse and severe scenario paths that Codex compared for directional severity and segment reasonableness.

```text
[adverse.csv]
quarter,unemployment_rate,gdp_growth,house_price_growth,cre_price_growth,prime_rate
2026Q1,5.4,0.8,-1.5,-2.2,5.6
2026Q2,5.9,0.3,-3.2,-4.1,5.75
2026Q3,6.3,-0.4,-4.8,-5.6,5.75
2026Q4,6.1,-0.1,-4.4,-4.7,5.55
2027Q1,5.8,0.2,-2.8,-3.1,5.4
2027Q2,5.5,0.6,-1.3,-1.5,5.25
2027Q3,5.1,1.0,0.1,-0.4,5.1
2027Q4,4.9,1.2,0.8,0.2,5.0

[severe.csv]
quarter,unemployment_rate,gdp_growth,house_price_growth,cre_price_growth,prime_rate
2026Q1,6.0,0.2,-2.0,-3.2,5.75
2026Q2,6.9,-0.8,-4.4,-6.6,6.0
2026Q3,7.6,-1.6,-5.8,-8.0,6.05
2026Q4,7.2,-0.9,-2.9,-5.1,5.85
2027Q1,6.6,-0.2,0.4,-2.6,5.55
2027Q2,6.0,0.4,1.6,-1.0,5.3
2027Q3,5.4,0.9,1.8,0.1,5.1
2027Q4,5.0,1.2,2.0,0.6,5.0
```

## [CODEX OUTPUT] `outputs/support/baseline_reproduction.json`
Codex-generated reproduction record showing the packaged baseline reserve and the rerun reserve matched exactly.

```text
{
  "packaged_total_reserve": 4876841.47,
  "rerun_total_reserve": 4876841.47,
  "absolute_delta": 0.0,
  "pct_delta": 0.0,
  "max_loan_level_abs_delta": 0.0,
  "segment_deltas": [
    {
      "segment_id": "commercial_and_industrial",
      "reserve_amount_packaged": 1977246.19,
      "reserve_amount_rerun": 1977246.19,
      "delta": 0.0,
      "pct_delta": 0.0
    },
    {
      "segment_id": "commercial_real_estate",
      "reserve_amount_packaged": 2545519.51,
      "reserve_amount_rerun": 2545519.51,
      "delta": 0.0,
      "pct_delta": 0.0
    },
    {
      "segment_id": "consumer_unsecured",
      "reserve_amount_packaged": 100355.66,
      "reserve_amount_rerun": 100355.66,
      "delta": 0.0,
      "pct_delta": 0.0
    },
    {
      "segment_id": "residential_mortgage",
      "reserve_amount_packaged": 253720.11,
      "reserve_amount_rerun": 253720.11,
      "delta": 0.0,
      "pct_delta": 0.0
    }
  ]
}
```

## [CODEX OUTPUT] `outputs/support/segment_reserve_comparison.csv`
Codex-generated segment comparison highlighting the Residential Mortgage severe-versus-adverse anomaly.

```text
segment_id,adverse,baseline,severe,adverse_minus_baseline,severe_minus_adverse
commercial_and_industrial,2712808.82,1977246.19,3148323.76,735562.63,435514.94
commercial_real_estate,3972723.25,2545519.51,4787769.99,1427203.74,815046.74
consumer_unsecured,118790.69,100355.66,133898.81,18435.03,15108.12
residential_mortgage,327699.21,253720.11,217710.91,73979.1,-109988.3
```

## [CODEX OUTPUT] `outputs/support/sensitivity_results.csv`
Codex-generated sensitivity results used to challenge forecast horizon, reversion, macro severity, and overlay magnitude assumptions.

```text
test_type,setting,scenario_name,reserve_amount
forecast_horizon,4,baseline,4877986.54
forecast_horizon,6,baseline,4876841.47
forecast_horizon,8,baseline,4876841.47
reversion_speed,2,severe,8287703.47
reversion_speed,4,severe,8384330.79
reversion_speed,6,severe,8472904.31
macro_severity_scale,0.75,severe,7126890.49
macro_severity_scale,1.0,severe,8287703.47
macro_severity_scale,1.25,severe,9803105.55
overlay_multiplier,0.0,severe,7850916.88
overlay_multiplier,1.0,severe,8287703.47
overlay_multiplier,1.5,severe,8506096.88
```
