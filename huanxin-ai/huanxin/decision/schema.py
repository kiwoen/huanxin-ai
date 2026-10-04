"""Bounded, provider-neutral decision schemas for agent execution."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


DecisionAction = Literal[
    "answer_directly",
    "query_knowledge_base",
    "read_github",
    "read_file",
    "write_file",
    "run_test",
    "request_approval",
    "retry",
    "change_strategy",
    "stop",
]


class DecisionRequest(BaseModel):
    """The bounded state exposed to a decision model."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    task_type: str = Field(min_length=1)
    state: dict[str, Any] = Field(default_factory=dict)
    allowed_actions: list[DecisionAction] = Field(min_items=1)
    step: int = Field(default=0, ge=0)


class Decision(BaseModel):
    """A validated action chosen from the caller-provided allow-list."""

    model_config = ConfigDict(extra="forbid")

    action: DecisionAction
    confidence: float = Field(ge=0.0, le=1.0)
    reason_code: str = Field(min_length=1)
    requires_approval: bool = False


def parse_decision(raw: str | dict[str, Any], request: DecisionRequest) -> Decision:
    """Parse and constrain a model response.

    The model may only select an action already present in ``request``.  This
    is a safety boundary, not a replacement for the project's policy engine.
    """

    payload: Any
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("decision output must be valid JSON") from exc
    else:
        payload = raw

    try:
        validator = getattr(Decision, "model_validate", None)
        decision = validator(payload) if validator else Decision.parse_obj(payload)
    except ValidationError as exc:
        raise ValueError("decision output does not match the decision schema") from exc

    if decision.action not in request.allowed_actions:
        raise ValueError(f"decision action is not allowed: {decision.action}")

    return decision
