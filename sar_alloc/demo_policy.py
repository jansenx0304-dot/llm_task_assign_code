from __future__ import annotations

from typing import Any, Dict, Optional


def demo_supervisor_kickoff(observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    remaining = _remaining(observation)
    return {
        "supervisor_decision": {
            "action": "start_run",
            "global_objective": {
                "objective_layers": ["missed_priority", "unassigned_count", "energy_total"],
                "selection_basis": [
                    {"metric": "missed_priority", "data_refs": ["E1"], "reason": "Prioritize mission value coverage."},
                    {"metric": "unassigned_count", "data_refs": ["E1"], "reason": "Track task coverage after value loss."},
                    {"metric": "energy_total", "data_refs": ["E1"], "reason": "Reduce resource use after coverage."},
                ],
            },
            "next_contract": {
                "contract_type": "initial_construction",
                "stage_goal": {
                    "summary": "Build a coverage-oriented initial solution.",
                    "main_problem": "The run starts from empty routes.",
                    "search_intent": "Insert valuable and scarce tasks early.",
                },
                "stage_objective_layers": ["missed_priority", "unassigned_count", "energy_total"],
                "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
                "guidance": {
                    "instruction": "Construct a stable initial solution with high task coverage.",
                    "preferred_search_direction": "priority-and-scarcity-aware insertion",
                    "protect": "Preserve time and energy slack for later insertions.",
                    "success_signal": "Most high-priority tasks are assigned.",
                    "failure_signal": "Many scarce high-priority tasks remain unassigned.",
                },
                "completion_policy": {
                    "min_solver_actions": 1,
                    "max_solver_actions": 1,
                    "max_time_sec": _cap_time(remaining, 5.0),
                    "max_iters": _cap_iters(remaining, 1),
                    "success_rules": [{"event": "initial_solution_built", "count": 1, "scope": "total"}],
                    "failure_rules": [{"event": "initial_solution_failed", "count": 1, "scope": "total"}],
                },
            },
            "decision_basis": _basis("Start with coverage-oriented construction."),
        }
    }


def demo_supervisor_review(observation: Optional[Dict[str, Any]] = None, *, stop: bool = False) -> Dict[str, Any]:
    remaining = _remaining(observation)
    allowed_actions = _allowed_actions(observation, remaining)
    if stop or allowed_actions < 1 or int(float(remaining.get("iters", 0))) < 1:
        return {
            "supervisor_decision": {
                "action": "stop_run",
                "contract_review": _contract_review("The demo search is complete."),
                "stop_reason": "The demo search is complete.",
                "decision_basis": _basis("Return the best solution found."),
            }
        }
    actions = min(3, allowed_actions)
    actions = max(1, actions)
    return {
        "supervisor_decision": {
            "action": "issue_contract",
            "contract_review": _contract_review("Initial construction produced a working solution."),
            "next_contract": {
                "contract_type": "alns_search",
                "stage_goal": {
                    "summary": "Improve the coverage-oriented solution.",
                    "main_problem": "Some valuable tasks may remain unassigned or costly.",
                    "search_intent": "Locally rebuild routes around valuable and coupled tasks.",
                },
                "stage_objective_layers": ["missed_priority", "unassigned_count", "energy_total"],
                "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
                "guidance": {
                    "instruction": "Run focused ALNS actions to improve priority coverage.",
                    "preferred_search_direction": "related-cluster removal with scarcity-aware reinsertion",
                    "protect": "Preserve feasible route structure and useful slack.",
                    "success_signal": "Priority loss or unassigned count decreases.",
                    "failure_signal": "Repeated flat outcomes indicate this direction is exhausted.",
                },
                "completion_policy": {
                    "min_solver_actions": actions,
                    "max_solver_actions": actions,
                    "max_time_sec": _cap_time(remaining, 1.0),
                    "max_iters": _cap_iters(remaining, max(actions, 3)),
                    "success_rules": [{"event": "global_best_improved", "count": 1, "scope": "total"}],
                    "failure_rules": [{"event": "quality_flat", "count": actions, "scope": "consecutive"}],
                },
            },
            "decision_basis": _basis("Use a short multi-action ALNS contract."),
        }
    }


def demo_solver_decision(observation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    contract = (observation or {}).get("active_contract", {}) or {}
    if contract.get("contract_type") == "initial_construction":
        return {
            "solver_decision": {
                "action": "construct_initial",
                "reason": "Build the first working solution under the initial construction contract.",
                "insertion_control": _insertion_control(),
                "decision_basis": _basis("Use priority and scarcity aware construction."),
            }
        }
    return {
        "solver_decision": {
            "action": "run_alns",
            "reason": "Use a focused local rebuild under the active contract.",
            "destroy_control": {
                "operator_scores": [{"name": "related_cluster_removal", "score": 8, "reason": "Rebuild a coupled local region."}],
                "signal_scores": [{"name": "coupling_pressure", "score": 8, "reason": "Target tightly coupled tasks."}],
                "intensity_score": 5,
            },
            "insertion_control": _insertion_control(),
            "acceptance_control": {"mode": "threshold", "intensity_score": 4, "reason": "Allow limited exploration."},
            "decision_basis": _basis("Run one bounded ALNS action."),
        }
    }


def _insertion_control() -> Dict[str, Any]:
    return {
        "operator_scores": [
            {"name": "scarcity_first_insertion", "score": 8, "reason": "Insert scarce tasks early."},
            {"name": "regret_insertion", "score": 7, "reason": "Avoid losing future insertion opportunities."},
        ],
        "task_signal_scores": [
            {"name": "priority_loss", "score": 9, "reason": "Protect valuable tasks."},
            {"name": "scarcity_pressure", "score": 8, "reason": "Prioritize constrained tasks."},
        ],
        "position_signal_scores": [
            {"name": "insert_cost", "score": 8, "reason": "Control route growth."},
            {"name": "future_slack", "score": 7, "reason": "Preserve future flexibility."},
        ],
    }


def _basis(summary: str) -> Dict[str, Any]:
    return {"evidence_refs": ["E1"], "memory_refs": [], "summary": summary}


def _contract_review(summary: str) -> Dict[str, str]:
    return {
        "outcome_summary": summary,
        "main_lesson": "The next decision should use the completed contract result and remaining budget.",
        "next_intent": "Continue only when there is enough budget for another contract.",
    }


def _remaining(observation: Optional[Dict[str, Any]]) -> Dict[str, float]:
    raw = (observation or {}).get("remaining_global_budget", {}) or {}
    return {
        "solver_calls": float(raw.get("solver_calls", 1) or 0),
        "time_sec": float(raw.get("time_sec", 1.0) or 0.0),
        "iters": float(raw.get("iters", 1) or 0),
    }


def _allowed_actions(observation: Optional[Dict[str, Any]], remaining: Dict[str, float]) -> int:
    limits = (observation or {}).get("next_contract_resource_limits", {}) or {}
    if "max_solver_actions_allowed" in limits:
        return max(0, int(float(limits.get("max_solver_actions_allowed", 0) or 0)))
    return max(
        0,
        min(
            int(float(remaining.get("solver_calls", 0) or 0)),
            int(float((observation or {}).get("remaining_global_budget", {}).get("step_calls", remaining.get("solver_calls", 0)) or 0)),
        ),
    )


def _cap_time(remaining: Dict[str, float], desired: float) -> float:
    available = max(1e-6, float(remaining.get("time_sec", desired)))
    return max(1e-6, min(float(desired), available))


def _cap_iters(remaining: Dict[str, float], desired: int) -> int:
    available = max(1, int(float(remaining.get("iters", desired))))
    return max(1, min(int(desired), available))


__all__ = ["demo_supervisor_kickoff", "demo_supervisor_review", "demo_solver_decision"]
