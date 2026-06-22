from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .llm_public_interface import PublicCandidates
from .models import Agent, Instance, Task


_OBJECTIVE_METRIC_DEFINITIONS = {
    "missed_priority": {
        "definition": "sum(priority[t] for each unassigned task t)",
        "depends_on": ["task priority", "whether task is assigned"],
    },
    "unassigned_count": {
        "definition": "count(tasks that are not assigned)",
        "depends_on": ["whether task is assigned"],
    },
    "energy_total": {
        "definition": "sum(energy used by each agent route)",
        "depends_on": [
            "assigned tasks",
            "route order",
            "agent energy model",
            "travel distance",
            "service energy",
            "waiting energy",
        ],
    },
    "total_distance": {
        "definition": "sum(travel distance of each agent route)",
        "depends_on": ["assigned tasks", "route order", "task locations", "depot locations"],
    },
    "makespan": {
        "definition": "max(finish_time of each agent route)",
        "depends_on": ["assigned tasks", "route order", "agent speed", "service time", "travel time"],
    },
    "route_balance": {
        "definition": "coefficient of variation of route task counts across agents",
        "depends_on": ["number of assigned tasks on each agent route"],
    },
}


def build_supervisor_kickoff_observation(
    *,
    instance: Instance,
    instance_summary: Dict[str, Any],
    candidates: PublicCandidates,
    user_goal_text: str,
    remaining_global_budget: Dict[str, Any],
    relaxation_scale_context: Dict[str, Any],
) -> Dict[str, Any]:
    objective_part = _objective_observation_part(instance, candidates, user_goal_text)
    evidence = [
        {"id": "E1", "type": "user_goal_and_instance", "summary": {"user_goal": user_goal_text, "instance_summary": instance_summary}},
        {"id": "E2", "type": "objective_metric_definitions", "summary": objective_part["objective_metric_definitions"]},
        {"id": "E3", "type": "remaining_global_budget", "summary": remaining_global_budget},
        {"id": "E4", "type": "relaxation_scale_context", "summary": relaxation_scale_context},
    ]
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "decision_context": {
            "stage": "supervisor_kickoff",
            "task": "Select global objective and issue the initial construction contract.",
            "user_goal": user_goal_text,
        },
        "remaining_global_budget": remaining_global_budget,
        "next_contract_resource_limits": resource_limits,
        "objective_metric_definitions": objective_part["objective_metric_definitions"],
        "instance_overview": objective_part["instance_overview"],
        "instance_summary": instance_summary,
        "objective_candidates": _public(candidates, "objective_candidates"),
        "feasibility_mode_candidates": _public(candidates, "feasibility_mode_candidates"),
        "relaxable_violation_candidates": _public(candidates, "relaxable_violation_candidates"),
        "completion_event_candidates": _public(candidates, "completion_event_candidates"),
        "relaxation_scale_context": dict(relaxation_scale_context),
        "evidence_items": evidence,
        "memory_items": [],
    }


def build_supervisor_review_observation(
    *,
    remaining_global_budget: Dict[str, Any],
    completed_contract: Dict[str, Any],
    completed_contract_progress: Dict[str, Any],
    completed_contract_result: Dict[str, Any],
    working_summary: Dict[str, Any],
    best_summary: Optional[Dict[str, Any]],
    candidate_landscape: Dict[str, Any],
    recent_memory: List[Dict[str, Any]],
    candidates: PublicCandidates,
    relaxation_scale_context: Dict[str, Any],
) -> Dict[str, Any]:
    evidence = [
        {"id": "E1", "type": "completed_contract", "summary": completed_contract},
        {"id": "E2", "type": "completed_contract_result", "summary": completed_contract_result},
        {"id": "E3", "type": "working_solution", "summary": working_summary},
        {"id": "E4", "type": "best_solution", "summary": best_summary or {}},
        {"id": "E5", "type": "candidate_landscape", "summary": candidate_landscape},
        {"id": "E6", "type": "remaining_global_budget", "summary": remaining_global_budget},
    ]
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "decision_context": {
            "stage": "supervisor_review",
            "task": "Review the completed contract and issue the next contract or stop.",
        },
        "remaining_global_budget": remaining_global_budget,
        "next_contract_resource_limits": resource_limits,
        "completed_contract": _solver_safe_contract(completed_contract),
        "completed_contract_progress": completed_contract_progress,
        "completed_contract_result": completed_contract_result,
        "current_solution": working_summary,
        "best_solution": best_summary or {},
        "candidate_landscape": candidate_landscape,
        "recent_memory": recent_memory,
        "objective_candidates": _public(candidates, "objective_candidates"),
        "feasibility_mode_candidates": _public(candidates, "feasibility_mode_candidates"),
        "relaxable_violation_candidates": _public(candidates, "relaxable_violation_candidates"),
        "completion_event_candidates": _public(candidates, "completion_event_candidates"),
        "relaxation_scale_context": dict(relaxation_scale_context),
        "evidence_items": evidence,
        "memory_items": recent_memory,
    }


