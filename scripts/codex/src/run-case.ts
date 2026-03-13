import { loadConfig } from "./lib/config.js";
import { readBridgeJson, runBridge } from "./lib/bridge.js";
import { runDiscovery } from "./discover.js";
import { runResolve } from "./resolve.js";
import { runExecution } from "./execute.js";
import { runReport } from "./report.js";
import { pathToFileURL } from "node:url";

async function main() {
  const caseId = parseCaseId(process.argv.slice(2));
  const cfg = loadConfig();

  if (!cfg.apiKey) {
    throw new Error("CODEX_API_KEY or OPENAI_API_KEY is required for the Codex runner.");
  }

  try {
    await runDiscovery(caseId);
    await runResolve(caseId);
    await runExecution(caseId);
    await runReport(caseId);
    await runBridge(cfg.repoRoot, ["mark-completed", "--case-id", caseId]);
    console.log(`[run-case] completed case ${caseId}`);
  } catch (err: any) {
    const message = String(err?.message ?? err);
    const current = await readBridgeJson<{ status?: string }>(cfg.repoRoot, [
      "read-case",
      "--case-id",
      caseId,
    ]).catch(() => ({ status: undefined }));
    if (current.status !== "failed") {
      await runBridge(cfg.repoRoot, ["mark-failed", "--case-id", caseId, "--message", message]);
    }
    throw err;
  }
}

function parseCaseId(args: string[]): string {
  const caseIndex = args.indexOf("--case-id");
  if (caseIndex === -1 || !args[caseIndex + 1]) {
    throw new Error("Usage: npm --prefix scripts/codex run run-case -- --case-id case_123");
  }
  return args[caseIndex + 1]!;
}

if (isDirectExecution(import.meta.url)) {
  main().catch((err: any) => {
    console.error(String(err?.message ?? err));
    process.exit(1);
  });
}

function isDirectExecution(metaUrl: string): boolean {
  return Boolean(process.argv[1]) && pathToFileURL(process.argv[1]!).href === metaUrl;
}
