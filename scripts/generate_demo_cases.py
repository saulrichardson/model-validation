"""Generate synthetic demo packages for the validation workbench."""

from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "demo_cases"


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def score_dataframe(
    frame: pd.DataFrame,
    *,
    intercept: float,
    coefficients: dict[str, float],
    threshold: float,
) -> pd.DataFrame:
    features = pd.DataFrame(
        {
            "bureau_headroom": np.clip((720 - frame["bureau_score"]) / 120, 0, None),
            "dti_ratio": frame["dti_ratio"],
            "utilization_rate": frame["utilization_rate"],
            "delinquency_12m": frame["delinquency_12m"],
            "inquiries_6m": frame["inquiries_6m"],
            "thin_file_flag": frame["thin_file_flag"],
            "short_tenure": np.clip((24 - frame["employment_tenure_mo"]) / 24, 0, None),
            "low_cash_buffer": np.clip((6 - frame["recent_cash_buffer_mo"]) / 6, 0, None),
        }
    )
    linear = np.full(len(frame), intercept, dtype=float)
    contributions: dict[str, pd.Series] = {}
    for name, weight in coefficients.items():
        contribution = features[name] * weight
        contributions[name] = contribution
        linear += contribution

    pd_estimate = sigmoid(linear)
    decisions = np.where(
        pd_estimate >= threshold,
        "decline",
        np.where(pd_estimate >= threshold - 0.07, "review", "approve"),
    )
    scores = np.round(850 - pd_estimate * 550).astype(int)

    reason_map = {
        "bureau_headroom": "LOW_BUREAU_SCORE",
        "dti_ratio": "HIGH_DTI",
        "utilization_rate": "HIGH_UTILIZATION",
        "delinquency_12m": "RECENT_DELINQUENCY",
        "inquiries_6m": "RECENT_CREDIT_SEEKING",
        "thin_file_flag": "THIN_CREDIT_FILE",
        "short_tenure": "SHORT_EMPLOYMENT_TENURE",
        "low_cash_buffer": "LOW_CASH_BUFFER",
    }
    reason_frame = pd.DataFrame(contributions)
    top_features = np.argsort(-reason_frame.to_numpy(), axis=1)[:, :3]
    feature_names = list(reason_frame.columns)
    reasons: list[list[str]] = []
    for row_idx, feature_indices in enumerate(top_features):
        row_reasons: list[str] = []
        for feature_idx in feature_indices:
            feature_name = feature_names[int(feature_idx)]
            if reason_frame.iloc[row_idx, int(feature_idx)] <= 0:
                continue
            row_reasons.append(reason_map[feature_name])
        reasons.append(row_reasons[:3] or ["LOW_BUREAU_SCORE"])

    result = frame.copy()
    result["pd_estimate"] = np.round(pd_estimate, 6)
    result["score"] = scores
    result["decision"] = decisions
    result["reason_1"] = [row[0] if len(row) > 0 else "" for row in reasons]
    result["reason_2"] = [row[1] if len(row) > 1 else "" for row in reasons]
    result["reason_3"] = [row[2] if len(row) > 2 else "" for row in reasons]
    return result


