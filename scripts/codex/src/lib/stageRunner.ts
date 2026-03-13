import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  AgentMessageItem,
  Codex,
  FileChangeItem,
  Thread,
  ThreadEvent,
  ThreadItem,
  TurnOptions,
  Usage,
} from "@openai/codex-sdk";
import { z } from "zod";
import { runBridge } from "./bridge.js";
import { RunnerConfig } from "./config.js";
import { StagePaths } from "./paths.js";
import {
  discoveryOutputSchema as discoveryOutputSchemaRef,
  discoveryOutputJsonSchema,
  executionOutputSchema as executionOutputSchemaRef,
  executionOutputJsonSchema,
  playbookOutputSchema as playbookOutputSchemaRef,
  playbookOutputJsonSchema,
  reportOutputSchema as reportOutputSchemaRef,
  reportOutputJsonSchema,
} from "./schema.js";
import { parseStructuredResponse } from "./validation.js";

export type StageRunnerInput<T> = {
  config: RunnerConfig;
  caseId: string;
  stage: "discovery" | "playbook" | "execution" | "report";
  agentName: string;
  skillId: string;
  stageMessage: string;
  prompt: string;
  schema: z.ZodSchema<T>;
  paths: StagePaths;
};

const transientPatterns = ["stream disconnected", "ECONNRESET", "ENETDOWN", "ETIMEDOUT"];
const STAGE_TIMEOUT_MS = 12 * 60 * 1000;

export async function runStage<T>(input: StageRunnerInput<T>): Promise<T> {
  mkdirSync(input.paths.dir, { recursive: true });
  writeFileSync(input.paths.promptTxt, input.prompt, "utf-8");
  writeFileSync(input.paths.eventsJsonl, "", "utf-8");

  await runBridge(input.config.repoRoot, [
    "stage-start",
    "--case-id",
    input.caseId,
    "--stage",
    input.stage,
    "--agent-name",
    input.agentName,
    "--skill-id",
    input.skillId,
    "--model",
    input.config.model,
    "--message",
    input.stageMessage,
  ]);

  const codex = new Codex({ apiKey: input.config.apiKey, baseUrl: input.config.baseURL } as any);
  const thread = codex.startThread(input.config.threadOptions as any);

  try {
    const turn = await runStructuredTurn(thread, input.prompt, input.schema, input.paths.eventsJsonl);
    writeFileSync(input.paths.responseTxt, turn.finalResponse, "utf-8");
    writeFileSync(input.paths.itemsJsonl, turn.items.map((item) => JSON.stringify(item)).join("\n"), "utf-8");
    writeFileSync(input.paths.usageJson, JSON.stringify(turn.usage ?? {}, null, 2), "utf-8");

    const parsed = parseStructuredResponse(turn.finalResponse, input.schema, input.stage);
    writeFileSync(input.paths.summary, JSON.stringify(parsed, null, 2), "utf-8");

    const responseId = turn.responseId || `fallback-${input.caseId}-${input.stage}-${Date.now()}`;
    const tracePayload = {
      responseId,
      threadId: turn.threadId,
      stage: input.stage,
      agentName: input.agentName,
      skillId: input.skillId,
      model: input.config.model,
      promptFile: input.paths.promptTxt,
      responseFile: input.paths.responseTxt,
      summaryFile: input.paths.summary,
      itemsFile: input.paths.itemsJsonl,
      usageFile: input.paths.usageJson,
      eventsFile: input.paths.eventsJsonl,
    };
    writeFileSync(input.paths.traceJson, JSON.stringify(tracePayload, null, 2), "utf-8");

    await runBridge(input.config.repoRoot, [
      "stage-complete",
      "--case-id",
      input.caseId,
      "--stage",
      input.stage,
      "--summary-file",
      input.paths.summary,
      "--trace-file",
      input.paths.traceJson,
      "--response-file",
      input.paths.responseTxt,
      "--usage-file",
      input.paths.usageJson,
      "--events-file",
      input.paths.eventsJsonl,
      "--response-id",
      responseId,
    ]);

    return parsed;
  } catch (error: any) {
    const message = String(error?.message ?? error);
    writeFileSync(
      input.paths.traceJson,
      JSON.stringify(
        {
          stage: input.stage,
          agentName: input.agentName,
          skillId: input.skillId,
          model: input.config.model,
          error: message,
          promptFile: input.paths.promptTxt,
          responseFile: input.paths.responseTxt,
          summaryFile: input.paths.summary,
          itemsFile: input.paths.itemsJsonl,
          eventsFile: input.paths.eventsJsonl,
        },
        null,
        2
      ),
      "utf-8"
    );
    await runBridge(input.config.repoRoot, [
      "stage-failed",
      "--case-id",
      input.caseId,
      "--stage",
      input.stage,
      "--message",
      message,
      "--trace-file",
      input.paths.traceJson,
    ]);
    throw error;
  }
}

