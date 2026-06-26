"""Strict validation for executable LLM decisions."""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Set

from .llm_public_interface import PublicCandidate, PublicCandidates
from .schemas import SUPPORTED_CONDITION_SOURCES

SOLVER_ACTIONS = ("construct_initial", "run_alns", "request_supervisor_review")
CONTRACT_TYPES = ("initial_construction", "alns_search", "recovery", "final_refinement")
DEFAULT_RELAXATION_RATIO_BOUNDS = {
    "time_window": {"min": 0.0, "max": 0.30},
    "energy": {"min": 0.0, "max": 0.20},
}
QUALITY_METRICS = {
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance",
}
INTENT_TYPES = {"construction", "repair", "improvement", "diversification", "review"}


def validate_sparse_score_items(
    items: Any,
    candidates: Iterable[PublicCandidate] | Iterable[str],
    *,
    field_name: str = "scores",
    min_len: int = 0,
    max_len: int = 3,
) -> List[Dict[str, Any]]:
    if not isinstance(items, list) or not min_len <= len(items) <= max_len:
        raise ValueError(f"{field_name} must be a list of length {min_len}..{max_len}")
    allowed = {
        candidate.name if isinstance(candidate, PublicCandidate) else str(candidate)
        for candidate in candidates
    }
    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []
    for index, raw in enumerate(items):
        item = _object(raw, f"{field_name}[{index}]")
        _exact(item, {"name", "score"}, f"{field_name}[{index}]")
        name = _string(item, "name", f"{field_name}[{index}]")
        if name not in allowed:
            raise ValueError(
                f"{field_name}[{index}].name is not allowed: {name}. "
                f"allowed={sorted(allowed)}"
            )
        if name in seen:
            raise ValueError(f"duplicate name in {field_name}: {name}")
        seen.add(name)
        _int_range(item, "score", 0, 10, f"{field_name}[{index}]")
        out.append(item)
    return out


def validate_insertion_control(
    control: Any, action_space_or_candidates: Any
) -> Dict[str, Any]:
    raw = _object(control, "insertion_control")
    _exact(
        raw,
        {"operator_scores", "task_signal_scores", "position_signal_scores"},
        "insertion_control",
    )
    allowed_ops = _allowed(
        action_space_or_candidates,
        "allowed_insertion_operators",
        "insertion_operator_candidates",
    )
    allowed_task = _allowed(
        action_space_or_candidates,
        "allowed_task_signals",
        "insertion_task_signal_candidates",
    )
    allowed_pos = _allowed(
        action_space_or_candidates,
        "allowed_position_signals",
        "insertion_position_signal_candidates",
    )
    validate_sparse_score_items(
        raw["operator_scores"],
        allowed_ops,
        field_name="insertion_control.operator_scores",
    )
    validate_sparse_score_items(
        raw["task_signal_scores"],
        allowed_task,
        field_name="insertion_control.task_signal_scores",
    )
    validate_sparse_score_items(
        raw["position_signal_scores"],
        allowed_pos,
        field_name="insertion_control.position_signal_scores",
    )
    return raw


def validate_destroy_control(
    control: Any, action_space_or_candidates: Any
) -> Dict[str, Any]:
    raw = _object(control, "destroy_control")
    _exact(
        raw, {"operator_scores", "signal_scores", "intensity_score"}, "destroy_control"
    )
    allowed_ops = _allowed(
        action_space_or_candidates,
        "allowed_destroy_operators",
        "destroy_operator_candidates",
    )
    allowed_signals = _allowed(
        action_space_or_candidates,
        "allowed_destroy_signals",
        "destroy_signal_candidates",
    )
    validate_sparse_score_items(
        raw["operator_scores"],
        allowed_ops,
        field_name="destroy_control.operator_scores",
    )
    validate_sparse_score_items(
        raw["signal_scores"],
        allowed_signals,
        field_name="destroy_control.signal_scores",
    )
    _int_range(raw, "intensity_score", 0, 10, "destroy_control")
    return raw


def validate_acceptance_control(
    control: Any, action_space_or_candidates: Any
) -> Dict[str, Any]:
    raw = _object(control, "acceptance_control")
    _exact(raw, {"mode", "intensity_score"}, "acceptance_control")
    mode = _string(raw, "mode", "acceptance_control")
    if mode not in set(
        _allowed(
            action_space_or_candidates,
            "allowed_acceptance_modes",
            "acceptance_candidates",
        )
    ):
        raise ValueError(f"unknown acceptance mode: {mode}")
    _int_range(raw, "intensity_score", 0, 10, "acceptance_control")
    return raw


