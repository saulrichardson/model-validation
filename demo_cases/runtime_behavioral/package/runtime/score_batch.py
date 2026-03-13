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
    Path(args.output).write_text("\n".join(scored.to_json(orient="records", lines=True).splitlines()), encoding="utf-8")

if __name__ == "__main__":
    main()
