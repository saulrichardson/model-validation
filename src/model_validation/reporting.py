"""Helpers for converting and rendering bank-facing validation reports."""

from __future__ import annotations

from .evidence import evidence_refs_from_ids
from .schemas import CaseRecord, Finding, FindingDraft, ValidationReport, ValidationReportDraft


def build_report(case: CaseRecord, draft: ValidationReportDraft) -> ValidationReport:
    return ValidationReport(
        report_type=draft.report_type,
        title=draft.title,
        executive_summary=draft.executive_summary,
        scope=draft.scope,
        artifacts_reviewed=draft.artifacts_reviewed,
        modules_executed=draft.modules_executed,
        modules_blocked=draft.modules_blocked,
        coverage_statement=draft.coverage_statement,
        coverage_rationale=draft.coverage_rationale,
        key_metrics=draft.key_metrics,
        findings=[build_finding(case, finding) for finding in draft.findings],
        recommended_actions=draft.recommended_actions,
        evidence_requests=draft.evidence_requests,
        narrative=draft.narrative,
    )


def build_finding(case: CaseRecord, finding: FindingDraft) -> Finding:
    return Finding(
        severity=finding.severity,
        title=finding.title,
        summary=finding.summary,
        evidence=evidence_refs_from_ids(case, finding.evidence_ids),
        affected_modules=finding.affected_modules,
    )


def render_markdown(report: ValidationReport) -> str:
    lines: list[str] = [
        f"# {report.title}",
        "",
        "## Executive Summary",
        report.executive_summary,
        "",
        "## Scope",
        *[f"- {item}" for item in report.scope],
        "",
        "## Coverage",
        report.coverage_statement,
    ]
    if report.coverage_rationale:
        lines.append(f"- {report.coverage_rationale}")

    lines.extend(["", "## Findings"])
    if report.findings:
        for finding in report.findings:
            lines.append(f"- [{finding.severity.value.upper()}] {finding.title}: {finding.summary}")
            for evidence in finding.evidence:
                evidence_label = evidence.relative_path or evidence.evidence_id
                lines.append(f"  - Evidence {evidence.evidence_id} ({evidence_label}): {evidence.detail}")
    else:
        lines.append("- No findings were generated from the supported scope.")

    lines.extend(["", "## Recommended Actions"])
    lines.extend(f"- {item}" for item in report.recommended_actions or ["No additional actions."])

    if report.evidence_requests:
        lines.extend(["", "## Evidence Requests"])
        lines.extend(f"- {item}" for item in report.evidence_requests)

    if report.key_metrics:
        lines.extend(["", "## Key Metrics"])
        lines.extend(f"- {metric.label}: {metric.value}" for metric in report.key_metrics)

    lines.extend(["", "## Narrative"])
    lines.extend(f"- {item}" for item in report.narrative)
    return "\n".join(lines) + "\n"