def validate_feasibility_control(
    control: Any,
    candidates: Optional[PublicCandidates] = None,
    config: Optional[Any] = None,
) -> Dict[str, Any]:
    raw = _object(control, "feasibility_control")
    _exact(raw, {"mode", "relaxation_ratios"}, "feasibility_control")
    mode = _string(raw, "mode", "feasibility_control")
    allowed_modes = (
        set(candidates.names("feasibility_mode_candidates"))
        if candidates is not None
        else {"strict", "relaxed_recoverable", "recovery_only"}
    )
    if mode not in allowed_modes:
        raise ValueError(f"unknown feasibility mode candidate: {mode}")
    ratios = _list(raw["relaxation_ratios"], "feasibility_control.relaxation_ratios")
    if mode != "relaxed_recoverable":
        if ratios:
            raise ValueError(
                f"{mode} feasibility_control requires empty relaxation_ratios"
            )
        return raw
    if not ratios:
        raise ValueError("relaxed_recoverable requires at least one relaxation ratio")

    bounds = _relaxation_ratio_bounds(config)
    allowed_types = (
        set(candidates.names("relaxable_violation_candidates"))
        if candidates is not None
        else set(bounds)
    )
    seen: Set[str] = set()
    for index, value in enumerate(ratios):
        context = f"feasibility_control.relaxation_ratios[{index}]"
        item = _object(value, context)
        _exact(item, {"violation_type", "max_ratio"}, context)
        violation_type = _string(item, "violation_type", context)
        if violation_type not in allowed_types:
            raise ValueError(
                f"{context}.violation_type is not relaxable: {violation_type}"
            )
        if violation_type in seen:
            raise ValueError(f"duplicate relaxation ratio type: {violation_type}")
        seen.add(violation_type)
        ratio = _finite_number(item, "max_ratio", context)
        type_bounds = bounds[violation_type]
        if ratio < type_bounds["min"] or ratio > type_bounds["max"]:
            raise ValueError(
                f"{context}.max_ratio must be in [{type_bounds['min']}, {type_bounds['max']}]"
            )
    return raw


