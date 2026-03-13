import { bridgeCommand } from "./bridge.js";
import { DiscoveryOutput, ExecutionOutput, PlaybookOutput } from "./schema.js";

type PromptBase = {
  caseId: string;
  repoRoot: string;
  summaryPath: string;
  globalInstructions: string;
  skillInstructions: string;
};

type DiscoveryPromptInput = PromptBase & {
  preparePayload: Record<string, any>;
};

type PlaybookPromptInput = PromptBase & {
  casePayload: Record<string, any>;
  discoveryOutput: DiscoveryOutput;
  inventorySummary: Record<string, any> | null;
  moduleCatalog: Record<string, any>;
};

type ExecutionPromptInput = PromptBase & {
  casePayload: Record<string, any>;
  discoveryOutput: DiscoveryOutput;
  playbookOutput: PlaybookOutput;
  executionSkillInstructions: string;
};

type ReportPromptInput = PromptBase & {
  casePayload: Record<string, any>;
  discoveryOutput: DiscoveryOutput;
  playbookOutput: PlaybookOutput;
  executionOutput: ExecutionOutput;
};

function caseInspectionCommands(stage: "discovery" | "execution"): string[][] {
  return [
    ["read-case", "--case-id", "<case-id>"],
    ["tool", "--case-id", "<case-id>", "--stage", stage, "--tool-name", "list_artifacts", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", stage, "--tool-name", "read_artifact_excerpt", "--args-json", '{"artifact_id":"art_001"}'],
    ["tool", "--case-id", "<case-id>", "--stage", stage, "--tool-name", "read_artifact_text", "--args-json", '{"artifact_id":"art_001","max_chars":8000}'],
    ["tool", "--case-id", "<case-id>", "--stage", stage, "--tool-name", "profile_dataset", "--args-json", '{"artifact_id":"art_003"}'],
    ["tool", "--case-id", "<case-id>", "--stage", stage, "--tool-name", "inspect_runtime_assets", "--args-json", "{}"],
  ];
}

function executionCommands(): string[][] {
  return [
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "run_material_model_pair", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "run_vendor_runtime_harness", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "compare_scored_outputs", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "run_sensitivity_analysis", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "review_material_behavior", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "review_vendor_behavior", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "check_document_consistency", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "review_reason_code_mapping", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "summarize_data_quality", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "review_conceptual_conditions", "--args-json", "{}"],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "benchmark_methodology_doc", "--args-json", '{"artifact_id":"art_001","benchmark_focus":"validation evidence sufficiency and documentation quality"}'],
    ["tool", "--case-id", "<case-id>", "--stage", "execution", "--tool-name", "benchmark_documentation_pack", "--args-json", '{"artifact_ids":[],"benchmark_focus":"validation evidence sufficiency, documentation consistency, and execution readiness"}'],
  ];
}

function commandList(commands: string[][], caseId: string): string {
  return commands
    .map((parts) =>
      `- ${bridgeCommand(parts.map((part) => (part === "<case-id>" ? caseId : part)))}`
    )
    .join("\n");
}

function artifactDigest(casePayload: Record<string, any>): Array<Record<string, unknown>> {
  return Array.isArray(casePayload.artifacts)
    ? casePayload.artifacts.map((artifact: Record<string, any>) => ({
        artifact_id: artifact.artifact_id,
        relative_path: artifact.relative_path,
        kind: artifact.kind,
        tags: artifact.tags ?? [],
      }))
    : [];
}

function evidenceDigest(casePayload: Record<string, any>): Array<Record<string, unknown>> {
  return Array.isArray(casePayload.evidence_ledger)
    ? casePayload.evidence_ledger.map((entry: Record<string, any>) => ({
        evidence_id: entry.evidence_id,
        source_type: entry.source_type,
        title: entry.title,
        artifact_id: entry.artifact_id ?? null,
        tool_call_id: entry.tool_call_id ?? null,
        relative_path: entry.relative_path ?? null,
      }))
    : [];
}

