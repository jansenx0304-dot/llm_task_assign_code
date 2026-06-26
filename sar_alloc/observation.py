from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence

from .llm_public_interface import PublicCandidates
from .models import Agent, Instance, Task
from .operators.types import DESTROY_OPERATOR_NAMES, INSERTION_OPERATOR_NAMES


def build_supervisor_kickoff_observation(
    *,
    instance: Instance,
    instance_summary: Dict[str, Any],
    candidates: PublicCandidates,
    user_goal_text: str,
    remaining_global_budget: Dict[str, Any],
    relaxation_scale_context: Dict[str, Any],
    observation_id: str = "O0",
    instance_name: str = "",
) -> Dict[str, Any]:
    del user_goal_text
    profile = _problem_evidence(instance, instance_summary)
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "run_context": {
            "observation_id": observation_id,
            "phase": "supervisor_kickoff",
            "instance": instance_name,
            "remaining_global_resources": dict(remaining_global_budget),
        },
        "problem_profile": profile,
        "relaxation_reference": _relaxation_reference(relaxation_scale_context),
        "action_space": {
            "allowed_contract_types": ["initial_construction"],
            "allowed_objective_metrics": list(
                candidates.names("objective_candidates")
            ),
            "allowed_feasibility_modes": list(
                candidates.names("feasibility_mode_candidates")
            ),
            "allowed_relaxable_violation_types": list(
                candidates.names("relaxable_violation_candidates")
            ),
            "next_contract_resource_limits": resource_limits,
        },
    }


def build_supervisor_review_observation(
    *,
    remaining_global_budget: Dict[str, Any],
    completed_contract: Dict[str, Any],
    completed_contract_progress: Dict[str, Any],
    completed_contract_result: Dict[str, Any],
    working_summary: Dict[str, Any],
    best_summary: Optional[Dict[str, Any]],
    recent_memory: Optional[List[Dict[str, Any]]] = None,
    candidates: Optional[PublicCandidates] = None,
    relaxation_scale_context: Optional[Dict[str, Any]] = None,
    verifications: Optional[List[Dict[str, Any]]] = None,
    observation_id: str = "O_review",
    instance_name: str = "",
) -> Dict[str, Any]:
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "run_context": {
            "observation_id": observation_id,
            "phase": "supervisor_review",
            "instance": instance_name,
            "remaining_global_resources": dict(remaining_global_budget),
        },
        "completed_contract": _contract_view(
            completed_contract, completed_contract_progress
        ),
        "completed_progress": _completed_progress_view(completed_contract_progress),
        "contract_result": _contract_result_view(completed_contract_result),
        "verification_summary": _verification_summary(verifications or []),
        "solution_state": {
            "working": _state_digest_from_summary(working_summary),
            "best_feasible": _best_digest(best_summary),
        },
        "recent_memory": list(recent_memory or []),
        "relaxation_reference": _relaxation_reference(relaxation_scale_context or {}),
        "action_space": {
            "allowed_contract_types": [
                "alns_search",
                "recovery",
                "final_refinement",
            ],
            "allowed_objective_metrics": list(
                candidates.names("objective_candidates")
                if candidates is not None
                else (
                    "missed_priority",
                    "unassigned_count",
                    "energy_total",
                    "total_distance",
                    "makespan",
                    "route_balance",
                )
            ),
            "allowed_feasibility_modes": list(
                candidates.names("feasibility_mode_candidates")
                if candidates is not None
                else ("strict", "relaxed_recoverable", "recovery_only")
            ),
            "allowed_relaxable_violation_types": list(
                candidates.names("relaxable_violation_candidates")
                if candidates is not None
                else ("time_window", "energy")
            ),
            "next_contract_resource_limits": resource_limits,
        },
    }


