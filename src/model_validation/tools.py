"""Tool registry for the LLM-first validation workbench."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, Field

from .discovery import (
    InventoryContext,
    capability_hints,
    primary_data_profile,
    summarize_inventory,
)
from .execution import AnalysisOutcome, ValidationAnalyzer
from .models import ChatRequest, Message, Role
from .schemas import AgentStage, ArtifactKind, ArtifactRecord, EvidenceSourceType, ToolTransport
from .settings import Settings
from .sidecar import GatewaySidecarService
from .storage import CaseRepository


class EmptyToolInput(BaseModel):
    pass


class ArtifactInput(BaseModel):
    artifact_id: str


class ArtifactTextInput(BaseModel):
    artifact_id: str
    max_chars: int = Field(ge=500, le=50000)


class MethodologyBenchmarkInput(BaseModel):
    artifact_id: str
    benchmark_focus: str = Field(min_length=10)


class DocumentationBenchmarkInput(BaseModel):
    artifact_ids: list[str] = Field(default_factory=list, max_length=12)
    benchmark_focus: str = Field(
        default="validation evidence sufficiency, documentation consistency, and execution readiness",
        min_length=10,
    )


class ToolEvidenceDraft(BaseModel):
    title: str
    summary: str
    source_type: EvidenceSourceType
    relative_path: str | None = None
    output_path: str | None = None


class ToolInvocationResult(BaseModel):
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence: list[ToolEvidenceDraft] = Field(default_factory=list)
    output_path: str | None = None


class MethodologyBenchmarkOutput(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)


class DocumentationPackBenchmarkOutput(BaseModel):
    summary: str
    readiness_assessment: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence_requests: list[str] = Field(default_factory=list)
    recommended_modules: list[str] = Field(default_factory=list)


class RegisteredTool:
    def __init__(
        self,
        *,
        name: str,
        description: str,
        input_model: type[BaseModel],
        transport: ToolTransport,
        handler: Callable[[Any], Any],
    ) -> None:
        self.name = name
        self.description = description
        self.input_model = input_model
        self.transport = transport
        self.handler = handler

    def as_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": _strict_json_schema(self.input_model.model_json_schema()),
            "strict": True,
        }


class WorkbenchToolbox:
    def __init__(
        self,
        *,
        inventory: InventoryContext,
        repo: CaseRepository,
        settings: Settings,
        gateway: GatewaySidecarService,
    ) -> None:
        self.inventory = inventory
        self.repo = repo
        self.settings = settings
        self.gateway = gateway
        self.analyzer = ValidationAnalyzer(inventory, repo)

    def tools_for_stage(self, stage: AgentStage) -> list[RegisteredTool]:
        discovery_tools = [
            RegisteredTool(
                name="list_artifacts",
                description="List the discovered artifacts, tags, sizes, and excerpts for the uploaded case.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._list_artifacts,
            ),
            RegisteredTool(
                name="read_artifact_excerpt",
                description="Read the stored excerpt and metadata for a single artifact by id.",
                input_model=ArtifactInput,
                transport=ToolTransport.LOCAL,
                handler=self._read_artifact_excerpt,
            ),
            RegisteredTool(
                name="read_artifact_text",
                description="Read the full text of a text-like artifact, truncated to a caller-specified maximum.",
                input_model=ArtifactTextInput,
                transport=ToolTransport.LOCAL,
                handler=self._read_artifact_text,
            ),
            RegisteredTool(
                name="profile_dataset",
                description="Return the deterministic profile of a discovered dataset artifact.",
                input_model=ArtifactInput,
                transport=ToolTransport.LOCAL,
                handler=self._profile_dataset,
            ),
            RegisteredTool(
                name="inspect_runtime_assets",
                description="Summarize runtime-related assets such as baseline code, candidate code, harnesses, datasets, and capability hints.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._inspect_runtime_assets,
            ),
        ]
        execution_tools = [
            RegisteredTool(
                name="run_material_model_pair",
                description="Execute the supplied baseline and candidate model scripts against the primary validation dataset.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._run_material_model_pair,
            ),
            RegisteredTool(
                name="run_vendor_runtime_harness",
                description="Execute the supplied vendor runtime harness against the smoke-test input batch.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._run_vendor_runtime_harness,
            ),
            RegisteredTool(
                name="compare_scored_outputs",
                description="Compare baseline and candidate scored outputs for approval, AUC, and thin-file shifts.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._compare_scored_outputs,
            ),
            RegisteredTool(
                name="review_material_behavior",
                description="Summarize channel-level behavioral shifts between candidate and baseline outputs.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._review_material_behavior,
            ),
            RegisteredTool(
                name="review_vendor_behavior",
                description="Profile vendor runtime outputs across channels and score distributions.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._review_vendor_behavior,
            ),
            RegisteredTool(
                name="check_document_consistency",
                description="Compare methodology and related documents against the discovered implementation and conceptual materials.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._check_document_consistency,
            ),
            RegisteredTool(
                name="review_reason_code_mapping",
                description="Check reason-code mappings against active runtime outputs and documented feature inventories.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._review_reason_code_mapping,
            ),
            RegisteredTool(
                name="summarize_data_quality",
                description="Profile the primary supplied dataset for row counts, columns, and missingness concentrations.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._summarize_data_quality,
            ),
            RegisteredTool(
                name="review_conceptual_conditions",
                description="Translate prior validation conditions and current documentation references into an evidence-request list.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._review_conceptual_conditions,
            ),
            RegisteredTool(
                name="run_sensitivity_analysis",
                description="Run threshold sweeps, stress scenarios, and directional checks for a material baseline/candidate model pair.",
                input_model=EmptyToolInput,
                transport=ToolTransport.LOCAL,
                handler=self._run_sensitivity_analysis,
            ),
        ]
        report_sidecar = [
            RegisteredTool(
                name="benchmark_methodology_doc",
                description="Use the gateway sidecar to benchmark a supplied methodology document against validation-documentation best-practice expectations.",
                input_model=MethodologyBenchmarkInput,
                transport=ToolTransport.GATEWAY_SIDECAR,
                handler=self._benchmark_methodology_doc,
            ),
            RegisteredTool(
                name="benchmark_documentation_pack",
                description="Use the gateway sidecar to benchmark the supplied documentation pack against validation-readiness expectations.",
                input_model=DocumentationBenchmarkInput,
                transport=ToolTransport.GATEWAY_SIDECAR,
                handler=self._benchmark_documentation_pack,
            )
        ]

        if stage == AgentStage.DISCOVERY:
            return discovery_tools
        if stage == AgentStage.PLAYBOOK:
            return discovery_tools
        if stage == AgentStage.EXECUTION:
            return discovery_tools + execution_tools + report_sidecar
        if stage == AgentStage.REPORT:
            return discovery_tools + execution_tools + report_sidecar
        return discovery_tools

    def get_tool(self, stage: AgentStage, name: str) -> RegisteredTool:
        for tool in self.tools_for_stage(stage):
            if tool.name == name:
                return tool
        raise KeyError(f"Unknown tool '{name}' for stage '{stage.value}'")

    def _list_artifacts(self, _: EmptyToolInput) -> ToolInvocationResult:
        artifacts = [
            {
                "artifact_id": artifact.artifact_id,
                "relative_path": artifact.relative_path,
                "kind": artifact.kind.value,
                "size_bytes": artifact.size_bytes,
                "tags": artifact.tags,
                "excerpt": artifact.excerpt,
            }
            for artifact in self.inventory.artifact_index.values()
        ]
        return ToolInvocationResult(
            summary=f"Listed {len(artifacts)} artifacts.",
            payload={"artifacts": artifacts, "inventory_summary": summarize_inventory(self.inventory)},
        )

    def _read_artifact_excerpt(self, args: ArtifactInput) -> ToolInvocationResult:
        artifact = self.inventory.get_artifact(args.artifact_id)
        return ToolInvocationResult(
            summary=f"Loaded excerpt for {artifact.relative_path}.",
            payload={
                "artifact": {
                    "artifact_id": artifact.artifact_id,
                    "relative_path": artifact.relative_path,
                    "kind": artifact.kind.value,
                    "tags": artifact.tags,
                    "excerpt": artifact.excerpt,
                }
            },
        )

    def _read_artifact_text(self, args: ArtifactTextInput) -> ToolInvocationResult:
        artifact = self.inventory.get_artifact(args.artifact_id)
        text = Path(artifact.absolute_path).read_text(encoding="utf-8", errors="ignore")
        truncated = text[: args.max_chars]
        return ToolInvocationResult(
            summary=f"Read full text for {artifact.relative_path} truncated to {len(truncated)} characters.",
            payload={
                "artifact": {
                    "artifact_id": artifact.artifact_id,
                    "relative_path": artifact.relative_path,
                    "kind": artifact.kind.value,
                    "tags": artifact.tags,
                },
                "text": truncated,
                "truncated": len(truncated) < len(text),
            },
        )

    def _profile_dataset(self, args: ArtifactInput) -> ToolInvocationResult:
        artifact = self.inventory.get_artifact(args.artifact_id)
        profile = self.inventory.dataset_profiles.get(args.artifact_id)
        if profile is None:
            raise ValueError(f"Artifact {artifact.relative_path} does not have a dataset profile.")
        return ToolInvocationResult(
            summary=f"Profiled dataset {artifact.relative_path}.",
            payload={
                "artifact": {
                    "artifact_id": artifact.artifact_id,
                    "relative_path": artifact.relative_path,
                },
                "profile": profile.model_dump(mode="json"),
            },
        )

    def _inspect_runtime_assets(self, _: EmptyToolInput) -> ToolInvocationResult:
        primary_profile = primary_data_profile(self.inventory)
        return ToolInvocationResult(
            summary="Summarized runtime-related assets and capability hints.",
            payload={
                "capability_hints": capability_hints(self.inventory),
                "runtime_assets": self.analyzer.inspect_runtime_assets(),
                "primary_data_profile": (
                    primary_profile.model_dump(mode="json") if primary_profile is not None else None
                ),
            },
        )

    def _run_material_model_pair(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.run_material_model_pair())

    def _run_vendor_runtime_harness(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.run_vendor_runtime_harness())

    def _compare_scored_outputs(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.compare_scored_outputs())

    def _review_material_behavior(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.review_material_behavior())

    def _review_vendor_behavior(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.review_vendor_behavior())

    def _check_document_consistency(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.check_document_consistency())

    def _review_reason_code_mapping(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.review_reason_code_mapping())

    def _summarize_data_quality(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.summarize_data_quality())

    def _review_conceptual_conditions(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.review_conceptual_conditions())

    def _run_sensitivity_analysis(self, _: EmptyToolInput) -> ToolInvocationResult:
        return self._analysis_result(self.analyzer.run_sensitivity_analysis())

    async def _benchmark_methodology_doc(
        self, args: MethodologyBenchmarkInput
    ) -> ToolInvocationResult:
        if not self.settings.workbench_enable_gateway_sidecars:
            raise RuntimeError("Gateway sidecars are disabled by configuration.")

        artifact = self.inventory.get_artifact(args.artifact_id)
        document_text = Path(artifact.absolute_path).read_text(encoding="utf-8", errors="ignore")
        schema = MethodologyBenchmarkOutput.model_json_schema()
        request = ChatRequest(
            provider="openai",
            model=self.settings.workbench_judge_model,
            messages=[
                Message(
                    role=Role.SYSTEM,
                    content=(
                        "You are a validation documentation benchmarking sidecar. "
                        "Evaluate the supplied methodology document against current bank model validation "
                        "documentation expectations. Focus on evidence sufficiency, internal consistency, "
                        "scope clarity, and stated limitations. Return strict JSON only."
                    ),
                ),
                Message(
                    role=Role.USER,
                    content=(
                        f"Benchmark focus: {args.benchmark_focus}\n\n"
                        f"Artifact path: {artifact.relative_path}\n\n"
                        f"Document text:\n{document_text[:16000]}"
                    ),
                ),
            ],
            temperature=0.1,
            metadata={
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "MethodologyBenchmarkOutput",
                        "schema": schema,
                        "strict": False,
                    }
                },
            },
        )
        response = await self.gateway.chat(request)
        parsed = MethodologyBenchmarkOutput.model_validate_json(response.output_text)
        output_path = self.repo.dump_output_json(
            self.inventory.case.case_id,
            "sidecar/methodology_benchmark.json",
            parsed.model_dump(mode="json"),
        )
        return ToolInvocationResult(
            summary=parsed.summary,
            payload=parsed.model_dump(mode="json"),
            evidence=[
                ToolEvidenceDraft(
                    title="Gateway sidecar methodology benchmark",
                    summary=parsed.summary,
                    source_type=EvidenceSourceType.SIDECAR,
                    output_path=output_path,
                )
            ],
            output_path=output_path,
        )

    async def _benchmark_documentation_pack(
        self, args: DocumentationBenchmarkInput
    ) -> ToolInvocationResult:
        if not self.settings.workbench_enable_gateway_sidecars:
            raise RuntimeError("Gateway sidecars are disabled by configuration.")

        selected_artifacts = self._documentation_benchmark_artifacts(args.artifact_ids)
        profile = primary_data_profile(self.inventory)
        sections: list[str] = []
        for artifact in selected_artifacts:
            text = Path(artifact.absolute_path).read_text(encoding="utf-8", errors="ignore")
            sections.append(
                f"## {artifact.relative_path}\n"
                f"kind={artifact.kind.value}\n"
                f"tags={','.join(artifact.tags)}\n\n"
                f"{text[:8000]}"
            )
        if profile is not None:
            sections.append(f"## dataset_profile\n{profile.model_dump_json(indent=2)}")
        joined_sections = "\n\n".join(sections)[:26000]

        schema = DocumentationPackBenchmarkOutput.model_json_schema()
        request = ChatRequest(
            provider="openai",
            model=self.settings.workbench_judge_model,
            messages=[
                Message(
                    role=Role.SYSTEM,
                    content=(
                        "You are a validation-readiness documentation benchmarking sidecar. "
                        "Assess the supplied documentation pack as preparation for a bank model-validation review. "
                        "Focus on evidence sufficiency, internal consistency, monitoring/readiness gaps, and the "
                        "specific artifacts still needed before deeper validation. Return strict JSON only."
                    ),
                ),
                Message(
                    role=Role.USER,
                    content=(
                        f"Benchmark focus: {args.benchmark_focus}\n\n"
                        f"Artifact count: {len(selected_artifacts)}\n\n"
                        f"Documentation pack:\n{joined_sections}"
                    ),
                ),
            ],
            temperature=0.1,
            metadata={
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "DocumentationPackBenchmarkOutput",
                        "schema": schema,
                        "strict": False,
                    }
                },
            },
        )
        response = await self.gateway.chat(request)
        parsed = DocumentationPackBenchmarkOutput.model_validate_json(response.output_text)
        output_path = self.repo.dump_output_json(
            self.inventory.case.case_id,
            "sidecar/documentation_pack_benchmark.json",
            {
                **parsed.model_dump(mode="json"),
                "artifact_ids": [artifact.artifact_id for artifact in selected_artifacts],
                "artifact_paths": [artifact.relative_path for artifact in selected_artifacts],
            },
        )
        return ToolInvocationResult(
            summary=parsed.summary,
            payload=parsed.model_dump(mode="json"),
            evidence=[
                ToolEvidenceDraft(
                    title="Gateway sidecar documentation pack benchmark",
                    summary=parsed.summary,
                    source_type=EvidenceSourceType.SIDECAR,
                    output_path=output_path,
                )
            ],
            output_path=output_path,
        )

    def _analysis_result(self, outcome: AnalysisOutcome) -> ToolInvocationResult:
        evidence: list[ToolEvidenceDraft] = []
        for finding in outcome.findings:
            for signal in finding.evidence:
                source_type = (
                    EvidenceSourceType.ARTIFACT
                    if signal.relative_path and not signal.relative_path.startswith("outputs/")
                    else EvidenceSourceType.TOOL
                )
                evidence.append(
                    ToolEvidenceDraft(
                        title=finding.title,
                        summary=signal.detail,
                        source_type=source_type,
                        relative_path=signal.relative_path,
                    )
                )
        for output_name, output_path in outcome.outputs.items():
            evidence.append(
                ToolEvidenceDraft(
                    title=output_name.replace("_", " ").title(),
                    summary=f"Generated output artifact {Path(output_path).name}.",
                    source_type=EvidenceSourceType.TOOL,
                    output_path=output_path,
                )
            )

        payload = outcome.as_dict()
        return ToolInvocationResult(
            summary=outcome.summary,
            payload=payload,
            evidence=evidence,
            output_path=next(iter(outcome.outputs.values()), None),
        )

    def _documentation_benchmark_artifacts(self, artifact_ids: list[str]) -> list[ArtifactRecord]:
        if artifact_ids:
            return [self.inventory.get_artifact(artifact_id) for artifact_id in artifact_ids]

        selected: list[ArtifactRecord] = []
        for artifact in self.inventory.artifact_index.values():
            if artifact.kind == ArtifactKind.DOCUMENT:
                selected.append(artifact)
                continue
            if artifact.kind == ArtifactKind.DATASET and (
                "feature_dictionary" in artifact.tags or "reason_codes" in artifact.tags
            ):
                selected.append(artifact)
        if not selected:
            raise RuntimeError("No documentation artifacts are available for documentation-pack benchmarking.")
        return selected[:10]


def _strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    def visit(node: Any) -> Any:
        if isinstance(node, dict):
            updated = {key: visit(value) for key, value in node.items()}
            if updated.get("type") == "object":
                updated.setdefault("additionalProperties", False)
            return updated
        if isinstance(node, list):
            return [visit(item) for item in node]
        return node

    return cast(dict[str, Any], visit(schema))
