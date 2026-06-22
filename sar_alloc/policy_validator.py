from __future__ import annotations

"""Strict validation for all public LLM decisions."""

import math
from typing import Any, Dict, Iterable, List, Optional, Set

from .llm_public_interface import PublicCandidate, PublicCandidates


SOLVER_ACTIONS = ("construct_initial", "run_alns", "request_supervisor_review")
CONTRACT_TYPES = ("initial_construction", "alns_search", "recovery", "final_refinement")
DEFAULT_RELAXATION_RATIO_BOUNDS = {
    "time_window": {"min": 0.0, "max": 0.30},
    "energy": {"min": 0.0, "max": 0.20},
}


def validate_sparse_score_items(
    items: Any,
    candidates: Iterable[PublicCandidate],
    *,
    field_name: str = "scores",
    min_len: int = 0,
    max_len: int = 3,
) -> List[Dict[str, Any]]:
    if not isinstance(items, list) or not min_len <= len(items) <= max_len:
        raise ValueError(f"{field_name} must be a list of length {min_len}..{max_len}")
    allowed = {candidate.name for candidate in candidates}
    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []
    for index, raw in enumerate(items):
        item = _object(raw, f"{field_name}[{index}]")
        _exact(item, {"name", "score", "reason"}, f"{field_name}[{index}]")
        name = _string(item, "name", f"{field_name}[{index}]")
        if name not in allowed:
            raise ValueError(f"{field_name}[{index}].name is not a public candidate: {name}")
        if name in seen:
            raise ValueError(f"duplicate name in {field_name}: {name}")
        seen.add(name)
        _int_range(item, "score", 0, 10, f"{field_name}[{index}]")
        _string(item, "reason", f"{field_name}[{index}]")
        out.append(item)
    return out


def validate_insertion_control(control: Any, candidates: PublicCandidates) -> Dict[str, Any]:
    raw = _object(control, "insertion_control")
    _exact(raw, {"operator_scores", "task_signal_scores", "position_signal_scores"}, "insertion_control")
    validate_sparse_score_items(raw["operator_scores"], candidates.insertion_operator_candidates, field_name="insertion_control.operator_scores")
    validate_sparse_score_items(raw["task_signal_scores"], candidates.insertion_task_signal_candidates, field_name="insertion_control.task_signal_scores")
    validate_sparse_score_items(raw["position_signal_scores"], candidates.insertion_position_signal_candidates, field_name="insertion_control.position_signal_scores")
    return raw


def validate_destroy_control(control: Any, candidates: PublicCandidates) -> Dict[str, Any]:
    raw = _object(control, "destroy_control")
    _exact(raw, {"operator_scores", "signal_scores", "intensity_score"}, "destroy_control")
    validate_sparse_score_items(raw["operator_scores"], candidates.destroy_operator_candidates, field_name="destroy_control.operator_scores")
    validate_sparse_score_items(raw["signal_scores"], candidates.destroy_signal_candidates, field_name="destroy_control.signal_scores")
    _int_range(raw, "intensity_score", 0, 10, "destroy_control")
    return raw


def validate_acceptance_control(control: Any, candidates: PublicCandidates) -> Dict[str, Any]:
    raw = _object(control, "acceptance_control")
    _exact(raw, {"mode", "intensity_score", "reason"}, "acceptance_control")
    mode = _string(raw, "mode", "acceptance_control")
    if mode not in set(candidates.names("acceptance_candidates")):
        raise ValueError(f"unknown acceptance candidate: {mode}")
    _int_range(raw, "intensity_score", 0, 10, "acceptance_control")
    _string(raw, "reason", "acceptance_control")
    return raw


