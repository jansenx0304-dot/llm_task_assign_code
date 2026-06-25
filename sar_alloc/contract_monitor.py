from __future__ import annotations

import operator
from typing import Any, Dict, List, Optional

from .schemas import SUPPORTED_CONDITION_SOURCES
from .tools.llm_utils import ContractProgress, SearchContract

OPS = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}


def update_contract_progress(
    progress: ContractProgress, verification: Dict[str, Any]
) -> ContractProgress:
    progress.solver_actions += 1
    vid = str(verification.get("verification_id", ""))
    if vid:
        progress.verification_ids.append(vid)
    status = str(verification.get("contract_objective_status", ""))
    blocker = str(verification.get("dominant_blocker", "none"))
    progress.contract_objective_status_counts[status] = (
        progress.contract_objective_status_counts.get(status, 0) + 1
    )
    progress.dominant_blocker_counts[blocker] = (
        progress.dominant_blocker_counts.get(blocker, 0) + 1
    )
    progress.recent_contract_objective_statuses.append(status)
    progress.recent_blockers.append(blocker)
    progress.recent_contract_objective_statuses[:] = progress.recent_contract_objective_statuses[-5:]
    progress.recent_blockers[:] = progress.recent_blockers[-5:]
    trace = verification.get("trace", {}) or {}
    progress.iters_used += int(trace.get("iters", 0) or 0)
    return progress


def check_contract_completion(
    contract: SearchContract,
    progress: ContractProgress,
    recent_verifications: Optional[List[Dict[str, Any]]] = None,
    solution_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply the fixed review -> success -> failure -> resource priority."""
    policy = contract.resource_policy
    verifications = list(recent_verifications or [])
    last = verifications[-1] if verifications else {}
    if str(last.get("action", "")) == "request_supervisor_review":
        review_reasons = list((last.get("trace", {}) or {}).get("review_reasons", []) or [])
        reason = (
            "no_executable_action"
            if "no_executable_action" in review_reasons
            else "solver_requested_review"
        )
        return _completion(
            reason,
            reason,
            progress.condition_report,
        )

    condition_report: List[Dict[str, Any]] = []
    if progress.solver_actions >= int(policy["min_actions"]):
        success_report = _evaluate_conditions(
            contract.exit_conditions.get("success", []),
            progress,
            verifications,
            solution_state or {},
        )
        failure_report = _evaluate_conditions(
            contract.exit_conditions.get("failure", []),
            progress,
            verifications,
            solution_state or {},
        )
        condition_report = success_report + failure_report
        progress.condition_report = condition_report
        for item in success_report:
            if item["passed"]:
                return _completion(
                    "success",
                    f"success_condition_passed:{item['condition_id']}",
                    condition_report,
                )
        for item in failure_report:
            if item["passed"]:
                return _completion(
                    "failure",
                    f"failure_condition_passed:{item['condition_id']}",
                    condition_report,
                )
    else:
        progress.condition_report = []

    if progress.solver_actions >= int(policy["max_actions"]):
        return _completion(
            "resource_exhausted", "max_actions_reached", condition_report
        )
    if progress.time_used_sec >= float(policy["max_time_sec"]):
        return _completion("resource_exhausted", "max_time_reached", condition_report)
    if progress.iters_used >= int(policy["max_iters"]):
        return _completion("resource_exhausted", "max_iters_reached", condition_report)
    reason = (
        "min_actions_not_reached"
        if progress.solver_actions < int(policy["min_actions"])
        else "conditions_not_met"
    )
    return _completion("continue", reason, condition_report)


def resolve_condition_source(
    source: str,
    progress: ContractProgress,
    solution_state: Dict[str, Any],
    last_verification: Optional[Dict[str, Any]] = None,
) -> Any:
    if source not in SUPPORTED_CONDITION_SOURCES:
        raise ValueError(f"unsupported condition source: {source}")
    last = dict(last_verification or {})
    if source == "progress.solver_actions":
        return progress.solver_actions
    if source == "progress.iters_used":
        return progress.iters_used
    if source == "progress.time_used_sec":
        return progress.time_used_sec
    if source == "last.contract_objective_status":
        return _required_value(last, "contract_objective_status", source)
    if source == "last.dominant_blocker":
        return _required_value(last, "dominant_blocker", source)
    if source == "last.improvement_flags.run_global_best_improved":
        flags = dict(last.get("improvement_flags", {}) or {})
        return bool(_required_value(flags, "run_global_best_improved", source))
    if source.startswith("aggregate."):
        name = source.split(".", 1)[1]
        if name == "solver_requested_review":
            return progress.dominant_blocker_counts.get("solver_requested_review", 0)
        return progress.contract_objective_status_counts.get(name, 0)
    if source == "best_feasible.exists":
        return bool(solution_state.get("best_feasible"))
    scope, metric = source.split(".", 1)
    summary = solution_state.get(scope)
    if not summary:
        raise RuntimeError(f"condition source {source} has no {scope} solution")
    if metric == "is_feasible":
        feasibility = summary.get("feasibility_summary", {}) or {}
        return bool(feasibility.get("is_feasible", summary.get("is_feasible", False)))
    quality = summary.get("quality_summary", {}) or {}
    if metric not in quality:
        raise RuntimeError(
            f"condition source {source} is missing from solution summary"
        )
    return float(quality[metric])


def _evaluate_conditions(
    conditions: List[Dict[str, Any]],
    progress: ContractProgress,
    verifications: List[Dict[str, Any]],
    solution_state: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        _evaluate_condition(item, progress, verifications, solution_state)
        for item in conditions
    ]


def _evaluate_condition(
    condition: Dict[str, Any],
    progress: ContractProgress,
    verifications: List[Dict[str, Any]],
    solution_state: Dict[str, Any],
) -> Dict[str, Any]:
    source = str(condition["source"])
    op = str(condition["op"])
    expected = condition["value"]
    window = int(condition.get("window", 1) or 1)
    recent = verifications[-window:]
    last = recent[-1] if recent else None
    if source.startswith("aggregate."):
        name = source.split(".", 1)[1]
        if name == "solver_requested_review":
            actual = sum(
                str(item.get("dominant_blocker", "")) == "solver_requested_review"
                for item in recent
            )
        else:
            actual = sum(
                str(item.get("contract_objective_status", "")) == name
                for item in recent
            )
    else:
        actual = resolve_condition_source(source, progress, solution_state, last)
    try:
        passed = bool(OPS[op](actual, expected))
    except TypeError:
        passed = bool(OPS[op](str(actual), str(expected)))
    return {
        "condition_id": str(condition["condition_id"]),
        "source": source,
        "actual": actual,
        "op": op,
        "expected": expected,
        "window": window,
        "passed": passed,
    }


def _required_value(mapping: Dict[str, Any], key: str, source: str) -> Any:
    if key not in mapping or mapping[key] is None:
        raise RuntimeError(f"condition source {source} cannot be resolved")
    return mapping[key]


def _completion(
    status: str, reason: str, condition_report: List[Dict[str, Any]]
) -> Dict[str, Any]:
    return {
        "completion_status": status,
        "completion_reason": reason,
        "condition_report": list(condition_report),
        "completed": status != "continue",
    }


__all__ = [
    "update_contract_progress",
    "check_contract_completion",
    "resolve_condition_source",
]
