"""Helpers for loading the workbench playbook module catalog."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field

from .skills import SkillRegistry


class ModuleRule(BaseModel):
    module_id: str
    title: str
    executable_when_all: list[str] = Field(default_factory=list)
    executable_when_any: list[str] = Field(default_factory=list)
    partial_when_any: list[str] = Field(default_factory=list)
    blocked_message: str


class ModuleRuleSet(BaseModel):
    modules: list[ModuleRule]


def load_module_catalog(skills: SkillRegistry) -> ModuleRuleSet:
    resource_text = skills.get("playbook-resolution").resources.get("modules.json")
    if resource_text is None:
        raise RuntimeError("Playbook resolution skill is missing modules.json")
    return ModuleRuleSet.model_validate(json.loads(resource_text))
