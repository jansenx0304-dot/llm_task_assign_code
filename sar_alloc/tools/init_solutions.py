from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    runtime_context: Optional[Dict[str, Any]] = None,
) -> InitialConstructionResult:
    empty_solution = AssignmentSolution.empty_from_instance(
        instance, put_all_unassigned=False
    )
    compiled_target = dict((runtime_context or {}).get("runtime_target", {}) or {})
    compiled_feasibility = dict(
        (runtime_context or {}).get("feasibility_policy", {}) or {}
    )
    solution = run_insertion_kernel(
        partial_solution=empty_solution,
        candidate_tasks=sorted(int(tid) for tid in instance.all_task_ids()),
        insertion_policy=insertion_policy,
        context=InsertionContext(
            kind="initial",
            feasibility_mode=str(compiled_feasibility.get("mode", "strict")),
            target_task_ids=tuple(
                int(tid) for tid in compiled_target.get("task_ids", []) or []
            ),
            target_agent_ids=tuple(
                int(aid) for aid in compiled_target.get("agent_ids", []) or []
            ),
        ),
        instance=instance,
        config=config,
        rng=random.Random(rng_seed),
    )
    solution.normalize(instance)
    evaluation = evaluate(solution, instance, config, update_solution_schedule=True)
    trace = _initial_trace(
        solution, instance, str((runtime_context or {}).get("trace_id", "X_initial"))
    )
    trace["runtime_target"] = compiled_target
    diagnostics = dict(
        (solution.solver_diagnostics or {}).get("last_insertion", {}) or {}
    )
    trace["target_engagement"] = _initial_target_engagement(
        solution=solution,
        diagnostics=diagnostics,
        target=compiled_target,
        instance=instance,
    )
    trace["target_agent_engagement"] = dict(
        diagnostics.get("target_agent_engagement", {}) or {}
    )
    trace["target_progress"] = _initial_target_progress(
        solution=solution,
        target=compiled_target,
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


def _initial_target_engagement(
    *,
    solution: AssignmentSolution,
    diagnostics: Dict[str, Any],
    target: Dict[str, Any],
    instance: Instance,
) -> Dict[str, Any]:
    target_task_ids = _target_task_ids(target)
    assigned = solution.all_assigned_tasks()
    still_unassigned = {int(tid) for tid in solution.unassigned}
    all_tasks = {int(tid) for tid in instance.all_task_ids()}
    inserted = [tid for tid in target_task_ids if tid in assigned]
    attempted = [tid for tid in target_task_ids if tid in all_tasks]
    return {
        "target_scope_kind": str(target.get("scope_kind", "global")),
        "target_task_count": len(target_task_ids),
        "target_agent_count": len(target.get("agent_ids", []) or []),
        "target_tasks_attempted": _limited_ints(attempted),
        "target_tasks_inserted": _limited_ints(inserted),
        "target_tasks_still_unassigned": _limited_ints(
            [tid for tid in target_task_ids if tid in still_unassigned]
        ),
        "target_insertion_alternate_count": int(bool(target_task_ids and not inserted)),
        "target_agent_engagement": dict(
            diagnostics.get("target_agent_engagement", {}) or {}
        ),
        "insertion_target_task_ids": _limited_ints(
            [int(tid) for tid in diagnostics.get("target_task_ids", []) or []]
        ),
    }


def _initial_target_progress(
    *, solution: AssignmentSolution, target: Dict[str, Any]
) -> Dict[str, Any]:
    target_task_ids = _target_task_ids(target)
    assigned = solution.all_assigned_tasks()
    unassigned = {int(tid) for tid in solution.unassigned}
    return {
        "target_task_count": len(target_task_ids),
        "target_tasks_inserted": _limited_ints(
            [tid for tid in target_task_ids if tid in assigned]
        ),
        "target_tasks_still_unassigned": _limited_ints(
            [tid for tid in target_task_ids if tid in unassigned]
        ),
        "focus_metric_delta": {},
    }


def _target_task_ids(target: Dict[str, Any]) -> List[int]:
    out: List[int] = []
    seen = set()
    for value in target.get("task_ids", []) or []:
        if isinstance(value, bool):
            continue
        tid = int(value)
        if tid not in seen:
            seen.add(tid)
            out.append(tid)
    return out


def _limited_ints(values: List[int], limit: int = 20) -> List[int]:
    return [int(value) for value in values[:limit]]


__all__ = ["InitialConstructionResult", "build_initial_solution_with_insertion"]

