from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


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
class ALNSConfig:
    destroy_frac: float = 0.12
    reaction_factor: float = 0.2
    acceptance: Literal["greedy", "threshold", "sa"] = "sa"
    accept_level: float = 0.3


@dataclass(slots=True)
class InitConstructConfig:
    method: Literal["insert", "sweep"] = "insert"
    randomized: bool = True
    rcl_k: int = 5
    allow_unassigned: bool = True


@dataclass(slots=True)
class SolverConfig:
    alns: ALNSConfig = field(default_factory=ALNSConfig)


@dataclass(slots=True)
class Config:
    eval: EvaluationConfig = field(default_factory=EvaluationConfig)
    init: InitConstructConfig = field(default_factory=InitConstructConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    rng_seed: int = 0
    extras: Dict[str, float] = field(default_factory=dict)