def build_solver_observation(
    *,
    active_contract: Dict[str, Any],
    contract_progress: Dict[str, Any],
    remaining_contract_resources: Dict[str, Any],
    remaining_global_budget: Optional[Dict[str, Any]] = None,
    working_summary: Optional[Dict[str, Any]] = None,
    best_summary: Optional[Dict[str, Any]] = None,
    candidate_landscape: Optional[Dict[str, Any]] = None,
    recent_memory: Optional[List[Dict[str, Any]]] = None,
    candidates: PublicCandidates,
    last_verification: Optional[Dict[str, Any]] = None,
    observation_id: str = "O_solver",
    step_index: int = 0,
    has_working_solution: Optional[bool] = None,
    instance_name: str = "",
) -> Dict[str, Any]:
    contract = _solver_contract_view(active_contract, contract_progress)
    contract_type = str(contract.get("contract_type", ""))
    has_working = bool(
        contract_type != "initial_construction"
        if has_working_solution is None
        else has_working_solution
    )
    progress = _progress_view(
        active_contract,
        contract_progress,
        remaining_contract_resources,
        last_verification,
    )
    action_space = _action_space(
        candidates,
        contract_type=contract_type,
        has_working_solution=has_working,
        progress=progress,
    )
    return {
        "run_context": {
            "observation_id": observation_id,
            "phase": (
                "solver_initial_construction"
                if contract_type == "initial_construction"
                else "solver_step"
            ),
            "instance": instance_name,
            "step_index": step_index,
            "contract_id": contract.get("contract_id", ""),
        },
        "active_contract": contract,
        "execution_state": {
            **action_space,
            "working_solution_exists": has_working,
            "remaining_contract_resources": dict(remaining_contract_resources),
            "remaining_global_resources": dict(remaining_global_budget or {}),
            "progress": progress,
        },
        "solution_evidence": {
            "working": _state_digest_from_summary(working_summary or {}),
            "best_feasible": _best_digest(best_summary),
        },
        "destroy_facts": dict((candidate_landscape or {}).get("destroy_facts", {}) or {}),
        "insertion_facts": dict((candidate_landscape or {}).get("insertion_facts", {}) or {}),
        "targetable_evidence": _targetable_evidence(
            candidate_landscape or {}, working_summary or {}, last_verification
        ),
        "control_catalog": _control_catalog(candidates),
        "recent_memory": list(recent_memory or []),
        "runtime_feedback": {
            "last_verification": _compact_last_verification(last_verification),
            "operator_effectiveness_recent": _operator_effectiveness_recent(
                recent_memory or [], last_verification
            ),
        },
    }


def next_contract_resource_limits(
    remaining_global_budget: Dict[str, Any],
) -> Dict[str, Any]:
    step_calls = int(float(remaining_global_budget.get("step_calls", 0) or 0))
    solver_calls = int(float(remaining_global_budget.get("solver_calls", 0) or 0))
    return {
        "max_solver_actions_allowed": max(0, min(step_calls, solver_calls)),
        "max_time_sec_allowed": max(
            0.0, float(remaining_global_budget.get("time_sec", 0.0) or 0.0)
        ),
        "max_iters_allowed": max(
            0, int(float(remaining_global_budget.get("iters", 0) or 0))
        ),
    }


def _contract_view(
    active_contract: Dict[str, Any], progress: Dict[str, Any]
) -> Dict[str, Any]:
    del progress
    feasibility = dict(active_contract.get("feasibility_control", {}) or {})
    feasibility_policy = dict(active_contract.get("feasibility_policy", {}) or {})
    return {
        "contract_id": active_contract.get("contract_id", ""),
        "contract_type": active_contract.get("contract_type", ""),
        "objective_layers": [
            item.get("metric", "") if isinstance(item, dict) else str(item)
            for item in active_contract.get("objective_layers", [])
        ],
        "feasibility_control": {
            "mode": str(feasibility.get("mode", "strict")),
            "relaxation_ratios": [
                dict(item) for item in feasibility.get("relaxation_ratios", []) or []
            ],
            "runtime_per_type": {
                str(name): dict(values)
                for name, values in dict(
                    feasibility_policy.get("per_type", {}) or {}
                ).items()
            },
        },
        "decision_basis": [
            dict(item) for item in active_contract.get("decision_basis", []) or []
        ],
        "situation_summary": dict(active_contract.get("situation_summary", {}) or {}),
        "target_intents": [
            dict(item) for item in active_contract.get("target_intents", []) or []
        ],
        "protected_metrics": [
            dict(item) for item in active_contract.get("protected_metrics", [])
        ],
        "protected_metric_baseline": dict(
            active_contract.get("protected_metric_baseline", {}) or {}
        ),
        "resource_policy": dict(active_contract.get("resource_policy", {}) or {}),
        "exit_conditions": {
            "success": [
                dict(item)
                for item in (active_contract.get("exit_conditions", {}) or {}).get(
                    "success", []
                )
            ],
            "failure": [
                dict(item)
                for item in (active_contract.get("exit_conditions", {}) or {}).get(
                    "failure", []
                )
            ],
        },
        "audit_note": str(active_contract.get("audit_note", "") or ""),
    }


