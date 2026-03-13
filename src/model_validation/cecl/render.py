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
    scenario_summary: pd.DataFrame,
    sensitivity_results: pd.DataFrame,
    findings: list[dict[str, Any]],
    doc_crosscheck: dict[str, Any],
) -> str:
    scenario_rows = [
        [row["scenario_name"].title(), _money(row["reserve_amount"]), _pct(row["reserve_rate"])]
        for _, row in scenario_summary.iterrows()
    ]
    sensitivity_rows = [
        [
            row["test_type"].replace("_", " ").title(),
            str(row["setting"]),
            row["scenario_name"].title(),
            _money(row["reserve_amount"]),
        ]
        for _, row in sensitivity_results.head(8).iterrows()
    ]

    executive_summary = (
        f"This review covers {spec.bank_name}'s {spec.portfolio_name} package. "
        f"The reserve engine was runnable, baseline reserve results were reproducible within tolerance, "
        f"and scenario reruns plus targeted sensitivities were completed. "
        f"Two material issues were identified: a documented-versus-implemented forecast/reversion mismatch "
        f"and a segment-level severe-scenario anomaly tied to scenario and overlay interaction."
    )

    return _wrap_latex_document(
        title=f"{spec.bank_name} CECL Review Memo",
        body="\n".join(
            [
                "\\section*{Executive Summary}",
                _latex_paragraph(executive_summary),
                "\\section*{Package Reviewed}",
                _latex_itemize(
                    [
                        "Runnable CECL reserve engine and synthetic loan-level portfolio",
                        "Baseline, adverse, and severe scenario tables",
                        "Methodology, model overview, scenario assumptions, and overlay memo",
                        "Prior baseline reserve output and governance/supporting notes",
                    ]
                ),
                "\\section*{Review Work Performed}",
                _latex_itemize(
                    [
                        "Reproduced the supplied baseline reserve output and compared results at loan and segment level",
                        "Ran baseline, adverse, and severe reserve projections using the supplied CECL engine",
                        "Executed sensitivity analysis for forecast horizon, reversion speed, macro severity, and overlay magnitude",
                        "Cross-checked documented methodology, scenario assumptions, and overlay posture against implementation behavior",
                    ]
                ),
                "\\section*{Scenario Results}",
                _latex_table(["Scenario", "Reserve", "Reserve Rate"], scenario_rows),
                "\\section*{Key Sensitivity Results}",
                _latex_table(["Test", "Setting", "Scenario", "Reserve"], sensitivity_rows),
                "\\section*{Findings}",
                _latex_itemize([_finding_sentence(item) for item in findings]),
                "\\section*{Overall Assessment}",
                _latex_paragraph(
                    "The package supported a substantive CECL review. Overall reserve direction was reasonable at portfolio level, "
                    "but the documented forecast/reversion treatment does not match the engine configuration and one segment exhibits "
                    "counterintuitive severe-scenario behavior. Remediation should address documentation alignment and segment-level scenario governance before approval without qualification."
                ),
                "\\section*{Recommended Actions}",
                _latex_itemize(
                    [
                        "Align methodology and model overview documents to the implemented 6-quarter forecast and 2-quarter reversion, or update the engine to match documented policy.",
                        f"Investigate the {spec.quantitative_anomaly_segment.replace('_', ' ')} severe-scenario result and the related overlay/scenario interaction before relying on the severe output for governance reporting.",
                        f"Reconcile overlay documentation to the actual overlay cap of {doc_crosscheck['actual_overlay_cap_bps']:.1f} bps and restate governance thresholds accordingly.",
                    ]
                ),
            ]
        ),
    )


def render_gap_assessment_latex(
    spec: GapAssessmentSpec,
    scenario_summary: pd.DataFrame,
    findings: list[dict[str, Any]],
    evidence_requests: list[str],
) -> str:
    scenario_rows = [
        [row["scenario_name"].title(), _money(row["reserve_amount"]), _pct(row["reserve_rate"])]
        for _, row in scenario_summary.iterrows()
    ]
    executive_summary = (
        f"This assessment covers {spec.bank_name}'s {spec.portfolio_name} package. "
        f"The materials support a meaningful documentation-led review, but the absence of a runnable reserve engine and lineaged execution evidence prevents an execution-based opinion. "
        "The review therefore focuses on package sufficiency, scenario consistency, segment reconciliation, and qualitative overlay support."
    )

    return _wrap_latex_document(
        title=f"{spec.bank_name} CECL Gap Assessment",
        body="\n".join(
            [
                "\\section*{Executive Summary}",
                _latex_paragraph(executive_summary),
                "\\section*{Package Reviewed}",
                _latex_itemize(
                    [
                        "Methodology, model overview, scenario assumptions, overlay memo, and prior review note",
                        "Scenario tables and provided reserve outputs",
                        "Evidence request log and governance/gap-tracker materials",
                    ]
                ),
                "\\section*{Work Performed}",
                _latex_itemize(
                    [
                        "Inventoried the supplied package and identified execution blockers",
                        "Compared scenario narrative to supplied scenario tables",
                        "Compared documented segment structure to the provided reserve outputs",
                        "Assessed whether overlay documentation was consistent with the supplied reserve bridge",
                    ]
                ),
                "\\section*{Provided Reserve Outputs}",
                _latex_table(["Scenario", "Reserve", "Reserve Rate"], scenario_rows),
                "\\section*{Key Gaps and Findings}",
                _latex_itemize([_finding_sentence(item) for item in findings]),
                "\\section*{Coverage Position}",
                _latex_paragraph(
                    "This package supports a documentation-led gap assessment only. Baseline reproduction, scenario reruns, sensitivity testing, and implementation validation remain blocked pending runnable model artifacts and execution lineage."
                ),
                "\\section*{Evidence Requests}",
                _latex_itemize(evidence_requests),
                "\\section*{Overall Assessment}",
                _latex_paragraph(
                    "The package is sufficient for a structured gap assessment but not for a model-driven CECL review opinion. "
                    "The primary blockers are missing implementation artifacts, unresolved scenario-definition inconsistencies, and overlay support that is not quantitatively reconciled."
                ),
            ]
        ),
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
            "\\usepackage[T1]{fontenc}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{lmodern}",
            "\\setlength{\\parskip}{0.6em}",
            "\\setlength{\\parindent}{0pt}",
            f"\\title{{{_latex_escape(title)}}}",
            "\\date{March 13, 2026}",
            "\\begin{document}",
            "\\maketitle",
            body,
            "\\end{document}",
        ]
    )


def _latex_table(headers: list[str], rows: list[list[str]]) -> str:
    cols = " | ".join(["p{0.24\\textwidth}" for _ in headers])
    lines = [
        f"\\begin{{tabular}}{{{cols}}}",
        "\\toprule",
        " & ".join(_latex_escape(item) for item in headers) + " \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(_latex_escape(cell) for cell in row) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def _latex_itemize(items: list[str]) -> str:
    lines = ["\\begin{itemize}"]
    lines.extend(f"\\item {_latex_escape(item)}" for item in items)
    lines.append("\\end{itemize}")
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