def build_solver_observation(
    *,
    active_contract: Dict[str, Any],
    contract_progress: Dict[str, Any],
    remaining_contract_resources: Dict[str, Any],
    remaining_global_budget: Dict[str, Any],
    working_summary: Dict[str, Any],
    best_summary: Optional[Dict[str, Any]],
    candidate_landscape: Dict[str, Any],
    recent_memory: List[Dict[str, Any]],
    candidates: PublicCandidates,
) -> Dict[str, Any]:
    contract = _solver_safe_contract(active_contract)
    contract_type = str(contract.get("contract_type", ""))
    if contract_type == "initial_construction":
        allowed_actions = ["construct_initial", "request_supervisor_review"]
    else:
        allowed_actions = ["run_alns", "request_supervisor_review"]
    contract["remaining_contract_resources"] = remaining_contract_resources
    evidence = _state_evidence(working_summary, best_summary, candidate_landscape, remaining_contract_resources, remaining_global_budget)
    return {
        "active_contract": contract,
        "contract_progress": contract_progress,
        "remaining_global_budget": remaining_global_budget,
        "current_solution": working_summary,
        "best_solution": best_summary or {},
        "candidate_landscape": candidate_landscape,
        "available_action_candidates": [{"name": name, "description": _action_description(name)} for name in allowed_actions],
        "available_alns_candidates": {
            name: _public(candidates, name)
            for name in (
                "destroy_operator_candidates",
                "destroy_signal_candidates",
                "insertion_operator_candidates",
                "insertion_task_signal_candidates",
                "insertion_position_signal_candidates",
                "acceptance_candidates",
            )
        },
        "recent_solver_results": recent_memory,
        "evidence_items": evidence,
        "memory_items": recent_memory,
    }


def next_contract_resource_limits(remaining_global_budget: Dict[str, Any]) -> Dict[str, Any]:
    step_calls = int(float(remaining_global_budget.get("step_calls", 0) or 0))
    solver_calls = int(float(remaining_global_budget.get("solver_calls", 0) or 0))
    return {
        "max_solver_actions_allowed": max(0, min(step_calls, solver_calls)),
        "max_time_sec_allowed": max(0.0, float(remaining_global_budget.get("time_sec", 0.0) or 0.0)),
        "max_iters_allowed": max(0, int(float(remaining_global_budget.get("iters", 0) or 0))),
    }


def _solver_safe_contract(active_contract: Dict[str, Any]) -> Dict[str, Any]:
    contract = dict(active_contract)
    contract.pop("feasibility_policy", None)
    contract["stage_objective_layers"] = [
        item.get("metric", "") if isinstance(item, dict) else str(item)
        for item in contract.get("stage_objective_layers", [])
    ]
    return contract


def _objective_observation_part(instance: Instance, candidates: PublicCandidates, user_goal_text: str) -> Dict[str, Any]:
    del user_goal_text
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    priorities = [float(task.priority) for task in tasks]
    priority_counts = Counter(priorities)
    capable_counts = [sum(1 for agent in agents if _capable(agent, task)) for task in tasks]
    depot_distances = [instance.distance(instance.depot.loc, task.loc) for task in tasks]
    nearest_distances = _nearest_task_distances(instance, tasks)
    service_times = [float(task.service_time) for task in tasks]
    time_window_widths = [float(task.tw_end - task.tw_start) for task in tasks]
    direct_arrivals, unavailable_arrivals = _direct_arrival_times(instance, tasks, agents)
    return {
        "objective_metric_definitions": _objective_metric_definitions(candidates),
        "instance_overview": {
            "scale": {
                "num_tasks": len(tasks),
                "num_agents": len(agents),
                "tasks_per_agent": _round(len(tasks) / len(agents)) if agents else None,
            },
            "task_value": {
                "field": "priority[t]",
                "used_by_metric": "missed_priority",
                "distribution": _distribution(priorities, include_sum=True),
                "counts_by_value": {
                    str(_round(value)): int(count)
                    for value, count in sorted(priority_counts.items())
                },
            },
            "task_assignability": {
                "field": "capable_agents[t]",
                "definition": "agents that have all required skills for task t",
                "distribution": _distribution(capable_counts),
                "counts": {
                    "zero_capable_tasks": sum(1 for count in capable_counts if count == 0),
                    "one_capable_task": sum(1 for count in capable_counts if count == 1),
                    "two_or_fewer_capable_tasks": sum(1 for count in capable_counts if count <= 2),
                },
            },
            "travel_distance_reference": {
                "fields": ["distance from depot to task", "distance from task to nearest other task"],
                "distance_from_depot_to_task": _distribution(depot_distances),
                "nearest_task_distance": _distribution(nearest_distances),
            },
            "task_time": {
                "service_time": _distribution(service_times),
                "time_window_width": _distribution(time_window_widths),
                "direct_arrival_time_from_depot": {
                    "definition": "for each task, minimum depot-to-task travel time among capable agents",
                    "distribution": _distribution(direct_arrivals),
                    "unavailable_task_count": unavailable_arrivals,
                },
            },
            "agent_profile": {
                "initial_energy": _distribution([agent.init_energy for agent in agents]),
                "speed": _distribution([agent.speed for agent in agents]),
                "travel_energy_rate": _distribution([agent.travel_energy_rate for agent in agents]),
                "standby_power": _distribution([agent.standby_power for agent in agents]),
                "skill_count": _distribution([len(agent.skills) for agent in agents]),
            },
        },
    }


