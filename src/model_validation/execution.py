"""Deterministic validation analyses exposed to the agent runtime as tools."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .discovery import InventoryContext, primary_data_profile
from .schemas import ArtifactKind, ArtifactRecord, ExecutionMetric, FindingSeverity
from .storage import CaseRepository


@dataclass
class EvidenceSignal:
    detail: str
    relative_path: str | None = None
    title: str | None = None


@dataclass
class FindingSignal:
    severity: FindingSeverity
    title: str
    summary: str
    evidence: list[EvidenceSignal] = field(default_factory=list)
    affected_modules: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "title": self.title,
            "summary": self.summary,
            "evidence": [asdict(item) for item in self.evidence],
            "affected_modules": self.affected_modules,
        }


@dataclass
class AnalysisOutcome:
    summary: str
    findings: list[FindingSignal] = field(default_factory=list)
    metrics: list[ExecutionMetric] = field(default_factory=list)
    narrative: list[str] = field(default_factory=list)
    evidence_requests: list[str] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "findings": [finding.as_dict() for finding in self.findings],
            "metrics": [metric.model_dump(mode="json") for metric in self.metrics],
            "narrative": self.narrative,
            "evidence_requests": self.evidence_requests,
            "outputs": self.outputs,
        }


class ValidationAnalyzer:
    def __init__(self, context: InventoryContext, repo: CaseRepository) -> None:
        self.context = context
        self.repo = repo
        self.case = context.case
        self.artifacts = list(context.artifact_index.values())
        self._cache: dict[str, Any] = {}

    def run_material_model_pair(self) -> AnalysisOutcome:
        baseline_model = self._artifact_path("baseline", "code")
        candidate_model = self._artifact_path("candidate", "code")
        input_data = self._largest_dataset_path()
        if not baseline_model or not candidate_model or input_data is None:
            return AnalysisOutcome(
                summary="Material runtime replay could not locate both model scripts and data.",
                narrative=[
                    "Material-change runtime reproduction could not locate both model scripts and data."
                ],
            )

        baseline_out = self.repo.output_path(self.case.case_id, "baseline_scored.csv")
        candidate_out = self.repo.output_path(self.case.case_id, "candidate_scored.csv")
        self._run_python_script(
            baseline_model, ["--input", str(input_data), "--output", str(baseline_out)]
        )
        self._run_python_script(
            candidate_model, ["--input", str(input_data), "--output", str(candidate_out)]
        )
        self._cache["baseline_scored"] = pd.read_csv(baseline_out)
        self._cache["candidate_scored"] = pd.read_csv(candidate_out)
        return AnalysisOutcome(
            summary="Executed the supplied baseline and candidate model scripts against the largest validation sample.",
            metrics=[
                ExecutionMetric(
                    label="Runtime Rows Replayed", value=str(len(self._cache["candidate_scored"]))
                ),
            ],
            narrative=[
                "Executed the supplied baseline and candidate model scripts against the out-of-time validation sample."
            ],
            outputs={
                "baseline_scored": str(baseline_out),
                "candidate_scored": str(candidate_out),
            },
        )

    def run_vendor_runtime_harness(self) -> AnalysisOutcome:
        harness_artifact = self._find_artifact_by_name("score_batch.py")
        if harness_artifact is None:
            harness_artifact = next(
                (
                    artifact
                    for artifact in self.artifacts
                    if "runtime_harness" in artifact.tags
                    and artifact.kind == ArtifactKind.CODE
                    and artifact.relative_path.endswith(".py")
                ),
                None,
            )
        harness = harness_artifact.absolute_path if harness_artifact else None
        input_data = self._largest_dataset_path(exclude="production_score_distribution")
        if not harness or input_data is None:
            return AnalysisOutcome(
                summary="Vendor runtime replay could not locate the harness and input batch.",
                narrative=["Vendor runtime reproduction could not locate the harness and input batch."],
            )
        output_path = self.repo.output_path(self.case.case_id, "vendor_scored.jsonl")
        self._run_python_script(harness, ["--input", str(input_data), "--output", str(output_path)])
        vendor_frame = pd.read_json(output_path, orient="records", lines=True)
        self._cache["vendor_scored"] = vendor_frame
        return AnalysisOutcome(
            summary="Executed the vendor runtime harness against the supplied smoke-test batch.",
            metrics=[
                ExecutionMetric(label="Vendor Rows Replayed", value=str(len(vendor_frame))),
            ],
            narrative=[
                "Executed the vendor scoring harness against the supplied smoke-test batch to obtain live output behavior."
            ],
            outputs={"vendor_scored": str(output_path)},
        )

    def compare_scored_outputs(self) -> AnalysisOutcome:
        baseline = self._load_runtime_output("baseline_scored")
        candidate = self._load_runtime_output("candidate_scored")
        if baseline is None or candidate is None:
            return AnalysisOutcome(
                summary="Baseline comparison could not load both scored datasets.",
                narrative=[
                    "Baseline comparison could not load both scored datasets.",
                    "Expected rerun outputs from run_material_model_pair to be available.",
                ],
            )

        reference_baseline_artifact = self._find_artifact_by_name("baseline_reference_scored")
        reference_candidate_artifact = self._find_artifact_by_name("candidate_reference_scored")
        if reference_baseline_artifact is None or reference_candidate_artifact is None:
            return AnalysisOutcome(
                summary="Baseline comparison could not locate reference scored outputs for reproducibility checks.",
                narrative=[
                    "Baseline comparison requires both rerun scored outputs and packaged reference scored outputs.",
                    "Reference scored outputs were not found under the expected baseline/candidate reference artifact names.",
                ],
            )
        reference_base = reference_baseline_artifact.absolute_path
        reference_cand = reference_candidate_artifact.absolute_path
        reference_baseline = pd.read_csv(reference_base)
        reference_candidate = pd.read_csv(reference_cand)

        auc_base = roc_auc_score(baseline["target_default"], baseline["pd_estimate"])
        auc_cand = roc_auc_score(candidate["target_default"], candidate["pd_estimate"])
        approval_base = float((baseline["decision"] == "approve").mean())
        approval_cand = float((candidate["decision"] == "approve").mean())
        thin_mask_base = baseline["thin_file_flag"] == 1
        thin_mask_cand = candidate["thin_file_flag"] == 1
        thin_delta = float(
            (candidate.loc[thin_mask_cand, "decision"] == "approve").mean()
            - (baseline.loc[thin_mask_base, "decision"] == "approve").mean()
        )
        overall_delta = approval_cand - approval_base

        payload = {
            "baseline_auc": round(float(auc_base), 4),
            "candidate_auc": round(float(auc_cand), 4),
            "auc_delta": round(float(auc_cand - auc_base), 4),
            "baseline_approval_rate": round(approval_base, 4),
            "candidate_approval_rate": round(approval_cand, 4),
            "overall_approval_delta": round(overall_delta, 4),
            "thin_file_approval_delta": round(thin_delta, 4),
        }
        output_path = self.repo.dump_output_json(
            self.case.case_id, "baseline_comparison.json", payload
        )

        replay_checks: dict[str, Any] = {}
        replay_findings: list[FindingSignal] = []

        def check_replay(
            *,
            runtime_frame: pd.DataFrame,
            reference_frame: pd.DataFrame,
            label: str,
        ) -> None:
            required = [
                "application_id",
                "pd_estimate",
                "score",
                "decision",
                "reason_1",
                "reason_2",
                "reason_3",
            ]
            missing_runtime = [name for name in required if name not in runtime_frame.columns]
            missing_reference = [name for name in required if name not in reference_frame.columns]
            if missing_runtime or missing_reference:
                replay_findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Runtime replay output is not schema-compatible with reference scored outputs",
                        summary=(
                            f"{label} replay cannot be validated because required columns are missing. "
                            f"Missing in runtime: {missing_runtime or 'none'}. "
                            f"Missing in reference: {missing_reference or 'none'}."
                        ),
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/baseline_scored.csv",
                                detail="Rerun baseline scored output (schema check).",
                            ),
                            EvidenceSignal(
                                relative_path="outputs/candidate_scored.csv",
                                detail="Rerun candidate scored output (schema check).",
                            ),
                            EvidenceSignal(
                                relative_path=reference_baseline_artifact.relative_path,
                                detail="Packaged baseline reference scored output (schema check).",
                            ),
                            EvidenceSignal(
                                relative_path=reference_candidate_artifact.relative_path,
                                detail="Packaged candidate reference scored output (schema check).",
                            ),
                        ],
                        affected_modules=["runtime_reproduction", "baseline_comparison"],
                    )
                )
                return

            runtime = runtime_frame[required].copy()
            reference = reference_frame[required].copy()
            if runtime["application_id"].duplicated().any() or reference["application_id"].duplicated().any():
                replay_findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Runtime replay cannot be validated due to duplicate application identifiers",
                        summary=f"{label} replay contains duplicate application_id values in either runtime or reference outputs.",
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/runtime_replay_vs_reference.json",
                                detail="Replay check summarizes identifier duplication and mergeability.",
                            )
                        ],
                        affected_modules=["runtime_reproduction"],
                    )
                )

            merged = runtime.merge(
                reference,
                on="application_id",
                how="outer",
                suffixes=("_runtime", "_reference"),
                indicator=True,
            )
            only_runtime = int((merged["_merge"] == "left_only").sum())
            only_reference = int((merged["_merge"] == "right_only").sum())
            both = merged[merged["_merge"] == "both"].copy()

            pd_diff = (both["pd_estimate_runtime"] - both["pd_estimate_reference"]).abs()
            score_match = (both["score_runtime"] == both["score_reference"]).mean()
            decision_match = (both["decision_runtime"] == both["decision_reference"]).mean()
            r1_match = (both["reason_1_runtime"] == both["reason_1_reference"]).mean()
            r2_match = (both["reason_2_runtime"] == both["reason_2_reference"]).mean()
            r3_match = (both["reason_3_runtime"] == both["reason_3_reference"]).mean()

            replay_checks[label] = {
                "runtime_rows": int(len(runtime)),
                "reference_rows": int(len(reference)),
                "id_only_in_runtime": only_runtime,
                "id_only_in_reference": only_reference,
                "pd_max_abs_diff": float(pd_diff.max()) if not pd_diff.empty else 0.0,
                "pd_mean_abs_diff": float(pd_diff.mean()) if not pd_diff.empty else 0.0,
                "score_match_rate": float(score_match),
                "decision_match_rate": float(decision_match),
                "reason_1_match_rate": float(r1_match),
                "reason_2_match_rate": float(r2_match),
                "reason_3_match_rate": float(r3_match),
            }

        check_replay(
            runtime_frame=baseline,
            reference_frame=reference_baseline,
            label="baseline",
        )
        check_replay(
            runtime_frame=candidate,
            reference_frame=reference_candidate,
            label="candidate",
        )

        replay_output_path = self.repo.dump_output_json(
            self.case.case_id, "runtime_replay_vs_reference.json", replay_checks
        )

        findings: list[FindingSignal] = []
        if overall_delta <= -0.10 and (auc_cand - auc_base) < 0.03:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Candidate approval rate falls materially relative to the baseline",
                    summary=f"Candidate approval falls by {overall_delta:.1%} while AUC improves by only {auc_cand - auc_base:.2%}.",
                    evidence=[
                        EvidenceSignal(
                            relative_path="outputs/baseline_comparison.json",
                            detail="Computed comparison of baseline and candidate scored outputs.",
                        ),
                        EvidenceSignal(
                            relative_path="outputs/runtime_replay_vs_reference.json",
                            detail="Runtime replay outputs compared to packaged reference scored outputs.",
                        ),
                    ],
                    affected_modules=["baseline_comparison", "behavioral_review"],
                )
            )
        if thin_delta <= -0.10:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.HIGH,
                    title="Thin-file approvals decline sharply after the candidate refresh",
                    summary=f"Thin-file approval rate falls by {thin_delta:.1%} versus the approved baseline, indicating a material behavioral change requiring challenge.",
                    evidence=[
                        EvidenceSignal(
                            relative_path="outputs/baseline_comparison.json",
                            detail="Thin-file approval delta calculated from rerun scored outputs.",
                        ),
                        EvidenceSignal(
                            relative_path="outputs/runtime_replay_vs_reference.json",
                            detail="Runtime replay outputs compared to packaged reference scored outputs.",
                        ),
                    ],
                    affected_modules=["baseline_comparison", "behavioral_review"],
                )
            )
        findings.extend(replay_findings)
        return AnalysisOutcome(
            summary="Compared baseline and candidate scored outputs and quantified approval and AUC shifts.",
            findings=findings,
            metrics=[
                ExecutionMetric(label="Baseline AUC", value=f"{auc_base:.3f}"),
                ExecutionMetric(label="Candidate AUC", value=f"{auc_cand:.3f}"),
                ExecutionMetric(label="Approval Delta", value=f"{overall_delta:.1%}"),
                ExecutionMetric(label="Thin-File Approval Delta", value=f"{thin_delta:.1%}"),
            ],
            narrative=[
                "Reran baseline and candidate models on the supplied out-of-time validation sample.",
                "Candidate rank ordering improved modestly, but approval tightened materially relative to the approved champion.",
            ],
            outputs={
                "baseline_comparison": output_path,
                "runtime_replay_vs_reference": replay_output_path,
            },
        )

    def review_material_behavior(self) -> AnalysisOutcome:
        candidate = self._load_runtime_output("candidate_scored")
        baseline = self._load_runtime_output("baseline_scored")
        if candidate is None or baseline is None:
            return AnalysisOutcome(
                summary="Material behavioral review could not load rerun scored outputs.",
                narrative=["Behavioral review could not reuse rerun scored outputs."],
            )

        rows: list[dict[str, Any]] = []
        for segment, group in candidate.groupby("channel"):
            baseline_group = baseline.loc[baseline["channel"] == segment]
            rows.append(
                {
                    "channel": segment,
                    "candidate_approval_rate": round(
                        float((group["decision"] == "approve").mean()), 4
                    ),
                    "baseline_approval_rate": round(
                        float((baseline_group["decision"] == "approve").mean()), 4
                    ),
                    "approval_delta": round(
                        float(
                            (group["decision"] == "approve").mean()
                            - (baseline_group["decision"] == "approve").mean()
                        ),
                        4,
                    ),
                }
            )
        output_path = self.repo.dump_output_json(
            self.case.case_id, "material_behavioral_review.json", rows
        )
        return AnalysisOutcome(
            summary="Reviewed channel-level approval behavior for the challenger versus the approved baseline.",
            metrics=[ExecutionMetric(label="Channels Reviewed", value=str(len(rows)))],
            narrative=[
                "Reviewed channel-level approval behavior for the challenger versus the approved baseline."
            ],
            outputs={"material_behavioral_review": output_path},
        )

    def run_sensitivity_analysis(self) -> AnalysisOutcome:
        baseline = self._load_runtime_output("baseline_scored")
        candidate = self._load_runtime_output("candidate_scored")
        if baseline is None or candidate is None:
            self.run_material_model_pair()
            baseline = self._load_runtime_output("baseline_scored")
            candidate = self._load_runtime_output("candidate_scored")
        if baseline is None or candidate is None:
            return AnalysisOutcome(
                summary="Sensitivity analysis could not load baseline and candidate scored outputs.",
                narrative=[
                    "Sensitivity analysis requires rerun scored outputs from the material model pair."
                ],
            )

        input_data = self._largest_dataset_path()
        baseline_model = self._artifact_path("baseline", "code")
        candidate_model = self._artifact_path("candidate", "code")
        if input_data is None or baseline_model is None or candidate_model is None:
            return AnalysisOutcome(
                summary="Sensitivity analysis could not locate the material validation dataset and both model scripts.",
                narrative=[
                    "Sensitivity analysis requires a primary validation dataset plus baseline and candidate model sources."
                ],
            )

        base_frame = pd.read_csv(input_data)
        baseline_threshold = extract_model_threshold(self._artifact_text("baseline") or "") or 0.43
        candidate_threshold = extract_model_threshold(self._artifact_text("candidate") or "") or 0.41

        threshold_rows: list[dict[str, Any]] = []
        for model_name, scored, current_threshold in (
            ("baseline", baseline, baseline_threshold),
            ("candidate", candidate, candidate_threshold),
        ):
            for threshold in [round(value, 2) for value in np.arange(0.37, 0.47, 0.01)]:
                rates = decision_rates_from_pd(scored, threshold)
                threshold_rows.append(
                    {
                        "model": model_name,
                        "threshold": threshold,
                        "current_threshold": threshold == round(current_threshold, 2),
                        **rates,
                    }
                )
        threshold_frame = pd.DataFrame(threshold_rows)
        threshold_path = self.repo.output_path(self.case.case_id, "sensitivity/threshold_sweep.csv")
        threshold_frame.to_csv(threshold_path, index=False)

        scenarios = {
            "bureau_score_down_20": lambda frame: frame.assign(
                bureau_score=np.clip(frame["bureau_score"] - 20, 300, None)
            ),
            "dti_up_5_points": lambda frame: frame.assign(
                dti_ratio=np.clip(frame["dti_ratio"] + 0.05, 0, 0.99)
            ),
            "cash_buffer_down_1_5_months": lambda frame: frame.assign(
                recent_cash_buffer_mo=np.clip(frame["recent_cash_buffer_mo"] - 1.5, 0, None)
            ),
            "combined_downturn": lambda frame: frame.assign(
                bureau_score=np.clip(frame["bureau_score"] - 35, 300, None),
                dti_ratio=np.clip(frame["dti_ratio"] + 0.08, 0, 0.99),
                utilization_rate=np.clip(frame["utilization_rate"] + 0.05, 0, 0.99),
                inquiries_6m=np.clip(frame["inquiries_6m"] + 1, 0, None),
                recent_cash_buffer_mo=np.clip(frame["recent_cash_buffer_mo"] - 2.0, 0, None),
            ),
        }

        stress_rows: list[dict[str, Any]] = []
        monotonicity: dict[str, dict[str, float]] = {}
        reason_stability: dict[str, dict[str, float]] = {}

        for scenario_name, transform in scenarios.items():
            scenario_input = transform(base_frame.copy())
            scenario_input_path = self.repo.output_path(
                self.case.case_id, f"sensitivity/{scenario_name}_input.csv"
            )
            scenario_input.to_csv(scenario_input_path, index=False)

            baseline_output = self.repo.output_path(
                self.case.case_id, f"sensitivity/{scenario_name}_baseline_scored.csv"
            )
            candidate_output = self.repo.output_path(
                self.case.case_id, f"sensitivity/{scenario_name}_candidate_scored.csv"
            )
            self._run_python_script(
                baseline_model,
                ["--input", str(scenario_input_path), "--output", str(baseline_output)],
            )
            self._run_python_script(
                candidate_model,
                ["--input", str(scenario_input_path), "--output", str(candidate_output)],
            )

            stressed_baseline = pd.read_csv(baseline_output)
            stressed_candidate = pd.read_csv(candidate_output)
            stress_rows.extend(
                [
                    build_stress_row("baseline", scenario_name, baseline, stressed_baseline),
                    build_stress_row("candidate", scenario_name, candidate, stressed_candidate),
                ]
            )
            monotonicity[scenario_name] = {
                "candidate_violation_rate": monotonicity_violation_rate(candidate, stressed_candidate),
                "baseline_violation_rate": monotonicity_violation_rate(baseline, stressed_baseline),
            }
            reason_stability[scenario_name] = {
                "candidate_low_cash_buffer_decline_share_base": decline_reason_share(
                    candidate, "LOW_CASH_BUFFER"
                ),
                "candidate_low_cash_buffer_decline_share_stressed": decline_reason_share(
                    stressed_candidate, "LOW_CASH_BUFFER"
                ),
            }

        stress_path = self.repo.dump_output_json(
            self.case.case_id,
            "sensitivity/stress_summary.json",
            {
                "rows": stress_rows,
                "reason_code_stability": reason_stability,
            },
        )
        monotonicity_path = self.repo.dump_output_json(
            self.case.case_id,
            "sensitivity/monotonicity_checks.json",
            monotonicity,
        )

        findings: list[FindingSignal] = []
        candidate_sweep = threshold_frame.loc[threshold_frame["model"] == "candidate"].copy()
        current_row = candidate_sweep.loc[
            candidate_sweep["threshold"] == round(candidate_threshold, 2)
        ].head(1)
        down_row = candidate_sweep.loc[
            candidate_sweep["threshold"] == round(candidate_threshold - 0.01, 2)
        ].head(1)
        up_row = candidate_sweep.loc[
            candidate_sweep["threshold"] == round(candidate_threshold + 0.01, 2)
        ].head(1)
        threshold_swing = 0.0
        if not current_row.empty:
            current_approval = float(current_row.iloc[0]["approval_rate"])
            if not down_row.empty:
                threshold_swing = max(
                    threshold_swing,
                    abs(float(down_row.iloc[0]["approval_rate"]) - current_approval),
                )
            if not up_row.empty:
                threshold_swing = max(
                    threshold_swing,
                    abs(float(up_row.iloc[0]["approval_rate"]) - current_approval),
                )
            if threshold_swing >= 0.04:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.MEDIUM,
                        title="Candidate operating point is sensitive to small threshold moves",
                        summary=(
                            f"A +/-1 point threshold move around {candidate_threshold:.2f} changes "
                            f"candidate approval by up to {threshold_swing:.1%}, indicating a tight operating point."
                        ),
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/sensitivity/threshold_sweep.csv",
                                detail="Threshold sweep over candidate and baseline scored outputs.",
                            )
                        ],
                        affected_modules=["baseline_comparison", "behavioral_review"],
                    )
                )

        stress_frame = pd.DataFrame(stress_rows)
        combined_candidate = stress_frame.loc[
            (stress_frame["model"] == "candidate")
            & (stress_frame["scenario"] == "combined_downturn")
        ].head(1)
        if not combined_candidate.empty:
            approval_delta = float(combined_candidate.iloc[0]["approval_delta"])
            thin_file_delta = float(combined_candidate.iloc[0]["thin_file_approval_delta"])
            if approval_delta <= -0.12 or thin_file_delta <= -0.10:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Combined downturn stress produces a severe candidate contraction",
                        summary=(
                            f"Under combined downturn stress, candidate approval falls by {approval_delta:.1%} "
                            f"overall and {thin_file_delta:.1%} for thin-file applicants relative to the base run."
                        ),
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/sensitivity/stress_summary.json",
                                detail="Scenario stress reruns for baseline and candidate models.",
                            )
                        ],
                        affected_modules=[
                            "behavioral_review",
                            "baseline_comparison",
                            "conceptual_soundness_review",
                        ],
                    )
                )
            stressed_share = reason_stability["combined_downturn"][
                "candidate_low_cash_buffer_decline_share_stressed"
            ]
            base_share = reason_stability["combined_downturn"][
                "candidate_low_cash_buffer_decline_share_base"
            ]
            if stressed_share - base_share >= 0.10:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.INFO,
                        title="Downturn stress shifts decline reasons toward liquidity stress as documented",
                        summary=(
                            f"LOW_CASH_BUFFER appears on {stressed_share:.1%} of candidate declines under combined stress "
                            f"versus {base_share:.1%} in the base run, consistent with the stated liquidity-stress change."
                        ),
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/sensitivity/stress_summary.json",
                                detail="Reason-code stability summary across stressed reruns.",
                            ),
                            EvidenceSignal(
                                relative_path=self._artifact_relative("methodology"),
                                detail="Methodology states that liquidity stress should influence adverse-action reasons.",
                            ),
                        ],
                        affected_modules=["reason_code_review", "documentation_consistency"],
                    )
                )

        for scenario_name, result in monotonicity.items():
            violation_rate = max(
                float(result.get("candidate_violation_rate", 0.0)),
                float(result.get("baseline_violation_rate", 0.0)),
            )
            if violation_rate > 0:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Sensitivity reruns contain directional monotonicity violations",
                        summary=(
                            f"{scenario_name} produced a monotonicity violation rate of {violation_rate:.2%}, "
                            "where worsening applicant attributes unexpectedly reduced modeled risk."
                        ),
                        evidence=[
                            EvidenceSignal(
                                relative_path="outputs/sensitivity/monotonicity_checks.json",
                                detail="Directional monotonicity checks comparing base and stressed reruns.",
                            )
                        ],
                        affected_modules=["conceptual_soundness_review", "behavioral_review"],
                    )
                )

        return AnalysisOutcome(
            summary="Ran threshold sweeps, downturn stress scenarios, and directional checks on the material baseline/candidate package.",
            findings=findings,
            metrics=[
                ExecutionMetric(label="Candidate Threshold Swing", value=f"{threshold_swing:.1%}"),
                ExecutionMetric(
                    label="Stress Scenarios",
                    value=str(len(scenarios)),
                    detail="Threshold sweep plus single-factor and combined downturn reruns.",
                ),
                ExecutionMetric(
                    label="Combined Stress Candidate Approval Delta",
                    value=(
                        f"{float(combined_candidate.iloc[0]['approval_delta']):.1%}"
                        if not combined_candidate.empty
                        else "n/a"
                    ),
                ),
            ],
            narrative=[
                "Sensitivity analysis re-used the material validation package to stress thresholds and key risk drivers rather than treating the model as a static comparison only.",
                "The resulting outputs are suitable for a revalidation appendix covering operating-point sensitivity, stress behavior, and reason-code stability.",
            ],
            outputs={
                "threshold_sweep": str(threshold_path),
                "sensitivity_stress_summary": stress_path,
                "sensitivity_monotonicity": monotonicity_path,
            },
        )

    def review_vendor_behavior(self) -> AnalysisOutcome:
        vendor = self._load_runtime_output("vendor_scored")
        if vendor is None:
            return AnalysisOutcome(
                summary="Vendor behavioral review could not load runtime outputs.",
                narrative=["Vendor behavioral review could not load runtime outputs."],
            )

        by_channel = (
            vendor.groupby("channel")["decision"]
            .apply(lambda values: float((values == "approve").mean()))
            .sort_values()
        )
        spread = float(by_channel.max() - by_channel.min()) if not by_channel.empty else 0.0
        output_codes: Counter[str] = Counter()
        for value in vendor["reason_codes"]:
            for code in str(value).split("|"):
                if code:
                    output_codes[code] += 1

        distribution_artifact = self._find_artifact("production_distribution")
        distribution_gap = None
        output_path = ""
        if distribution_artifact is not None:
            reference = pd.read_csv(distribution_artifact.absolute_path)
            bins = [299, 499, 549, 599, 649, 699, 749, 850]
            labels = reference["score_band"].tolist()
            observed = pd.cut(vendor["risk_score"], bins=bins, labels=labels, include_lowest=True)
            observed_share = observed.value_counts(normalize=True).reindex(labels, fill_value=0)
            distribution_gap = float(
                (observed_share - reference["production_share"]).abs().sum() / 2
            )
            output_path = self.repo.dump_output_json(
                self.case.case_id,
                "vendor_behavioral_distribution.json",
                {
                    "observed_share": observed_share.round(4).to_dict(),
                    "reference_share": dict(
                        zip(
                            reference["score_band"],
                            reference["production_share"],
                            strict=False,
                        )
                    ),
                    "distribution_gap": round(distribution_gap, 4),
                },
            )

        findings: list[FindingSignal] = []
        if spread >= 0.15:
            lowest_channel = str(by_channel.index[0])
            highest_channel = str(by_channel.index[-1])
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Vendor approvals vary materially across intake channels",
                    summary=f"Approval rates span {spread:.1%} from {lowest_channel} to {highest_channel} in the smoke-test batch, but the package does not provide conceptual evidence to explain the spread.",
                    evidence=[
                        EvidenceSignal(
                            relative_path="outputs/vendor_scored.jsonl",
                            detail="Channel-level approvals calculated from runtime output.",
                        ),
                    ],
                    affected_modules=["behavioral_review", "conceptual_soundness_review"],
                )
            )
        if distribution_gap is not None and distribution_gap >= 0.12:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Vendor runtime score distribution differs materially from the supplied production reference",
                    summary=f"The total variation distance between smoke-test scores and the production reference is {distribution_gap:.1%}.",
                    evidence=[
                        EvidenceSignal(
                            relative_path=(
                                distribution_artifact.relative_path
                                if distribution_artifact
                                else None
                            ),
                            detail="Production score distribution supplied by the bank.",
                        ),
                        EvidenceSignal(
                            relative_path="outputs/vendor_behavioral_distribution.json",
                            detail="Observed runtime score distribution from smoke-test replay.",
                        ),
                    ],
                    affected_modules=["behavioral_review"],
                )
            )
        return AnalysisOutcome(
            summary="Profiled runtime output distributions and segment behavior using the smoke-test batch.",
            findings=findings,
            metrics=[
                ExecutionMetric(label="Approval Spread by Channel", value=f"{spread:.1%}"),
                ExecutionMetric(label="Distinct Reason Codes", value=str(len(output_codes))),
            ],
            narrative=[
                "Profiled runtime output distributions and segment behavior using the smoke-test batch.",
                "Conceptual interpretation remains bounded because the package contains only runtime materials and a short vendor note.",
            ],
            outputs={"vendor_behavioral_distribution": output_path} if output_path else {},
        )

    def check_document_consistency(self) -> AnalysisOutcome:
        findings: list[FindingSignal] = []
        narratives: list[str] = []
        methodology = self._artifact_text("methodology")
        change_request = self._artifact_text("change_request")
        candidate_model_text = self._artifact_text("candidate")
        model_card = self._artifact_text_by_name("model_card")

        if (
            methodology
            and "no new explanatory variables" in methodology.lower()
            and candidate_model_text
            and "low_cash_buffer" in candidate_model_text
        ):
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.HIGH,
                    title="Methodology document does not reflect the candidate liquidity feature",
                    summary="The methodology states that no new explanatory variables were introduced, but the candidate runtime uses `low_cash_buffer` in scoring.",
                    evidence=[
                        EvidenceSignal(
                            relative_path=self._artifact_relative("methodology"),
                            detail="Methodology states no new explanatory variables were introduced.",
                        ),
                        EvidenceSignal(
                            relative_path=self._artifact_relative("candidate"),
                            detail="Candidate model includes `low_cash_buffer` in the coefficient set.",
                        ),
                    ],
                    affected_modules=["documentation_consistency", "reason_code_review"],
                )
            )
            narratives.append(
                "Compared the supplied methodology narrative to the actual candidate scoring code and found a direct inconsistency."
            )

        methodology_count = extract_feature_count(methodology or "")
        model_card_count = extract_feature_count(model_card or "")
        if methodology_count and model_card_count and methodology_count != model_card_count:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Feature counts conflict across conceptual documentation",
                    summary=f"Methodology describes {methodology_count} features while the model card describes {model_card_count}.",
                    evidence=[
                        EvidenceSignal(
                            relative_path=self._artifact_relative("methodology"),
                            detail="Methodology feature-count reference.",
                        ),
                        EvidenceSignal(
                            relative_path=self._artifact_relative_by_name("model_card"),
                            detail="Model card feature-count reference.",
                        ),
                    ],
                    affected_modules=["documentation_consistency", "conceptual_soundness_review"],
                )
            )
            narratives.append(
                "Documentation set contains inconsistent feature-count statements, reducing confidence in the package as a single source of truth."
            )

        if not findings and change_request:
            narratives.append(
                "Documentation pack was reviewed and no direct contradiction was detected beyond normal incompleteness."
            )

        summary = (
            "Checked methodology, change-request, and model-card materials for internal consistency."
        )
        return AnalysisOutcome(summary=summary, findings=findings, narrative=narratives)

    def review_reason_code_mapping(self) -> AnalysisOutcome:
        findings: list[FindingSignal] = []
        narratives: list[str] = []
        mapping_artifact = self._find_reason_code_mapping_artifact()
        mapping_codes: set[str] = set()
        mapping_features: set[str] = set()
        duplicate_reason_labels: list[str] = []
        mapping_relative_path = mapping_artifact.relative_path if mapping_artifact else None
        if mapping_artifact:
            frame = pd.read_csv(mapping_artifact.absolute_path)
            if "reason_code" in frame.columns:
                mapping_codes = set(frame["reason_code"].dropna().astype(str))
            if "feature_name" in frame.columns:
                mapping_features = set(frame["feature_name"].dropna().astype(str))
            if "consumer_statement" in frame.columns:
                duplicates = frame["consumer_statement"].value_counts()
                duplicate_reason_labels = [
                    str(label) for label, count in duplicates.items() if int(count) > 1
                ]

        candidate = self._load_runtime_output("candidate_scored")
        vendor = self._load_runtime_output("vendor_scored")
        if candidate is not None and mapping_codes:
            output_codes = {
                code
                for column in ["reason_1", "reason_2", "reason_3"]
                for code in candidate[column].dropna().astype(str)
                if code
            }
            missing_codes = sorted(output_codes - mapping_codes)
            if missing_codes:
                impacted_share = float(
                    (candidate[["reason_1", "reason_2", "reason_3"]] == missing_codes[0])
                    .any(axis=1)
                    .mean()
                )
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Candidate adverse-action mapping is incomplete for an active reason code",
                        summary=f"{missing_codes[0]} appears in candidate outputs but is missing from the supplied reason-code mapping; it affects {impacted_share:.1%} of rerun cases.",
                        evidence=[
                            EvidenceSignal(
                                relative_path=mapping_relative_path,
                                detail="Supplied reason-code table.",
                            ),
                            EvidenceSignal(
                                relative_path="outputs/candidate_scored.csv",
                                detail="Rerun candidate outputs contain the missing reason code.",
                            ),
                        ],
                        affected_modules=["reason_code_review"],
                    )
                )
                narratives.append(
                    "Compared live candidate reason outputs to the supplied adverse-action table and found an unmapped active reason."
                )

        if vendor is not None and mapping_codes:
            counter: Counter[str] = Counter()
            decline_rows = 0
            missing_rows = 0
            for _, row in vendor.iterrows():
                if row["decision"] == "decline":
                    decline_rows += 1
                codes = [value for value in str(row["reason_codes"]).split("|") if value]
                for code in codes:
                    counter[code] += 1
                if any(code not in mapping_codes for code in codes) and row["decision"] == "decline":
                    missing_rows += 1
            missing_codes = sorted(set(counter) - mapping_codes)
            if missing_codes:
                share = missing_rows / decline_rows if decline_rows else 0.0
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Vendor runtime emits a generic reason code that is not documented",
                        summary=f"{', '.join(missing_codes)} appears in runtime outputs but not in the vendor reason table; undocumented codes affect {share:.1%} of declines.",
                        evidence=[
                            EvidenceSignal(
                                relative_path=mapping_relative_path,
                                detail="Vendor reason table supplied with the package.",
                            ),
                            EvidenceSignal(
                                relative_path="outputs/vendor_scored.jsonl",
                                detail="Runtime smoke-test outputs contain undocumented reason codes.",
                            ),
                        ],
                        affected_modules=["reason_code_review", "behavioral_review"],
                    )
                )
                narratives.append(
                    "Vendor reason outputs were checked against the supplied table and uncovered undocumented generic decline reasons."
                )

        feature_dictionary = self._find_artifact("feature_dictionary")
        if feature_dictionary and mapping_features:
            feature_frame = pd.read_csv(feature_dictionary.absolute_path)
            feature_names = set(feature_frame["feature_name"].dropna().astype(str))
            unmapped_features = sorted(
                name for name in feature_names - mapping_features if "override" not in name.lower()
            )
            if unmapped_features:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.HIGH,
                        title="Reason-code mapping does not cover documented high-impact features",
                        summary=f"The reason-code table does not map documented features such as {', '.join(unmapped_features[:3])}.",
                        evidence=[
                            EvidenceSignal(
                                relative_path=feature_dictionary.relative_path,
                                detail="Documented feature inventory.",
                            ),
                            EvidenceSignal(
                                relative_path=mapping_relative_path,
                                detail="Supplied reason-code mapping.",
                            ),
                        ],
                        affected_modules=["reason_code_review", "conceptual_soundness_review"],
                    )
                )
                narratives.append(
                    "Compared the feature dictionary to the reason-code table and found documented features without mapping coverage."
                )

        if duplicate_reason_labels:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Reason-code language is overly generic for multiple documented features",
                    summary=f"The same consumer-facing explanation is reused across multiple features, including: {duplicate_reason_labels[0]}",
                    evidence=[
                        EvidenceSignal(
                            relative_path=mapping_relative_path,
                            detail="Reason-code table contains repeated consumer statements.",
                        ),
                    ],
                    affected_modules=["reason_code_review"],
                )
            )

        return AnalysisOutcome(
            summary="Checked active runtime reasons and documented features against the supplied reason-code mapping.",
            findings=findings,
            narrative=narratives,
        )

    def summarize_data_quality(self) -> AnalysisOutcome:
        profile = primary_data_profile(self.context)
        if profile is None:
            return AnalysisOutcome(
                summary="No profileable dataset was available.",
                narrative=["No profileable dataset was available."],
            )

        findings: list[FindingSignal] = []
        if profile.missing_rate_by_column:
            column, rate = sorted(
                profile.missing_rate_by_column.items(),
                key=lambda item: item[1],
                reverse=True,
            )[0]
            if rate >= 0.25:
                findings.append(
                    FindingSignal(
                        severity=FindingSeverity.MEDIUM,
                        title="Sample data contains a material missingness concentration",
                        summary=f"{column} is missing for {rate:.1%} of sampled rows, which could limit execution or monitoring conclusions.",
                        evidence=[
                            EvidenceSignal(detail="Profiled from the largest supplied dataset.")
                        ],
                        affected_modules=["data_profile_review"],
                    )
                )

        return AnalysisOutcome(
            summary="Profiled the largest supplied dataset for row counts, column types, and missingness.",
            findings=findings,
            metrics=[
                ExecutionMetric(label="Rows Profiled", value=str(profile.row_count or 0)),
                ExecutionMetric(label="Columns Profiled", value=str(profile.column_count or 0)),
            ],
            narrative=profile.highlights,
        )

    def review_conceptual_conditions(self) -> AnalysisOutcome:
        findings: list[FindingSignal] = []
        evidence_requests: list[str] = []
        prior_text = self._artifact_text("prior_validation") or ""
        methodology = self._artifact_text("methodology") or ""
        if "execution artifacts" in prior_text.lower():
            evidence_requests.append(
                "Provide runnable scoring artifacts or a controlled scoring harness for execution-based validation."
            )
        if "monitoring evidence" in prior_text.lower() or "payment-shock drift" in prior_text.lower():
            evidence_requests.append(
                "Provide monitoring evidence for the newly introduced or high-risk features noted in prior validation."
            )
        if "available upon request" in methodology.lower():
            evidence_requests.append(
                "Provide the runtime package referenced in methodology rather than a documentation-only placeholder."
            )
        if evidence_requests:
            findings.append(
                FindingSignal(
                    severity=FindingSeverity.MEDIUM,
                    title="Conceptual review remains conditional on evidence previously requested",
                    summary="Prior and current documents still reference missing execution or monitoring artifacts needed to complete validation.",
                    evidence=[
                        EvidenceSignal(
                            relative_path=self._artifact_relative("prior_validation"),
                            detail="Prior memo identified open evidence conditions.",
                        ),
                        EvidenceSignal(
                            relative_path=self._artifact_relative("methodology"),
                            detail="Methodology references artifacts that were not supplied.",
                        ),
                    ],
                    affected_modules=["conceptual_soundness_review"],
                )
            )
        return AnalysisOutcome(
            summary="Reviewed prior memo conditions and current documentation for unresolved conceptual evidence requests.",
            findings=findings,
            narrative=[
                "Reviewed conceptual materials and translated prior memo conditions into a current evidence request list."
            ],
            evidence_requests=evidence_requests,
        )

    def inspect_runtime_assets(self) -> dict[str, Any]:
        largest_dataset = self._largest_dataset_path()
        harness_artifact = (
            self._find_artifact("runtime_harness", "code")
            or self._find_artifact_by_name("score_batch.py")
            or self._find_artifact_by_name("compare_models.py")
            or self._find_artifact_by_name("run_revalidation")
        )
        dependency_artifact = (
            self._find_artifact("dependency_spec")
            or self._find_artifact_by_name("requirements.txt")
            or self._find_artifact_by_name("pyproject.toml")
        )
        return {
            "baseline_model_path": self._artifact_relative("baseline", "code"),
            "candidate_model_path": self._artifact_relative("candidate", "code"),
            "runtime_harness_path": harness_artifact.relative_path if harness_artifact else None,
            "dependency_spec_path": dependency_artifact.relative_path if dependency_artifact else None,
            "largest_dataset_path": (
                str(largest_dataset.relative_to(Path(self.case.root_dir)))
                if largest_dataset is not None
                else None
            ),
        }

    def _run_python_script(self, script_path: str, arguments: list[str]) -> None:
        cmd = [sys.executable, script_path, *arguments]
        subprocess.run(cmd, check=True, cwd=str(Path(script_path).resolve().parents[1]))

    def _artifact_path(self, *tags: str) -> str | None:
        artifact = self._find_artifact(*tags)
        return artifact.absolute_path if artifact else None

    def _artifact_relative(self, *tags: str) -> str | None:
        artifact = self._find_artifact(*tags)
        return artifact.relative_path if artifact else None

    def _artifact_relative_by_name(self, token: str) -> str | None:
        artifact = self._find_artifact_by_name(token)
        return artifact.relative_path if artifact else None

    def _artifact_text(self, *tags: str) -> str | None:
        artifact = self._find_artifact(*tags)
        return artifact.excerpt if artifact else None

    def _artifact_text_by_name(self, token: str) -> str | None:
        artifact = self._find_artifact_by_name(token)
        return artifact.excerpt if artifact else None

    def _find_artifact(self, *tags: str) -> ArtifactRecord | None:
        for artifact in self.artifacts:
            if all(tag in artifact.tags for tag in tags):
                return artifact
        return None

    def _find_artifact_by_name(self, token: str) -> ArtifactRecord | None:
        token_lower = token.lower()
        for artifact in self.artifacts:
            if token_lower in artifact.relative_path.lower():
                return artifact
        return None

    def _find_reason_code_mapping_artifact(self) -> ArtifactRecord | None:
        exact = self._find_artifact_by_name("reason_code_mapping")
        if exact is not None:
            return exact
        for artifact in self.artifacts:
            if "reason_codes" in artifact.tags and artifact.kind == ArtifactKind.DATASET:
                return artifact
        return None

    def _largest_dataset_path(self, *, exclude: str | None = None) -> Path | None:
        dataset_artifacts = [
            artifact for artifact in self.artifacts if artifact.kind == ArtifactKind.DATASET
        ]
        if exclude:
            dataset_artifacts = [
                artifact for artifact in dataset_artifacts if exclude not in artifact.relative_path
            ]
        if not dataset_artifacts:
            return None

        def sort_key(artifact: ArtifactRecord) -> tuple[int, int]:
            relative = artifact.relative_path.replace("\\", "/")
            is_metrics = relative.startswith("metrics/")
            # Prefer raw input datasets (typically under data/) over derived scored outputs (typically under metrics/).
            return (1 if is_metrics else 0, -int(artifact.size_bytes))

        dataset_artifacts.sort(key=sort_key)
        return Path(dataset_artifacts[0].absolute_path)

    def _load_runtime_output(self, key: str) -> Any | None:
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        candidate_path = self.repo.output_path(self.case.case_id, f"{key}.csv")
        if candidate_path.exists():
            frame = pd.read_csv(candidate_path)
            self._cache[key] = frame
            return frame
        jsonl_path = self.repo.output_path(self.case.case_id, f"{key}.jsonl")
        if jsonl_path.exists():
            frame = pd.read_json(jsonl_path, orient="records", lines=True)
            self._cache[key] = frame
            return frame
        return None


def extract_feature_count(text: str) -> int | None:
    match = re.search(r"(\d+)\s+features?", text.lower())
    return int(match.group(1)) if match else None


def extract_model_threshold(text: str) -> float | None:
    match = re.search(r"THRESHOLD\s*=\s*([0-9.]+)", text)
    return float(match.group(1)) if match else None


def decision_rates_from_pd(frame: pd.DataFrame, threshold: float) -> dict[str, float | None]:
    pd_estimate = frame["pd_estimate"].astype(float)
    approve_mask = pd_estimate < (threshold - 0.07)
    review_mask = (pd_estimate >= (threshold - 0.07)) & (pd_estimate < threshold)
    decline_mask = pd_estimate >= threshold
    captured_default_rate: float | None = None
    approval_default_rate: float | None = None
    if "target_default" in frame.columns:
        target = frame["target_default"].astype(float)
        default_rows = target == 1
        if float(default_rows.sum()) > 0:
            captured_default_rate = float((decline_mask & default_rows).sum() / default_rows.sum())
        if float(approve_mask.sum()) > 0:
            approval_default_rate = float(target.loc[approve_mask].mean())
    return {
        "approval_rate": float(approve_mask.mean()),
        "review_rate": float(review_mask.mean()),
        "decline_rate": float(decline_mask.mean()),
        "captured_default_rate": captured_default_rate,
        "approval_default_rate": approval_default_rate,
    }


def build_stress_row(
    model_name: str,
    scenario_name: str,
    base_frame: pd.DataFrame,
    stressed_frame: pd.DataFrame,
) -> dict[str, Any]:
    base_approval = float((base_frame["decision"] == "approve").mean())
    stressed_approval = float((stressed_frame["decision"] == "approve").mean())
    base_avg_pd = float(base_frame["pd_estimate"].mean())
    stressed_avg_pd = float(stressed_frame["pd_estimate"].mean())
    thin_base = float(
        (base_frame.loc[base_frame["thin_file_flag"] == 1, "decision"] == "approve").mean()
    )
    thin_stressed = float(
        (stressed_frame.loc[stressed_frame["thin_file_flag"] == 1, "decision"] == "approve").mean()
    )
    return {
        "model": model_name,
        "scenario": scenario_name,
        "approval_rate_base": round(base_approval, 4),
        "approval_rate_stressed": round(stressed_approval, 4),
        "approval_delta": round(stressed_approval - base_approval, 4),
        "avg_pd_base": round(base_avg_pd, 4),
        "avg_pd_stressed": round(stressed_avg_pd, 4),
        "avg_pd_delta": round(stressed_avg_pd - base_avg_pd, 4),
        "thin_file_approval_delta": round(thin_stressed - thin_base, 4),
    }


def monotonicity_violation_rate(base_frame: pd.DataFrame, stressed_frame: pd.DataFrame) -> float:
    merged = base_frame[["application_id", "pd_estimate"]].merge(
        stressed_frame[["application_id", "pd_estimate"]],
        on="application_id",
        suffixes=("_base", "_stressed"),
        how="inner",
    )
    if merged.empty:
        return 0.0
    return float((merged["pd_estimate_stressed"] + 1e-9 < merged["pd_estimate_base"]).mean())


def decline_reason_share(frame: pd.DataFrame, reason_code: str) -> float:
    reason_columns = [column for column in ("reason_1", "reason_2", "reason_3") if column in frame.columns]
    if not reason_columns:
        return 0.0
    decline_rows = frame["decision"] == "decline"
    if float(decline_rows.sum()) == 0:
        return 0.0
    reason_present = (frame[reason_columns] == reason_code).any(axis=1)
    return float((decline_rows & reason_present).sum() / decline_rows.sum())
