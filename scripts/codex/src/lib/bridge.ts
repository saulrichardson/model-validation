import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export const BRIDGE_BASE_COMMAND = "poetry run workbench-bridge";

type BridgeOptions = {
  repoRoot: string;
};

export async function readBridgeJson<T>(repoRoot: string, args: string[]): Promise<T> {
  const stdout = await runBridge(repoRoot, args);
  return JSON.parse(stdout) as T;
}

export async function runBridge(repoRoot: string, args: string[]): Promise<string> {
  const { stdout, stderr } = await execFileAsync(
    "poetry",
    ["run", "workbench-bridge", ...args],
    {
      cwd: repoRoot,
      maxBuffer: 10 * 1024 * 1024,
      env: process.env,
    }
  );
  if (stderr && stderr.trim()) {
    return stdout;
  }
  return stdout;
}

export function bridgeCommand(args: string[]): string {
  return `${BRIDGE_BASE_COMMAND} ${args.map(shellEscape).join(" ")}`.trim();
}

function shellEscape(value: string): string {
  if (/^[A-Za-z0-9_./:=,-]+$/.test(value)) {
    return value;
  }
  return `'${value.replace(/'/g, `'\"'\"'`)}'`;
}
