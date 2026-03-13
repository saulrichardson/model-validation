"""Gateway-backed authoring helpers for CECL demo upload packages."""

from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel

from ..models import ChatRequest, Message, Role
from ..settings import Settings
from ..sidecar import GatewaySidecarService
from .schemas import FullReviewDocumentSet, GapAssessmentDocumentSet

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class CeclAuthoringClient:
    """Use the gateway utility to author rich, bank-plausible CECL documents."""

    def __init__(self, settings: Settings, *, model: str | None = None) -> None:
        self._settings = settings
        self._model = model or settings.workbench_agent_model
        self._gateway = GatewaySidecarService(settings)

    async def shutdown(self) -> None:
        await self._gateway.shutdown()

    async def author_full_review_documents(
        self,
        spec: dict[str, Any],
    ) -> FullReviewDocumentSet:
        system_prompt = (
            "You are authoring internal CECL model risk artifacts for a bank review package. "
            "Return strict JSON only. Write in a serious bank documentation tone. "
            "Use the supplied specification exactly, including the documented horizon/reversion assumptions, "
            "scenario framing, overlay posture, and any stated control language. "
            "Do not mention that the materials are synthetic."
        )
        user_prompt = (
            "Generate a full CECL review upload package.\n\n"
            "Requirements:\n"
            "- Each field must contain markdown body content only.\n"
            "- The methodology must describe the documented horizon and reversion exactly as specified.\n"
            "- The overlay memo must sound realistic and may understate the effective overlay magnitude if the spec says so.\n"
            "- Governance minutes should read like internal committee notes.\n"
            "- Control notes should describe reproducibility and reporting practices in a plausible internal tone.\n\n"
            f"Specification:\n{json.dumps(spec, indent=2)}"
        )
        return await self._author(FullReviewDocumentSet, system_prompt, user_prompt)

    async def author_gap_assessment_documents(
        self,
        spec: dict[str, Any],
    ) -> GapAssessmentDocumentSet:
        system_prompt = (
            "You are authoring internal CECL documentation artifacts for a documentation-led review package. "
            "Return strict JSON only. Write in a serious bank documentation tone. "
            "Use the supplied specification exactly, including intended inconsistencies, missing evidence, "
            "and open action items. Do not mention that the materials are synthetic."
        )
        user_prompt = (
            "Generate a CECL documentation-led gap assessment upload package.\n\n"
            "Requirements:\n"
            "- Each field must contain markdown body content only.\n"
            "- The methodology and model overview may disagree where the specification says they should.\n"
            "- The evidence request log and gap tracker should read like real internal working materials.\n"
            "- Governance minutes should explicitly limit the package to non-execution review if the spec says runtime evidence is missing.\n\n"
            f"Specification:\n{json.dumps(spec, indent=2)}"
        )
        return await self._author(GapAssessmentDocumentSet, system_prompt, user_prompt)

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
            temperature=0.2,
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
