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


def render_artifact_provenance(
    *,
    case_name: str,
    uploaded_artifacts: list[dict[str, Any]],
    generated_artifacts: list[dict[str, Any]],
    input_tree: str,
    generated_tree: str,
) -> str:
    lines = [
        f"# Artifact Provenance: {case_name}",
        "",
        "Conventions:",
        "- `[BANK INPUT]` means a file that was part of the pseudo-bank upload package.",
        "- `[CODEX OUTPUT]` means a file generated during the review workflow or final report rendering.",
        "",
        "## Bank-Uploaded Input Package",
    ]
    for artifact in uploaded_artifacts:
        lines.extend(
            [
                f"- {artifact['label']} `{artifact['relative_path']}`",
                f"  - Kind: {artifact['kind_label']}",
                f"  - Detail: {artifact['detail']}",
                f"  - Review use: {artifact['use_summary']}",
            ]
        )
    lines.extend(["", "## Codex-Generated Review Record"])
    for artifact in generated_artifacts:
        lines.extend(
            [
                f"- {artifact['label']} `{artifact['relative_path']}`",
                f"  - Kind: {artifact['kind_label']}",
                f"  - Detail: {artifact['detail']}",
                f"  - Purpose: {artifact['use_summary']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Uploaded Package Tree",
            "```text",
            input_tree.rstrip(),
            "```",
            "",
            "## Codex Output Tree",
            "```text",
            generated_tree.rstrip(),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_procedure_run_log(case_name: str, events: list[dict[str, Any]]) -> str:
    lines = [
        f"# Procedure Run Log: {case_name}",
        "",
        "This log records the granular review actions that the platform is intended to automate.",
        "",
    ]
    for event in events:
        lines.extend(
            [
                f"## {event['event_id']} - {event['title']}",
                f"- Phase: {event['phase']}",
                f"- Related procedure: {event['procedure_id']}",
                f"- Action: {event['action']}",
                f"- Inputs: {', '.join(event.get('inputs', []))}",
                f"- Outputs: {', '.join(event.get('outputs', []))}",
                f"- Result: {event['result']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_evidence_excerpts(case_name: str, excerpts: list[dict[str, Any]]) -> str:
    lines = [
        f"# Evidence Excerpts: {case_name}",
        "",
        "The excerpts below are short raw snippets from uploaded materials or generated review artifacts.",
        "",
    ]
    for excerpt in excerpts:
        lines.extend(
            [
                f"## {excerpt['label']} `{excerpt['relative_path']}`",
                excerpt["purpose"],
                "",
                "```text",
                excerpt["content"].rstrip(),
                "```",
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
    uploaded_artifacts: list[dict[str, Any]],
    generated_artifacts: list[dict[str, Any]],
    input_tree: str,
    generated_tree: str,
    evidence_excerpts: list[dict[str, Any]],
    procedure_run_log: list[dict[str, Any]],
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
    segment_rows = [
        [
            _display_segment(str(row["segment_id"])),
            _money(float(row["baseline"])),
            _money(float(row["adverse"])),
            _money(float(row["severe"])),
            _money(float(row["severe_minus_adverse"])),
        ]
        for _, row in segment_comparison.sort_values("segment_id").iterrows()
    ]
    driver_rows = [
        [
            _display_driver(str(row["driver"])),
            _money(float(row["reserve_delta_vs_baseline"])),
        ]
        for _, row in driver_bridge.sort_values("reserve_delta_vs_baseline", ascending=False).head(4).iterrows()
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

    findings_sections = "\n".join(
        _latex_finding_detail(
            finding,
            recommendation=_full_review_recommendation(finding["title"], spec, doc_crosscheck),
        )
        for finding in findings
    )
    evidence_excerpt_sections = "\n".join(_latex_evidence_excerpt(excerpt) for excerpt in evidence_excerpts)
    procedure_log_sections = "\n".join(_latex_log_event(event) for event in procedure_run_log)

    executed_count = sum(1 for item in procedure_matrix if item["status"] == "executed")
    blocked_count = sum(1 for item in procedure_matrix if item["status"] != "executed")
    strategy_rows = [
        [
            item["procedure_id"],
            item["procedure_name"],
            item["objective"],
            item["status"].replace("_", " ").title(),
        ]
        for item in procedure_matrix
    ]
    uploaded_paths = [item["path"] for item in inventory]
    uploaded_groups = [
        ("Model implementation", [path for path in uploaded_paths if path.startswith("model/")]),
        ("Portfolio data and overlays", [path for path in uploaded_paths if path.startswith("data/")]),
        ("Scenario definitions", [path for path in uploaded_paths if path.startswith("scenarios/")]),
        ("Documentation and governance materials", [path for path in uploaded_paths if path.startswith("docs/")]),
        ("Packaged prior outputs", [path for path in uploaded_paths if path.startswith("outputs/")]),
    ]
    generated_paths = [str(item["relative_path"]) for item in generated_artifacts]
    generated_groups = [
        (
            "Discovery and planning workpapers",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/discovery_summary.json",
                    "outputs/support/discovery_summary.md",
                    "outputs/support/case_understanding.md",
                    "outputs/support/review_plan.md",
                    "outputs/support/review_strategy.md",
                    "outputs/support/executed_test_matrix.md",
                    "outputs/support/executed_test_matrix.csv",
                    "outputs/support/evidence_map.md",
                    "outputs/support/evidence_ledger.json",
                    "outputs/support/coverage_statement.md",
                }
            ],
        ),
        (
            "Quantitative workpapers",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/baseline_reproduction.json",
                    "outputs/support/scenario_results.csv",
                    "outputs/support/segment_reserve_comparison.csv",
                    "outputs/support/sensitivity_results.csv",
                    "outputs/support/driver_bridge.csv",
                }
            ],
        ),
        (
            "Documentation and findings workpapers",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/documentation_crosscheck.md",
                    "outputs/support/findings_register.json",
                    "outputs/support/evidence_excerpts.md",
                }
            ],
        ),
        (
            "Process and trace artifacts",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/agentic_review_log.md",
                    "outputs/support/procedure_run_log.md",
                    "outputs/support/procedure_run_log.csv",
                    "outputs/support/codex_trace.md",
                    "outputs/support/artifact_provenance.md",
                    "outputs/support/artifact_provenance.json",
                }
            ],
        ),
        (
            "Final deliverables",
            [path for path in generated_paths if path.startswith("outputs/stakeholder/")],
        ),
    ]
    quantitative_support_files = [
        "outputs/support/baseline_reproduction.json",
        "outputs/support/scenario_results.csv",
        "outputs/support/segment_reserve_comparison.csv",
        "outputs/support/sensitivity_results.csv",
        "outputs/support/driver_bridge.csv",
    ]
    documentation_support_files = [
        "outputs/support/documentation_crosscheck.md",
        "outputs/support/findings_register.json",
        "outputs/support/evidence_excerpts.md",
    ]
    appendix_support_files = [
        "outputs/support/artifact_provenance.md",
        "outputs/support/review_plan.md",
        "outputs/support/review_strategy.md",
        "outputs/support/executed_test_matrix.md",
        "outputs/support/procedure_run_log.md",
        "outputs/support/codex_trace.md",
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
        _latex_section("Executive Conclusion"),
        _latex_paragraph(executive_summary),
        _latex_itemize(
            [
                "Review status: qualified internal review conclusion; package supports substantive CECL challenge work, but identified findings should be remediated before an unqualified governance posture is taken.",
                "Most material quantitative observation: portfolio reserve ordering is monotonic, but Residential Mortgage reserve declines from Adverse to Severe.",
                "Most material documentation observation: documented forecast and reversion treatment do not match the implemented reserve engine.",
                "Most material governance observation: overlay usage is materially larger than the documented cap.",
            ]
        ),
        "",
        _latex_section("Review Scope, Package Reviewed, and Coverage"),
        _latex_paragraph(
            "This memo documents an internal CECL review of the supplied package for Redwood Regional Bank's Q1 2026 CECL Allowance Review. The work focused on whether the package was internally coherent, reproducible, directionally reasonable under stressed scenarios, and aligned to its own methodology and governance materials."
        ),
        _latex_itemize(
            [
                "Supported work: baseline reproduction, portfolio and segment scenario reruns, sensitivity testing, reserve-driver interpretation, and documentation/governance alignment review.",
                "Blocked work: none within the scope of the supplied package.",
                "Coverage boundary: conclusions are bounded to the uploaded CECL package, the synthetic portfolio, and the scenarios and overlays included in that package.",
                f"Constraint: {case_understanding['constraints'][0]}",
            ]
        ),
        _latex_subsection("Materials Reviewed"),
        _latex_paragraph(
            "The uploaded package contained enough material to support both quantitative reruns and documentation challenge. The artifact groups below reflect the main categories of bank-supplied inputs that informed the review."
        ),
        _latex_grouped_file_sections(uploaded_groups),
        "",
        _latex_section("CECL Process Overview"),
        _latex_paragraph(case_understanding["summary"]),
        _latex_paragraph(
            f"The documented CECL process covers {len(spec.segments)} primary segments: {', '.join(segment.display_name for segment in spec.segments)}. "
            "The reserve process applies scenario-dependent macro paths to loan-level reserve components and then layers scenario-specific qualitative overlays by segment."
        ),
        _latex_table(
            ["Assumption Area", "Documented Position", "Observed in Package", "Review Implication"],
            assumption_rows,
            column_ratios=[0.16, 0.22, 0.24, 0.28],
            small=True,
        ),
        "",
        _latex_section("Validation Approach"),
        _latex_paragraph(
            f"Codex formed the review strategy from the discovered evidence. The package supported {executed_count} executable procedures across quantitative and documentation lanes, with {blocked_count} blocked procedures."
        ),
        _latex_paragraph(case_understanding["strategy_summary"]),
        _latex_enumerate(review_questions),
        _latex_table(
            ["ID", "Procedure", "What Codex Was Trying To Test", "Status"],
            strategy_rows,
            column_ratios=[0.10, 0.24, 0.48, 0.12],
            small=True,
        ),
        _latex_paragraph(
            "Detailed planning rationale, evidence mapping, and the granular procedure log are retained in the appendices and support files rather than in the main body of the memo."
        ),
        "",
        _latex_section("Quantitative Review Results"),
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
        _latex_subsection("Scenario Analysis"),
        _latex_paragraph(
            f"Portfolio reserve ordering was monotonic. Adverse increased reserve by {_money(adverse_delta)} versus Baseline, and Severe increased reserve by {_money(severe_delta)} versus Adverse."
        ),
        _latex_table(
            ["Scenario", "Reserve", "Reserve Rate", "Change vs Baseline"],
            scenario_rows,
            column_ratios=[0.18, 0.22, 0.18, 0.22],
            small=True,
        ),
        "",
        _latex_subsection("Segment-Level Reasonableness"),
        _latex_paragraph(
            f"Most segments behaved directionally as expected under worsening macro conditions. The principal exception was {_display_segment(spec.quantitative_anomaly_segment)}, which produced a severe-scenario reserve below its adverse reserve."
        ),
        _latex_table(
            ["Segment", "Baseline", "Adverse", "Severe", "Sev - Adv"],
            segment_rows,
            column_ratios=[0.28, 0.15, 0.15, 0.15, 0.15],
            small=True,
        ),
        "",
        _latex_subsection("Sensitivity Analysis"),
        _latex_paragraph(sensitivity_summary),
        _latex_itemize(
            [
                f"Forecast horizon sensitivity: moving from 6 to 4 forecast quarters changed reserve by {_money(_lookup_sensitivity(sensitivity_results, 'forecast_horizon', '4') - _lookup_sensitivity(sensitivity_results, 'forecast_horizon', '6'))}.",
                f"Reversion sensitivity: extending severe-scenario reversion from 2 to 6 quarters increased reserve by {_money(_lookup_sensitivity(sensitivity_results, 'reversion_speed', '6') - _lookup_sensitivity(sensitivity_results, 'reversion_speed', '2'))}.",
                f"Macro severity sensitivity: scaling severe stress from 1.00x to 1.25x increased reserve by {_money(_lookup_sensitivity(sensitivity_results, 'macro_severity_scale', '1.25') - _lookup_sensitivity(sensitivity_results, 'macro_severity_scale', '1.0'))}.",
                f"Overlay sensitivity: removing overlays reduced reserve by {_money(_lookup_sensitivity(sensitivity_results, 'overlay_multiplier', '1.0') - _lookup_sensitivity(sensitivity_results, 'overlay_multiplier', '0.0'))}.",
            ]
        ),
        _latex_paragraph(
            "The full sensitivity grid is retained in the support files and should be used for any follow-on appendix work or management discussion."
        ),
        "",
        _latex_subsection("Reserve Driver Interpretation"),
        _latex_paragraph(
            f"The reserve-driver bridge indicates that {_display_driver(str(largest_driver['driver']))} was the largest modeled contributor to the Severe-versus-Baseline reserve increase, adding {_money(float(largest_driver['reserve_delta_vs_baseline']))} on a standalone basis."
        ),
        _latex_table(
            ["Driver", "Reserve Delta vs Baseline"],
            driver_rows,
            column_ratios=[0.42, 0.33],
        ),
        _latex_subsection("Quantitative Workpapers"),
        _latex_file_reference_items(quantitative_support_files),
        "",
        _latex_section("Documentation and Governance Review"),
        _latex_paragraph(documentation_summary),
        _latex_itemize(
            [
                f"Documented forecast/reversion: {spec.documented_forecast_quarters}Q forecast and {spec.documented_reversion_quarters}Q reversion.",
                f"Implemented forecast/reversion: {spec.implemented_forecast_quarters}Q forecast and {spec.implemented_reversion_quarters}Q reversion.",
                f"Documented overlay cap: {doc_crosscheck['documented_overlay_cap_bps']:.1f} bps; scheduled overlay cap: {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps.",
                f"Scenario/segment observation: {_display_segment(spec.quantitative_anomaly_segment)} severe reserve {_money(float(anomaly_row['severe']))} versus adverse reserve {_money(float(anomaly_row['adverse']))}.",
            ]
        ),
        _latex_subsection("Documentation and Governance Workpapers"),
        _latex_file_reference_items(documentation_support_files),
        "",
        _latex_section("Findings and Required Remediation"),
        findings_sections,
        "",
        _latex_section("Overall Assessment"),
        _latex_paragraph(
            "The supplied package supported a substantive CECL review and allowed execution of the core quantitative and documentation work expected for this scope. "
            "The baseline output was reproducible and overall reserve direction was reasonable, but documentation and governance artifacts are not yet aligned to implemented behavior, and one segment-level severe result requires explicit management challenge before the package would support an unqualified review conclusion."
        ),
        "",
        _latex_section("Appendix A. Materials Reviewed and Artifact Provenance"),
        _latex_paragraph(
            "The main body summarizes the material inputs and outputs. This appendix records the provenance split more explicitly so a reviewer can distinguish what the bank uploaded from what Codex generated during the review."
        ),
        _latex_subsection("Bank-Uploaded Input Categories"),
        _latex_grouped_file_sections(uploaded_groups),
        _latex_subsection("Codex-Generated Review Categories"),
        _latex_grouped_file_sections(generated_groups),
        _latex_subsection("Full Provenance Registers"),
        _latex_file_reference_items(
            [
                "outputs/support/artifact_provenance.md",
                "outputs/support/artifact_provenance.json",
                "outputs/support/evidence_ledger.json",
            ]
        ),
        "",
        _latex_section("Appendix B. Executed Procedure Register"),
        *[_latex_procedure_detail(procedure) for procedure in procedure_matrix],
        "",
        _latex_section("Appendix C. Agentic Review Record"),
        _latex_paragraph(
            "This appendix records the staged review behavior and the granular action log behind the memo. It is intended to show the review workflow without interrupting the main validation narrative."
        ),
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
        _latex_subsection("Planning and Process Files"),
        _latex_file_reference_items(appendix_support_files),
        _latex_subsection("Chronological Procedure Log"),
        procedure_log_sections,
        "",
        _latex_section("Appendix D. Selected Evidence Excerpts"),
        _latex_paragraph(
            "Only text and code excerpts are reproduced here. Structured data outputs are referenced through the support files listed elsewhere in the memo."
        ),
        evidence_excerpt_sections,
    ]

    return _wrap_latex_document(
        title=f"{spec.bank_name} CECL Review Memo",
        body="\n".join(part for part in body_parts if part != ""),
    )


