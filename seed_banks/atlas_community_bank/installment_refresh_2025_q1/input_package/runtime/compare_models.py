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
