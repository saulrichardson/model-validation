import { readFileSync } from "node:fs";
import { loadConfig } from "./lib/config.js";
import { readBridgeJson } from "./lib/bridge.js";
import { stagePaths } from "./lib/paths.js";
import { executionOutputSchema } from "./lib/schema.js";
import { executionPrompt } from "./lib/prompts.js";
import { loadGlobalInstructions, loadSkill } from "./lib/skills.js";
import { runStage } from "./lib/stageRunner.js";
import { pathToFileURL } from "node:url";

export async function runExecution(caseId: string) {
  const config = loadConfig();
  const casePayload = await readBridgeJson<Record<string, any>>(config.repoRoot, [
    "read-case",
    "--case-id",
    caseId,
  ]);
  const outputsDir = String(casePayload.outputs?.inventory).replace(/\/inventory\.json$/, "");
  const discoveryOutput = JSON.parse(readFileSync(requireSummary(casePayload, "discovery"), "utf-8"));
  const playbookOutput = JSON.parse(readFileSync(requireSummary(casePayload, "playbook"), "utf-8"));
  const paths = stagePaths(
    {
      caseDir: String(casePayload.root_dir).includes("/input/")
        ? String(casePayload.root_dir).split("/input/")[0]
        : outputsDir.replace(/\/outputs$/, ""),
      outputsDir,
    },
    "execution"
  );
  const executionSkillId = pickExecutionSkillId(casePayload);
  const executionSkill = loadSkill(config.repoRoot, executionSkillId);
  const prompt = executionPrompt({
    caseId,
    repoRoot: config.repoRoot,
    summaryPath: paths.summary,
    globalInstructions: loadGlobalInstructions(config.repoRoot),
    skillInstructions: executionSkill.instructions,
    executionSkillInstructions: executionSkill.instructions,
    casePayload,
    discoveryOutput,
    playbookOutput,
  });
  return runStage({
    config,
    caseId,
    stage: "execution",
    agentName: "Execution Agent",
    skillId: executionSkill.skillId,
    stageMessage:
      "Execution agent is selecting and running validation tools from the supported playbook.",
    prompt,
    schema: executionOutputSchema,
    paths,
  });
}

function requireSummary(casePayload: Record<string, any>, stage: "discovery" | "playbook"): string {
  const path = String(casePayload.outputs?.[`${stage}_summary`] || "").trim();
  if (!path) {
    throw new Error(`${stage} summary is missing; execution stage cannot proceed.`);
  }
  return path;
}

function pickExecutionSkillId(casePayload: Record<string, any>): string {
  const workflow = casePayload.coverage?.dominant_workflow;
  if (workflow === "full_revalidation") {
    return "full-revalidation";
  }
  if (workflow === "black_box_behavioral_review") {
    return "black-box-review";
  }
  return "conceptual-review";
}

async function main() {
  const caseId = parseCaseId(process.argv.slice(2));
  await runExecution(caseId);
}

function parseCaseId(args: string[]): string {
  const index = args.findIndex((value) => value === "--case-id");
  if (index === -1 || !args[index + 1]) {
    throw new Error("Usage: npm --prefix scripts/codex run execute -- --case-id <id>");
  }
  return args[index + 1];
}

if (isDirectExecution(import.meta.url)) {
  main().catch((error) => {
    console.error(String((error as Error)?.message ?? error));
    process.exit(1);
  });
}

function isDirectExecution(metaUrl: string): boolean {
  return Boolean(process.argv[1]) && pathToFileURL(process.argv[1]!).href === metaUrl;
}
