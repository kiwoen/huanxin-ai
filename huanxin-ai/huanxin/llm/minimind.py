"""Optional OpenAI-compatible MiniMind provider.

MiniMind is intentionally treated as a remote/local provider boundary.  The
provider does not import or depend on MiniMind's training implementation; it
only talks to its OpenAI-compatible inference service.  This keeps training,
serving, and Huanxin orchestration independently replaceable.
"""

from __future__ import annotations

import os
from typing import Any, Protocol

from huanxin.decision import Decision, DecisionRequest, parse_decision


class _AsyncChatCompletions(Protocol):
    async def create(self, **kwargs: Any) -> Any: ...


class _AsyncClient(Protocol):
    chat: Any


class MiniMindProvider:
    """Call a local MiniMind server using the OpenAI-compatible API shape."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        client: _AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("HUANXIN_MINIMIND_BASE_URL", "http://127.0.0.1:8001/v1")).rstrip("/")
        self.api_key = api_key or os.getenv("HUANXIN_MINIMIND_API_KEY", "local")
        self.model = model or os.getenv("HUANXIN_MINIMIND_MODEL", "minimind-decision")
        self._client = client

    @property
    def configured(self) -> bool:
        """Whether a client was injected or the OpenAI SDK is available."""
        if self._client is not None:
            return True
        try:
            import openai  # noqa: F401
        except ImportError:
            return False
        return True

    def _get_client(self) -> _AsyncClient:
        if self._client is not None:
            return self._client
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("MiniMind provider requires the openai package") from exc
        self._client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        """Return the text content from a MiniMind chat completion."""
        kwargs: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format

        response = await self._get_client().chat.completions.create(**kwargs)
        try:
            return response.choices[0].message.content or ""
        except (AttributeError, IndexError, TypeError) as exc:
            raise RuntimeError("MiniMind returned an invalid chat response") from exc

    async def decide(self, request: DecisionRequest) -> Decision:
        """Ask MiniMind for a bounded decision and validate its action."""
        prompt = {
            "task_id": request.task_id,
            "task_type": request.task_type,
            "state": request.state,
            "allowed_actions": request.allowed_actions,
            "step": request.step,
        }
        raw = await self.chat(
            [
                {
                    "role": "system",
                    "content": "你是幻炘AI的受限决策器，只输出合法JSON，不得选择未提供的动作。",
                },
                {"role": "user", "content": str(prompt)},
            ],
            model=self.model,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return parse_decision(raw, request)

