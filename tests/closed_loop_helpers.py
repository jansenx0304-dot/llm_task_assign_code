from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from sar_alloc.config import Config, ObjectiveLayer
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.tools import SearchContract


def tiny_instance() -> Instance:
    return Instance(
        tasks=(
            Task(1, (1.0, 0.0), 0.0, 30.0, 1.0, {"a"}, 8.0),
            Task(2, (2.0, 0.0), 0.0, 30.0, 1.0, {"a"}, 3.0),
            Task(3, (3.0, 0.0), 0.0, 30.0, 1.0, {"rare"}, 5.0),
        ),
        agents=(
            Agent(0, 100.0, {"a", "rare"}, 1.0, 1.0, 0.0, {"a": 1.0, "rare": 1.0}),
            Agent(1, 100.0, {"a"}, 1.0, 1.0, 0.0, {"a": 1.0}),
        ),
        depot=Depot(0, (0.0, 0.0)),
    )


def configured() -> Config:
    config = Config()
    config.eval.objective_policy.layers = [
        ObjectiveLayer("missed_priority", "missed_priority", "min"),
        ObjectiveLayer("energy_total", "energy_total", "min"),
    ]
    return config


def contract(
    *,
    objective: list[str] | None = None,
    success: list[Dict[str, Any]] | None = None,
    failure: list[Dict[str, Any]] | None = None,
    min_actions: int = 1,
    max_actions: int = 2,
) -> SearchContract:
    return SearchContract(
        contract_id="C1",
        contract_type="alns_search",
        objective_layers=[{"metric": name, "direction": "min"} for name in (objective or ["missed_priority", "energy_total"])],
        feasibility_control={"mode": "strict", "relaxation_ratios": []},
        feasibility_policy={"mode": "strict"},
        target_policy={"preferred_target_kinds": ["unassigned_priority"]},
        protected_metrics=[],
        resource_policy={"min_actions": min_actions, "max_actions": max_actions, "max_iters": 100, "max_time_sec": 100.0},
        exit_conditions={"success": success or [], "failure": failure or []},
    )


@dataclass
class Report:
    is_feasible: bool = True
    violation_total: float = 0.0
    violation_ratio_by_type: Dict[str, float] | None = None

    def __post_init__(self) -> None:
        self.violation_ratio_by_type = self.violation_ratio_by_type or {"time_window": 0.0, "energy": 0.0}


@dataclass
class Evaluation:
    quality_metrics: Dict[str, float]
    constraint_report: Report = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.constraint_report = self.constraint_report or Report()

    @property
    def is_feasible(self) -> bool:
        return self.constraint_report.is_feasible

    def get_quality_metric(self, name: str) -> float:
        return float(self.quality_metrics.get(name, 0.0))

    def get_metric(self, name: str) -> float:
        return self.get_quality_metric(name)
