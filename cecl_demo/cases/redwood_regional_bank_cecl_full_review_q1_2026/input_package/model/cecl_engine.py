"""Standalone CECL reserve engine shipped with the demo package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEGMENTS = {
  "commercial_real_estate": {
    "display_name": "Commercial Real Estate",
    "base_intercept": -2.9,
    "lgd_base": 0.34,
    "macro_sensitivities": {
      "unemployment_rate": 0.22,
      "gdp_growth": 0.24,
      "house_price_growth": 0.06,
      "cre_price_growth": 0.31,
      "prime_rate": 0.12
    }
  },
  "commercial_and_industrial": {
    "display_name": "Commercial and Industrial",
    "base_intercept": -2.72,
    "lgd_base": 0.3,
    "macro_sensitivities": {
      "unemployment_rate": 0.19,
      "gdp_growth": 0.29,
      "house_price_growth": 0.04,
      "cre_price_growth": 0.11,
      "prime_rate": 0.15
    }
  },
  "residential_mortgage": {
    "display_name": "Residential Mortgage",
    "base_intercept": -3.18,
    "lgd_base": 0.18,
    "macro_sensitivities": {
      "unemployment_rate": 0.15,
      "gdp_growth": 0.12,
      "house_price_growth": 0.39,
      "cre_price_growth": 0.02,
      "prime_rate": 0.08
    }
  },
  "consumer_unsecured": {
    "display_name": "Consumer Unsecured",
    "base_intercept": -2.4,
    "lgd_base": 0.61,
    "macro_sensitivities": {
      "unemployment_rate": 0.33,
      "gdp_growth": 0.17,
      "house_price_growth": 0.0,
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
    return pd.concat([forecast, pd.DataFrame(reversion_rows)], ignore_index=True)


def run_engine(portfolio: pd.DataFrame, scenario: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
    projection = build_projection(scenario)
    rows = portfolio.copy()
    pd_paths = []
    for _, quarter in projection.iterrows():
        stress = np.zeros(len(rows))
        for segment_id, segment in SEGMENTS.items():
            mask = rows["segment_id"] == segment_id
            component = (
                segment["macro_sensitivities"]["unemployment_rate"] * (float(quarter["unemployment_rate"]) - 4.5)
                + segment["macro_sensitivities"]["gdp_growth"] * max(1.6 - float(quarter["gdp_growth"]), 0.0)
                + segment["macro_sensitivities"]["house_price_growth"] * max(1.5 - float(quarter["house_price_growth"]), 0.0)
                + segment["macro_sensitivities"]["cre_price_growth"] * max(1.0 - float(quarter["cre_price_growth"]), 0.0)
                + segment["macro_sensitivities"]["prime_rate"] * max(float(quarter["prime_rate"]) - 5.0, 0.0)
            )
            stress[mask.to_numpy()] = component
        base_score = (
            rows["segment_id"].map(lambda value: SEGMENTS[str(value)]["base_intercept"])
            + 0.19 * (rows["risk_rating"] - 5.0)
            + 1.05 * np.maximum(rows["ltv_ratio"] - 0.75, 0.0)
            + 1.15 * np.maximum(rows["dti_ratio"] - 0.38, 0.0)
            + 0.75 * np.maximum(1.12 - rows["dscr"], 0.0)
            + 0.72 * np.maximum(rows["utilization_rate"] - 0.60, 0.0)
            + 0.44 * rows["payment_shock_index"]
            + 0.86 * rows["delinquency_flag"]
            - 0.0035 * (rows["fico"] - 680.0)
        )
        quarter_pd = 1.0 / (1.0 + np.exp(-(base_score + 0.34 * stress - 2.65)))
        pd_paths.append(np.clip(quarter_pd / 3.9, 0.001, 0.095))
    pd_matrix = np.vstack(pd_paths).T
    lifetime_paths = []
    for row_index, remaining in enumerate(rows["remaining_term_quarters"].astype(int).tolist()):
        loan_path = pd_matrix[row_index]
        if remaining <= len(loan_path):
            lifetime_paths.append(loan_path[:remaining])
        else:
            lifetime_paths.append(np.concatenate([loan_path, np.repeat(loan_path[-1], remaining - len(loan_path))]))
    lifetime_pd = np.array([1.0 - np.prod(1.0 - path) for path in lifetime_paths])
    lgd = (
        rows["segment_id"].map(lambda value: SEGMENTS[str(value)]["lgd_base"])
        + 0.29 * np.maximum(rows["ltv_ratio"] - 0.72, 0.0)
        + 0.06 * rows["delinquency_flag"]
        + 0.08 * np.maximum(1.0 - rows["collateral_buffer"], 0.0)
        - 0.0018 * (rows["fico"] - 680.0)
    ).clip(0.08, 0.88)
    overlay = rows["segment_id"].map(OVERLAYS[scenario_name]).astype(float) / 10000.0
    rows["scenario_name"] = scenario_name
    rows["lifetime_pd"] = lifetime_pd.round(6)
    rows["lgd"] = lgd.round(6)
    rows["overlay_rate"] = overlay.round(6)
    rows["reserve_rate"] = (rows["lifetime_pd"] * rows["lgd"] + rows["overlay_rate"]).round(6)
    rows["reserve_amount"] = (rows["current_balance"] * rows["reserve_rate"]).round(2)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--scenario-name", required=True, choices=list(OVERLAYS))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    portfolio = pd.read_csv(args.portfolio)
    scenario = pd.read_csv(args.scenario)
    result = run_engine(portfolio, scenario, args.scenario_name)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
