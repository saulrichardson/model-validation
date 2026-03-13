"""Load repo-local workbench skills from disk."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class SkillDefinition(BaseModel):
    skill_id: str
    path: str
    instructions: str
    resources: dict[str, str] = Field(default_factory=dict)


class SkillRegistry:
    def __init__(self, root_dir: Path) -> None:
        self._root_dir = root_dir
        self._skills: dict[str, SkillDefinition] = {}

    def load(self) -> None:
        self._skills.clear()
        if not self._root_dir.exists():
            raise FileNotFoundError(f"Skill directory does not exist: {self._root_dir}")

        for skill_dir in sorted(path for path in self._root_dir.iterdir() if path.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            resources: dict[str, str] = {}
            resource_dir = skill_dir / "resources"
            if resource_dir.is_dir():
                for resource_file in sorted(resource_dir.glob("*")):
                    if resource_file.is_file():
                        resources[resource_file.name] = resource_file.read_text(encoding="utf-8")
            self._skills[skill_dir.name] = SkillDefinition(
                skill_id=skill_dir.name,
                path=str(skill_dir),
                instructions=skill_file.read_text(encoding="utf-8"),
                resources=resources,
            )

    def get(self, skill_id: str) -> SkillDefinition:
        skill = self._skills.get(skill_id)
        if skill is None:
            available = ", ".join(sorted(self._skills))
            raise KeyError(f"Unknown skill '{skill_id}'. Available skills: {available}")
        return skill

    def list_ids(self) -> list[str]:
        return sorted(self._skills)
