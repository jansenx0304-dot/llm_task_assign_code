from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence

from .control_surface import FIELD_CANDIDATES
from .llm_public_interface import PublicCandidates
from .models import Agent, Instance, Task


def build_supervisor_kickoff_observation(
    *,
    instance: Instance,
    instance_summary: Dict[str, Any],
    candidates: PublicCandidates,
    user_goal_text: str,
    remaining_global_budget: Dict[str, Any],
    relaxation_scale_context: Dict[str, Any],
    observation_id: str = "O0",
) -> Dict[str, Any]:
    del candidates
    profile = _problem_profile(instance, instance_summary)
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "observation_id": observation_id,
        "frame_type": "supervisor_kickoff",
        "role": "supervisor",
        "user_goal": user_goal_text,
        "budget_caps": {
            "max_solver_actions": resource_limits["max_solver_actions_allowed"],
            "max_time_sec": resource_limits["max_time_sec_allowed"],
            "max_iters": resource_limits["max_iters_allowed"],
        },
        "problem_profile": profile,
        "relaxation_reference": _relaxation_reference(relaxation_scale_context),
        "allowed_contract_types": ["initial_construction"],
        "allowed_objective_metrics": [
            "missed_priority",
            "unassigned_count",
            "energy_total",
            "total_distance",
            "makespan",
            "route_balance",
        ],
        "next_contract_resource_limits": resource_limits,
    }


def build_supervisor_review_observation(
    *,
    remaining_global_budget: Dict[str, Any],
    completed_contract: Dict[str, Any],
    completed_contract_progress: Dict[str, Any],
    completed_contract_result: Dict[str, Any],
    working_summary: Dict[str, Any],
    best_summary: Optional[Dict[str, Any]],
    candidate_landscape: Optional[Dict[str, Any]] = None,
    recent_memory: Optional[List[Dict[str, Any]]] = None,
    candidates: Optional[PublicCandidates] = None,
    relaxation_scale_context: Optional[Dict[str, Any]] = None,
    verifications: Optional[List[Dict[str, Any]]] = None,
    observation_id: str = "O_review",
) -> Dict[str, Any]:
    del candidate_landscape, candidates
    resource_limits = next_contract_resource_limits(remaining_global_budget)
    return {
        "observation_id": observation_id,
        "frame_type": "supervisor_review",
        "role": "supervisor",
        "budget_caps": {
            "max_solver_actions": resource_limits["max_solver_actions_allowed"],
            "max_time_sec": resource_limits["max_time_sec_allowed"],
            "max_iters": resource_limits["max_iters_allowed"],
        },
        "completed_contract": _contract_view(completed_contract, completed_contract_progress),
        "contract_completion": dict(completed_contract_result),
        "condition_report": list(completed_contract_progress.get("condition_report", []) or completed_contract_result.get("condition_report", []) or []),
        "stage_verification_summary": _verification_summary(verifications or []),
        "solution_position": {
            "working": _state_digest_from_summary(working_summary),
            "best_feasible": _best_digest(best_summary),
        },
        "usable_memory": list(recent_memory or []),
        "relaxation_reference": _relaxation_reference(relaxation_scale_context or {}),
        "allowed_contract_types": ["alns_search", "recovery", "final_refinement"],
        "allowed_objective_metrics": [
            "missed_priority",
            "unassigned_count",
            "energy_total",
            "total_distance",
            "makespan",
            "route_balance",
        ],
        "next_contract_resource_limits": resource_limits,
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
) -> Dict[str, Any]:
    del remaining_global_budget
    contract = _contract_view(active_contract, contract_progress)
    contract_type = str(contract.get("contract_type", ""))
    contract["remaining_resources"] = dict(remaining_contract_resources)
    if contract_type == "initial_construction":
        return {
            "observation_id": observation_id,
            "frame_type": "solver_initial_construction",
            "role": "solver",
            "step_index": step_index,
            "contract_view": contract,
            "task_buildability_view": _task_buildability_view(working_summary or {}, candidate_landscape or {}),
            "insertion_position_landscape": _insertion_position_landscape(candidate_landscape or {}),
            "decision_targets": _initial_targets(working_summary or {}, candidate_landscape or {}),
            "last_action_verification": _compact_last_verification(last_verification),
            "action_space": _action_space(candidates, initial=True),
            "usable_memory": list(recent_memory or []),
        }
    return {
        "observation_id": observation_id,
        "frame_type": "solver_step",
        "role": "solver",
        "step_index": step_index,
        "contract_view": contract,
        "state_digest": {
            "working": _state_digest_from_summary(working_summary or {}),
            "best_feasible": _best_digest(best_summary),
        },
        "last_action_verification": _compact_last_verification(last_verification),
        "decision_targets": _decision_targets(active_contract, working_summary or {}, candidate_landscape or {}),
        "action_space": _action_space(candidates, initial=False),
        "usable_memory": list(recent_memory or []),
    }


