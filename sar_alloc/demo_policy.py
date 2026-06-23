from __future__ import annotations

from typing import Any, Dict, Optional


def demo_supervisor_kickoff(observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    remaining = _remaining(observation)
    return {
        "supervisor_decision": {
            "action": "start_run",
            "global_objective": {
                "objective_layers": ["missed_priority", "unassigned_count", "energy_total"],
                "explanation": {"summary": "Prioritize coverage, then energy."},
            },
            "next_contract": _contract(
                "initial_construction",
                remaining,
                min_actions=1,
                max_actions=1,
                max_iters=1,
                max_time_sec=5.0,
                success=[{"condition_id": "S_initial", "source": "last.intent_status", "op": "==", "value": "achieved", "window": 1}],
                failure=[{"condition_id": "F_initial", "source": "last.intent_status", "op": "==", "value": "not_achieved", "window": 1}],
                explanation="Build a coverage-oriented initial solution.",
            ),
        }
    }


def demo_supervisor_review(observation: Optional[Dict[str, Any]] = None, *, stop: bool = False) -> Dict[str, Any]:
    remaining = _remaining(observation)
    allowed_actions = _allowed_actions(observation, remaining)
    if stop or allowed_actions < 1 or int(float(remaining.get("iters", 0))) < 1:
        return {
            "supervisor_decision": {
                "action": "stop_run",
                "contract_review": _contract_review("The search is complete."),
                "stop_explanation": "The search is complete.",
            }
        }
    actions = max(1, min(3, allowed_actions))
    return {
        "supervisor_decision": {
            "action": "issue_contract",
            "contract_review": _contract_review("The previous contract produced verified feedback."),
            "next_contract": _contract(
                "alns_search",
                remaining,
                min_actions=actions,
                max_actions=actions,
                max_iters=max(actions, 3),
                max_time_sec=1.0,
                success=[{"condition_id": "S_best", "source": "last.best_improved", "op": "==", "value": True, "window": 1}],
                failure=[{"condition_id": "F_no_gain", "source": "aggregate.not_achieved", "op": ">=", "value": actions, "window": actions}],
                explanation="Run a short ALNS contract using verified feedback.",
            ),
        }
    }


def demo_solver_decision(observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    action_space = (observation or {}).get("action_space", {}) or {}
    allowed_actions = [str(value) for value in action_space.get("allowed_actions", [])]
    if allowed_actions == ["request_supervisor_review"]:
        return {
            "solver_decision": {
                "action": "request_supervisor_review",
                "target_id": _review_target(observation),
                "explanation": {"reason_summary": "No executable search action is available."},
            }
        }
    contract = (observation or {}).get("contract_view", {}) or (observation or {}).get("active_contract", {}) or {}
    if contract.get("contract_type") == "initial_construction":
        return {
            "solver_decision": {
                "action": "construct_initial",
                "target_id": _first_target(observation, "T_unassigned_priority"),
                "insertion_control": _insertion_control(action_space),
                "explanation": {"reason_summary": "Use priority and scarcity aware construction."},
            }
        }
    return {
        "solver_decision": {
            "action": "run_alns",
            "target_id": _first_target(observation, "T_unassigned_priority"),
            "destroy_control": {
                "operator_scores": _preferred_scores(
                    action_space, "allowed_destroy_operators", ["related_cluster_removal"], 8
                ),
                "signal_scores": _preferred_scores(
                    action_space, "allowed_destroy_signals", ["coupling_pressure"], 8
                ),
                "intensity_score": 5,
            },
            "insertion_control": _insertion_control(action_space),
            "acceptance_control": {
                "mode": _preferred_name(action_space, "allowed_acceptance_modes", "threshold"),
                "intensity_score": 4,
            },
            "explanation": {"reason_summary": "Run one bounded local rebuild."},
        }
    }


def _contract(
    contract_type: str,
    remaining: Dict[str, float],
    *,
    min_actions: int,
    max_actions: int,
    max_iters: int,
    max_time_sec: float,
    success: list[Dict[str, Any]],
    failure: list[Dict[str, Any]],
    explanation: str,
) -> Dict[str, Any]:
    return {
        "contract_type": contract_type,
        "objective_layers": ["missed_priority", "unassigned_count", "energy_total"],
        "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
        "target_policy": {"preferred_target_kinds": ["unassigned_priority", "energy_debt"]},
        "protected_metrics": [{"metric": "unassigned_count", "max_worsen": 0}],
        "resource_policy": {
            "min_actions": min_actions,
            "max_actions": max_actions,
            "max_time_sec": _cap_time(remaining, max_time_sec),
            "max_iters": _cap_iters(remaining, max_iters),
        },
        "exit_conditions": {"success": success, "failure": failure},
        "explanation": {"stage_summary": explanation},
    }


def _insertion_control(action_space: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operator_scores": _preferred_scores(
            action_space, "allowed_insertion_operators",
            ["scarcity_first_insertion", "regret_insertion"], 8,
        ),
        "task_signal_scores": _preferred_scores(
            action_space, "allowed_task_signals", ["priority_loss", "scarcity_pressure"], 9,
        ),
        "position_signal_scores": _preferred_scores(
            action_space, "allowed_position_signals", ["insert_cost", "future_slack"], 8,
        ),
    }


def _preferred_scores(
    action_space: Dict[str, Any], key: str, preferred: list[str], score: int
) -> list[Dict[str, Any]]:
    allowed = [str(value) for value in action_space.get(key, [])]
    selected = [name for name in preferred if name in allowed]
    if not selected and allowed:
        selected = allowed[:1]
    return [{"name": name, "score": max(0, int(score) - index)} for index, name in enumerate(selected[:3])]


def _preferred_name(action_space: Dict[str, Any], key: str, preferred: str) -> str:
    allowed = [str(value) for value in action_space.get(key, [])]
    if preferred in allowed:
        return preferred
    if allowed:
        return allowed[0]
    raise ValueError(f"demo policy requires at least one candidate in action_space.{key}")


def _contract_review(summary: str) -> Dict[str, str]:
    return {
        "outcome_summary": summary,
        "main_lesson": "The next decision should use condition_report and verified outcomes.",
    }


def _remaining(observation: Optional[Dict[str, Any]]) -> Dict[str, float]:
    obs = observation or {}
    raw = obs.get("remaining_global_budget", {}) or {}
    caps = obs.get("budget_caps", {}) or {}
    return {
        "solver_calls": float(raw.get("solver_calls", caps.get("max_solver_actions", 1)) or 0),
        "step_calls": float(raw.get("step_calls", caps.get("max_solver_actions", 1)) or 0),
        "time_sec": float(raw.get("time_sec", caps.get("max_time_sec", 1.0)) or 0.0),
        "iters": float(raw.get("iters", caps.get("max_iters", 1)) or 0),
    }


def _allowed_actions(observation: Optional[Dict[str, Any]], remaining: Dict[str, float]) -> int:
    limits = (observation or {}).get("next_contract_resource_limits", {}) or {}
    if "max_solver_actions_allowed" in limits:
        return max(0, int(float(limits.get("max_solver_actions_allowed", 0) or 0)))
    return max(0, min(int(float(remaining.get("solver_calls", 0) or 0)), int(float(remaining.get("step_calls", 0) or 0))))


def _first_target(observation: Optional[Dict[str, Any]], fallback: str) -> str:
    for item in (observation or {}).get("decision_targets", []) or []:
        if isinstance(item, dict) and item.get("kind") != "contract_review":
            return str(item.get("target_id", fallback))
    return fallback


def _review_target(observation: Optional[Dict[str, Any]]) -> str:
    for item in (observation or {}).get("decision_targets", []) or []:
        if isinstance(item, dict) and item.get("kind") == "contract_review":
            return str(item.get("target_id", "contract_review"))
    return "contract_review"


def _cap_time(remaining: Dict[str, float], desired: float) -> float:
    available = max(1e-6, float(remaining.get("time_sec", desired)))
    return max(1e-6, min(float(desired), available))


def _cap_iters(remaining: Dict[str, float], desired: int) -> int:
    available = max(1, int(float(remaining.get("iters", desired))))
    return max(1, min(int(desired), available))


__all__ = ["demo_supervisor_kickoff", "demo_supervisor_review", "demo_solver_decision"]
