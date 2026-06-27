"""Observation builders for supervisor and step agents."""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any, Dict, List, Mapping, Optional

from .config import Config
from .evaluator import build_objective_keys, evaluate
from .models import Agent, Instance, Task
from .operators.destroy import build_destroy_landscape
from .operators.insertion import build_insertion_landscape
from .schemas import QUALITY_METRICS, build_action_space as _base_action_space
from .solution import AssignmentSolution


def build_action_space(
    *,
    instance: Instance | None = None,
    config: Config | None = None,
    phase: str = "step",
    remaining_global_budget: Optional[Mapping[str, Any]] = None,
    stage_type: str = "",
    has_working_solution: bool = False,
    remaining_stage_resources: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    space = _base_action_space(instance, config)
    if phase.startswith("supervisor"):
        limits = next_stage_resource_limits(dict(remaining_global_budget or {}))
        space["next_stage_resource_limits"] = limits
        if phase == "supervisor_kickoff":
            space["stage_types"] = ["initial_construction"]
        return space

    normal_action = "construct_initial" if stage_type == "initial_construction" else "run_alns"
    remaining = dict(remaining_stage_resources or {})
    has_action_budget = int(remaining.get("actions", 0) or 0) > 0
    min_left = int(remaining.get("min_actions_remaining", 0) or 0)
    executable: List[str] = []
    blocked: List[Dict[str, str]] = []
    if has_action_budget and normal_action == "construct_initial" and not has_working_solution:
        executable.append(normal_action)
    elif has_action_budget and normal_action == "run_alns" and has_working_solution:
        executable.append(normal_action)
    else:
        blocked.append({"action": normal_action, "reason": "not_executable_now"})
    if has_action_budget and min_left <= 0:
        executable.append("request_supervisor_review")
    else:
        blocked.append({"action": "request_supervisor_review", "reason": "min_actions_not_reached"})
    space["hard_executable_actions"] = executable or ["request_supervisor_review"]
    space["hard_inexecutable_actions"] = blocked
    return space


def build_supervisor_observation(
    *,
    phase: str,
    instance: Instance,
    run_state: Any,
    completed_stage: Any | None = None,
) -> Dict[str, Any]:
    observation_id = run_state.next_observation_id()
    remaining = run_state.global_budget.remaining()
    action_space = build_action_space(
        instance=instance,
        config=run_state.config,
        phase=f"supervisor_{phase}",
        remaining_global_budget=remaining,
    )
    obs: Dict[str, Any] = {
        "run_context": {
            "observation_id": observation_id,
            "phase": f"supervisor_{phase}",
            "instance": run_state.instance_name,
            "remaining_global_resources": remaining,
        },
        "problem_profile": instance_summary(instance, rng_seed=run_state.rng_seed),
        "solution_state": {
            "working": _state_digest(run_state.working_summary),
            "best_feasible": _best_digest(run_state.best_summary),
        },
        "recent_records": run_state.records.recent_for_supervisor(),
        "action_space": action_space,
    }
    if completed_stage is not None:
        obs["completed_stage"] = completed_stage.as_observation()
        obs["completed_result"] = (
            run_state.last_completion.as_dict()
            if run_state.last_completion is not None
            else {}
        )
    return obs


def build_step_observation(
    *,
    instance: Instance,
    run_state: Any,
    active_stage: Any,
) -> Dict[str, Any]:
    observation_id = run_state.next_observation_id()
    working = run_state.working_solution or AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    landscape = _landscape(working, instance, run_state.config)
    action_space = build_action_space(
        instance=instance,
        config=run_state.config,
        phase="step",
        stage_type=active_stage.stage_type,
        has_working_solution=run_state.working_solution is not None,
        remaining_stage_resources=active_stage.remaining(),
    )
    return {
        "run_context": {
            "observation_id": observation_id,
            "phase": "step",
            "instance": run_state.instance_name,
            "step_index": run_state.step_index,
            "stage_id": active_stage.stage_id,
        },
        "active_stage": active_stage.as_observation(),
        "execution_state": {
            "hard_executable_actions": list(action_space["hard_executable_actions"]),
            "hard_inexecutable_actions": list(action_space["hard_inexecutable_actions"]),
            "working_solution_exists": run_state.working_solution is not None,
            "remaining_stage_resources": active_stage.remaining(),
            "remaining_global_resources": run_state.global_budget.remaining(),
        },
        "solution_evidence": {
            "working": _state_digest(run_state.working_summary),
            "best_feasible": _best_digest(run_state.best_summary),
        },
        "destroy_facts": dict(landscape.get("destroy_facts", {}) or {}),
        "insertion_facts": dict(landscape.get("insertion_facts", {}) or {}),
        "targetable_evidence": _targetable_evidence(landscape),
        "control_catalog": _control_catalog(action_space),
        "action_space": action_space,
        "recent_records": run_state.records.recent_for_step(),
        "runtime_feedback": {"last_result": _last_result_feedback(run_state.last_result)},
    }


def next_stage_resource_limits(remaining_global_budget: Mapping[str, Any]) -> Dict[str, Any]:
    step_calls = int(float(remaining_global_budget.get("step_calls", 0) or 0))
    solver_calls = int(float(remaining_global_budget.get("solver_calls", 0) or 0))
    return {
        "max_solver_actions_allowed": max(0, min(step_calls, solver_calls)),
        "max_time_sec_allowed": max(0.0, float(remaining_global_budget.get("time_sec", 0.0) or 0.0)),
        "max_iters_allowed": max(0, int(float(remaining_global_budget.get("iters", 0) or 0))),
    }


def solution_summary(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    *,
    stage_objective_layers: Optional[List[Dict[str, Any]]] = None,
    global_objective_layers: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    ev = evaluate(solution, instance, config, update_solution_schedule=True)
    report = ev.constraint_report
    default_layers = [{"metric": layer.metric, "direction": layer.direction} for layer in config.eval.objective_policy.layers]
    if not default_layers:
        default_layers = [{"metric": "missed_priority", "direction": "min"}, {"metric": "unassigned_count", "direction": "min"}]
    stage_layers = stage_objective_layers or default_layers
    global_layers = global_objective_layers or default_layers
    return {
        "is_feasible": bool(report.is_feasible),
        "objective_keys": build_objective_keys(ev, stage_layers, global_layers),
        "quality_summary": {name: float(ev.quality_metrics.get(name, 0.0)) for name in QUALITY_METRICS},
        "feasibility_summary": {
            "is_feasible": bool(report.is_feasible),
            "violation_total": float(report.violation_total),
            "violation_by_type": {
                "capability": float(report.violation_capability),
                "time_window": float(report.violation_time_window),
                "energy": float(report.violation_energy),
            },
            "recoverable_violation_total": float(report.recoverable_violation_total),
            "unrecoverable_violation_total": float(report.unrecoverable_violation_total),
            "violation_ratio_by_type": {str(k): float(v) for k, v in report.violation_ratio_by_type.items()},
        },
    }


def instance_summary(instance: Instance, rng_seed: int = 0) -> Dict[str, Any]:
    rng = random.Random(rng_seed)
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    base = {
        "num_tasks": len(tasks),
        "num_agents": len(agents),
        "priority_mass": sum(float(task.priority) for task in tasks),
    }
    if not tasks or not agents:
        return base
    capable_counts = [_capable_count(agents, task) for task in tasks]
    priorities = [float(task.priority) for task in tasks]
    negative_slack = sum(
        1
        for task in tasks
        if min(instance.travel_time(agent, instance.depot.loc, task.loc) for agent in agents)
        > task.tw_end + 1e-9
    )
    depot_distances = [instance.distance(instance.depot.loc, task.loc) for task in tasks]
    return {
        **base,
        "high_priority_task_count": sum(v >= _quantile(priorities, 0.75) for v in priorities),
        "zero_capable_task_count": sum(count == 0 for count in capable_counts),
        "static_capability_scarce_task_count": sum(count <= max(1, len(agents) // 4) for count in capable_counts),
        "time_window_negative_slack_frac_lb": negative_slack / len(tasks),
        "static_capable_count_distribution": {str(k): int(v) for k, v in Counter(capable_counts).items()},
        "spatial": {
            "radius95_to_depot": _quantile(depot_distances, 0.95),
            "sample_nearest_neighbor_distance": _mean_nearest_neighbor_distance(instance, tasks, rng, min(len(tasks), 20)),
        },
    }


def _landscape(solution: AssignmentSolution, instance: Instance, config: Config) -> Dict[str, Any]:
    destroy = build_destroy_landscape(solution, instance, config)
    insertion = build_insertion_landscape(solution, instance, config)
    return {
        "destroy_facts": dict(destroy.get("destroy_facts", {}) or {}),
        "insertion_facts": dict(insertion.get("insertion_facts", {}) or {}),
        "candidate_routes": [dict(item) for item in destroy.get("candidate_routes", []) or [] if isinstance(item, dict)],
    }


def _targetable_evidence(landscape: Mapping[str, Any]) -> Dict[str, Any]:
    insertion_facts = dict(landscape.get("insertion_facts", {}) or {})
    candidate_routes = [
        {
            "agent_id": int(item.get("agent_id", 0) or 0),
            "route_len": int(item.get("route_len", 0) or 0),
            "route_cost": float(item.get("route_cost", 0.0) or 0.0),
        }
        for item in landscape.get("candidate_routes", []) or []
        if isinstance(item, Mapping) and item.get("agent_id") is not None
    ][:12]
    tasks = [
        {
            "task_id": int(item.get("task_id", 0) or 0),
            "priority": float(item.get("priority", 0.0) or 0.0),
            "candidate_position_count": int(item.get("candidate_position_count", 0) or 0),
            "feasible_position_count": int(item.get("feasible_position_count", 0) or 0),
            "capable_agent_count": int(item.get("capable_agent_count", 0) or 0),
        }
        for item in insertion_facts.get("unassigned_task_facts", []) or []
        if isinstance(item, Mapping) and item.get("task_id") is not None
    ][:12]
    return {
        "visible_task_ids": sorted({int(item["task_id"]) for item in tasks}),
        "visible_agent_ids": sorted({int(item["agent_id"]) for item in candidate_routes}),
        "target_catalog": {"tasks": tasks, "routes": candidate_routes},
    }


def _control_catalog(action_space: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "insertion_operators": list(action_space["insertion_operators"]),
        "insertion_task_signals": list(action_space["insertion_task_signals"]),
        "insertion_position_signals": list(action_space["insertion_position_signals"]),
        "destroy_operators": list(action_space["destroy_operators"]),
        "destroy_signals": list(action_space["destroy_signals"]),
        "acceptance_modes": list(action_space["acceptance_modes"]),
    }


def _last_result_feedback(result: Any | None) -> Dict[str, Any]:
    if result is None:
        return {"exists": False}
    data = dict(result or {}) if isinstance(result, Mapping) else {}
    trace = dict(data.get("trace", {}) or {})
    flow = dict(trace.get("trial_flow", {}) or {})
    return {
        "exists": True,
        "last_action": str(data.get("action", "")),
        "quality_delta": dict(data.get("quality_delta", {}) or {}),
        "before_feasible": bool(data.get("before_feasible", False)),
        "after_feasible": bool(data.get("after_feasible", False)),
        "protected_passed": bool(data.get("protected_passed", False)),
        "trace_counts": {
            "candidate_trials": int(flow.get("candidate_trials", 0) or 0),
            "accepted": int(flow.get("accepted_trials", 0) or 0),
            "global_best_updates": int(flow.get("global_best_improved_trials", 0) or 0),
        },
    }


def _state_digest(summary: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not summary:
        return {"is_feasible": False, "quality": {}}
    return {
        "is_feasible": bool((summary.get("feasibility_summary", {}) or {}).get("is_feasible", False)),
        "quality": {str(k): float(v) for k, v in (summary.get("quality_summary", {}) or {}).items()},
        "feasibility": dict(summary.get("feasibility_summary", {}) or {}),
    }


def _best_digest(summary: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not summary:
        return {"exists": False, "quality": {}}
    return {"exists": True, **_state_digest(summary)}


def _capable_count(agents: List[Agent], task: Task) -> int:
    return sum(1 for agent in agents if set(task.skill_req).issubset(agent.skills))


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(v) for v in values)
    pos = max(0.0, min(1.0, q)) * (len(ordered) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return ordered[lo] if lo == hi else ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def _mean_nearest_neighbor_distance(instance: Instance, tasks: List[Task], rng: random.Random, sample: int) -> float:
    if len(tasks) <= 1:
        return 0.0
    selected = tasks if sample >= len(tasks) else rng.sample(tasks, sample)
    return sum(
        min(instance.distance(task.loc, other.loc) for other in tasks if other.id != task.id)
        for task in selected
    ) / len(selected)


__all__ = [
    "build_action_space",
    "build_supervisor_observation",
    "build_step_observation",
    "instance_summary",
    "next_stage_resource_limits",
    "solution_summary",
]
