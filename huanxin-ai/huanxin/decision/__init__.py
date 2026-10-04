"""Structured decision contracts for the Huanxin harness.

The decision layer deliberately returns a bounded action instead of free-form
instructions.  A local MiniMind decision model can implement this contract,
while GPT or a rule engine can remain a fallback.
"""

from huanxin.decision.schema import Decision, DecisionRequest, parse_decision

__all__ = ["Decision", "DecisionRequest", "parse_decision"]
