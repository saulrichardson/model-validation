"""Deterministic CECL portfolio generation and review analyses."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .schemas import FullReviewSpec, GapAssessmentSpec, ScenarioQuarter

LONG_RUN_MACRO = {
    "unemployment_rate": 4.7,
    "gdp_growth": 1.7,
    "house_price_growth": 1.9,
    "cre_price_growth": 1.4,
    "prime_rate": 5.0,
}

FULL_REVIEW_FINDING_TITLES = {
    "horizon": "Documented CECL horizon and reversion do not match the implemented reserve engine",
    "overlay": "Qualitative overlay effect is materially larger than documentation suggests",
    "anomaly": "One segment behaves directionally oddly under the severe scenario",
}

GAP_FINDING_TITLES = {
    "runtime": "Execution-based review is blocked by missing reserve engine and lineage evidence",
    "scenario": "Scenario narrative is not fully aligned to the supplied scenario tables",
    "segments": "Documented segment structure does not reconcile to the provided reserve outputs",
    "overlay": "Overlay documentation understates the magnitude implied by the provided reserve bridge",
}


def quarter_frame(quarters: list[ScenarioQuarter]) -> pd.DataFrame:
    return pd.DataFrame([quarter.model_dump() for quarter in quarters])


def generate_portfolio(spec: FullReviewSpec) -> pd.DataFrame:
    rng = np.random.default_rng(spec.rng_seed)
    rows: list[pd.DataFrame] = []
    total_assigned = 0

    for index, segment in enumerate(spec.segments):
        if index == len(spec.segments) - 1:
            segment_count = spec.sample_size - total_assigned
        else:
            segment_count = int(round(spec.sample_size * segment.mix_weight))
        total_assigned += segment_count

        balances = rng.uniform(segment.balance_range[0], segment.balance_range[1], segment_count)
        term_quarters = rng.integers(
            segment.remaining_term_range[0],
            segment.remaining_term_range[1] + 1,
            segment_count,
        )
        frame = pd.DataFrame(
            {
                "segment_id": segment.segment_id,
                "segment_name": segment.display_name,
                "current_balance": balances.round(2),
                "orig_balance": (balances * rng.uniform(1.05, 1.45, segment_count)).round(2),
                "remaining_term_quarters": term_quarters,
                "risk_rating": rng.integers(
                    segment.risk_rating_range[0], segment.risk_rating_range[1] + 1, segment_count
                ),
                "fico": rng.integers(segment.fico_range[0], segment.fico_range[1] + 1, segment_count),
                "ltv_ratio": rng.uniform(segment.ltv_range[0], segment.ltv_range[1], segment_count).round(4),
                "dti_ratio": rng.uniform(segment.dti_range[0], segment.dti_range[1], segment_count).round(4),
                "dscr": rng.uniform(segment.dscr_range[0], segment.dscr_range[1], segment_count).round(4),
                "utilization_rate": rng.uniform(
                    segment.utilization_range[0], segment.utilization_range[1], segment_count
                ).round(4),
                "payment_shock_index": rng.uniform(
                    segment.payment_shock_range[0], segment.payment_shock_range[1], segment_count
                ).round(4),
                "delinquency_flag": rng.binomial(1, 0.08 if segment.segment_id != "residential_mortgage" else 0.04, segment_count),
                "collateral_buffer": rng.uniform(0.75, 1.15, segment_count).round(4),
                "region": rng.choice(
                    ["Northeast", "Midwest", "Southeast", "Mountain"], size=segment_count
                ),
            }
        )
        rows.append(frame)

    portfolio = pd.concat(rows, ignore_index=True)
    portfolio.insert(0, "loan_id", [f"RRB-{idx:05d}" for idx in range(1, len(portfolio) + 1)])
    return portfolio


def build_projected_scenario(
    quarters: list[ScenarioQuarter],
    *,
    forecast_quarters: int,
    reversion_quarters: int,
) -> pd.DataFrame:
    frame = quarter_frame(quarters)
    forecast = frame.iloc[:forecast_quarters].copy()
    last = forecast.iloc[-1].copy()
    reversion_rows: list[dict[str, Any]] = []
    for step in range(1, reversion_quarters + 1):
        weight = step / reversion_quarters
        row: dict[str, Any] = {"quarter": f"reversion_{step}"}
        for key, long_run_value in LONG_RUN_MACRO.items():
            last_value = float(last[key])
            row[key] = round(last_value + (long_run_value - last_value) * weight, 4)
        reversion_rows.append(row)
    return pd.concat([forecast, pd.DataFrame(reversion_rows)], ignore_index=True)


def run_full_review_analysis(spec: FullReviewSpec, portfolio: pd.DataFrame) -> dict[str, Any]:
    baseline_projection = build_projected_scenario(
        spec.baseline_scenario,
        forecast_quarters=spec.implemented_forecast_quarters,
        reversion_quarters=spec.implemented_reversion_quarters,
    )
    adverse_projection = build_projected_scenario(
        spec.adverse_scenario,
        forecast_quarters=spec.implemented_forecast_quarters,
        reversion_quarters=spec.implemented_reversion_quarters,
    )
    severe_projection = build_projected_scenario(
        spec.severe_scenario,
        forecast_quarters=spec.implemented_forecast_quarters,
        reversion_quarters=spec.implemented_reversion_quarters,
    )

    baseline_result = evaluate_reserve(
        portfolio,
        spec,
        "baseline",
        baseline_projection,
    )
    adverse_result = evaluate_reserve(
        portfolio,
        spec,
        "adverse",
        adverse_projection,
    )
    severe_result = evaluate_reserve(
        portfolio,
        spec,
        "severe",
        severe_projection,
    )

    prior_baseline = baseline_result["loan_frame"][
        ["loan_id", "segment_id", "scenario_name", "current_balance", "reserve_amount", "reserve_rate"]
    ].copy()
    prior_baseline["reserve_amount"] = prior_baseline["reserve_amount"].round(2)
    prior_baseline["reserve_rate"] = prior_baseline["reserve_rate"].round(6)

    baseline_reproduction = evaluate_reserve(
        portfolio,
        spec,
        "baseline",
        baseline_projection,
    )
    reproduction_summary = summarize_reproduction(
        prior_baseline,
        baseline_reproduction["loan_frame"],
        baseline_result["segment_summary"],
        baseline_reproduction["segment_summary"],
    )

    scenario_summary = pd.concat(
        [
            baseline_result["scenario_summary"],
            adverse_result["scenario_summary"],
            severe_result["scenario_summary"],
        ],
        ignore_index=True,
    )
    segment_summary = pd.concat(
        [
            baseline_result["segment_summary"],
            adverse_result["segment_summary"],
            severe_result["segment_summary"],
        ],
        ignore_index=True,
    )
    segment_pivot = (
        segment_summary.pivot(index="segment_id", columns="scenario_name", values="reserve_amount")
        .reset_index()
        .rename_axis(columns=None)
    )
    segment_pivot["adverse_minus_baseline"] = (
        segment_pivot["adverse"] - segment_pivot["baseline"]
    ).round(2)
    segment_pivot["severe_minus_adverse"] = (segment_pivot["severe"] - segment_pivot["adverse"]).round(2)

    sensitivity_results = build_sensitivity_results(spec, portfolio)
    driver_bridge = build_driver_bridge(spec, portfolio)
    doc_crosscheck = build_full_review_crosscheck(spec, scenario_summary, segment_summary)
    findings = build_full_review_findings(spec, doc_crosscheck, reproduction_summary)
    evidence_requests: list[str] = []

    return {
        "projected_scenarios": {
            "baseline": baseline_projection,
            "adverse": adverse_projection,
            "severe": severe_projection,
        },
        "prior_baseline": prior_baseline,
        "scenario_summary": scenario_summary,
        "segment_summary": segment_summary,
        "segment_comparison": segment_pivot,
        "baseline_reproduction": reproduction_summary,
        "sensitivity_results": sensitivity_results,
        "driver_bridge": driver_bridge,
        "doc_crosscheck": doc_crosscheck,
        "findings": findings,
        "evidence_requests": evidence_requests,
        "analysis_summary": {
            "overall_baseline_reserve": round(float(baseline_result["scenario_summary"]["reserve_amount"].iloc[0]), 2),
            "overall_adverse_reserve": round(float(adverse_result["scenario_summary"]["reserve_amount"].iloc[0]), 2),
            "overall_severe_reserve": round(float(severe_result["scenario_summary"]["reserve_amount"].iloc[0]), 2),
            "seeded_anomaly_segment": spec.quantitative_anomaly_segment,
            "scenario_count": 3,
        },
    }


def evaluate_reserve(
    portfolio: pd.DataFrame,
    spec: FullReviewSpec,
    scenario_name: str,
    projection: pd.DataFrame,
    *,
    overlay_scenario_name: str | None = None,
) -> dict[str, Any]:
    sensitivities = {segment.segment_id: segment for segment in spec.segments}
    frame = portfolio.copy()
    frame["scenario_name"] = scenario_name

    pd_paths: list[np.ndarray] = []
    for _, quarter in projection.iterrows():
        stress = np.zeros(len(frame))
        for segment_id, segment in sensitivities.items():
            mask = frame["segment_id"] == segment_id
            stress_component = (
                segment.macro_sensitivities["unemployment_rate"] * (float(quarter["unemployment_rate"]) - 4.5)
                + segment.macro_sensitivities["gdp_growth"] * max(1.6 - float(quarter["gdp_growth"]), 0.0)
                + segment.macro_sensitivities["house_price_growth"] * max(1.5 - float(quarter["house_price_growth"]), 0.0)
                + segment.macro_sensitivities["cre_price_growth"] * max(1.0 - float(quarter["cre_price_growth"]), 0.0)
                + segment.macro_sensitivities["prime_rate"] * max(float(quarter["prime_rate"]) - 5.0, 0.0)
            )
            stress[mask.to_numpy()] = stress_component
        base_score = (
            frame["segment_id"].map(lambda value: sensitivities[str(value)].base_intercept)
            + 0.19 * (frame["risk_rating"] - 5.0)
            + 1.05 * np.maximum(frame["ltv_ratio"] - 0.75, 0.0)
            + 1.15 * np.maximum(frame["dti_ratio"] - 0.38, 0.0)
            + 0.75 * np.maximum(1.12 - frame["dscr"], 0.0)
            + 0.72 * np.maximum(frame["utilization_rate"] - 0.60, 0.0)
            + 0.44 * frame["payment_shock_index"]
            + 0.86 * frame["delinquency_flag"]
            - 0.0035 * (frame["fico"] - 680.0)
        )
        quarter_pd = 1.0 / (1.0 + np.exp(-(base_score + 0.34 * stress - 2.65)))
        pd_paths.append(np.clip(quarter_pd / 3.9, 0.001, 0.095))

    pd_matrix = np.vstack(pd_paths).T
    extended_paths: list[np.ndarray] = []
    for row_index, remaining in enumerate(frame["remaining_term_quarters"].astype(int).tolist()):
        loan_path = pd_matrix[row_index]
        if remaining <= len(loan_path):
            extended_paths.append(loan_path[:remaining])
            continue
        tail = np.repeat(loan_path[-1], remaining - len(loan_path))
        extended_paths.append(np.concatenate([loan_path, tail]))

    lifetime_pd = np.array([1.0 - np.prod(1.0 - path) for path in extended_paths])
    lgd = (
        frame["segment_id"].map(lambda value: sensitivities[str(value)].lgd_base)
        + 0.29 * np.maximum(frame["ltv_ratio"] - 0.72, 0.0)
        + 0.06 * frame["delinquency_flag"]
        + 0.08 * np.maximum(1.0 - frame["collateral_buffer"], 0.0)
        - 0.0018 * (frame["fico"] - 680.0)
    ).clip(0.08, 0.88)
    overlay_key = overlay_scenario_name or scenario_name
    overlay = frame["segment_id"].map(spec.overlay_bps_by_scenario[overlay_key]).astype(float) / 10000.0

    frame["lifetime_pd"] = lifetime_pd.round(6)
    frame["lgd"] = lgd.round(6)
    frame["overlay_rate"] = overlay.round(6)
    frame["reserve_rate"] = (frame["lifetime_pd"] * frame["lgd"] + frame["overlay_rate"]).round(6)
    frame["reserve_amount"] = (frame["current_balance"] * frame["reserve_rate"]).round(2)

    scenario_summary = pd.DataFrame(
        [
            {
                "scenario_name": scenario_name,
                "reserve_amount": round(float(frame["reserve_amount"].sum()), 2),
                "reserve_rate": round(float(frame["reserve_amount"].sum() / frame["current_balance"].sum()), 6),
                "loan_count": int(len(frame)),
                "documented_forecast_quarters": spec.documented_forecast_quarters,
                "implemented_forecast_quarters": spec.implemented_forecast_quarters,
            }
        ]
    )

    segment_summary = (
        frame.groupby(["scenario_name", "segment_id", "segment_name"], as_index=False)
        .agg(
            reserve_amount=("reserve_amount", "sum"),
            balance=("current_balance", "sum"),
            avg_lifetime_pd=("lifetime_pd", "mean"),
            avg_overlay_rate=("overlay_rate", "mean"),
        )
        .assign(
            reserve_rate=lambda item: (item["reserve_amount"] / item["balance"]).round(6),
            reserve_amount=lambda item: item["reserve_amount"].round(2),
            balance=lambda item: item["balance"].round(2),
            avg_lifetime_pd=lambda item: item["avg_lifetime_pd"].round(6),
            avg_overlay_rate=lambda item: item["avg_overlay_rate"].round(6),
        )
    )

    return {
        "loan_frame": frame,
        "scenario_summary": scenario_summary,
        "segment_summary": segment_summary,
    }


def summarize_reproduction(
    packaged_baseline: pd.DataFrame,
    rerun_baseline: pd.DataFrame,
    packaged_segment_summary: pd.DataFrame,
    rerun_segment_summary: pd.DataFrame,
) -> dict[str, Any]:
    merged = packaged_baseline.merge(
        rerun_baseline[["loan_id", "reserve_amount", "reserve_rate"]],
        on="loan_id",
        how="inner",
        suffixes=("_packaged", "_rerun"),
    )
    total_packaged = float(packaged_baseline["reserve_amount"].sum())
    total_rerun = float(rerun_baseline["reserve_amount"].sum())
    delta = total_rerun - total_packaged

    packaged_segment = (
        packaged_segment_summary[packaged_segment_summary["scenario_name"] == "baseline"][
            ["segment_id", "reserve_amount"]
        ]
        .rename(columns={"reserve_amount": "reserve_amount_packaged"})
    )
    rerun_segment = (
        rerun_segment_summary[rerun_segment_summary["scenario_name"] == "baseline"][
            ["segment_id", "reserve_amount"]
        ]
        .rename(columns={"reserve_amount": "reserve_amount_rerun"})
    )
    by_segment = packaged_segment.merge(rerun_segment, on="segment_id", how="outer").fillna(0.0)
    by_segment["delta"] = (by_segment["reserve_amount_rerun"] - by_segment["reserve_amount_packaged"]).round(2)
    by_segment["pct_delta"] = np.where(
        by_segment["reserve_amount_packaged"] == 0.0,
        0.0,
        ((by_segment["reserve_amount_rerun"] - by_segment["reserve_amount_packaged"]) / by_segment["reserve_amount_packaged"]) * 100.0,
    ).round(3)

    return {
        "packaged_total_reserve": round(total_packaged, 2),
        "rerun_total_reserve": round(total_rerun, 2),
        "absolute_delta": round(delta, 2),
        "pct_delta": round((delta / total_packaged) * 100.0, 3),
        "max_loan_level_abs_delta": round(
            float((merged["reserve_amount_rerun"] - merged["reserve_amount_packaged"]).abs().max()),
            2,
        ),
        "segment_deltas": by_segment.to_dict(orient="records"),
    }


def build_sensitivity_results(spec: FullReviewSpec, portfolio: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for horizon in [4, 6, 8]:
        result = evaluate_reserve(
            portfolio,
            spec,
            f"baseline_h{horizon}",
            build_projected_scenario(
                spec.baseline_scenario,
                forecast_quarters=min(horizon, len(spec.baseline_scenario)),
                reversion_quarters=spec.implemented_reversion_quarters,
            ),
            overlay_scenario_name="baseline",
        )
        rows.append(
            {
                "test_type": "forecast_horizon",
                "setting": str(horizon),
                "scenario_name": "baseline",
                "reserve_amount": float(result["scenario_summary"]["reserve_amount"].iloc[0]),
            }
        )

    for reversion in [2, 4, 6]:
        result = evaluate_reserve(
            portfolio,
            spec,
            f"severe_r{reversion}",
            build_projected_scenario(
                spec.severe_scenario,
                forecast_quarters=spec.implemented_forecast_quarters,
                reversion_quarters=reversion,
            ),
            overlay_scenario_name="severe",
        )
        rows.append(
            {
                "test_type": "reversion_speed",
                "setting": str(reversion),
                "scenario_name": "severe",
                "reserve_amount": float(result["scenario_summary"]["reserve_amount"].iloc[0]),
            }
        )

    severity_base = quarter_frame(spec.baseline_scenario)
    severity_target = quarter_frame(spec.severe_scenario)
    for scale in [0.75, 1.0, 1.25]:
        scaled = severity_base.copy()
        for field in LONG_RUN_MACRO:
            delta = severity_target[field] - severity_base[field]
            scaled[field] = severity_base[field] + delta * scale
        scaled_quarters = [ScenarioQuarter(**row) for row in scaled.to_dict(orient="records")]
        result = evaluate_reserve(
            portfolio,
            spec,
            f"severe_scale_{scale}",
            build_projected_scenario(
                scaled_quarters,
                forecast_quarters=spec.implemented_forecast_quarters,
                reversion_quarters=spec.implemented_reversion_quarters,
            ),
            overlay_scenario_name="severe",
        )
        rows.append(
            {
                "test_type": "macro_severity_scale",
                "setting": str(scale),
                "scenario_name": "severe",
                "reserve_amount": float(result["scenario_summary"]["reserve_amount"].iloc[0]),
            }
        )

    for multiplier in [0.0, 1.0, 1.5]:
        adjusted = {
            name: {segment: value * multiplier for segment, value in mapping.items()}
            for name, mapping in spec.overlay_bps_by_scenario.items()
        }
        adjusted_spec = spec.model_copy(update={"overlay_bps_by_scenario": adjusted})
        result = evaluate_reserve(
            portfolio,
            adjusted_spec,
            f"severe_overlay_{multiplier}",
            build_projected_scenario(
                spec.severe_scenario,
                forecast_quarters=spec.implemented_forecast_quarters,
                reversion_quarters=spec.implemented_reversion_quarters,
            ),
            overlay_scenario_name="severe",
        )
        rows.append(
            {
                "test_type": "overlay_multiplier",
                "setting": str(multiplier),
                "scenario_name": "severe",
                "reserve_amount": float(result["scenario_summary"]["reserve_amount"].iloc[0]),
            }
        )

    frame = pd.DataFrame(rows)
    frame["reserve_amount"] = frame["reserve_amount"].round(2)
    return frame


def build_driver_bridge(spec: FullReviewSpec, portfolio: pd.DataFrame) -> pd.DataFrame:
    baseline = quarter_frame(spec.baseline_scenario)
    severe = quarter_frame(spec.severe_scenario)
    baseline_result = evaluate_reserve(
        portfolio,
        spec,
        "baseline",
        build_projected_scenario(
            spec.baseline_scenario,
            forecast_quarters=spec.implemented_forecast_quarters,
            reversion_quarters=spec.implemented_reversion_quarters,
        ),
    )
    baseline_total = float(baseline_result["scenario_summary"]["reserve_amount"].iloc[0])

    rows: list[dict[str, Any]] = []
    for driver in [
        "unemployment_rate",
        "gdp_growth",
        "house_price_growth",
        "cre_price_growth",
        "prime_rate",
    ]:
        hybrid = baseline.copy()
        hybrid[driver] = severe[driver]
        hybrid_quarters = [ScenarioQuarter(**row) for row in hybrid.to_dict(orient="records")]
        result = evaluate_reserve(
            portfolio,
            spec,
            f"bridge_{driver}",
            build_projected_scenario(
                hybrid_quarters,
                forecast_quarters=spec.implemented_forecast_quarters,
                reversion_quarters=spec.implemented_reversion_quarters,
            ),
            overlay_scenario_name="baseline",
        )
        total = float(result["scenario_summary"]["reserve_amount"].iloc[0])
        rows.append(
            {
                "driver": driver,
                "reserve_delta_vs_baseline": round(total - baseline_total, 2),
            }
        )

    no_overlay = spec.model_copy(
        update={
            "overlay_bps_by_scenario": {
                name: dict.fromkeys(mapping, 0.0)
                for name, mapping in spec.overlay_bps_by_scenario.items()
            }
        }
    )
    no_overlay_result = evaluate_reserve(
        portfolio,
        no_overlay,
        "severe_no_overlay",
        build_projected_scenario(
            spec.severe_scenario,
            forecast_quarters=spec.implemented_forecast_quarters,
            reversion_quarters=spec.implemented_reversion_quarters,
        ),
        overlay_scenario_name="severe",
    )
    overlay_result = evaluate_reserve(
        portfolio,
        spec,
        "severe",
        build_projected_scenario(
            spec.severe_scenario,
            forecast_quarters=spec.implemented_forecast_quarters,
            reversion_quarters=spec.implemented_reversion_quarters,
        ),
    )
    rows.append(
        {
            "driver": "overlay",
            "reserve_delta_vs_baseline": round(
                float(overlay_result["scenario_summary"]["reserve_amount"].iloc[0])
                - float(no_overlay_result["scenario_summary"]["reserve_amount"].iloc[0]),
                2,
            ),
        }
    )
    return pd.DataFrame(rows)


def build_full_review_crosscheck(
    spec: FullReviewSpec,
    scenario_summary: pd.DataFrame,
    segment_summary: pd.DataFrame,
) -> dict[str, Any]:
    severe_segment = segment_summary[
        (segment_summary["scenario_name"] == "severe")
        & (segment_summary["segment_id"] == spec.quantitative_anomaly_segment)
    ].iloc[0]
    adverse_segment = segment_summary[
        (segment_summary["scenario_name"] == "adverse")
        & (segment_summary["segment_id"] == spec.quantitative_anomaly_segment)
    ].iloc[0]

    actual_overlay_cap = max(
        abs(value)
        for scenario in spec.overlay_bps_by_scenario.values()
        for value in scenario.values()
    )

    return {
        "documented_forecast_quarters": spec.documented_forecast_quarters,
        "implemented_forecast_quarters": spec.implemented_forecast_quarters,
        "documented_reversion_quarters": spec.documented_reversion_quarters,
        "implemented_reversion_quarters": spec.implemented_reversion_quarters,
        "documented_overlay_cap_bps": spec.documented_overlay_cap_bps,
        "actual_overlay_cap_bps": round(actual_overlay_cap, 2),
        "overall_monotonicity": {
            "baseline": float(
                scenario_summary[scenario_summary["scenario_name"] == "baseline"]["reserve_amount"].iloc[0]
            ),
            "adverse": float(
                scenario_summary[scenario_summary["scenario_name"] == "adverse"]["reserve_amount"].iloc[0]
            ),
            "severe": float(
                scenario_summary[scenario_summary["scenario_name"] == "severe"]["reserve_amount"].iloc[0]
            ),
        },
        "anomaly_segment": {
            "segment_id": spec.quantitative_anomaly_segment,
            "adverse_reserve_amount": round(float(adverse_segment["reserve_amount"]), 2),
            "severe_reserve_amount": round(float(severe_segment["reserve_amount"]), 2),
            "delta": round(float(severe_segment["reserve_amount"] - adverse_segment["reserve_amount"]), 2),
            "detail": spec.quantitative_anomaly_description,
        },
    }


def build_full_review_findings(
    spec: FullReviewSpec,
    doc_crosscheck: dict[str, Any],
    reproduction_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = [
        {
            "severity": "high",
            "title": FULL_REVIEW_FINDING_TITLES["horizon"],
            "summary": (
                f"Documentation describes a {spec.documented_forecast_quarters}-quarter reasonable-and-supportable period "
                f"with {spec.documented_reversion_quarters}-quarter reversion, while the reserve engine is configured for "
                f"{spec.implemented_forecast_quarters} forecast quarters and {spec.implemented_reversion_quarters} reversion quarters."
            ),
            "evidence": [
                "docs/methodology.md",
                "docs/model_overview.md",
                "model/cecl_engine.py",
            ],
        },
        {
            "severity": "medium",
            "title": FULL_REVIEW_FINDING_TITLES["overlay"],
            "summary": (
                f"The documentation frames qualitative overlays as capped at {spec.documented_overlay_cap_bps:.1f} bps, "
                f"but the supplied overlay table uses up to {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps."
            ),
            "evidence": [
                "docs/overlay_memo.md",
                "data/overlay_schedule.csv",
                "outputs/support/sensitivity_results.csv",
            ],
        },
    ]

    anomaly = doc_crosscheck["anomaly_segment"]
    if anomaly["delta"] <= 0:
        findings.append(
            {
                "severity": "high",
                "title": FULL_REVIEW_FINDING_TITLES["anomaly"],
                "summary": (
                    f"Segment {anomaly['segment_id']} produces a severe-scenario reserve of "
                    f"{anomaly['severe_reserve_amount']:.2f}, below the adverse reserve of "
                    f"{anomaly['adverse_reserve_amount']:.2f}. {anomaly['detail']}"
                ),
                "evidence": [
                    "outputs/support/segment_reserve_comparison.csv",
                    "scenarios/severe.csv",
                    "docs/scenario_assumptions.md",
                    "docs/overlay_memo.md",
                ],
            }
        )

    findings.append(
        {
            "severity": "low",
            "title": "Baseline reserve was reproducible within tolerance",
            "summary": (
                f"Rerunning the supplied baseline logic reproduced the packaged baseline reserve within "
                f"{reproduction_summary['pct_delta']:.3f}%."
            ),
            "evidence": [
                "outputs/prior_baseline_reserve.csv",
                "outputs/support/baseline_reproduction.json",
            ],
        }
    )
    return findings


def generate_gap_assessment_provided_outputs(spec: GapAssessmentSpec) -> dict[str, pd.DataFrame]:
    scenario_summary = pd.DataFrame(
        [
            {"scenario_name": "baseline", "reserve_amount": 38_420_000.0, "reserve_rate": 0.0184},
            {"scenario_name": "adverse", "reserve_amount": 52_180_000.0, "reserve_rate": 0.0248},
            {"scenario_name": "severe", "reserve_amount": 53_010_000.0, "reserve_rate": 0.0251},
        ]
    )

    rows: list[dict[str, Any]] = []
    base_values = {
        "residential_mortgage": (8_420_000.0, 11_300_000.0, 10_980_000.0),
        "heloc": (5_180_000.0, 6_450_000.0, 6_430_000.0),
        "cre_investor": (11_900_000.0, 17_120_000.0, 17_880_000.0),
        "commercial_and_industrial": (12_920_000.0, 17_310_000.0, 17_720_000.0),
    }
    for segment, values in base_values.items():
        for scenario_name, reserve_amount in zip(["baseline", "adverse", "severe"], values, strict=True):
            rows.append(
                {
                    "segment_id": segment,
                    "scenario_name": scenario_name,
                    "reserve_amount": reserve_amount,
                }
            )
    segment_summary = pd.DataFrame(rows)

    overlay_bridge = pd.DataFrame(
        [
            {"segment_id": segment, "documented_cap_bps": spec.documented_overlay_cap_bps, "provided_overlay_bps": overlay}
            for segment, overlay in spec.provided_overlay_bps_by_segment.items()
        ]
    )

    sample_rollforward = pd.DataFrame(
        [
            {"segment_id": "residential_mortgage", "ead": 810_000_000.0, "historical_loss_rate": 0.0081, "avg_ltv": 0.681},
            {"segment_id": "heloc", "ead": 356_000_000.0, "historical_loss_rate": 0.0112, "avg_ltv": 0.731},
            {"segment_id": "cre_investor", "ead": 522_000_000.0, "historical_loss_rate": 0.0191, "avg_ltv": 0.702},
            {"segment_id": "commercial_and_industrial", "ead": 611_000_000.0, "historical_loss_rate": 0.0178, "avg_ltv": 0.000},
        ]
    )

    return {
        "scenario_summary": scenario_summary,
        "segment_summary": segment_summary,
        "overlay_bridge": overlay_bridge,
        "sample_rollforward": sample_rollforward,
    }


def run_gap_assessment_analysis(
    spec: GapAssessmentSpec,
    provided_outputs: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    scenario_summary = provided_outputs["scenario_summary"]
    segment_summary = provided_outputs["segment_summary"]
    overlay_bridge = provided_outputs["overlay_bridge"]

    severe = quarter_frame(spec.severe_scenario)
    adverse = quarter_frame(spec.adverse_scenario)
    scenario_issue_rows = severe.merge(adverse, on="quarter", suffixes=("_severe", "_adverse"))
    hpi_mismatch = scenario_issue_rows[
        scenario_issue_rows["house_price_growth_severe"] > scenario_issue_rows["house_price_growth_adverse"]
    ]

    findings = [
        {
            "severity": "high",
            "title": GAP_FINDING_TITLES["runtime"],
            "summary": "The package includes prior outputs and narrative materials, but no reserve engine, reproducibility script, or lineaged runbook sufficient for execution-based review.",
            "evidence": [
                "docs/evidence_request_log.md",
                "docs/gap_tracker.md",
                "outputs/provided_reserve_summary.csv",
            ],
        },
        {
            "severity": "high",
            "title": GAP_FINDING_TITLES["scenario"],
            "summary": (
                "The severe scenario narrative describes a uniformly harsher path, but the supplied numeric scenarios "
                f"show {len(hpi_mismatch)} quarter(s) where severe house-price growth is less severe than adverse."
            ),
            "evidence": [
                "docs/scenario_assumptions.md",
                "scenarios/adverse.csv",
                "scenarios/severe.csv",
            ],
        },
        {
            "severity": "medium",
            "title": GAP_FINDING_TITLES["segments"],
            "summary": (
                f"Documentation describes {len(spec.documented_segments)} segments, while the provided reserve outputs reconcile to "
                f"{len(spec.output_segments)} output segments."
            ),
            "evidence": [
                "docs/methodology.md",
                "docs/model_overview.md",
                "outputs/provided_segment_reserves.csv",
            ],
        },
        {
            "severity": "medium",
            "title": GAP_FINDING_TITLES["overlay"],
            "summary": (
                f"The overlay memo frames qualitative adjustment as capped at {spec.documented_overlay_cap_bps:.1f} bps, "
                f"but the provided bridge shows up to {overlay_bridge['provided_overlay_bps'].max():.1f} bps."
            ),
            "evidence": [
                "docs/overlay_memo.md",
                "outputs/provided_overlay_bridge.csv",
            ],
        },
    ]

    evidence_requests = [
        "Provide the runnable CECL reserve engine or reproducibility notebook used to generate the supplied reserve outputs.",
        "Provide a lineaged runbook linking the prior output snapshots to the model version and scenario definitions reviewed by governance.",
        "Reconcile documented segment taxonomy to the segment structure used in the reserve outputs.",
        "Refresh scenario documentation so the severe narrative matches the numeric severe path quarter by quarter.",
    ]

    return {
        "scenario_summary": scenario_summary,
        "segment_summary": segment_summary,
        "overlay_bridge": overlay_bridge,
        "sample_rollforward": provided_outputs["sample_rollforward"],
        "scenario_mismatch_quarters": hpi_mismatch.to_dict(orient="records"),
        "findings": findings,
        "evidence_requests": evidence_requests,
        "analysis_summary": {
            "coverage": "documentation-led gap assessment",
            "runtime_blocked": True,
            "output_scenarios_available": True,
        },
    }


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pd.Series(payload).to_json(indent=2), encoding="utf-8")


def build_data_dictionary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"field_name": "loan_id", "definition": "Stable synthetic loan identifier", "type": "string"},
            {"field_name": "segment_id", "definition": "CECL segment identifier", "type": "string"},
            {"field_name": "current_balance", "definition": "Current amortized cost basis", "type": "float"},
            {"field_name": "remaining_term_quarters", "definition": "Remaining modeled life in quarters", "type": "integer"},
            {"field_name": "risk_rating", "definition": "Internal risk rating on a 1-10 scale", "type": "integer"},
            {"field_name": "fico", "definition": "Borrower credit score or proxy score", "type": "integer"},
            {"field_name": "ltv_ratio", "definition": "Current loan-to-value ratio", "type": "float"},
            {"field_name": "dti_ratio", "definition": "Debt-to-income ratio or analogous burden metric", "type": "float"},
            {"field_name": "dscr", "definition": "Debt-service coverage ratio", "type": "float"},
            {"field_name": "utilization_rate", "definition": "Line or borrowing-base utilization", "type": "float"},
            {"field_name": "payment_shock_index", "definition": "Synthetic payment shock proxy used in reserve sensitivity", "type": "float"},
            {"field_name": "delinquency_flag", "definition": "Indicator for recent delinquency or nonaccrual signal", "type": "integer"},
            {"field_name": "collateral_buffer", "definition": "Collateral support buffer or haircut proxy", "type": "float"},
        ]
    )


def build_evidence_ledger(paths: list[str]) -> list[dict[str, Any]]:
    ledger = []
    for index, relative_path in enumerate(paths, start=1):
        if relative_path.startswith("outputs/support/"):
            origin = "codex_generated_review_artifact"
            provenance_label = "[CODEX OUTPUT]"
        elif relative_path.startswith("outputs/stakeholder/"):
            origin = "codex_generated_final_deliverable"
            provenance_label = "[CODEX OUTPUT]"
        else:
            origin = "bank_uploaded_input"
            provenance_label = "[BANK INPUT]"
        area = Path(relative_path).parts[0] if Path(relative_path).parts else "unknown"
        ledger.append(
            {
                "evidence_id": f"E{index:03d}",
                "relative_path": relative_path,
                "title": Path(relative_path).name,
                "summary": f"{provenance_label} Evidence from {relative_path}",
                "origin": origin,
                "provenance_label": provenance_label,
                "area": area,
            }
        )
    return ledger


def nested_json_safe(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: nested_json_safe(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [nested_json_safe(item) for item in payload]
    if isinstance(payload, np.generic):
        return payload.item()
    if isinstance(payload, pd.DataFrame):
        return payload.to_dict(orient="records")
    return payload


def build_full_review_inventory() -> list[dict[str, str]]:
    return [
        {"path": "model/cecl_engine.py", "kind": "code"},
        {"path": "data/loan_level_snapshot.csv", "kind": "dataset"},
        {"path": "data/data_dictionary.csv", "kind": "document"},
        {"path": "data/overlay_schedule.csv", "kind": "config"},
        {"path": "scenarios/baseline.csv", "kind": "scenario"},
        {"path": "scenarios/adverse.csv", "kind": "scenario"},
        {"path": "scenarios/severe.csv", "kind": "scenario"},
        {"path": "docs/methodology.md", "kind": "document"},
        {"path": "docs/model_overview.md", "kind": "document"},
        {"path": "docs/scenario_assumptions.md", "kind": "document"},
        {"path": "docs/overlay_memo.md", "kind": "document"},
        {"path": "outputs/prior_baseline_reserve.csv", "kind": "metrics"},
    ]


def build_gap_inventory() -> list[dict[str, str]]:
    return [
        {"path": "docs/methodology.md", "kind": "document"},
        {"path": "docs/model_overview.md", "kind": "document"},
        {"path": "docs/scenario_assumptions.md", "kind": "document"},
        {"path": "docs/overlay_memo.md", "kind": "document"},
        {"path": "docs/prior_review_note.md", "kind": "document"},
        {"path": "docs/evidence_request_log.md", "kind": "document"},
        {"path": "docs/gap_tracker.md", "kind": "document"},
        {"path": "data/data_dictionary.csv", "kind": "document"},
        {"path": "scenarios/baseline.csv", "kind": "scenario"},
        {"path": "scenarios/adverse.csv", "kind": "scenario"},
        {"path": "scenarios/severe.csv", "kind": "scenario"},
        {"path": "outputs/provided_reserve_summary.csv", "kind": "metrics"},
        {"path": "outputs/provided_segment_reserves.csv", "kind": "metrics"},
    ]
