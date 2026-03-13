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
    render_agentic_review_log,
    render_case_understanding,
    render_codex_trace,
    render_coverage_statement,
    render_discovery_summary,
    render_document_crosscheck,
    render_evidence_map,
    render_executed_test_matrix,
    render_full_review_latex,
    render_gap_assessment_latex,
    render_review_plan,
    render_review_strategy,
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
    case_understanding = _full_review_case_understanding(spec)
    review_questions = _full_review_review_questions(spec)
    procedure_matrix = _full_review_procedure_matrix(spec, analysis)
    evidence_map = _build_evidence_map(procedure_matrix)
    trace_steps = _full_review_trace_steps(spec)
    evidence_paths = [item["path"] for item in inventory] + [
        "outputs/support/case_understanding.md",
        "outputs/support/review_strategy.md",
        "outputs/support/executed_test_matrix.md",
        "outputs/support/executed_test_matrix.csv",
        "outputs/support/evidence_map.md",
        "outputs/support/baseline_reproduction.json",
        "outputs/support/scenario_results.csv",
        "outputs/support/segment_reserve_comparison.csv",
        "outputs/support/sensitivity_results.csv",
        "outputs/support/driver_bridge.csv",
        "outputs/support/documentation_crosscheck.md",
        "outputs/support/review_plan.md",
        "outputs/support/agentic_review_log.md",
        "outputs/support/codex_trace.md",
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
    _write_text(
        support_dir / "case_understanding.md",
        render_case_understanding(
            case_name=spec.portfolio_name,
            workflow_label="model-driven CECL review memo",
            summary=case_understanding["summary"],
            central_assumptions=case_understanding["central_assumptions"],
            reviewable_scope=case_understanding["reviewable_scope"],
            constraints=case_understanding["constraints"],
            key_risks=case_understanding["key_risks"],
        ),
    )
    _write_text(
        support_dir / "review_strategy.md",
        render_review_strategy(
            case_name=spec.portfolio_name,
            strategy_summary=case_understanding["strategy_summary"],
            review_questions=review_questions,
            procedures=procedure_matrix,
        ),
    )
    _write_text(
        support_dir / "executed_test_matrix.md",
        render_executed_test_matrix(spec.portfolio_name, procedure_matrix),
    )
    write_csv(support_dir / "executed_test_matrix.csv", pd.DataFrame(procedure_matrix))
    _write_text(
        support_dir / "evidence_map.md",
        render_evidence_map(spec.portfolio_name, evidence_map),
    )
    _write_text(
        support_dir / "agentic_review_log.md",
        render_agentic_review_log(spec.portfolio_name, trace_steps),
    )

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

    latex = render_full_review_latex(
        spec,
        inventory,
        case_understanding,
        review_questions,
        plan_items,
        procedure_matrix,
        trace_steps,
        scenario_results,
        segment_comparison,
        sensitivity_results,
        driver_bridge,
        baseline_reproduction,
        findings,
        doc_crosscheck,
    )
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
    case_understanding = _gap_assessment_case_understanding(spec)
    review_questions = _gap_assessment_review_questions(spec)
    procedure_matrix = _gap_assessment_procedure_matrix(spec, analysis)
    evidence_map = _build_evidence_map(procedure_matrix)
    trace_steps = _gap_assessment_trace_steps(spec)
    evidence_paths = [item["path"] for item in inventory] + [
        "outputs/support/case_understanding.md",
        "outputs/support/review_strategy.md",
        "outputs/support/executed_test_matrix.md",
        "outputs/support/executed_test_matrix.csv",
        "outputs/support/evidence_map.md",
        "outputs/support/documentation_crosscheck.md",
        "outputs/support/findings_register.json",
        "outputs/support/coverage_statement.md",
        "outputs/support/review_plan.md",
        "outputs/support/agentic_review_log.md",
        "outputs/support/codex_trace.md",
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
    _write_text(
        support_dir / "case_understanding.md",
        render_case_understanding(
            case_name=spec.portfolio_name,
            workflow_label="CECL gap assessment",
            summary=case_understanding["summary"],
            central_assumptions=case_understanding["central_assumptions"],
            reviewable_scope=case_understanding["reviewable_scope"],
            constraints=case_understanding["constraints"],
            key_risks=case_understanding["key_risks"],
        ),
    )
    _write_text(
        support_dir / "review_strategy.md",
        render_review_strategy(
            case_name=spec.portfolio_name,
            strategy_summary=case_understanding["strategy_summary"],
            review_questions=review_questions,
            procedures=procedure_matrix,
        ),
    )
    _write_text(
        support_dir / "executed_test_matrix.md",
        render_executed_test_matrix(spec.portfolio_name, procedure_matrix),
    )
    write_csv(support_dir / "executed_test_matrix.csv", pd.DataFrame(procedure_matrix))
    _write_text(
        support_dir / "evidence_map.md",
        render_evidence_map(spec.portfolio_name, evidence_map),
    )
    _write_text(
        support_dir / "agentic_review_log.md",
        render_agentic_review_log(spec.portfolio_name, trace_steps),
    )

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
        inventory,
        case_understanding,
        review_questions,
        plan_items,
        procedure_matrix,
        trace_steps,
        analysis["scenario_summary"],
        analysis["segment_summary"],
        analysis["overlay_bridge"],
        analysis["scenario_mismatch_quarters"],
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


def _full_review_case_understanding(spec: FullReviewSpec) -> dict[str, Any]:
    return {
        "summary": (
            f"The discovered package is best understood as a model-driven CECL review case for {spec.bank_name}'s {spec.portfolio_name}. "
            "It includes executable reserve logic, loan-level portfolio data, scenario definitions, prior baseline outputs, and enough supporting documentation to support both quantitative reruns and documentation challenge."
        ),
        "strategy_summary": (
            "Because the package contained runnable code, scenario files, prior outputs, and core methodology documents, the review strategy prioritized execution-based challenge first and then used documentation review to test whether the written methodology and governance artifacts actually described the observed reserve behavior."
        ),
        "central_assumptions": [
            f"Reasonable-and-supportable horizon is documented as {spec.documented_forecast_quarters} quarters, with {spec.documented_reversion_quarters} quarters of reversion.",
            "Scenario severity should increase reserve directionally from Baseline to Adverse to Severe at portfolio level and generally by segment.",
            "Qualitative overlays should remain within documented governance guardrails and should not produce unexplained segment relief.",
        ],
        "reviewable_scope": [
            "Baseline reproduction from supplied engine and data.",
            "Scenario reruns and segment-level reasonableness testing.",
            "Sensitivity testing for horizon, reversion, macro severity, and overlays.",
            "Methodology, scenario, and overlay documentation alignment review.",
        ],
        "constraints": [
            "No independent historical performance dataset or external benchmark was supplied; conclusions are bounded to the package and synthetic portfolio.",
        ],
        "key_risks": [
            "Documentation may not match the implemented forecast and reversion treatment.",
            "Overlay governance may not reflect actual overlay usage by scenario and segment.",
            "A severe scenario can appear directionally harsher at portfolio level while still producing a segment anomaly.",
        ],
    }


def _full_review_review_questions(spec: FullReviewSpec) -> list[str]:
    return [
        "Does the package contain enough evidence to support a full execution-based CECL review rather than a documentation-only assessment?",
        "Can the supplied baseline reserve be reproduced from the packaged reserve engine, portfolio data, and baseline scenario?",
        "Do reserve outputs move directionally and materially across Baseline, Adverse, and Severe scenarios both overall and by major segment?",
        "How sensitive are reserves to forecast horizon, reversion speed, macro severity, and overlay magnitude assumptions?",
        f"Do the methodology, scenario, and overlay documents faithfully describe the behavior observed in the implemented CECL process, especially for {_humanize_label(spec.quantitative_anomaly_segment)}?",
    ]


def _full_review_procedure_matrix(spec: FullReviewSpec, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    anomaly = analysis["doc_crosscheck"]["anomaly_segment"]
    return [
        {
            "procedure_id": "FR-01",
            "procedure_name": "Package inventory and case classification",
            "objective": "Determine whether the upload supports a model-driven CECL review and identify the core evidence types available.",
            "selection_rationale": "Runnable code, scenario tables, loan-level data, prior outputs, and methodology documents were all present.",
            "assessment_criteria": "Review should only proceed as execution-based if engine, data, scenarios, and prior outputs are all available.",
            "evidence": [
                "model/cecl_engine.py",
                "data/loan_level_snapshot.csv",
                "scenarios/baseline.csv",
                "outputs/prior_baseline_reserve.csv",
                "docs/methodology.md",
            ],
            "status": "executed",
            "outputs": ["discovery_summary.md", "evidence_ledger.json"],
            "key_result": "Package classified as model-driven CECL review with no material execution blockers.",
        },
        {
            "procedure_id": "FR-02",
            "procedure_name": "Baseline reproduction",
            "objective": "Confirm that the packaged baseline reserve can be reproduced from the supplied engine and portfolio inputs.",
            "selection_rationale": "A packaged prior baseline reserve was supplied alongside the runnable engine and source portfolio.",
            "assessment_criteria": "Total reserve and segment reserve should reconcile within tolerance; large deltas would undermine confidence in package integrity.",
            "evidence": [
                "model/cecl_engine.py",
                "data/loan_level_snapshot.csv",
                "outputs/prior_baseline_reserve.csv",
            ],
            "status": "executed",
            "outputs": ["baseline_reproduction.json"],
            "key_result": f"Baseline rerun matched packaged reserve exactly at {analysis['baseline_reproduction']['rerun_total_reserve']:.2f} with 0.000% delta.",
        },
        {
            "procedure_id": "FR-03",
            "procedure_name": "Portfolio-level scenario reruns",
            "objective": "Run Baseline, Adverse, and Severe scenarios and assess directional reserve ordering.",
            "selection_rationale": "The package included three explicit scenario files and a model designed to consume them.",
            "assessment_criteria": "Portfolio reserve should generally increase with scenario severity absent a documented exception.",
            "evidence": [
                "scenarios/baseline.csv",
                "scenarios/adverse.csv",
                "scenarios/severe.csv",
                "model/cecl_engine.py",
            ],
            "status": "executed",
            "outputs": ["scenario_results.csv"],
            "key_result": (
                f"Portfolio reserve increased from {analysis['analysis_summary']['overall_baseline_reserve']:.2f} to "
                f"{analysis['analysis_summary']['overall_adverse_reserve']:.2f} to {analysis['analysis_summary']['overall_severe_reserve']:.2f}."
            ),
        },
        {
            "procedure_id": "FR-04",
            "procedure_name": "Segment-level reasonableness review",
            "objective": "Test whether scenario ordering remains directionally sensible at the segment level.",
            "selection_rationale": "CECL governance depends on segment-level reserve understanding, not just portfolio totals.",
            "assessment_criteria": "Segment movements should generally align to scenario severity or be explicitly supported by documented assumptions.",
            "evidence": [
                "outputs/support/segment_reserve_comparison.csv",
                "docs/scenario_assumptions.md",
                "docs/overlay_memo.md",
            ],
            "status": "executed",
            "outputs": ["segment_reserve_comparison.csv"],
            "key_result": (
                f"{_humanize_label(spec.quantitative_anomaly_segment)} severe reserve was {anomaly['severe_reserve_amount']:.2f}, "
                f"below adverse reserve {anomaly['adverse_reserve_amount']:.2f}, creating a documented challenge item."
            ),
        },
        {
            "procedure_id": "FR-05",
            "procedure_name": "Forecast horizon sensitivity",
            "objective": "Assess reserve sensitivity to changing the reasonable-and-supportable forecast horizon.",
            "selection_rationale": "The methodology makes forecast horizon a named governance assumption.",
            "assessment_criteria": "Reserve movement should be understandable and documented; mismatch to stated policy must be surfaced.",
            "evidence": [
                "docs/methodology.md",
                "outputs/support/sensitivity_results.csv",
            ],
            "status": "executed",
            "outputs": ["sensitivity_results.csv"],
            "key_result": "Moving from 6 to 4 forecast quarters changed baseline reserve only modestly, but it directly exposed a documented-versus-implemented policy mismatch.",
        },
        {
            "procedure_id": "FR-06",
            "procedure_name": "Reversion speed sensitivity",
            "objective": "Assess how severe-scenario reserve responds to longer reversion periods.",
            "selection_rationale": "Reversion mechanics are central to CECL governance and are explicitly documented in the package.",
            "assessment_criteria": "Reserve should move directionally as reversion assumptions are extended or shortened.",
            "evidence": [
                "docs/methodology.md",
                "outputs/support/sensitivity_results.csv",
            ],
            "status": "executed",
            "outputs": ["sensitivity_results.csv"],
            "key_result": "Extending severe-scenario reversion from 2 to 6 quarters increased reserve materially, confirming reversion is a meaningful reserve lever.",
        },
        {
            "procedure_id": "FR-07",
            "procedure_name": "Macro severity sensitivity",
            "objective": "Test whether reserve responds proportionally to macro severity scaling.",
            "selection_rationale": "Scenario severity and directional reasonableness are core to CECL challenge work.",
            "assessment_criteria": "Scaling macro severity upward should generally increase reserve; weaker response would require explanation.",
            "evidence": [
                "scenarios/severe.csv",
                "outputs/support/sensitivity_results.csv",
            ],
            "status": "executed",
            "outputs": ["sensitivity_results.csv"],
            "key_result": "Scaling severe stress from 1.00x to 1.25x materially increased reserve, supporting macro sensitivity monotonicity at portfolio level.",
        },
        {
            "procedure_id": "FR-08",
            "procedure_name": "Overlay magnitude sensitivity",
            "objective": "Assess the reserve effect of removing or amplifying qualitative overlays.",
            "selection_rationale": "The package included a scenario-by-segment overlay schedule and an overlay governance memo.",
            "assessment_criteria": "Overlay effect should be quantitatively explainable and consistent with governance statements.",
            "evidence": [
                "data/overlay_schedule.csv",
                "docs/overlay_memo.md",
                "outputs/support/sensitivity_results.csv",
            ],
            "status": "executed",
            "outputs": ["sensitivity_results.csv"],
            "key_result": "Removing severe overlays reduced reserve materially, confirming overlay posture is consequential and governance-relevant.",
        },
        {
            "procedure_id": "FR-09",
            "procedure_name": "Reserve driver bridge",
            "objective": "Identify which macro and overlay drivers explain the majority of severe-versus-baseline reserve movement.",
            "selection_rationale": "A driver bridge makes the review more interpretable and supports reasonableness challenge.",
            "assessment_criteria": "Major reserve movement should be attributable to understandable drivers rather than unexplained residual behavior.",
            "evidence": [
                "outputs/support/driver_bridge.csv",
                "scenarios/baseline.csv",
                "scenarios/severe.csv",
            ],
            "status": "executed",
            "outputs": ["driver_bridge.csv"],
            "key_result": "CRE price growth was the largest modeled standalone driver of severe-versus-baseline reserve change.",
        },
        {
            "procedure_id": "FR-10",
            "procedure_name": "Methodology and documentation alignment review",
            "objective": "Test whether written methodology, model overview, and overlay documentation match implemented behavior and observed outputs.",
            "selection_rationale": "The package contained enough documentation to support direct cross-checking against the model and results.",
            "assessment_criteria": "Documented horizon, reversion, scenario logic, and overlay posture should match the implemented process or be clearly qualified.",
            "evidence": [
                "docs/methodology.md",
                "docs/model_overview.md",
                "docs/scenario_assumptions.md",
                "docs/overlay_memo.md",
                "model/cecl_engine.py",
            ],
            "status": "executed",
            "outputs": ["documentation_crosscheck.md", "findings_register.json"],
            "key_result": "Cross-checking identified a forecast/reversion mismatch, overlay cap mismatch, and a severe-scenario segment anomaly requiring remediation.",
        },
    ]


def _full_review_trace_steps(spec: FullReviewSpec) -> list[dict[str, Any]]:
    return [
        {
            "stage": "Discovery",
            "summary": "The review started by inventorying the package and determining whether a quantitative review was actually possible from the supplied materials.",
            "question": "What is in the package and does it support execution-based CECL review?",
            "decision": "Treat the case as model-driven because reserve code, loan-level data, scenarios, prior outputs, and core methodology documents were all present.",
            "inputs": ["input_package/*"],
            "outputs": ["discovery_summary.md", "evidence_ledger.json", "case_understanding.md"],
        },
        {
            "stage": "Case understanding and planning",
            "summary": "Codex formed a review strategy around the strongest available evidence and explicitly selected a test set before running the work.",
            "question": "Which review questions matter most for this package and which procedures can answer them credibly?",
            "decision": "Prioritize baseline reproduction, scenario reruns, sensitivities, and documentation alignment because the package supports all four lanes.",
            "inputs": ["discovery_summary.md", "docs/methodology.md", "docs/scenario_assumptions.md", "docs/overlay_memo.md"],
            "outputs": ["review_plan.md", "review_strategy.md", "executed_test_matrix.md"],
        },
        {
            "stage": "Quantitative execution",
            "summary": "The review ran the CECL engine against baseline and stressed scenarios, then executed targeted sensitivities to challenge the major reserve assumptions.",
            "question": "Can the reserve process be reproduced, and do outputs move sensibly overall and by segment?",
            "decision": "Run baseline, adverse, and severe scenarios first, then test horizon, reversion, macro severity, and overlays as the most consequential levers.",
            "inputs": ["model/cecl_engine.py", "data/loan_level_snapshot.csv", "scenarios/*.csv", "data/overlay_schedule.csv"],
            "outputs": ["baseline_reproduction.json", "scenario_results.csv", "segment_reserve_comparison.csv", "sensitivity_results.csv", "driver_bridge.csv"],
        },
        {
            "stage": "Documentation challenge",
            "summary": "After quantitative outputs were produced, the review cross-checked the documents against implemented behavior and reserve results.",
            "question": "Do the written methodology, scenario, and overlay materials describe the same process that the results imply?",
            "decision": "Escalate mismatches where documented governance assumptions differ from implementation or where narrative support is insufficient for observed output behavior.",
            "inputs": ["docs/*.md", "model/cecl_engine.py", "segment_reserve_comparison.csv", "sensitivity_results.csv"],
            "outputs": ["documentation_crosscheck.md", "findings_register.json", "evidence_map.md"],
        },
        {
            "stage": "Synthesis",
            "summary": "The final stage combined discovery, planning, quantitative results, and documentation challenge into an internal review report and support pack.",
            "question": "What opinion can be supported, what findings should be issued, and what evidence supports that conclusion?",
            "decision": "Issue a substantive review with explicit remediation for documentation mismatch, overlay governance, and the residential mortgage severe-scenario anomaly.",
            "inputs": ["findings_register.json", "executed_test_matrix.md", "coverage_statement.md", "agentic_review_log.md"],
            "outputs": ["cecl_review_memo.tex", "cecl_review_memo.pdf"],
        },
    ]


def _gap_assessment_case_understanding(spec: GapAssessmentSpec) -> dict[str, Any]:
    return {
        "summary": (
            f"The discovered package is best understood as a documentation-led CECL gap assessment for {spec.bank_name}'s {spec.portfolio_name}. "
            "It contains narrative methodology, scenario definitions, prior output snapshots, and governance artifacts, but it does not contain the implementation artifacts required for execution-based validation."
        ),
        "strategy_summary": (
            "Because the package lacks a reserve engine and execution lineage, the review strategy intentionally shifts from runtime validation to evidence sufficiency, scenario consistency, output reconciliation, and remediation planning. "
            "The goal is to show what can be credibly reviewed now and what remains blocked."
        ),
        "central_assumptions": [
            f"Methodology documents a {spec.documented_forecast_quarters}-quarter forecast and {spec.documented_reversion_quarters}-quarter reversion.",
            "Scenario narratives should align quarter by quarter to numeric scenario files and to any reserve conclusions drawn from them.",
            "Documented segment taxonomy and overlay limits should reconcile to the provided reserve outputs.",
        ],
        "reviewable_scope": [
            "Documentation sufficiency and internal consistency review.",
            "Scenario narrative versus numeric table comparison.",
            "Provided-output segment and overlay reconciliation.",
            "Evidence request formulation for a future execution-based review.",
        ],
        "constraints": [
            "No reserve engine was supplied.",
            "No reproducibility notebook or execution runbook was supplied.",
            "No lineaged link from outputs to a controlled model version was supplied.",
        ],
        "key_risks": [
            "Scenario documentation may overstate severity relative to the numeric scenario path.",
            "Segment taxonomy may not reconcile across documents and outputs.",
            "Overlay governance may be understated relative to the provided reserve bridge.",
        ],
    }


def _gap_assessment_review_questions(spec: GapAssessmentSpec) -> list[str]:
    return [
        "Does the package support a model-driven CECL opinion, or only a documentation-led gap assessment?",
        "Are the scenario narratives and numeric scenario files aligned closely enough to support directional reserve conclusions?",
        "Do documented forecast horizon, reversion, segment taxonomy, and overlay guardrails reconcile to the provided output snapshots?",
        "What concrete evidence must be supplied before baseline reproduction, scenario reruns, and sensitivity testing can be performed credibly?",
    ]


def _gap_assessment_procedure_matrix(spec: GapAssessmentSpec, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    mismatch_quarters = ", ".join(item["quarter"] for item in analysis["scenario_mismatch_quarters"])
    return [
        {
            "procedure_id": "GA-01",
            "procedure_name": "Package inventory and coverage classification",
            "objective": "Determine whether the upload supports execution-based review or only a documentation-led assessment.",
            "selection_rationale": "The package contained scenario files, output snapshots, and governance documents but no reserve engine or runtime lineage.",
            "assessment_criteria": "Execution-based procedures should be blocked unless code, runbook, and reproducibility evidence are present.",
            "evidence": [
                "docs/evidence_request_log.md",
                "docs/gap_tracker.md",
                "outputs/provided_reserve_summary.csv",
            ],
            "status": "executed",
            "outputs": ["discovery_summary.md", "coverage_statement.md"],
            "key_result": "Case classified as documentation-led CECL gap assessment; execution-based review blocked.",
        },
        {
            "procedure_id": "GA-02",
            "procedure_name": "Execution readiness and lineage assessment",
            "objective": "Establish whether the package includes the artifacts required for baseline reproduction and scenario reruns.",
            "selection_rationale": "A clear coverage boundary is necessary before any deeper opinion can be formed.",
            "assessment_criteria": "Reserve engine, reproducibility materials, and run lineage must be available before execution work can proceed.",
            "evidence": [
                "docs/evidence_request_log.md",
                "docs/gap_tracker.md",
                "docs/governance_minutes.md",
            ],
            "status": "executed",
            "outputs": ["coverage_statement.md", "documentation_crosscheck.md"],
            "key_result": "Runtime validation remained blocked because no reserve engine, reproducibility notebook, or lineaged runbook was supplied.",
        },
        {
            "procedure_id": "GA-03",
            "procedure_name": "Scenario narrative versus table comparison",
            "objective": "Test whether the severe scenario narrative matches the supplied numeric scenario path.",
            "selection_rationale": "Scenario definition quality is reviewable even without runnable code.",
            "assessment_criteria": "A narrative described as uniformly harsher should be reflected in the quarter-by-quarter numeric path or explicitly qualified.",
            "evidence": [
                "docs/scenario_assumptions.md",
                "scenarios/adverse.csv",
                "scenarios/severe.csv",
            ],
            "status": "executed",
            "outputs": ["documentation_crosscheck.md", "findings_register.json"],
            "key_result": f"Severe house-price growth was less severe than adverse in {len(analysis['scenario_mismatch_quarters'])} quarters: {mismatch_quarters}.",
        },
        {
            "procedure_id": "GA-04",
            "procedure_name": "Horizon and reversion consistency review",
            "objective": "Test whether documented forecast and reversion descriptions reconcile across methodology, model overview, and supplied scenario files.",
            "selection_rationale": "Horizon and reversion are governance-critical CECL assumptions even when the implementation is absent.",
            "assessment_criteria": "Documents should describe a consistent forecast and reversion framework that is evidenced in supplied files.",
            "evidence": [
                "docs/methodology.md",
                "docs/model_overview.md",
                "docs/scenario_assumptions.md",
            ],
            "status": "executed",
            "outputs": ["documentation_crosscheck.md", "findings_register.json"],
            "key_result": "Methodology, model overview, and scenario files do not describe one consistent horizon/reversion structure.",
        },
        {
            "procedure_id": "GA-05",
            "procedure_name": "Segment taxonomy reconciliation",
            "objective": "Compare documented segment definitions to the segment structure in the provided reserve outputs.",
            "selection_rationale": "Output reconciliation is one of the few quantitative checks available without the model.",
            "assessment_criteria": "Documented segment structure should match the segmentation of provided output files or be explicitly bridged.",
            "evidence": [
                "docs/methodology.md",
                "docs/model_overview.md",
                "outputs/provided_segment_reserves.csv",
            ],
            "status": "executed",
            "outputs": ["provided_segment_reserves.csv", "findings_register.json"],
            "key_result": f"Documentation references {len(spec.documented_segments)} segments, while outputs reconcile to {len(spec.output_segments)} segments.",
        },
        {
            "procedure_id": "GA-06",
            "procedure_name": "Overlay magnitude reconciliation",
            "objective": "Compare documented overlay posture to the reserve bridge included in the package.",
            "selection_rationale": "Overlay support is reviewable from documentation and provided output snapshots even without code.",
            "assessment_criteria": "Documented overlay cap and rationale should reconcile to the magnitude shown in the reserve bridge.",
            "evidence": [
                "docs/overlay_memo.md",
                "outputs/provided_overlay_bridge.csv",
            ],
            "status": "executed",
            "outputs": ["provided_overlay_bridge.csv", "findings_register.json"],
            "key_result": f"Overlay memo cites a {spec.documented_overlay_cap_bps:.1f} bps cap while the provided bridge reaches {max(spec.provided_overlay_bps_by_segment.values()):.1f} bps.",
        },
        {
            "procedure_id": "GA-07",
            "procedure_name": "Baseline reproduction",
            "objective": "Reproduce the baseline reserve from the implementation and baseline scenario.",
            "selection_rationale": "This would normally be a core CECL procedure if the package contained runnable implementation artifacts.",
            "assessment_criteria": "Cannot proceed without reserve engine, reproducibility materials, and execution lineage.",
            "evidence": [
                "outputs/provided_reserve_summary.csv",
                "docs/evidence_request_log.md",
            ],
            "status": "blocked",
            "outputs": ["coverage_statement.md", "evidence_request_list.md"],
            "key_result": "Not executed because the package contains no reserve engine or reproducibility notebook.",
            "blocker": "Missing reserve engine and execution lineage.",
        },
        {
            "procedure_id": "GA-08",
            "procedure_name": "Scenario reruns and sensitivity testing",
            "objective": "Rerun scenarios and challenge reserve sensitivity to key assumptions.",
            "selection_rationale": "These procedures were considered because they would normally follow scenario and methodology review.",
            "assessment_criteria": "Cannot proceed without executable reserve logic, controllable parameters, and runbook support.",
            "evidence": [
                "scenarios/baseline.csv",
                "scenarios/adverse.csv",
                "scenarios/severe.csv",
                "docs/gap_tracker.md",
            ],
            "status": "blocked",
            "outputs": ["coverage_statement.md", "evidence_request_list.md"],
            "key_result": "Not executed because no model implementation or controllable parameter set was supplied.",
            "blocker": "Missing runtime artifacts and parameter lineage.",
        },
        {
            "procedure_id": "GA-09",
            "procedure_name": "Evidence request and remediation planning",
            "objective": "Translate identified blockers and inconsistencies into a prioritized request list for a future execution-based review.",
            "selection_rationale": "The package still supports useful next-step guidance even without runnable code.",
            "assessment_criteria": "Evidence requests should map directly to blocked procedures and identified gaps.",
            "evidence": [
                "findings_register.json",
                "coverage_statement.md",
                "docs/evidence_request_log.md",
            ],
            "status": "executed",
            "outputs": ["evidence_request_list.md"],
            "key_result": "Produced a focused evidence request list to unlock baseline reproduction, scenario reruns, and deeper model challenge.",
        },
    ]


def _gap_assessment_trace_steps(spec: GapAssessmentSpec) -> list[dict[str, Any]]:
    return [
        {
            "stage": "Discovery",
            "summary": "The review started by inventorying the package and determining whether it supported model execution or only documentation-led review.",
            "question": "What evidence is present, and what kind of CECL review does that evidence support?",
            "decision": "Treat the case as a gap assessment because the package contained narratives, scenarios, and outputs but no runnable reserve implementation.",
            "inputs": ["input_package/*"],
            "outputs": ["discovery_summary.md", "evidence_ledger.json", "case_understanding.md"],
        },
        {
            "stage": "Case understanding and planning",
            "summary": "Codex formed a narrowed review strategy based on the evidence boundary, explicitly separating executable work from blocked work.",
            "question": "Which review questions can be answered credibly now, and which must be deferred?",
            "decision": "Focus on evidence sufficiency, scenario consistency, segment reconciliation, and overlay support; mark runtime procedures as blocked.",
            "inputs": ["discovery_summary.md", "docs/evidence_request_log.md", "docs/methodology.md", "outputs/provided_reserve_summary.csv"],
            "outputs": ["review_plan.md", "review_strategy.md", "executed_test_matrix.md"],
        },
        {
            "stage": "Documentation and output cross-checking",
            "summary": "The review challenged the package using the scenario tables, prior outputs, and governance materials that were actually supplied.",
            "question": "Do the narrative materials reconcile to the numeric scenario files and provided output snapshots?",
            "decision": "Escalate inconsistencies where the severe narrative does not match the numeric path, where segment definitions do not reconcile, or where overlay posture is understated.",
            "inputs": ["docs/*.md", "scenarios/*.csv", "outputs/*.csv"],
            "outputs": ["documentation_crosscheck.md", "findings_register.json", "evidence_map.md"],
        },
        {
            "stage": "Blocked quantitative procedures",
            "summary": "Codex explicitly considered baseline reproduction and sensitivity testing and recorded why they could not be executed.",
            "question": "What normally expected CECL validation work remains unsupported by the package?",
            "decision": "Do not simulate baseline reruns or sensitivities without a reserve engine, reproducibility notebook, or run lineage.",
            "inputs": ["coverage_statement.md", "executed_test_matrix.md", "docs/gap_tracker.md"],
            "outputs": ["coverage_statement.md", "evidence_request_list.md"],
        },
        {
            "stage": "Synthesis",
            "summary": "The final stage combined discovery, planning, blocked-work logic, and documentation findings into a comprehensive internal gap assessment.",
            "question": "What opinion is actually supportable now, and what must management supply next?",
            "decision": "Issue a documentation-led gap assessment with explicit blockers, findings, and next-step evidence requests rather than overclaiming execution coverage.",
            "inputs": ["findings_register.json", "coverage_statement.md", "evidence_request_list.md", "agentic_review_log.md"],
            "outputs": ["cecl_gap_assessment.tex", "cecl_gap_assessment.pdf"],
        },
    ]


def _build_evidence_map(procedures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for procedure in procedures:
        for evidence_path in procedure.get("evidence", []):
            entry = mapping.setdefault(
                evidence_path,
                {
                    "evidence_path": evidence_path,
                    "role": "package or derived evidence",
                    "procedures": [],
                    "use_summary": [],
                },
            )
            entry["procedures"].append(procedure["procedure_id"])
            entry["use_summary"].append(
                f"{procedure['procedure_name']}: {procedure['objective']}"
            )

    return [
        {
            "evidence_path": path,
            "role": entry["role"],
            "procedures": entry["procedures"],
            "use_summary": "; ".join(entry["use_summary"]),
        }
        for path, entry in sorted(mapping.items())
    ]


def _humanize_label(value: str) -> str:
    return value.replace("_", " ").title()


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
