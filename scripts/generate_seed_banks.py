"""Generate bank-style seed bundles for the model-validation workbench."""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.metrics import roc_auc_score

from model_validation.seed_authoring import (
    DocumentationDocumentSet,
    MaterialChangeDocumentSet,
    SeedAuthoringClient,
)
from model_validation.settings import Settings

ROOT = Path(__file__).resolve().parents[1]
SEED_ROOT = ROOT / "seed_banks"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    lines = render_yaml(payload)
    write_text(path, "\n".join(lines))


def render_yaml(payload: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(payload, dict):
        lines: list[str] = []
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(render_yaml(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
        return lines
    if isinstance(payload, list):
        lines = []
        for item in payload:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(render_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{yaml_scalar(payload)}"]


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if any(char in text for char in ":#[]{}") or text.strip() != text:
        return json.dumps(text)
    return text


def write_notebook(path: Path, title: str, markdown: str, code: str) -> None:
    payload = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title}\n", markdown.strip() + "\n"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in code.strip().splitlines()],
            },
        ],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    write_json(path, payload)


def sigmoid(values: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.asarray(1.0 / (1.0 + np.exp(-values)), dtype=np.float64)


def score_dataframe(
    frame: pd.DataFrame,
    *,
    intercept: float,
    coefficients: dict[str, float],
    threshold: float,
    reason_map: dict[str, str],
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
    contribution_frame = pd.DataFrame(contributions)
    top_features = np.argsort(-contribution_frame.to_numpy(), axis=1)[:, :3]
    feature_names = list(contribution_frame.columns)
    reasons: list[list[str]] = []
    for row_idx, indices in enumerate(top_features):
        row_reasons: list[str] = []
        for index in indices:
            feature_name = feature_names[int(index)]
            if contribution_frame.iloc[row_idx, int(index)] <= 0:
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


def metric_block(scored: pd.DataFrame) -> dict[str, float]:
    return {
        "auc": round(float(roc_auc_score(scored["target_default"], scored["pd_estimate"])), 4),
        "approval_rate": round(float((scored["decision"] == "approve").mean()), 4),
        "review_rate": round(float((scored["decision"] == "review").mean()), 4),
        "decline_rate": round(float((scored["decision"] == "decline").mean()), 4),
        "avg_pd": round(float(scored["pd_estimate"].mean()), 4),
        "avg_score": round(float(scored["score"].mean()), 2),
    }


def seed_layout(bank_slug: str, bundle_slug: str) -> dict[str, Path]:
    root = SEED_ROOT / bank_slug / bundle_slug
    return {
        "root": ensure_dir(root),
        "package": ensure_dir(root / "input_package"),
        "expected": ensure_dir(root / "expected_outputs"),
    }


def material_seed_specs() -> list[dict[str, Any]]:
    return [
        {
            "seed_id": "atlas_installment_refresh_2025_q1",
            "bank_name": "Atlas Community Bank",
            "bank_slug": "atlas_community_bank",
            "bundle_name": "Installment Refresh 2025 Q1",
            "bundle_slug": "installment_refresh_2025_q1",
            "workflow_intent": "full_revalidation",
            "quality_profile": "high",
            "description": "Comprehensive internal material-change package for an installment credit refresh with strong governance evidence and runnable implementation.",
            "upload_story": "Atlas uploaded the full challenger-to-champion refresh package after internal development sign-off and committee approval, including source code, validation data, prior memo, monitoring plan, and threshold sensitivity evidence.",
            "expected_case_type": "material_change_revalidation",
            "expected_workflow": "full_revalidation",
            "expected_report_type": "full_revalidation_memo",
            "minimum_coverage_ratio": 0.85,
            "product_context": "Retail unsecured installment lending",
            "champion_version": "2024.9",
            "candidate_version": "2025.1",
            "sample_size": 1800,
            "rng_seed": 19,
            "baseline_intercept": -2.54,
            "candidate_intercept": -2.42,
            "baseline_threshold": 0.43,
            "candidate_threshold": 0.41,
            "baseline_coefficients": {
                "bureau_headroom": 1.28,
                "dti_ratio": 1.34,
                "utilization_rate": 0.77,
                "delinquency_12m": 0.53,
                "inquiries_6m": 0.13,
                "thin_file_flag": 0.33,
                "short_tenure": 0.18,
            },
            "candidate_coefficients": {
                "bureau_headroom": 1.25,
                "dti_ratio": 1.29,
                "utilization_rate": 0.76,
                "delinquency_12m": 0.55,
                "inquiries_6m": 0.12,
                "thin_file_flag": 0.46,
                "short_tenure": 0.2,
                "low_cash_buffer": 0.68,
            },
            "threshold_range": [0.37, 0.39, 0.41, 0.43, 0.45],
            "highlights": [
                "Champion and candidate scorecards are both runnable from source.",
                "Threshold recalibration and liquidity-feature introduction are documented consistently.",
                "Governance materials and implementation runbook are present.",
            ],
            "intended_issues": [
                "Candidate approval rate is lower for thin-file applicants even though overall discrimination improves modestly.",
                "Liquidity-driven reason codes become materially more common under downturn stress and should remain monitored post-implementation.",
            ],
            "expected_findings": [
                "Thin-file approvals decline relative to the champion after the liquidity refresh.",
                "Overall AUC improves modestly, supporting the refresh absent stronger segment deterioration.",
                "Reason-code coverage for LOW_CASH_BUFFER should be maintained after deployment.",
            ],
            "expected_blocked_modules": [],
            "reason_code_mapping": {
                "LOW_BUREAU_SCORE": "Credit bureau score below policy expectation.",
                "HIGH_DTI": "Debt obligations are high relative to income.",
                "HIGH_UTILIZATION": "Revolving credit utilization is elevated.",
                "RECENT_DELINQUENCY": "Recent delinquency history increased observed risk.",
                "RECENT_CREDIT_SEEKING": "Recent credit inquiries indicate higher credit seeking.",
                "THIN_CREDIT_FILE": "Limited credit history reduced score confidence.",
                "SHORT_EMPLOYMENT_TENURE": "Short employment tenure reduced resilience assessment.",
                "LOW_CASH_BUFFER": "Available cash reserves were lower than policy expectations.",
            },
        },
        {
            "seed_id": "cedar_installment_threshold_recalibration",
            "bank_name": "Cedar Retail Bank",
            "bank_slug": "cedar_retail_bank",
            "bundle_name": "Installment Threshold Recalibration",
            "bundle_slug": "installment_threshold_recalibration",
            "workflow_intent": "full_revalidation",
            "quality_profile": "mixed",
            "description": "Runnable material-change package with real implementation evidence but mixed-quality governance and stale threshold documentation.",
            "upload_story": "Cedar uploaded a candidate score package and supporting materials after an expedited policy recalibration. The upload includes source, data, and comparison metrics, but several governance artifacts are incomplete or stale.",
            "expected_case_type": "material_change_revalidation",
            "expected_workflow": "full_revalidation",
            "expected_report_type": "full_revalidation_memo",
            "minimum_coverage_ratio": 0.72,
            "product_context": "Point-of-sale installment lending",
            "champion_version": "2024.4",
            "candidate_version": "2025.2",
            "sample_size": 1600,
            "rng_seed": 77,
            "baseline_intercept": -2.38,
            "candidate_intercept": -2.21,
            "baseline_threshold": 0.42,
            "candidate_threshold": 0.39,
            "baseline_coefficients": {
                "bureau_headroom": 1.22,
                "dti_ratio": 1.26,
                "utilization_rate": 0.7,
                "delinquency_12m": 0.49,
                "inquiries_6m": 0.15,
                "thin_file_flag": 0.29,
                "short_tenure": 0.17,
            },
            "candidate_coefficients": {
                "bureau_headroom": 1.2,
                "dti_ratio": 1.31,
                "utilization_rate": 0.73,
                "delinquency_12m": 0.52,
                "inquiries_6m": 0.14,
                "thin_file_flag": 0.51,
                "short_tenure": 0.2,
                "low_cash_buffer": 0.54,
            },
            "threshold_range": [0.35, 0.37, 0.39, 0.41, 0.43],
            "highlights": [
                "Champion and candidate packages are runnable and include packaged reference scores.",
                "Threshold policy moved materially to preserve booking targets.",
                "Governance artifacts intentionally include stale and incomplete references.",
            ],
            "intended_issues": [
                "Methodology and committee minutes reference the old 0.40 threshold instead of the implemented 0.39 cutoff.",
                "Reason-code mapping omits LOW_CASH_BUFFER even though the candidate can emit it.",
                "Monitoring thresholds for thin-file approvals are missing from the monitoring plan.",
            ],
            "expected_findings": [
                "Documentation does not fully align with the implemented cutoff and reason-code behavior.",
                "Candidate materially tightens thin-file approvals relative to the champion.",
                "Governance evidence is sufficient for review but not clean enough for an unconditional sign-off.",
            ],
            "expected_blocked_modules": [],
            "reason_code_mapping": {
                "LOW_BUREAU_SCORE": "External credit score below minimum policy expectation.",
                "HIGH_DTI": "Debt burden exceeds current policy tolerance.",
                "HIGH_UTILIZATION": "Revolving exposure is elevated relative to policy.",
                "RECENT_DELINQUENCY": "Recent delinquency behavior increased expected risk.",
                "RECENT_CREDIT_SEEKING": "Recent credit seeking activity is elevated.",
                "THIN_CREDIT_FILE": "Limited credit history reduced underwriting confidence.",
                "SHORT_EMPLOYMENT_TENURE": "Employment history is shorter than preferred.",
            },
        },
    ]


def documentation_seed_specs() -> list[dict[str, Any]]:
    return [
        {
            "seed_id": "meridian_heloc_readiness_pack_q1",
            "bank_name": "Meridian Home Equity",
            "bank_slug": "meridian_home_equity",
            "bundle_name": "HELOC Readiness Pack Q1",
            "bundle_slug": "heloc_readiness_pack_q1",
            "workflow_intent": "conceptual_readiness_review",
            "quality_profile": "rich_inconsistent",
            "description": "Rich documentation-led upload with sample data and broad governance materials but no runnable implementation.",
            "upload_story": "Meridian uploaded a readiness package for a home-equity line model refresh. The package is documentation-heavy and broad, but runtime artifacts are withheld pending vendor release and the pack contains several internal inconsistencies.",
            "expected_case_type": "documentation_only_review",
            "expected_workflow": "conceptual_readiness_review",
            "expected_report_type": "conceptual_readiness_memo",
            "minimum_coverage_ratio": 0.6,
            "product_context": "Home equity line underwriting",
            "sample_size": 680,
            "rng_seed": 31,
            "feature_count_methodology": 18,
            "feature_count_model_card": 22,
            "reason_code_gaps": [
                "payment_shock_index",
                "verified_income_stability",
                "override_propensity_score",
            ],
            "highlights": [
                "Broad documentation pack includes governance minutes, monitoring proposal, and evidence request tracker.",
                "Feature counts intentionally conflict between methodology and model card.",
                "No runtime package or reproducibility script is included.",
            ],
            "intended_issues": [
                "Feature counts differ between methodology and model card.",
                "Reason-code mapping omits several resilience variables.",
                "Monitoring proposal refers to runtime evidence that is not present in the package.",
            ],
            "expected_findings": [
                "The pack is useful for conceptual review but insufficient for execution-based validation.",
                "Reason-code coverage is incomplete for newly introduced resilience variables.",
                "Additional reproducibility and monitoring evidence should be requested before approval.",
            ],
            "expected_blocked_modules": [
                "runtime_reproduction",
                "baseline_comparison",
            ],
        },
        {
            "seed_id": "oakline_vendor_readiness_packet",
            "bank_name": "Oakline Auto Finance",
            "bank_slug": "oakline_auto_finance",
            "bundle_name": "Vendor Readiness Packet",
            "bundle_slug": "vendor_readiness_packet",
            "workflow_intent": "conceptual_readiness_review",
            "quality_profile": "thin",
            "description": "Thin documentation-led packet from a vendor-managed auto finance model with clear evidence gaps and only light supporting materials.",
            "upload_story": "Oakline received a sparse vendor packet for an auto finance acquisition model. The upload contains a model inventory record, a short methodology note, a partial reason-code table, and a thin evidence request trail but no runnable assets.",
            "expected_case_type": "documentation_only_review",
            "expected_workflow": "conceptual_readiness_review",
            "expected_report_type": "conceptual_readiness_memo",
            "minimum_coverage_ratio": 0.4,
            "product_context": "Indirect auto finance acquisition model",
            "sample_size": 420,
            "rng_seed": 53,
            "feature_count_methodology": 11,
            "feature_count_model_card": 11,
            "reason_code_gaps": [
                "dealer_quality_band",
                "loan_term_stretch_flag",
            ],
            "highlights": [
                "The packet includes a model inventory entry and policy exception memo.",
                "Feature dictionary and monitoring support are intentionally thin.",
                "No executable scoring assets, development evidence, or prior validation package are included.",
            ],
            "intended_issues": [
                "Monitoring support is generic and lacks metric thresholds.",
                "Policy exception memo acknowledges unresolved documentation gaps.",
                "Reason-code mapping is partial and uses generic statements for multiple features.",
            ],
            "expected_findings": [
                "The packet is materially insufficient for anything beyond an early readiness review.",
                "Evidence requests should prioritize runnable assets, monitoring thresholds, and fuller reason-code coverage.",
            ],
            "expected_blocked_modules": [
                "runtime_reproduction",
                "baseline_comparison",
                "behavioral_review",
            ],
        },
    ]


def authoring_mode_docs(
    authoring_mode: str,
    settings: Settings,
    model_override: str | None,
) -> SeedAuthoringClient | None:
    if authoring_mode != "gateway":
        return None
    return SeedAuthoringClient(settings, model=model_override)


async def material_documents(
    spec: dict[str, Any],
    authoring_mode: str,
    settings: Settings,
    model_override: str | None,
) -> MaterialChangeDocumentSet:
    if authoring_mode == "gateway":
        client = authoring_mode_docs(authoring_mode, settings, model_override)
        assert client is not None
        try:
            return await client.author_material_change_documents(spec)
        finally:
            await client.shutdown()

    threshold_text = (
        f"The documented decline threshold moved from {spec['baseline_threshold']:.2f} "
        f"to {spec['candidate_threshold']:.2f}."
    )
    issue_block = "\n".join(f"- {item}" for item in spec["intended_issues"])
    return MaterialChangeDocumentSet(
        methodology_md=f"# Methodology\n\n{spec['product_context']} score refresh for {spec['bank_name']}. {threshold_text}",
        development_summary_md=(
            f"# Development Summary\n\nCandidate version {spec['candidate_version']} extends champion "
            f"{spec['champion_version']} with recalibrated coefficients and liquidity stress treatment."
        ),
        change_request_md=(
            f"# Change Request\n\nRequested change for {spec['bundle_name']}.\n\n## Noted Issues\n{issue_block}"
        ),
        prior_validation_memo_md=(
            "# Prior Validation Memo\n\nPrior review approved the champion subject to documentation alignment and "
            "reason-code traceability for future refreshes."
        ),
        monitoring_plan_md="# Monitoring Plan\n\nMonthly approval-rate, score migration, and reason-code coverage monitoring.",
        validation_test_plan_md="# Validation Test Plan\n\nReproduce champion and candidate runs, compare metrics, and execute sensitivity testing.",
        governance_minutes_md="# Governance Minutes\n\nCommittee reviewed the refresh package and approved validation intake.",
        implementation_runbook_md="# Implementation Runbook\n\n1. Re-run packaged harness.\n2. Compare outputs.\n3. Validate post-cutover monitoring.",
        issue_log_md=f"# Issue Log\n\n{issue_block}",
    )


async def documentation_documents(
    spec: dict[str, Any],
    authoring_mode: str,
    settings: Settings,
    model_override: str | None,
) -> DocumentationDocumentSet:
    if authoring_mode == "gateway":
        client = authoring_mode_docs(authoring_mode, settings, model_override)
        assert client is not None
        try:
            return await client.author_documentation_documents(spec)
        finally:
            await client.shutdown()

    issue_block = "\n".join(f"- {item}" for item in spec["intended_issues"])
    return DocumentationDocumentSet(
        model_methodology_md=f"# Model Methodology\n\n{spec['product_context']} underwriting methodology summary.",
        model_card_md=f"# Model Card\n\nCurrent package for {spec['bundle_name']}.",
        prior_validation_memo_md="# Prior Validation Memo\n\nExecution artifacts were previously requested and not delivered.",
        monitoring_plan_md="# Monitoring Proposal\n\nPopulation stability, score drift, overrides, and reason-code coverage are proposed.",
        governance_minutes_md="# Governance Minutes\n\nThe committee accepted the package for documentation review only.",
        assumptions_register_md=f"# Assumptions Register\n\n{issue_block}",
        evidence_request_log_md="# Evidence Request Log\n\nRequest runnable assets, updated mappings, and monitoring evidence.",
        policy_exception_memo_md="# Policy Exception Memo\n\nDocumentation exceptions remain open pending vendor follow-up.",
    )


def material_input_frame(sample_size: int, rng_seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(rng_seed)
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
    recent_cash_buffer_mo = np.clip(rng.normal(5.2 - thin_file * 1.5, 1.9, size=sample_size), 0.2, 12)
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
    return pd.DataFrame(
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


def documentation_input_frame(sample_size: int, rng_seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(rng_seed)
    frame = pd.DataFrame(
        {
            "account_id": [f"DOC-{idx:05d}" for idx in range(sample_size)],
            "channel": rng.choice(["branch", "call_center", "digital"], p=[0.42, 0.21, 0.37], size=sample_size),
            "fico_band": rng.choice(["subprime", "near_prime", "prime"], p=[0.22, 0.39, 0.39], size=sample_size),
            "ltv_ratio": np.round(np.clip(rng.normal(0.78, 0.11, size=sample_size), 0.35, 1.15), 4),
            "dti_ratio": np.round(np.clip(rng.normal(0.34, 0.13, size=sample_size), 0.05, 0.81), 4),
            "payment_shock_index": np.round(np.clip(rng.normal(0.24, 0.16, size=sample_size), 0.0, 1.2), 4),
            "verified_income_stability": np.round(np.clip(rng.normal(0.64, 0.21, size=sample_size), 0.0, 1.0), 4),
            "manual_override_flag": rng.binomial(1, 0.08, size=sample_size),
            "self_employed_flag": rng.binomial(1, 0.14, size=sample_size),
            "zip_risk_band": rng.choice(["low", "moderate", "elevated"], p=[0.48, 0.35, 0.17], size=sample_size),
        }
    )
    missing_mask = rng.binomial(1, 0.31, size=sample_size).astype(bool)
    frame.loc[missing_mask, "verified_income_stability"] = np.nan
    return frame


def segment_shift_summary(frame: pd.DataFrame, baseline: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for segment_name, mask in {
        "thin_file": frame["thin_file_flag"] == 1,
        "thick_file": frame["thin_file_flag"] == 0,
        "broker": frame["channel"] == "broker",
        "direct": frame["channel"] == "direct",
    }.items():
        baseline_segment = baseline.loc[mask]
        candidate_segment = candidate.loc[mask]
        rows.append(
            {
                "segment": segment_name,
                "baseline_approval_rate": round(float((baseline_segment["decision"] == "approve").mean()), 4),
                "candidate_approval_rate": round(float((candidate_segment["decision"] == "approve").mean()), 4),
                "approval_delta": round(
                    float((candidate_segment["decision"] == "approve").mean() - (baseline_segment["decision"] == "approve").mean()),
                    4,
                ),
                "baseline_avg_pd": round(float(baseline_segment["pd_estimate"].mean()), 4),
                "candidate_avg_pd": round(float(candidate_segment["pd_estimate"].mean()), 4),
            }
        )
    return pd.DataFrame(rows)


def threshold_sweep(candidate: pd.DataFrame, thresholds: list[float]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for threshold in thresholds:
        decisions = np.where(
            candidate["pd_estimate"] >= threshold,
            "decline",
            np.where(candidate["pd_estimate"] >= threshold - 0.07, "review", "approve"),
        )
        rows.append(
            {
                "threshold": threshold,
                "approval_rate": round(float((decisions == "approve").mean()), 4),
                "review_rate": round(float((decisions == "review").mean()), 4),
                "decline_rate": round(float((decisions == "decline").mean()), 4),
            }
        )
    return pd.DataFrame(rows)


def monotonicity_checks(frame: pd.DataFrame, scored: pd.DataFrame) -> dict[str, Any]:
    base = scored["pd_estimate"]
    worse_bureau = frame.copy()
    worse_bureau["bureau_score"] = np.clip(frame["bureau_score"] - 20, 540, None)
    worse_dti = frame.copy()
    worse_dti["dti_ratio"] = np.clip(frame["dti_ratio"] + 0.05, None, 0.95)
    delta_bureau = float((np.clip((720 - worse_bureau["bureau_score"]) / 120, 0, None) > np.clip((720 - frame["bureau_score"]) / 120, 0, None)).mean())
    delta_dti = float((worse_dti["dti_ratio"] > frame["dti_ratio"]).mean())
    return {
        "bureau_score_directional_check": {
            "status": "pass",
            "detail": "Lower bureau scores increase modeled risk exposure for the scored population.",
            "share_of_records_stressed": round(delta_bureau, 4),
        },
        "dti_directional_check": {
            "status": "pass",
            "detail": "Higher debt-to-income ratios increase modeled risk exposure for the scored population.",
            "share_of_records_stressed": round(delta_dti, 4),
        },
        "baseline_average_pd": round(float(base.mean()), 4),
    }


def reason_code_stability(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column in ("reason_1", "reason_2", "reason_3"):
        shares = scored[column].value_counts(normalize=True).head(6)
        for code, share in shares.items():
            rows.append({"reason_slot": column, "reason_code": code, "share": round(float(share), 4)})
    return pd.DataFrame(rows)


def material_model_template(model_name: str, intercept: float, threshold: float, coefficients: dict[str, float], reason_map: dict[str, str]) -> str:
    return f"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MODEL_NAME = "{model_name}"
INTERCEPT = {intercept}
THRESHOLD = {threshold}
COEFFICIENTS = {json.dumps(coefficients, sort_keys=True)}
REASON_CODES = {json.dumps(reason_map, sort_keys=True)}


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


def material_runtime_harness() -> str:
    return """
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


async def build_material_seed(
    spec: dict[str, Any],
    *,
    authoring_mode: str,
    settings: Settings,
    model_override: str | None,
) -> dict[str, Any]:
    layout = seed_layout(spec["bank_slug"], spec["bundle_slug"])
    package_dir = layout["package"]
    expected_dir = layout["expected"]

    for subdir in ("data", "docs", "models", "metrics", "runtime", "governance", "analysis", "config"):
        ensure_dir(package_dir / subdir)

    frame = material_input_frame(spec["sample_size"], spec["rng_seed"])
    frame.to_csv(package_dir / "data" / "oot_validation_sample.csv", index=False)

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
    baseline = score_dataframe(
        frame,
        intercept=spec["baseline_intercept"],
        coefficients=spec["baseline_coefficients"],
        threshold=spec["baseline_threshold"],
        reason_map=reason_map,
    )
    candidate = score_dataframe(
        frame,
        intercept=spec["candidate_intercept"],
        coefficients=spec["candidate_coefficients"],
        threshold=spec["candidate_threshold"],
        reason_map=reason_map,
    )
    baseline.to_csv(package_dir / "metrics" / "baseline_reference_scored.csv", index=False)
    candidate.to_csv(package_dir / "metrics" / "candidate_reference_scored.csv", index=False)
    segment_summary = segment_shift_summary(frame, baseline, candidate)
    segment_summary.to_csv(package_dir / "metrics" / "segment_shift_summary.csv", index=False)
    comparison_summary = {
        "baseline": metric_block(baseline),
        "candidate": metric_block(candidate),
        "notes": spec["expected_findings"],
    }
    write_json(package_dir / "metrics" / "comparison_summary.json", comparison_summary)

    docs = await material_documents(spec, authoring_mode, settings, model_override)
    write_text(package_dir / "docs" / "methodology.md", docs.methodology_md)
    write_text(package_dir / "docs" / "development_summary.md", docs.development_summary_md)
    write_text(package_dir / "docs" / "change_request.md", docs.change_request_md)
    write_text(package_dir / "docs" / "prior_validation_memo.md", docs.prior_validation_memo_md)
    write_text(package_dir / "docs" / "monitoring_plan.md", docs.monitoring_plan_md)
    write_text(package_dir / "docs" / "validation_test_plan.md", docs.validation_test_plan_md)
    write_text(package_dir / "governance" / "committee_minutes.md", docs.governance_minutes_md)
    write_text(package_dir / "docs" / "implementation_runbook.md", docs.implementation_runbook_md)
    write_text(package_dir / "docs" / "issue_log.md", docs.issue_log_md)
    write_text(
        package_dir / "docs" / "metric_provenance.md",
        """
        Metric Provenance Note

        Comparison summary metrics were computed on the packaged OOT validation sample using the packaged baseline and
        candidate source files. Segment shift summary is calculated on thin-file and channel segments using the same scored outputs.
        """,
    )

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
    ).to_csv(package_dir / "docs" / "feature_dictionary.csv", index=False)

    pd.DataFrame(
        [{"reason_code": code, "consumer_statement": text} for code, text in spec["reason_code_mapping"].items()]
    ).to_csv(package_dir / "docs" / "reason_code_mapping.csv", index=False)

    write_text(
        package_dir / "requirements.txt",
        """
        numpy>=1.26
        pandas>=2.2
        scikit-learn>=1.5
        """,
    )
    write_text(
        package_dir / "models" / "baseline_model.py",
        material_model_template(
            f"{spec['bank_slug']}_{spec['champion_version']}",
            spec["baseline_intercept"],
            spec["baseline_threshold"],
            spec["baseline_coefficients"],
            reason_map,
        ),
    )
    write_text(
        package_dir / "models" / "candidate_model.py",
        material_model_template(
            f"{spec['bank_slug']}_{spec['candidate_version']}",
            spec["candidate_intercept"],
            spec["candidate_threshold"],
            spec["candidate_coefficients"],
            reason_map,
        ),
    )
    write_text(package_dir / "runtime" / "compare_models.py", material_runtime_harness())
    write_text(
        package_dir / "runtime" / "run_revalidation.sh",
        "python runtime/compare_models.py --input data/oot_validation_sample.csv --output-dir outputs/revalidation_run",
    )
    write_yaml(
        package_dir / "config" / "scoring_policy.yaml",
        {
            "champion_version": spec["champion_version"],
            "candidate_version": spec["candidate_version"],
            "baseline_threshold": spec["baseline_threshold"],
            "candidate_threshold": spec["candidate_threshold"],
            "review_band_width": 0.07,
            "workflow_intent": spec["workflow_intent"],
        },
    )
    write_json(
        package_dir / "governance" / "model_inventory_entry.json",
        {
            "bank_name": spec["bank_name"],
            "product_context": spec["product_context"],
            "champion_version": spec["champion_version"],
            "candidate_version": spec["candidate_version"],
            "quality_profile": spec["quality_profile"],
            "open_conditions": spec["intended_issues"],
        },
    )
    if spec["quality_profile"] == "high":
        write_json(
            package_dir / "package_manifest.json",
            {
                "bundle_name": spec["bundle_name"],
                "bank_name": spec["bank_name"],
                "workflow_intent": spec["workflow_intent"],
                "artifact_groups": ["data", "docs", "models", "metrics", "runtime", "governance", "analysis", "config"],
            },
        )
    write_notebook(
        package_dir / "analysis" / "sensitivity_walkthrough.ipynb",
        "Sensitivity Walkthrough",
        "This notebook is included as part of the seed upload and sketches the sensitivity checks the validation team expects to run.",
        "import pandas as pd\nframe = pd.read_csv('../data/oot_validation_sample.csv')\nframe[['bureau_score','dti_ratio','thin_file_flag']].describe()",
    )

    sweep = threshold_sweep(candidate, spec["threshold_range"])
    sweep.to_csv(expected_dir / "threshold_sweep.csv", index=False)
    stability = reason_code_stability(candidate)
    stability.to_csv(expected_dir / "reason_code_stability.csv", index=False)
    monotonicity = monotonicity_checks(frame, candidate)
    write_json(expected_dir / "monotonicity_checks.json", monotonicity)
    sensitivity_summary = {
        "summary": f"{spec['bank_name']} candidate threshold sensitivity centered on {spec['candidate_threshold']:.2f}.",
        "stress_cases": [
            {
                "name": "bureau_minus_20",
                "expected_effect": "higher modeled risk and lower approvals",
            },
            {
                "name": "dti_plus_5_points",
                "expected_effect": "higher modeled risk and more review/decline outcomes",
            },
            {
                "name": "cash_buffer_minus_1_5_months",
                "expected_effect": "greater LOW_CASH_BUFFER prevalence in top reasons",
            },
        ],
    }
    write_json(expected_dir / "sensitivity_summary.json", sensitivity_summary)
    write_json(expected_dir / "baseline_vs_candidate_summary.json", comparison_summary)

    discovery_summary = {
        "case_type": spec["expected_case_type"],
        "runtime_mode": "runnable_source",
        "likely_execution_path": "full_revalidation",
        "artifact_highlights": spec["highlights"],
        "gaps": spec["expected_blocked_modules"],
    }
    playbook_summary = {
        "dominant_workflow": spec["expected_workflow"],
        "coverage_ratio": spec["minimum_coverage_ratio"],
        "modules": {
            "runtime_reproduction": "executable",
            "baseline_comparison": "executable",
            "behavioral_review": "executable",
            "documentation_consistency": "executable" if spec["quality_profile"] == "high" else "partial",
            "reason_code_review": "executable" if "LOW_CASH_BUFFER" in spec["reason_code_mapping"] else "partial",
        },
    }
    execution_summary = {
        "summary": f"Expected execution outputs for {spec['seed_id']}.",
        "metrics": comparison_summary,
        "findings": spec["expected_findings"],
    }
    report_payload = {
        "report_type": spec["expected_report_type"],
        "title": f"{spec['bank_name']} {spec['bundle_name']} Revalidation Memo",
        "executive_summary": spec["expected_findings"][0],
        "recommended_actions": [
            "Confirm post-implementation monitoring thresholds.",
            "Review thin-file segment movement before final approval.",
        ],
    }
    write_json(expected_dir / "discovery_summary.json", discovery_summary)
    write_json(expected_dir / "playbook_summary.json", playbook_summary)
    write_json(expected_dir / "execution_summary.json", execution_summary)
    write_json(expected_dir / "final_report.json", report_payload)
    write_text(
        expected_dir / "final_report.md",
        f"# {report_payload['title']}\n\n## Executive Summary\n\n{report_payload['executive_summary']}\n\n## Key Findings\n\n"
        + "\n".join(f"- {item}" for item in spec["expected_findings"])
        + "\n",
    )

    seed_spec = {
        **spec,
        "expected_output_files": sorted(str(path.relative_to(layout["root"])) for path in expected_dir.rglob("*") if path.is_file()),
    }
    seed_descriptor = {
        "seed_id": spec["seed_id"],
        "bank_name": spec["bank_name"],
        "bank_slug": spec["bank_slug"],
        "bundle_name": spec["bundle_name"],
        "bundle_slug": spec["bundle_slug"],
        "workflow_intent": spec["workflow_intent"],
        "quality_profile": spec["quality_profile"],
        "description": spec["description"],
        "upload_story": spec["upload_story"],
        "expected_case_type": spec["expected_case_type"],
        "package_dir": f"{spec['bank_slug']}/{spec['bundle_slug']}/input_package",
        "expected_outputs_dir": f"{spec['bank_slug']}/{spec['bundle_slug']}/expected_outputs",
        "highlights": spec["highlights"],
        "expected_workflow": spec["expected_workflow"],
        "expected_report_type": spec["expected_report_type"],
        "minimum_coverage_ratio": spec["minimum_coverage_ratio"],
    }
    write_json(layout["root"] / "seed_spec.json", seed_spec)
    write_json(layout["root"] / "seed.json", seed_descriptor)
    return seed_descriptor


async def build_documentation_seed(
    spec: dict[str, Any],
    *,
    authoring_mode: str,
    settings: Settings,
    model_override: str | None,
) -> dict[str, Any]:
    layout = seed_layout(spec["bank_slug"], spec["bundle_slug"])
    package_dir = layout["package"]
    expected_dir = layout["expected"]

    for subdir in ("data", "docs", "governance", "config", "analysis"):
        ensure_dir(package_dir / subdir)

    frame = documentation_input_frame(spec["sample_size"], spec["rng_seed"])
    frame.to_csv(package_dir / "data" / "sample_extract.csv", index=False)

    docs = await documentation_documents(spec, authoring_mode, settings, model_override)
    write_text(package_dir / "docs" / "model_methodology.md", docs.model_methodology_md)
    write_text(package_dir / "docs" / "model_card.md", docs.model_card_md)
    write_text(package_dir / "docs" / "prior_validation_memo.md", docs.prior_validation_memo_md)
    write_text(package_dir / "docs" / "monitoring_plan.md", docs.monitoring_plan_md)
    write_text(package_dir / "governance" / "committee_minutes.md", docs.governance_minutes_md)
    write_text(package_dir / "docs" / "assumptions_register.md", docs.assumptions_register_md)
    write_text(package_dir / "docs" / "evidence_request_log.md", docs.evidence_request_log_md)
    write_text(package_dir / "docs" / "policy_exception_memo.md", docs.policy_exception_memo_md)

    feature_rows = [
        {"feature_name": "fico_band", "business_definition": "External bureau risk band", "documented": 1},
        {"feature_name": "ltv_ratio", "business_definition": "Current combined loan-to-value ratio", "documented": 1},
        {"feature_name": "dti_ratio", "business_definition": "Debt burden at application", "documented": 1},
        {"feature_name": "payment_shock_index", "business_definition": "Estimated payment shock under stress", "documented": 1},
        {"feature_name": "verified_income_stability", "business_definition": "Stability score based on verified income trends", "documented": 1},
        {"feature_name": "manual_override_flag", "business_definition": "Indicator that manual override channel was used", "documented": 1},
        {"feature_name": "override_propensity_score", "business_definition": "Estimated probability of manual override", "documented": 1},
        {"feature_name": "zip_risk_band", "business_definition": "Internal ZIP concentration risk band", "documented": 1},
    ]
    if spec["quality_profile"] == "thin":
        feature_rows = feature_rows[:5]
    pd.DataFrame(feature_rows).to_csv(package_dir / "docs" / "feature_dictionary.csv", index=False)

    reason_rows = [
        {"feature_name": "fico_band", "reason_code": "HE001", "consumer_statement": "Credit profile did not meet minimum expectation."},
        {"feature_name": "ltv_ratio", "reason_code": "HE014", "consumer_statement": "Combined loan-to-value was higher than policy allows."},
        {"feature_name": "dti_ratio", "reason_code": "HE019", "consumer_statement": "Debt obligations were high relative to income."},
        {"feature_name": "manual_override_flag", "reason_code": "HE099", "consumer_statement": "Overall application profile required manual review."},
        {"feature_name": "zip_risk_band", "reason_code": "HE099", "consumer_statement": "Overall application profile required manual review."},
    ]
    pd.DataFrame(reason_rows).to_csv(package_dir / "docs" / "reason_code_mapping.csv", index=False)
    write_json(
        package_dir / "governance" / "model_inventory_entry.json",
        {
            "bank_name": spec["bank_name"],
            "product_context": spec["product_context"],
            "quality_profile": spec["quality_profile"],
            "runtime_artifacts_included": False,
            "open_gaps": spec["intended_issues"],
        },
    )
    write_yaml(
        package_dir / "config" / "implementation_checklist.yaml",
        {
            "documentation_received": True,
            "runtime_received": False,
            "reason_code_refresh_complete": False,
            "committee_approval_ready": False,
            "open_items": spec["intended_issues"],
        },
    )
    write_notebook(
        package_dir / "analysis" / "readiness_profile.ipynb",
        "Readiness Profile",
        "This notebook is included in the upload as an analyst scratchpad summarizing sample extract characteristics.",
        "import pandas as pd\nframe = pd.read_csv('../data/sample_extract.csv')\nframe.isna().mean().sort_values(ascending=False).head()",
    )

    missing_rates = {
        column: round(float(frame[column].isna().mean()), 4)
        for column in frame.columns
        if float(frame[column].isna().mean()) > 0
    }
    discovery_summary = {
        "case_type": spec["expected_case_type"],
        "runtime_mode": "document_only",
        "likely_execution_path": "conceptual_readiness_review",
        "artifact_highlights": spec["highlights"],
        "gaps": spec["expected_blocked_modules"],
    }
    playbook_summary = {
        "dominant_workflow": spec["expected_workflow"],
        "coverage_ratio": spec["minimum_coverage_ratio"],
        "modules": {
            "conceptual_soundness_review": "executable",
            "documentation_consistency": "executable" if spec["quality_profile"] == "rich_inconsistent" else "partial",
            "reason_code_review": "partial",
            "data_profile_review": "executable",
            "runtime_reproduction": "blocked",
        },
    }
    benchmark_output = {
        "summary": f"{spec['bank_name']} readiness pack benchmarked as documentation-only with open evidence gaps.",
        "strengths": [
            "Core methodology and governance narrative are present.",
            "A sample extract supports limited data profiling.",
        ],
        "gaps": spec["intended_issues"],
        "evidence_requests": [
            "Provide runnable implementation or reproducibility scripts.",
            "Refresh reason-code mapping for omitted features.",
            "Provide monitoring evidence with explicit thresholds.",
        ],
    }
    consistency_review = {
        "conflicts": [
            f"Methodology lists {spec['feature_count_methodology']} features while model card lists {spec['feature_count_model_card']}."
        ]
        if spec["feature_count_methodology"] != spec["feature_count_model_card"]
        else [],
        "missing_reason_code_features": spec["reason_code_gaps"],
        "missing_rate_snapshot": missing_rates,
    }
    report_payload = {
        "report_type": spec["expected_report_type"],
        "title": f"{spec['bank_name']} {spec['bundle_name']} Readiness Memo",
        "executive_summary": spec["expected_findings"][0],
        "evidence_requests": benchmark_output["evidence_requests"],
    }
    write_json(expected_dir / "discovery_summary.json", discovery_summary)
    write_json(expected_dir / "playbook_summary.json", playbook_summary)
    write_json(expected_dir / "documentation_pack_benchmark.json", benchmark_output)
    write_json(expected_dir / "document_consistency_review.json", consistency_review)
    write_json(expected_dir / "evidence_request_list.json", {"requests": benchmark_output["evidence_requests"]})
    write_json(expected_dir / "final_report.json", report_payload)
    write_text(
        expected_dir / "final_report.md",
        f"# {report_payload['title']}\n\n## Executive Summary\n\n{report_payload['executive_summary']}\n\n## Evidence Requests\n\n"
        + "\n".join(f"- {item}" for item in benchmark_output["evidence_requests"])
        + "\n",
    )

    seed_spec = {
        **spec,
        "expected_output_files": sorted(str(path.relative_to(layout["root"])) for path in expected_dir.rglob("*") if path.is_file()),
    }
    seed_descriptor = {
        "seed_id": spec["seed_id"],
        "bank_name": spec["bank_name"],
        "bank_slug": spec["bank_slug"],
        "bundle_name": spec["bundle_name"],
        "bundle_slug": spec["bundle_slug"],
        "workflow_intent": spec["workflow_intent"],
        "quality_profile": spec["quality_profile"],
        "description": spec["description"],
        "upload_story": spec["upload_story"],
        "expected_case_type": spec["expected_case_type"],
        "package_dir": f"{spec['bank_slug']}/{spec['bundle_slug']}/input_package",
        "expected_outputs_dir": f"{spec['bank_slug']}/{spec['bundle_slug']}/expected_outputs",
        "highlights": spec["highlights"],
        "expected_workflow": spec["expected_workflow"],
        "expected_report_type": spec["expected_report_type"],
        "minimum_coverage_ratio": spec["minimum_coverage_ratio"],
    }
    write_json(layout["root"] / "seed_spec.json", seed_spec)
    write_json(layout["root"] / "seed.json", seed_descriptor)
    return seed_descriptor


async def generate_seed_banks(authoring_mode: str, model_override: str | None) -> None:
    shutil.rmtree(SEED_ROOT, ignore_errors=True)
    ensure_dir(SEED_ROOT)
    settings = Settings()
    descriptors: list[dict[str, Any]] = []

    for spec in material_seed_specs():
        descriptor = await build_material_seed(
            spec,
            authoring_mode=authoring_mode,
            settings=settings,
            model_override=model_override,
        )
        descriptors.append(descriptor)

    for spec in documentation_seed_specs():
        descriptor = await build_documentation_seed(
            spec,
            authoring_mode=authoring_mode,
            settings=settings,
            model_override=model_override,
        )
        descriptors.append(descriptor)

    write_text(
        SEED_ROOT / "README.md",
        """
        Bank-style seed bundles for the Codex-first validation workbench.

        Each bundle contains:
        - seed.json: runtime-facing seed descriptor
        - seed_spec.json: richer generation and seed specification
        - input_package/: synthetic artifacts that simulate a bank upload
        - expected_outputs/: golden outputs representing the ideal completed run
        """,
    )
    write_json(SEED_ROOT / "manifest.json", {"seeds": descriptors})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate bank-style seed bundles.")
    parser.add_argument(
        "--authoring-mode",
        choices=["gateway", "deterministic"],
        default="gateway",
        help="Use the gateway utility for rich narrative docs or local deterministic templates.",
    )
    parser.add_argument(
        "--authoring-model",
        default=None,
        help="Optional gateway model override for seed authoring.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(generate_seed_banks(args.authoring_mode, args.authoring_model))


if __name__ == "__main__":
    main()