type StructuredTurn = {
  finalResponse: string;
  items: ThreadItem[];
  usage: Usage | null;
  responseId: string | null;
  threadId: string | null;
};

async function runStructuredTurn<T>(
  thread: Thread,
  prompt: string,
  schema: z.ZodSchema<T>,
  eventsPath: string,
  maxAttempts = 3
): Promise<StructuredTurn> {
  let attempt = 0;
  while (true) {
    attempt += 1;
    try {
      return await streamTurn(thread, prompt, schema, eventsPath);
    } catch (error: any) {
      const message = String(error?.message ?? error);
      const transient = transientPatterns.some((pattern) => message.includes(pattern));
      if (!transient || attempt >= maxAttempts) {
        throw error;
      }
      const backoffMs = 500 * attempt;
      await new Promise((resolve) => setTimeout(resolve, backoffMs));
    }
  }
}

async function streamTurn<T>(
  thread: Thread,
  prompt: string,
  schema: z.ZodSchema<T>,
  eventsPath: string
): Promise<StructuredTurn> {
  const timeoutController = new AbortController();
  const timeout = setTimeout(() => {
    timeoutController.abort(
      new Error(`Codex turn exceeded the ${Math.round(STAGE_TIMEOUT_MS / 60000)} minute stage limit.`)
    );
  }, STAGE_TIMEOUT_MS);
  const turnOptions: TurnOptions = {
    outputSchema: schemaForStage(schema),
    signal: timeoutController.signal,
  };
  try {
    const streamed = await thread.runStreamed(prompt, turnOptions);
    const items = new Map<string, ThreadItem>();
    let finalResponse = "";
    let usage: Usage | null = null;
    let threadId: string | null = thread.id;
    let responseId: string | null = null;

    for await (const event of streamed.events) {
      appendJsonLine(eventsPath, event);
      assertSafeEvent(event);
      captureEvent(event, items);

      if (event.type === "thread.started") {
        threadId = event.thread_id;
        responseId = event.thread_id;
        continue;
      }
      if (event.type === "turn.completed") {
        usage = event.usage;
        continue;
      }
      if (event.type === "turn.failed") {
        throw new Error(event.error.message);
      }
      if (event.type === "error") {
        throw new Error(event.message);
      }

      if (event.type === "item.completed" && event.item.type === "agent_message") {
        finalResponse = event.item.text;
        responseId = event.item.id || responseId;
      }
    }

    if (!finalResponse) {
      finalResponse = findLatestAgentMessage(items.values()) ?? "";
    }
    if (!finalResponse) {
      throw new Error("Codex turn completed without a final structured response.");
    }

    return {
      finalResponse,
      items: [...items.values()],
      usage,
      responseId,
      threadId,
    };
  } finally {
    clearTimeout(timeout);
  }
}

function schemaForStage(schema: z.ZodSchema<unknown>): Record<string, unknown> {
  if (schema === discoveryOutputSchemaRef) {
    return discoveryOutputJsonSchema;
  }
  if (schema === playbookOutputSchemaRef) {
    return playbookOutputJsonSchema;
  }
  if (schema === executionOutputSchemaRef) {
    return executionOutputJsonSchema;
  }
  if (schema === reportOutputSchemaRef) {
    return reportOutputJsonSchema;
  }
  throw new Error("No JSON schema registered for the requested stage schema.");
}

function appendJsonLine(path: string, value: unknown): void {
  appendFileSync(path, `${JSON.stringify(value)}\n`, "utf-8");
}

function captureEvent(event: ThreadEvent, items: Map<string, ThreadItem>): void {
  if (event.type === "item.started" || event.type === "item.updated" || event.type === "item.completed") {
    items.set(event.item.id, event.item);
  }
}

function assertSafeEvent(event: ThreadEvent): void {
  if (
    (event.type === "item.started" ||
      event.type === "item.updated" ||
      event.type === "item.completed") &&
    event.item.type === "file_change"
  ) {
    throw new Error(describeDisallowedFileChange(event.item));
  }
}

function describeDisallowedFileChange(item: FileChangeItem): string {
  const changedPaths = item.changes.map((change) => `${change.kind}:${change.path}`).join(", ");
  return `Codex attempted to modify workspace files during a validation run (${changedPaths}). Validation stages must use bridge tools and may not edit repository files.`;
}

function findLatestAgentMessage(items: Iterable<ThreadItem>): string | null {
  let latest: AgentMessageItem | null = null;
  for (const item of items) {
    if (item.type === "agent_message") {
      latest = item;
    }
  }
  return latest?.text ?? null;
}
