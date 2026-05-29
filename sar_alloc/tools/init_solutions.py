from __future__ import annotations

import random

from ..config import Config
from ..evaluator import evaluate
from ..models import Instance
from ..operators import (
    DESTROY_CANDIDATE_GENERATORS,
    REPAIR_TASK_SELECTORS,
    SEARCH_DIAGNOSIS_FIELDS,
    LandscapeMetricPreferences,
    MetricPreference,
    PositionMetricPreferences,
    WeightedALNSPolicy,
    operator_score_to_prior,
)
from ..solution import AssignmentSolution
from ..operators.repair import repair_with_feasible_greedy


def build_initial_solution(
    instance: Instance,
    config: Config,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Build the initial incumbent used before LLM-directed ALNS actions.

    The construction heuristic is a fixed part of the solver workflow. It is
    not used as a fallback run_alns policy and does not choose objective tiers.
    """
    rng = random.Random(rng_seed)
    return build_weighted_insert(instance, config, rng)


def build_weighted_insert(instance: Instance, config: Config, rng: random.Random) -> AssignmentSolution:
    sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    policy = _initial_construction_policy()
    sol = repair_with_feasible_greedy(sol, instance, config, policy, rng)
    sol.normalize(instance)
    ev = evaluate(sol, instance, config, update_solution_schedule=True)
    assigned = len(sol.all_assigned_tasks())
    print(
        f"[INIT] assigned={assigned} "
        f"unassigned={len(sol.unassigned)} "
        f"lex_key={list(ev.lex_key or ())}"
    )
    return sol


def _initial_construction_policy() -> WeightedALNSPolicy:
    # This local construction policy replaces the old config default. Keeping it
    # near the construction routine makes it clear that real run_alns strategy
    # still has to come from the LLM action payload.
    return WeightedALNSPolicy(
        search_diagnosis_scores={name: 5 for name in SEARCH_DIAGNOSIS_FIELDS},
        destroy_operator_scores={name: 5 for name in DESTROY_CANDIDATE_GENERATORS},
        repair_operator_scores={name: 5 for name in REPAIR_TASK_SELECTORS},
        destroy_metric_preferences=LandscapeMetricPreferences(
            cost_pressure=MetricPreference(7, "prefer_high"),
            scarcity_pressure=MetricPreference(7, "avoid_high"),
            coupling_pressure=MetricPreference(6, "prefer_high"),
            mobility_opportunity=MetricPreference(6, "prefer_high"),
            balance_pressure=MetricPreference(5, "prefer_high"),
        ),
        repair_task_metric_preferences=LandscapeMetricPreferences(
            cost_pressure=MetricPreference(5, "prefer_high"),
            scarcity_pressure=MetricPreference(8, "prefer_high"),
            coupling_pressure=MetricPreference(6, "prefer_high"),
            mobility_opportunity=MetricPreference(4, "prefer_low"),
            balance_pressure=MetricPreference(5, "prefer_high"),
        ),
        repair_position_metric_preferences=PositionMetricPreferences(
            insert_cost=MetricPreference(8, "prefer_low"),
            future_slack=MetricPreference(7, "prefer_high"),
            route_balance_gain=MetricPreference(5, "prefer_high"),
            local_coupling_penalty=MetricPreference(5, "prefer_low"),
            diversity_gain=MetricPreference(3, "prefer_high"),
        ),
        destroy_strength_score=5,
        candidate_budget_score=7,
        exploration_score=3,
        destroy_operator_priors={name: operator_score_to_prior(5) for name in DESTROY_CANDIDATE_GENERATORS},
        repair_operator_priors={name: operator_score_to_prior(5) for name in REPAIR_TASK_SELECTORS},
        strength_ratio=0.18,
        exploration_rate=0.10,
        acceptance="sa",
        accept_level=0.25,
        reaction_factor=0.20,
        prior_mix_lambda=0.25,
    )
