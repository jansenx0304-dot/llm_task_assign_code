from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..config import Config
from ..evaluator import evaluate
from ..models import Instance
from ..operators import InsertionPolicy
from ..operators.insertion import InsertionContext, run_insertion_kernel
from ..solution import AssignmentSolution


@dataclass(slots=True)
class InitialConstructionResult:
    solution: AssignmentSolution
    evaluation: Any
    trace: Dict[str, Any]


def build_initial_solution_with_insertion(
    instance: Instance,
    config: Config,
    insertion_policy: InsertionPolicy,
    rng_seed: int = 0,
    manifest: Optional[Dict[str, Any]] = None,
) -> InitialConstructionResult:
    empty_solution = AssignmentSolution.empty_from_instance(
        instance, put_all_unassigned=False
    )
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
    trace = _initial_trace(
        solution, instance, str((manifest or {}).get("trace_id", "X_initial"))
    )
    print(
        f"[INITIAL INSERTION] assigned={len(solution.all_assigned_tasks())} "
        f"unassigned={len(solution.unassigned)}"
    )
    return InitialConstructionResult(
        solution=solution, evaluation=evaluation, trace=trace
    )


def _initial_trace(
    solution: AssignmentSolution, instance: Instance, trace_id: str
) -> Dict[str, Any]:
    diagnostics = dict(
        (solution.solver_diagnostics or {}).get("last_insertion", {}) or {}
    )
    candidate_count = len(instance.all_task_ids())
    failure_breakdown = dict(diagnostics.get("failure_breakdown", {}) or {})
    zero_candidates = int(failure_breakdown.get("no_candidate", 0) or 0)
    hard_rejected = int(diagnostics.get("positions_generated", 0) or 0) - int(
        diagnostics.get("strict_feasible_positions", 0) or 0
    )
    dominant = "none"
    if failure_breakdown:
        dominant = max(failure_breakdown.items(), key=lambda item: int(item[1]))[0]
    return {
        "trace_id": trace_id,
        "kind": "initial_insertion",
        "candidate_task_count": int(candidate_count),
        "attempted_task_count": int(
            diagnostics.get("tasks_analyzed", candidate_count) or 0
        ),
        "inserted_task_count": int(len(solution.all_assigned_tasks())),
        "uninserted_task_count": int(len(solution.unassigned)),
        "zero_candidate_task_count": zero_candidates,
        "hard_filter_rejected_count": max(0, int(hard_rejected)),
        "top_failed_tasks": list(diagnostics.get("top_failed_tasks", []) or []),
        "dominant_failure_reason": str(dominant),
        "operator_use": dict(diagnostics.get("operator_use", {}) or {}),
    }


__all__ = ["InitialConstructionResult", "build_initial_solution_with_insertion"]