def validate_feasibility_control(
    control: Any,
    candidates: PublicCandidates,
    config: Optional[Any] = None,
) -> Dict[str, Any]:
    raw = _object(control, "feasibility_control")
    _exact(raw, {"mode", "relaxation_ratios"}, "feasibility_control")
    mode = _string(raw, "mode", "feasibility_control")
    allowed_modes = set(candidates.names("feasibility_mode_candidates"))
    if mode not in allowed_modes:
        raise ValueError(f"unknown feasibility mode candidate: {mode}")
    ratios = raw["relaxation_ratios"]
    if not isinstance(ratios, list):
        raise ValueError("feasibility_control.relaxation_ratios must be a list")
    if mode != "relaxed_recoverable":
        if ratios:
            raise ValueError(f"{mode} feasibility_control requires empty relaxation_ratios")
        return raw
    if not ratios:
        raise ValueError("relaxed_recoverable requires at least one relaxation ratio")

    bounds = _relaxation_ratio_bounds(config)
    allowed_types = set(candidates.names("relaxable_violation_candidates"))
    seen: Set[str] = set()
    for index, value in enumerate(ratios):
        context = f"feasibility_control.relaxation_ratios[{index}]"
        item = _object(value, context)
        _exact(item, {"type", "limit_ratio", "reason"}, context)
        violation_type = _string(item, "type", context)
        if violation_type not in allowed_types:
            raise ValueError(f"{context}.type is not relaxable: {violation_type}")
        if violation_type in seen:
            raise ValueError(f"duplicate relaxation ratio type: {violation_type}")
        seen.add(violation_type)
        ratio = _finite_number(item, "limit_ratio", context)
        type_bounds = bounds[violation_type]
        if ratio < type_bounds["min"] or ratio > type_bounds["max"]:
            raise ValueError(
                f"{context}.limit_ratio must be in "
                f"[{type_bounds['min']}, {type_bounds['max']}]"
            )
        _string(item, "reason", context)
    return raw


