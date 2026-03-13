import { z } from "zod";

export const stageNameSchema = z.enum(["discovery", "playbook", "execution", "report"]);
export type StageName = z.infer<typeof stageNameSchema>;

const caseTypeValues = [
  "material_change_revalidation",
  "vendor_black_box_review",
  "conceptual_documentation_review",
  "documentation_only_review",
  "new_model_review",
  "unknown",
] as const;

const caseTypeSchema = z.enum(caseTypeValues);

const runtimeModeValues = [
  "runnable_source",
  "runtime_harness",
  "containerized",
  "document_only",
  "unknown",
] as const;

const runtimeModeSchema = z.enum(runtimeModeValues);

const workflowTypeValues = [
  "full_revalidation",
  "black_box_behavioral_review",
  "conceptual_readiness_review",
  "manual_triage",
] as const;

const workflowTypeSchema = z.enum(workflowTypeValues);

const moduleStatusSchema = z.enum(["executable", "partial", "blocked"]);
const findingSeveritySchema = z.enum(["high", "medium", "low", "info"]);
const reportTypeValues = [
  "full_revalidation_memo",
  "partial_validation_report",
  "conceptual_readiness_memo",
] as const;

const reportTypeSchema = z.enum(reportTypeValues);

const missingRateEntriesSchema = z.array(
  z
    .object({
      column: z.string(),
      missing_rate: z.number(),
    })
    .strict()
);

const dataProfileSchema = z
  .object({
    row_count: z.number().int().nullable().optional(),
    column_count: z.number().int().nullable().optional(),
    target_column: z.string().nullable().optional(),
    numeric_columns: z.array(z.string()).default([]),
    categorical_columns: z.array(z.string()).default([]),
    missing_rate_by_column: z
      .union([z.record(z.number()), missingRateEntriesSchema])
      .transform((value) => {
        if (Array.isArray(value)) {
          return Object.fromEntries(value.map((entry) => [entry.column, entry.missing_rate]));
        }
        return value;
      })
      .default({}),
    highlights: z.array(z.string()).default([]),
  })
  .strict();

export const normalizedCaseRecordSchema = z
  .object({
    case_type: caseTypeSchema,
    model_family: z.string(),
    decision_context: z.string(),
    runtime_mode: runtimeModeSchema,
    available_artifact_types: z.array(z.string()).default([]),
    available_evidence: z.array(z.string()).default([]),
    likely_execution_path: workflowTypeSchema,
    gaps: z.array(z.string()).default([]),
    notes: z.array(z.string()).default([]),
    artifact_highlights: z.array(z.string()).default([]),
    key_artifact_ids: z.array(z.string()).default([]),
    data_profile: dataProfileSchema.nullable().optional(),
    confidence_statement: z.string(),
  })
  .strict();

const coverageSummarySchema = z
  .object({
    executable: z.number().int(),
    partial: z.number().int(),
    blocked: z.number().int(),
    coverage_ratio: z.number(),
    dominant_workflow: workflowTypeSchema,
    coverage_rationale: z.string(),
  })
  .strict();

const playbookModuleSchema = z
  .object({
    module_id: z.string(),
    title: z.string(),
    status: moduleStatusSchema,
    rationale: z.string(),
    evidence_ids: z.array(z.string()).default([]),
    blocked_by: z.array(z.string()).default([]),
    recommended_tools: z.array(z.string()).default([]),
  })
  .strict();

const executionMetricSchema = z
  .object({
    label: z.string(),
    value: z.string(),
    detail: z.string().nullable().optional(),
  })
  .strict();

const findingDraftSchema = z
  .object({
    severity: findingSeveritySchema,
    title: z.string(),
    summary: z.string(),
    evidence_ids: z.array(z.string()).default([]),
    affected_modules: z.array(z.string()).default([]),
  })
  .strict();

