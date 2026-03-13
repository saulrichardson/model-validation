import { Codex } from "@openai/codex-sdk";
import { loadConfig } from "./lib/config.js";
import { pathToFileURL } from "node:url";

function classifyFailure(message: string) {
  const lowered = message.toLowerCase();
  if (lowered.includes("401") || lowered.includes("unauthorized")) {
    return {
      code: "AUTH_INVALID",
      hint: "The configured API key was rejected. Refresh OPENAI_API_KEY and retry.",
    };
  }
  if (
    (lowered.includes("model") && lowered.includes("not found")) ||
    lowered.includes("unknown model") ||
    lowered.includes("unsupported model")
  ) {
    return {
      code: "MODEL_INVALID",
      hint: "The configured model is unavailable for this account. Update WORKBENCH_AGENT_MODEL or codex.config.toml.",
    };
  }
  if (lowered.includes("rate limit") || lowered.includes("429")) {
    return {
      code: "RATE_LIMITED",
      hint: "The account is rate-limited. Retry later or reduce concurrency.",
    };
  }
  return {
    code: "PRECHECK_FAILED",
    hint: "Inspect the full error and rerun with a known-good key/model configuration.",
  };
}

async function main() {
  const cfg = loadConfig();
  for (const warning of cfg.configWarnings) {
    console.error(`[preflight][config] ${warning}`);
  }

  if (!cfg.apiKey) {
    throw new Error("OPENAI_API_KEY is required.");
  }

  const codex = new Codex({ apiKey: cfg.apiKey, baseUrl: cfg.baseURL } as any);
  const thread = codex.startThread(cfg.threadOptions as any);
  const startedAt = new Date().toISOString();

  try {
    const result = await thread.run(
      "Preflight check: reply with exactly the text OK and nothing else."
    );
    const response = String((result as any)?.finalResponse ?? result ?? "").trim();
    console.log(
      JSON.stringify(
        {
          event: "codex_preflight_ok",
          startedAt,
          finishedAt: new Date().toISOString(),
          model: cfg.model,
          reasoningEffort: cfg.reasoningEffort,
          baseURL: cfg.baseURL || null,
          response: response.slice(0, 120),
          configWarnings: cfg.configWarnings,
        },
        null,
        2
      )
    );
  } catch (err: any) {
    const message = String(err?.message ?? err);
    const classified = classifyFailure(message);
    console.error(
      JSON.stringify(
        {
          event: "codex_preflight_failed",
          startedAt,
          finishedAt: new Date().toISOString(),
          code: classified.code,
          detail: message,
          hint: classified.hint,
          model: cfg.model,
          reasoningEffort: cfg.reasoningEffort,
          baseURL: cfg.baseURL || null,
          configWarnings: cfg.configWarnings,
        },
        null,
        2
      )
    );
    process.exit(1);
  }
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
