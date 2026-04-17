from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from .operators.types import (
    DESTROY_CANDIDATE_GENERATORS,
    MetricWeights,
    REPAIR_TASK_SELECTORS,
)


Direction = Literal["min", "max"]


@dataclass(slots=True)
class ObjectiveLayer:
    name: str
    metric: str
    direction: Direction = "min"


@dataclass(slots=True)
class ObjectivePolicy:
    layers: List[ObjectiveLayer] = field(default_factory=list)
    max_layers: int = 6


def default_objective_policy() -> ObjectivePolicy:
    return ObjectivePolicy(
        layers=[
            ObjectiveLayer(name="feasibility", metric="violation_total", direction="min"),
            ObjectiveLayer(name="rescue_priority", metric="missed_priority", direction="min"),
            ObjectiveLayer(name="efficiency", metric="energy_total", direction="min"),
        ],
        max_layers=6,
    )


@dataclass(slots=True)
class EvaluationConfig:
    objective_policy: ObjectivePolicy = field(default_factory=default_objective_policy)
    include_depot_legs: bool = True
    time_unit: str = "minute"
    energy_unit: str = "unit"


@dataclass(slots=True)
class Budget:
    time_limit_sec: Optional[float] = None
    max_iters: Optional[int] = None


@dataclass(slots=True)
class WeightedALNSConfig:
    """Static weighted-ALNS settings shared across runs.

    Task selectors decide repair order. `filtered_best_position` keeps its
    external name, but internally it means: rank filtered positions by insert
    score, then strict-evaluate them in that ranked order until a feasible
    insertion is found or all candidates are exhausted.
    """
    destroy_generator_priors: Dict[str, float] = field(
        default_factory=lambda: {
            name: 1.0 for name in DESTROY_CANDIDATE_GENERATORS
        }
    )
    repair_task_selector_priors: Dict[str, float] = field(
        default_factory=lambda: {
            name: 1.0 for name in REPAIR_TASK_SELECTORS
        }
    )
    repair_position_selector: Literal["filtered_best_position"] = "filtered_best_position"
    remove_metric_weights: MetricWeights = field(default_factory=MetricWeights)
    reinsert_metric_weights: MetricWeights = field(default_factory=MetricWeights)
    insert_metric_weights: MetricWeights = field(default_factory=MetricWeights)
    strength_ratio: float = 0.18
    acceptance: Literal["greedy", "threshold", "sa"] = "sa"
    accept_level: float = 0.25
    reaction_factor: float = 0.20
    prior_mix_lambda: float = 0.25
    default_time_limit_sec: float = 1.0
    default_max_iters: int = 60


@dataclass(slots=True)
class InitConstructConfig:
    """Initial construction aligned with weighted repair scoring.

    `task_top_k` limits how many highest-scored unassigned tasks are attempted
    each dynamic re-scoring round. `position_top_k` limits how many lowest-scored
    insertion positions receive strict feasibility evaluation for a chosen task.
    `rcl_k` only randomizes within those score-ranked prefixes.
    """

    method: Literal["weighted_insert"] = "weighted_insert"
    randomized: bool = True
    task_top_k: int = 4
    position_top_k: int = 4
    rcl_k: int = 5
    allow_unassigned: bool = True


@dataclass(slots=True)
class SolverConfig:
    weighted_alns: WeightedALNSConfig = field(default_factory=WeightedALNSConfig)


@dataclass(slots=True)
class Config:
    eval: EvaluationConfig = field(default_factory=EvaluationConfig)
    init: InitConstructConfig = field(default_factory=InitConstructConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    rng_seed: int = 0
    extras: Dict[str, float] = field(default_factory=dict)
