from __future__ import annotations

import operator
from typing import Any, Dict, List, Optional

from .tools.llm_utils import ContractProgress, SearchContract


OPS = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}


def update_contract_progress(progress: ContractProgress, verification: Dict[str, Any]) -> ContractProgress:
    progress.solver_actions += 1
    vid = str(verification.get("verification_id", ""))
    if vid:
        progress.verification_ids.append(vid)
    status = str(verification.get("intent_status", ""))
    blocker = str(verification.get("dominant_blocker", "none"))
    progress.intent_status_counts[status] = progress.intent_status_counts.get(status, 0) + 1
    progress.dominant_blocker_counts[blocker] = progress.dominant_blocker_counts.get(blocker, 0) + 1
    for metric, value in (verification.get("metric_delta", {}) or {}).get("working", {}).items():
        progress.metric_delta_total[str(metric)] = progress.metric_delta_total.get(str(metric), 0.0) + float(value)
    trace = verification.get("trace", {}) or {}
    progress.iters_used += int(trace.get("iters", 0) or 0)
    return progress


def check_contract_completion(
    contract: SearchContract,
    progress: ContractProgress,
    recent_verifications: Optional[List[Dict[str, Any]]] = None,
    budget_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    del budget_state
    policy = contract.resource_policy
    verifications = list(recent_verifications or [])
    if progress.solver_actions >= int(policy["max_actions"]):
        return _completion("resource_exhausted", "max_actions_reached", progress.condition_report)
    if progress.time_used_sec >= float(policy["max_time_sec"]):
        return _completion("resource_exhausted", "max_time_reached", progress.condition_report)
    if progress.iters_used >= int(policy["max_iters"]):
        return _completion("resource_exhausted", "max_iters_reached", progress.condition_report)
    if verifications and str(verifications[-1].get("action", "")) == "request_supervisor_review":
        return _completion("solver_requested_review", "solver_requested_review", progress.condition_report)
    if progress.solver_actions < int(policy["min_actions"]):
        progress.condition_report = []
        return _completion("continue", "min_actions_not_reached", [])

    success_report = _evaluate_conditions(contract.exit_conditions.get("success", []), progress, verifications)
    failure_report = _evaluate_conditions(contract.exit_conditions.get("failure", []), progress, verifications)
    condition_report = success_report + failure_report
    progress.condition_report = condition_report
    for item in success_report:
        if item["passed"]:
            return _completion("success", f"success_condition_passed:{item['condition_id']}", condition_report)
    for item in failure_report:
        if item["passed"]:
            return _completion("failure", f"failure_condition_passed:{item['condition_id']}", condition_report)
    return _completion("continue", "conditions_not_met", condition_report)


def _evaluate_conditions(conditions: List[Dict[str, Any]], progress: ContractProgress, verifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_evaluate_condition(condition, progress, verifications) for condition in conditions]


def _evaluate_condition(condition: Dict[str, Any], progress: ContractProgress, verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    source = str(condition["source"])
    op = str(condition["op"])
    expected = condition["value"]
    window = int(condition.get("window", 1) or 1)
    actual = _source_value(source, progress, verifications[-window:])
    passed = False
    if actual is not None and op in OPS:
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


def _source_value(source: str, progress: ContractProgress, window_verifications: List[Dict[str, Any]]) -> Any:
    last = window_verifications[-1] if window_verifications else {}
    if source == "last.intent_status":
        return last.get("intent_status")
    if source == "last.dominant_blocker":
        return last.get("dominant_blocker")
    if source.startswith("last.metric_delta.working."):
        return ((last.get("metric_delta", {}) or {}).get("working", {}) or {}).get(source.rsplit(".", 1)[-1], 0.0)
    if source.startswith("last.metric_delta.best_feasible."):
        return ((last.get("metric_delta", {}) or {}).get("best_feasible", {}) or {}).get(source.rsplit(".", 1)[-1], 0.0)
    if source.startswith("last.debt_delta."):
        return (last.get("debt_delta", {}) or {}).get(source.rsplit(".", 1)[-1], 0.0)
    if source == "last.protected_metric_result.passed":
        return (last.get("protected_metric_result", {}) or {}).get("passed")
    if source.startswith("last.trace.trial_flow."):
        key = source.rsplit(".", 1)[-1]
        return (((last.get("trace", {}) or {}).get("trial_flow", {}) or {}).get(key, 0))
    if source.startswith("aggregate.intent_status."):
        key = source.rsplit(".", 1)[-1]
        return progress.intent_status_counts.get(key, 0)
    if source.startswith("aggregate.dominant_blocker."):
        key = source.rsplit(".", 1)[-1]
        return progress.dominant_blocker_counts.get(key, 0)
    if source.startswith("aggregate.metric_delta_total."):
        key = source.rsplit(".", 1)[-1]
        return progress.metric_delta_total.get(key, 0.0)
    if source == "progress.solver_actions":
        return progress.solver_actions
    if source == "progress.iters_used":
        return progress.iters_used
    if source == "progress.time_used_sec":
        return progress.time_used_sec
    return None


def _completion(status: str, reason: str, condition_report: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "completion_status": status,
        "completion_reason": reason,
        "condition_report": list(condition_report),
        "completed": status != "continue",
        "reason": reason,
        "result": status,
    }


__all__ = ["update_contract_progress", "check_contract_completion"]
