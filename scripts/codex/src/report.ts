import { readFileSync } from "node:fs";
import { loadConfig } from "./lib/config.js";
import { readBridgeJson } from "./lib/bridge.js";
import { stagePaths } from "./lib/paths.js";
import { reportOutputSchema } from "./lib/schema.js";
import { reportPrompt } from "./lib/prompts.js";
import { loadGlobalInstructions, loadSkill } from "./lib/skills.js";
import { runStage } from "./lib/stageRunner.js";
import { pathToFileURL } from "node:url";

export async function runReport(caseId: string) {
  const config = loadConfig();
  const casePayload = await readBridgeJson<Record<string, any>>(config.repoRoot, [
    "read-case",
    "--case-id",
    caseId,
  ]);
  const outputsDir = String(casePayload.outputs?.inventory).replace(/\/inventory\.json$/, "");
  const discoveryOutput = JSON.parse(
    readFileSync(requireSummary(casePayload, "discovery"), "utf-8")
  );
  const playbookOutput = JSON.parse(
    readFileSync(requireSummary(casePayload, "playbook"), "utf-8")
  );
  const executionOutput = JSON.parse(
    readFileSync(requireExecutionSummary(casePayload), "utf-8")
  );
  const paths = stagePaths(
    {
      caseDir: String(casePayload.root_dir).includes("/input/")
        ? String(casePayload.root_dir).split("/input/")[0]
        : outputsDir.replace(/\/outputs$/, ""),
      outputsDir,
    },
    "report"
  );
  const skill = loadSkill(config.repoRoot, "final-report");
  const prompt = reportPrompt({
    caseId,
    repoRoot: config.repoRoot,
    summaryPath: paths.summary,
    globalInstructions: loadGlobalInstructions(config.repoRoot),
    skillInstructions: skill.instructions,
    casePayload,
    discoveryOutput,
    playbookOutput,
    executionOutput,
  });
  return runStage({
    config,
    caseId,
    stage: "report",
    agentName: "Report Agent",
    skillId: skill.skillId,
    stageMessage: "Report agent is drafting the bank-facing work product.",
    prompt,
    schema: reportOutputSchema,
    paths,
  });
}

function requireSummary(casePayload: Record<string, any>, stage: "discovery" | "playbook"): string {
  const path = String(casePayload.outputs?.[`${stage}_summary`] || "").trim();
  if (!path) {
    throw new Error(`${stage} summary is missing; report stage cannot proceed.`);
  }
  return path;
}

function requireExecutionSummary(casePayload: Record<string, any>): string {
  const path = String(casePayload.outputs?.execution_summary || "").trim();
  if (!path) {
    throw new Error("execution summary is missing; report stage cannot proceed.");
  }
  return path;
}

async function main() {
  const caseId = parseCaseId(process.argv.slice(2));
  await runReport(caseId);
}

function parseCaseId(args: string[]): string {
  const index = args.findIndex((value) => value === "--case-id");
  if (index === -1 || !args[index + 1]) {
    throw new Error("Usage: npm --prefix scripts/codex run report -- --case-id <id>");
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
