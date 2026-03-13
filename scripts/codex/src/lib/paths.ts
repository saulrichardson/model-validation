import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export type StageName = "discovery" | "playbook" | "execution" | "report";

export type CasePaths = {
  caseDir: string;
  outputsDir: string;
};

export type StagePaths = {
  dir: string;
  summary: string;
  promptTxt: string;
  responseTxt: string;
  itemsJsonl: string;
  eventsJsonl: string;
  usageJson: string;
  traceJson: string;
};

export function stagePaths(casePaths: CasePaths, stage: StageName): StagePaths {
  const dir = join(casePaths.outputsDir, "codex", stage);
  mkdirSync(dir, { recursive: true });
  return {
    dir,
    summary: join(dir, "summary.json"),
    promptTxt: join(dir, "prompt.txt"),
    responseTxt: join(dir, "response.txt"),
    itemsJsonl: join(dir, "items.jsonl"),
    eventsJsonl: join(dir, "events.jsonl"),
    usageJson: join(dir, "usage.json"),
    traceJson: join(dir, "trace.json"),
  };
}

export function writeJson(path: string, payload: unknown): void {
  writeFileSync(path, JSON.stringify(payload, null, 2), "utf-8");
}