def validate_supervisor_kickoff(
    payload: Any,
    observation_or_candidates: Any,
    candidates: Optional[PublicCandidates] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    observation, candidate_set = _split_observation_candidates(
        observation_or_candidates, candidates
    )
    root = _root(payload, "supervisor_decision")
    _exact(root, {"action", "global_objective", "next_contract"}, "supervisor_decision")
    if _string(root, "action", "supervisor_decision") != "start_run":
        raise ValueError("supervisor_decision.action must be start_run")
    _global_objective(root["global_objective"], observation, candidate_set)
    validate_contract(
        root["next_contract"],
        observation,
        candidate_set,
        config,
        remaining_budget or _budget_from_observation(observation),
        {"initial_construction"},
    )
    return payload


def validate_supervisor_review(
    payload: Any,
    observation_or_candidates: Any,
    candidates: Optional[PublicCandidates] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    observation, candidate_set = _split_observation_candidates(
        observation_or_candidates, candidates
    )
    root = _root(payload, "supervisor_decision")
    action = _string(root, "action", "supervisor_decision")
    if action == "issue_contract":
        _exact(
            root, {"action", "contract_review", "next_contract"}, "supervisor_decision"
        )
        _contract_review(root["contract_review"])
        validate_contract(
            root["next_contract"],
            observation,
            candidate_set,
            config,
            remaining_budget or _budget_from_observation(observation),
            {"alns_search", "recovery", "final_refinement"},
        )
        return payload
    if action == "stop_run":
        _exact(
            root,
            {"action", "contract_review", "stop_explanation"},
            "supervisor_decision",
        )
        _contract_review(root["contract_review"])
        _string(root, "stop_explanation", "supervisor_decision")
        return payload
    raise ValueError(f"illegal supervisor action: {action}")


def validate_contract(
    contract: Any,
    observation: Optional[Dict[str, Any]] = None,
    candidates: Optional[PublicCandidates] = None,
    config: Optional[Any] = None,
    remaining_budget: Optional[Dict[str, float]] = None,
    allowed_contract_types: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    raw = _object(contract, "contract")
    required = {
        "contract_type",
        "objective_layers",
        "feasibility_control",
        "decision_basis",
        "situation_summary",
        "target_intents",
        "protected_metrics",
        "resource_policy",
        "exit_conditions",
    }
    allowed = set(required) | {"audit_note"}
    _allowed_exact(raw, allowed, required, "contract")
    contract_type = _string(raw, "contract_type", "contract")
    type_allowed = set(allowed_contract_types or CONTRACT_TYPES)
    supervisor_space = _supervisor_action_space(observation)
    if supervisor_space.get("allowed_contract_types"):
        type_allowed &= set(
            str(x) for x in supervisor_space.get("allowed_contract_types", [])
        )
    if contract_type not in type_allowed:
        raise ValueError(f"contract.contract_type is not allowed: {contract_type}")

    layers = _string_list(raw, "objective_layers", "contract")
    allowed_objectives = (
        set(candidates.names("objective_candidates"))
        if candidates is not None
        else QUALITY_METRICS
    )
    if supervisor_space.get("allowed_objective_metrics"):
        allowed_objectives &= set(
            str(x) for x in supervisor_space.get("allowed_objective_metrics", [])
        )
    if not 1 <= len(layers) <= min(4, len(allowed_objectives)):
        raise ValueError("contract.objective_layers must contain 1 to 4 metrics")
    if len(set(layers)) != len(layers) or any(
        name not in allowed_objectives for name in layers
    ):
        raise ValueError(
            "contract.objective_layers must be unique allowed objective candidates"
        )

    feasibility = validate_feasibility_control(
        raw["feasibility_control"], candidates, config
    )
    basis_ids = _decision_basis(raw["decision_basis"], observation, "contract.decision_basis")
    _situation_summary(raw["situation_summary"], basis_ids, "contract.situation_summary")
    _target_intents(raw["target_intents"], observation)
    _protected_metrics(raw["protected_metrics"])
    _resource_policy(raw["resource_policy"], remaining_budget)
    _exit_conditions(raw["exit_conditions"])
    _audit_note_optional(raw)
    return raw


def validate_solver_decision(
    payload: Any,
    observation_or_candidates: Any,
    active_contract_type: Optional[str] = None,
    *,
    candidates: Optional[PublicCandidates] = None,
) -> Dict[str, Any]:
    observation = (
        observation_or_candidates
        if isinstance(observation_or_candidates, dict)
        and (
            "execution_state" in observation_or_candidates
            or "control_catalog" in observation_or_candidates
        )
        else None
    )
    candidate_source = candidates or (
        None if observation is not None else observation_or_candidates
    )
    root = _root(payload, "solver_decision")
    action = _string(root, "action", "solver_decision")
    contract_type = active_contract_type or str(
        ((observation or {}).get("active_contract") or {}).get("contract_type", "")
    )
    if observation is not None:
        allowed_actions = set(
            str(x)
            for x in (
                (observation.get("execution_state") or {}).get(
                    "hard_executable_actions"
                )
                or []
            )
        )
    elif contract_type == "initial_construction":
        allowed_actions = {"construct_initial", "request_supervisor_review"}
    else:
        allowed_actions = {"run_alns", "request_supervisor_review"}
    if action not in allowed_actions:
        raise ValueError(f"illegal solver action for {contract_type}: {action}")

    allowed_fields = {"action", "decision_basis", "situation_summary", "audit_note"}
    if action == "construct_initial":
        allowed_fields |= {
            "intent_id",
            "runtime_target",
            "insertion_control",
            "solver_budget",
            "expected_effects",
        }
        required = {
            "action",
            "decision_basis",
            "situation_summary",
            "intent_id",
            "runtime_target",
            "insertion_control",
            "solver_budget",
            "expected_effects",
        }
        _allowed_exact(root, allowed_fields, required, "solver_decision")
        basis_ids = _decision_basis(root["decision_basis"], observation, "solver_decision.decision_basis")
        _situation_summary(root["situation_summary"], basis_ids, "solver_decision.situation_summary")
        _validate_intent_id(root["intent_id"], observation)
        _validate_runtime_target(root["runtime_target"], root["intent_id"], observation)
        _solver_budget(root["solver_budget"], observation)
        _expected_effects(root["expected_effects"], basis_ids)
        validate_insertion_control(
            root["insertion_control"],
            _action_space_or_candidates(observation, candidate_source),
        )
    elif action == "run_alns":
        allowed_fields |= {
            "intent_id",
            "runtime_target",
            "destroy_control",
            "insertion_control",
            "acceptance_control",
            "solver_budget",
            "expected_effects",
        }
        required = {
            "action",
            "decision_basis",
            "situation_summary",
            "intent_id",
            "runtime_target",
            "destroy_control",
            "insertion_control",
            "acceptance_control",
            "solver_budget",
            "expected_effects",
        }
        _allowed_exact(root, allowed_fields, required, "solver_decision")
        basis_ids = _decision_basis(root["decision_basis"], observation, "solver_decision.decision_basis")
        _situation_summary(root["situation_summary"], basis_ids, "solver_decision.situation_summary")
        _validate_intent_id(root["intent_id"], observation)
        _validate_runtime_target(root["runtime_target"], root["intent_id"], observation)
        _solver_budget(root["solver_budget"], observation)
        _expected_effects(root["expected_effects"], basis_ids)
        validate_destroy_control(
            root["destroy_control"],
            _action_space_or_candidates(observation, candidate_source),
        )
        validate_insertion_control(
            root["insertion_control"],
            _action_space_or_candidates(observation, candidate_source),
        )
        validate_acceptance_control(
            root["acceptance_control"],
            _action_space_or_candidates(observation, candidate_source),
        )
    else:
        allowed_fields.add("review_request")
        _allowed_exact(
            root,
            allowed_fields,
            {"action", "decision_basis", "situation_summary", "review_request"},
            "solver_decision",
        )
        basis_ids = _decision_basis(root["decision_basis"], observation, "solver_decision.decision_basis")
        _situation_summary(root["situation_summary"], basis_ids, "solver_decision.situation_summary")
        _review_request(root["review_request"])
    _audit_note_optional(root)
    return payload


def _global_objective(
    raw_value: Any,
    observation: Optional[Dict[str, Any]],
    candidates: Optional[PublicCandidates],
) -> None:
    raw = _object(raw_value, "global_objective")
    _allowed_exact(
        raw,
        {"objective_layers", "audit_note"},
        {"objective_layers"},
        "global_objective",
    )
    layers = _string_list(raw, "objective_layers", "global_objective")
    allowed = (
        set(candidates.names("objective_candidates"))
        if candidates is not None
        else QUALITY_METRICS
    )
    supervisor_space = _supervisor_action_space(observation)
    if supervisor_space.get("allowed_objective_metrics"):
        allowed &= set(
            str(x) for x in supervisor_space.get("allowed_objective_metrics", [])
        )
    if not 1 <= len(layers) <= min(4, len(allowed)):
        raise ValueError(
            "global_objective.objective_layers must contain 1 to 4 metrics"
        )
    if len(set(layers)) != len(layers):
        raise ValueError("global_objective.objective_layers contains duplicates")
    unknown = [name for name in layers if name not in allowed]
    if unknown:
        raise ValueError(f"unknown objective candidate: {unknown[0]}")
    _audit_note_optional(raw)


def _contract_review(raw_value: Any) -> None:
    raw = _object(raw_value, "contract_review")
    _exact(raw, {"outcome_summary", "main_lesson"}, "contract_review")
    for key in ("outcome_summary", "main_lesson"):
        _string(raw, key, "contract_review")


def _decision_basis(
    raw_value: Any,
    observation: Optional[Dict[str, Any]],
    context: str,
) -> Set[str]:
    values = _list(raw_value, context)
    if not 1 <= len(values) <= 4:
        raise ValueError(f"{context} must contain 1 to 4 items")
    seen: Set[str] = set()
    for index, value in enumerate(values):
        item_context = f"{context}[{index}]"
        item = _object(value, item_context)
        _exact(item, {"basis_id", "claim", "evidence_refs"}, item_context)
        basis_id = _string(item, "basis_id", item_context)
        if basis_id in seen:
            raise ValueError(f"duplicate basis_id: {basis_id}")
        seen.add(basis_id)
        _string(item, "claim", item_context)
        refs = _string_list(item, "evidence_refs", item_context)
        if not 1 <= len(refs) <= 5:
            raise ValueError(f"{item_context}.evidence_refs must contain 1 to 5 refs")
        if observation is not None:
            for ref in refs:
                if not _observation_ref_exists(observation, ref):
                    raise ValueError(f"{item_context}.evidence_refs unresolved: {ref}")
    return seen


def _situation_summary(raw_value: Any, basis_ids: Set[str], context: str) -> None:
    raw = _object(raw_value, context)
    _exact(raw, {"summary", "basis_ids"}, context)
    _string(raw, "summary", context)
    refs = _string_list(raw, "basis_ids", context)
    if not refs or any(ref not in basis_ids for ref in refs):
        raise ValueError(f"{context}.basis_ids must reference decision_basis")


def _target_intents(
    raw_value: Any, observation: Optional[Dict[str, Any]] = None
) -> None:
    values = _list(raw_value, "target_intents")
    if not 1 <= len(values) <= 6:
        raise ValueError("target_intents must contain 1 to 6 items")
    seen: Set[str] = set()
    for index, value in enumerate(values):
        context = f"target_intents[{index}]"
        item = _object(value, context)
        _exact(
            item,
            {
                "intent_id",
                "intent_type",
                "evidence_refs",
                "expected_effects",
                "rationale",
            },
            context,
        )
        intent_id = _string(item, "intent_id", context)
        if intent_id in seen:
            raise ValueError(f"duplicate intent_id: {intent_id}")
        seen.add(intent_id)
        if _string(item, "intent_type", context) not in INTENT_TYPES:
            raise ValueError(f"{context}.intent_type is invalid")
        refs = _string_list(item, "evidence_refs", context)
        if not 1 <= len(refs) <= 8:
            raise ValueError(f"{context}.evidence_refs must contain 1 to 8 refs")
        if observation is not None:
            for ref in refs:
                if not _observation_ref_exists(observation, ref):
                    raise ValueError(f"{context}.evidence_refs unresolved: {ref}")
        _legacy_expected_effects(item["expected_effects"])
        _string(item, "rationale", context)


def _expected_effects(raw_value: Any, basis_ids: Set[str]) -> None:
    values = _list(raw_value, "expected_effects")
    if len(values) > 4:
        raise ValueError("expected_effects must contain at most 4 items")
    for index, value in enumerate(values):
        context = f"expected_effects[{index}]"
        item = _object(value, context)
        _exact(item, {"effect_id", "metric", "direction", "scope", "basis_ids"}, context)
        _string(item, "effect_id", context)
        if _string(item, "metric", context) not in QUALITY_METRICS:
            raise ValueError(f"{context}.metric is invalid")
        if _string(item, "direction", context) not in {
            "decrease",
            "increase",
            "stabilize",
        }:
            raise ValueError(f"{context}.direction is invalid")
        if _string(item, "scope", context) not in {"working", "best", "contract"}:
            raise ValueError(f"{context}.scope is invalid")
        refs = _string_list(item, "basis_ids", context)
        if not refs or any(ref not in basis_ids for ref in refs):
            raise ValueError(f"{context}.basis_ids must reference decision_basis")


def _legacy_expected_effects(raw_value: Any) -> None:
    values = _list(raw_value, "expected_effects")
    if len(values) > 4:
        raise ValueError("target_intents.expected_effects must contain at most 4 items")
    for index, value in enumerate(values):
        context = f"target_intents.expected_effects[{index}]"
        item = _object(value, context)
        if "basis_ids" in item:
            _exact(item, {"effect_id", "metric", "direction", "scope", "basis_ids"}, context)
        else:
            _exact(item, {"metric", "direction"}, context)
        if _string(item, "metric", context) not in QUALITY_METRICS:
            raise ValueError(f"{context}.metric is invalid")
        if _string(item, "direction", context) not in {
            "decrease",
            "increase",
            "maintain",
            "stabilize",
        }:
            raise ValueError(f"{context}.direction is invalid")


def _validate_intent_id(raw_value: Any, observation: Optional[Dict[str, Any]]) -> None:
    intent_id = raw_value if isinstance(raw_value, str) else ""
    if not intent_id.strip():
        raise ValueError("solver_decision.intent_id must be a non-empty string")
    if observation is None:
        return
    intents = {
        str(item.get("intent_id", ""))
        for item in ((observation.get("active_contract") or {}).get("target_intents") or [])
        if isinstance(item, dict)
    }
    if intent_id not in intents:
        raise ValueError(f"solver_decision.intent_id is not in target_intents: {intent_id}")


def _validate_runtime_target(
    raw_value: Any, intent_id: Any, observation: Optional[Dict[str, Any]]
) -> None:
    raw = _object(raw_value, "runtime_target")
    _exact(raw, {"scope_kind", "task_ids", "agent_ids", "focus_metrics"}, "runtime_target")
    scope_kind = _string(raw, "scope_kind", "runtime_target")
    if scope_kind not in {"global", "task_scope", "route_scope", "mixed_scope"}:
        raise ValueError("runtime_target.scope_kind is invalid")

    task_ids = _runtime_target_int_list(
        raw.get("task_ids"), "runtime_target.task_ids", max_len=8
    )
    agent_ids = _runtime_target_int_list(
        raw.get("agent_ids"), "runtime_target.agent_ids", max_len=6
    )
    metrics = _string_list(raw, "focus_metrics", "runtime_target")
    if not 1 <= len(metrics) <= 3:
        raise ValueError("runtime_target.focus_metrics must contain 1 to 3 metrics")
    if len(set(metrics)) != len(metrics) or any(
        metric not in QUALITY_METRICS for metric in metrics
    ):
        raise ValueError("runtime_target.focus_metrics must be unique quality metrics")

    if scope_kind == "global":
        if task_ids or agent_ids:
            raise ValueError("global runtime_target cannot include task_ids or agent_ids")
    elif scope_kind == "task_scope":
        if not task_ids or agent_ids:
            raise ValueError("task_scope runtime_target requires task_ids only")
    elif scope_kind == "route_scope":
        if task_ids or not agent_ids:
            raise ValueError("route_scope runtime_target requires agent_ids only")
    elif not task_ids and not agent_ids:
        raise ValueError("mixed_scope runtime_target requires task_ids or agent_ids")

    if observation is None:
        return
    evidence = dict(observation.get("targetable_evidence", {}) or {})
    visible_tasks = {
        int(tid) for tid in evidence.get("visible_task_ids", []) or []
        if not isinstance(tid, bool)
    }
    visible_agents = {
        int(aid) for aid in evidence.get("visible_agent_ids", []) or []
        if not isinstance(aid, bool)
    }
    unknown_tasks = [tid for tid in task_ids if tid not in visible_tasks]
    unknown_agents = [aid for aid in agent_ids if aid not in visible_agents]
    if unknown_tasks:
        raise ValueError(
            f"runtime_target.task_ids contains non-visible task id: {unknown_tasks[0]}"
        )
    if unknown_agents:
        raise ValueError(
            f"runtime_target.agent_ids contains non-visible agent id: {unknown_agents[0]}"
        )
    if intent_id is not None and not str(intent_id).strip():
        raise ValueError("runtime_target requires the selected intent_id")


def _runtime_target_int_list(raw_value: Any, field_name: str, *, max_len: int) -> List[int]:
    values = _list(raw_value, field_name)
    if len(values) > max_len:
        raise ValueError(f"{field_name} must contain at most {max_len} items")
    out: List[int] = []
    seen: Set[int] = set()
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name}[{index}] must be an integer")
        if int(value) in seen:
            raise ValueError(f"{field_name} contains duplicate id: {value}")
        seen.add(int(value))
        out.append(int(value))
    return out


def _solver_budget(raw_value: Any, observation: Optional[Dict[str, Any]]) -> None:
    raw = _object(raw_value, "solver_budget")
    _exact(raw, {"max_iters", "max_time_sec"}, "solver_budget")
    max_iters = _positive_int(raw, "max_iters", "solver_budget")
    max_time = _positive_number(raw, "max_time_sec", "solver_budget")
    if observation is not None:
        remaining = (
            ((observation.get("execution_state") or {}).get("remaining_contract_resources"))
            or {}
        )
        if max_iters > int(float(remaining.get("iters", max_iters))):
            raise ValueError("solver_budget.max_iters exceeds remaining contract iters")
        if max_time > float(remaining.get("time_sec", max_time)) + 1e-9:
            raise ValueError("solver_budget.max_time_sec exceeds remaining contract time")


def _review_request(raw_value: Any) -> None:
    raw = _object(raw_value, "review_request")
    _exact(raw, {"reason", "evidence_refs"}, "review_request")
    _string(raw, "reason", "review_request")
    refs = _string_list(raw, "evidence_refs", "review_request")
    if not 1 <= len(refs) <= 8:
        raise ValueError("review_request.evidence_refs must contain 1 to 8 refs")


def _protected_metrics(raw_value: Any) -> None:
    values = _list(raw_value, "protected_metrics")
    if len(values) > 4:
        raise ValueError("protected_metrics must contain at most 4 items")
    seen: Set[str] = set()
    for index, value in enumerate(values):
        context = f"protected_metrics[{index}]"
        item = _object(value, context)
        _exact(item, {"metric", "max_worsen"}, context)
        metric = _string(item, "metric", context)
        if metric not in QUALITY_METRICS or metric in seen:
            raise ValueError(f"{context}.metric is invalid or duplicated")
        seen.add(metric)
        if _finite_number(item, "max_worsen", context) < 0.0:
            raise ValueError(f"{context}.max_worsen must be non-negative")


def _resource_policy(
    raw_value: Any, remaining_budget: Optional[Dict[str, float]]
) -> None:
    raw = _object(raw_value, "resource_policy")
    _exact(
        raw,
        {"min_actions", "max_actions", "max_iters", "max_time_sec"},
        "resource_policy",
    )
    min_actions = _int_range(raw, "min_actions", 1, 20, "resource_policy")
    max_actions = _positive_int(raw, "max_actions", "resource_policy")
    if min_actions > max_actions:
        raise ValueError("resource_policy.min_actions must be <= max_actions")
    max_time = _positive_number(raw, "max_time_sec", "resource_policy")
    max_iters = _positive_int(raw, "max_iters", "resource_policy")
    if remaining_budget is not None:
        allowed_actions = min(
            int(
                float(
                    remaining_budget.get(
                        "step_calls", remaining_budget.get("actions", 0)
                    )
                )
            ),
            int(
                float(
                    remaining_budget.get(
                        "solver_calls", remaining_budget.get("actions", 0)
                    )
                )
            ),
        )
        if allowed_actions > 0 and max_actions > allowed_actions:
            raise ValueError(
                "resource_policy.max_actions exceeds remaining action limit"
            )
        if max_time > float(remaining_budget.get("time_sec", max_time)) + 1e-9:
            raise ValueError("resource_policy.max_time_sec exceeds remaining time_sec")
        if max_iters > int(float(remaining_budget.get("iters", max_iters))):
            raise ValueError("resource_policy.max_iters exceeds remaining iters")


def _exit_conditions(raw_value: Any) -> None:
    raw = _object(raw_value, "exit_conditions")
    _exact(raw, {"success", "failure"}, "exit_conditions")
    for name in ("success", "failure"):
        values = _list(raw[name], f"exit_conditions.{name}")
        if len(values) > 4:
            raise ValueError(
                f"exit_conditions.{name} must contain at most 4 conditions"
            )
        seen: Set[str] = set()
        for index, value in enumerate(values):
            context = f"exit_conditions.{name}[{index}]"
            item = _object(value, context)
            _exact(item, {"condition_id", "source", "op", "value", "window"}, context)
            condition_id = _string(item, "condition_id", context)
            if condition_id in seen:
                raise ValueError(f"duplicate condition_id: {condition_id}")
            seen.add(condition_id)
            source = _string(item, "source", context)
            if source not in SUPPORTED_CONDITION_SOURCES:
                raise ValueError(
                    f"{context}.source is not allowed: {source}. "
                    f"allowed={list(SUPPORTED_CONDITION_SOURCES)}"
                )
            if _string(item, "op", context) not in {"<", "<=", "==", "!=", ">=", ">"}:
                raise ValueError(f"{context}.op is invalid")
            _condition_value(item.get("value"), f"{context}.value")
            _int_range(item, "window", 1, 20, context)


def _allowed(source: Any, action_space_key: str, candidate_key: str) -> List[str]:
    if isinstance(source, dict):
        key_aliases = {
            "allowed_insertion_operators": "insertion_operators",
            "allowed_task_signals": "insertion_task_signals",
            "allowed_position_signals": "insertion_position_signals",
            "allowed_destroy_operators": "destroy_operators",
            "allowed_destroy_signals": "destroy_signals",
            "allowed_acceptance_modes": "acceptance_modes",
        }
        key = action_space_key if action_space_key in source else key_aliases.get(action_space_key, action_space_key)
        values = source.get(key, [])
        return [
            str(item.get("name")) if isinstance(item, dict) else str(item)
            for item in values
        ]
    if source is not None and hasattr(source, "names"):
        return list(source.names(candidate_key))
    return []


def _action_space_or_candidates(
    observation: Optional[Dict[str, Any]], candidates: Any
) -> Any:
    return (
        (observation or {}).get("control_catalog")
        if observation is not None
        else candidates
    )


def _split_observation_candidates(
    value: Any, candidates: Optional[PublicCandidates]
) -> tuple[Optional[Dict[str, Any]], Optional[PublicCandidates]]:
    if isinstance(value, dict):
        return value, candidates
    return None, value if candidates is None else candidates


def _supervisor_action_space(
    observation: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if not isinstance(observation, dict):
        return {}
    value = observation.get("action_space", {}) or {}
    return dict(value) if isinstance(value, dict) else {}


def _budget_from_observation(
    observation: Optional[Dict[str, Any]],
) -> Optional[Dict[str, float]]:
    if not isinstance(observation, dict):
        return None
    limits = _supervisor_action_space(observation).get(
        "next_contract_resource_limits", {}
    ) or {}
    if limits:
        return {
            "step_calls": float(
                limits.get("max_solver_actions_allowed", 0) or 0
            ),
            "solver_calls": float(
                limits.get("max_solver_actions_allowed", 0) or 0
            ),
            "time_sec": float(limits.get("max_time_sec_allowed", 0.0) or 0.0),
            "iters": float(limits.get("max_iters_allowed", 0) or 0),
        }
    return None


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
    _allowed_exact(raw, expected, expected, field_name)


def _allowed_exact(
    raw: Dict[str, Any], allowed: Set[str], required: Set[str], field_name: str
) -> None:
    actual = set(raw)
    extra = sorted(actual - allowed)
    missing = sorted(required - actual)
    if extra:
        raise ValueError(f"unknown field '{field_name}.{extra[0]}'")
    if missing:
        raise ValueError(f"missing field '{field_name}.{missing[0]}'")


def _string(raw: Dict[str, Any], key: str, field_name: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name}.{key} must be a non-empty string")
    return value.strip()


def _string_list(raw: Dict[str, Any], key: str, field_name: str) -> List[str]:
    value = raw.get(key)
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{field_name}.{key} must be a list of non-empty strings")
    return [item.strip() for item in value]


def _int_range(
    raw: Dict[str, Any], key: str, lower: int, upper: int, field_name: str
) -> int:
    value = raw.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not lower <= value <= upper
    ):
        raise ValueError(f"{field_name}.{key} must be an integer in [{lower}, {upper}]")
    return value


def _positive_int(raw: Dict[str, Any], key: str, field_name: str) -> int:
    return _int_range(raw, key, 1, 2_147_483_647, field_name)


def _positive_number(raw: Dict[str, Any], key: str, field_name: str) -> float:
    value = _finite_number(raw, key, field_name)
    if value <= 0:
        raise ValueError(f"{field_name}.{key} must be positive")
    return value


def _finite_number(raw: Dict[str, Any], key: str, field_name: str) -> float:
    value = raw.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field_name}.{key} must be a finite number")
    return float(value)


def _condition_value(value: Any, field_name: str) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, str) and value:
        return
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    ):
        return
    raise ValueError(
        f"{field_name} must be a finite number, non-empty string, or boolean"
    )


