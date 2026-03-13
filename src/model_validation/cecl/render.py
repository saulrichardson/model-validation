"""Markdown and LaTeX rendering for the CECL demo artifact pack."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from .schemas import FullReviewSpec, GapAssessmentSpec


def render_discovery_summary(
    *,
    case_name: str,
    workflow_label: str,
    portfolio_context: str,
    inventory: list[dict[str, str]],
    key_observations: list[str],
    gaps: list[str],
) -> str:
    lines = [
        f"# Discovery Summary: {case_name}",
        "",
        f"- Workflow: {workflow_label}",
        f"- Context: {portfolio_context}",
        "",
        "## Package Inventory",
    ]
    lines.extend(f"- `{item['path']}` ({item['kind']})" for item in inventory)
    lines.extend(["", "## Key Observations"])
    lines.extend(f"- {item}" for item in key_observations)
    lines.extend(["", "## Gaps"])
    if gaps:
        lines.extend(f"- {item}" for item in gaps)
    else:
        lines.append("- No material discovery gaps prevented execution of the planned review.")
    return "\n".join(lines) + "\n"


def render_review_plan(case_name: str, plan_items: list[dict[str, Any]]) -> str:
    lines = [
        f"# Review Plan: {case_name}",
        "",
        "The review plan below is the work Codex would perform against the discovered package.",
        "",
    ]
    for item in plan_items:
        lines.extend(
            [
                f"## {item['title']}",
                item["why_it_matters"],
                "",
                f"- Evidence: {', '.join(item['evidence'])}",
                f"- Planned checks: {', '.join(item['checks'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_case_understanding(
    *,
    case_name: str,
    workflow_label: str,
    summary: str,
    central_assumptions: list[str],
    reviewable_scope: list[str],
    constraints: list[str],
    key_risks: list[str],
) -> str:
    lines = [
        f"# Case Understanding: {case_name}",
        "",
        f"- Workflow understanding: {workflow_label}",
        "",
        "## Working Summary",
        summary,
        "",
        "## Central Assumptions and Themes",
    ]
    lines.extend(f"- {item}" for item in central_assumptions)
    lines.extend(["", "## Reviewable Scope"])
    lines.extend(f"- {item}" for item in reviewable_scope)
    lines.extend(["", "## Key Risks to Challenge"])
    lines.extend(f"- {item}" for item in key_risks)
    lines.extend(["", "## Constraints and Boundaries"])
    if constraints:
        lines.extend(f"- {item}" for item in constraints)
    else:
        lines.append("- No material constraints were identified beyond normal interpretation limits.")
    return "\n".join(lines).rstrip() + "\n"


def render_review_strategy(
    *,
    case_name: str,
    strategy_summary: str,
    review_questions: list[str],
    procedures: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Review Strategy: {case_name}",
        "",
        strategy_summary,
        "",
        "## Review Questions",
    ]
    lines.extend(f"{index}. {question}" for index, question in enumerate(review_questions, start=1))
    lines.extend(["", "## Procedure Selection Rationale"])
    for procedure in procedures:
        lines.extend(
            [
                f"### {procedure['procedure_id']} - {procedure['procedure_name']}",
                f"- Status: {procedure['status']}",
                f"- Objective: {procedure['objective']}",
                f"- Why selected: {procedure['selection_rationale']}",
                f"- Evidence relied upon: {', '.join(procedure.get('evidence', []))}",
                f"- Success or assessment criteria: {procedure['assessment_criteria']}",
            ]
        )
        blocker = procedure.get("blocker")
        if blocker:
            lines.append(f"- Blocking factor: {blocker}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_executed_test_matrix(case_name: str, procedures: list[dict[str, Any]]) -> str:
    lines = [
        f"# Executed Test Matrix: {case_name}",
        "",
        "| ID | Procedure | Status | Evidence | Outputs | Key Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for procedure in procedures:
        evidence = "<br>".join(procedure.get("evidence", []))
        outputs = "<br>".join(procedure.get("outputs", []))
        key_result = procedure["key_result"].replace("|", "\\|")
        lines.append(
            f"| {procedure['procedure_id']} | {procedure['procedure_name']} | {procedure['status']} | {evidence} | {outputs} | {key_result} |"
        )
    return "\n".join(lines) + "\n"


def render_evidence_map(case_name: str, mappings: list[dict[str, Any]]) -> str:
    lines = [
        f"# Evidence-to-Procedure Map: {case_name}",
        "",
        "This map shows how package artifacts and derived outputs informed specific review procedures.",
        "",
    ]
    for mapping in mappings:
        procedures = ", ".join(mapping.get("procedures", []))
        lines.extend(
            [
                f"## {mapping['evidence_path']}",
                f"- Artifact role: {mapping['role']}",
                f"- Procedures supported: {procedures}",
                f"- How used: {mapping['use_summary']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_agentic_review_log(case_name: str, steps: list[dict[str, Any]]) -> str:
    lines = [
        f"# Agentic Review Log: {case_name}",
        "",
        "This is a readable log of the staged review behavior the platform is intended to automate.",
        "",
    ]
    for index, step in enumerate(steps, start=1):
        lines.extend(
            [
                f"## Step {index}: {step['stage']}",
                step["summary"],
                "",
                f"- Review question addressed: {step['question']}",
                f"- Decision or rationale: {step['decision']}",
                f"- Inputs reviewed: {', '.join(step.get('inputs', []))}",
                f"- Outputs produced: {', '.join(step.get('outputs', []))}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_document_crosscheck(title: str, sections: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", ""]
    for section in sections:
        lines.extend([f"## {section['title']}", section["summary"], ""])
        evidence = section.get("evidence") or []
        if evidence:
            lines.append(f"- Evidence: {', '.join(evidence)}")
        observations = section.get("observations") or []
        lines.extend(f"- {item}" for item in observations)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_codex_trace(case_name: str, steps: list[dict[str, Any]]) -> str:
    lines = [
        f"# Codex Trace: {case_name}",
        "",
        "This is a readable execution trace for the review behaviors the platform should eventually automate.",
        "",
    ]
    for index, step in enumerate(steps, start=1):
        lines.extend(
            [
                f"## Step {index}: {step['stage']}",
                step["summary"],
                "",
                f"- Inputs: {', '.join(step.get('inputs', []))}",
                f"- Outputs: {', '.join(step.get('outputs', []))}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_coverage_statement(title: str, supported: list[str], blocked: list[str], rationale: str) -> str:
    lines = [f"# {title}", "", rationale, "", "## Supported Work"]
    lines.extend(f"- {item}" for item in supported)
    lines.extend(["", "## Blocked Work"])
    if blocked:
        lines.extend(f"- {item}" for item in blocked)
    else:
        lines.append("- No blocked work for this review.")
    return "\n".join(lines) + "\n"


def render_full_review_latex(
    spec: FullReviewSpec,
    inventory: list[dict[str, str]],
    case_understanding: dict[str, Any],
    review_questions: list[str],
    plan_items: list[dict[str, Any]],
    procedure_matrix: list[dict[str, Any]],
    trace_steps: list[dict[str, Any]],
    scenario_summary: pd.DataFrame,
    segment_comparison: pd.DataFrame,
    sensitivity_results: pd.DataFrame,
    driver_bridge: pd.DataFrame,
    baseline_reproduction: dict[str, Any],
    findings: list[dict[str, Any]],
    doc_crosscheck: dict[str, Any],
) -> str:
    scenario_lookup = {
        str(row["scenario_name"]): {
            "reserve_amount": float(row["reserve_amount"]),
            "reserve_rate": float(row["reserve_rate"]),
        }
        for _, row in scenario_summary.iterrows()
    }
    baseline = scenario_lookup["baseline"]
    adverse = scenario_lookup["adverse"]
    severe = scenario_lookup["severe"]
    adverse_delta = adverse["reserve_amount"] - baseline["reserve_amount"]
    severe_delta = severe["reserve_amount"] - adverse["reserve_amount"]
    severe_vs_baseline = severe["reserve_amount"] - baseline["reserve_amount"]

    segment_rows = [
        [
            _display_segment(str(row["segment_id"])),
            _money(float(row["baseline"])),
            _money(float(row["adverse"])),
            _money(float(row["severe"])),
            _money(float(row["adverse_minus_baseline"])),
            _money(float(row["severe_minus_adverse"])),
        ]
        for _, row in segment_comparison.sort_values("segment_id").iterrows()
    ]
    anomaly_row = segment_comparison.loc[
        segment_comparison["segment_id"] == spec.quantitative_anomaly_segment
    ].iloc[0]

    scenario_rows = [
        [
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _pct(float(row["reserve_rate"])),
            _money(float(row["reserve_amount"] - baseline["reserve_amount"])),
        ]
        for _, row in _ordered_scenarios(scenario_summary).iterrows()
    ]

    horizon_rows = _subset_rows(
        sensitivity_results,
        "forecast_horizon",
        ["Forecast Horizon", "Scenario", "Reserve", "Change vs 6Q Base"],
        lambda row: [
            f"{row['setting']} quarters",
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _money(float(row["reserve_amount"] - _lookup_sensitivity(sensitivity_results, 'forecast_horizon', '6'))),
        ],
    )
    reversion_rows = _subset_rows(
        sensitivity_results,
        "reversion_speed",
        ["Reversion Speed", "Scenario", "Reserve", "Change vs 2Q Base"],
        lambda row: [
            f"{row['setting']} quarters",
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _money(float(row["reserve_amount"] - _lookup_sensitivity(sensitivity_results, 'reversion_speed', '2'))),
        ],
    )
    severity_rows = _subset_rows(
        sensitivity_results,
        "macro_severity_scale",
        ["Severity Scale", "Scenario", "Reserve", "Change vs 1.00x"],
        lambda row: [
            f"{row['setting']}x",
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _money(
                float(row["reserve_amount"] - _lookup_sensitivity(sensitivity_results, "macro_severity_scale", "1.0"))
            ),
        ],
    )
    overlay_rows = _subset_rows(
        sensitivity_results,
        "overlay_multiplier",
        ["Overlay Multiplier", "Scenario", "Reserve", "Change vs 1.00x"],
        lambda row: [
            f"{row['setting']}x",
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _money(float(row["reserve_amount"] - _lookup_sensitivity(sensitivity_results, "overlay_multiplier", "1.0"))),
        ],
    )

    driver_rows = [
        [
            _display_driver(str(row["driver"])),
            _money(float(row["reserve_delta_vs_baseline"])),
        ]
        for _, row in driver_bridge.sort_values("reserve_delta_vs_baseline", ascending=False).iterrows()
    ]
    largest_driver = driver_bridge.sort_values("reserve_delta_vs_baseline", ascending=False).iloc[0]

    assumption_rows = [
        [
            "Forecast horizon",
            f"{spec.documented_forecast_quarters} quarters documented",
            f"{spec.implemented_forecast_quarters} quarters implemented",
            "Methodology and model overview are not aligned to engine behavior.",
        ],
        [
            "Reversion horizon",
            f"{spec.documented_reversion_quarters} quarters documented",
            f"{spec.implemented_reversion_quarters} quarters implemented",
            "Policy description and actual reserve mechanics differ.",
        ],
        [
            "Overlay cap",
            f"{doc_crosscheck['documented_overlay_cap_bps']:.1f} bps documented",
            f"{doc_crosscheck['actual_overlay_cap_bps']:.1f} bps scheduled",
            "Qualitative adjustment magnitude exceeds documented guardrail.",
        ],
        [
            "Scenario reasonableness",
            "Severe should be directionally harsher unless clearly justified",
            f"{_display_segment(spec.quantitative_anomaly_segment)} reserve falls by {_money(abs(float(anomaly_row['severe_minus_adverse'])))} from adverse to severe",
            "Segment-level severe path requires additional governance challenge.",
        ],
    ]

    inventory_items = [
        f"{item['path']} ({item['kind']})"
        for item in inventory
    ]
    findings_sections = "\n".join(
        _latex_finding_detail(
            finding,
            recommendation=_full_review_recommendation(finding["title"], spec, doc_crosscheck),
        )
        for finding in findings
    )

    executed_count = sum(1 for item in procedure_matrix if item["status"] == "executed")
    blocked_count = sum(1 for item in procedure_matrix if item["status"] != "executed")
    strategy_rows = [
        [
            item["procedure_id"],
            item["procedure_name"],
            item["status"].replace("_", " ").title(),
            item["selection_rationale"],
        ]
        for item in procedure_matrix
    ]

    executive_summary = (
        f"This memo documents an end-to-end CECL review of {spec.bank_name}'s {spec.portfolio_name}. "
        f"The supplied reserve engine was executable, the packaged baseline reserve was reproduced exactly, and scenario reruns plus targeted sensitivities were completed using the supplied portfolio, scenario, and overlay artifacts. "
        f"Portfolio-level reserve direction was broadly reasonable with total ACL rising from {_money(baseline['reserve_amount'])} under Baseline to {_money(adverse['reserve_amount'])} under Adverse and {_money(severe['reserve_amount'])} under Severe. "
        f"The review nonetheless identified material exceptions requiring remediation before an unqualified approval posture would be appropriate."
    )

    quantitative_summary = (
        f"Baseline reproduction landed at {_money(baseline_reproduction['rerun_total_reserve'])} against a packaged baseline of {_money(baseline_reproduction['packaged_total_reserve'])}, "
        f"with absolute delta {_money(abs(float(baseline_reproduction['absolute_delta'])))} and maximum loan-level delta {_money(float(baseline_reproduction['max_loan_level_abs_delta']))}. "
        f"Relative to Baseline, Adverse increased reserve by {_money(adverse_delta)} and Severe increased reserve by another {_money(severe_delta)}, for a total Severe-versus-Baseline increase of {_money(severe_vs_baseline)}."
    )

    sensitivity_summary = (
        f"Sensitivity testing showed limited change from moving the documented forecast horizon to 4 quarters (change of {_money(_lookup_sensitivity(sensitivity_results, 'forecast_horizon', '4') - _lookup_sensitivity(sensitivity_results, 'forecast_horizon', '6'))}), "
        f"but reserve meaningfully increased as reversion lengthened from 2 to 6 quarters under Severe (change of {_money(_lookup_sensitivity(sensitivity_results, 'reversion_speed', '6') - _lookup_sensitivity(sensitivity_results, 'reversion_speed', '2'))}). "
        f"Scaling severe macro stress from 1.00x to 1.25x added {_money(_lookup_sensitivity(sensitivity_results, 'macro_severity_scale', '1.25') - _lookup_sensitivity(sensitivity_results, 'macro_severity_scale', '1.0'))}, "
        f"while removing overlays reduced Severe reserve by {_money(_lookup_sensitivity(sensitivity_results, 'overlay_multiplier', '1.0') - _lookup_sensitivity(sensitivity_results, 'overlay_multiplier', '0.0'))}."
    )

    documentation_summary = (
        f"Documentation cross-checking found that the written methodology still describes a {spec.documented_forecast_quarters}-quarter reasonable-and-supportable period with {spec.documented_reversion_quarters}-quarter reversion, "
        f"while the engine implements {spec.implemented_forecast_quarters} forecast quarters and {spec.implemented_reversion_quarters} reversion quarters. "
        f"The overlay memo references a {doc_crosscheck['documented_overlay_cap_bps']:.1f} bps guardrail, but the supplied overlay schedule applies up to {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps. "
        f"At segment level, {_display_segment(spec.quantitative_anomaly_segment)} shows a severe-scenario reserve {_money(float(anomaly_row['severe']))}, below its adverse reserve {_money(float(anomaly_row['adverse']))}, driven by the scenario and overlay posture described in the package."
    )

    body_parts = [
        _latex_section("Executive Summary"),
        _latex_paragraph(executive_summary),
        "",
        _latex_section("Scope and Coverage"),
        _latex_paragraph(
            "This review assessed the supplied CECL package for internal coherence, quantitative reasonableness, and documentation alignment. The work covered baseline reproduction, scenario reruns, sensitivity testing, reserve driver analysis, and cross-checking of methodology, scenario, and overlay documentation against implemented behavior."
        ),
        _latex_itemize(
            [
                "Supported work: baseline reproduction, scenario reruns, sensitivity testing, driver analysis, and documentation cross-checking.",
                "Blocked work: none within the scope of the supplied package.",
                "Coverage note: conclusions are grounded in the supplied engine, portfolio, scenario files, overlays, and supporting documentation.",
            ]
        ),
        "",
        _latex_section("Artifacts Reviewed"),
        _latex_itemize(inventory_items),
        "",
        _latex_section("Package Discovery and Case Understanding"),
        _latex_paragraph(case_understanding["summary"]),
        _latex_itemize(
            [f"Central assumption or theme: {item}" for item in case_understanding["central_assumptions"]]
            + [f"Reviewable scope: {item}" for item in case_understanding["reviewable_scope"]]
            + [f"Key risk to challenge: {item}" for item in case_understanding["key_risks"]]
            + [f"Constraint: {item}" for item in case_understanding["constraints"]]
        ),
        "",
        _latex_section("CECL Process Understanding"),
        _latex_paragraph(
            f"The package describes a loan-level CECL process spanning {len(spec.segments)} segments: {', '.join(segment.display_name for segment in spec.segments)}. "
            "The quantitative framework applies scenario-dependent macro paths to lifetime PD and LGD components and then layers qualitative overlays by segment and scenario."
        ),
        _latex_table(
            ["Assumption Area", "Documented Position", "Observed in Package", "Review Implication"],
            assumption_rows,
            column_ratios=[0.16, 0.22, 0.24, 0.28],
            small=True,
        ),
        "",
        _latex_section("Review Strategy and Planning Logic"),
        _latex_paragraph(
            f"The review strategy was formed from the discovered evidence. Codex considered {len(review_questions)} central review questions, selected {executed_count} executable procedures, and identified {blocked_count} blocked or non-applicable procedures."
        ),
        _latex_paragraph(case_understanding["strategy_summary"]),
        _latex_enumerate(review_questions),
        _latex_table(
            ["ID", "Procedure", "Status", "Why Selected"],
            strategy_rows,
            column_ratios=[0.10, 0.22, 0.14, 0.44],
            small=True,
        ),
        "",
        _latex_section("Procedures Performed"),
        *[
            "\n".join(
                [
                    _latex_subsection(procedure["procedure_id"] + " - " + procedure["procedure_name"]),
                    _latex_paragraph(procedure["objective"]),
                    _latex_itemize(
                        [
                            f"Status: {procedure['status'].replace('_', ' ')}",
                            f"Why selected: {procedure['selection_rationale']}",
                            f"Evidence relied upon: {', '.join(procedure['evidence'])}",
                            f"Outputs produced: {', '.join(procedure['outputs'])}",
                            f"Assessment criteria: {procedure['assessment_criteria']}",
                            f"Key result: {procedure['key_result']}",
                        ]
                    ),
                ]
            )
            for procedure in procedure_matrix
        ],
        "",
        _latex_section("Agentic Execution Workflow"),
        *[
            "\n".join(
                [
                    _latex_subsection(step["stage"]),
                    _latex_paragraph(step["summary"]),
                    _latex_itemize(
                        [
                            f"Review question addressed: {step['question']}",
                            f"Decision or rationale: {step['decision']}",
                            f"Inputs reviewed: {', '.join(step.get('inputs', []))}",
                            f"Outputs produced: {', '.join(step.get('outputs', []))}",
                        ]
                    ),
                ]
            )
            for step in trace_steps
        ],
        "",
        _latex_section("Quantitative Results"),
        _latex_subsection("Baseline Reproduction"),
        _latex_paragraph(quantitative_summary),
        _latex_table(
            ["Metric", "Result"],
            [
                ["Packaged baseline reserve", _money(float(baseline_reproduction["packaged_total_reserve"]))],
                ["Rerun baseline reserve", _money(float(baseline_reproduction["rerun_total_reserve"]))],
                ["Absolute delta", _money(abs(float(baseline_reproduction["absolute_delta"])))],
                ["Percent delta", f"{float(baseline_reproduction['pct_delta']):.3f}%"],
                ["Maximum loan-level absolute delta", _money(float(baseline_reproduction["max_loan_level_abs_delta"]))],
            ],
            column_ratios=[0.42, 0.33],
        ),
        "",
        _latex_subsection("Scenario Results"),
        _latex_paragraph(
            f"Portfolio-level reserve ordering was monotonic. Adverse increased reserve by {_money(adverse_delta)} versus Baseline, and Severe increased reserve by {_money(severe_delta)} versus Adverse."
        ),
        _latex_table(
            ["Scenario", "Reserve", "Reserve Rate", "Change vs Baseline"],
            scenario_rows,
            column_ratios=[0.18, 0.22, 0.18, 0.22],
            small=True,
        ),
        "",
        _latex_subsection("Segment Results"),
        _latex_paragraph(
            f"Segment-level behavior was directionally reasonable for most segments. The notable exception was {_display_segment(spec.quantitative_anomaly_segment)}, which declined by {_money(abs(float(anomaly_row['severe_minus_adverse'])))} from Adverse to Severe."
        ),
        _latex_table(
            ["Segment", "Baseline", "Adverse", "Severe", "Adv - Base", "Sev - Adv"],
            segment_rows,
            column_ratios=[0.18, 0.14, 0.14, 0.14, 0.14, 0.14],
            small=True,
        ),
        "",
        _latex_subsection("Sensitivity Testing"),
        _latex_paragraph(sensitivity_summary),
        _latex_table(horizon_rows["headers"], horizon_rows["rows"], column_ratios=[0.18, 0.18, 0.22, 0.22], small=True),
        "",
        _latex_table(reversion_rows["headers"], reversion_rows["rows"], column_ratios=[0.18, 0.18, 0.22, 0.22], small=True),
        "",
        _latex_table(severity_rows["headers"], severity_rows["rows"], column_ratios=[0.18, 0.18, 0.22, 0.22], small=True),
        "",
        _latex_table(overlay_rows["headers"], overlay_rows["rows"], column_ratios=[0.18, 0.18, 0.22, 0.22], small=True),
        "",
        _latex_subsection("Driver Analysis"),
        _latex_paragraph(
            f"The simple reserve bridge indicates that {_display_driver(str(largest_driver['driver']))} was the largest modeled contributor to the Severe-versus-Baseline reserve increase, adding {_money(float(largest_driver['reserve_delta_vs_baseline']))} on a standalone basis."
        ),
        _latex_table(
            ["Driver", "Reserve Delta vs Baseline"],
            driver_rows,
            column_ratios=[0.42, 0.33],
        ),
        "",
        _latex_section("Documentation and Assumption Alignment"),
        _latex_paragraph(documentation_summary),
        _latex_itemize(
            [
                f"Documented forecast/reversion: {spec.documented_forecast_quarters}Q forecast and {spec.documented_reversion_quarters}Q reversion.",
                f"Implemented forecast/reversion: {spec.implemented_forecast_quarters}Q forecast and {spec.implemented_reversion_quarters}Q reversion.",
                f"Documented overlay cap: {doc_crosscheck['documented_overlay_cap_bps']:.1f} bps; scheduled overlay cap: {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps.",
                f"Anomaly observation: {_display_segment(spec.quantitative_anomaly_segment)} severe reserve {_money(float(anomaly_row['severe']))} versus adverse reserve {_money(float(anomaly_row['adverse']))}.",
            ]
        ),
        "",
        _latex_section("Detailed Findings and Remediation"),
        findings_sections,
        "",
        _latex_section("Overall Assessment"),
        _latex_paragraph(
            "The supplied package supported a substantive CECL review and allowed execution of the core quantitative and documentation work expected for this scope. "
            "The baseline output was reproducible and overall reserve direction was reasonable, but documentation and governance artifacts are not yet aligned to implemented behavior, and one segment-level severe result requires explicit management challenge before the package would support an unqualified review conclusion."
        ),
    ]

    return _wrap_latex_document(
        title=f"{spec.bank_name} CECL Review Memo",
        body="\n".join(part for part in body_parts if part != ""),
    )


def render_gap_assessment_latex(
    spec: GapAssessmentSpec,
    inventory: list[dict[str, str]],
    case_understanding: dict[str, Any],
    review_questions: list[str],
    plan_items: list[dict[str, Any]],
    procedure_matrix: list[dict[str, Any]],
    trace_steps: list[dict[str, Any]],
    scenario_summary: pd.DataFrame,
    segment_summary: pd.DataFrame,
    overlay_bridge: pd.DataFrame,
    scenario_mismatch_quarters: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    evidence_requests: list[str],
) -> str:
    scenario_rows = [
        [
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _pct(float(row["reserve_rate"])),
        ]
        for _, row in _ordered_scenarios(scenario_summary).iterrows()
    ]
    segment_pivot = (
        segment_summary.pivot(index="segment_id", columns="scenario_name", values="reserve_amount")
        .reset_index()
        .rename_axis(columns=None)
    )
    segment_rows = [
        [
            _display_segment(str(row["segment_id"])),
            _money(float(row.get("baseline", 0.0))),
            _money(float(row.get("adverse", 0.0))),
            _money(float(row.get("severe", 0.0))),
        ]
        for _, row in segment_pivot.sort_values("segment_id").iterrows()
    ]
    overlay_rows = [
        [
            _display_segment(str(row["segment_id"])),
            f"{float(row['provided_overlay_bps']):.1f} bps",
        ]
        for _, row in overlay_bridge.sort_values("provided_overlay_bps", ascending=False).iterrows()
    ]

    assumption_rows = [
        [
            "Forecast horizon",
            f"{spec.documented_forecast_quarters} quarters in methodology",
            f"{spec.model_card_forecast_quarters} quarters in model overview / 6 numeric quarters provided",
            "Horizon treatment is not consistently documented or evidenced.",
        ],
        [
            "Reversion horizon",
            f"{spec.documented_reversion_quarters} quarters in methodology",
            f"{spec.model_card_reversion_quarters} quarters in model overview / no reversion files provided",
            "Reversion mechanics cannot be independently assessed.",
        ],
        [
            "Segment taxonomy",
            f"{len(spec.documented_segments)} documented segments",
            f"{len(spec.output_segments)} output segments in reserve files",
            "Output reporting does not reconcile to the documented segment structure.",
        ],
        [
            "Overlay guardrail",
            f"{spec.documented_overlay_cap_bps:.1f} bps documented cap",
            f"{max(spec.provided_overlay_bps_by_segment.values()):.1f} bps shown in output bridge",
            "Qualitative adjustment support is incomplete and inconsistent.",
        ],
    ]

    inventory_items = [f"{item['path']} ({item['kind']})" for item in inventory]
    mismatch_text = ", ".join(str(item["quarter"]) for item in scenario_mismatch_quarters) or "none"

    findings_sections = "\n".join(
        _latex_finding_detail(
            finding,
            recommendation=_gap_assessment_recommendation(finding["title"]),
        )
        for finding in findings
    )

    executed_count = sum(1 for item in procedure_matrix if item["status"] == "executed")
    blocked_count = sum(1 for item in procedure_matrix if item["status"] != "executed")
    strategy_rows = [
        [
            item["procedure_id"],
            item["procedure_name"],
            item["status"].replace("_", " ").title(),
            item["selection_rationale"],
        ]
        for item in procedure_matrix
    ]

    executive_summary = (
        f"This assessment covers {spec.bank_name}'s {spec.portfolio_name} package. "
        "The materials are sufficient for a structured documentation-led gap assessment, but they do not support an execution-based CECL review because no reserve engine, reproducibility notebook, or lineaged execution runbook was supplied. "
        "The review therefore focuses on evidence sufficiency, scenario-definition consistency, provided-output reconciliation, and overlay documentation support."
    )

    body_parts = [
        _latex_section("Executive Summary"),
        _latex_paragraph(executive_summary),
        "",
        _latex_section("Scope and Coverage Boundary"),
        _latex_paragraph(
            "This work assessed whether the supplied CECL package is sufficient to support a deeper reserve review and whether the materials provided are internally consistent. The review did not attempt baseline reproduction, scenario reruns, or sensitivity testing because the implementation artifacts required for those procedures were not part of the package."
        ),
        _latex_itemize(
            [
                "Supported work: evidence sufficiency review, scenario-definition consistency review, provided-output reconciliation, and overlay documentation review.",
                "Blocked work: reserve-engine execution, baseline reproduction, implementation sensitivity testing, and model-code review.",
                "Coverage note: all conclusions are bounded to the documents, scenario tables, and output snapshots provided in the package.",
            ]
        ),
        "",
        _latex_section("Artifacts Reviewed"),
        _latex_itemize(inventory_items),
        "",
        _latex_section("Package Discovery and Case Understanding"),
        _latex_paragraph(case_understanding["summary"]),
        _latex_itemize(
            [f"Central assumption or theme: {item}" for item in case_understanding["central_assumptions"]]
            + [f"Reviewable scope: {item}" for item in case_understanding["reviewable_scope"]]
            + [f"Key risk to challenge: {item}" for item in case_understanding["key_risks"]]
            + [f"Constraint: {item}" for item in case_understanding["constraints"]]
        ),
        "",
        _latex_section("Documented CECL Process Understanding"),
        _latex_paragraph(
            f"The package describes a CECL process covering {len(spec.documented_segments)} documented segments: {', '.join(_display_segment(item) for item in spec.documented_segments)}. "
            "Documentation frames the workflow as a narrative and prior-output review package rather than a reproducible model handoff."
        ),
        _latex_table(
            ["Assumption Area", "Documented Position", "Observed in Package", "Review Implication"],
            assumption_rows,
            column_ratios=[0.16, 0.22, 0.24, 0.28],
            small=True,
        ),
        "",
        _latex_section("Review Strategy and Planning Logic"),
        _latex_paragraph(
            f"The review strategy was shaped by the discovered package boundary. Codex considered {len(review_questions)} central review questions, executed {executed_count} documentation-led procedures, and marked {blocked_count} procedures as blocked because the package lacked runnable implementation artifacts."
        ),
        _latex_paragraph(case_understanding["strategy_summary"]),
        _latex_enumerate(review_questions),
        _latex_table(
            ["ID", "Procedure", "Status", "Why Selected"],
            strategy_rows,
            column_ratios=[0.10, 0.22, 0.14, 0.44],
            small=True,
        ),
        "",
        _latex_section("Procedures Performed"),
        *[
            "\n".join(
                [
                    _latex_subsection(procedure["procedure_id"] + " - " + procedure["procedure_name"]),
                    _latex_paragraph(procedure["objective"]),
                    _latex_itemize(
                        [
                            f"Status: {procedure['status'].replace('_', ' ')}",
                            f"Why selected: {procedure['selection_rationale']}",
                            f"Evidence relied upon: {', '.join(procedure['evidence'])}",
                            f"Outputs produced: {', '.join(procedure['outputs'])}",
                            f"Assessment criteria: {procedure['assessment_criteria']}",
                            f"Key result: {procedure['key_result']}",
                        ]
                    ),
                ]
            )
            for procedure in procedure_matrix
        ],
        "",
        _latex_section("Agentic Execution Workflow"),
        *[
            "\n".join(
                [
                    _latex_subsection(step["stage"]),
                    _latex_paragraph(step["summary"]),
                    _latex_itemize(
                        [
                            f"Review question addressed: {step['question']}",
                            f"Decision or rationale: {step['decision']}",
                            f"Inputs reviewed: {', '.join(step.get('inputs', []))}",
                            f"Outputs produced: {', '.join(step.get('outputs', []))}",
                        ]
                    ),
                ]
            )
            for step in trace_steps
        ],
        "",
        _latex_section("Provided Output Snapshot"),
        _latex_paragraph(
            "Although no executable reserve engine was supplied, the package included prior reserve summaries and segment output snapshots that could be reconciled at a high level."
        ),
        _latex_table(
            ["Scenario", "Provided Reserve", "Provided Reserve Rate"],
            scenario_rows,
            column_ratios=[0.22, 0.26, 0.22],
        ),
        "",
        _latex_table(
            ["Output Segment", "Baseline", "Adverse", "Severe"],
            segment_rows,
            column_ratios=[0.30, 0.18, 0.18, 0.18],
            small=True,
        ),
        "",
        _latex_table(
            ["Segment", "Provided Overlay"],
            overlay_rows,
            column_ratios=[0.44, 0.22],
        ),
        "",
        _latex_section("Documentation and Evidence Assessment"),
        _latex_subsection("Execution Readiness"),
        _latex_paragraph(
            "The package does not support runtime validation. No reserve engine, no reproducibility notebook, and no lineaged runbook were included, so the review could not test whether the provided reserves are reproducible from the documented methodology."
        ),
        _latex_subsection("Scenario Consistency"),
        _latex_paragraph(
            f"The numeric scenario files cover six quarters, not the full documented forecast and reversion path. In addition, the severe scenario is not uniformly harsher than the adverse scenario for house-price growth in the following quarters: {mismatch_text}."
        ),
        _latex_subsection("Segment and Overlay Reconciliation"),
        _latex_paragraph(
            f"Documentation references {len(spec.documented_segments)} segments, while the provided reserve output files reconcile to {len(spec.output_segments)} segments. "
            f"The overlay memo frames qualitative adjustments as capped at {spec.documented_overlay_cap_bps:.1f} bps, but the supplied bridge reaches {max(spec.provided_overlay_bps_by_segment.values()):.1f} bps."
        ),
        "",
        _latex_section("Detailed Gaps and Findings"),
        findings_sections,
        "",
        _latex_section("Evidence Requests and Next Actions"),
        _latex_paragraph(
            "The following items are required before the package can support execution-based review procedures."
        ),
        _latex_enumerate(evidence_requests),
        "",
        _latex_section("Overall Assessment"),
        _latex_paragraph(
            "The package is sufficient for a structured CECL gap assessment, but not for a model-driven review opinion. "
            "The principal blockers are missing execution artifacts, inconsistent horizon and segment documentation, scenario narratives that do not fully align to numeric tables, and overlay support that is not quantitatively reconciled."
        ),
    ]

    return _wrap_latex_document(
        title=f"{spec.bank_name} CECL Gap Assessment",
        body="\n".join(part for part in body_parts if part != ""),
    )


def compile_latex(tex_path: Path) -> Path:
    subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            tex_path.name,
        ],
        cwd=tex_path.parent,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["latexmk", "-c", tex_path.name], cwd=tex_path.parent, check=True)
    return tex_path.with_suffix(".pdf")


def _wrap_latex_document(*, title: str, body: str) -> str:
    return "\n".join(
        [
            "\\documentclass[11pt]{article}",
            "\\usepackage[margin=1in]{geometry}",
            "\\usepackage{booktabs}",
            "\\usepackage{array}",
            "\\usepackage{tabularx}",
            "\\usepackage{enumitem}",
            "\\usepackage[T1]{fontenc}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{lmodern}",
            "\\setlength{\\parskip}{0.6em}",
            "\\setlength{\\parindent}{0pt}",
            "\\setlist[itemize]{topsep=3pt,itemsep=3pt,leftmargin=1.4em}",
            "\\setlist[enumerate]{topsep=3pt,itemsep=3pt,leftmargin=1.6em}",
            f"\\title{{{_latex_escape(title)}}}",
            "\\date{March 13, 2026}",
            "\\begin{document}",
            "\\maketitle",
            body,
            "\\end{document}",
        ]
    )


def _latex_table(
    headers: list[str],
    rows: list[list[str]],
    *,
    column_ratios: list[float] | None = None,
    small: bool = False,
) -> str:
    if column_ratios is None:
        col_spec = "".join([">{\\raggedright\\arraybackslash}X" for _ in headers])
    else:
        total = sum(column_ratios)
        normalized = [ratio / total for ratio in column_ratios]
        col_spec = "".join(
            f">{{\\raggedright\\arraybackslash}}p{{{min(ratio * 0.96, 0.92):.3f}\\textwidth}}"
            for ratio in normalized
        )
    lines = [
        "\\begin{center}",
        "\\small" if small else "",
        f"\\begin{{tabularx}}{{\\textwidth}}{{{col_spec}}}",
        "\\toprule",
        " & ".join(_latex_escape(item) for item in headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(_latex_escape(cell) for cell in row) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabularx}", "\\normalsize" if small else "", "\\end{center}"])
    return "\n".join(item for item in lines if item)


def _latex_itemize(items: list[str]) -> str:
    lines = ["\\begin{itemize}"]
    lines.extend(f"\\item {_latex_escape(item)}" for item in items)
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def _latex_enumerate(items: list[str]) -> str:
    lines = ["\\begin{enumerate}"]
    lines.extend(f"\\item {_latex_escape(item)}" for item in items)
    lines.append("\\end{enumerate}")
    return "\n".join(lines)


def _latex_paragraph(text: str) -> str:
    return _latex_escape(text)


def _finding_sentence(finding: dict[str, Any]) -> str:
    severity = str(finding["severity"]).upper()
    return f"[{severity}] {finding['title']}: {finding['summary']}"


def _money(value: float) -> str:
    return f"${value:,.0f}"


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _latex_section(title: str) -> str:
    return f"\\section*{{{_latex_escape(title)}}}"


def _latex_subsection(title: str) -> str:
    return f"\\subsection*{{{_latex_escape(title)}}}"


def _ordered_scenarios(frame: pd.DataFrame) -> pd.DataFrame:
    order = {"baseline": 0, "adverse": 1, "severe": 2}
    return frame.assign(_sort=frame["scenario_name"].map(order)).sort_values("_sort").drop(columns="_sort")


def _lookup_sensitivity(frame: pd.DataFrame, test_type: str, setting: str) -> float:
    subset = frame[(frame["test_type"] == test_type) & (frame["setting"].astype(str) == setting)]
    if subset.empty:
        raise ValueError(f"Missing sensitivity result for {test_type=} {setting=}")
    return float(subset["reserve_amount"].iloc[0])


def _subset_rows(
    frame: pd.DataFrame,
    test_type: str,
    headers: list[str],
    row_builder: Any,
) -> dict[str, Any]:
    subset = frame[frame["test_type"] == test_type].copy()
    rows = [row_builder(row) for _, row in subset.iterrows()]
    return {"headers": headers, "rows": rows}


def _display_segment(value: str) -> str:
    return value.replace("_", " ").title()


def _display_driver(value: str) -> str:
    return value.replace("_", " ").title()


def _display_scenario(value: str) -> str:
    return value.replace("_", " ").title()


def _full_review_recommendation(title: str, spec: FullReviewSpec, doc_crosscheck: dict[str, Any]) -> str:
    if "horizon and reversion" in title.lower():
        return (
            f"Either update the methodology and model overview to the implemented {spec.implemented_forecast_quarters}-quarter forecast and "
            f"{spec.implemented_reversion_quarters}-quarter reversion, or change the engine to match documented policy before the next governance submission."
        )
    if "overlay effect" in title.lower():
        return (
            f"Reconcile the overlay memo and governance materials to the actual schedule, including the {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps cap and the rationale for segment-level relief under Severe."
        )
    if "directionally oddly" in title.lower():
        return (
            f"Challenge the {_display_segment(spec.quantitative_anomaly_segment)} severe scenario result, document whether the house-price recovery and negative overlay are intended, and update committee materials accordingly."
        )
    return "Retain the reproduction evidence as support for package completeness and execution readiness."


def _gap_assessment_recommendation(title: str) -> str:
    if "missing reserve engine" in title.lower():
        return "Provide executable model artifacts, a reproducibility notebook or script, and a lineaged runbook before requesting an execution-based CECL opinion."
    if "scenario narrative" in title.lower():
        return "Refresh the scenario narrative so it matches the numeric path quarter by quarter and include governance approval for the final scenario set."
    if "segment structure" in title.lower():
        return "Reconcile segment taxonomy across methodology, model overview, and reserve reporting, then restate the official segment inventory in one controlled artifact."
    return "Quantify and document the overlay methodology and cap so the reserve bridge can be independently reconciled."


def _latex_finding_detail(finding: dict[str, Any], recommendation: str) -> str:
    evidence = ", ".join(str(item) for item in finding.get("evidence", []))
    return "\n".join(
        [
            _latex_subsection(str(finding["title"])),
            f"\\textbf{{Severity:}} {_latex_escape(str(finding['severity']).upper())}\\\\",
            f"\\textbf{{Observation:}} {_latex_escape(str(finding['summary']))}\\\\",
            f"\\textbf{{Evidence:}} {_latex_escape(evidence)}\\\\",
            f"\\textbf{{Recommended response:}} {_latex_escape(recommendation)}",
        ]
    )


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    escaped = value
    for source, target in replacements.items():
        escaped = escaped.replace(source, target)
    return escaped