const validationReportDraftSchema = z
  .object({
    report_type: reportTypeSchema,
    title: z.string(),
    executive_summary: z.string(),
    scope: z.array(z.string()).default([]),
    artifacts_reviewed: z.array(z.string()).default([]),
    modules_executed: z.array(z.string()).default([]),
    modules_blocked: z.array(z.string()).default([]),
    coverage_statement: z.string(),
    coverage_rationale: z.string().default(""),
    key_metrics: z.array(executionMetricSchema).default([]),
    findings: z.array(findingDraftSchema).default([]),
    recommended_actions: z.array(z.string()).default([]),
    evidence_requests: z.array(z.string()).default([]),
    narrative: z.array(z.string()).default([]),
  })
  .strict();

export const discoveryOutputSchema = z
  .object({
    summary: z.string(),
    normalized_case_record: normalizedCaseRecordSchema,
    evidence_ids: z.array(z.string()).default([]),
  })
  .strict();

export const playbookOutputSchema = z
  .object({
    summary: z.string(),
    coverage: coverageSummarySchema,
    modules: z.array(playbookModuleSchema).default([]),
  })
  .strict();

export const executionOutputSchema = z
  .object({
    summary: z.string(),
    findings: z.array(findingDraftSchema).default([]),
    metrics: z.array(executionMetricSchema).default([]),
    narrative: z.array(z.string()).default([]),
    evidence_requests: z.array(z.string()).default([]),
  })
  .strict();

export const reportOutputSchema = z
  .object({
    summary: z.string(),
    report: validationReportDraftSchema,
  })
  .strict();

export const caseMetadataSchema = z
  .object({
    case_id: z.string(),
    name: z.string(),
    source: z.string(),
    root_dir: z.string(),
    case_dir: z.string(),
    outputs_dir: z.string(),
    inventory_path: z.string(),
    inventory_summary: z.record(z.any()),
    artifact_count: z.number().int(),
  })
  .passthrough();

export type DiscoveryOutput = z.infer<typeof discoveryOutputSchema>;
export type PlaybookOutput = z.infer<typeof playbookOutputSchema>;
export type ExecutionOutput = z.infer<typeof executionOutputSchema>;
export type ReportOutput = z.infer<typeof reportOutputSchema>;

export const discoveryOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "normalized_case_record", "evidence_ids"],
  properties: {
    summary: { type: "string" },
    normalized_case_record: {
      type: "object",
      additionalProperties: false,
      required: [
        "case_type",
        "model_family",
        "decision_context",
        "runtime_mode",
        "available_artifact_types",
        "available_evidence",
        "likely_execution_path",
        "gaps",
        "notes",
        "artifact_highlights",
        "key_artifact_ids",
        "data_profile",
        "confidence_statement",
      ],
      properties: {
        case_type: { type: "string", enum: [...caseTypeValues] },
        model_family: { type: "string" },
        decision_context: { type: "string" },
        runtime_mode: { type: "string", enum: [...runtimeModeValues] },
        available_artifact_types: stringArraySchema(),
        available_evidence: stringArraySchema(),
        likely_execution_path: { type: "string", enum: [...workflowTypeValues] },
        gaps: stringArraySchema(),
        notes: stringArraySchema(),
        artifact_highlights: stringArraySchema(),
        key_artifact_ids: stringArraySchema(),
        data_profile: {
          anyOf: [
            { type: "null" },
            {
              type: "object",
              additionalProperties: false,
              required: [
                "row_count",
                "column_count",
                "target_column",
                "numeric_columns",
                "categorical_columns",
                "missing_rate_by_column",
                "highlights",
              ],
              properties: {
                row_count: nullableIntegerSchema(),
                column_count: nullableIntegerSchema(),
                target_column: nullableStringSchema(),
                numeric_columns: stringArraySchema(),
                categorical_columns: stringArraySchema(),
                missing_rate_by_column: missingRateEntriesJsonSchema(),
                highlights: stringArraySchema(),
              },
            },
          ],
        },
        confidence_statement: { type: "string" },
      },
    },
    evidence_ids: stringArraySchema(),
  },
} as const;

