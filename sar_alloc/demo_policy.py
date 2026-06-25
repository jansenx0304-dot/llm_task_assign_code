from __future__ import annotations

from typing import Any, Dict, Optional


def demo_supervisor_kickoff(
    observation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    remaining = _remaining(observation)
    return {
        "supervisor_decision": {
            "action": "start_run",
            "global_objective": {
                "objective_layers": [
                    "missed_priority",
                    "unassigned_count",
                    "energy_total",
                ],
                "explanation": {"summary": "Prioritize coverage, then energy."},
            },
            "next_contract": _contract(
                "initial_construction",
                remaining,
                min_actions=1,
                max_actions=1,
                max_iters=1,
                max_time_sec=5.0,
                success=[
                    {
                        "condition_id": "S_initial",
                        "source": "last.contract_objective_status",
                        "op": "==",
                        "value": "achieved",
                        "window": 1,
                    }
                ],
                failure=[
                    {
                        "condition_id": "F_initial",
                        "source": "last.contract_objective_status",
                        "op": "==",
                        "value": "not_achieved",
                        "window": 1,
                    }
                ],
                explanation="Build a coverage-oriented initial solution.",
            ),
        }
    }


def demo_supervisor_review(
    observation: Optional[Dict[str, Any]] = None, *, stop: bool = False
) -> Dict[str, Any]:
    remaining = _remaining(observation)
    allowed_actions = _allowed_actions(observation, remaining)
    if (
        stop
        or allowed_actions < 1
        or int(float(remaining.get("iters", 0))) < 1
        or float(remaining.get("time_sec", 0.0)) <= 0.0
    ):
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
            "contract_review": _contract_review(
                "The previous contract produced verified feedback."
            ),
            "next_contract": _contract(
                "alns_search",
                remaining,
                min_actions=actions,
                max_actions=actions,
                max_iters=max(actions, 3),
                max_time_sec=1.0,
                success=[
                    {
                        "condition_id": "S_best",
                        "source": "last.improvement_flags.run_global_best_improved",
                        "op": "==",
                        "value": True,
                        "window": 1,
                    }
                ],
                failure=[
                    {
                        "condition_id": "F_no_gain",
                        "source": "aggregate.not_achieved",
                        "op": ">=",
                        "value": actions,
                        "window": actions,
                    }
                ],
                explanation="Run a short ALNS contract using verified feedback.",
            ),
        }
    }