def _solver_contract_view(
    active_contract: Dict[str, Any], progress: Dict[str, Any]
) -> Dict[str, Any]:
    contract = _contract_view(active_contract, progress)
    return {
        "contract_id": contract["contract_id"],
        "contract_type": contract["contract_type"],
        "objective_layers": contract["objective_layers"],
        "feasibility_control": contract["feasibility_control"],
        "target_intents": [
            dict(item) for item in active_contract.get("target_intents", []) or []
        ],
        "protected_metrics": contract["protected_metrics"],
        "protected_metric_baseline": contract["protected_metric_baseline"],
        "resource_policy": contract["resource_policy"],
        "exit_conditions": contract["exit_conditions"],
    }


def _completed_progress_view(progress: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract_id": progress.get("contract_id", ""),
        "solver_actions": int(progress.get("solver_actions", 0) or 0),
        "iters_used": int(progress.get("iters_used", 0) or 0),
        "time_used_sec": float(progress.get("time_used_sec", 0.0) or 0.0),
        "contract_objective_status_counts": dict(
            progress.get("contract_objective_status_counts", {}) or {}
        ),
        "dominant_blocker_counts": dict(
            progress.get("dominant_blocker_counts", {}) or {}
        ),
    }


def _contract_result_view(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "completion_status": result.get("completion_status", ""),
        "completion_reason": result.get("completion_reason", ""),
        "condition_report": [
            {
                "condition_id": item.get("condition_id", ""),
                "source": item.get("source", ""),
                "actual": item.get("actual"),
                "op": item.get("op", ""),
                "expected": item.get("expected"),
                "window": item.get("window", 1),
                "passed": bool(item.get("passed", False)),
            }
            for item in result.get("condition_report", []) or []
            if isinstance(item, dict)
        ],
    }


