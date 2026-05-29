from __future__ import annotations

"""Typed objects for the weighted ALNS policy interface."""

from dataclasses import dataclass, fields
from typing import Any, Dict, Tuple


LANDSCAPE_METRIC_FIELDS: Tuple[str, ...] = (
    "cost_pressure",
    "scarcity_pressure",
    "coupling_pressure",
    "mobility_opportunity",
    "balance_pressure",
)

REPAIR_POSITION_METRIC_FIELDS: Tuple[str, ...] = (
    "insert_cost",
    "future_slack",
    "route_balance_gain",
    "local_coupling_penalty",
    "diversity_gain",
)

METRIC_DIRECTIONS: Tuple[str, ...] = (
    "prefer_high",
    "prefer_low",
    "avoid_high",
    "neutral",
)

SEARCH_DIAGNOSIS_FIELDS: Tuple[str, ...] = (
    "cost_descent",
    "scarcity_protection",
    "structure_rebuild",
    "route_rebalance",
    "diversified_escape",
)

DESTROY_CANDIDATE_GENERATORS: Tuple[str, ...] = (
    "random_removal",
    "worst_task_removal",
    "related_cluster_removal",
    "critical_block_removal",
    "route_rebalance_removal",
)

REPAIR_TASK_SELECTORS: Tuple[str, ...] = (
    "feasible_greedy_repair",
    "scarcity_first_repair",
    "regret_k_repair",
    "bottleneck_targeted_repair",
    "diversified_random_repair",
)

ACCEPTANCE_MODES: Tuple[str, ...] = (
    "greedy",
    "threshold",
    "sa",
)

POLICY_BOUNDS: Dict[str, Tuple[float, float]] = {
    "strength_ratio": (0.02, 0.40),
    "reaction_factor": (0.05, 0.40),
    "accept_level": (0.0, 1.0),
    "prior_mix_lambda": (0.20, 0.35),
}

OPERATOR_PRIOR_BOUNDS: Tuple[float, float] = (0.10, 5.0)


@dataclass(frozen=True, slots=True)
class MetricPreference:
    score: int
    direction: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "score": int(self.score),
            "direction": str(self.direction),
        }


@dataclass(frozen=True, slots=True)
class LandscapeFeatures:
    cost_pressure: float
    scarcity_pressure: float
    coupling_pressure: float
    mobility_opportunity: float
    balance_pressure: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class PositionFeatures:
    insert_cost: float
    future_slack: float
    route_balance_gain: float
    local_coupling_penalty: float
    diversity_gain: float

    def as_dict(self) -> Dict[str, float]:
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class LandscapeMetricPreferences:
    cost_pressure: MetricPreference
    scarcity_pressure: MetricPreference
    coupling_pressure: MetricPreference
    mobility_opportunity: MetricPreference
    balance_pressure: MetricPreference

    def as_dict(self) -> Dict[str, Any]:
        return {field.name: getattr(self, field.name).as_dict() for field in fields(self)}

    def preferences_dict(self) -> Dict[str, MetricPreference]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class PositionMetricPreferences:
    insert_cost: MetricPreference
    future_slack: MetricPreference
    route_balance_gain: MetricPreference
    local_coupling_penalty: MetricPreference
    diversity_gain: MetricPreference

    def as_dict(self) -> Dict[str, Any]:
        return {field.name: getattr(self, field.name).as_dict() for field in fields(self)}

    def preferences_dict(self) -> Dict[str, MetricPreference]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


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
    destroy_operator_scores: Dict[str, int]
    repair_operator_scores: Dict[str, int]
    destroy_metric_preferences: LandscapeMetricPreferences
    repair_task_metric_preferences: LandscapeMetricPreferences
    repair_position_metric_preferences: PositionMetricPreferences
    search_diagnosis_scores: Dict[str, int]
    destroy_strength_score: int
    candidate_budget_score: int
    exploration_score: int
    destroy_operator_priors: Dict[str, float]
    repair_operator_priors: Dict[str, float]
    strength_ratio: float
    exploration_rate: float
    acceptance: str
    accept_level: float
    reaction_factor: float
    prior_mix_lambda: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "search_diagnosis_scores": {
                str(name): int(score)
                for name, score in self.search_diagnosis_scores.items()
            },
            "destroy_operator_scores": {
                str(name): int(score)
                for name, score in self.destroy_operator_scores.items()
            },
            "repair_operator_scores": {
                str(name): int(score)
                for name, score in self.repair_operator_scores.items()
            },
            "destroy_metric_preferences": self.destroy_metric_preferences.as_dict(),
            "repair_task_metric_preferences": self.repair_task_metric_preferences.as_dict(),
            "repair_position_metric_preferences": self.repair_position_metric_preferences.as_dict(),
            "destroy_strength_score": int(self.destroy_strength_score),
            "candidate_budget_score": int(self.candidate_budget_score),
            "exploration_score": int(self.exploration_score),
            "destroy_operator_priors": {
                str(name): float(weight)
                for name, weight in self.destroy_operator_priors.items()
            },
            "repair_operator_priors": {
                str(name): float(weight)
                for name, weight in self.repair_operator_priors.items()
            },
            "strength_ratio": float(self.strength_ratio),
            "exploration_rate": float(self.exploration_rate),
            "acceptance": str(self.acceptance),
            "accept_level": float(self.accept_level),
            "reaction_factor": float(self.reaction_factor),
            "prior_mix_lambda": float(self.prior_mix_lambda),
        }