def _audit_note_optional(raw: Dict[str, Any]) -> None:
    if "audit_note" not in raw:
        return
    if not isinstance(raw["audit_note"], str):
        raise ValueError("audit_note must be a string")


def _observation_ref_exists(observation: Dict[str, Any], ref: str) -> bool:
    if not ref or ref.startswith(".") or ".." in ref:
        return False
    current: Any = observation
    for part in ref.split("."):
        if isinstance(current, dict):
            if part not in current:
                return False
            current = current[part]
        elif isinstance(current, list):
            if not part.isdigit():
                return False
            index = int(part)
            if index < 0 or index >= len(current):
                return False
            current = current[index]
        else:
            return False
    return True


def _relaxation_ratio_bounds(config: Optional[Any]) -> Dict[str, Dict[str, float]]:
    bounds = {
        name: {"min": float(values["min"]), "max": float(values["max"])}
        for name, values in DEFAULT_RELAXATION_RATIO_BOUNDS.items()
    }
    extras = getattr(config, "extras", {}) if config is not None else {}
    overrides = (
        extras.get("relaxation_ratio_bounds", {}) if isinstance(extras, dict) else {}
    )
    if not isinstance(overrides, dict):
        raise ValueError("config.extras['relaxation_ratio_bounds'] must be an object")
    for violation_type, raw in overrides.items():
        if violation_type not in bounds or not isinstance(raw, dict):
            raise ValueError(f"invalid relaxation ratio bounds: {violation_type}")
        lower = float(raw.get("min", bounds[violation_type]["min"]))
        upper = float(raw.get("max", bounds[violation_type]["max"]))
        if (
            not math.isfinite(lower)
            or not math.isfinite(upper)
            or lower < 0.0
            or upper < lower
        ):
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