def build_material_change_case(root: Path) -> dict[str, object]:
    rng = np.random.default_rng(19)
    case_dir = ensure_dir(root / "material_change_full" / "package")
    shutil.rmtree(case_dir, ignore_errors=True)
    case_dir.mkdir(parents=True, exist_ok=True)
    data_dir = ensure_dir(case_dir / "data")
    docs_dir = ensure_dir(case_dir / "docs")
    models_dir = ensure_dir(case_dir / "models")
    metrics_dir = ensure_dir(case_dir / "metrics")
    runtime_dir = ensure_dir(case_dir / "runtime")

    sample_size = 1800
    thin_file = rng.binomial(1, 0.29, size=sample_size)
    channel = rng.choice(["branch", "direct", "broker"], p=[0.44, 0.36, 0.20], size=sample_size)
    region = rng.choice(["northeast", "south", "midwest", "west"], size=sample_size)
    bureau_score = np.clip(rng.normal(694 - 22 * thin_file, 48, size=sample_size), 540, 820)
    dti_ratio = np.clip(rng.beta(2.4, 3.7, size=sample_size) + thin_file * 0.08, 0.06, 0.87)
    utilization_rate = np.clip(rng.beta(2.7, 2.3, size=sample_size) + thin_file * 0.05, 0.03, 0.98)
    delinquency_12m = np.clip(rng.poisson(0.38 + thin_file * 0.32, size=sample_size), 0, 4)
    inquiries_6m = np.clip(rng.poisson(1.4 + thin_file * 0.7, size=sample_size), 0, 7)
    employment_tenure_mo = np.clip(rng.normal(54 - thin_file * 12, 21, size=sample_size), 2, 160)
    annual_income_k = np.clip(rng.normal(92 - thin_file * 11, 28, size=sample_size), 24, 260)
    recent_cash_buffer_mo = np.clip(
        rng.normal(5.2 - thin_file * 1.5, 1.9, size=sample_size), 0.2, 12
    )
    requested_amount_k = np.clip(rng.normal(18, 7, size=sample_size), 3, 45)

    truth_logit = (
        -2.65
        + np.clip((700 - bureau_score) / 115, 0, None) * 1.35
        + dti_ratio * 1.55
        + utilization_rate * 0.95
        + delinquency_12m * 0.52
        + inquiries_6m * 0.16
        + thin_file * 0.48
        + np.clip((18 - recent_cash_buffer_mo) / 18, 0, None) * 0.72
        + np.clip((24 - employment_tenure_mo) / 24, 0, None) * 0.22
        - (annual_income_k / 100) * 0.18
        + (channel == "broker") * 0.12
    )
    target_default = rng.binomial(1, sigmoid(truth_logit))

    frame = pd.DataFrame(
        {
            "application_id": [f"APP-{idx:05d}" for idx in range(sample_size)],
            "channel": channel,
            "region": region,
            "annual_income_k": np.round(annual_income_k, 2),
            "requested_amount_k": np.round(requested_amount_k, 2),
            "bureau_score": np.round(bureau_score, 0).astype(int),
            "dti_ratio": np.round(dti_ratio, 4),
            "utilization_rate": np.round(utilization_rate, 4),
            "delinquency_12m": delinquency_12m.astype(int),
            "inquiries_6m": inquiries_6m.astype(int),
            "employment_tenure_mo": np.round(employment_tenure_mo, 1),
            "recent_cash_buffer_mo": np.round(recent_cash_buffer_mo, 2),
            "thin_file_flag": thin_file.astype(int),
            "target_default": target_default.astype(int),
        }
    )
    frame.to_csv(data_dir / "oot_validation_sample.csv", index=False)

    baseline_coeffs = {
        "bureau_headroom": 1.28,
        "dti_ratio": 1.34,
        "utilization_rate": 0.77,
        "delinquency_12m": 0.53,
        "inquiries_6m": 0.13,
        "thin_file_flag": 0.33,
        "short_tenure": 0.18,
    }
    candidate_coeffs = {
        "bureau_headroom": 1.25,
        "dti_ratio": 1.29,
        "utilization_rate": 0.76,
        "delinquency_12m": 0.55,
        "inquiries_6m": 0.12,
        "thin_file_flag": 0.46,
        "short_tenure": 0.20,
        "low_cash_buffer": 0.68,
    }

    baseline_scores = score_dataframe(
        frame, intercept=-2.54, coefficients=baseline_coeffs, threshold=0.43
    )
    candidate_scores = score_dataframe(
        frame, intercept=-2.42, coefficients=candidate_coeffs, threshold=0.41
    )
    baseline_scores.to_csv(metrics_dir / "baseline_reference_scored.csv", index=False)
    candidate_scores.to_csv(metrics_dir / "candidate_reference_scored.csv", index=False)

    def metric_block(scored: pd.DataFrame) -> dict[str, float]:
        return {
            "auc": round(float(roc_auc_score(scored["target_default"], scored["pd_estimate"])), 4),
            "approval_rate": round(float((scored["decision"] == "approve").mean()), 4),
            "review_rate": round(float((scored["decision"] == "review").mean()), 4),
            "decline_rate": round(float((scored["decision"] == "decline").mean()), 4),
            "avg_pd": round(float(scored["pd_estimate"].mean()), 4),
            "avg_score": round(float(scored["score"].mean()), 2),
        }

    segment_rows: list[dict[str, object]] = []
    for segment_name, mask in {
        "thin_file": frame["thin_file_flag"] == 1,
        "thick_file": frame["thin_file_flag"] == 0,
        "broker": frame["channel"] == "broker",
        "direct": frame["channel"] == "direct",
    }.items():
        baseline_segment = baseline_scores.loc[mask]
        candidate_segment = candidate_scores.loc[mask]
        segment_rows.append(
            {
                "segment": segment_name,
                "baseline_approval_rate": round(
                    float((baseline_segment["decision"] == "approve").mean()), 4
                ),
                "candidate_approval_rate": round(
                    float((candidate_segment["decision"] == "approve").mean()), 4
                ),
                "approval_delta": round(
                    float(
                        (candidate_segment["decision"] == "approve").mean()
                        - (baseline_segment["decision"] == "approve").mean()
                    ),
                    4,
                ),
                "baseline_avg_pd": round(float(baseline_segment["pd_estimate"].mean()), 4),
                "candidate_avg_pd": round(float(candidate_segment["pd_estimate"].mean()), 4),
            }
        )
    pd.DataFrame(segment_rows).to_csv(metrics_dir / "segment_shift_summary.csv", index=False)

    comparison_payload = {
        "baseline": metric_block(baseline_scores),
        "candidate": metric_block(candidate_scores),
        "notes": [
            "Candidate version introduces recent_cash_buffer_mo as a liquidity stress feature.",
            "Thin-file approval rate falls materially relative to the champion model.",
        ],
    }
    write_text(metrics_dir / "comparison_summary.json", json.dumps(comparison_payload, indent=2))

    reason_code_mapping = pd.DataFrame(
        [
            {
                "reason_code": "LOW_BUREAU_SCORE",
                "consumer_statement": "Credit bureau score below policy expectation.",
            },
            {
                "reason_code": "HIGH_DTI",
                "consumer_statement": "Debt obligations are high relative to income.",
            },
            {
                "reason_code": "HIGH_UTILIZATION",
                "consumer_statement": "Revolving credit utilization is elevated.",
            },
            {
                "reason_code": "RECENT_DELINQUENCY",
                "consumer_statement": "Recent delinquency history increased observed risk.",
            },
            {
                "reason_code": "RECENT_CREDIT_SEEKING",
                "consumer_statement": "Recent credit inquiries indicate higher credit seeking.",
            },
            {
                "reason_code": "THIN_CREDIT_FILE",
                "consumer_statement": "Limited credit history reduced score confidence.",
            },
            {
                "reason_code": "SHORT_EMPLOYMENT_TENURE",
                "consumer_statement": "Short employment tenure reduced resilience assessment.",
            },
            {
                "reason_code": "LOW_CASH_BUFFER",
                "consumer_statement": "Available cash reserves were lower than policy expectations.",
            },
        ]
    )
    reason_code_mapping.to_csv(docs_dir / "reason_code_mapping.csv", index=False)

    methodology = """
    Retail Installment Credit Methodology

    The candidate scorecard refresh extends the validated champion structure used in version 2024.9 to an
    eight-factor underwriting scorecard.
    Inputs include bureau score, debt-to-income ratio, revolving utilization, twelve month delinquency count,
    six month inquiry count, thin-file indicator, employment tenure, and a liquidity stress feature derived from
    recent cash-buffer months.

    The decline threshold is recalibrated from 0.43 to 0.41 to preserve operational review volumes after adding the
    liquidity feature. Adverse-action generation is refreshed to include LOW_CASH_BUFFER whenever the liquidity feature
    is among the top three contributors.
    """
    write_text(docs_dir / "methodology.md", methodology)

    development_summary = """
    Development and Calibration Summary

    The candidate refresh was fit on the 2022-Q1 through 2024-Q3 retail installment booking vintages using
    logistic regression with monotonic bin review and coefficient sign constraints inherited from the approved
    2024.9 champion. The refresh retained the prior champion factor set and introduced one additional liquidity
    feature derived from recent_cash_buffer_mo. Coefficients were re-estimated after a stability screen on
    population drift, missingness, and segment prevalence. Operating-point calibration targeted a stable manual-review
    queue while preserving rank ordering relative to the champion.

    Validation package scope:
    - Development sample window: 2022-01 through 2024-09.
    - OOT validation window: 2024-10 through 2025-01.
    - Candidate liquidity feature: low_cash_buffer = clip((6 - recent_cash_buffer_mo) / 6, 0, None).
    - Threshold recalibration: decline threshold moved from 0.43 to 0.41 after approval-rate sensitivity testing.
    """
    write_text(docs_dir / "development_summary.md", development_summary)

    change_request = """
    Change Request Summary

    Business sponsors requested a refresh to improve downturn sensitivity for applicants showing shallow liquidity positions.
    The challenger package adds a liquidity stress input derived from recent cash-buffer months and recalibrates the decline
    threshold from 0.43 to 0.41. Documentation and adverse-action appendix updates were completed for this package.
    """
    write_text(docs_dir / "change_request.md", change_request)

    prior_validation = """
    Prior Validation Memo Excerpt

    Version 2024.9 was approved with two routine conditions: maintain documentation alignment after future refreshes and
    ensure every reason-code driver remains traceable to the consumer adverse-action table. No conceptual issues were open at approval.
    """
    write_text(docs_dir / "prior_validation_memo.md", prior_validation)

    monitoring_plan = """
    Monitoring Plan

    Monthly monitoring for the candidate package includes approval/review/decline rate tracking, PSI on the liquidity
    feature, thin-file approval-rate drift, reason-code coverage for LOW_CASH_BUFFER, and back-book default capture by
    channel and thin-file segment. Escalation is required if thin-file approval rate shifts by more than 8 percentage
    points against the champion or if LOW_CASH_BUFFER coverage falls below 95% of materially impacted declines.
    """
    write_text(docs_dir / "monitoring_plan.md", monitoring_plan)

    metric_provenance = """
    Metric Provenance Note

    Comparison summary metrics were computed on the packaged OOT validation sample using the packaged baseline and
    candidate source files. AUC is calculated against target_default. Approval, review, and decline rates are based on
    the scripted threshold policy embedded in each model file. Segment shift summary is calculated on thin_file_flag and
    channel segments using the same scored outputs included in this package.
    """
    write_text(docs_dir / "metric_provenance.md", metric_provenance)

    pd.DataFrame(
        [
            ["bureau_score", "External bureau score at application intake.", "integer", "560-820"],
            ["dti_ratio", "Debt-to-income ratio at decision time.", "float", "0.05-0.90"],
            ["utilization_rate", "Revolving utilization share.", "float", "0.03-0.99"],
            ["delinquency_12m", "Number of delinquencies in trailing 12 months.", "integer", "0-4"],
            ["inquiries_6m", "Recent bureau inquiries in trailing six months.", "integer", "0-7"],
            ["thin_file_flag", "Indicator for thin-file applicants.", "integer", "0-1"],
            ["employment_tenure_mo", "Months in current employment.", "float", "2-160"],
            ["recent_cash_buffer_mo", "Estimated months of liquid cash buffer.", "float", "0.2-12"],
            ["low_cash_buffer", "Derived liquidity stress feature used in candidate model only.", "float", "0-1"],
        ],
        columns=["feature_name", "business_definition", "data_type", "expected_range"],
    ).to_csv(docs_dir / "feature_dictionary.csv", index=False)

    write_text(
        case_dir / "requirements.txt",
        """
        numpy>=1.26
        pandas>=2.2
        scikit-learn>=1.5
        """,
    )

    model_template = """
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MODEL_NAME = "{model_name}"
INTERCEPT = {intercept}
THRESHOLD = {threshold}
COEFFICIENTS = {coefficients}

REASON_CODES = {{
    "bureau_headroom": "LOW_BUREAU_SCORE",
    "dti_ratio": "HIGH_DTI",
    "utilization_rate": "HIGH_UTILIZATION",
    "delinquency_12m": "RECENT_DELINQUENCY",
    "inquiries_6m": "RECENT_CREDIT_SEEKING",
    "thin_file_flag": "THIN_CREDIT_FILE",
    "short_tenure": "SHORT_EMPLOYMENT_TENURE",
    "low_cash_buffer": "LOW_CASH_BUFFER",
}}

def _sigmoid(values):
    return 1.0 / (1.0 + np.exp(-values))

def _features(frame):
    return pd.DataFrame({{
        "bureau_headroom": np.clip((720 - frame["bureau_score"]) / 120, 0, None),
        "dti_ratio": frame["dti_ratio"],
        "utilization_rate": frame["utilization_rate"],
        "delinquency_12m": frame["delinquency_12m"],
        "inquiries_6m": frame["inquiries_6m"],
        "thin_file_flag": frame["thin_file_flag"],
        "short_tenure": np.clip((24 - frame["employment_tenure_mo"]) / 24, 0, None),
        "low_cash_buffer": np.clip((6 - frame["recent_cash_buffer_mo"]) / 6, 0, None),
    }})

def score_frame(frame):
    features = _features(frame)
    linear = np.full(len(frame), INTERCEPT, dtype=float)
    contribution_map = {{}}
    for feature_name, weight in COEFFICIENTS.items():
        contribution = features[feature_name] * weight
        contribution_map[feature_name] = contribution
        linear += contribution
    pd_estimate = _sigmoid(linear)
    decision = np.where(pd_estimate >= THRESHOLD, "decline", np.where(pd_estimate >= THRESHOLD - 0.07, "review", "approve"))
    output = frame.copy()
    output["pd_estimate"] = np.round(pd_estimate, 6)
    output["score"] = np.round(850 - pd_estimate * 550).astype(int)
    output["decision"] = decision
    contribution_frame = pd.DataFrame(contribution_map)
    ranking = np.argsort(-contribution_frame.to_numpy(), axis=1)[:, :3]
    feature_names = list(contribution_frame.columns)
    reasons = []
    for row_idx, indices in enumerate(ranking):
        row_reasons = []
        for idx in indices:
            feature_name = feature_names[int(idx)]
            if contribution_frame.iloc[row_idx, int(idx)] <= 0:
                continue
            row_reasons.append(REASON_CODES[feature_name])
        reasons.append(row_reasons[:3] or ["LOW_BUREAU_SCORE"])
    output["reason_1"] = [row[0] if len(row) > 0 else "" for row in reasons]
    output["reason_2"] = [row[1] if len(row) > 1 else "" for row in reasons]
    output["reason_3"] = [row[2] if len(row) > 2 else "" for row in reasons]
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    scored = score_frame(frame)
    scored.to_csv(args.output, index=False)
    summary = {{
        "model_name": MODEL_NAME,
        "rows": int(len(scored)),
        "approval_rate": round(float((scored["decision"] == "approve").mean()), 4),
        "average_score": round(float(scored["score"].mean()), 2),
    }}
    Path(args.output).with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
"""
    write_text(
        models_dir / "baseline_model.py",
        model_template.format(
            model_name="baseline_v2024_09",
            intercept=-2.54,
            threshold=0.43,
            coefficients=json.dumps(baseline_coeffs, sort_keys=True),
        ),
    )
    write_text(
        models_dir / "candidate_model.py",
        model_template.format(
            model_name="candidate_v2025_02",
            intercept=-2.42,
            threshold=0.41,
            coefficients=json.dumps(candidate_coeffs, sort_keys=True),
        ),
    )

    runtime_harness = """
import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def _run_model(script_path: Path, input_path: Path, output_path: Path) -> dict[str, object]:
    cmd = [sys.executable, str(script_path), "--input", str(input_path), "--output", str(output_path)]
    subprocess.run(cmd, check=True, cwd=str(script_path.parent.parent))
    scored = pd.read_csv(output_path)
    return {
        "model_path": str(script_path),
        "output_path": str(output_path),
        "rows": int(len(scored)),
        "approval_rate": round(float((scored["decision"] == "approve").mean()), 4),
        "review_rate": round(float((scored["decision"] == "review").mean()), 4),
        "decline_rate": round(float((scored["decision"] == "decline").mean()), 4),
        "avg_pd": round(float(scored["pd_estimate"].mean()), 4),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    package_root = Path(__file__).resolve().parents[1]
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    baseline_path = package_root / "models" / "baseline_model.py"
    candidate_path = package_root / "models" / "candidate_model.py"
    baseline_output = output_dir / "baseline_scored.csv"
    candidate_output = output_dir / "candidate_scored.csv"

    baseline_summary = _run_model(baseline_path, input_path, baseline_output)
    candidate_summary = _run_model(candidate_path, input_path, candidate_output)

    payload = {
        "input_path": str(input_path),
        "baseline": baseline_summary,
        "candidate": candidate_summary,
    }
    (output_dir / "revalidation_summary.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
"""
    write_text(runtime_dir / "compare_models.py", runtime_harness)
    write_text(
        runtime_dir / "run_revalidation.sh",
        """
        python runtime/compare_models.py --input data/oot_validation_sample.csv --output-dir outputs/revalidation_run
        """,
    )

    return {
        "demo_id": "material_change_full",
        "title": "Material Change Revalidation",
        "description": "Comprehensive lending model package with baseline and candidate versions, runnable code, metrics, and documentation.",
        "expected_case_type": "material_change_revalidation",
        "package_dir": "material_change_full/package",
        "highlights": [
            "Rerunnable baseline and candidate models.",
            "Methodology, change request, and adverse-action mapping are aligned to the candidate liquidity feature.",
            "Package is designed to support a full material-change revalidation memo and sensitivity appendix.",
        ],
        "expected_workflow": "full_revalidation",
        "expected_report_type": "full_revalidation_memo",
        "minimum_coverage_ratio": 0.7,
    }


