"""Build the contained CECL demo artifact pack."""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, Literal, cast

import pandas as pd

from ..settings import Settings, get_settings
from .analysis import (
    build_data_dictionary,
    build_evidence_ledger,
    build_full_review_inventory,
    build_gap_inventory,
    generate_gap_assessment_provided_outputs,
    generate_portfolio,
    nested_json_safe,
    quarter_frame,
    run_full_review_analysis,
    run_gap_assessment_analysis,
    write_csv,
)
from .authoring import CeclAuthoringClient
from .render import (
    compile_latex,
    render_codex_trace,
    render_coverage_statement,
    render_discovery_summary,
    render_document_crosscheck,
    render_full_review_latex,
    render_gap_assessment_latex,
    render_review_plan,
)
from .schemas import (
    BuiltCaseArtifacts,
    FullReviewDocumentSet,
    FullReviewSpec,
    GapAssessmentDocumentSet,
    GapAssessmentSpec,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CECL_DEMO_ROOT = PROJECT_ROOT / "cecl_demo"
SPECS_DIR = CECL_DEMO_ROOT / "specs"
CASES_DIR = CECL_DEMO_ROOT / "cases"


def build_cecl_demo_artifacts(
    *,
    case: Literal["full_review", "gap_assessment", "all"] = "all",
    authoring_mode: Literal["gateway", "local"] = "gateway",
    compile_pdf: bool = True,
    settings: Settings | None = None,
) -> list[BuiltCaseArtifacts]:
    settings = settings or get_settings()
    cases: list[BuiltCaseArtifacts] = []

    if case in {"full_review", "all"}:
        full_spec = FullReviewSpec.model_validate_json((SPECS_DIR / "full_review.json").read_text())
        cases.append(
            _build_full_review_case(
                full_spec,
                settings=settings,
                authoring_mode=authoring_mode,
                compile_pdf=compile_pdf,
            )
        )

    if case in {"gap_assessment", "all"}:
        gap_spec = GapAssessmentSpec.model_validate_json((SPECS_DIR / "gap_assessment.json").read_text())
        cases.append(
            _build_gap_assessment_case(
                gap_spec,
                settings=settings,
                authoring_mode=authoring_mode,
                compile_pdf=compile_pdf,
            )
        )

    return cases


def _build_full_review_case(
    spec: FullReviewSpec,
    *,
    settings: Settings,
    authoring_mode: Literal["gateway", "local"],
    compile_pdf: bool,
) -> BuiltCaseArtifacts:
    case_dir = _reset_case_dir(spec.case_slug)
    input_dir = case_dir / "input_package"
    stakeholder_dir = case_dir / "outputs" / "stakeholder"
    support_dir = case_dir / "outputs" / "support"

    for path in [
        input_dir / "model",
        input_dir / "data",
        input_dir / "docs",
        input_dir / "outputs",
        input_dir / "scenarios",
        stakeholder_dir,
        support_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    documents = _author_full_review_documents(spec, settings=settings, authoring_mode=authoring_mode)
    portfolio = generate_portfolio(spec)
    analysis = run_full_review_analysis(spec, portfolio)

    write_csv(input_dir / "data" / "loan_level_snapshot.csv", portfolio)
    write_csv(input_dir / "data" / "data_dictionary.csv", build_data_dictionary())
    write_csv(
        input_dir / "data" / "overlay_schedule.csv",
        pd.DataFrame(
            [
                {"scenario_name": scenario_name, "segment_id": segment_id, "overlay_bps": value}
                for scenario_name, mapping in spec.overlay_bps_by_scenario.items()
                for segment_id, value in mapping.items()
            ]
        ),
    )
    write_csv(input_dir / "scenarios" / "baseline.csv", quarter_frame(spec.baseline_scenario))
    write_csv(input_dir / "scenarios" / "adverse.csv", quarter_frame(spec.adverse_scenario))
    write_csv(input_dir / "scenarios" / "severe.csv", quarter_frame(spec.severe_scenario))
    write_csv(input_dir / "outputs" / "prior_baseline_reserve.csv", analysis["prior_baseline"])
    write_csv(input_dir / "outputs" / "prior_scenario_summary.csv", analysis["scenario_summary"])
    write_csv(input_dir / "outputs" / "prior_segment_reserves.csv", analysis["segment_summary"])

    _write_text(input_dir / "docs" / "methodology.md", documents.methodology_md)
    _write_text(input_dir / "docs" / "model_overview.md", documents.model_overview_md)
    _write_text(input_dir / "docs" / "scenario_assumptions.md", documents.scenario_assumptions_md)
    _write_text(input_dir / "docs" / "overlay_memo.md", documents.overlay_memo_md)
    _write_text(input_dir / "docs" / "prior_review_note.md", documents.prior_review_note_md)
    _write_text(input_dir / "docs" / "governance_minutes.md", documents.governance_minutes_md)
    _write_text(input_dir / "docs" / "control_process_note.md", documents.control_process_note_md)
    _write_text(input_dir / "model" / "cecl_engine.py", _render_engine_script(spec))

    inventory = build_full_review_inventory()
    evidence_paths = [item["path"] for item in inventory] + [
        "outputs/support/baseline_reproduction.json",
        "outputs/support/scenario_results.csv",
        "outputs/support/segment_reserve_comparison.csv",
        "outputs/support/sensitivity_results.csv",
        "outputs/support/driver_bridge.csv",
        "outputs/support/documentation_crosscheck.md",
    ]
    evidence_ledger = build_evidence_ledger(evidence_paths)

    discovery_payload = {
        "case_type": "cecl_full_review",
        "workflow": "model_driven_review_memo",
        "artifact_inventory": inventory,
        "runnable": True,
        "gaps": [],
        "key_observations": [
            "Reserve engine, scenario tables, prior outputs, and supporting methodology documents were all present.",
            "The package supports baseline reproduction, scenario reruns, sensitivity testing, and documentation cross-checking.",
            "Documentation claims a different forecast/reversion treatment than the implemented engine.",
        ],
    }
    _write_json(support_dir / "discovery_summary.json", discovery_payload)
    _write_text(
        support_dir / "discovery_summary.md",
        render_discovery_summary(
            case_name=spec.portfolio_name,
            workflow_label="model-driven CECL review memo",
            portfolio_context=spec.product_context,
            inventory=inventory,
            key_observations=cast(list[str], discovery_payload["key_observations"]),
            gaps=[],
        ),
    )

    plan_items = [
        {
            "title": "Baseline reproduction",
            "why_it_matters": "Reproducing the supplied baseline reserve is the first check on whether the package is internally coherent and executable.",
            "evidence": ["model/cecl_engine.py", "data/loan_level_snapshot.csv", "outputs/prior_baseline_reserve.csv"],
            "checks": ["rerun baseline reserve", "compare total reserve", "compare segment reserve"],
        },
        {
            "title": "Scenario review",
            "why_it_matters": "Baseline, adverse, and severe reruns show whether reserves move directionally and materially in line with scenario severity.",
            "evidence": ["scenarios/baseline.csv", "scenarios/adverse.csv", "scenarios/severe.csv", "docs/scenario_assumptions.md"],
            "checks": ["rerun scenarios", "compare total reserve", "compare segment ordering"],
        },
        {
            "title": "Sensitivity testing",
            "why_it_matters": "Forecast horizon, reversion speed, macro severity, and overlay magnitude are core CECL assumptions that should have understandable reserve impact.",
            "evidence": ["docs/methodology.md", "docs/overlay_memo.md", "data/overlay_schedule.csv"],
            "checks": ["horizon sensitivity", "reversion sensitivity", "overlay sensitivity", "driver bridge"],
        },
        {
            "title": "Documentation cross-check",
            "why_it_matters": "Documentation should describe the same horizon, reversion, scenario, and overlay behavior that the implementation actually exhibits.",
            "evidence": ["docs/methodology.md", "docs/model_overview.md", "docs/overlay_memo.md", "model/cecl_engine.py"],
            "checks": ["horizon mismatch", "overlay cap mismatch", "scenario anomaly review"],
        },
    ]
    _write_text(support_dir / "review_plan.md", render_review_plan(spec.portfolio_name, plan_items))

    scenario_results = analysis["scenario_summary"].copy()
    segment_comparison = analysis["segment_comparison"].copy()
    sensitivity_results = analysis["sensitivity_results"].copy()
    driver_bridge = analysis["driver_bridge"].copy()
    baseline_reproduction = analysis["baseline_reproduction"]
    doc_crosscheck = analysis["doc_crosscheck"]
    findings = analysis["findings"]

    write_csv(support_dir / "scenario_results.csv", scenario_results)
    write_csv(support_dir / "segment_reserve_comparison.csv", segment_comparison)
    write_csv(support_dir / "sensitivity_results.csv", sensitivity_results)
    write_csv(support_dir / "driver_bridge.csv", driver_bridge)
    _write_json(support_dir / "baseline_reproduction.json", baseline_reproduction)
    _write_json(support_dir / "findings_register.json", {"findings": findings})
    _write_json(support_dir / "evidence_ledger.json", {"evidence": evidence_ledger})
    _write_json(support_dir / "analysis_summary.json", analysis["analysis_summary"])

    crosscheck_sections = [
        {
            "title": "Methodology versus implementation",
            "summary": "The written methodology and model overview describe a different forecast and reversion treatment than the reserve engine actually uses.",
            "evidence": ["docs/methodology.md", "docs/model_overview.md", "model/cecl_engine.py"],
            "observations": [
                f"Documented forecast quarters: {doc_crosscheck['documented_forecast_quarters']}",
                f"Implemented forecast quarters: {doc_crosscheck['implemented_forecast_quarters']}",
                f"Documented reversion quarters: {doc_crosscheck['documented_reversion_quarters']}",
                f"Implemented reversion quarters: {doc_crosscheck['implemented_reversion_quarters']}",
            ],
        },
        {
            "title": "Overlay posture",
            "summary": "The overlay memo understates the magnitude of the overlay table used in the actual scenario runs.",
            "evidence": ["docs/overlay_memo.md", "data/overlay_schedule.csv", "outputs/support/sensitivity_results.csv"],
            "observations": [
                f"Documented overlay cap: {doc_crosscheck['documented_overlay_cap_bps']:.1f} bps",
                f"Actual overlay cap in schedule: {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps",
            ],
        },
        {
            "title": "Scenario reasonableness",
            "summary": "Overall reserve monotonicity is intact, but one segment behaves oddly under the severe scenario.",
            "evidence": ["outputs/support/segment_reserve_comparison.csv", "docs/scenario_assumptions.md", "docs/overlay_memo.md"],
            "observations": [
                f"Overall reserve ordering: baseline {doc_crosscheck['overall_monotonicity']['baseline']:.2f}, adverse {doc_crosscheck['overall_monotonicity']['adverse']:.2f}, severe {doc_crosscheck['overall_monotonicity']['severe']:.2f}",
                f"Anomaly segment: {doc_crosscheck['anomaly_segment']['segment_id']}",
                f"Adverse versus severe segment delta: {doc_crosscheck['anomaly_segment']['delta']:.2f}",
            ],
        },
    ]
    _write_text(
        support_dir / "documentation_crosscheck.md",
        render_document_crosscheck("Documentation Cross-Check", crosscheck_sections),
    )
    _write_text(
        support_dir / "coverage_statement.md",
        render_coverage_statement(
            "Coverage Statement",
            supported=[
                "Baseline reproduction",
                "Scenario reruns",
                "Sensitivity testing",
                "Reserve driver bridge",
                "Documentation cross-checking",
            ],
            blocked=[],
            rationale="The package included runnable model logic, scenario tables, loan-level data, and supporting documentation sufficient for a substantive CECL review.",
        ),
    )
    _write_text(
        support_dir / "codex_trace.md",
        render_codex_trace(
            spec.portfolio_name,
            [
                {
                    "stage": "Discovery",
                    "summary": "Inventoried the CECL package, identified model code, scenario tables, loan-level data, prior outputs, and supporting methodology documents.",
                    "inputs": ["input_package/*"],
                    "outputs": ["discovery_summary.json", "evidence_ledger.json"],
                },
                {
                    "stage": "Planning",
                    "summary": "Committed to baseline reproduction, scenario reruns, sensitivity testing, and documentation cross-checking based on the evidence supplied.",
                    "inputs": ["discovery_summary.json", "docs/methodology.md", "outputs/prior_baseline_reserve.csv"],
                    "outputs": ["review_plan.md"],
                },
                {
                    "stage": "Quantitative execution",
                    "summary": "Ran the reserve engine across baseline, adverse, and severe scenarios, then executed horizon, reversion, severity, and overlay sensitivities.",
                    "inputs": ["model/cecl_engine.py", "data/loan_level_snapshot.csv", "scenarios/*.csv"],
                    "outputs": ["scenario_results.csv", "segment_reserve_comparison.csv", "sensitivity_results.csv", "driver_bridge.csv"],
                },
                {
                    "stage": "Documentation cross-checking",
                    "summary": "Compared documented horizon, reversion, scenario, and overlay assumptions to actual behavior in the reserve results.",
                    "inputs": ["docs/*.md", "data/overlay_schedule.csv", "segment_reserve_comparison.csv"],
                    "outputs": ["documentation_crosscheck.md", "findings_register.json"],
                },
                {
                    "stage": "Synthesis",
                    "summary": "Drafted the stakeholder-facing CECL review memo and supporting artifact pack.",
                    "inputs": ["findings_register.json", "coverage_statement.md", "baseline_reproduction.json"],
                    "outputs": ["cecl_review_memo.tex", "cecl_review_memo.pdf"],
                },
            ],
        ),
    )

    latex = render_full_review_latex(spec, scenario_results, sensitivity_results, findings, doc_crosscheck)
    tex_path = stakeholder_dir / "cecl_review_memo.tex"
    _write_text(tex_path, latex)
    stakeholder_artifacts = [str(tex_path.relative_to(case_dir))]
    if compile_pdf:
        pdf_path = compile_latex(tex_path)
        stakeholder_artifacts.append(str(pdf_path.relative_to(case_dir)))

    return BuiltCaseArtifacts(
        case_slug=spec.case_slug,
        workflow="full_review",
        input_package_dir=str(input_dir),
        stakeholder_dir=str(stakeholder_dir),
        support_dir=str(support_dir),
        stakeholder_artifacts=stakeholder_artifacts,
        support_artifacts=[str(path.relative_to(case_dir)) for path in sorted(support_dir.rglob("*")) if path.is_file()],
    )


def _build_gap_assessment_case(
    spec: GapAssessmentSpec,
    *,
    settings: Settings,
    authoring_mode: Literal["gateway", "local"],
    compile_pdf: bool,
) -> BuiltCaseArtifacts:
    case_dir = _reset_case_dir(spec.case_slug)
    input_dir = case_dir / "input_package"
    stakeholder_dir = case_dir / "outputs" / "stakeholder"
    support_dir = case_dir / "outputs" / "support"

    for path in [
        input_dir / "docs",
        input_dir / "data",
        input_dir / "outputs",
        input_dir / "scenarios",
        stakeholder_dir,
        support_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    documents = _author_gap_assessment_documents(spec, settings=settings, authoring_mode=authoring_mode)
    provided_outputs = generate_gap_assessment_provided_outputs(spec)
    analysis = run_gap_assessment_analysis(spec, provided_outputs)

    write_csv(input_dir / "data" / "data_dictionary.csv", build_data_dictionary())
    write_csv(input_dir / "data" / "sample_rollforward.csv", provided_outputs["sample_rollforward"])
    write_csv(input_dir / "scenarios" / "baseline.csv", quarter_frame(spec.baseline_scenario))
    write_csv(input_dir / "scenarios" / "adverse.csv", quarter_frame(spec.adverse_scenario))
    write_csv(input_dir / "scenarios" / "severe.csv", quarter_frame(spec.severe_scenario))
    write_csv(input_dir / "outputs" / "provided_reserve_summary.csv", provided_outputs["scenario_summary"])
    write_csv(input_dir / "outputs" / "provided_segment_reserves.csv", provided_outputs["segment_summary"])
    write_csv(input_dir / "outputs" / "provided_overlay_bridge.csv", provided_outputs["overlay_bridge"])

    _write_text(input_dir / "docs" / "methodology.md", documents.methodology_md)
    _write_text(input_dir / "docs" / "model_overview.md", documents.model_overview_md)
    _write_text(input_dir / "docs" / "scenario_assumptions.md", documents.scenario_assumptions_md)
    _write_text(input_dir / "docs" / "overlay_memo.md", documents.overlay_memo_md)
    _write_text(input_dir / "docs" / "prior_review_note.md", documents.prior_review_note_md)
    _write_text(input_dir / "docs" / "governance_minutes.md", documents.governance_minutes_md)
    _write_text(input_dir / "docs" / "evidence_request_log.md", documents.evidence_request_log_md)
    _write_text(input_dir / "docs" / "gap_tracker.md", documents.gap_tracker_md)

    inventory = build_gap_inventory()
    evidence_paths = [item["path"] for item in inventory] + [
        "outputs/support/documentation_crosscheck.md",
        "outputs/support/findings_register.json",
        "outputs/support/coverage_statement.md",
    ]
    evidence_ledger = build_evidence_ledger(evidence_paths)

    discovery_payload = {
        "case_type": "cecl_gap_assessment",
        "workflow": "documentation_led_gap_assessment",
        "artifact_inventory": inventory,
        "runnable": False,
        "gaps": [
            "No CECL reserve engine or reproducibility notebook supplied.",
            "No lineaged execution runbook linking prior outputs to a model build.",
        ],
        "key_observations": [
            "Scenario tables, prior reserve outputs, and rich narrative materials are present.",
            "Execution-based validation is blocked by missing implementation artifacts.",
            "The package is still sufficient for scenario, segment, and evidence-completeness review.",
        ],
    }
    _write_json(support_dir / "discovery_summary.json", discovery_payload)
    _write_text(
        support_dir / "discovery_summary.md",
        render_discovery_summary(
            case_name=spec.portfolio_name,
            workflow_label="CECL gap assessment",
            portfolio_context=spec.product_context,
            inventory=inventory,
            key_observations=cast(list[str], discovery_payload["key_observations"]),
            gaps=cast(list[str], discovery_payload["gaps"]),
        ),
    )

    plan_items = [
        {
            "title": "Evidence sufficiency",
            "why_it_matters": "The first job is to determine whether the package supports a review memo or only a gap assessment.",
            "evidence": ["docs/evidence_request_log.md", "docs/gap_tracker.md", "outputs/provided_reserve_summary.csv"],
            "checks": ["runtime blocker assessment", "lineage assessment", "coverage statement"],
        },
        {
            "title": "Scenario consistency",
            "why_it_matters": "If scenario narratives do not match the numeric scenario tables, management cannot rely on directional reserve conclusions.",
            "evidence": ["docs/scenario_assumptions.md", "scenarios/adverse.csv", "scenarios/severe.csv"],
            "checks": ["narrative versus table comparison", "severity ordering review"],
        },
        {
            "title": "Output reconciliation",
            "why_it_matters": "Even without code, prior reserve outputs can be checked for segment reconciliation and overlay magnitude claims.",
            "evidence": ["outputs/provided_segment_reserves.csv", "outputs/provided_overlay_bridge.csv", "docs/overlay_memo.md"],
            "checks": ["segment taxonomy comparison", "overlay magnitude comparison"],
        },
    ]
    _write_text(support_dir / "review_plan.md", render_review_plan(spec.portfolio_name, plan_items))

    write_csv(support_dir / "provided_reserve_summary.csv", analysis["scenario_summary"])
    write_csv(support_dir / "provided_segment_reserves.csv", analysis["segment_summary"])
    write_csv(support_dir / "provided_overlay_bridge.csv", analysis["overlay_bridge"])
    _write_json(support_dir / "findings_register.json", {"findings": analysis["findings"]})
    _write_json(support_dir / "evidence_ledger.json", {"evidence": evidence_ledger})
    _write_json(support_dir / "analysis_summary.json", analysis["analysis_summary"])

    crosscheck_sections = [
        {
            "title": "Execution readiness",
            "summary": "The package supports narrative and prior-output review only. It does not support baseline reproduction or scenario reruns.",
            "evidence": ["docs/evidence_request_log.md", "docs/gap_tracker.md", "outputs/provided_reserve_summary.csv"],
            "observations": [
                "No reserve engine was supplied.",
                "No reproducibility notebook or execution runbook was supplied.",
            ],
        },
        {
            "title": "Scenario definition review",
            "summary": "The scenario narrative and numeric scenario tables are not perfectly aligned.",
            "evidence": ["docs/scenario_assumptions.md", "scenarios/adverse.csv", "scenarios/severe.csv"],
            "observations": [
                f"Quarters with severe house-price growth less severe than adverse: {len(analysis['scenario_mismatch_quarters'])}",
            ],
        },
        {
            "title": "Segment and overlay reconciliation",
            "summary": "The documented segment structure and overlay posture do not reconcile cleanly to the supplied reserve outputs.",
            "evidence": ["docs/methodology.md", "docs/model_overview.md", "docs/overlay_memo.md", "outputs/provided_segment_reserves.csv", "outputs/provided_overlay_bridge.csv"],
            "observations": [
                f"Documented segments: {len(spec.documented_segments)}",
                f"Output segments: {len(spec.output_segments)}",
                f"Documented overlay cap: {spec.documented_overlay_cap_bps:.1f} bps",
                f"Provided overlay cap: {max(spec.provided_overlay_bps_by_segment.values()):.1f} bps",
            ],
        },
    ]
    _write_text(
        support_dir / "documentation_crosscheck.md",
        render_document_crosscheck("Documentation Cross-Check", crosscheck_sections),
    )
    _write_text(
        support_dir / "coverage_statement.md",
        render_coverage_statement(
            "Coverage Statement",
            supported=[
                "Discovery and evidence sufficiency review",
                "Scenario-definition consistency review",
                "Provided-output reconciliation",
                "Overlay documentation review",
            ],
            blocked=[
                "Baseline reproduction",
                "Scenario reruns against a reserve engine",
                "Sensitivity testing on implementation assumptions",
                "Model-code review",
            ],
            rationale="The package contains useful CECL documentation and output snapshots, but it does not contain the implementation artifacts needed for execution-based validation.",
        ),
    )
    _write_text(
        support_dir / "evidence_request_list.md",
        "\n".join(
            ["# Evidence Requests", ""]
            + [f"- {item}" for item in analysis["evidence_requests"]]
        )
        + "\n",
    )
    _write_text(
        support_dir / "codex_trace.md",
        render_codex_trace(
            spec.portfolio_name,
            [
                {
                    "stage": "Discovery",
                    "summary": "Inventoried the documentation-led CECL package and identified scenario tables, prior outputs, and governance materials but no runnable engine.",
                    "inputs": ["input_package/*"],
                    "outputs": ["discovery_summary.json", "evidence_ledger.json"],
                },
                {
                    "stage": "Planning",
                    "summary": "Narrowed the review to evidence sufficiency, scenario consistency, output reconciliation, and overlay support because runtime validation was blocked.",
                    "inputs": ["discovery_summary.json", "docs/evidence_request_log.md"],
                    "outputs": ["review_plan.md"],
                },
                {
                    "stage": "Cross-checking",
                    "summary": "Compared documentation claims to supplied scenario tables and reserve outputs, then drafted specific evidence requests.",
                    "inputs": ["docs/*.md", "scenarios/*.csv", "outputs/*.csv"],
                    "outputs": ["documentation_crosscheck.md", "findings_register.json", "evidence_request_list.md"],
                },
                {
                    "stage": "Synthesis",
                    "summary": "Drafted the stakeholder-facing gap assessment and supporting artifact pack.",
                    "inputs": ["findings_register.json", "coverage_statement.md", "evidence_request_list.md"],
                    "outputs": ["cecl_gap_assessment.tex", "cecl_gap_assessment.pdf"],
                },
            ],
        ),
    )

    latex = render_gap_assessment_latex(
        spec,
        analysis["scenario_summary"],
        analysis["findings"],
        analysis["evidence_requests"],
    )
    tex_path = stakeholder_dir / "cecl_gap_assessment.tex"
    _write_text(tex_path, latex)
    stakeholder_artifacts = [str(tex_path.relative_to(case_dir))]
    if compile_pdf:
        pdf_path = compile_latex(tex_path)
        stakeholder_artifacts.append(str(pdf_path.relative_to(case_dir)))

    return BuiltCaseArtifacts(
        case_slug=spec.case_slug,
        workflow="gap_assessment",
        input_package_dir=str(input_dir),
        stakeholder_dir=str(stakeholder_dir),
        support_dir=str(support_dir),
        stakeholder_artifacts=stakeholder_artifacts,
        support_artifacts=[str(path.relative_to(case_dir)) for path in sorted(support_dir.rglob("*")) if path.is_file()],
    )


def _author_full_review_documents(
    spec: FullReviewSpec,
    *,
    settings: Settings,
    authoring_mode: Literal["gateway", "local"],
) -> FullReviewDocumentSet:
    if authoring_mode == "local":
        return _local_full_review_documents(spec)

    async def _run() -> FullReviewDocumentSet:
        client = CeclAuthoringClient(settings, model=settings.workbench_agent_model)
        try:
            return await client.author_full_review_documents(spec.model_dump(mode="json"))
        finally:
            await client.shutdown()

    return asyncio.run(_run())


def _author_gap_assessment_documents(
    spec: GapAssessmentSpec,
    *,
    settings: Settings,
    authoring_mode: Literal["gateway", "local"],
) -> GapAssessmentDocumentSet:
    if authoring_mode == "local":
        return _local_gap_assessment_documents(spec)

    async def _run() -> GapAssessmentDocumentSet:
        client = CeclAuthoringClient(settings, model=settings.workbench_agent_model)
        try:
            return await client.author_gap_assessment_documents(spec.model_dump(mode="json"))
        finally:
            await client.shutdown()

    return asyncio.run(_run())


def _local_full_review_documents(spec: FullReviewSpec) -> FullReviewDocumentSet:
    methodology = f"""# CECL Methodology

## Objective
Review the {spec.portfolio_name} CECL reserve process for {spec.bank_name}. The documented methodology states a {spec.documented_forecast_quarters}-quarter reasonable-and-supportable forecast period followed by {spec.documented_reversion_quarters} quarters of straight-line reversion to long-run loss behavior.

## Segments
{chr(10).join(f"- {segment.display_name}" for segment in spec.segments)}

## Key Drivers
- Unemployment rate
- GDP growth
- House price growth
- CRE price growth
- Prime rate

## Overlay Treatment
Qualitative overlays are documented as targeted adjustments capped at {spec.documented_overlay_cap_bps:.1f} bps and are not expected to change scenario ordering at segment level.
"""

    model_overview = f"""# Model Overview

**Owner:** Redwood Regional Bank Finance and Credit Analytics

**Purpose:** Estimate CECL reserves for the {spec.product_context}.

**Core Design:** Segment-level lifetime expected loss using loan risk features, macro scenarios, and modest qualitative overlays. Documentation describes {spec.documented_forecast_quarters} forecast quarters and {spec.documented_reversion_quarters} reversion quarters.
"""

    scenario_assumptions = """# Scenario Assumptions

Baseline, adverse, and severe scenarios were prepared by Finance. Severe is described as a uniformly harsher path than adverse, with higher unemployment, lower GDP growth, and weaker real-estate prices across the modeled horizon.

The review should therefore expect total reserve and segment reserve ordering to be baseline, then adverse, then severe, absent a clearly documented exception.
"""

    overlay_memo = f"""# Overlay Memo

Management overlays are described as targeted and modest, capped at {spec.documented_overlay_cap_bps:.1f} bps by segment-scenario combination. The documented intent is to preserve scenario ordering while capturing qualitative risks not fully represented in the core reserve engine.
"""

    prior_review_note = """# Prior Review Note

The previous review emphasized that scenario ordering and documentation alignment should remain explicit after any reserve-engine refresh. Particular attention was recommended for housing-sensitive segments if scenario recovery paths changed.
"""

    governance_minutes = """# Governance Minutes

Finance, Credit Analytics, and Model Risk reviewed the CECL package. The committee agreed that the package was ready for a substantive review and requested explicit evidence on scenario ordering, overlay effects, and any changes to forecast or reversion assumptions.
"""

    control_process_note = """# Control Process Note

Quarterly CECL packages are archived with scenario tables, loan-level reserve extracts, prior run outputs, and governance documents. Reproduction checks are expected before any governance opinion is finalized.
"""

    return FullReviewDocumentSet(
        methodology_md=methodology,
        model_overview_md=model_overview,
        scenario_assumptions_md=scenario_assumptions,
        overlay_memo_md=overlay_memo,
        prior_review_note_md=prior_review_note,
        governance_minutes_md=governance_minutes,
        control_process_note_md=control_process_note,
    )


def _local_gap_assessment_documents(spec: GapAssessmentSpec) -> GapAssessmentDocumentSet:
    methodology = f"""# CECL Methodology

The documented CECL process for {spec.bank_name} describes a {spec.documented_forecast_quarters}-quarter reasonable-and-supportable period with {spec.documented_reversion_quarters} reversion quarters. Documentation states the reserve process covers the following segments:

{chr(10).join(f"- {segment}" for segment in spec.documented_segments)}
"""

    model_overview = f"""# Model Overview

The model overview describes a CECL reserve process for {spec.product_context}. It refers to {spec.model_card_forecast_quarters} forecast quarters and {spec.model_card_reversion_quarters} reversion quarters, which does not match the methodology.
"""

    scenario_assumptions = """# Scenario Assumptions

Severe is described as a uniformly harsher path than adverse across the full review horizon. Management expects house prices and unemployment to remain materially worse under severe in every quarter reviewed by governance.
"""

    overlay_memo = f"""# Overlay Memo

Qualitative overlay is described as modest and capped at {spec.documented_overlay_cap_bps:.1f} bps, pending additional governance evidence.
"""

    prior_review_note = """# Prior Review Note

The prior review requested runnable implementation artifacts, lineaged runbooks, and reconciliation between documented segment definitions and reserve outputs before any execution-based review could proceed.
"""

    governance_minutes = """# Governance Minutes

Governance accepted the package for documentation-led review only. Baseline reproduction, scenario reruns, and sensitivity testing were deferred pending a runnable reserve engine and complete execution lineage.
"""

    evidence_request_log = """# Evidence Request Log

- Provide the reserve engine or reproducibility notebook used to produce the supplied reserve outputs.
- Provide execution lineage linking the reserve outputs to the reviewed scenario definitions.
- Reconcile segment definitions across methodology, overview, and reserve outputs.
- Quantify qualitative overlay by segment and scenario.
"""

    gap_tracker = """# Gap Tracker

- Runtime package missing
- Execution lineage missing
- Scenario narrative consistency unresolved
- Segment taxonomy reconciliation unresolved
- Overlay support unresolved
"""

    return GapAssessmentDocumentSet(
        methodology_md=methodology,
        model_overview_md=model_overview,
        scenario_assumptions_md=scenario_assumptions,
        overlay_memo_md=overlay_memo,
        prior_review_note_md=prior_review_note,
        governance_minutes_md=governance_minutes,
        evidence_request_log_md=evidence_request_log,
        gap_tracker_md=gap_tracker,
    )


def _render_engine_script(spec: FullReviewSpec) -> str:
    segment_payload = json.dumps(
        {
            segment.segment_id: {
                "display_name": segment.display_name,
                "base_intercept": segment.base_intercept,
                "lgd_base": segment.lgd_base,
                "macro_sensitivities": segment.macro_sensitivities,
            }
            for segment in spec.segments
        },
        indent=2,
    )
    overlay_payload = json.dumps(spec.overlay_bps_by_scenario, indent=2)
    return f'''"""Standalone CECL reserve engine shipped with the demo package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEGMENTS = {segment_payload}
OVERLAYS = {overlay_payload}
FORECAST_QUARTERS = {spec.implemented_forecast_quarters}
REVERSION_QUARTERS = {spec.implemented_reversion_quarters}


def build_projection(frame: pd.DataFrame) -> pd.DataFrame:
    long_run = {{
        "unemployment_rate": 4.7,
        "gdp_growth": 1.7,
        "house_price_growth": 1.9,
        "cre_price_growth": 1.4,
        "prime_rate": 5.0,
    }}
    forecast = frame.iloc[:FORECAST_QUARTERS].copy()
    last = forecast.iloc[-1].copy()
    reversion_rows = []
    for step in range(1, REVERSION_QUARTERS + 1):
        weight = step / REVERSION_QUARTERS
        row = {{"quarter": f"reversion_{{step}}"}}
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
'''


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_normalize_text(content), encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nested_json_safe(payload), indent=2), encoding="utf-8")


def _normalize_text(content: str) -> str:
    return (
        content.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u00a0", " ")
    )


def _reset_case_dir(case_slug: str) -> Path:
    case_dir = CASES_DIR / case_slug
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the contained CECL demo artifact pack.")
    parser.add_argument(
        "--case",
        choices=["full_review", "gap_assessment", "all"],
        default="all",
    )
    parser.add_argument(
        "--authoring-mode",
        choices=["gateway", "local"],
        default="gateway",
    )
    parser.add_argument(
        "--compile-pdf",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    args = parser.parse_args()
    build_cecl_demo_artifacts(
        case=args.case,
        authoring_mode=args.authoring_mode,
        compile_pdf=args.compile_pdf,
    )
