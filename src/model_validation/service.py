"""Core service for the root model-validation repo."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from .schemas import CaseRecord, CaseSource, SeedBundleDescriptor
from .settings import Settings
from .skills import SkillRegistry
from .storage import CaseRepository


class ValidationWorkbenchService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._repo = CaseRepository(settings.workbench_storage_dir)
        self._repo.initialize()
        self._skills = SkillRegistry(settings.workbench_skill_dir)
        self._skills.load()

    @property
    def repo(self) -> CaseRepository:
        return self._repo

    @property
    def skills(self) -> SkillRegistry:
        return self._skills

    def runtime_status(self) -> dict[str, object]:
        package_dir = self._settings.workbench_codex_package_dir
        return {
            "openai_configured": bool(self._settings.openai_api_key),
            "agent_model": self._settings.workbench_agent_model,
            "judge_model": self._settings.workbench_judge_model,
            "gateway_sidecars_enabled": self._settings.workbench_enable_gateway_sidecars,
            "gateway_base_url": self._settings.gateway_base_url,
            "codex_package_dir": str(package_dir),
            "codex_package_exists": package_dir.is_dir(),
            "codex_runner_type": "typescript_codex_sdk",
        }

    def list_cases(self) -> list[CaseRecord]:
        return self._repo.list_cases()

    def get_case(self, case_id: str) -> CaseRecord:
        return self._repo.get_case(case_id)

    def list_seed_bundles(self) -> list[SeedBundleDescriptor]:
        seed_root = self._settings.workbench_seed_banks_dir
        return [
            SeedBundleDescriptor.model_validate_json(descriptor.read_text(encoding="utf-8"))
            for descriptor in sorted(seed_root.glob("*/*/seed.json"))
        ]

    def create_case_from_seed(self, seed_id: str) -> CaseRecord:
        descriptor = next((item for item in self.list_seed_bundles() if item.seed_id == seed_id), None)
        if descriptor is None:
            raise KeyError(f"Unknown seed bundle: {seed_id}")

        case_id = f"case_{uuid.uuid4().hex[:12]}"
        case_dir = self._repo.create_case_dir(case_id)
        source_dir = Path(descriptor.package_dir)
        if not source_dir.is_absolute():
            source_dir = self._settings.workbench_seed_banks_dir / source_dir
        target_dir = case_dir / "input" / f"{descriptor.bank_slug}_{descriptor.bundle_slug}"
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=False)
        case = CaseRecord(
            case_id=case_id,
            name=f"{descriptor.bank_name} - {descriptor.bundle_name}",
            source=CaseSource.SEED,
            source_id=descriptor.seed_id,
            root_dir=str(target_dir),
        )
        return self._repo.save_case(case)
