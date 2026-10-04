from __future__ import annotations

from types import SimpleNamespace

import pytest

from huanxin.decision import DecisionRequest
from huanxin.harness import HarnessLoop
from huanxin.tools.github_readonly import register_github_tools
from huanxin.tools.base import ToolDef, ToolResult
from huanxin.tools.registry import ToolRegistry
from huanxin.tools.audit_trail import AuditTrail


class _DecisionProvider:
    def __init__(self, actions: list[str]) -> None:
        self.actions = iter(actions)

    async def decide(self, request: DecisionRequest):
        return SimpleNamespace(
            action=next(self.actions),
            confidence=1.0,
            reason_code="test",
            requires_approval=False,
        )


@pytest.mark.asyncio
async def test_harness_loop_executes_registered_tool_and_stops() -> None:
    registry = ToolRegistry()
    registry.register_tool(
        ToolDef(
            name="github_read_file",
            description="test",
            func=lambda **kwargs: ToolResult(success=True, data={"ok": True}),
        )
    )
    loop = HarnessLoop(
        decision_provider=_DecisionProvider(["read_github", "stop"]),
        registry=registry,
        max_steps=3,
    )

    result = await loop.run(
        task_id="task-1",
        task_type="github_analysis",
        state={"tool_arguments": {"owner": "kiwoen", "repo": "huanxin-ai", "path": "README.md"}},
        allowed_actions=["read_github", "stop"],
    )

    assert result.success is True
    assert result.status == "stopped"
    assert result.state["last_tool"] == "github_read_file"


@pytest.mark.asyncio
async def test_harness_loop_has_a_hard_step_limit() -> None:
    registry = ToolRegistry()
    registry.register_tool(
        ToolDef(name="github_read_file", description="test", func=lambda **kwargs: {"ok": True})
    )
    loop = HarnessLoop(
        decision_provider=_DecisionProvider(["read_github", "read_github", "read_github"]),
        registry=registry,
        max_steps=2,
    )

    result = await loop.run(
        task_id="task-2",
        task_type="github_analysis",
        state={"tool_arguments": {}},
        allowed_actions=["read_github"],
    )

    assert result.success is False
    assert result.status == "max_steps"


@pytest.mark.asyncio
async def test_harness_loop_records_tool_audit(tmp_path) -> None:
    registry = ToolRegistry()
    registry.register_tool(
        ToolDef(name="github_read_file", description="test", func=lambda **kwargs: {"ok": True})
    )
    audit = AuditTrail(str(tmp_path / "audit.db"), auto_archive=False)
    loop = HarnessLoop(
        decision_provider=_DecisionProvider(["read_github", "stop"]),
        registry=registry,
        audit=audit,
    )

    result = await loop.run(
        task_id="audit-task",
        task_type="github_analysis",
        state={"tool_arguments": {}},
        allowed_actions=["read_github", "stop"],
    )

    assert result.success is True
    records = [record for record in audit.get_recent(20) if record.task_id == "audit-task"]
    assert len(records) == 1


def test_register_github_tools_is_idempotent() -> None:
    registry = ToolRegistry()
    register_github_tools(registry)
    register_github_tools(registry)

    assert registry.get_tool("github_read_file") is not None
    assert registry.get_tool("github_list_repository") is not None
    assert registry.tool_count() == 2