def _problem_evidence(
    instance: Instance, instance_summary: Dict[str, Any]
) -> Dict[str, Any]:
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    capable_counts = [_capable_count(agents, task) for task in tasks]
    priorities = [float(task.priority) for task in tasks]
    high_cut = (
        sorted(priorities)[max(0, int(0.75 * len(priorities)) - 1)]
        if priorities
        else 0.0
    )
    scarce = [
        task
        for task, count in zip(tasks, capable_counts)
        if count <= max(1, len(agents) // 4)
    ]
    tw_frac = float(
        (instance_summary.get("time_window_risk", {}) or {}).get(
            "negative_slack_frac_lb", 0.0
        )
        or 0.0
    )
    energy_frac = float(
        (instance_summary.get("energy_risk", {}) or {}).get("energy_tight_frac_lb", 0.0)
        or 0.0
    )
    spatial = dict(instance_summary.get("spatial", {}) or {})
    skill = dict(instance_summary.get("skills", {}) or {})
    capable_dist = Counter(capable_counts)
    return {
        "num_tasks": len(tasks),
        "num_agents": len(agents),
        "priority_mass": round(sum(priorities), 6),
        "high_priority_task_count": sum(1 for value in priorities if value >= high_cut),
        "zero_capable_task_count": sum(1 for count in capable_counts if count == 0),
        "static_capability_scarce_task_count": len(scarce),
        "static_capability_scarce_priority_mass": round(
            sum(float(task.priority) for task in scarce), 6
        ),
        "time_window_negative_slack_frac_lb": tw_frac,
        "energy_tight_frac_lb": energy_frac,
        "skill_uncoverable_task_frac": float(
            skill.get("skill_uncoverable_task_frac", 0.0) or 0.0
        ),
        "skill_bottleneck_task_frac": float(
            skill.get("skill_bottleneck_task_frac", 0.0) or 0.0
        ),
        "static_capable_count_distribution": {
            str(count): int(total) for count, total in sorted(capable_dist.items())
        },
        "spatial": {
            "cluster_strength": float(spatial.get("cluster_strength", 0.0) or 0.0),
            "radius95_to_depot": float(spatial.get("radius95_to_depot", 0.0) or 0.0),
        },
    }


def _targetable_evidence(
    landscape: Dict[str, Any],
    working_summary: Dict[str, Any],
    last_verification: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    del working_summary
    insertion_facts = dict(landscape.get("insertion_facts", {}) or {})
    unassigned_tasks = _targetable_unassigned_tasks(landscape)
    candidate_routes = _targetable_routes(landscape)
    visible_task_ids = sorted(
        {
            int(tid)
            for tid in insertion_facts.get("unassigned_task_ids", []) or []
            if not isinstance(tid, bool)
        }
    )
    visible_agent_ids = sorted(
        {int(item["agent_id"]) for item in candidate_routes if "agent_id" in item}
    )
    compact_last = _compact_last_verification(last_verification)
    return {
        "visible_task_ids": visible_task_ids,
        "visible_agent_ids": visible_agent_ids,
        "target_catalog": {
            "tasks": unassigned_tasks,
            "routes": candidate_routes,
        },
        "last_runtime_target": dict(compact_last.get("runtime_target", {}) or {}),
        "last_target_engagement": dict(compact_last.get("target_engagement", {}) or {}),
        "last_target_progress": dict(compact_last.get("target_progress", {}) or {}),
    }


def _targetable_unassigned_tasks(landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
    facts = dict(landscape.get("insertion_facts", {}) or {})
    out = [
        {
            "task_id": int(item.get("task_id", 0) or 0),
            "priority": float(item.get("priority", 0.0) or 0.0),
            "candidate_position_count": int(
                item.get("candidate_position_count", 0) or 0
            ),
            "feasible_position_count": int(
                item.get("feasible_position_count", 0) or 0
            ),
            "capable_agent_count": int(item.get("capable_agent_count", 0) or 0),
        }
        for item in facts.get("unassigned_task_facts", []) or []
        if isinstance(item, dict) and item.get("task_id") is not None
    ]
    out.sort(key=lambda item: int(item["task_id"]))
    return out[:12]


def _targetable_routes(landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
    routes = [
        {
            "agent_id": int(item.get("agent_id", 0) or 0),
            "route_len": int(item.get("route_len", 0) or 0),
            "route_cost": float(item.get("route_cost", 0.0) or 0.0),
        }
        for item in landscape.get("candidate_routes", []) or []
        if isinstance(item, dict) and item.get("agent_id") is not None
    ]
    for item in routes:
        item["remaining_energy"] = float(item.get("remaining_energy", 0.0) or 0.0)
    routes.sort(key=lambda item: int(item.get("agent_id", 0) or 0))
    return routes[:12]


def _state_digest_from_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    quality = summary.get("quality_summary", {}) or {}
    feasibility = summary.get("feasibility_summary", {}) or {}
    ratios = dict(feasibility.get("violation_ratio_by_type", {}) or {})
    recoverable = float(feasibility.get("recoverable_violation_total", 0.0) or 0.0)
    unrecoverable = float(
        feasibility.get("unrecoverable_violation_total", 0.0) or 0.0
    )
    return {
        "is_feasible": bool(
            feasibility.get("is_feasible", summary.get("is_feasible", False))
        ),
        "quality": {
            name: float(quality.get(name, 0.0) or 0.0)
            for name in (
                "missed_priority",
                "unassigned_count",
                "energy_total",
                "total_distance",
                "makespan",
                "route_balance",
            )
            if name in quality
        },
        "debt": {
            "recoverable_violation_total": recoverable,
            "unrecoverable_violation_total": unrecoverable,
            "violation_ratio_by_type": {str(k): float(v) for k, v in ratios.items()},
        },
    }


def _best_digest(best_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not best_summary:
        return {"exists": False, "quality": {}}
    return {
        "exists": True,
        "quality": _state_digest_from_summary(best_summary).get("quality", {}),
    }


def _compact_last_verification(
    verification: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if not verification:
        return {"exists": False}
    trace = verification.get("trace", {}) or {}
    flow = trace.get("trial_flow", {}) or {}
    return {
        "exists": True,
        "verification_id": verification.get("verification_id"),
        "contract_objective_status": verification.get("contract_objective_status"),
        "dominant_blocker": verification.get("dominant_blocker"),
        "metric_delta": (verification.get("metric_delta", {}) or {}).get("working", {}),
        "debt_delta": verification.get("debt_delta", {}),
        "protected_metric_result": dict(
            verification.get("protected_metric_result", {}) or {}
        ),
        "feasibility_result": dict(verification.get("feasibility_result", {}) or {}),
        "improvement_flags": dict(verification.get("improvement_flags", {}) or {}),
        "trace_counts": {
            "candidate_trials": int(flow.get("candidate_trials", 0) or 0),
            "feasibility_rejected": int(flow.get("feasibility_rejected", 0) or 0),
            "accepted": int(flow.get("accepted_trials", 0) or 0),
            "global_best_updates": int(flow.get("global_best_improved_trials", 0) or 0),
        },
        "runtime_target": dict(trace.get("runtime_target", {}) or {}),
        "target_engagement": dict(trace.get("target_engagement", {}) or {}),
        "target_progress": dict(trace.get("target_progress", {}) or {}),
        "source": "program_verifier",
    }


def _operator_effectiveness_recent(
    recent_memory: List[Dict[str, Any]],
    last_verification: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    destroy = {
        str(name): {
            "used": 0,
            "accepted": 0,
            "global_best_improved": 0,
            "protected_rejects": 0,
            "mean_removed_count": 0.0,
            "total_reward": 0.0,
        }
        for name in DESTROY_OPERATOR_NAMES
    }
    insertion = {
        str(name): {
            "used": 0,
            "accepted": 0,
            "inserted_sum": 0,
            "positions_checked_sum": 0,
            "failed_insertions": 0,
        }
        for name in INSERTION_OPERATOR_NAMES
    }
    sources: List[Dict[str, Any]] = []
    for item in recent_memory:
        if isinstance(item, dict):
            sources.append(item)
    if last_verification:
        sources.append({"verification": last_verification})
    for item in sources[-3:]:
        verification = dict(item.get("verification", item) or {})
        trace = dict(verification.get("trace", {}) or {})
        for name, values in dict(trace.get("operator_effectiveness", {}).get("destroy", {}) or {}).items():
            if name in destroy and isinstance(values, dict):
                for key in destroy[name]:
                    destroy[name][key] += values.get(key, 0) or 0
        for name, values in dict(trace.get("operator_effectiveness", {}).get("insertion", {}) or {}).items():
            if name in insertion and isinstance(values, dict):
                for key in insertion[name]:
                    insertion[name][key] += values.get(key, 0) or 0
    return {"destroy": destroy, "insertion": insertion}


def _verification_summary(verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = Counter(
        str(item.get("contract_objective_status", "")) for item in verifications
    )
    blockers = Counter(str(item.get("dominant_blocker", "")) for item in verifications)
    return {
        "action_count": len(verifications),
        "contract_objective_status_counts": dict(statuses),
        "dominant_blocker_counts": dict(blockers),
        "last": _compact_last_verification(
            verifications[-1] if verifications else None
        ),
    }


def _progress_view(
    active_contract: Dict[str, Any],
    contract_progress: Dict[str, Any],
    remaining_contract_resources: Dict[str, Any],
    last_verification: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    policy = dict(active_contract.get("resource_policy", {}) or {})
    actions_used = int(contract_progress.get("solver_actions", 0) or 0)
    status_counts = dict(
        contract_progress.get("contract_objective_status_counts", {}) or {}
    )
    recent_statuses = list(
        contract_progress.get("recent_contract_objective_statuses", []) or []
    )
    min_actions = int(policy.get("min_actions", 1) or 1)
    del last_verification
    return {
        "actions_used": actions_used,
        "actions_remaining": int(remaining_contract_resources.get("actions", 0) or 0),
        "min_actions_remaining": int(
            remaining_contract_resources.get(
                "min_actions_remaining", max(0, min_actions - actions_used)
            )
            or 0
        ),
        "iters_used": int(contract_progress.get("iters_used", 0) or 0),
        "time_used_sec": float(contract_progress.get("time_used_sec", 0.0) or 0.0),
        "remaining_resources": dict(remaining_contract_resources),
        "contract_objective_status_counts": status_counts,
        "last_contract_objective_status": str(
            recent_statuses[-1] if recent_statuses else "none"
        ),
        "recent_outcome_window": {
            "contract_objective_statuses": recent_statuses[-5:],
        },
    }


def _action_space(
    candidates: PublicCandidates,
    *,
    contract_type: str,
    has_working_solution: bool,
    progress: Dict[str, Any],
) -> Dict[str, Any]:
    normal_action = "construct_initial" if contract_type == "initial_construction" else "run_alns"
    has_resources = int(progress.get("actions_remaining", 0) or 0) > 0
    normal_allowed = bool(
        has_resources
        and (
            (normal_action == "construct_initial" and not has_working_solution)
            or (normal_action == "run_alns" and has_working_solution)
        )
    )
    hard_inexecutable: List[Dict[str, str]] = []
    if not has_resources:
        hard_inexecutable.append({"action": normal_action, "reason": "no_remaining_action_budget"})
    elif normal_action == "construct_initial" and has_working_solution:
        hard_inexecutable.append({"action": normal_action, "reason": "working_solution_already_exists"})
    elif normal_action == "run_alns" and not has_working_solution:
        hard_inexecutable.append({"action": normal_action, "reason": "missing_working_solution"})
    allowed_actions = [normal_action] if normal_allowed else []
    min_actions_remaining = int(progress.get("min_actions_remaining", 0) or 0)
    if has_resources and min_actions_remaining <= 0:
        allowed_actions.append("request_supervisor_review")
    else:
        hard_inexecutable.append(
            {
                "action": "request_supervisor_review",
                "reason": (
                    "min_actions_not_reached"
                    if min_actions_remaining > 0
                    else "no_remaining_action_budget"
                ),
            }
        )
    base = {
        "hard_executable_actions": allowed_actions,
        "hard_inexecutable_actions": hard_inexecutable,
    }
    return base


def _control_catalog(candidates: PublicCandidates) -> Dict[str, Any]:
    raw = candidates.as_dict()
    return {
        "insertion_operators": raw["insertion_operator_candidates"],
        "insertion_task_signals": raw["insertion_task_signal_candidates"],
        "insertion_position_signals": raw["insertion_position_signal_candidates"],
        "destroy_operators": raw["destroy_operator_candidates"],
        "destroy_signals": raw["destroy_signal_candidates"],
        "acceptance_modes": raw["acceptance_candidates"],
        "intensity_mappings": {
            "destroy.remove_ratio": "0.05 + 0.03 * intensity_score",
            "acceptance.greedy": "no worsening accepted",
            "acceptance.threshold": "threshold = 0.5 * intensity_score; worsening_allowance = 0.02 * intensity_score",
            "acceptance.sa": "threshold = intensity_score; worsening_allowance = 0.05 * intensity_score",
        },
    }


def _relaxation_reference(context: Dict[str, Any]) -> Dict[str, float]:
    if "time_window_median_width" in context or "agent_energy_median" in context:
        return {
            "time_window_median_width": float(
                context.get("time_window_median_width", 0.0) or 0.0
            ),
            "agent_energy_median": float(
                context.get("agent_energy_median", 0.0) or 0.0
            ),
        }
    return {
        "time_window_median_width": float(
            (context.get("time_window", {}) or {}).get("median", 0.0) or 0.0
        ),
        "agent_energy_median": float(
            (context.get("energy", {}) or {}).get("median", 0.0) or 0.0
        ),
    }


def _capable_count(agents: Sequence[Agent], task: Task) -> int:
    return sum(1 for agent in agents if set(task.skill_req).issubset(agent.skills))


__all__ = [
    "build_supervisor_kickoff_observation",
    "build_supervisor_review_observation",
    "build_solver_observation",
    "next_contract_resource_limits",
]