function playbookDigest(casePayload: Record<string, any>): Array<Record<string, unknown>> {
  return Array.isArray(casePayload.playbook)
    ? casePayload.playbook.map((module: Record<string, any>) => ({
        module_id: module.module_id,
        title: module.title,
        status: module.status,
        evidence_ids: module.evidence_ids ?? [],
        blocked_by: module.blocked_by ?? [],
        recommended_tools: module.recommended_tools ?? [],
      }))
    : [];
}

function compactCaseContext(casePayload: Record<string, any>): Record<string, unknown> {
  return {
    case_id: casePayload.case_id,
    name: casePayload.name,
    source: casePayload.source,
    status: casePayload.status,
    root_dir: casePayload.root_dir,
    artifacts: artifactDigest(casePayload),
    evidence_ledger: evidenceDigest(casePayload),
    coverage: casePayload.coverage ?? null,
  };
}

function compactExecutionCaseContext(casePayload: Record<string, any>): Record<string, unknown> {
  return {
    ...compactCaseContext(casePayload),
    normalized_case_record: casePayload.normalized_case_record ?? null,
    playbook: playbookDigest(casePayload),
  };
}

function compactReportCaseContext(casePayload: Record<string, any>): Record<string, unknown> {
  return {
    ...compactExecutionCaseContext(casePayload),
    outputs: {
      inventory: casePayload.outputs?.inventory ?? null,
      discovery_summary: casePayload.outputs?.discovery_summary ?? null,
      playbook_summary: casePayload.outputs?.playbook_summary ?? null,
      execution_summary: casePayload.outputs?.execution_summary ?? null,
    },
  };
}

function fileWriteInstructions(summaryPath: string): string {
  return [
    `Return the final JSON object directly as your final response. The runner will persist it to ${summaryPath}.`,
    "Do not wrap the JSON in markdown fences.",
    "Do not add commentary before or after the JSON object.",
  ].join("\n");
}

export function discoveryPrompt(input: DiscoveryPromptInput): string {
  return `
${input.globalInstructions}

You are the discovery agent for a local bank model validation workbench.

Skill instructions:
${input.skillInstructions}

Ground truth:
- Repo root: ${input.repoRoot}
- Case id: ${input.caseId}
- Prepared case payload:
${JSON.stringify(input.preparePayload, null, 2)}

Bridge commands available in this stage:
${commandList(caseInspectionCommands("discovery"), input.caseId)}

Rules:
- Use only the bridge command surface for case inspection.
- Use shell commands from the repo root when invoking bridge commands.
- Do not create, edit, or patch repository files during the run.
- Build a normalized case record from evidence that actually exists.
- Cite evidence ids that already exist in the case ledger or were returned by tool calls.
- Do not claim runnable coverage if the package does not support it.
- Keep the tool budget tight. Stop once you have enough evidence to make a grounded discovery decision.
- Do not start with read-case unless the prepared payload is insufficient. Prefer this sequence: inspect_runtime_assets, profile_dataset on the primary dataset, then targeted read_artifact_text or read_artifact_excerpt.
- Do not re-read the full case JSON if the prepared payload and targeted tools already answer the question.

Required output shape:
{
  "summary": "string",
  "normalized_case_record": {
    "case_type": "material_change_revalidation|vendor_black_box_review|conceptual_documentation_review|documentation_only_review|new_model_review|unknown",
    "model_family": "string",
    "decision_context": "string",
    "runtime_mode": "runnable_source|runtime_harness|containerized|document_only|unknown",
    "available_artifact_types": ["string"],
    "available_evidence": ["string"],
    "likely_execution_path": "full_revalidation|black_box_behavioral_review|conceptual_readiness_review|manual_triage",
    "gaps": ["string"],
    "notes": ["string"],
    "artifact_highlights": ["string"],
    "key_artifact_ids": ["artifact or evidence id"],
    "data_profile": null or {
      "row_count": number|null,
      "column_count": number|null,
      "target_column": string|null,
      "numeric_columns": ["string"],
      "categorical_columns": ["string"],
      "missing_rate_by_column": [{"column": "string", "missing_rate": number}],
      "highlights": ["string"]
    },
    "confidence_statement": "string"
  },
  "evidence_ids": ["string"]
}

${fileWriteInstructions(input.summaryPath)}
`.trim();
}

