import { readFileSync } from "node:fs";
import { loadConfig } from "./lib/config.js";
import { readBridgeJson } from "./lib/bridge.js";
import { stagePaths } from "./lib/paths.js";
import { playbookOutputSchema } from "./lib/schema.js";
import { loadGlobalInstructions, loadSkill } from "./lib/skills.js";
import { playbookPrompt } from "./lib/prompts.js";
import { runStage } from "./lib/stageRunner.js";
import { pathToFileURL } from "node:url";

export async function runResolve(caseId: string) {
  const config = loadConfig();
  const casePayload = await readBridgeJson<Record<string, any>>(config.repoRoot, [
    "read-case",
    "--case-id",
    caseId,
  ]);
  const outputsDir = String(casePayload.outputs?.inventory).replace(/\/inventory\.json$/, "");
  const discoverySummaryPath = String(casePayload.outputs?.discovery_summary || "").trim();
  if (!discoverySummaryPath) {
    throw new Error("Discovery summary is missing; resolve stage cannot proceed.");
  }
  const discoveryOutput = JSON.parse(readFileSync(discoverySummaryPath, "utf-8"));
  const inventoryPath = String(casePayload.outputs?.inventory || "").trim();
  const inventorySummary = inventoryPath ? JSON.parse(readFileSync(inventoryPath, "utf-8")) : null;
  const paths = stagePaths(
    {
      caseDir: String(casePayload.root_dir).includes("/input/")
        ? String(casePayload.root_dir).split("/input/")[0]
        : outputsDir.replace(/\/outputs$/, ""),
      outputsDir,
    },
    "playbook"
  );
  const skill = loadSkill(config.repoRoot, "playbook-resolution");
  const moduleCatalog = JSON.parse(skill.resources["modules.json"] || "{}");
  const prompt = playbookPrompt({
    caseId,
    repoRoot: config.repoRoot,
    summaryPath: paths.summary,
    globalInstructions: loadGlobalInstructions(config.repoRoot),
    skillInstructions: skill.instructions,
    casePayload,
    discoveryOutput,
    inventorySummary,
    moduleCatalog,
  });
  return runStage({
    config,
    caseId,
    stage: "playbook",
    agentName: "Playbook Agent",
    skillId: skill.skillId,
    stageMessage: "Playbook agent is resolving executable, partial, and blocked modules.",
    prompt,
    schema: playbookOutputSchema,
    paths,
  });
}

async function main() {
  const caseId = parseCaseId(process.argv.slice(2));
  await runResolve(caseId);
}

function parseCaseId(args: string[]): string {
  const index = args.findIndex((value) => value === "--case-id");
  if (index === -1 || !args[index + 1]) {
    throw new Error("Usage: npm --prefix scripts/codex run resolve -- --case-id <id>");
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
