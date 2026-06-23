from __future__ import annotations

"""Small candidate-name registry used by validators and compilers."""

from dataclasses import dataclass, fields
from typing import Any, Dict, Iterable, List, Optional

from .config import Config
from .models import Instance


@dataclass(frozen=True, slots=True)
class PublicCandidate:
    name: str
    description: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {"name": self.name}


@dataclass(frozen=True, slots=True)
class PublicCandidates:
    objective_candidates: tuple[PublicCandidate, ...]
    insertion_operator_candidates: tuple[PublicCandidate, ...]
    insertion_task_signal_candidates: tuple[PublicCandidate, ...]
    insertion_position_signal_candidates: tuple[PublicCandidate, ...]
    destroy_operator_candidates: tuple[PublicCandidate, ...]
    destroy_signal_candidates: tuple[PublicCandidate, ...]
    acceptance_candidates: tuple[PublicCandidate, ...]
    feasibility_mode_candidates: tuple[PublicCandidate, ...]
    relaxable_violation_candidates: tuple[PublicCandidate, ...]

    def as_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            field.name: [candidate.as_dict() for candidate in getattr(self, field.name)]
            for field in fields(self)
        }

    def names(self, field_name: str) -> tuple[str, ...]:
        return tuple(candidate.name for candidate in getattr(self, field_name))


def _items(values: Iterable[tuple[str, str]]) -> tuple[PublicCandidate, ...]:
    return tuple(PublicCandidate(name, description) for name, description in values)


def build_public_candidates(
    instance: Instance,
    config: Config,
    state: Optional[Any] = None,
) -> PublicCandidates:
    del instance, config
    feasibility = [
        ("strict", ""),
        ("relaxed_recoverable", ""),
        ("recovery_only", ""),
    ]
    current_solution = getattr(state, "working_solution", None) if state is not None else None
    current_eval = getattr(current_solution, "eval", None)
    if current_eval is not None and bool(getattr(current_eval, "is_feasible", False)):
        feasibility = [item for item in feasibility if item[0] != "recovery_only"]

    return PublicCandidates(
        objective_candidates=_items(
            [
                ("missed_priority", ""),
                ("unassigned_count", ""),
                ("energy_total", ""),
                ("total_distance", ""),
                ("makespan", ""),
                ("route_balance", ""),
            ]
        ),
        insertion_operator_candidates=_items(
            [
                ("greedy_insertion", ""),
                ("scarcity_first_insertion", ""),
                ("regret_insertion", ""),
                ("bottleneck_insertion", ""),
                ("diversified_insertion", ""),
            ]
        ),
        insertion_task_signal_candidates=_items(
            [
                ("priority_loss", ""),
                ("scarcity_pressure", ""),
                ("regret_pressure", ""),
                ("bottleneck_pressure", ""),
                ("mobility_opportunity", ""),
            ]
        ),
        insertion_position_signal_candidates=_items(
            [
                ("insert_cost", ""),
                ("future_slack", ""),
                ("route_balance_gain", ""),
                ("local_coupling_penalty", ""),
                ("diversity_gain", ""),
            ]
        ),
        destroy_operator_candidates=_items(
            [
                ("random_removal", ""),
                ("worst_task_removal", ""),
                ("related_cluster_removal", ""),
                ("critical_block_removal", ""),
                ("route_rebalance_removal", ""),
            ]
        ),
        destroy_signal_candidates=_items(
            [
                ("cost_pressure", ""),
                ("coupling_pressure", ""),
                ("route_balance_pressure", ""),
                ("mobility_opportunity", ""),
                ("scarcity_protection", ""),
            ]
        ),
        acceptance_candidates=_items(
            [
                ("greedy", ""),
                ("threshold", ""),
                ("sa", ""),
            ]
        ),
        feasibility_mode_candidates=_items(feasibility),
        relaxable_violation_candidates=_items(
            [
                ("time_window", ""),
                ("energy", ""),
            ]
        ),
    )


__all__ = ["PublicCandidate", "PublicCandidates", "build_public_candidates"]