export function playbookPrompt(input: PlaybookPromptInput): string {
  return `
${input.globalInstructions}

You are the playbook resolution agent for a local bank model validation workbench.

Skill instructions:
${input.skillInstructions}

Current case state:
${JSON.stringify(compactCaseContext(input.casePayload), null, 2)}

Discovery output:
${JSON.stringify(input.discoveryOutput, null, 2)}

Playbook catalog:
${JSON.stringify(input.moduleCatalog, null, 2)}

Inventory summary:
${JSON.stringify(input.inventorySummary, null, 2)}

Rules:
- Resolve the maximal defensible subset of the playbook.
- Do not create, edit, or patch repository files during the run.
- Start from inventory_summary.capability_hints and the module catalog. Use discovery narrative and artifact paths to explain those capabilities, not to invent stricter prerequisites than the catalog actually requires.
- Mark modules executable only when the evidence supports running them now.
- Mark modules partial when some evidence exists but scope is constrained.
- Mark modules blocked when required evidence is missing and name the missing evidence in blocked_by.
- Use evidence ids from the existing case ledger.
- recommended_tools must use exact bridge tool names, not generic technologies. Valid values include: list_artifacts, read_artifact_excerpt, read_artifact_text, profile_dataset, inspect_runtime_assets, run_material_model_pair, run_vendor_runtime_harness, compare_scored_outputs, run_sensitivity_analysis, review_material_behavior, review_vendor_behavior, check_document_consistency, review_reason_code_mapping, summarize_data_quality, review_conceptual_conditions, benchmark_methodology_doc, benchmark_documentation_pack.
- Treat dominant workflow as a case-shape judgment, not as a penalty for partial modules.
- If discovery indicates a material-change revalidation with runnable source, a baseline/candidate pair, validation data, and supporting methodology/change documentation, prefer full_revalidation unless execution-based work is mostly blocked.
- Use black_box_behavioral_review when execution is possible but internal model visibility is weak or opaque.
- Use conceptual_readiness_review when documentation-led review is credible but execution-based validation is not.
- Partial runtime reproduction or partial conceptual soundness does not by itself force a black-box workflow.
- Return the playbook decision once the module statuses are grounded; do not continue exploring.
- For full_revalidation packages with executable runtime and baseline comparison support, recommended_tools should usually include run_material_model_pair, compare_scored_outputs, run_sensitivity_analysis, review_reason_code_mapping, and check_document_consistency where relevant.
- For conceptual_readiness_review packages, recommended_tools should usually include benchmark_documentation_pack, review_conceptual_conditions, summarize_data_quality, and review_reason_code_mapping where relevant.

Required output shape:
{
  "summary": "string",
  "coverage": {
    "executable": number,
    "partial": number,
    "blocked": number,
    "coverage_ratio": number,
    "dominant_workflow": "full_revalidation|black_box_behavioral_review|conceptual_readiness_review|manual_triage",
    "coverage_rationale": "string"
  },
  "modules": [
    {
      "module_id": "string",
      "title": "string",
      "status": "executable|partial|blocked",
      "rationale": "string",
      "evidence_ids": ["string"],
      "blocked_by": ["string"],
      "recommended_tools": ["string"]
    }
  ]
}

${fileWriteInstructions(input.summaryPath)}
`.trim();
}

