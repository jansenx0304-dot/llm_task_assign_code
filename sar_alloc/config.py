from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


Direction = Literal["min", "max"]


@dataclass(slots=True)
class ObjectiveLayer:
    name: str
    metric: str
    direction: Direction = "min"


@dataclass(slots=True)
class ObjectivePolicy:
    """Objective selected by the LLM for the current run."""

    layers: List[ObjectiveLayer] = field(default_factory=list)
    max_layers: int = 6


@dataclass(slots=True)
class EvaluationConfig:
    objective_policy: ObjectivePolicy = field(default_factory=ObjectivePolicy)
    include_depot_legs: bool = True
    time_unit: str = "minute"
    energy_unit: str = "unit"


@dataclass(slots=True)
class Budget:
    time_limit_sec: Optional[float] = None
    max_iters: Optional[int] = None


@dataclass(slots=True)
class SolverConfig:
    """Placeholder for non-strategy solver settings.

    Weighted ALNS operator weights, metric weights, acceptance, and budget
    requests are intentionally absent. They must come from the LLM action plan
    or from the explicitly labeled demo policy in dummy/fallback mode.
    """


@dataclass(slots=True)
class Config:
    eval: EvaluationConfig = field(default_factory=EvaluationConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    rng_seed: int = 0
    extras: Dict[str, Any] = field(default_factory=dict)
