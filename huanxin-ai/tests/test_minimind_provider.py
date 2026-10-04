from __future__ import annotations

from types import SimpleNamespace

import pytest

from huanxin.decision import DecisionRequest
from huanxin.llm.minimind import MiniMindProvider


class _Completions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))]
        )


class _Client:
    def __init__(self, content: str) -> None:
        self.completions = _Completions(content)
        self.chat = SimpleNamespace(completions=self.completions)


@pytest.mark.asyncio
async def test_minimind_chat_uses_openai_compatible_client() -> None:
    client = _Client("hello")
    provider = MiniMindProvider(client=client, model="minimind-chat")

    result = await provider.chat([{"role": "user", "content": "hi"}])

    assert result == "hello"
    assert client.completions.calls[0]["model"] == "minimind-chat"


@pytest.mark.asyncio
async def test_minimind_decide_validates_bounded_action() -> None:
    client = _Client(
        '{"action":"read_github","confidence":0.95,"reason_code":"repo_needed"}'
    )
    provider = MiniMindProvider(client=client)
    request = DecisionRequest(
        task_id="task-1",
        task_type="github_analysis",
        allowed_actions=["read_github", "stop"],
    )

    result = await provider.decide(request)

    assert result.action == "read_github"
    assert client.completions.calls[0]["response_format"] == {"type": "json_object"}
