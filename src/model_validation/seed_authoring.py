"""Gateway-backed authoring helpers for rich seed-bank documents."""

from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from .models import ChatRequest, Message, Role
from .settings import Settings
from .sidecar import GatewaySidecarService


class MaterialChangeDocumentSet(BaseModel):
    methodology_md: str
    development_summary_md: str
    change_request_md: str
    prior_validation_memo_md: str
    monitoring_plan_md: str
    validation_test_plan_md: str
    governance_minutes_md: str
    implementation_runbook_md: str
    issue_log_md: str


class DocumentationDocumentSet(BaseModel):
    model_methodology_md: str
    model_card_md: str
    prior_validation_memo_md: str
    monitoring_plan_md: str
    governance_minutes_md: str
    assumptions_register_md: str
    evidence_request_log_md: str
    policy_exception_memo_md: str


ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class SeedAuthoringClient:
    """Use the gateway utility to author rich, fixed-schema seed documents."""

    def __init__(self, settings: Settings, *, model: str | None = None) -> None:
        self._settings = settings
        self._model = model or settings.workbench_seed_authoring_model
        self._gateway = GatewaySidecarService(settings)

    async def shutdown(self) -> None:
        await self._gateway.shutdown()

    async def author_material_change_documents(
        self,
        spec: dict[str, Any],
    ) -> MaterialChangeDocumentSet:
        system_prompt = (
            "You are authoring synthetic but bank-plausible model-validation upload artifacts. "
            "Return strict JSON only. Write in a serious bank documentation tone. "
            "Use the supplied seed specification exactly, including intentional gaps, stale references, "
            "or inconsistencies. Do not mention that the content is synthetic."
        )
        user_prompt = (
            "Generate a full document pack for a bank material-change revalidation upload.\n\n"
            "Requirements:\n"
            "- Each field must contain markdown or plain text body content only.\n"
            "- Reflect the specified product context, threshold changes, reason-code treatment, and quality profile.\n"
            "- Include deliberate issues only where the spec says to include them.\n"
            "- Governance minutes should read like internal committee notes.\n"
            "- Issue log should be concise and realistic.\n\n"
            f"Seed specification:\n{json.dumps(spec, indent=2)}"
        )
        return await self._author(MaterialChangeDocumentSet, system_prompt, user_prompt)

    async def author_documentation_documents(
        self,
        spec: dict[str, Any],
    ) -> DocumentationDocumentSet:
        system_prompt = (
            "You are authoring synthetic but bank-plausible documentation-only validation upload artifacts. "
            "Return strict JSON only. Write in a serious bank documentation tone. "
            "Use the supplied seed specification exactly, including intentional inconsistencies, omissions, "
            "and open evidence requests. Do not mention that the content is synthetic."
        )
        user_prompt = (
            "Generate a documentation-led model validation readiness pack.\n\n"
            "Requirements:\n"
            "- Each field must contain markdown or plain text body content only.\n"
            "- Reflect the stated model purpose, feature coverage, monitoring claims, and documentation quality profile.\n"
            "- Include the requested internal inconsistencies only where specified.\n"
            "- Governance minutes and policy exception memo should sound like real institutional artifacts.\n\n"
            f"Seed specification:\n{json.dumps(spec, indent=2)}"
        )
        return await self._author(DocumentationDocumentSet, system_prompt, user_prompt)

    async def _author(
        self,
        response_model: type[ResponseModelT],
        system_prompt: str,
        user_prompt: str,
    ) -> ResponseModelT:
        request = ChatRequest(
            provider="openai",
            model=self._model,
            messages=[
                Message(role=Role.SYSTEM, content=system_prompt),
                Message(role=Role.USER, content=user_prompt),
            ],
            temperature=0.3,
            metadata={
                "response_format": {
                    "type": "json_schema",
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                    "strict": False,
                }
            },
        )
        response = await self._gateway.chat(request)
        return response_model.model_validate_json(response.output_text)
