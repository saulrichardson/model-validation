"""Shared case-state mutations for the Codex-driven workbench runtime."""

from __future__ import annotations

from pathlib import Path

from .discovery import inventory_case, summarize_inventory
from .evidence import evidence_refs_from_ids
from .playbook import load_module_catalog
from .reporting import build_report, render_markdown
from .schemas import (
    AgentStage,
    AgentStageRecord,
    CaseRecord,
    CaseStatus,
    DiscoveryStageOutput,
    EvidenceLedgerEntry,
    EvidenceSourceType,
    ExecutionStageOutput,
    PlaybookModule,
    PlaybookModuleDraft,
    PlaybookStageOutput,
    ReportStageOutput,
    TraceEvent,
    WorkflowType,
    utc_now,
)
from .skills import SkillRegistry
from .storage import CaseRepository

STAGE_TO_STATUS = {
    AgentStage.DISCOVERY: CaseStatus.DISCOVERING,
    AgentStage.PLAYBOOK: CaseStatus.RESOLVING,
    AgentStage.EXECUTION: CaseStatus.EXECUTING,
    AgentStage.REPORT: CaseStatus.REPORTING,
}


def build_global_instructions(project_root: Path) -> str:
    instruction_parts: list[str] = []
    root_agents = project_root.parent / "AGENTS.md"
    local_agents = project_root / "AGENTS.md"
    for path in (root_agents, local_agents):
        if path.is_file():
            instruction_parts.append(path.read_text(encoding="utf-8").strip())
    return "\n\n".join(part for part in instruction_parts if part)


def reset_case_for_run(case: CaseRecord) -> None:
    case.failure_message = None
    case.status = CaseStatus.CREATED
    case.trace = []
    case.agent_trace_summary = []
    case.tool_calls = []
    case.evidence_ledger = []
    case.normalized_case_record = None
    case.discovery = None
    case.playbook = []
    case.playbook_decision_log = []
    case.coverage = None
    case.outputs = {}
    case.final_report = None


def seed_artifact_evidence(case: CaseRecord) -> None:
    case.evidence_ledger = []
    for artifact in case.artifacts:
        summary = artifact.excerpt or f"{artifact.kind.value} artifact discovered during inventory."
        case.evidence_ledger.append(
            EvidenceLedgerEntry(
                evidence_id=artifact.artifact_id,
                source_type=EvidenceSourceType.ARTIFACT,
                title=f"Artifact: {artifact.relative_path}",
                summary=summary[:500],
                artifact_id=artifact.artifact_id,
                relative_path=artifact.relative_path,
            )
        )


def prepare_case(case: CaseRecord, repo: CaseRepository) -> dict[str, object]:
    inventory = inventory_case(case)
    seed_artifact_evidence(case)
    inventory_summary = summarize_inventory(inventory)
    inventory_path = repo.dump_output_json(case.case_id, "inventory.json", inventory_summary)
    artifacts_path = repo.dump_output_json(
        case.case_id,
        "inventory_artifacts.json",
        [artifact.model_dump(mode="json") for artifact in case.artifacts],
    )
    case.outputs["inventory"] = inventory_path
    case.outputs["inventory_artifacts"] = artifacts_path
    repo.save_case(case)

    case_dir = repo.create_case_dir(case.case_id)
    return {
        "case": case.model_dump(mode="json"),
        "case_id": case.case_id,
        "name": case.name,
        "source": case.source.value,
        "root_dir": case.root_dir,
        "case_dir": str(case_dir),
        "outputs_dir": str(case_dir / "outputs"),
        "inventory_path": inventory_path,
        "inventory_artifacts_path": artifacts_path,
        "inventory_summary": inventory_summary,
        "artifact_count": len(case.artifacts),
    }


def stage_start(
    case: CaseRecord,
    repo: CaseRepository,
    *,
    stage: AgentStage,
    agent_name: str,
    skill_id: str,
    model: str,
    message: str,
) -> None:
    status = STAGE_TO_STATUS[stage]
    case.status = status
    case.trace.append(TraceEvent(stage=stage.value, message=message, status="running"))
    case.agent_trace_summary.append(
        AgentStageRecord(
            stage=stage,
            agent_name=agent_name,
            skill_id=skill_id,
            model=model,
            status="running",
        )
    )
    repo.save_case(case)


