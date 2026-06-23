"""Typed internal policies compiled from the small public LLM controls."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict, Tuple

DESTROY_OPERATOR_NAMES: Tuple[str, ...] = (
    "random_removal",
    "worst_task_removal",
    "related_cluster_removal",
    "critical_block_removal",
    "route_rebalance_removal",
)
INSERTION_OPERATOR_NAMES: Tuple[str, ...] = (
    "greedy_insertion",
    "scarcity_first_insertion",
    "regret_insertion",
    "bottleneck_insertion",
    "diversified_insertion",
)
DESTROY_SIGNAL_NAMES: Tuple[str, ...] = (
    "cost_pressure",
    "coupling_pressure",
    "route_balance_pressure",
    "mobility_opportunity",
    "scarcity_protection",
)
INSERTION_TASK_SIGNAL_NAMES: Tuple[str, ...] = (
    "priority_loss",
    "scarcity_pressure",
    "regret_pressure",
    "bottleneck_pressure",
    "mobility_opportunity",
)
INSERTION_POSITION_SIGNAL_NAMES: Tuple[str, ...] = (
    "insert_cost",
    "future_slack",
    "route_balance_gain",
    "local_coupling_penalty",
    "diversity_gain",
)
ACCEPTANCE_MODES: Tuple[str, ...] = ("greedy", "threshold", "sa")


@dataclass(frozen=True, slots=True)
class DestroyPolicy:
    operator_weights: Dict[str, int]
    signal_weights: Dict[str, int]
    intensity_score: int
    remove_ratio: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "operator_weights": dict(self.operator_weights),
            "signal_weights": dict(self.signal_weights),
            "intensity_score": self.intensity_score,
            "remove_ratio": self.remove_ratio,
        }


@dataclass(frozen=True, slots=True)
class InsertionPolicy:
    operator_weights: Dict[str, int]
    task_signal_weights: Dict[str, int]
    position_signal_weights: Dict[str, int]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "operator_weights": dict(self.operator_weights),
            "task_signal_weights": dict(self.task_signal_weights),
            "position_signal_weights": dict(self.position_signal_weights),
        }


@dataclass(frozen=True, slots=True)
class AcceptancePolicy:
    mode: str
    intensity_score: int
    accept_level: float
    exploration_score: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "intensity_score": self.intensity_score,
            "accept_level": self.accept_level,
            "exploration_score": self.exploration_score,
        }


@dataclass(frozen=True, slots=True)
class CompiledALNSPolicy:
    destroy_policy: DestroyPolicy
    insertion_policy: InsertionPolicy
    acceptance_policy: AcceptancePolicy
    reaction_factor: float = 0.20
    prior_mix_lambda: float = 0.25

    def as_dict(self) -> Dict[str, Any]:
        return {
            "destroy_policy": self.destroy_policy.as_dict(),
            "insertion_policy": self.insertion_policy.as_dict(),
            "acceptance_policy": self.acceptance_policy.as_dict(),
            "reaction_factor": self.reaction_factor,
            "prior_mix_lambda": self.prior_mix_lambda,
        }


@dataclass(frozen=True, slots=True)
class SolverRequest:
    time_limit_sec: float
    max_iters: int

    def as_dict(self) -> Dict[str, Any]:
        return {"time_limit_sec": self.time_limit_sec, "max_iters": self.max_iters}


@dataclass(frozen=True, slots=True)
class LandscapeFeatures:
    cost_pressure: float
    priority_loss: float
    scarcity_pressure: float
    coupling_pressure: float
    mobility_opportunity: float
    route_balance_pressure: float
    violation_pressure: float
    regret_pressure: float
    bottleneck_pressure: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class PositionFeatures:
    insert_cost: float
    future_slack: float
    route_balance_gain: float
    local_coupling_penalty: float
    diversity_gain: float
    violation_delta: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class InsertPosition:
    agent_id: int
    position: int

    def as_dict(self) -> Dict[str, int]:
        return {"agent_id": self.agent_id, "position": self.position}


__all__ = [
    "ACCEPTANCE_MODES",
    "DESTROY_OPERATOR_NAMES",
    "DESTROY_SIGNAL_NAMES",
    "INSERTION_OPERATOR_NAMES",
    "INSERTION_TASK_SIGNAL_NAMES",
    "INSERTION_POSITION_SIGNAL_NAMES",
    "DestroyPolicy",
    "InsertionPolicy",
    "AcceptancePolicy",
    "CompiledALNSPolicy",
    "SolverRequest",
    "LandscapeFeatures",
    "PositionFeatures",
    "InsertPosition",
]
