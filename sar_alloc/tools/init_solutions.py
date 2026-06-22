from __future__ import annotations

import random

from ..config import Config
from ..evaluator import evaluate
from ..models import Instance
from ..operators import InsertionPolicy
from ..operators.insertion import InsertionContext, run_insertion_kernel
from ..solution import AssignmentSolution


def build_initial_solution_with_insertion(
    instance: Instance,
    config: Config,
    insertion_policy: InsertionPolicy,
    rng_seed: int = 0,
) -> AssignmentSolution:
    empty_solution = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=False)
    solution = run_insertion_kernel(
        partial_solution=empty_solution,
        candidate_tasks=sorted(int(tid) for tid in instance.all_task_ids()),
        insertion_policy=insertion_policy,
        context=InsertionContext(kind="initial", feasibility_mode="strict"),
        instance=instance,
        config=config,
        rng=random.Random(rng_seed),
    )
    solution.normalize(instance)
    evaluation = evaluate(solution, instance, config, update_solution_schedule=True)
    print(
        f"[INITIAL INSERTION] assigned={len(solution.all_assigned_tasks())} "
        f"unassigned={len(solution.unassigned)} lex_key={list(evaluation.lex_key or ())}"
    )
    return solution


__all__ = ["build_initial_solution_with_insertion"]
