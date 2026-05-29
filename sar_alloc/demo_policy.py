from __future__ import annotations

"""Demo LLM policies used only by dummy mode and explicit fallback.

These values are not imported by the real LLM path unless the caller has
explicitly enabled `allow_llm_fallback`. They exist so command-line smoke tests
can exercise the orchestration and ALNS plumbing without a network call.
"""

from typing import Any, Dict, Optional


def demo_objective_plan() -> Dict[str, Any]:
    return {
        "rationale": "Demo objective for local CLI smoke tests.",
        "layers": [
            {"name": "hard_feasibility", "metric": "violation_total", "direction": "min"},
            {"name": "rescue_priority", "metric": "missed_priority", "direction": "min"},
            {"name": "energy_use", "metric": "energy_total", "direction": "min"},
        ],
    }


def demo_build_initial_action() -> Dict[str, Any]:
    return {
        "rationale": "Build a deterministic initial incumbent before ALNS.",
        "operator_intent": {
            "remove": "not used during construction",
            "reinsert": "high priority feasible tasks",
            "insert": "low violation insertion positions",
        },
        "action_type": "build_initial_solution",
        "action_payload": {},
        "budget_request": {},
    }


def demo_run_alns_action(
    *,
    time_limit_sec: float = 1.0,
    max_iters: Optional[int] = 60,
) -> Dict[str, Any]:
    budget_request: Dict[str, Any] = {"time_limit_sec": float(time_limit_sec)}
    if max_iters is not None:
        budget_request["max_iters"] = int(max_iters)

    return {
        "rationale": "Run demo weighted ALNS with balanced repair pressure.",
        "operator_intent": {
            "remove": "risky assigned tasks",
            "reinsert": "high priority unassigned tasks",
            "insert": "feasible low detour positions",
        },
        "action_type": "run_alns",
        "action_payload": {
            "search_diagnosis_scores": {
                "cost_descent": 8,
                "scarcity_protection": 7,
                "structure_rebuild": 6,
                "route_rebalance": 5,
                "diversified_escape": 3,
            },
            "destroy_operator_scores": {
                "random_removal": 2,
                "worst_task_removal": 8,
                "related_cluster_removal": 7,
                "critical_block_removal": 6,
                "route_rebalance_removal": 5,
            },
            "repair_operator_scores": {
                "feasible_greedy_repair": 4,
                "scarcity_first_repair": 8,
                "regret_k_repair": 8,
                "bottleneck_targeted_repair": 6,
                "diversified_random_repair": 3,
            },
            "destroy_metric_preferences": {
                "cost_pressure": {"score": 9, "direction": "prefer_high"},
                "scarcity_pressure": {"score": 7, "direction": "avoid_high"},
                "coupling_pressure": {"score": 8, "direction": "prefer_high"},
                "mobility_opportunity": {"score": 6, "direction": "prefer_high"},
                "balance_pressure": {"score": 5, "direction": "prefer_high"},
            },
            "repair_task_metric_preferences": {
                "cost_pressure": {"score": 5, "direction": "prefer_high"},
                "scarcity_pressure": {"score": 9, "direction": "prefer_high"},
                "coupling_pressure": {"score": 7, "direction": "prefer_high"},
                "mobility_opportunity": {"score": 4, "direction": "prefer_low"},
                "balance_pressure": {"score": 6, "direction": "prefer_high"},
            },
            "repair_position_metric_preferences": {
                "insert_cost": {"score": 9, "direction": "prefer_low"},
                "future_slack": {"score": 8, "direction": "prefer_high"},
                "route_balance_gain": {"score": 6, "direction": "prefer_high"},
                "local_coupling_penalty": {"score": 5, "direction": "prefer_low"},
                "diversity_gain": {"score": 3, "direction": "prefer_high"},
            },
            "destroy_strength_score": 6,
            "candidate_budget_score": 7,
            "exploration_score": 3,
            "acceptance": "sa",
            "accept_level": 0.25,
            "reaction_factor": 0.20,
            "prior_mix_lambda": 0.25,
        },
        "budget_request": budget_request,
    }


def demo_stop_action() -> Dict[str, Any]:
    return {
        "rationale": "Stop after the demo construction and ALNS step.",
        "operator_intent": {
            "remove": "not needed",
            "reinsert": "not needed",
            "insert": "not needed",
        },
        "action_type": "stop",
        "action_payload": {},
        "budget_request": {},
    }
