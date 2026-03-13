import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MODEL_NAME = "cedar_retail_bank_2025.2"
INTERCEPT = -2.21
THRESHOLD = 0.39
COEFFICIENTS = {"bureau_headroom": 1.2, "delinquency_12m": 0.52, "dti_ratio": 1.31, "inquiries_6m": 0.14, "low_cash_buffer": 0.54, "short_tenure": 0.2, "thin_file_flag": 0.51, "utilization_rate": 0.73}
REASON_CODES = {"bureau_headroom": "LOW_BUREAU_SCORE", "delinquency_12m": "RECENT_DELINQUENCY", "dti_ratio": "HIGH_DTI", "inquiries_6m": "RECENT_CREDIT_SEEKING", "low_cash_buffer": "LOW_CASH_BUFFER", "short_tenure": "SHORT_EMPLOYMENT_TENURE", "thin_file_flag": "THIN_CREDIT_FILE", "utilization_rate": "HIGH_UTILIZATION"}


def _sigmoid(values):
    return 1.0 / (1.0 + np.exp(-values))


def _features(frame):
    return pd.DataFrame({
        "bureau_headroom": np.clip((720 - frame["bureau_score"]) / 120, 0, None),
        "dti_ratio": frame["dti_ratio"],
        "utilization_rate": frame["utilization_rate"],
        "delinquency_12m": frame["delinquency_12m"],
        "inquiries_6m": frame["inquiries_6m"],
        "thin_file_flag": frame["thin_file_flag"],
        "short_tenure": np.clip((24 - frame["employment_tenure_mo"]) / 24, 0, None),
        "low_cash_buffer": np.clip((6 - frame["recent_cash_buffer_mo"]) / 6, 0, None),
    })


def score_frame(frame):
    features = _features(frame)
    linear = np.full(len(frame), INTERCEPT, dtype=float)
    contribution_map = {}
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
    summary = {
        "model_name": MODEL_NAME,
        "rows": int(len(scored)),
        "approval_rate": round(float((scored["decision"] == "approve").mean()), 4),
        "average_score": round(float(scored["score"].mean()), 2),
    }
    Path(args.output).with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
