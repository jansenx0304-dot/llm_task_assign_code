from __future__ import annotations

"""Typed objects for the unified weighted-operator ALNS architecture.

Repair is explicitly split into task selectors and one position selector. The
external selector name `filtered_best_position` is stable, but its semantics are
insert-score ranking plus progressive strict evaluation.
"""

from dataclasses import dataclass, fields
from typing import Any, Dict, Tuple


METRIC_FIELDS: Tuple[str, ...] = (
    "priority",
    "tw_tightness",
    "violation_risk",
    "energy_pressure",
    "detour_cost",
    "service_burden",
    "feasibility_scarcity",
    "route_instability",
)

DESTROY_CANDIDATE_GENERATORS: Tuple[str, ...] = (
    "global_assigned",
    "random_subset",
    "route_segment",
    "route_tail",
    "single_route",
)

REPAIR_TASK_SELECTORS: Tuple[str, ...] = (
    "weighted_priority_order",
    "regret2_order",
)

REPAIR_POSITION_SELECTORS: Tuple[str, ...] = ("filtered_best_position",)

ACCEPTANCE_MODES: Tuple[str, ...] = (
    "greedy",
    "threshold",
    "sa",
)

METRIC_WEIGHT_BOUNDS: Dict[str, Tuple[float, float]] = {
    "priority": (0.0, 5.0),
    "tw_tightness": (0.0, 5.0),
    "violation_risk": (0.0, 8.0),
    "energy_pressure": (0.0, 5.0),
    "detour_cost": (0.0, 5.0),
    "service_burden": (0.0, 5.0),
    "feasibility_scarcity": (0.0, 5.0),
    "route_instability": (0.0, 3.0),
}

POLICY_BOUNDS: Dict[str, Tuple[float, float]] = {
    "strength_ratio": (0.02, 0.40),
    "reaction_factor": (0.05, 0.40),
    "accept_level": (0.0, 1.0),
    "prior_mix_lambda": (0.20, 0.35),
}

OPERATOR_PRIOR_BOUNDS: Tuple[float, float] = (0.10, 5.0)


@dataclass(frozen=True, slots=True)
class MetricWeights:
    priority: float = 1.5
    tw_tightness: float = 1.2
    violation_risk: float = 4.0
    energy_pressure: float = 1.6
    detour_cost: float = 1.4
    service_burden: float = 0.8
    feasibility_scarcity: float = 2.2
    route_instability: float = 0.7

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class RemoveFeatures:
    priority: float
    tw_tightness: float
    violation_risk: float
    energy_pressure: float
    detour_cost: float
    service_burden: float
    feasibility_scarcity: float
    route_instability: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class ReinsertTaskFeatures:
    priority: float
    tw_tightness: float
    violation_risk: float
    energy_pressure: float
    detour_cost: float
    service_burden: float
    feasibility_scarcity: float
    route_instability: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class InsertCandidateFeatures:
    priority: float
    tw_tightness: float
    violation_risk: float
    energy_pressure: float
    detour_cost: float
    service_burden: float
    feasibility_scarcity: float
    route_instability: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class InsertPosition:
    agent_id: int
    position: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "agent_id": int(self.agent_id),
            "position": int(self.position),
        }


@dataclass(frozen=True, slots=True)
class WeightedALNSPolicy:
    destroy_generator_priors: Dict[str, float]
    repair_task_selector_priors: Dict[str, float]
    repair_position_selector: str
    metric_weights: MetricWeights
    strength_ratio: float
    acceptance: str
    accept_level: float
    reaction_factor: float
    prior_mix_lambda: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "destroy_generator_priors": {
                str(name): float(weight)
                for name, weight in self.destroy_generator_priors.items()
            },
            "repair_task_selector_priors": {
                str(name): float(weight)
                for name, weight in self.repair_task_selector_priors.items()
            },
            "repair_position_selector": str(self.repair_position_selector),
            "metric_weights": self.metric_weights.as_dict(),
            "strength_ratio": float(self.strength_ratio),
            "acceptance": str(self.acceptance),
            "accept_level": float(self.accept_level),
            "reaction_factor": float(self.reaction_factor),
            "prior_mix_lambda": float(self.prior_mix_lambda),
        }