def _public(candidates: PublicCandidates, name: str) -> List[Dict[str, str]]:
    return [candidate.as_dict() for candidate in getattr(candidates, name)]


def _objective_metric_definitions(candidates: PublicCandidates) -> List[Dict[str, Any]]:
    out = []
    for name in candidates.names("objective_candidates"):
        item = {"metric": name}
        item.update(_OBJECTIVE_METRIC_DEFINITIONS[name])
        out.append(item)
    return out


def _action_description(name: str) -> str:
    return {
        "construct_initial": "Build the first working solution with insertion control.",
        "run_alns": "Run one ALNS action under the active contract.",
        "request_supervisor_review": "End the current contract and ask Supervisor to review.",
    }.get(name, "Available solver action.")


def _round(value: float) -> float:
    return round(float(value), 6)


def _quantile(sorted_values: Sequence[float], q: float) -> Optional[float]:
    if not sorted_values:
        return None
    values = sorted(float(value) for value in sorted_values)
    if len(values) == 1:
        return _round(values[0])
    pos = (len(values) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    frac = pos - lo
    return _round(values[lo] * (1.0 - frac) + values[hi] * frac)


def _distribution(values: Sequence[float], *, include_sum: bool = False) -> Dict[str, Any]:
    vals = sorted(float(value) for value in values)
    if not vals:
        base: Dict[str, Any] = {"min": None, "p25": None, "median": None, "p75": None, "max": None}
        if include_sum:
            base["sum"] = 0.0
        return base
    out = {
        "min": _round(vals[0]),
        "p25": _quantile(vals, 0.25),
        "median": _quantile(vals, 0.50),
        "p75": _quantile(vals, 0.75),
        "max": _round(vals[-1]),
    }
    if include_sum:
        out["sum"] = _round(sum(vals))
    return out


def _capable(agent: Agent, task: Task) -> bool:
    return set(task.skill_req).issubset(agent.skills)


def _nearest_task_distances(instance: Instance, tasks: List[Task]) -> List[float]:
    if len(tasks) <= 1:
        return []
    out = []
    for i, task in enumerate(tasks):
        best = None
        for j, other in enumerate(tasks):
            if i == j:
                continue
            distance = instance.distance(task.loc, other.loc)
            best = distance if best is None else min(best, distance)
        if best is not None:
            out.append(best)
    return out


def _direct_arrival_times(instance: Instance, tasks: List[Task], agents: List[Agent]) -> Tuple[List[float], int]:
    values = []
    unavailable = 0
    for task in tasks:
        times = [
            instance.travel_time(agent, instance.depot.loc, task.loc)
            for agent in agents
            if _capable(agent, task)
        ]
        if not times:
            unavailable += 1
            continue
        values.append(min(times))
    return values, unavailable


def _state_evidence(
    working: Dict[str, Any],
    best: Optional[Dict[str, Any]],
    landscape: Dict[str, Any],
    contract_budget: Dict[str, Any],
    global_budget: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        {"id": "E1", "type": "working_solution", "summary": working},
        {"id": "E2", "type": "best_solution", "summary": best or {}},
        {"id": "E3", "type": "candidate_landscape", "summary": landscape},
        {"id": "E4", "type": "remaining_contract_resources", "summary": contract_budget},
        {"id": "E5", "type": "remaining_global_budget", "summary": global_budget},
    ]


__all__ = [
    "build_supervisor_kickoff_observation",
    "build_supervisor_review_observation",
    "build_solver_observation",
    "next_contract_resource_limits",
]