def validate_supervisor_kickoff(
    payload: Any,
    candidates: PublicCandidates,
    evidence_items: Optional[List[Dict[str, Any]]] = None,
    memory_items: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    root = _root(payload, "supervisor_decision")
    _exact(root, {"action", "global_objective", "next_contract", "decision_basis"}, "supervisor_decision")
    if _string(root, "action", "supervisor_decision") != "start_run":
        raise ValueError("supervisor_decision.action must be start_run")
    _global_objective(root["global_objective"], candidates)
    validate_contract(
        root["next_contract"],
        candidates,
        evidence_items,
        memory_items,
        config,
        remaining_budget,
        {"initial_construction"},
    )
    _decision_basis(root["decision_basis"], evidence_items, memory_items)
    return payload


def validate_supervisor_review(
    payload: Any,
    candidates: PublicCandidates,
    evidence_items: Optional[List[Dict[str, Any]]] = None,
    memory_items: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    root = _root(payload, "supervisor_decision")
    action = _string(root, "action", "supervisor_decision")
    if action == "issue_contract":
        _exact(root, {"action", "contract_review", "next_contract", "decision_basis"}, "supervisor_decision")
        _contract_review(root["contract_review"])
        validate_contract(
            root["next_contract"],
            candidates,
            evidence_items,
            memory_items,
            config,
            remaining_budget,
            {"alns_search", "recovery", "final_refinement"},
        )
        _decision_basis(root["decision_basis"], evidence_items, memory_items)
        return payload
    if action == "stop_run":
        _exact(root, {"action", "contract_review", "stop_reason", "decision_basis"}, "supervisor_decision")
        _contract_review(root["contract_review"])
        _string(root, "stop_reason", "supervisor_decision")
        _decision_basis(root["decision_basis"], evidence_items, memory_items)
        return payload
    raise ValueError(f"illegal supervisor action: {action}")


def validate_contract(
    contract: Any,
    candidates: PublicCandidates,
    evidence_items: Optional[List[Dict[str, Any]]] = None,
    memory_items: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
    allowed_contract_types: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    del evidence_items, memory_items
    raw = _object(contract, "contract")
    _exact(raw, {"contract_type", "stage_goal", "stage_objective_layers", "feasibility_control", "guidance", "completion_policy"}, "contract")
    contract_type = _string(raw, "contract_type", "contract")
    allowed_types = set(allowed_contract_types or CONTRACT_TYPES)
    if contract_type not in allowed_types:
        raise ValueError(f"contract.contract_type is not allowed: {contract_type}")

    goal = _object(raw["stage_goal"], "contract.stage_goal")
    _exact(goal, {"summary", "main_problem", "search_intent"}, "contract.stage_goal")
    for key in ("summary", "main_problem", "search_intent"):
        _string(goal, key, "contract.stage_goal")

    layers = _string_list(raw, "stage_objective_layers", "contract")
    allowed_objectives = set(candidates.names("objective_candidates"))
    if not 1 <= len(layers) <= min(4, len(allowed_objectives)):
        raise ValueError("contract.stage_objective_layers must contain 1 to 4 metrics")
    if len(set(layers)) != len(layers) or any(name not in allowed_objectives for name in layers):
        raise ValueError("contract.stage_objective_layers must be unique public objective candidates")

    validate_feasibility_control(raw["feasibility_control"], candidates, config)

    guidance = _object(raw["guidance"], "contract.guidance")
    _exact(guidance, {"instruction", "preferred_search_direction", "protect", "success_signal", "failure_signal"}, "contract.guidance")
    for key in ("instruction", "preferred_search_direction", "protect", "success_signal", "failure_signal"):
        _string(guidance, key, "contract.guidance")

    _completion_policy(raw["completion_policy"], candidates, remaining_budget)
    return raw


def validate_solver_decision(
    payload: Any,
    candidates: PublicCandidates,
    active_contract_type: str,
    evidence_items: Optional[List[Dict[str, Any]]] = None,
    memory_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    root = _root(payload, "solver_decision")
    action = _string(root, "action", "solver_decision")
    if active_contract_type == "initial_construction":
        allowed_actions = {"construct_initial", "request_supervisor_review"}
    elif active_contract_type in {"alns_search", "recovery", "final_refinement"}:
        allowed_actions = {"run_alns", "request_supervisor_review"}
    else:
        raise ValueError(f"unknown active contract type: {active_contract_type}")
    if action not in allowed_actions:
        raise ValueError(f"illegal solver action for {active_contract_type}: {action}")

    if action == "construct_initial":
        _exact(root, {"action", "reason", "insertion_control", "decision_basis"}, "solver_decision")
        validate_insertion_control(root["insertion_control"], candidates)
    elif action == "run_alns":
        _exact(root, {"action", "reason", "destroy_control", "insertion_control", "acceptance_control", "decision_basis"}, "solver_decision")
        validate_destroy_control(root["destroy_control"], candidates)
        validate_insertion_control(root["insertion_control"], candidates)
        validate_acceptance_control(root["acceptance_control"], candidates)
    else:
        _exact(root, {"action", "reason", "decision_basis"}, "solver_decision")
    _string(root, "reason", "solver_decision")
    _decision_basis(root["decision_basis"], evidence_items, memory_items)
    return payload


def _global_objective(raw_value: Any, candidates: PublicCandidates) -> None:
    raw = _object(raw_value, "global_objective")
    _exact(raw, {"objective_layers", "selection_basis"}, "global_objective")
    layers = _string_list(raw, "objective_layers", "global_objective")
    allowed = set(candidates.names("objective_candidates"))
    if not 1 <= len(layers) <= min(4, len(allowed)):
        raise ValueError("global_objective.objective_layers must contain 1 to 4 metrics")
    if len(set(layers)) != len(layers):
        raise ValueError("global_objective.objective_layers contains duplicates")
    unknown = [name for name in layers if name not in allowed]
    if unknown:
        raise ValueError(f"unknown objective candidate: {unknown[0]}")
    basis = _list(raw.get("selection_basis"), "global_objective.selection_basis")
    if len(basis) != len(layers):
        raise ValueError("global_objective.selection_basis must match objective_layers length")
    for index, item in enumerate(basis):
        context = f"global_objective.selection_basis[{index}]"
        basis_item = _object(item, context)
        _exact(basis_item, {"metric", "data_refs", "reason"}, context)
        if _string(basis_item, "metric", context) != layers[index]:
            raise ValueError("global_objective.selection_basis metric order must match objective_layers")
        refs = _string_list(basis_item, "data_refs", context)
        if not 1 <= len(refs) <= 4:
            raise ValueError("global_objective.selection_basis.data_refs must contain 1 to 4 refs")
        _string(basis_item, "reason", context)


def _contract_review(raw_value: Any) -> None:
    raw = _object(raw_value, "contract_review")
    _exact(raw, {"outcome_summary", "main_lesson", "next_intent"}, "contract_review")
    for key in ("outcome_summary", "main_lesson", "next_intent"):
        _string(raw, key, "contract_review")


def _completion_policy(raw_value: Any, candidates: PublicCandidates, remaining_budget: Optional[Dict[str, float]]) -> None:
    raw = _object(raw_value, "completion_policy")
    _exact(raw, {"min_solver_actions", "max_solver_actions", "max_time_sec", "max_iters", "success_rules", "failure_rules"}, "completion_policy")
    min_actions = _int_range(raw, "min_solver_actions", 1, 20, "completion_policy")
    max_actions = _positive_int(raw, "max_solver_actions", "completion_policy")
    if min_actions > max_actions:
        raise ValueError("completion_policy.min_solver_actions must be <= max_solver_actions")
    max_time = _positive_number(raw, "max_time_sec", "completion_policy")
    max_iters = _positive_int(raw, "max_iters", "completion_policy")
    if remaining_budget is not None:
        allowed_actions = min(
            int(float(remaining_budget.get("step_calls", 0))),
            int(float(remaining_budget.get("solver_calls", 0))),
        )
        if max_actions > allowed_actions:
            raise ValueError("completion_policy.max_solver_actions exceeds next contract solver action limit")
        if max_time > float(remaining_budget.get("time_sec", 0.0)) + 1e-9:
            raise ValueError("completion_policy.max_time_sec exceeds remaining time_sec")
        if max_iters > int(float(remaining_budget.get("iters", 0))):
            raise ValueError("completion_policy.max_iters exceeds remaining iters")
    _completion_rules(raw["success_rules"], candidates, "completion_policy.success_rules")
    _completion_rules(raw["failure_rules"], candidates, "completion_policy.failure_rules")


def _completion_rules(raw_value: Any, candidates: PublicCandidates, context: str) -> None:
    rules = _list(raw_value, context)
    if not 1 <= len(rules) <= 3:
        raise ValueError(f"{context} must contain 1 to 3 rules")
    allowed_events = set(candidates.names("completion_event_candidates"))
    seen: Set[str] = set()
    for index, raw_item in enumerate(rules):
        item_context = f"{context}[{index}]"
        rule = _object(raw_item, item_context)
        _exact(rule, {"event", "count", "scope"}, item_context)
        event = _string(rule, "event", item_context)
        if event not in allowed_events:
            raise ValueError(f"unknown completion event candidate: {event}")
        if event in seen:
            raise ValueError(f"duplicate completion event in {context}: {event}")
        seen.add(event)
        _int_range(rule, "count", 1, 20, item_context)
        scope = _string(rule, "scope", item_context)
        if scope not in {"total", "consecutive"}:
            raise ValueError(f"{item_context}.scope must be total or consecutive")


def _decision_basis(raw: Any, evidence_items: Optional[List[Dict[str, Any]]], memory_items: Optional[List[Dict[str, Any]]]) -> None:
    basis = _object(raw, "decision_basis")
    _exact(basis, {"evidence_refs", "memory_refs", "summary"}, "decision_basis")
    evidence_refs = _string_list(basis, "evidence_refs", "decision_basis")
    memory_refs = _string_list(basis, "memory_refs", "decision_basis")
    if not 1 <= len(evidence_refs) <= 6:
        raise ValueError("decision_basis.evidence_refs must contain 1 to 6 refs")
    if len(memory_refs) > 6:
        raise ValueError("decision_basis.memory_refs must contain at most 6 refs")
    _string(basis, "summary", "decision_basis")
    if evidence_items is not None:
        allowed = {str(item.get("id", "")) for item in evidence_items}
        if any(ref not in allowed for ref in evidence_refs):
            raise ValueError("decision_basis contains an unknown evidence ref")
    if memory_items is not None:
        allowed = {str(item.get("id", item.get("memory_id", ""))) for item in memory_items}
        if any(ref not in allowed for ref in memory_refs):
            raise ValueError("decision_basis contains an unknown memory ref")


def _root(payload: Any, key: str) -> Dict[str, Any]:
    raw = _object(payload, f"{key}_response")
    _exact(raw, {key}, f"{key}_response")
    return _object(raw[key], key)


def _object(value: Any, field_name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _list(value: Any, field_name: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return value


def _exact(raw: Dict[str, Any], expected: Set[str], field_name: str) -> None:
    actual = set(raw)
    if actual != expected:
        extra = sorted(actual - expected)
        missing = sorted(expected - actual)
        if extra:
            raise ValueError(f"unknown field '{field_name}.{extra[0]}'")
        raise ValueError(f"missing field '{field_name}.{missing[0]}'")


def _string(raw: Dict[str, Any], key: str, field_name: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name}.{key} must be a non-empty string")
    return value.strip()


def _string_list(raw: Dict[str, Any], key: str, field_name: str) -> List[str]:
    value = raw.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field_name}.{key} must be a list of non-empty strings")
    return [item.strip() for item in value]


def _int_range(raw: Dict[str, Any], key: str, lower: int, upper: int, field_name: str) -> int:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise ValueError(f"{field_name}.{key} must be an integer in [{lower}, {upper}]")
    return value


def _positive_int(raw: Dict[str, Any], key: str, field_name: str) -> int:
    return _int_range(raw, key, 1, 2_147_483_647, field_name)


def _positive_number(raw: Dict[str, Any], key: str, field_name: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) <= 0:
        raise ValueError(f"{field_name}.{key} must be a positive finite number")
    return float(value)


def _finite_number(raw: Dict[str, Any], key: str, field_name: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{field_name}.{key} must be a finite number")
    return float(value)


def _relaxation_ratio_bounds(config: Optional[Any]) -> Dict[str, Dict[str, float]]:
    bounds = {
        name: {"min": float(values["min"]), "max": float(values["max"])}
        for name, values in DEFAULT_RELAXATION_RATIO_BOUNDS.items()
    }
    extras = getattr(config, "extras", {}) if config is not None else {}
    overrides = extras.get("relaxation_ratio_bounds", {}) if isinstance(extras, dict) else {}
    if not isinstance(overrides, dict):
        raise ValueError("config.extras['relaxation_ratio_bounds'] must be an object")
    for violation_type, raw in overrides.items():
        if violation_type not in bounds or not isinstance(raw, dict):
            raise ValueError(f"invalid relaxation ratio bounds: {violation_type}")
        lower = float(raw.get("min", bounds[violation_type]["min"]))
        upper = float(raw.get("max", bounds[violation_type]["max"]))
        if not math.isfinite(lower) or not math.isfinite(upper) or lower < 0.0 or upper < lower:
            raise ValueError(f"invalid relaxation ratio bounds: {violation_type}")
        bounds[violation_type] = {"min": lower, "max": upper}
    return bounds


__all__ = [
    "SOLVER_ACTIONS",
    "DEFAULT_RELAXATION_RATIO_BOUNDS",
    "validate_sparse_score_items",
    "validate_insertion_control",
    "validate_destroy_control",
    "validate_acceptance_control",
    "validate_feasibility_control",
    "validate_supervisor_kickoff",
    "validate_supervisor_review",
    "validate_contract",
    "validate_solver_decision",
]