def build_black_box_case(root: Path) -> dict[str, object]:
    rng = np.random.default_rng(27)
    case_dir = ensure_dir(root / "runtime_behavioral" / "package")
    shutil.rmtree(case_dir, ignore_errors=True)
    case_dir.mkdir(parents=True, exist_ok=True)
    data_dir = ensure_dir(case_dir / "data")
    runtime_dir = ensure_dir(case_dir / "runtime")
    docs_dir = ensure_dir(case_dir / "docs")

    sample_size = 1400
    channel = rng.choice(
        ["branch", "direct", "broker", "digital_partner"],
        p=[0.33, 0.29, 0.19, 0.19],
        size=sample_size,
    )
    thin_file = rng.binomial(1, 0.24, size=sample_size)
    bureau_score = np.clip(rng.normal(688 - thin_file * 28, 56, size=sample_size), 525, 818)
    dti_ratio = np.clip(
        rng.beta(2.1, 3.0, size=sample_size) + (channel == "broker") * 0.07, 0.05, 0.92
    )
    utilization_rate = np.clip(rng.beta(2.5, 2.2, size=sample_size), 0.04, 0.97)
    delinquency_12m = np.clip(rng.poisson(0.36 + thin_file * 0.22, size=sample_size), 0, 4)
    inquiries_6m = np.clip(
        rng.poisson(1.2 + (channel == "digital_partner") * 0.5, size=sample_size), 0, 8
    )
    annual_income_k = np.clip(rng.normal(88, 31, size=sample_size), 20, 280)
    requested_amount_k = np.clip(rng.normal(17, 8, size=sample_size), 2, 50)

    frame = pd.DataFrame(
        {
            "application_id": [f"VEND-{idx:05d}" for idx in range(sample_size)],
            "channel": channel,
            "annual_income_k": np.round(annual_income_k, 2),
            "requested_amount_k": np.round(requested_amount_k, 2),
            "bureau_score": np.round(bureau_score, 0).astype(int),
            "dti_ratio": np.round(dti_ratio, 4),
            "utilization_rate": np.round(utilization_rate, 4),
            "delinquency_12m": delinquency_12m.astype(int),
            "inquiries_6m": inquiries_6m.astype(int),
            "thin_file_flag": thin_file.astype(int),
        }
    )
    frame.to_csv(data_dir / "smoke_input_batch.csv", index=False)

    bundle = {
        "intercept": -1.92,
        "thresholds": {"approve": 665, "review": 610},
        "weights": {
            "bureau_headroom": 1.18,
            "dti_ratio": 1.24,
            "utilization_rate": 0.74,
            "delinquency_12m": 0.49,
            "inquiries_6m": 0.16,
            "thin_file_flag": 0.45,
            "requested_amount_ratio": 0.21,
            "broker_penalty": 0.42,
            "digital_partner_penalty": 0.27,
        },
    }
    encoded_bundle = base64.b64encode(json.dumps(bundle).encode("utf-8")).decode("utf-8")
    write_text(
        runtime_dir / "opaque_model_bundle.json",
        json.dumps({"bundle_type": "vendor_risk_bundle", "payload": encoded_bundle}, indent=2),
    )

    harness = """
    import argparse
    import base64
    import json
    from pathlib import Path

    import numpy as np
    import pandas as pd


    def _sigmoid(values):
        return 1.0 / (1.0 + np.exp(-values))

    def _load_bundle():
        bundle_path = Path(__file__).resolve().parent / "opaque_model_bundle.json"
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        return json.loads(base64.b64decode(payload["payload"]).decode("utf-8"))

    def _reason_codes(frame):
        reasons = []
        for _, row in frame.iterrows():
            row_reasons = []
            if row["bureau_score"] < 620:
                row_reasons.append("RC101")
            if row["dti_ratio"] > 0.46:
                row_reasons.append("RC104")
            if row["utilization_rate"] > 0.78:
                row_reasons.append("RC112")
            if row["thin_file_flag"] == 1:
                row_reasons.append("RC207")
            if row["channel"] in {"broker", "digital_partner"} and row["dti_ratio"] > 0.40:
                row_reasons = ["RC900"] + row_reasons[:2]
            reasons.append(row_reasons[:3] or ["RC101"])
        return reasons

    def score_frame(frame):
        bundle = _load_bundle()
        weights = bundle["weights"]
        linear = np.full(len(frame), bundle["intercept"], dtype=float)
        linear += np.clip((700 - frame["bureau_score"]) / 115, 0, None) * weights["bureau_headroom"]
        linear += frame["dti_ratio"] * weights["dti_ratio"]
        linear += frame["utilization_rate"] * weights["utilization_rate"]
        linear += frame["delinquency_12m"] * weights["delinquency_12m"]
        linear += frame["inquiries_6m"] * weights["inquiries_6m"]
        linear += frame["thin_file_flag"] * weights["thin_file_flag"]
        linear += np.clip(frame["requested_amount_k"] / np.maximum(frame["annual_income_k"], 1), 0, None) * weights["requested_amount_ratio"]
        linear += (frame["channel"] == "broker") * weights["broker_penalty"]
        linear += (frame["channel"] == "digital_partner") * weights["digital_partner_penalty"]
        risk_probability = _sigmoid(linear)
        risk_score = np.round(850 - risk_probability * 560).astype(int)
        decision = np.where(risk_score >= bundle["thresholds"]["approve"], "approve", np.where(risk_score >= bundle["thresholds"]["review"], "review", "decline"))
        reasons = _reason_codes(frame)
        output = frame.copy()
        output["risk_probability"] = np.round(risk_probability, 6)
        output["risk_score"] = risk_score
        output["decision"] = decision
        output["reason_codes"] = ["|".join(row) for row in reasons]
        return output

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", required=True)
        parser.add_argument("--output", required=True)
        args = parser.parse_args()
        frame = pd.read_csv(args.input)
        scored = score_frame(frame)
        Path(args.output).write_text("\\n".join(scored.to_json(orient="records", lines=True).splitlines()), encoding="utf-8")

    if __name__ == "__main__":
        main()
    """
    write_text(runtime_dir / "score_batch.py", harness)
    write_text(
        runtime_dir / "run_smoke.sh",
        "python runtime/score_batch.py --input data/smoke_input_batch.csv --output outputs/vendor_outputs.jsonl",
    )

    doc_note = """
    Vendor Method Note

    Package contains executable scoring runtime and batch interface only. The vendor has not supplied training data, model development evidence,
    coefficient tables, challenger benchmarks, or feature lineage documentation in this package. Output includes risk score, decision, and up to three reason codes.
    """
    write_text(docs_dir / "vendor_method_note.md", doc_note)
    write_text(
        docs_dir / "output_contract.json",
        json.dumps(
            {
                "fields": [
                    "application_id",
                    "risk_probability",
                    "risk_score",
                    "decision",
                    "reason_codes",
                ]
            },
            indent=2,
        ),
    )
    pd.DataFrame(
        [
            {"reason_code": "RC101", "label": "External credit score below minimum expectation."},
            {"reason_code": "RC104", "label": "Debt burden exceeds policy tolerance."},
            {"reason_code": "RC112", "label": "Revolving utilization is elevated."},
            {
                "reason_code": "RC207",
                "label": "Thin file reduced confidence in repayment estimate.",
            },
        ]
    ).to_csv(docs_dir / "vendor_reason_table.csv", index=False)

    prod_reference = pd.DataFrame(
        {
            "score_band": [
                "300-499",
                "500-549",
                "550-599",
                "600-649",
                "650-699",
                "700-749",
                "750-850",
            ],
            "production_share": [0.04, 0.08, 0.13, 0.18, 0.24, 0.21, 0.12],
        }
    )
    prod_reference.to_csv(data_dir / "production_score_distribution.csv", index=False)

    return {
        "demo_id": "runtime_behavioral",
        "title": "Vendor Black-Box Behavioral Review",
        "description": "Opaque vendor scoring package with executable runtime, smoke inputs, and limited supporting documentation.",
        "expected_case_type": "vendor_black_box_review",
        "package_dir": "runtime_behavioral/package",
        "highlights": [
            "Runtime harness is executable but conceptual design evidence is absent.",
            "Reason code table omits the generic RC900 output actually produced by the harness.",
            "Package includes a production score distribution for behavioral comparison.",
        ],
        "expected_workflow": "black_box_behavioral_review",
        "expected_report_type": "partial_validation_report",
        "minimum_coverage_ratio": 0.75,
    }


