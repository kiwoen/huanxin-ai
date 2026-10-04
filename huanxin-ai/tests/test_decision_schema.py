from __future__ import annotations

import pytest

from huanxin.decision import DecisionRequest, parse_decision


def _request() -> DecisionRequest:
    return DecisionRequest(
        task_id="task-1",
        task_type="github_analysis",
        allowed_actions=["read_github", "request_approval", "stop"],
    )


def test_parse_decision_accepts_allowed_action() -> None:
    decision = parse_decision(
        '{"action":"read_github","confidence":0.92,"reason_code":"needs_repo"}',
        _request(),
    )

    assert decision.action == "read_github"
    assert decision.confidence == 0.92


def test_parse_decision_rejects_action_outside_allow_list() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        parse_decision(
            '{"action":"write_file","confidence":0.99,"reason_code":"edit"}',
            _request(),
        )


def test_parse_decision_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        parse_decision("not-json", _request())