def stage_complete(
    case: CaseRecord,
    repo: CaseRepository,
    *,
    stage: AgentStage,
    stage_output: DiscoveryStageOutput | PlaybookStageOutput | ExecutionStageOutput | ReportStageOutput,
    summary_file: str,
    trace_file: str,
    response_file: str,
    events_file: str,
    usage_file: str,
    usage: dict[str, object],
    response_id: str | None,
) -> None:
    case.outputs[f"{stage.value}_summary"] = summary_file
    case.outputs[f"{stage.value}_trace"] = trace_file
    case.outputs[f"{stage.value}_response"] = response_file
    case.outputs[f"{stage.value}_events"] = events_file
    case.outputs[f"{stage.value}_usage"] = usage_file

    if stage == AgentStage.DISCOVERY:
        assert isinstance(stage_output, DiscoveryStageOutput)
        case.normalized_case_record = stage_output.normalized_case_record
        case.discovery = stage_output.normalized_case_record
        details: dict[str, object] = {
            "case_type": stage_output.normalized_case_record.case_type.value,
            "runtime_mode": stage_output.normalized_case_record.runtime_mode.value,
            "evidence_ids": stage_output.evidence_ids,
        }
    elif stage == AgentStage.PLAYBOOK:
        assert isinstance(stage_output, PlaybookStageOutput)
        case.coverage = stage_output.coverage
        case.playbook = [build_playbook_module(case, module) for module in stage_output.modules]
        case.playbook_decision_log = [module.model_copy(deep=True) for module in case.playbook]
        details = {
            "dominant_workflow": stage_output.coverage.dominant_workflow.value,
            "coverage_ratio": stage_output.coverage.coverage_ratio,
        }
    elif stage == AgentStage.EXECUTION:
        assert isinstance(stage_output, ExecutionStageOutput)
        case.outputs["execution_stage_summary"] = summary_file
        details = {
            "findings": len(stage_output.findings),
            "metrics": len(stage_output.metrics),
        }
    elif stage == AgentStage.REPORT:
        assert isinstance(stage_output, ReportStageOutput)
        report = build_report(case, stage_output.report)
        case.final_report = report
        case.outputs["final_report_markdown"] = repo.dump_output_text(
            case.case_id, "final_report.md", render_markdown(report)
        )
        case.outputs["final_report_json"] = repo.dump_output_json(
            case.case_id, "final_report.json", report.model_dump(mode="json")
        )
        details = {"report_type": report.report_type.value}
    else:
        raise ValueError(f"Unsupported stage for completion: {stage.value}")

    stage_record = latest_stage_record(case, stage)
    if stage_record is None:
        raise ValueError(f"No running stage record found for {stage.value}")
    stage_record.status = "completed"
    stage_record.completed_at = utc_now()
    stage_record.summary = getattr(stage_output, "summary", None)
    stage_record.output_path = trace_file
    stage_record.response_id = response_id
    stage_record.usage = usage
    stage_record.tool_call_ids = [
        record.tool_call_id for record in case.tool_calls if record.stage == stage
    ]

    trace_event = latest_trace_event(case, stage)
    if trace_event is not None:
        trace_event.status = "completed"
        trace_event.completed_at = utc_now()
        trace_event.details = details

    repo.save_case(case)


def stage_failed(
    case: CaseRecord,
    repo: CaseRepository,
    *,
    stage: AgentStage,
    message: str,
    trace_file: str | None = None,
) -> None:
    stage_record = latest_stage_record(case, stage)
    if stage_record is not None:
        stage_record.status = "failed"
        stage_record.completed_at = utc_now()
        stage_record.error_message = message
        if trace_file:
            stage_record.output_path = trace_file

    trace_event = latest_trace_event(case, stage)
    if trace_event is not None:
        trace_event.status = "failed"
        trace_event.completed_at = utc_now()
        trace_event.details = {"error": message}

    repo.save_case(case)


def mark_case_failed(case: CaseRecord, repo: CaseRepository, message: str) -> None:
    case.status = CaseStatus.FAILED
    case.failure_message = message
    case.trace.append(
        TraceEvent(
            stage="failed",
            message=message,
            status="failed",
            completed_at=utc_now(),
        )
    )
    repo.save_case(case)


def mark_case_completed(case: CaseRecord, repo: CaseRepository) -> None:
    case.status = CaseStatus.COMPLETED
    repo.save_case(case)


def latest_stage_record(case: CaseRecord, stage: AgentStage) -> AgentStageRecord | None:
    for record in reversed(case.agent_trace_summary):
        if record.stage == stage:
            return record
    return None


def latest_trace_event(case: CaseRecord, stage: AgentStage) -> TraceEvent | None:
    for event in reversed(case.trace):
        if event.stage == stage.value:
            return event
    return None


def build_playbook_module(case: CaseRecord, draft: PlaybookModuleDraft) -> PlaybookModule:
    return PlaybookModule(
        module_id=draft.module_id,
        title=draft.title,
        status=draft.status,
        rationale=draft.rationale,
        evidence=evidence_refs_from_ids(case, draft.evidence_ids),
        blocked_by=draft.blocked_by,
        recommended_tools=draft.recommended_tools,
    )


def execution_skill_id(case: CaseRecord) -> str:
    if case.coverage and case.coverage.dominant_workflow == WorkflowType.FULL_REVALIDATION:
        return "full-revalidation"
    if case.coverage and case.coverage.dominant_workflow == WorkflowType.BLACK_BOX_BEHAVIORAL_REVIEW:
        return "black-box-review"
    return "conceptual-review"


def playbook_catalog_payload(skills: SkillRegistry) -> dict[str, object]:
    return load_module_catalog(skills).model_dump(mode="json")
