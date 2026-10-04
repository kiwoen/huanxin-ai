"""A small, bounded harness loop built on existing Huanxin registries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from huanxin.decision import DecisionRequest
from huanxin.llm.minimind import MiniMindProvider
from huanxin.tools.registry import ToolRegistry, get_registry


class DecisionProvider(Protocol):
    async def decide(self, request: DecisionRequest): ...


@dataclass
class LoopResult:
    success: bool
    status: str
    state: dict[str, Any] = field(default_factory=dict)
    steps: int = 0
    error: str = ""


class HarnessLoop:
    """Execute bounded read-oriented tool loops with a decision provider."""

    def __init__(
        self,
        *,
        decision_provider: DecisionProvider | None = None,
        registry: ToolRegistry | None = None,
        max_steps: int = 8,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.decision_provider = decision_provider or MiniMindProvider()
        self.registry = registry or get_registry()
        self.max_steps = max_steps

    async def run(
        self,
        *,
        task_id: str,
        task_type: str,
        state: dict[str, Any] | None = None,
        allowed_actions: list[str] | None = None,
    ) -> LoopResult:
        current_state = dict(state or {})
        actions = allowed_actions or ["answer_directly", "read_github", "read_file", "stop"]

        for step in range(self.max_steps):
            request = DecisionRequest(
                task_id=task_id,
                task_type=task_type,
                state=current_state,
                allowed_actions=actions,
                step=step,
            )
            try:
                decision = await self.decision_provider.decide(request)
            except Exception as exc:
                return LoopResult(False, "decision_error", current_state, step, str(exc))

            if decision.action == "stop":
                return LoopResult(True, "stopped", current_state, step + 1)
            if decision.action == "answer_directly":
                return LoopResult(True, "complete", current_state, step + 1)
            if decision.action == "request_approval":
                return LoopResult(False, "approval_required", current_state, step + 1)

            tool_name = {
                "read_github": "github_read_file",
                "read_file": "file_info",
            }.get(decision.action)
            if not tool_name:
                return LoopResult(False, "unsupported_action", current_state, step + 1, decision.action)

            arguments = current_state.get("tool_arguments", {})
            result = self.registry.execute_tool(tool_name, arguments)
            current_state["last_tool"] = tool_name
            current_state["last_result"] = result.to_dict()
            if not result.success:
                return LoopResult(False, "tool_error", current_state, step + 1, result.error)

            current_state["tool_data"] = result.data

        return LoopResult(False, "max_steps", current_state, self.max_steps, "maximum steps reached")

