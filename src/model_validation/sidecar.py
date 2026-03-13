"""Thin client for bounded sidecar analyses routed through the gateway utility."""

from __future__ import annotations

import uuid
from typing import Any

from .client import GatewayAgentClient
from .models import ChatRequest, ChatResponse, Message
from .settings import Settings


class GatewaySidecarService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = GatewayAgentClient(
            base_url=settings.gateway_base_url,
            timeout=settings.gateway_timeout_seconds,
        )

    async def shutdown(self) -> None:
        await self._client.aclose()

    async def chat(self, request: ChatRequest, trace_id: str | None = None) -> ChatResponse:
        if not self._settings.workbench_enable_gateway_sidecars:
            raise RuntimeError("Gateway sidecars are disabled by configuration.")

        response_format = _extract_response_format(request.metadata)
        reasoning = _extract_reasoning(request.metadata)
        metadata = _residual_metadata(request.metadata)
        result = await self._client.complete_response(
            model=_qualified_model(request),
            input_messages=[_message_payload(message) for message in request.messages],
            response_format=response_format,
            reasoning=reasoning,
            metadata=metadata or None,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )
        completed = result.get("meta") or {}
        response_meta = completed.get("response") if isinstance(completed, dict) else {}
        usage = response_meta.get("usage", {}) if isinstance(response_meta, dict) else {}
        provider_request_id = response_meta.get("id") if isinstance(response_meta, dict) else None
        model = response_meta.get("model", request.model) if isinstance(response_meta, dict) else request.model
        return ChatResponse(
            provider=request.provider,
            model=str(model),
            output_text=str(result.get("text", "")),
            usage=usage if isinstance(usage, dict) else {},
            trace_id=trace_id or uuid.uuid4().hex,
            conversation_id=request.conversation_id,
            agent_id=request.agent_id,
            provider_request_id=str(provider_request_id) if provider_request_id else None,
        )


def _qualified_model(request: ChatRequest) -> str:
    if ":" in request.model:
        return request.model
    return f"{request.provider}:{request.model}"


def _message_payload(message: Message) -> dict[str, Any]:
    return {
        "role": message.role.value,
        "content": message.content,
    }


def _extract_response_format(metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    if not metadata:
        return None
    value = metadata.get("response_format")
    if isinstance(value, dict):
        return value
    text = metadata.get("text")
    if isinstance(text, dict):
        format_value = text.get("format")
        if isinstance(format_value, dict):
            return format_value
    return None


def _extract_reasoning(metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    if not metadata:
        return None
    value = metadata.get("reasoning")
    return value if isinstance(value, dict) else None


def _residual_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if not metadata:
        return {}
    residual = dict(metadata)
    residual.pop("response_format", None)
    residual.pop("reasoning", None)
    residual.pop("text", None)
    return residual
