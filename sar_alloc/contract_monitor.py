from __future__ import annotations

from typing import Any, Dict, List

from .tools.llm_utils import ContractProgress, SearchContract


def update_contract_events(progress: ContractProgress, events: List[str]) -> None:
    event_set = set(events)
    known_events = set(progress.event_counts) | set(progress.consecutive_event_counts) | event_set
    for event in known_events:
        if event in event_set:
            progress.event_counts[event] = progress.event_counts.get(event, 0) + 1
            progress.consecutive_event_counts[event] = progress.consecutive_event_counts.get(event, 0) + 1
        else:
            progress.consecutive_event_counts[event] = 0


def check_contract_completion(contract: SearchContract, progress: ContractProgress) -> Dict[str, Any]:
    policy = contract.completion_policy
    if progress.solver_actions >= int(policy["max_solver_actions"]):
        return {"completed": True, "reason": "max_solver_actions_reached", "result": "budget"}
    if progress.time_used_sec >= float(policy["max_time_sec"]):
        return {"completed": True, "reason": "max_time_reached", "result": "budget"}
    if progress.iters_used >= int(policy["max_iters"]):
        return {"completed": True, "reason": "max_iters_reached", "result": "budget"}
    if progress.solver_actions < int(policy["min_solver_actions"]):
        return {"completed": False, "reason": "", "result": "running"}
    for rule in policy["success_rules"]:
        if _rule_matched(rule, progress):
            return {"completed": True, "reason": f"success_rule:{rule['event']}", "result": "success"}
    for rule in policy["failure_rules"]:
        if _rule_matched(rule, progress):
            return {"completed": True, "reason": f"failure_rule:{rule['event']}", "result": "failure"}
    return {"completed": False, "reason": "", "result": "running"}


def _rule_matched(rule: Dict[str, Any], progress: ContractProgress) -> bool:
    source = progress.consecutive_event_counts if rule["scope"] == "consecutive" else progress.event_counts
    return int(source.get(rule["event"], 0)) >= int(rule["count"])


__all__ = ["update_contract_events", "check_contract_completion"]
