"""Supervisor stage data structures and stage lifecycle state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(slots=True)
class StageCompletion:
    completed: bool
    status: str
    reason: str

    def as_dict(self) -> Dict[str, Any]:
        return {"completed": self.completed, "status": self.status, "reason": self.reason}


@dataclass(slots=True)
class StageProgress:
    actions_used: int = 0
    iters_used: int = 0
    time_sec_used: float = 0.0
    last_quality_delta: Dict[str, float] | None = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "actions_used": int(self.actions_used),
            "iters_used": int(self.iters_used),
            "time_sec_used": round(float(self.time_sec_used), 6),
            "last_quality_delta": None if self.last_quality_delta is None else dict(self.last_quality_delta),
        }


@dataclass(slots=True)
class StagePlan:
    stage_id: str
    stage_type: str
    objective_layers: List[Dict[str, str]]
    target_intents: List[Dict[str, Any]]
    feasibility_policy: Dict[str, Any]
    protected_metrics: List[Dict[str, Any]]
    resource_policy: Dict[str, Any]
    protected_metric_baseline: Dict[str, float] = field(default_factory=dict)
    progress: StageProgress = field(default_factory=StageProgress)
    raw: Dict[str, Any] = field(default_factory=dict)

    def remaining(self) -> Dict[str, Any]:
        return {
            "actions": max(0, int(self.resource_policy.get("max_actions", 0)) - self.progress.actions_used),
            "time_sec": max(0.0, float(self.resource_policy.get("max_time_sec", 0.0)) - self.progress.time_sec_used),
            "iters": max(0, int(self.resource_policy.get("max_iters", 0)) - self.progress.iters_used),
            "min_actions_remaining": max(0, int(self.resource_policy.get("min_actions", 1)) - self.progress.actions_used),
        }

    def apply_result(self, result: Mapping[str, Any]) -> None:
        self.progress.actions_used += 1
        self.progress.time_sec_used += float(result.get("time_sec_used", 0.0) or 0.0)
        self.progress.iters_used += int(result.get("iters_used", 0) or 0)
        self.progress.last_quality_delta = {
            str(k): float(v) for k, v in dict(result.get("quality_delta", {}) or {}).items()
        }

    def is_complete(self, state: Any) -> StageCompletion:
        min_actions = int(self.resource_policy.get("min_actions", 1) or 1)
        if self.progress.actions_used < min_actions:
            return StageCompletion(False, "running", "min_actions_not_reached")

        if bool(self.resource_policy.get("require_feasible", False)):
            feasible = bool((getattr(state, "working_summary", {}) or {}).get("feasibility_summary", {}).get("is_feasible", False))
            if feasible:
                return StageCompletion(True, "success", "require_feasible_met")

        thresholds = dict(self.resource_policy.get("metric_thresholds", {}) or {})
        if thresholds and _thresholds_met(getattr(state, "working_summary", {}) or {}, thresholds):
            return StageCompletion(True, "success", "metric_thresholds_met")

        remaining = self.remaining()
        if remaining["actions"] <= 0:
            return StageCompletion(True, "budget_exhausted", "max_actions_reached")
        if remaining["time_sec"] <= 0:
            return StageCompletion(True, "budget_exhausted", "max_time_reached")
        if remaining["iters"] <= 0:
            return StageCompletion(True, "budget_exhausted", "max_iters_reached")
        return StageCompletion(False, "running", "")

    def as_observation(self) -> Dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_type": self.stage_type,
            "objective_layers": [dict(item) for item in self.objective_layers],
            "target_intents": [dict(item) for item in self.target_intents],
            "feasibility_policy": dict(self.feasibility_policy),
            "protected_metrics": [dict(item) for item in self.protected_metrics],
            "protected_metric_baseline": dict(self.protected_metric_baseline),
            "resource_policy": dict(self.resource_policy),
            "progress": self.progress.as_dict(),
            "remaining": self.remaining(),
        }


@dataclass(slots=True)
class SupervisorDecision:
    action: str
    global_objective: List[Dict[str, str]]
    next_stage: StagePlan | None
    raw: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "global_objective": [dict(item) for item in self.global_objective],
            "next_stage": None if self.next_stage is None else self.next_stage.as_observation(),
            "raw": dict(self.raw),
        }


def _thresholds_met(summary: Mapping[str, Any], thresholds: Mapping[str, Any]) -> bool:
    quality = dict((summary.get("quality_summary", {}) if isinstance(summary, Mapping) else {}) or {})
    feasibility = dict((summary.get("feasibility_summary", {}) if isinstance(summary, Mapping) else {}) or {})
    metrics = {**quality, **feasibility, **dict(feasibility.get("violation_by_type", {}) or {})}
    for metric, raw_limit in thresholds.items():
        if str(metric) not in metrics:
            return False
        if float(metrics[str(metric)]) > float(raw_limit):
            return False
    return True


__all__ = ["StageCompletion", "StagePlan", "StageProgress", "SupervisorDecision"]
