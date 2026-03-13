import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import dotenv from "dotenv";
import toml from "@iarna/toml";

export type ThreadOptions = {
  model?: string;
  sandboxMode?: string;
  workingDirectory?: string;
  modelReasoningEffort?: string;
  approvalPolicy?: string;
  networkAccessEnabled?: boolean;
  webSearchEnabled?: boolean;
};

export type RunnerConfig = {
  repoRoot: string;
  packageRoot: string;
  apiKey: string;
  baseURL?: string;
  model: string;
  judgeModel: string;
  reasoningEffort: string;
  threadOptions: ThreadOptions;
  configWarnings: string[];
};

const SUPPORTED_TOML_ROOT_KEYS = new Set([
  "model",
  "model_reasoning_effort",
  "approval_policy",
  "sandbox_mode",
  "sandbox_workspace_write",
  "features",
]);

const KNOWN_UNSUPPORTED_FOR_SDK = new Set([
  "model_verbosity",
  "model_reasoning_summary",
  "notice",
  "shell_environment_policy",
]);

export function resolveRepoRoot(): string {
  if (process.env.CODEX_REPO_ROOT) {
    return resolve(process.env.CODEX_REPO_ROOT);
  }
  const __filename = fileURLToPath(import.meta.url);
  return resolve(join(dirname(__filename), "..", "..", "..", ".."));
}

export function loadConfig(repoRoot = resolveRepoRoot()): RunnerConfig {
  dotenv.config({ path: join(repoRoot, ".env") });
  dotenv.config({ path: join(dirname(repoRoot), ".env"), override: false });

  const env = process.env;
  const configPath = env.CODEX_CONFIG_PATH || join(repoRoot, "codex.config.toml");
  const tomlConfig = existsSync(configPath)
    ? (toml.parse(readFileSync(configPath, "utf-8")) as Record<string, any>)
    : {};

  const apiKey = env.CODEX_API_KEY || env.OPENAI_API_KEY || "";
  const baseURL = env.CODEX_BASE_URL || env.OPENAI_BASE_URL;
  const model =
    env.CODEX_MODEL ||
    env.WORKBENCH_AGENT_MODEL ||
    String(tomlConfig.model || "gpt-5.2");
  const judgeModel = env.WORKBENCH_JUDGE_MODEL || env.CODEX_JUDGE_MODEL || "gpt-4.1";
  const reasoningEffort =
    env.CODEX_REASONING_EFFORT ||
    env.WORKBENCH_REASONING_EFFORT ||
    String(tomlConfig.model_reasoning_effort || "high");

  const threadOptions: ThreadOptions = {
    model,
    sandboxMode: String(tomlConfig.sandbox_mode || "workspace-write"),
    workingDirectory: repoRoot,
    modelReasoningEffort: reasoningEffort,
    approvalPolicy: String(tomlConfig.approval_policy || "never"),
    networkAccessEnabled: Boolean(tomlConfig.sandbox_workspace_write?.network_access ?? true),
    webSearchEnabled: Boolean(tomlConfig.features?.web_search_request ?? false),
  };

  const configWarnings: string[] = [];
  for (const key of Object.keys(tomlConfig)) {
    if (SUPPORTED_TOML_ROOT_KEYS.has(key)) {
      continue;
    }
    if (KNOWN_UNSUPPORTED_FOR_SDK.has(key)) {
      configWarnings.push(
        `codex.config key '${key}' is not applied by @openai/codex-sdk thread options; remove it or enforce it via another runtime layer`
      );
      continue;
    }
    configWarnings.push(`codex.config key '${key}' is not recognized by this runner and may be ignored`);
  }

  return {
    repoRoot,
    packageRoot: join(repoRoot, "scripts", "codex"),
    apiKey,
    baseURL,
    model,
    judgeModel,
    reasoningEffort,
    threadOptions,
    configWarnings,
  };
}
