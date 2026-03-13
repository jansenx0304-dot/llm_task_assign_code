# sar_alloc/config.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


Direction = Literal["min", "max"]


@dataclass(slots=True)
class ObjectiveLayer:
    name: str
    metric: str
    direction: Direction = "min"
    epsilon: float = 0.0


@dataclass(slots=True)
class ObjectivePolicy:
    layers: List[ObjectiveLayer] = field(default_factory=list)
    max_layers: int = 6


def default_objective_policy() -> ObjectivePolicy:
    return ObjectivePolicy(
        layers=[
            ObjectiveLayer(name="feasibility", metric="violation_total", direction="min", epsilon=0.0),
            ObjectiveLayer(name="rescue_priority", metric="missed_priority", direction="min", epsilon=0.0),
            ObjectiveLayer(name="efficiency", metric="energy_total", direction="min", epsilon=0.0),
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
class ALNSConfig:
    destroy_frac: float = 0.12
    reaction_factor: float = 0.2
    acceptance: Literal["greedy", "threshold", "sa"] = "sa"
    accept_level: float = 0.3


@dataclass(slots=True)
class ILSConfig:
    perturb_frac: float = 0.10
    local_search_passes: int = 2
    perturb_operator: Literal["random_remove", "worst_remove", "segment_remove"] = "worst_remove"
    repair_operator: Literal["greedy_insert", "regret2_insert"] = "regret2_insert"


@dataclass(slots=True)
class InitConstructConfig:
    method: Literal["insert", "sweep"] = "insert"
    randomized: bool = True
    rcl_k: int = 5
    allow_unassigned: bool = True


@dataclass(slots=True)
class SolverConfig:
    algorithm: Literal["ils", "alns"] = "alns"
    ils: ILSConfig = field(default_factory=ILSConfig)
    alns: ALNSConfig = field(default_factory=ALNSConfig)


@dataclass(slots=True)
class Config:
    eval: EvaluationConfig = field(default_factory=EvaluationConfig)
    init: InitConstructConfig = field(default_factory=InitConstructConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    rng_seed: int = 0
    extras: Dict[str, float] = field(default_factory=dict)
