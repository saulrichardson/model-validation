"""Core models for the validation workbench."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class CaseSource(str, Enum):
    DEMO = "demo"
    UPLOAD = "upload"


class CaseType(str, Enum):
    MATERIAL_CHANGE = "material_change_revalidation"
    VENDOR_BLACK_BOX = "vendor_black_box_review"
    CONCEPTUAL = "conceptual_documentation_review"
    DOCUMENTATION_ONLY = "documentation_only_review"
    NEW_MODEL = "new_model_review"
    UNKNOWN = "unknown"


class RuntimeMode(str, Enum):
    CODE = "runnable_source"
    HARNESS = "runtime_harness"
    CONTAINER = "containerized"
    DOCUMENT_ONLY = "document_only"
    UNKNOWN = "unknown"


class WorkflowType(str, Enum):
    FULL_REVALIDATION = "full_revalidation"
    BLACK_BOX_BEHAVIORAL_REVIEW = "black_box_behavioral_review"
    CONCEPTUAL_READINESS_REVIEW = "conceptual_readiness_review"
    MANUAL_TRIAGE = "manual_triage"


class ArtifactKind(str, Enum):
    CODE = "code"
    DOCUMENT = "document"
    DATASET = "dataset"
    METRICS = "metrics"
    MODEL = "model"
    NOTEBOOK = "notebook"
    CONFIG = "config"
    CONTAINER = "container"
    BINARY = "binary"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class CaseStatus(str, Enum):
    CREATED = "created"
    DISCOVERING = "discovering"
    RESOLVING = "resolving"
    EXECUTING = "executing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStage(str, Enum):
    DISCOVERY = "discovery"
    PLAYBOOK = "playbook"
    EXECUTION = "execution"
    REPORT = "report"
    SIDECAR = "sidecar"


class ModuleStatus(str, Enum):
    EXECUTABLE = "executable"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class FindingSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReportType(str, Enum):
    FULL_REVALIDATION = "full_revalidation_memo"
    PARTIAL_VALIDATION = "partial_validation_report"
    CONCEPTUAL_REVIEW = "conceptual_readiness_memo"


class EvidenceSourceType(str, Enum):
    ARTIFACT = "artifact"
    TOOL = "tool"
    SIDECAR = "sidecar"


class ToolTransport(str, Enum):
    LOCAL = "local"
    GATEWAY_SIDECAR = "gateway_sidecar"


class ArtifactRecord(BaseModel):
    artifact_id: str
    relative_path: str
    absolute_path: str
    kind: ArtifactKind
    size_bytes: int
    mime_type: str | None = None
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    excerpt: str | None = None


class DataProfile(BaseModel):
    row_count: int | None = None
    column_count: int | None = None
    target_column: str | None = None
    numeric_columns: list[str] = Field(default_factory=list)
    categorical_columns: list[str] = Field(default_factory=list)
    missing_rate_by_column: dict[str, float] = Field(default_factory=dict)
    highlights: list[str] = Field(default_factory=list)


class EvidenceLedgerEntry(BaseModel):
    evidence_id: str
    source_type: EvidenceSourceType
    title: str
    summary: str
    artifact_id: str | None = None
    relative_path: str | None = None
    output_path: str | None = None
    stage: AgentStage | None = None
    tool_name: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceRef(BaseModel):
    evidence_id: str
    detail: str
    title: str | None = None
    relative_path: str | None = None


class TraceEvent(BaseModel):
    stage: str
    message: str
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    status: str = "running"
    details: dict[str, Any] | None = None


class NormalizedCaseRecord(BaseModel):
    case_type: CaseType = CaseType.UNKNOWN
    model_family: str = "unknown"
    decision_context: str = "unknown"
    runtime_mode: RuntimeMode = RuntimeMode.UNKNOWN
    available_artifact_types: list[str] = Field(default_factory=list)
    available_evidence: list[str] = Field(default_factory=list)
    likely_execution_path: WorkflowType = WorkflowType.MANUAL_TRIAGE
    gaps: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    artifact_highlights: list[str] = Field(default_factory=list)
    key_artifact_ids: list[str] = Field(default_factory=list)
    data_profile: DataProfile | None = None
    confidence_statement: str = "Evidence-limited discovery."

    @field_validator("likely_execution_path", mode="before")
    @classmethod
    def coerce_workflow(cls, value: WorkflowType | str) -> WorkflowType:
        return normalize_workflow(value)


class PlaybookModule(BaseModel):
    module_id: str
    title: str
    status: ModuleStatus
    rationale: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    recommended_tools: list[str] = Field(default_factory=list)


class CoverageSummary(BaseModel):
    executable: int = 0
    partial: int = 0
    blocked: int = 0
    coverage_ratio: float = 0.0
    dominant_workflow: WorkflowType = WorkflowType.MANUAL_TRIAGE
    coverage_rationale: str = ""

    @field_validator("dominant_workflow", mode="before")
    @classmethod
    def coerce_workflow(cls, value: WorkflowType | str) -> WorkflowType:
        return normalize_workflow(value)


class ExecutionMetric(BaseModel):
    label: str
    value: str
    detail: str | None = None


class Finding(BaseModel):
    severity: FindingSeverity
    title: str
    summary: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    affected_modules: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    report_type: ReportType
    title: str
    executive_summary: str
    scope: list[str] = Field(default_factory=list)
    artifacts_reviewed: list[str] = Field(default_factory=list)
    modules_executed: list[str] = Field(default_factory=list)
    modules_blocked: list[str] = Field(default_factory=list)
    coverage_statement: str
    coverage_rationale: str = ""
    key_metrics: list[ExecutionMetric] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)
    narrative: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class FindingDraft(BaseModel):
    severity: FindingSeverity
    title: str
    summary: str
    evidence_ids: list[str] = Field(default_factory=list)
    affected_modules: list[str] = Field(default_factory=list)


class PlaybookModuleDraft(BaseModel):
    module_id: str
    title: str
    status: ModuleStatus
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    recommended_tools: list[str] = Field(default_factory=list)


class ValidationReportDraft(BaseModel):
    report_type: ReportType
    title: str
    executive_summary: str
    scope: list[str] = Field(default_factory=list)
    artifacts_reviewed: list[str] = Field(default_factory=list)
    modules_executed: list[str] = Field(default_factory=list)
    modules_blocked: list[str] = Field(default_factory=list)
    coverage_statement: str
    coverage_rationale: str = ""
    key_metrics: list[ExecutionMetric] = Field(default_factory=list)
    findings: list[FindingDraft] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)
    narrative: list[str] = Field(default_factory=list)


class DiscoveryStageOutput(BaseModel):
    summary: str
    normalized_case_record: NormalizedCaseRecord
    evidence_ids: list[str] = Field(default_factory=list)


class PlaybookStageOutput(BaseModel):
    summary: str
    coverage: CoverageSummary
    modules: list[PlaybookModuleDraft] = Field(default_factory=list)


class ExecutionStageOutput(BaseModel):
    summary: str
    findings: list[FindingDraft] = Field(default_factory=list)
    metrics: list[ExecutionMetric] = Field(default_factory=list)
    narrative: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)


class ReportStageOutput(BaseModel):
    summary: str
    report: ValidationReportDraft


class ToolCallRecord(BaseModel):
    tool_call_id: str
    call_id: str
    stage: AgentStage
    tool_name: str
    transport: ToolTransport
    arguments: dict[str, Any] = Field(default_factory=dict)
    output_summary: str = ""
    output_path: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    status: str = "completed"
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    error_message: str | None = None


class AgentStageRecord(BaseModel):
    stage: AgentStage
    agent_name: str
    skill_id: str
    model: str
    response_id: str | None = None
    status: str = "running"
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    summary: str | None = None
    output_path: str | None = None
    tool_call_ids: list[str] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None


class CaseRecord(BaseModel):
    case_id: str
    name: str
    source: CaseSource
    source_id: str | None = None
    root_dir: str
    uploaded_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    status: CaseStatus = CaseStatus.CREATED
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    evidence_ledger: list[EvidenceLedgerEntry] = Field(default_factory=list)
    normalized_case_record: NormalizedCaseRecord | None = None
    discovery: NormalizedCaseRecord | None = None
    playbook: list[PlaybookModule] = Field(default_factory=list)
    playbook_decision_log: list[PlaybookModule] = Field(default_factory=list)
    coverage: CoverageSummary | None = None
    trace: list[TraceEvent] = Field(default_factory=list)
    agent_trace_summary: list[AgentStageRecord] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    outputs: dict[str, str] = Field(default_factory=dict)
    final_report: ValidationReport | None = None
    failure_message: str | None = None


class DemoCaseDescriptor(BaseModel):
    demo_id: str
    title: str
    description: str
    expected_case_type: CaseType
    package_dir: str
    highlights: list[str] = Field(default_factory=list)
    expected_workflow: WorkflowType | None = None
    expected_report_type: ReportType | None = None
    minimum_coverage_ratio: float | None = Field(default=None, ge=0.0, le=1.0)


CaseRecord.model_rebuild()


def normalize_workflow(value: WorkflowType | str) -> WorkflowType:
    if isinstance(value, WorkflowType):
        return value

    lowered = str(value).strip().lower()
    if "full_revalidation" in lowered or "revalidation workflow" in lowered:
        return WorkflowType.FULL_REVALIDATION
    if "black_box_behavioral_review" in lowered or "black-box" in lowered:
        return WorkflowType.BLACK_BOX_BEHAVIORAL_REVIEW
    if "conceptual_readiness_review" in lowered or "conceptual" in lowered:
        return WorkflowType.CONCEPTUAL_READINESS_REVIEW
    return WorkflowType.MANUAL_TRIAGE
