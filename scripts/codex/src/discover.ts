import { loadConfig } from "./lib/config.js";
import { readBridgeJson } from "./lib/bridge.js";
import { stagePaths } from "./lib/paths.js";
import { caseMetadataSchema, discoveryOutputSchema } from "./lib/schema.js";
import { loadGlobalInstructions, loadSkill } from "./lib/skills.js";
import { discoveryPrompt } from "./lib/prompts.js";
import { runStage } from "./lib/stageRunner.js";
import { pathToFileURL } from "node:url";

export async function runDiscovery(caseId: string) {
  const config = loadConfig();
  const prepared = caseMetadataSchema.parse(
    await readBridgeJson(config.repoRoot, ["prepare-case", "--case-id", caseId])
  );
  const paths = stagePaths(
    {
      caseDir: String(prepared.case_dir),
      outputsDir: String(prepared.outputs_dir),
    },
    "discovery"
  );
  const skill = loadSkill(config.repoRoot, "discovery-case-shaping");
  const prompt = discoveryPrompt({
    caseId,
    repoRoot: config.repoRoot,
    summaryPath: paths.summary,
    globalInstructions: loadGlobalInstructions(config.repoRoot),
    skillInstructions: skill.instructions,
    preparePayload: prepared,
  });
  return runStage({
    config,
    caseId,
    stage: "discovery",
    agentName: "Discovery Agent",
    skillId: skill.skillId,
    stageMessage: "Discovery agent is inventorying evidence and shaping the case record.",
    prompt,
    schema: discoveryOutputSchema,
    paths,
  });
}

async function main() {
  const caseId = parseCaseId(process.argv.slice(2));
  await runDiscovery(caseId);
}

function parseCaseId(args: string[]): string {
  const caseIndex = args.indexOf("--case-id");
  if (caseIndex === -1 || !args[caseIndex + 1]) {
    throw new Error("Usage: npm --prefix scripts/codex run discover -- --case-id case_123");
  }
  return args[caseIndex + 1]!;
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