def build_documentation_case(root: Path) -> dict[str, object]:
    rng = np.random.default_rng(31)
    case_dir = ensure_dir(root / "documentation_readiness" / "package")
    shutil.rmtree(case_dir, ignore_errors=True)
    case_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = ensure_dir(case_dir / "docs")
    data_dir = ensure_dir(case_dir / "data")

    sample_size = 640
    frame = pd.DataFrame(
        {
            "account_id": [f"DOC-{idx:05d}" for idx in range(sample_size)],
            "channel": rng.choice(
                ["branch", "call_center", "digital"], p=[0.42, 0.21, 0.37], size=sample_size
            ),
            "fico_band": rng.choice(
                ["subprime", "near_prime", "prime"], p=[0.22, 0.39, 0.39], size=sample_size
            ),
            "ltv_ratio": np.round(np.clip(rng.normal(0.78, 0.11, size=sample_size), 0.35, 1.15), 4),
            "dti_ratio": np.round(np.clip(rng.normal(0.34, 0.13, size=sample_size), 0.05, 0.81), 4),
            "payment_shock_index": np.round(
                np.clip(rng.normal(0.24, 0.16, size=sample_size), 0.0, 1.2), 4
            ),
            "verified_income_stability": np.round(
                np.clip(rng.normal(0.64, 0.21, size=sample_size), 0.0, 1.0), 4
            ),
            "manual_override_flag": rng.binomial(1, 0.08, size=sample_size),
            "self_employed_flag": rng.binomial(1, 0.14, size=sample_size),
            "zip_risk_band": rng.choice(
                ["low", "moderate", "elevated"], p=[0.48, 0.35, 0.17], size=sample_size
            ),
        }
    )
    missing_mask = rng.binomial(1, 0.31, size=sample_size).astype(bool)
    frame.loc[missing_mask, "verified_income_stability"] = np.nan
    frame.to_csv(data_dir / "sample_extract.csv", index=False)

    methodology = """
    Home Equity Line Credit Methodology

    The model card states that the current underwriting model is a logistic regression using 18 features spanning borrower capacity,
    collateral performance, and payment resilience. Adverse-action support is available for every feature eligible to appear in the top three drivers.

    Monthly monitoring is described as including population stability, score migration, override tracking, and reason-code coverage testing.
    Runtime package and score reproducibility scripts are maintained by the model development team and are available upon request.
    """
    write_text(docs_dir / "model_methodology.md", methodology)

    model_card = """
    Model Card Summary

    Current version: HEL-2025-Q1.
    Primary objective: approve home-equity line applicants while constraining bad rate under adverse housing-price scenarios.
    Inputs listed in the model card: 22 features, including payment_shock_index, verified_income_stability, override propensity, and zip risk band.

    The model card notes that reason-code coverage is still being refreshed after the collateral feature expansion delivered in February.
    """
    write_text(docs_dir / "model_card.md", model_card)

    prior_memo = """
    Prior Validation Memorandum

    The prior review concluded that conceptual soundness was conditionally acceptable, subject to delivery of execution artifacts,
    monitoring evidence for payment-shock drift, and a refreshed adverse-action mapping for any newly introduced resilience variables.
    Those materials were not in the prior package and should be requested again before implementation approval.
    """
    write_text(docs_dir / "prior_validation_memo.md", prior_memo)

    pd.DataFrame(
        [
            {
                "feature_name": "fico_band",
                "business_definition": "External bureau risk band",
                "documented": 1,
            },
            {
                "feature_name": "ltv_ratio",
                "business_definition": "Current combined loan-to-value ratio",
                "documented": 1,
            },
            {
                "feature_name": "dti_ratio",
                "business_definition": "Debt burden at application",
                "documented": 1,
            },
            {
                "feature_name": "payment_shock_index",
                "business_definition": "Estimated payment shock under stress",
                "documented": 1,
            },
            {
                "feature_name": "verified_income_stability",
                "business_definition": "Stability score based on verified income trends",
                "documented": 1,
            },
            {
                "feature_name": "manual_override_flag",
                "business_definition": "Indicator that manual override channel was used",
                "documented": 1,
            },
            {
                "feature_name": "override_propensity_score",
                "business_definition": "Estimated probability of manual override",
                "documented": 1,
            },
            {
                "feature_name": "zip_risk_band",
                "business_definition": "Internal ZIP concentration risk band",
                "documented": 1,
            },
        ]
    ).to_csv(docs_dir / "feature_dictionary.csv", index=False)

    pd.DataFrame(
        [
            {
                "feature_name": "fico_band",
                "reason_code": "HE001",
                "consumer_statement": "Credit profile did not meet minimum expectation.",
            },
            {
                "feature_name": "ltv_ratio",
                "reason_code": "HE014",
                "consumer_statement": "Combined loan-to-value was higher than policy allows.",
            },
            {
                "feature_name": "dti_ratio",
                "reason_code": "HE019",
                "consumer_statement": "Debt obligations were high relative to income.",
            },
            {
                "feature_name": "manual_override_flag",
                "reason_code": "HE099",
                "consumer_statement": "Overall application profile required manual review.",
            },
            {
                "feature_name": "zip_risk_band",
                "reason_code": "HE099",
                "consumer_statement": "Overall application profile required manual review.",
            },
        ]
    ).to_csv(docs_dir / "reason_code_mapping.csv", index=False)

    return {
        "demo_id": "documentation_readiness",
        "title": "Documentation-Led Conceptual Review",
        "description": "Documentation-heavy package with sample data, feature dictionary, and adverse-action mapping but no runnable implementation.",
        "expected_case_type": "conceptual_documentation_review",
        "package_dir": "documentation_readiness/package",
        "highlights": [
            "Feature counts conflict across methodology and model card artifacts.",
            "Reason-code mapping omits payment_shock_index and verified_income_stability.",
            "Sample extract includes elevated missingness in verified income stability.",
            "Documentation pack is designed for rubric-based readiness benchmarking plus Codex synthesis.",
        ],
        "expected_workflow": "conceptual_readiness_review",
        "expected_report_type": "conceptual_readiness_memo",
        "minimum_coverage_ratio": 0.5,
    }


def main() -> None:
    shutil.rmtree(DEMO_ROOT, ignore_errors=True)
    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    descriptors = [
        build_material_change_case(DEMO_ROOT),
        build_black_box_case(DEMO_ROOT),
        build_documentation_case(DEMO_ROOT),
    ]
    for descriptor in descriptors:
        descriptor_path = DEMO_ROOT / descriptor["demo_id"] / "descriptor.json"
        write_text(descriptor_path, json.dumps(descriptor, indent=2))
    write_text(
        DEMO_ROOT / "README.md",
        """
        Synthetic demo cases for the Codex-native validation workbench.

        These packages are intentionally heterogeneous and incomplete in different ways so the workbench has to discover
        what is present, resolve what is actually supported, and produce different validation outputs.
        """,
    )


if __name__ == "__main__":
    main()
