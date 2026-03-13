"""Runtime settings for the model-validation demo repo."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime settings loaded from environment or the repo-root `.env`."""

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", PROJECT_ROOT.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "OPENAI_KEY"),
    )
    gateway_base_url: str = Field(default="http://127.0.0.1:8000", alias="GATEWAY_URL")
    gateway_timeout_seconds: float = Field(default=120.0, alias="GATEWAY_TIMEOUT_SECONDS")

    workbench_storage_dir: Path = Field(
        default=PROJECT_ROOT / ".workbench",
        alias="WORKBENCH_STORAGE_DIR",
    )
    workbench_demo_cases_dir: Path = Field(
        default=PROJECT_ROOT / "demo_cases",
        alias="WORKBENCH_DEMO_CASES_DIR",
    )
    workbench_skill_dir: Path = Field(
        default=PROJECT_ROOT / "skills",
        alias="WORKBENCH_SKILL_DIR",
    )
    workbench_codex_package_dir: Path = Field(
        default=PROJECT_ROOT / "scripts" / "codex",
        alias="WORKBENCH_CODEX_PACKAGE_DIR",
    )
    workbench_agent_model: str = Field(default="gpt-5.2", alias="WORKBENCH_AGENT_MODEL")
    workbench_judge_model: str = Field(default="gpt-4.1", alias="WORKBENCH_JUDGE_MODEL")
    workbench_reasoning_effort: Literal["low", "medium", "high"] = Field(
        default="medium",
        alias="WORKBENCH_REASONING_EFFORT",
    )
    workbench_max_tool_rounds: int = Field(default=12, alias="WORKBENCH_MAX_TOOL_ROUNDS")
    workbench_enable_gateway_sidecars: bool = Field(
        default=True,
        alias="WORKBENCH_ENABLE_GATEWAY_SIDECARS",
    )


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
