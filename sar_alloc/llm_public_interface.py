from __future__ import annotations

"""The complete, deliberately small surface exposed to LLM agents."""

from dataclasses import dataclass, fields
from typing import Any, Dict, Iterable, List, Optional

from .config import Config
from .models import Instance


@dataclass(frozen=True, slots=True)
class PublicCandidate:
    name: str
    description: str

    def as_dict(self) -> Dict[str, str]:
        return {"name": self.name, "description": self.description}


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
    completion_event_candidates: tuple[PublicCandidate, ...]

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
        ("strict", "Keep only states that satisfy the current feasibility requirements."),
        ("relaxed_recoverable", "Allow short-lived recoverable violations to widen the search space."),
        ("recovery_only", "Focus exclusively on reducing feasibility debt and restoring a stable state."),
    ]
    current_solution = getattr(state, "working_solution", None) if state is not None else None
    current_eval = getattr(current_solution, "eval", None)
    if current_eval is not None and bool(getattr(current_eval, "is_feasible", False)):
        feasibility = [item for item in feasibility if item[0] != "recovery_only"]

    return PublicCandidates(
        objective_candidates=_items(
            [
                ("missed_priority", "Sum of priorities of unassigned tasks; lower means fewer important tasks are missed."),
                ("unassigned_count", "Number of unassigned tasks; lower means greater task coverage."),
                ("energy_total", "Total route energy consumption; lower means less energy is used."),
                ("total_distance", "Total travel distance over all agents; lower means shorter routes."),
                ("makespan", "Longest agent completion time; lower means the mission finishes sooner."),
                ("route_balance", "Route workload imbalance; lower means work is distributed more evenly."),
            ]
        ),
        insertion_operator_candidates=_items(
            [
                ("greedy_insertion", "Choose the currently highest-scoring task and position; stable and direct."),
                ("scarcity_first_insertion", "Prioritize tasks with few feasible positions or scarce capable agents."),
                ("regret_insertion", "Prioritize tasks whose future insertion cost is likely to rise most."),
                ("bottleneck_insertion", "Prioritize tasks connected to the current search bottleneck."),
                ("diversified_insertion", "Sample among strong candidates to create structural diversity."),
            ]
        ),
        insertion_task_signal_candidates=_items(
            [
                ("priority_loss", "Emphasize tasks whose omission causes high mission-value loss."),
                ("scarcity_pressure", "Emphasize tasks with few feasible positions or capable agents."),
                ("regret_pressure", "Emphasize tasks that become substantially harder to insert later."),
                ("bottleneck_pressure", "Emphasize tasks associated with the current bottleneck."),
                ("mobility_opportunity", "Emphasize tasks with a strong immediate opportunity for successful insertion."),
            ]
        ),
        insertion_position_signal_candidates=_items(
            [
                ("insert_cost", "Prefer positions with lower distance, time, and energy increase."),
                ("future_slack", "Prefer positions preserving time and energy slack for later insertions."),
                ("route_balance_gain", "Prefer positions that improve workload balance."),
                ("local_coupling_penalty", "Avoid positions creating local conflicts or tight coupling."),
                ("diversity_gain", "Prefer positions producing a different route structure."),
            ]
        ),
        destroy_operator_candidates=_items(
            [
                ("random_removal", "Remove random tasks to introduce broad perturbation."),
                ("worst_task_removal", "Remove tasks creating high route or energy pressure."),
                ("related_cluster_removal", "Remove a spatially, temporally, or skill-related cluster."),
                ("critical_block_removal", "Remove a consecutive route block to change local order."),
                ("route_rebalance_removal", "Remove tasks from overloaded routes to improve balance."),
            ]
        ),
        destroy_signal_candidates=_items(
            [
                ("cost_pressure", "Favor removal of tasks producing high distance, time, or energy pressure."),
                ("coupling_pressure", "Favor removal of strongly coupled neighboring tasks."),
                ("route_balance_pressure", "Favor removal from overloaded routes."),
                ("mobility_opportunity", "Favor tasks that are likely to be inserted elsewhere."),
                ("scarcity_protection", "Protect scarce tasks by reducing their removal preference."),
            ]
        ),
        acceptance_candidates=_items(
            [
                ("greedy", "Accept only candidates that are no worse under the contract objective."),
                ("threshold", "Allow limited worsening to balance stability and exploration."),
                ("sa", "Use simulated-annealing acceptance for stronger exploration."),
            ]
        ),
        feasibility_mode_candidates=_items(feasibility),
        relaxable_violation_candidates=_items(
            [
                (
                    "time_window",
                    "Task service starts after its time-window end. limit_ratio=0.10 allows temporary lateness up to 10% of each task's time-window width.",
                ),
                (
                    "energy",
                    "An agent route exceeds its initial energy. limit_ratio=0.05 allows temporary over-energy up to 5% of each agent's initial energy.",
                ),
            ]
        ),
        completion_event_candidates=_items(
            [
                ("initial_solution_built", "The initial construction produced a working solution."),
                ("initial_solution_failed", "The initial construction did not produce a usable working solution."),
                ("quality_improved", "Quality improved under the active stage objective."),
                ("quality_flat", "Quality did not materially change under the active stage objective."),
                ("quality_worsened", "Quality worsened under the active stage objective."),
                ("global_best_improved", "The global best solution was improved."),
                ("no_admissible_candidate", "The solver found no admissible candidate."),
                ("feasibility_recovered", "The working solution returned to a stable feasible state."),
                ("recovery_debt_reduced", "Recoverable feasibility debt decreased."),
            ]
        ),
    )


__all__ = ["PublicCandidate", "PublicCandidates", "build_public_candidates"]
