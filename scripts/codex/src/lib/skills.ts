import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export type SkillDefinition = {
  skillId: string;
  instructions: string;
  resources: Record<string, string>;
};

export function loadSkill(repoRoot: string, skillId: string): SkillDefinition {
  const skillDir = join(repoRoot, "skills", skillId);
  const skillFile = join(skillDir, "SKILL.md");
  if (!existsSync(skillFile)) {
    throw new Error(`Missing skill file: ${skillFile}`);
  }
  const resourcesDir = join(skillDir, "resources");
  const resources: Record<string, string> = {};
  if (existsSync(resourcesDir)) {
    for (const name of readdirSync(resourcesDir)) {
      const path = join(resourcesDir, name);
      resources[name] = readFileSync(path, "utf-8");
    }
  }
  return {
    skillId,
    instructions: readFileSync(skillFile, "utf-8"),
    resources,
  };
}

export function loadGlobalInstructions(repoRoot: string): string {
  const paths = [join(repoRoot, "..", "AGENTS.md"), join(repoRoot, "AGENTS.md")];
  return paths
    .filter((path) => existsSync(path))
    .map((path) => readFileSync(path, "utf-8").trim())
    .filter(Boolean)
    .join("\n\n");
}