export const playbookOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "coverage", "modules"],
  properties: {
    summary: { type: "string" },
    coverage: {
      type: "object",
      additionalProperties: false,
      required: [
        "executable",
        "partial",
        "blocked",
        "coverage_ratio",
        "dominant_workflow",
        "coverage_rationale",
      ],
      properties: {
        executable: { type: "integer" },
        partial: { type: "integer" },
        blocked: { type: "integer" },
        coverage_ratio: { type: "number" },
        dominant_workflow: { type: "string", enum: [...workflowTypeValues] },
        coverage_rationale: { type: "string" },
      },
    },
    modules: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: [
          "module_id",
          "title",
          "status",
          "rationale",
          "evidence_ids",
          "blocked_by",
          "recommended_tools",
        ],
        properties: {
          module_id: { type: "string" },
          title: { type: "string" },
          status: { type: "string", enum: ["executable", "partial", "blocked"] },
          rationale: { type: "string" },
          evidence_ids: stringArraySchema(),
          blocked_by: stringArraySchema(),
          recommended_tools: stringArraySchema(),
        },
      },
    },
  },
} as const;

export const executionOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "findings", "metrics", "narrative", "evidence_requests"],
  properties: {
    summary: { type: "string" },
    findings: findingsArraySchema(),
    metrics: metricsArraySchema(),
    narrative: stringArraySchema(),
    evidence_requests: stringArraySchema(),
  },
} as const;

export const reportOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: ["summary", "report"],
  properties: {
    summary: { type: "string" },
    report: {
      type: "object",
      additionalProperties: false,
      required: [
        "report_type",
        "title",
        "executive_summary",
        "scope",
        "artifacts_reviewed",
        "modules_executed",
        "modules_blocked",
        "coverage_statement",
        "coverage_rationale",
        "key_metrics",
        "findings",
        "recommended_actions",
        "evidence_requests",
        "narrative",
      ],
      properties: {
        report_type: { type: "string", enum: [...reportTypeValues] },
        title: { type: "string" },
        executive_summary: { type: "string" },
        scope: stringArraySchema(),
        artifacts_reviewed: stringArraySchema(),
        modules_executed: stringArraySchema(),
        modules_blocked: stringArraySchema(),
        coverage_statement: { type: "string" },
        coverage_rationale: { type: "string" },
        key_metrics: metricsArraySchema(),
        findings: findingsArraySchema(),
        recommended_actions: stringArraySchema(),
        evidence_requests: stringArraySchema(),
        narrative: stringArraySchema(),
      },
    },
  },
} as const;

function stringArraySchema() {
  return {
    type: "array",
    items: { type: "string" },
  } as const;
}

function nullableStringSchema() {
  return {
    anyOf: [{ type: "string" }, { type: "null" }],
  } as const;
}

function nullableIntegerSchema() {
  return {
    anyOf: [{ type: "integer" }, { type: "null" }],
  } as const;
}

function metricsArraySchema() {
  return {
    type: "array",
    items: {
      type: "object",
      additionalProperties: false,
      required: ["label", "value", "detail"],
      properties: {
        label: { type: "string" },
        value: { type: "string" },
        detail: nullableStringSchema(),
      },
    },
  } as const;
}

function findingsArraySchema() {
  return {
    type: "array",
    items: {
      type: "object",
      additionalProperties: false,
      required: ["severity", "title", "summary", "evidence_ids", "affected_modules"],
      properties: {
        severity: { type: "string", enum: ["high", "medium", "low", "info"] },
        title: { type: "string" },
        summary: { type: "string" },
        evidence_ids: stringArraySchema(),
        affected_modules: stringArraySchema(),
      },
    },
  } as const;
}

function missingRateEntriesJsonSchema() {
  return {
    type: "array",
    items: {
      type: "object",
      additionalProperties: false,
      required: ["column", "missing_rate"],
      properties: {
        column: { type: "string" },
        missing_rate: { type: "number" },
      },
    },
  } as const;
}