def render_gap_assessment_latex(
    spec: GapAssessmentSpec,
    inventory: list[dict[str, str]],
    uploaded_artifacts: list[dict[str, Any]],
    generated_artifacts: list[dict[str, Any]],
    input_tree: str,
    generated_tree: str,
    evidence_excerpts: list[dict[str, Any]],
    procedure_run_log: list[dict[str, Any]],
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
    segment_pivot = (
        segment_summary.pivot(index="segment_id", columns="scenario_name", values="reserve_amount")
        .reset_index()
        .rename_axis(columns=None)
    )
    scenario_rows = [
        [
            _display_scenario(str(row["scenario_name"])),
            _money(float(row["reserve_amount"])),
            _pct(float(row["reserve_rate"])),
        ]
        for _, row in _ordered_scenarios(scenario_summary).iterrows()
    ]
    segment_rows = [
        [
            _display_segment(str(row["segment_id"])),
            _money(float(row.get("baseline", 0.0))),
            _money(float(row.get("adverse", 0.0))),
            _money(float(row.get("severe", 0.0))),
        ]
        for _, row in segment_pivot.sort_values("segment_id").iterrows()
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

    mismatch_text = ", ".join(str(item["quarter"]) for item in scenario_mismatch_quarters) or "none"
    evidence_excerpt_sections = "\n".join(_latex_evidence_excerpt(excerpt) for excerpt in evidence_excerpts)
    procedure_log_sections = "\n".join(_latex_log_event(event) for event in procedure_run_log)

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
            item["objective"],
            item["status"].replace("_", " ").title(),
        ]
        for item in procedure_matrix
    ]
    uploaded_paths = [item["path"] for item in inventory]
    uploaded_groups = [
        ("Documentation and governance materials", [path for path in uploaded_paths if path.startswith("docs/")]),
        ("Scenario definitions", [path for path in uploaded_paths if path.startswith("scenarios/")]),
        ("Provided reserve outputs", [path for path in uploaded_paths if path.startswith("outputs/")]),
        ("Reference data", [path for path in uploaded_paths if path.startswith("data/")]),
    ]
    generated_paths = [str(item["relative_path"]) for item in generated_artifacts]
    generated_groups = [
        (
            "Discovery and planning workpapers",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/discovery_summary.json",
                    "outputs/support/discovery_summary.md",
                    "outputs/support/case_understanding.md",
                    "outputs/support/review_plan.md",
                    "outputs/support/review_strategy.md",
                    "outputs/support/executed_test_matrix.md",
                    "outputs/support/executed_test_matrix.csv",
                    "outputs/support/evidence_map.md",
                    "outputs/support/evidence_ledger.json",
                    "outputs/support/coverage_statement.md",
                }
            ],
        ),
        (
            "Documentation and reconciliation workpapers",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/documentation_crosscheck.md",
                    "outputs/support/provided_reserve_summary.csv",
                    "outputs/support/provided_segment_reserves.csv",
                    "outputs/support/provided_overlay_bridge.csv",
                    "outputs/support/findings_register.json",
                    "outputs/support/evidence_request_list.md",
                }
            ],
        ),
        (
            "Process and trace artifacts",
            [
                path
                for path in generated_paths
                if path
                in {
                    "outputs/support/agentic_review_log.md",
                    "outputs/support/procedure_run_log.md",
                    "outputs/support/procedure_run_log.csv",
                    "outputs/support/codex_trace.md",
                    "outputs/support/artifact_provenance.md",
                    "outputs/support/artifact_provenance.json",
                }
            ],
        ),
        (
            "Final deliverables",
            [path for path in generated_paths if path.startswith("outputs/stakeholder/")],
        ),
    ]
    gap_support_files = [
        "outputs/support/provided_reserve_summary.csv",
        "outputs/support/provided_segment_reserves.csv",
        "outputs/support/provided_overlay_bridge.csv",
        "outputs/support/documentation_crosscheck.md",
        "outputs/support/evidence_request_list.md",
        "outputs/support/findings_register.json",
    ]
    appendix_support_files = [
        "outputs/support/artifact_provenance.md",
        "outputs/support/review_plan.md",
        "outputs/support/review_strategy.md",
        "outputs/support/executed_test_matrix.md",
        "outputs/support/procedure_run_log.md",
        "outputs/support/codex_trace.md",
    ]

    executive_summary = (
        f"This assessment covers {spec.bank_name}'s {spec.portfolio_name} package. "
        "The materials are sufficient for a structured documentation-led gap assessment, but they do not support an execution-based CECL review because no reserve engine, reproducibility notebook, or lineaged execution runbook was supplied. "
        "The review therefore focuses on evidence sufficiency, scenario-definition consistency, provided-output reconciliation, and overlay documentation support."
    )

    body_parts = [
        _latex_section("Executive Conclusion"),
        _latex_paragraph(executive_summary),
        _latex_itemize(
            [
                "Assessment status: documentation-led CECL gap assessment only; the package does not support an execution-based validation opinion.",
                "Primary blocker: no reserve engine, reproducibility script, or lineaged runbook was supplied.",
                "Primary documentation issue: horizon, segment, and scenario descriptions are not fully reconciled across the package.",
                "Primary governance issue: provided overlay magnitude exceeds the documented cap and is not quantitatively explained.",
            ]
        ),
        "",
        _latex_section("Scope, Package Reviewed, and Coverage Boundary"),
        _latex_paragraph(
            "This memo documents a documentation-led CECL gap assessment of the supplied package for Harborlight Savings. The work focused on whether the package is sufficient for a deeper CECL review and whether the documents, scenario definitions, and prior output snapshots are internally consistent."
        ),
        _latex_itemize(
            [
                "Supported work: evidence sufficiency review, scenario-definition consistency review, provided-output reconciliation, and overlay documentation review.",
                "Blocked work: reserve-engine execution, baseline reproduction, implementation sensitivity testing, and model-code review.",
                "Coverage boundary: all conclusions are bounded to the documents, scenario tables, and output snapshots provided in the package.",
                "Key limitation: no execution-based opinion is supportable from this package alone.",
            ]
        ),
        _latex_subsection("Materials Reviewed"),
        _latex_paragraph(
            "The package was rich enough to support a formal gap assessment, but not rich enough to support CECL reruns or implementation challenge. The artifact groups below summarize the bank-supplied materials that were reviewed."
        ),
        _latex_grouped_file_sections(uploaded_groups),
        "",
        _latex_section("Documented CECL Process Overview"),
        _latex_paragraph(case_understanding["summary"]),
        _latex_paragraph(
            f"The package describes a CECL process covering {len(spec.documented_segments)} documented segments: {', '.join(_display_segment(item) for item in spec.documented_segments)}. "
            "Documentation frames the package as a narrative and prior-output review pack rather than a reproducible model handoff."
        ),
        _latex_table(
            ["Assumption Area", "Documented Position", "Observed in Package", "Review Implication"],
            assumption_rows,
            column_ratios=[0.16, 0.22, 0.24, 0.28],
            small=True,
        ),
        "",
        _latex_section("Assessment Approach"),
        _latex_paragraph(
            f"Codex formed the assessment approach from the discovered evidence boundary. The package supported {executed_count} documentation-led procedures and left {blocked_count} procedures blocked because runnable implementation artifacts were not supplied."
        ),
        _latex_paragraph(case_understanding["strategy_summary"]),
        _latex_enumerate(review_questions),
        _latex_table(
            ["ID", "Procedure", "What Codex Was Trying To Test", "Status"],
            strategy_rows,
            column_ratios=[0.10, 0.24, 0.48, 0.12],
            small=True,
        ),
        _latex_paragraph(
            "Detailed planning rationale, procedure-level records, and the granular process log are retained in the appendices and support files rather than in the main narrative."
        ),
        "",
        _latex_section("Documentation-Led Review Results"),
        _latex_subsection("Execution Readiness"),
        _latex_paragraph(
            "The package does not support runtime validation. No reserve engine, no reproducibility notebook, and no lineaged runbook were included, so the review could not test whether the provided reserves are reproducible from the documented methodology."
        ),
        _latex_subsection("Scenario Definition Consistency"),
        _latex_paragraph(
            f"The numeric scenario files cover six quarters, not the full documented forecast and reversion path. In addition, the severe scenario is not uniformly harsher than the adverse scenario for house-price growth in the following quarters: {mismatch_text}."
        ),
        _latex_subsection("Provided Output Reconciliation"),
        _latex_paragraph(
            "Although the package did not support reruns, it did contain prior reserve summaries and segment output snapshots that could be reconciled at a high level."
        ),
        _latex_table(
            ["Scenario", "Provided Reserve", "Provided Reserve Rate"],
            scenario_rows,
            column_ratios=[0.22, 0.26, 0.22],
        ),
        _latex_table(
            ["Output Segment", "Baseline", "Adverse", "Severe"],
            segment_rows,
            column_ratios=[0.30, 0.18, 0.18, 0.18],
            small=True,
        ),
        _latex_itemize(
            [
                f"The supplied output files reconcile to {len(segment_pivot)} reporting segments rather than the {len(spec.documented_segments)} documented methodology segments.",
                f"The largest provided overlay in the bridge is {max(spec.provided_overlay_bps_by_segment.values()):.1f} bps, above the documented {spec.documented_overlay_cap_bps:.1f} bps cap.",
            ]
        ),
        _latex_subsection("Documentation and Gap-Assessment Workpapers"),
        _latex_file_reference_items(gap_support_files),
        "",
        _latex_section("Findings and Required Evidence"),
        findings_sections,
        "",
        _latex_section("Evidence Requests and Next Actions"),
        _latex_paragraph(
            "The following items are required before the package can support execution-based CECL review procedures."
        ),
        _latex_enumerate(evidence_requests),
        "",
        _latex_section("Overall Assessment"),
        _latex_paragraph(
            "The package is sufficient for a structured CECL gap assessment, but not for a model-driven review opinion. "
            "The principal blockers are missing execution artifacts, inconsistent horizon and segment documentation, scenario narratives that do not fully align to numeric tables, and overlay support that is not quantitatively reconciled."
        ),
        "",
        _latex_section("Appendix A. Materials Reviewed and Artifact Provenance"),
        _latex_paragraph(
            "This appendix separates bank-supplied materials from Codex-generated review records so the provenance of the assessment is explicit without interrupting the main narrative."
        ),
        _latex_subsection("Bank-Uploaded Input Categories"),
        _latex_grouped_file_sections(uploaded_groups),
        _latex_subsection("Codex-Generated Review Categories"),
        _latex_grouped_file_sections(generated_groups),
        _latex_subsection("Full Provenance Registers"),
        _latex_file_reference_items(
            [
                "outputs/support/artifact_provenance.md",
                "outputs/support/artifact_provenance.json",
                "outputs/support/evidence_ledger.json",
            ]
        ),
        "",
        _latex_section("Appendix B. Executed Procedure Register"),
        *[_latex_procedure_detail(procedure) for procedure in procedure_matrix],
        "",
        _latex_section("Appendix C. Agentic Review Record"),
        _latex_paragraph(
            "This appendix records the staged assessment behavior and the granular action log behind the memo. It is intended to make the review workflow legible without overwhelming the main body."
        ),
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
        _latex_subsection("Planning and Process Files"),
        _latex_file_reference_items(appendix_support_files),
        _latex_subsection("Chronological Procedure Log"),
        procedure_log_sections,
        "",
        _latex_section("Appendix D. Selected Evidence Excerpts"),
        _latex_paragraph(
            "Only text excerpts are reproduced here. Structured output tables remain in the support files listed elsewhere in the memo."
        ),
        evidence_excerpt_sections,
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
            "\\usepackage{fancyvrb}",
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


def _latex_itemize_raw(items: list[str]) -> str:
    lines = ["\\begin{itemize}"]
    lines.extend(f"\\item {item}" for item in items)
    lines.append("\\end{itemize}")
    return "\n".join(lines)


def _latex_enumerate(items: list[str]) -> str:
    lines = ["\\begin{enumerate}"]
    lines.extend(f"\\item {_latex_escape(item)}" for item in items)
    lines.append("\\end{enumerate}")
    return "\n".join(lines)


def _latex_paragraph(text: str) -> str:
    return _latex_escape(text)


def _latex_verbatim_block(text: str) -> str:
    return "\n".join(
        [
            "\\begin{Verbatim}[fontsize=\\small]",
            text.rstrip(),
            "\\end{Verbatim}",
        ]
    )


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


def _latex_artifact_entry(artifact: dict[str, Any]) -> str:
    return (
        f"\\textbf{{{_latex_escape(str(artifact['label']))}}} "
        f"\\texttt{{{_latex_escape(str(artifact['relative_path']))}}} -- "
        f"{_latex_escape(str(artifact['kind_label']))}; "
        f"{_latex_escape(str(artifact['detail']))}; "
        f"{_latex_escape(str(artifact['use_summary']))}"
    )


def _split_procedure_evidence(procedure: dict[str, Any]) -> tuple[list[str], list[str]]:
    bank_inputs: list[str] = []
    codex_outputs: list[str] = []
    for path in procedure.get("evidence", []):
        if str(path).startswith("outputs/support/") or str(path).startswith("outputs/stakeholder/"):
            codex_outputs.append(str(path))
        else:
            bank_inputs.append(str(path))
    return bank_inputs, codex_outputs


def _latex_path_list(paths: list[str]) -> str:
    if not paths:
        return "\\textit{None}"
    return ", ".join(f"\\texttt{{{_latex_escape(path)}}}" for path in paths)


def _latex_file_reference_items(paths: list[str], *, prefix: str = "") -> str:
    if not paths:
        return _latex_itemize_raw(["\\textit{None}"])
    items = [f"{prefix}\\texttt{{{_latex_escape(path)}}}" for path in paths]
    return _latex_itemize_raw(items)


def _latex_grouped_file_sections(groups: list[tuple[str, list[str]]]) -> str:
    sections: list[str] = []
    for title, paths in groups:
        if not paths:
            continue
        sections.extend(
            [
                _latex_subsection(title),
                _latex_file_reference_items(paths),
                "",
            ]
        )
    return "\n".join(part for part in sections if part)


def _latex_procedure_detail(procedure: dict[str, Any]) -> str:
    bank_inputs, derived_outputs = _split_procedure_evidence(procedure)
    lines = [
        _latex_subsection(procedure["procedure_id"] + " - " + procedure["procedure_name"]),
        _latex_paragraph(procedure["objective"]),
        _latex_itemize_raw(
            [
                f"\\textbf{{Status:}} {_latex_escape(procedure['status'].replace('_', ' '))}",
                f"\\textbf{{Why selected:}} {_latex_escape(procedure['selection_rationale'])}",
                f"\\textbf{{Bank-input evidence relied upon:}} {_latex_path_list(bank_inputs)}",
                f"\\textbf{{Codex-generated evidence relied upon:}} {_latex_path_list(derived_outputs)}",
                f"\\textbf{{Codex-generated outputs produced:}} {_latex_path_list(list(procedure['outputs']))}",
                f"\\textbf{{Assessment criteria:}} {_latex_escape(procedure['assessment_criteria'])}",
                f"\\textbf{{Key result:}} {_latex_escape(procedure['key_result'])}",
            ]
        ),
    ]
    blocker = procedure.get("blocker")
    if blocker:
        lines.append(_latex_itemize_raw([f"\\textbf{{Blocking factor:}} {_latex_escape(str(blocker))}"]))
    return "\n".join(lines)


def _latex_log_event(event: dict[str, Any]) -> str:
    return "\n".join(
        [
            _latex_subsection(f"{event['event_id']} - {event['title']}"),
            _latex_itemize_raw(
                [
                    f"\\textbf{{Phase:}} {_latex_escape(event['phase'])}",
                    f"\\textbf{{Related procedure:}} {_latex_escape(event['procedure_id'])}",
                    f"\\textbf{{Action:}} {_latex_escape(event['action'])}",
                    f"\\textbf{{Inputs:}} {_latex_path_list(list(event.get('inputs', [])))}",
                    f"\\textbf{{Outputs:}} {_latex_path_list(list(event.get('outputs', [])))}",
                    f"\\textbf{{Result:}} {_latex_escape(event['result'])}",
                ]
            ),
        ]
    )


def _latex_evidence_excerpt(excerpt: dict[str, Any]) -> str:
    return "\n".join(
        [
            _latex_subsection(f"{excerpt['label']} {excerpt['relative_path']}"),
            _latex_paragraph(excerpt["purpose"]),
            _latex_verbatim_block(excerpt["content"]),
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
