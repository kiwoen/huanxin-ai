from __future__ import annotations

import pytest

from huanxin.core.integration import SystemIntegration


class _DecisionProvider:
    def __init__(self, actions: list[str]) -> None:
        self.actions = iter(actions)

    async def decide(self, request):
        from types import SimpleNamespace

        return SimpleNamespace(
            action=next(self.actions),
            confidence=1.0,
            reason_code="test",
            requires_approval=False,
        )


@pytest.mark.asyncio
async def test_harness_entrypoint_is_opt_in(monkeypatch, tmp_path) -> None:
    integration = SystemIntegration()
    provider = _DecisionProvider(["answer_directly"])

    class _Loop:
        max_steps = 8

        async def run(self, **kwargs):
            from types import SimpleNamespace

            return SimpleNamespace(success=True, status="complete", state={}, steps=1, error="")

    monkeypatch.setattr("huanxin.harness.HarnessLoop", lambda **kwargs: _Loop())
    monkeypatch.setattr("huanxin.harness.register_default_harness_tools", lambda: object())

    result = await integration.execute_harness(
        task_id="integration-task",
        task_type="test",
        max_steps=8,
    )

    assert result["success"] is True
    assert result["status"] == "complete"
    assert integration.status()["harness"]["loaded"] is True