export function executionPrompt(input: ExecutionPromptInput): string {
  return `
${input.globalInstructions}

You are the execution agent for a local bank model validation workbench.

Primary execution skill instructions:
${input.executionSkillInstructions}

Shared skill instructions:
${input.skillInstructions}

Current case state:
${JSON.stringify(compactExecutionCaseContext(input.casePayload), null, 2)}

Discovery output:
${JSON.stringify(input.discoveryOutput, null, 2)}

Playbook output:
${JSON.stringify(input.playbookOutput, null, 2)}

Bridge commands available in this stage:
${commandList(caseInspectionCommands("execution"), input.caseId)}
${"\n"}
${commandList(executionCommands(), input.caseId)}

Rules:
- Run only tools relevant to executable or partial modules.
- Prefer deterministic local tools before any sidecar LLM benchmark.
- Do not create, edit, or patch repository files during the run.
- Every finding must cite evidence ids returned by prior artifacts or tool calls.
- If scope remains blocked, say what evidence is still needed.
- Keep tool usage disciplined. Do not invoke tools that are not named in recommended_tools unless you need them to support a cited finding.
- Avoid broad read-case dumps during execution. Use the supplied stage outputs and targeted tool calls instead.
- When the dominant workflow is full_revalidation and runtime reproduction plus baseline comparison are executable, include run_sensitivity_analysis unless the evidence clearly blocks it.
- When the dominant workflow is conceptual_readiness_review and the package is documentation-heavy, use benchmark_documentation_pack if sidecars are enabled and the benchmark will sharpen the evidence request list.

Required output shape:
{
  "summary": "string",
  "findings": [
    {
      "severity": "high|medium|low|info",
      "title": "string",
      "summary": "string",
      "evidence_ids": ["string"],
      "affected_modules": ["string"]
    }
  ],
  "metrics": [
    {
      "label": "string",
      "value": "string",
      "detail": "string|null"
    }
  ],
  "narrative": ["string"],
  "evidence_requests": ["string"]
}

${fileWriteInstructions(input.summaryPath)}
`.trim();
}

export function reportPrompt(input: ReportPromptInput): string {
  return `
${input.globalInstructions}

You are the final report agent for a local bank model validation workbench.

Skill instructions:
${input.skillInstructions}

Current case state:
${JSON.stringify(compactReportCaseContext(input.casePayload), null, 2)}

Discovery output:
${JSON.stringify(input.discoveryOutput, null, 2)}

Playbook output:
${JSON.stringify(input.playbookOutput, null, 2)}

Execution output:
${JSON.stringify(input.executionOutput, null, 2)}

Rules:
- Draft a bank-facing work product.
- Do not create, edit, or patch repository files during the run.
- Findings must remain bounded by executed scope and cited evidence.
- Make blocked work and remaining evidence requests explicit.
- Do not claim full validation if the case only supports partial coverage.
- Report type selection must follow the resolved workflow:
  - Use full_revalidation_memo when the dominant workflow is full_revalidation and there are no blocked modules. Partial modules alone do not downgrade the report type; disclose that limited coverage inside the memo.
  - Use partial_validation_report when the dominant workflow is black_box_behavioral_review, or when one or more blocked modules materially constrain execution-based validation.
  - Use conceptual_readiness_memo when the dominant workflow is conceptual_readiness_review.
- Return only the final report JSON object.

Required output shape:
{
  "summary": "string",
  "report": {
    "report_type": "full_revalidation_memo|partial_validation_report|conceptual_readiness_memo",
    "title": "string",
    "executive_summary": "string",
    "scope": ["string"],
    "artifacts_reviewed": ["string"],
    "modules_executed": ["string"],
    "modules_blocked": ["string"],
    "coverage_statement": "string",
    "coverage_rationale": "string",
    "key_metrics": [{"label":"string","value":"string","detail":"string|null"}],
    "findings": [
      {
        "severity": "high|medium|low|info",
        "title": "string",
        "summary": "string",
        "evidence_ids": ["string"],
        "affected_modules": ["string"]
      }
    ],
    "recommended_actions": ["string"],
    "evidence_requests": ["string"],
    "narrative": ["string"]
  }
}

${fileWriteInstructions(input.summaryPath)}
`.trim();
}
