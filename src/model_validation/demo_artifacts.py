"""Artifact-first summaries for demo-oriented workbench runs."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from .schemas import AgentStage, CaseRecord
from .storage import CaseRepository


def build_case_demo_summary(
    case: CaseRecord,
    *,
    stop_after: AgentStage,
    preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    discovery = _read_json_output(case.outputs.get("discovery_summary"))
    playbook = _read_json_output(case.outputs.get("playbook_summary"))
    execution = _read_json_output(case.outputs.get("execution_summary"))
    report = _read_json_output(case.outputs.get("report_summary"))

    tool_calls_by_stage = dict(Counter(call.stage.value for call in case.tool_calls))
    tool_calls_by_transport = dict(Counter(call.transport.value for call in case.tool_calls))

    coverage = case.coverage.model_dump(mode="json") if case.coverage else None
    normalized = case.normalized_case_record.model_dump(mode="json") if case.normalized_case_record else None
    final_report = case.final_report.model_dump(mode="json") if case.final_report else None

    findings = _summary_findings(case, execution)
    evidence_requests = _summary_evidence_requests(case, execution)

    payload: dict[str, Any] = {
        "case_id": case.case_id,
        "name": case.name,
        "source": case.source.value,
        "source_id": case.source_id,
        "status": case.status.value,
        "stop_after": stop_after.value,
        "root_dir": case.root_dir,
        "updated_at": case.updated_at.isoformat(),
        "normalized_case_record": normalized,
        "coverage": coverage,
        "stage_records": [_stage_payload(record) for record in case.agent_trace_summary],
        "tool_calls_by_stage": tool_calls_by_stage,
        "tool_calls_by_transport": tool_calls_by_transport,
        "tool_call_count": len(case.tool_calls),
        "findings": findings,
        "evidence_requests": evidence_requests,
        "preflight": preflight,
        "output_files": _important_outputs(case),
        "final_report": final_report,
        "stage_outputs": {
            "discovery": discovery,
            "playbook": playbook,
            "execution": execution,
            "report": report,
        },
        "notes": _summary_notes(case, stop_after),
    }
    return payload


def persist_case_demo_summary(
    repo: CaseRepository,
    case: CaseRecord,
    *,
    stop_after: AgentStage,
    preflight: dict[str, Any] | None = None,
) -> dict[str, str]:
    payload = build_case_demo_summary(case, stop_after=stop_after, preflight=preflight)
    json_path = repo.dump_output_json(case.case_id, "demo/case_summary.json", payload)
    markdown_path = repo.dump_output_text(
        case.case_id,
        "demo/case_summary.md",
        render_case_demo_summary(payload),
    )
    case.outputs["demo_case_summary_json"] = json_path
    case.outputs["demo_case_summary_markdown"] = markdown_path
    repo.save_case(case)
    return {"json": json_path, "markdown": markdown_path}


def persist_sweep_summary(
    storage_dir: Path,
    *,
    label: str,
    case_summaries: list[dict[str, Any]],
    preflight: dict[str, Any] | None = None,
) -> dict[str, str]:
    run_dir = storage_dir / "demo_runs" / label
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "label": label,
        "generated_at": datetime.now(UTC).isoformat(),
        "preflight": preflight,
        "cases": case_summaries,
    }
    json_path = run_dir / "summary.json"
    markdown_path = run_dir / "summary.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown_path.write_text(render_sweep_summary(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def render_case_demo_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['name']}",
        "",
        f"- Case ID: {summary['case_id']}",
        f"- Source: {summary['source']}",
        f"- Source ID: {summary.get('source_id') or 'n/a'}",
        f"- Status: {summary['status']}",
        f"- Stop After: {summary['stop_after']}",
    ]

    coverage = summary.get("coverage") or {}
    normalized = summary.get("normalized_case_record") or {}
    if normalized or coverage:
        lines.extend(
            [
                "",
                "## Workflow",
                f"- Case Type: {normalized.get('case_type', 'unknown')}",
                f"- Runtime Mode: {normalized.get('runtime_mode', 'unknown')}",
                f"- Likely Execution Path: {normalized.get('likely_execution_path', 'unknown')}",
                f"- Dominant Workflow: {coverage.get('dominant_workflow', 'unknown')}",
                f"- Coverage Ratio: {coverage.get('coverage_ratio', 'n/a')}",
                f"- Executable / Partial / Blocked: {coverage.get('executable', 0)} / {coverage.get('partial', 0)} / {coverage.get('blocked', 0)}",
            ]
        )

    lines.extend(["", "## Stage Trace"])
    for record in summary.get("stage_records", []):
        lines.append(
            f"- {record['stage']}: {record['status']} ({record['elapsed_seconds']}s) {record.get('summary') or ''}".rstrip()
        )

    lines.extend(
        [
            "",
            "## Tool Usage",
            f"- Total Tool Calls: {summary.get('tool_call_count', 0)}",
            f"- By Stage: {json.dumps(summary.get('tool_calls_by_stage', {}), sort_keys=True)}",
            f"- By Transport: {json.dumps(summary.get('tool_calls_by_transport', {}), sort_keys=True)}",
        ]
    )

    findings = summary.get("findings") or []
    lines.extend(["", "## Findings"])
    if findings:
        for finding in findings:
            evidence = ", ".join(finding.get("evidence_ids", []))
            lines.append(
                f"- [{finding.get('severity', 'info').upper()}] {finding.get('title')}: {finding.get('summary')}"
            )
            if evidence:
                lines.append(f"  Evidence: {evidence}")
    else:
        lines.append("- No findings captured yet at the selected stop stage.")

    evidence_requests = summary.get("evidence_requests") or []
    if evidence_requests:
        lines.extend(["", "## Evidence Requests"])
        lines.extend(f"- {item}" for item in evidence_requests)

    notes = summary.get("notes") or []
    if notes:
        lines.extend(["", "## Notes"])
        lines.extend(f"- {item}" for item in notes)

    lines.extend(["", "## Output Files"])
    for key, value in (summary.get("output_files") or {}).items():
        lines.append(f"- {key}: {value}")

    return "\n".join(lines) + "\n"


def render_sweep_summary(summary: dict[str, Any]) -> str:
    lines = [
        f"# Demo Sweep {summary['label']}",
        "",
        f"- Generated At: {summary['generated_at']}",
    ]
    preflight = summary.get("preflight")
    if preflight:
        lines.append(f"- Preflight Event: {preflight.get('event', 'unknown')}")
        lines.append(f"- Preflight Model: {preflight.get('model', 'unknown')}")

    lines.extend(["", "## Cases"])
    for case in summary.get("cases", []):
        coverage = case.get("coverage") or {}
        report = case.get("final_report") or {}
        lines.extend(
            [
                f"- {case['name']} ({case['case_id']}):",
                f"  Workflow: {coverage.get('dominant_workflow', 'unknown')}",
                f"  Coverage: {coverage.get('coverage_ratio', 'n/a')}",
                f"  Report Type: {report.get('report_type', 'n/a')}",
                f"  Status: {case['status']}",
            ]
        )
        mismatches = case.get("mismatches") or []
        for mismatch in mismatches:
            lines.append(f"  Mismatch: {mismatch}")
    return "\n".join(lines) + "\n"


def _read_json_output(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.is_file():
        return None
    return cast(dict[str, Any], json.loads(file_path.read_text(encoding="utf-8")))


def _summary_findings(case: CaseRecord, execution_output: dict[str, Any] | None) -> list[dict[str, Any]]:
    if case.final_report:
        return [
            {
                "severity": finding.severity.value,
                "title": finding.title,
                "summary": finding.summary,
                "evidence_ids": [evidence.evidence_id for evidence in finding.evidence],
                "affected_modules": finding.affected_modules,
            }
            for finding in case.final_report.findings
        ]
    if not execution_output:
        return []
    return list(execution_output.get("findings", []))


def _summary_evidence_requests(
    case: CaseRecord,
    execution_output: dict[str, Any] | None,
) -> list[str]:
    if case.final_report:
        return list(case.final_report.evidence_requests)
    if not execution_output:
        return []
    requests = execution_output.get("evidence_requests", [])
    return list(requests) if isinstance(requests, list) else []


def _important_outputs(case: CaseRecord) -> dict[str, str]:
    keys = [
        "inventory",
        "inventory_artifacts",
        "discovery_summary",
        "playbook_summary",
        "execution_summary",
        "report_summary",
        "final_report_json",
        "final_report_markdown",
        "codex_runner_log",
        "demo_orchestration_log",
        "demo_case_summary_json",
        "demo_case_summary_markdown",
    ]
    return {key: case.outputs[key] for key in keys if key in case.outputs}


def _stage_payload(record: Any) -> dict[str, Any]:
    elapsed = None
    if record.completed_at is not None:
        elapsed = round((record.completed_at - record.started_at).total_seconds(), 2)
    return {
        "stage": record.stage.value,
        "status": record.status,
        "model": record.model,
        "skill_id": record.skill_id,
        "summary": record.summary,
        "started_at": record.started_at.isoformat(),
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
        "elapsed_seconds": elapsed,
        "tool_call_ids": list(record.tool_call_ids),
        "output_path": record.output_path,
        "error_message": record.error_message,
    }


def _summary_notes(case: CaseRecord, stop_after: AgentStage) -> list[str]:
    notes: list[str] = []
    if stop_after != AgentStage.REPORT:
        notes.append(
            f"Run intentionally stopped after {stop_after.value}; case status reflects the last completed stage rather than a final report outcome."
        )
    if case.failure_message:
        notes.append(case.failure_message)
    return notes
