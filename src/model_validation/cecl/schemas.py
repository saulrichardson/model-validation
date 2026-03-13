"""Typed specs and outputs for the contained CECL demo layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScenarioQuarter(BaseModel):
    quarter: str
    unemployment_rate: float
    gdp_growth: float
    house_price_growth: float
    cre_price_growth: float
    prime_rate: float


class SegmentSpec(BaseModel):
    segment_id: str
    display_name: str
    mix_weight: float
    balance_range: tuple[float, float]
    fico_range: tuple[int, int]
    ltv_range: tuple[float, float]
    dti_range: tuple[float, float]
    dscr_range: tuple[float, float]
    utilization_range: tuple[float, float]
    payment_shock_range: tuple[float, float]
    remaining_term_range: tuple[int, int]
    risk_rating_range: tuple[int, int]
    base_intercept: float
    lgd_base: float
    macro_sensitivities: dict[str, float]


class FullReviewSpec(BaseModel):
    workflow: Literal["full_review"] = "full_review"
    case_slug: str
    bank_name: str
    portfolio_name: str
    product_context: str
    sample_size: int
    rng_seed: int
    documented_forecast_quarters: int
    documented_reversion_quarters: int
    implemented_forecast_quarters: int
    implemented_reversion_quarters: int
    segments: list[SegmentSpec]
    baseline_scenario: list[ScenarioQuarter]
    adverse_scenario: list[ScenarioQuarter]
    severe_scenario: list[ScenarioQuarter]
    overlay_bps_by_scenario: dict[str, dict[str, float]]
    documented_overlay_cap_bps: float
    quantitative_anomaly_segment: str
    quantitative_anomaly_description: str
    expected_findings: list[str] = Field(default_factory=list)


class GapAssessmentSpec(BaseModel):
    workflow: Literal["gap_assessment"] = "gap_assessment"
    case_slug: str
    bank_name: str
    portfolio_name: str
    product_context: str
    documented_forecast_quarters: int
    documented_reversion_quarters: int
    model_card_forecast_quarters: int
    model_card_reversion_quarters: int
    documented_segments: list[str]
    output_segments: list[str]
    baseline_scenario: list[ScenarioQuarter]
    adverse_scenario: list[ScenarioQuarter]
    severe_scenario: list[ScenarioQuarter]
    documented_overlay_cap_bps: float
    provided_overlay_bps_by_segment: dict[str, float]
    expected_findings: list[str] = Field(default_factory=list)


class FullReviewDocumentSet(BaseModel):
    methodology_md: str
    model_overview_md: str
    scenario_assumptions_md: str
    overlay_memo_md: str
    prior_review_note_md: str
    governance_minutes_md: str
    control_process_note_md: str


class GapAssessmentDocumentSet(BaseModel):
    methodology_md: str
    model_overview_md: str
    scenario_assumptions_md: str
    overlay_memo_md: str
    prior_review_note_md: str
    governance_minutes_md: str
    evidence_request_log_md: str
    gap_tracker_md: str


class BuiltCaseArtifacts(BaseModel):
    case_slug: str
    workflow: Literal["full_review", "gap_assessment"]
    input_package_dir: str
    stakeholder_dir: str
    support_dir: str
    stakeholder_artifacts: list[str] = Field(default_factory=list)
    support_artifacts: list[str] = Field(default_factory=list)
