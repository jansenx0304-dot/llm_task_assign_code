from __future__ import annotations

import random

from ..config import Config
from ..console import success
from ..evaluator import evaluate
from ..models import Instance
from ..operators import WeightedALNSPolicy
from ..solution import AssignmentSolution
from .assign_solvers import repair_with_weighted_priority


def build_initial_solution(
    instance: Instance,
    config: Config,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Build the initial solution with the same weighted-priority repair flow."""
    rng = random.Random(rng_seed)
    return build_weighted_insert(instance, config, rng)


def build_weighted_insert(instance: Instance, config: Config, rng: random.Random) -> AssignmentSolution:
    sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    policy = _weighted_alns_policy_from_config(config)
    sol = repair_with_weighted_priority(sol, instance, config, policy, rng)
    sol.normalize(instance)
    ev = evaluate(sol, instance, config, update_solution_schedule=True)
    assigned = len(sol.all_assigned_tasks())
    success(
        f"init_solution_ready assigned={assigned} "
        f"unassigned={len(sol.unassigned)} "
        f"lex_key={list(ev.lex_key or ())}"
    )
    return sol


def _weighted_alns_policy_from_config(config: Config) -> WeightedALNSPolicy:
    weighted = config.solver.weighted_alns
    return WeightedALNSPolicy(
        destroy_generator_priors=dict(weighted.destroy_generator_priors),
        repair_task_selector_priors=dict(weighted.repair_task_selector_priors),
        remove_metric_weights=weighted.remove_metric_weights,
        reinsert_metric_weights=weighted.reinsert_metric_weights,
        insert_metric_weights=weighted.insert_metric_weights,
        strength_ratio=float(weighted.strength_ratio),
        acceptance=str(weighted.acceptance),
        accept_level=float(weighted.accept_level),
        reaction_factor=float(weighted.reaction_factor),
        prior_mix_lambda=float(weighted.prior_mix_lambda),
    )