def demo_solver_decision(
    observation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    action_space = (observation or {}).get("execution_state", {}) or {}
    catalog = (observation or {}).get("control_catalog", {}) or {}
    allowed_actions = [
        str(value) for value in action_space.get("hard_executable_actions", [])
    ]
    if allowed_actions == ["request_supervisor_review"]:
        return {
            "solver_decision": {
                "action": "request_supervisor_review",
                "situation_assessment": _assessment("Request supervisor review."),
                "review_request": {
                    "reason": "No useful executable search action is available under the current contract.",
                    "evidence_refs": ["execution_state", "last_verification"],
                },
                "explanation": {
                    "reason_summary": "No executable search action is available."
                },
            }
        }
    contract = (
        (observation or {}).get("active_contract", {})
        or {}
    )
    if contract.get("contract_type") == "initial_construction":
        return {
            "solver_decision": {
                "action": "construct_initial",
                "situation_assessment": _assessment(
                    "Construct an initial solution using the selected contract intent."
                ),
                "intent_id": _first_intent(observation),
                "insertion_control": _insertion_control(catalog),
                "solver_budget": _solver_budget(observation),
                "expected_effects": [
                    {"metric": "missed_priority", "direction": "decrease"},
                    {"metric": "unassigned_count", "direction": "decrease"},
                ],
                "explanation": {
                    "reason_summary": "Use priority and scarcity aware construction."
                },
            }
        }
    return {
        "solver_decision": {
            "action": "run_alns",
            "situation_assessment": _assessment(
                "Run ALNS with explicit controls selected by the solver decision."
            ),
            "intent_id": _first_intent(observation),
            "destroy_control": {
                "operator_scores": _preferred_scores(
                    catalog,
                    "destroy_operators",
                    ["related_cluster_removal"],
                    8,
                ),
                "signal_scores": _preferred_scores(
                    catalog, "destroy_signals", ["coupling_pressure"], 8
                ),
                "intensity_score": 5,
            },
            "insertion_control": _insertion_control(catalog),
            "acceptance_control": {
                "mode": _preferred_name(
                    catalog, "acceptance_modes", "threshold"
                ),
                "intensity_score": 4,
            },
            "solver_budget": _solver_budget(observation),
            "expected_effects": [
                {"metric": "missed_priority", "direction": "decrease"},
                {"metric": "energy_total", "direction": "decrease"},
            ],
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
        "situation_assessment": _assessment(explanation),
        "target_intents": [
            {
                "intent_id": (
                    "construct_coverage"
                    if contract_type == "initial_construction"
                    else "search_coverage_energy"
                ),
                "intent_type": (
                    "construction"
                    if contract_type == "initial_construction"
                    else "improvement"
                ),
                "evidence_refs": [
                    "candidate_landscape.insertion_evidence",
                    "solution_evidence.working.quality",
                ],
                "expected_effects": [
                    {"metric": "missed_priority", "direction": "decrease"},
                    {"metric": "unassigned_count", "direction": "decrease"},
                    {"metric": "energy_total", "direction": "decrease"},
                ],
                "rationale": explanation,
            }
        ],
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
            action_space,
            "insertion_operators",
            ["scarcity_first_insertion", "regret_insertion"],
            8,
        ),
        "task_signal_scores": _preferred_scores(
            action_space,
            "insertion_task_signals",
            ["priority_loss", "scarcity_pressure"],
            9,
        ),
        "position_signal_scores": _preferred_scores(
            action_space,
            "insertion_position_signals",
            ["insert_cost", "future_slack"],
            8,
        ),
    }


def _preferred_scores(
    action_space: Dict[str, Any], key: str, preferred: list[str], score: int
) -> list[Dict[str, Any]]:
    allowed = [
        str(value.get("name")) if isinstance(value, dict) else str(value)
        for value in action_space.get(key, [])
    ]
    selected = [name for name in preferred if name in allowed]
    if not selected and allowed:
        selected = allowed[:1]
    return [
        {"name": name, "score": max(0, int(score) - index)}
        for index, name in enumerate(selected[:3])
    ]


def _preferred_name(action_space: Dict[str, Any], key: str, preferred: str) -> str:
    allowed = [
        str(value.get("name")) if isinstance(value, dict) else str(value)
        for value in action_space.get(key, [])
    ]
    if preferred in allowed:
        return preferred
    if allowed:
        return allowed[0]
    raise ValueError(
        f"demo policy requires at least one candidate in action_space.{key}"
    )


def _contract_review(summary: str) -> Dict[str, str]:
    return {
        "outcome_summary": summary,
        "main_lesson": "The next decision should use condition_report and verified outcomes.",
    }


def _remaining(observation: Optional[Dict[str, Any]]) -> Dict[str, float]:
    obs = observation or {}
    raw = (obs.get("run_context", {}) or {}).get(
        "remaining_global_resources", {}
    ) or {}
    limits = (obs.get("action_space", {}) or {}).get(
        "next_contract_resource_limits", {}
    ) or {}
    return {
        "solver_calls": float(
            raw.get(
                "solver_calls", limits.get("max_solver_actions_allowed", 1)
            )
            or 0
        ),
        "step_calls": float(
            raw.get("step_calls", limits.get("max_solver_actions_allowed", 1))
            or 0
        ),
        "time_sec": float(
            raw.get("time_sec", limits.get("max_time_sec_allowed", 1.0)) or 0.0
        ),
        "iters": float(
            raw.get("iters", limits.get("max_iters_allowed", 1)) or 0
        ),
    }


def _allowed_actions(
    observation: Optional[Dict[str, Any]], remaining: Dict[str, float]
) -> int:
    limits = ((observation or {}).get("action_space", {}) or {}).get(
        "next_contract_resource_limits", {}
    ) or {}
    if "max_solver_actions_allowed" in limits:
        return max(0, int(float(limits.get("max_solver_actions_allowed", 0) or 0)))
    return max(
        0,
        min(
            int(float(remaining.get("solver_calls", 0) or 0)),
            int(float(remaining.get("step_calls", 0) or 0)),
        ),
    )


def _first_intent(observation: Optional[Dict[str, Any]]) -> str:
    for item in ((observation or {}).get("active_contract", {}) or {}).get(
        "target_intents", []
    ):
        if isinstance(item, dict) and item.get("intent_id"):
            return str(item["intent_id"])
    return "construct_coverage"


def _solver_budget(observation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    remaining = (
        ((observation or {}).get("execution_state", {}) or {}).get(
            "remaining_contract_resources", {}
        )
        or {}
    )
    return {
        "max_iters": max(1, min(1, int(float(remaining.get("iters", 1) or 1)))),
        "max_time_sec": max(
            1e-6, min(1.0, float(remaining.get("time_sec", 1.0) or 1.0))
        ),
    }


def _assessment(summary: str) -> Dict[str, str]:
    return {
        "summary": summary,
        "reasoning_from_evidence": "Demo mode uses deterministic evidence references for a mock LLM decision.",
    }


def _cap_time(remaining: Dict[str, float], desired: float) -> float:
    available = max(1e-6, float(remaining.get("time_sec", desired)))
    return max(1e-6, min(float(desired), available))


def _cap_iters(remaining: Dict[str, float], desired: int) -> int:
    available = max(1, int(float(remaining.get("iters", desired))))
    return max(1, min(int(desired), available))


__all__ = ["demo_supervisor_kickoff", "demo_supervisor_review", "demo_solver_decision"]
