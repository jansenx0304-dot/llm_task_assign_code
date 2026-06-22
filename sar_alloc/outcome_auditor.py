from __future__ import annotations

from typing import Any, Dict, List, Optional

from .evaluator import compare_quality
from .solution import EvalResult


OUTCOME_EVENTS = (
    "initial_solution_built",
    "initial_solution_failed",
    "quality_improved",
    "quality_flat",
    "quality_worsened",
    "global_best_improved",
    "no_admissible_candidate",
    "feasibility_recovered",
    "recovery_debt_reduced",
)


def audit_initial_result(*, initial_eval: Optional[EvalResult]) -> Dict[str, Any]:
    if initial_eval is None:
        return {
            "action": "construct_initial",
            "initial_quality": {"is_feasible": False, "quality_metrics": {}},
            "events": ["initial_solution_failed"],
        }
    return {
        "action": "construct_initial",
        "initial_quality": {
            "is_feasible": bool(initial_eval.is_feasible),
            "quality_metrics": dict(initial_eval.quality_metrics),
        },
        "events": ["initial_solution_built"],
    }


def audit_outcome(
    *,
    before_working_eval: EvalResult,
    after_working_eval: EvalResult,
    before_best_eval: Optional[EvalResult],
    after_best_eval: Optional[EvalResult],
    contract_objective_layers: List[Dict[str, Any]],
    global_objective_layers: List[Dict[str, Any]],
    solver_diagnostics: Dict[str, Any],
    solver_events: List[str],
) -> Dict[str, Any]:
    comparison = compare_quality(after_working_eval, before_working_eval, contract_objective_layers)
    status = "improved" if comparison < 0 else "worsened" if comparison > 0 else "flat"
    events = [f"quality_{status}"]
    global_improved = bool(
        after_best_eval is not None
        and (before_best_eval is None or compare_quality(after_best_eval, before_best_eval, global_objective_layers) < 0)
    )
    if global_improved:
        events.append("global_best_improved")
    if "no_admissible_candidate" in solver_events:
        events.append("no_admissible_candidate")
    if not before_working_eval.is_feasible and after_working_eval.is_feasible:
        events.append("feasibility_recovered")
    if bool(solver_diagnostics.get("recovery_debt_reduced", False)):
        events.append("recovery_debt_reduced")
    events = [event for event in OUTCOME_EVENTS if event in events]
    return {
        "action": "run_alns",
        "contract_quality_change": {
            "status": status,
            "before": _metrics(before_working_eval, contract_objective_layers),
            "after": _metrics(after_working_eval, contract_objective_layers),
        },
        "global_best_change": {"improved": global_improved},
        "solver_stats": {
            "iterations": int(solver_diagnostics.get("total_iters", 0) or 0),
            "accepted_trials": int(solver_diagnostics.get("accepted_trial_count", 0) or 0),
            "rejected_trials": int(solver_diagnostics.get("rejected_trial_count", 0) or 0),
            "best_changed": global_improved,
            "violation_ratios": dict(solver_diagnostics.get("violation_ratios", {}) or {}),
            "feasibility_rejection_reasons": dict(
                solver_diagnostics.get("feasibility_rejection_reasons", {}) or {}
            ),
        },
        "events": events,
    }


def _metrics(evaluation: EvalResult, layers: List[Dict[str, Any]]) -> Dict[str, float]:
    return {str(layer["metric"]): float(evaluation.get_metric(str(layer["metric"]))) for layer in layers}


__all__ = ["OUTCOME_EVENTS", "audit_initial_result", "audit_outcome"]