def next_contract_resource_limits(remaining_global_budget: Dict[str, Any]) -> Dict[str, Any]:
    step_calls = int(float(remaining_global_budget.get("step_calls", 0) or 0))
    solver_calls = int(float(remaining_global_budget.get("solver_calls", 0) or 0))
    return {
        "max_solver_actions_allowed": max(0, min(step_calls, solver_calls)),
        "max_time_sec_allowed": max(0.0, float(remaining_global_budget.get("time_sec", 0.0) or 0.0)),
        "max_iters_allowed": max(0, int(float(remaining_global_budget.get("iters", 0) or 0))),
    }


def _contract_view(active_contract: Dict[str, Any], progress: Dict[str, Any]) -> Dict[str, Any]:
    del progress
    feasibility = dict(active_contract.get("feasibility_control", {}) or {})
    return {
        "contract_id": active_contract.get("contract_id", ""),
        "contract_type": active_contract.get("contract_type", ""),
        "objective_layers": [
            item.get("metric", "") if isinstance(item, dict) else str(item)
            for item in active_contract.get("objective_layers", [])
        ],
        "feasibility_mode": feasibility.get("mode", "strict"),
        "protected_metrics": [dict(item) for item in active_contract.get("protected_metrics", [])],
    }


def _problem_profile(instance: Instance, instance_summary: Dict[str, Any]) -> Dict[str, Any]:
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    capable_counts = [_capable_count(agents, task) for task in tasks]
    priorities = [float(task.priority) for task in tasks]
    high_cut = sorted(priorities)[max(0, int(0.75 * len(priorities)) - 1)] if priorities else 0.0
    scarce = [task for task, count in zip(tasks, capable_counts) if count <= max(1, len(agents) // 4)]
    tw_risk = float((instance_summary.get("time_window_risk", {}) or {}).get("negative_slack_frac_lb", 0.0) or 0.0)
    energy_risk = float((instance_summary.get("energy_risk", {}) or {}).get("energy_tight_frac_lb", 0.0) or 0.0)
    dominant = "energy" if energy_risk >= tw_risk else "time_window"
    return {
        "num_tasks": len(tasks),
        "num_agents": len(agents),
        "priority_mass": round(sum(priorities), 6),
        "high_priority_task_count": sum(1 for value in priorities if value >= high_cut),
        "zero_capable_task_count": sum(1 for count in capable_counts if count == 0),
        "scarce_task_count": len(scarce),
        "scarce_priority_mass": round(sum(float(task.priority) for task in scarce), 6),
        "time_window_risk": _risk_label(tw_risk),
        "energy_risk": _risk_label(energy_risk),
        "dominant_risk": dominant,
    }


def _task_buildability_view(working_summary: Dict[str, Any], landscape: Dict[str, Any]) -> Dict[str, Any]:
    raw_buckets = landscape.get("target_buckets", {}) or {}
    quality = working_summary.get("quality_summary", {}) or {}
    if "unassigned_priority" not in raw_buckets:
        raw_buckets = dict(raw_buckets)
        raw_buckets["unassigned_priority"] = {
            "task_ids": [],
            "task_count": int(quality.get("unassigned_count", 0) or 0),
            "priority_mass": float(quality.get("missed_priority", 0.0) or 0.0),
        }
    active: List[Dict[str, Any]] = []
    inactive: List[Dict[str, Any]] = []
    for kind, target_id, controls in (
        (
            "unassigned_priority", "T_unassigned_priority",
            {
                "insertion_control.task_signal_scores": ["priority_loss", "scarcity_pressure"],
                "insertion_control.position_signal_scores": ["future_slack", "insert_cost"],
            },
        ),
        (
            "scarce_unassigned", "T_scarce_unassigned",
            {
                "insertion_control.task_signal_scores": ["scarcity_pressure", "priority_loss"],
                "insertion_control.position_signal_scores": ["future_slack"],
            },
        ),
    ):
        bucket = dict(raw_buckets.get(kind, {}) or {})
        item = {
            "target_id": target_id,
            "kind": kind,
            "task_ids": [int(value) for value in bucket.get("task_ids", [])],
            "task_count": int(bucket.get("task_count", 0) or 0),
            "priority_mass": float(bucket.get("priority_mass", 0.0) or 0.0),
            "recommended_controls": controls,
        }
        (active if item["task_count"] > 0 else inactive).append(item)
    return {
        "target_buckets": active,
        "inactive_target_summary": [
            {"kind": item["kind"], "task_count": 0, "priority_mass": 0.0}
            for item in inactive
        ],
    }


def _insertion_position_landscape(landscape: Dict[str, Any]) -> Dict[str, Any]:
    stats = landscape.get("candidate_stats", {}) or {}
    candidate_percentiles = stats.get("candidate_position_percentiles", {}) or {}
    feasible_percentiles = stats.get("feasible_position_percentiles", {}) or {}
    return {
        "candidate_position_count": {
            "p25": float(candidate_percentiles.get("p25", 0.0) or 0.0),
            "p50": float(candidate_percentiles.get("p50", 0.0) or 0.0),
            "p75": float(candidate_percentiles.get("p75", 0.0) or 0.0),
            "low_count": int(stats.get("one_feasible_position_tasks", 0) or 0),
            "zero_count": int(stats.get("zero_candidate_tasks", 0) or 0),
        },
        "feasible_position_count": {
            "p25": float(feasible_percentiles.get("p25", 0.0) or 0.0),
            "p50": float(feasible_percentiles.get("p50", 0.0) or 0.0),
            "p75": float(feasible_percentiles.get("p75", 0.0) or 0.0),
            "low_count": int(stats.get("one_feasible_position_tasks", 0) or 0),
            "zero_count": int(stats.get("no_feasible_tasks", 0) or 0),
        },
        "top_failed_tasks": list(stats.get("top_failed_tasks", []) or []),
    }


def _initial_targets(working_summary: Dict[str, Any], landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
    targets = list(_task_buildability_view(working_summary, landscape)["target_buckets"])
    targets.append({"target_id": "contract_review", "kind": "contract_review", "recommended_controls": {}})
    _validate_recommended_controls(targets)
    return targets


def _decision_targets(contract: Dict[str, Any], working_summary: Dict[str, Any], landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
    quality = (working_summary.get("quality_summary", {}) or {})
    feasibility = (working_summary.get("feasibility_summary", {}) or {})
    target_kinds = list((contract.get("target_policy", {}) or {}).get("preferred_target_kinds", []) or [])
    if not target_kinds:
        target_kinds = ["unassigned_priority", "energy_debt"]
    out: List[Dict[str, Any]] = []
    bucket_map = landscape.get("target_buckets", {}) or {}
    for kind in target_kinds:
        if kind == "unassigned_priority":
            bucket = dict(bucket_map.get(kind, {}) or {})
            if not bucket:
                bucket = {
                    "task_count": int(quality.get("unassigned_count", 0) or 0),
                    "priority_mass": float(quality.get("missed_priority", 0.0) or 0.0),
                    "task_ids": [],
                }
            if int(bucket.get("task_count", 0) or 0) == 0:
                continue
            out.append({
                "target_id": "T_unassigned_priority",
                "kind": kind,
                "task_ids": [int(value) for value in bucket.get("task_ids", [])],
                "task_count": int(bucket.get("task_count", 0)),
                "priority_mass": float(bucket.get("priority_mass", 0.0)),
                "metric_pressure": {
                    "missed_priority": float(quality.get("missed_priority", 0.0) or 0.0),
                    "unassigned_count": float(quality.get("unassigned_count", 0.0) or 0.0),
                },
                "recommended_controls": {
                    "insertion_control.task_signal_scores": ["priority_loss", "scarcity_pressure"],
                    "insertion_control.position_signal_scores": ["future_slack", "insert_cost"],
                    "destroy_control.signal_scores": ["mobility_opportunity", "scarcity_protection"],
                },
            })
        elif kind == "scarce_unassigned":
            bucket = dict(bucket_map.get(kind, {}) or {})
            if int(bucket.get("task_count", 0) or 0) == 0:
                continue
            out.append({
                "target_id": "T_scarce_unassigned",
                "kind": kind,
                "task_ids": [int(value) for value in bucket.get("task_ids", [])],
                "task_count": int(bucket.get("task_count", 0)),
                "priority_mass": float(bucket.get("priority_mass", 0.0)),
                "metric_pressure": {"count": int(bucket.get("task_count", 0) or 0)},
                "recommended_controls": {
                    "insertion_control.task_signal_scores": ["scarcity_pressure", "priority_loss"],
                    "insertion_control.position_signal_scores": ["future_slack"],
                    "destroy_control.signal_scores": ["scarcity_protection", "mobility_opportunity"],
                },
            })
        elif kind == "time_window_debt":
            out.append(_debt_target("T_time_window_debt", kind, "time_window", feasibility))
        elif kind == "route_balance":
            out.append({
                "target_id": "T_route_balance",
                "kind": kind,
                "metric_pressure": {"route_balance": float(quality.get("route_balance", 0.0) or 0.0)},
                "recommended_controls": {
                    "destroy_control.signal_scores": ["route_balance_pressure"],
                    "insertion_control.position_signal_scores": ["route_balance_gain"],
                },
            })
        else:
            out.append(_debt_target("T_energy_debt", "energy_debt", "energy", feasibility))
    out.append({"target_id": "contract_review", "kind": "contract_review", "recommended_controls": {}})
    _validate_recommended_controls(out)
    return out


def _debt_target(target_id: str, kind: str, debt_type: str, feasibility: Dict[str, Any]) -> Dict[str, Any]:
    ratios = feasibility.get("violation_ratio_by_type", {}) or {}
    return {
        "target_id": target_id,
        "kind": kind,
        "metric_pressure": {f"{debt_type}_ratio": float(ratios.get(debt_type, 0.0) or 0.0)},
        "recommended_controls": {
            "destroy_control.signal_scores": ["cost_pressure", "mobility_opportunity"],
            "insertion_control.position_signal_scores": (
                ["future_slack", "local_coupling_penalty"]
                if debt_type == "time_window" else ["insert_cost", "future_slack"]
            ),
            "acceptance_control.mode": ["threshold"],
        },
    }


def _validate_recommended_controls(targets: List[Dict[str, Any]]) -> None:
    for target in targets:
        controls = target.get("recommended_controls", {})
        if not isinstance(controls, dict):
            raise ValueError(f"{target.get('target_id')}.recommended_controls must be an object")
        for field_path, names in controls.items():
            if field_path not in FIELD_CANDIDATES:
                raise ValueError(f"unknown recommended control field: {field_path}")
            allowed = set(FIELD_CANDIDATES[field_path])
            for name in names:
                if name not in allowed:
                    raise ValueError(
                        f"{target.get('target_id')}.recommended_controls[{field_path}] "
                        f"contains invalid candidate {name}; allowed={sorted(allowed)}"
                    )


def _state_digest_from_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    quality = summary.get("quality_summary", {}) or {}
    feasibility = summary.get("feasibility_summary", {}) or {}
    ratios = dict(feasibility.get("violation_ratio_by_type", {}) or {})
    debt_total = float(feasibility.get("recoverable_violation_total", feasibility.get("violation_total", 0.0)) or 0.0)
    dominant = (
        ("none", 0.0)
        if debt_total <= 0.0
        else max(ratios.items(), key=lambda item: float(item[1]), default=("none", 0.0))
    )
    return {
        "is_feasible": bool(feasibility.get("is_feasible", summary.get("is_feasible", False))),
        "quality": {
            name: float(quality.get(name, 0.0) or 0.0)
            for name in ("missed_priority", "unassigned_count", "energy_total", "total_distance", "makespan", "route_balance")
            if name in quality
        },
        "debt": {
            "total": debt_total,
            "dominant_type": str(dominant[0]),
            "dominant_ratio": float(dominant[1]),
        },
    }


def _best_digest(best_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not best_summary:
        return {"exists": False, "quality": {}}
    return {
        "exists": True,
        "quality": _state_digest_from_summary(best_summary).get("quality", {}),
    }


def _compact_last_verification(verification: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not verification:
        return {"exists": False}
    trace = verification.get("trace", {}) or {}
    flow = trace.get("trial_flow", {}) or {}
    return {
        "exists": True,
        "verification_id": verification.get("verification_id"),
        "intent_status": verification.get("intent_status"),
        "dominant_blocker": verification.get("dominant_blocker"),
        "metric_delta": (verification.get("metric_delta", {}) or {}).get("working", {}),
        "debt_delta": verification.get("debt_delta", {}),
        "trace_counts": {
            "candidate_trials": int(flow.get("candidate_trials", 0) or 0),
            "feasibility_rejected": int(flow.get("feasibility_rejected", 0) or 0),
            "accepted": int(flow.get("accepted_trials", 0) or 0),
            "best_improved": int(flow.get("best_improved_trials", 0) or 0),
        },
    }


def _verification_summary(verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = Counter(str(item.get("intent_status", "")) for item in verifications)
    blockers = Counter(str(item.get("dominant_blocker", "")) for item in verifications)
    return {
        "verification_ids": [item.get("verification_id") for item in verifications],
        "intent_status_counts": dict(statuses),
        "dominant_blocker_counts": dict(blockers),
        "last": _compact_last_verification(verifications[-1] if verifications else None),
    }


def _action_space(candidates: PublicCandidates, *, initial: bool) -> Dict[str, Any]:
    base = {
        "allowed_actions": ["construct_initial", "request_supervisor_review"] if initial else ["run_alns", "request_supervisor_review"],
        "allowed_insertion_operators": list(candidates.names("insertion_operator_candidates")),
        "allowed_task_signals": list(candidates.names("insertion_task_signal_candidates")),
        "allowed_position_signals": list(candidates.names("insertion_position_signal_candidates")),
    }
    if not initial:
        base.update({
            "allowed_destroy_operators": list(candidates.names("destroy_operator_candidates")),
            "allowed_destroy_signals": list(candidates.names("destroy_signal_candidates")),
            "allowed_acceptance_modes": list(candidates.names("acceptance_candidates")),
        })
    return base


def _relaxation_reference(context: Dict[str, Any]) -> Dict[str, float]:
    if "time_window_median_width" in context or "agent_energy_median" in context:
        return {
            "time_window_median_width": float(context.get("time_window_median_width", 0.0) or 0.0),
            "agent_energy_median": float(context.get("agent_energy_median", 0.0) or 0.0),
        }
    return {
        "time_window_median_width": float((context.get("time_window", {}) or {}).get("median", 0.0) or 0.0),
        "agent_energy_median": float((context.get("energy", {}) or {}).get("median", 0.0) or 0.0),
    }


def _capable_count(agents: Sequence[Agent], task: Task) -> int:
    return sum(1 for agent in agents if set(task.skill_req).issubset(agent.skills))


def _risk_label(value: float) -> str:
    if value >= 0.30:
        return "high"
    if value >= 0.10:
        return "medium"
    return "low"


__all__ = [
    "build_supervisor_kickoff_observation",
    "build_supervisor_review_observation",
    "build_solver_observation",
    "next_contract_resource_limits",
]
