"""Step agent decision semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class StepDecision:
    action: str
    intent_id: str
    decision_basis: List[Dict[str, Any]]
    situation_summary: Dict[str, Any]
    raw: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "intent_id": self.intent_id,
            "decision_basis": [dict(item) for item in self.decision_basis],
            "situation_summary": dict(self.situation_summary),
            "raw": dict(self.raw),
        }


@dataclass(slots=True)
class RuntimeControl:
    action: str
    intent_id: str
    runtime_target: Dict[str, Any]
    insertion_policy: Any | None = None
    destroy_policy: Any | None = None
    acceptance_policy: Any | None = None
    feasibility_policy: Dict[str, Any] | None = None
    protected_metrics: List[Dict[str, Any]] = field(default_factory=list)
    solver_budget: Dict[str, Any] = field(default_factory=dict)
    review_request: Dict[str, Any] | None = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "intent_id": self.intent_id,
            "runtime_target": dict(self.runtime_target),
            "insertion_policy": _policy_dict(self.insertion_policy),
            "destroy_policy": _policy_dict(self.destroy_policy),
            "acceptance_policy": _policy_dict(self.acceptance_policy),
            "feasibility_policy": dict(self.feasibility_policy or {}),
            "protected_metrics": [dict(item) for item in self.protected_metrics],
            "solver_budget": dict(self.solver_budget),
            "review_request": None if self.review_request is None else dict(self.review_request),
        }


def _policy_dict(value: Any) -> Dict[str, Any] | None:
    if value is None:
        return None
    if hasattr(value, "as_dict"):
        return value.as_dict()
    return dict(value)


__all__ = ["RuntimeControl", "StepDecision"]
