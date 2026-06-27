"""LLM output parsing, validation, domain checks, and compilation."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

from jsonschema import validate as jsonschema_validate

from .config import Config
from .operators import AcceptancePolicy, DestroyPolicy, InsertionPolicy
from .schemas import CONSTRAINT_METRICS, QUALITY_METRICS, STEP_BASIS_NAMES, SUPERVISOR_BASIS_NAMES
from .step_agent import RuntimeControl, StepDecision
from .supervisor import StagePlan, SupervisorDecision


class AgentIOError(ValueError):
    """Raised when LLM output cannot be parsed, validated, or compiled."""


DEFAULT_DELTA_RULES: Dict[str, Dict[str, float]] = {
    "time_window": {"delta_fraction": 0.5, "delta_cap": 0.05},
    "energy": {"delta_fraction": 0.5, "delta_cap": 0.03},
}


def parse_validate_compile_supervisor(
    *,
    raw_text: str,
    schema: Dict[str, Any],
    observation: Dict[str, Any],
    phase: str,
    config: Config,
    stage_index: int,
) -> SupervisorDecision:
    try:
        payload = extract_json(raw_text)
        _validate_schema(payload, schema)
        root = dict(payload["supervisor_decision"])
        _validate_decision_evidence(
            root,
            observation,
            SUPERVISOR_BASIS_NAMES,
            require_expected_effect=(str(root.get("action")) == "issue_stage"),
        )
        _validate_supervisor_domain(root, observation)
        return _compile_supervisor_decision(
            root,
            phase=phase,
            config=config,
            stage_index=stage_index,
            observation=observation,
        )
    except Exception as exc:
        if isinstance(exc, AgentIOError):
            raise
        raise AgentIOError(str(exc)) from exc


def parse_validate_compile_step(
    *,
    raw_text: str,
    schema: Dict[str, Any],
    observation: Dict[str, Any],
    active_stage: StagePlan,
    config: Config,
) -> tuple[StepDecision, RuntimeControl]:
    del config
    try:
        payload = extract_json(raw_text)
        _validate_schema(payload, schema)
        root = dict(payload["step_decision"])
        _validate_decision_evidence(
            root,
            observation,
            STEP_BASIS_NAMES,
            require_expected_effect=(str(root.get("action")) != "request_supervisor_review"),
        )
        _validate_step_domain(root, observation, active_stage)
        decision = StepDecision(
            action=str(root["action"]),
            intent_id=str(root.get("intent_id", "")),
            decision_evidence=dict(root.get("decision_evidence", {}) or {}),
            raw=root,
        )
        control = _compile_step_control(root, active_stage, observation["action_space"])
        return decision, control
    except Exception as exc:
        if isinstance(exc, AgentIOError):
            raise
        raise AgentIOError(str(exc)) from exc


def extract_json(raw_text: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise AgentIOError(f"LLM output is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentIOError("LLM output must be one JSON object")
    return value


def compile_global_objective(config: Config, raw: Any) -> List[Dict[str, str]]:
    metrics = raw.get("objective_layers", raw) if isinstance(raw, Mapping) else raw
    layers: List[Dict[str, str]] = []
    for metric in metrics or []:
        name = str(metric)
        if name in CONSTRAINT_METRICS:
            raise AgentIOError(f"constraint metric is not a quality objective: {name}")
        if name not in QUALITY_METRICS:
            raise AgentIOError(f"unknown objective metric: {name}")
        layers.append({"metric": name, "direction": "min"})
    if layers:
        return layers
    return [
        {"metric": str(layer.metric), "direction": str(layer.direction)}
        for layer in config.eval.objective_policy.layers
    ]


def compile_protected_metric_bounds(
    protected_metrics: Iterable[Mapping[str, Any]],
    baseline: Mapping[str, Any],
) -> List[Dict[str, float | str]]:
    bounds: List[Dict[str, float | str]] = []
    for item in protected_metrics:
        metric = str(item["metric"])
        if metric not in baseline:
            raise AgentIOError(f"protected metric has no baseline: {metric}")
        bounds.append(
            {
                "metric": metric,
                "baseline": float(baseline[metric]),
                "max_worsen": float(item.get("max_worsen", 0.0) or 0.0),
            }
        )
    return bounds


def compile_feasibility_policy(feasibility_control: Mapping[str, Any], config: Config | None = None) -> Dict[str, Any]:
    mode = str(feasibility_control["mode"])
    if mode in {"strict", "recovery_only"}:
        return {"mode": mode}
    if mode != "relaxed_recoverable":
        raise AgentIOError(f"unknown feasibility mode: {mode}")

    rules = _load_delta_rules(config)
    per_type: Dict[str, Dict[str, float]] = {}
    for item in feasibility_control["relaxation_ratios"]:
        violation_type = str(item.get("violation_type", item.get("type", "")))
        limit_ratio = float(item.get("max_ratio", item.get("limit_ratio", 0.0)))
        rule = rules[violation_type]
        per_type[violation_type] = {
            "limit_ratio": limit_ratio,
            "delta_ratio": min(float(rule["delta_cap"]), float(rule["delta_fraction"]) * limit_ratio),
        }
    return {"mode": mode, "per_type": per_type}


def _compile_supervisor_decision(
    root: Mapping[str, Any],
    *,
    phase: str,
    config: Config,
    stage_index: int,
    observation: Mapping[str, Any],
) -> SupervisorDecision:
    action = str(root["action"])
    global_objective = compile_global_objective(config, root.get("global_objective", {})) if action == "issue_stage" else []
    if action == "stop_run":
        return SupervisorDecision(action=action, global_objective=[], next_stage=None, raw=dict(root))
    if action != "issue_stage":
        raise AgentIOError(f"unsupported supervisor action: {action}")

    raw_stage = dict(root["next_stage"])
    baseline = ((observation.get("solution_state", {}) or {}).get("working", {}) or {}).get("quality", {}) or {}
    stage = StagePlan(
        stage_id=f"S{stage_index:03d}",
        stage_type=str(raw_stage["stage_type"]),
        objective_layers=[{"metric": str(metric), "direction": "min"} for metric in raw_stage.get("objective_layers", []) or []],
        target_intents=[dict(item) for item in raw_stage.get("target_intents", []) or []],
        feasibility_policy=compile_feasibility_policy(raw_stage["feasibility_control"], config),
        protected_metrics=[dict(item) for item in raw_stage.get("protected_metrics", []) or []],
        protected_metric_baseline={str(k): float(v) for k, v in dict(baseline).items()},
        resource_policy=dict(raw_stage["resource_policy"]),
        raw=dict(raw_stage),
    )
    if phase == "kickoff" and stage.stage_type != "initial_construction":
        raise AgentIOError("kickoff supervisor must issue an initial_construction stage")
    return SupervisorDecision(action=action, global_objective=global_objective, next_stage=stage, raw=dict(root))


def _compile_step_control(
    root: Mapping[str, Any],
    active_stage: StagePlan,
    action_space: Mapping[str, Any],
) -> RuntimeControl:
    action = str(root["action"])
    if action == "request_supervisor_review":
        return RuntimeControl(
            action=action,
            intent_id="",
            runtime_target={},
            review_request=dict(root.get("review_request", {}) or {}),
        )
    intent_id = str(root["intent_id"])
    budget = dict(root.get("solver_budget", {}) or {})
    remaining = active_stage.remaining()
    control = RuntimeControl(
        action=action,
        intent_id=intent_id,
        runtime_target=_compile_runtime_target(root.get("runtime_target", {}) or {}, intent_id, active_stage),
        insertion_policy=_compile_insertion(root["insertion_control"], action_space),
        feasibility_policy=dict(active_stage.feasibility_policy),
        protected_metrics=[dict(item) for item in active_stage.protected_metrics],
        solver_budget={
            "max_time_sec": max(1e-6, min(float(budget.get("max_time_sec", 1e-6)), float(remaining.get("time_sec", 1e-6) or 1e-6))),
            "max_iters": max(1, min(int(budget.get("max_iters", 1)), int(remaining.get("iters", 1) or 1))),
        },
    )
    if action == "run_alns":
        control.destroy_policy = _compile_destroy(root["destroy_control"], action_space)
        control.acceptance_policy = _compile_acceptance(root["acceptance_control"])
    elif action != "construct_initial":
        raise AgentIOError(f"unsupported step action: {action}")
    return control


def _validate_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    jsonschema_validate(instance=payload, schema=schema)


def _validate_step_domain(root: Mapping[str, Any], observation: Mapping[str, Any], active_stage: StagePlan) -> None:
    action = str(root.get("action", ""))
    allowed = {str(item) for item in (observation.get("execution_state", {}) or {}).get("hard_executable_actions", [])}
    if allowed and action not in allowed:
        raise AgentIOError(f"step action is not executable now: {action}")
    if action == "request_supervisor_review":
        return
    intent_id = str(root.get("intent_id", ""))
    _require_stage_intent(active_stage, intent_id)
    target = dict(root.get("runtime_target", {}) or {})
    visible_tasks = {int(v) for v in (observation.get("targetable_evidence", {}) or {}).get("visible_task_ids", []) if not isinstance(v, bool)}
    visible_agents = {int(v) for v in (observation.get("targetable_evidence", {}) or {}).get("visible_agent_ids", []) if not isinstance(v, bool)}
    for tid in target.get("task_ids", []) or []:
        if int(tid) not in visible_tasks:
            raise AgentIOError(f"runtime_target references non-visible task id: {tid}")
    for aid in target.get("agent_ids", []) or []:
        if int(aid) not in visible_agents:
            raise AgentIOError(f"runtime_target references non-visible agent id: {aid}")
    remaining = (observation.get("execution_state", {}) or {}).get("remaining_stage_resources", {}) or {}
    budget = dict(root.get("solver_budget", {}) or {})
    if int(budget.get("max_iters", 1)) > int(remaining.get("iters", budget.get("max_iters", 1))):
        raise AgentIOError("solver_budget.max_iters exceeds remaining stage resources")
    if float(budget.get("max_time_sec", 1.0)) > float(remaining.get("time_sec", budget.get("max_time_sec", 1.0))) + 1e-9:
        raise AgentIOError("solver_budget.max_time_sec exceeds remaining stage resources")


def _validate_supervisor_domain(root: Mapping[str, Any], observation: Mapping[str, Any]) -> None:
    if str(root.get("action", "")) != "issue_stage":
        return
    limits = ((observation.get("action_space", {}) or {}).get("next_stage_resource_limits", {}) or {})
    policy = ((root.get("next_stage", {}) or {}).get("resource_policy", {}) or {})
    if limits and int(policy.get("max_actions", 0)) > int(limits.get("max_solver_actions_allowed", 0)):
        raise AgentIOError("next stage max_actions exceeds remaining global resources")
    if limits and int(policy.get("max_iters", 0)) > int(limits.get("max_iters_allowed", 0)):
        raise AgentIOError("next stage max_iters exceeds remaining global resources")
    if limits and float(policy.get("max_time_sec", 0.0)) > float(limits.get("max_time_sec_allowed", 0.0)) + 1e-9:
        raise AgentIOError("next stage max_time_sec exceeds remaining global resources")


def _validate_decision_evidence(
    root: Mapping[str, Any],
    observation: Mapping[str, Any],
    allowed_basis: Mapping[str, Iterable[str]],
    *,
    require_expected_effect: bool,
) -> None:
    evidence = root.get("decision_evidence", {})
    if not isinstance(evidence, Mapping):
        raise AgentIOError("decision_evidence must be an object")

    basis = list(evidence.get("basis", []) or [])
    if not basis:
        raise AgentIOError("decision_evidence.basis must not be empty")
    allowed_by_source = {str(source): {str(name) for name in names} for source, names in allowed_basis.items()}
    for index, item in enumerate(basis):
        if not isinstance(item, Mapping):
            raise AgentIOError(f"decision_evidence.basis[{index}] must be an object")
        source = str(item.get("source", ""))
        name = str(item.get("name", ""))
        if source not in allowed_by_source:
            raise AgentIOError(f"decision_evidence basis source is not allowed: {source}")
        if source not in observation:
            raise AgentIOError(f"decision_evidence basis source is not present in observation: {source}")
        if name not in allowed_by_source[source]:
            raise AgentIOError(f"decision_evidence basis name is not allowed for {source}: {name}")

    argument = list(evidence.get("argument", []) or [])
    if not argument:
        raise AgentIOError("decision_evidence.argument must not be empty")
    for arg_index, item in enumerate(argument):
        if not isinstance(item, Mapping):
            raise AgentIOError(f"decision_evidence.argument[{arg_index}] must be an object")
        uses = list(item.get("uses", []) or [])
        if not uses:
            raise AgentIOError(f"decision_evidence.argument[{arg_index}].uses must not be empty")
        for raw_index in uses:
            idx = int(raw_index)
            if idx < 0 or idx >= len(basis):
                raise AgentIOError(f"decision_evidence.argument[{arg_index}].uses index out of range: {idx}")

    effects = list(evidence.get("expected_effects", []) or [])
    if require_expected_effect and not effects:
        raise AgentIOError("executable decision must include at least one expected_effect")
    for item in effects:
        metric = str(item.get("metric", "")) if isinstance(item, Mapping) else ""
        if metric not in QUALITY_METRICS:
            raise AgentIOError(f"unknown expected_effect metric: {metric}")


def _compile_insertion(control: Mapping[str, Any], action_space: Mapping[str, Any]) -> InsertionPolicy:
    return InsertionPolicy(
        operator_weights=_weights(_names(action_space, "insertion_operators"), control.get("operator_scores", [])),
        task_signal_weights=_weights(_names(action_space, "insertion_task_signals"), control.get("task_signal_scores", [])),
        position_signal_weights=_weights(_names(action_space, "insertion_position_signals"), control.get("position_signal_scores", [])),
    )


def _compile_destroy(control: Mapping[str, Any], action_space: Mapping[str, Any]) -> DestroyPolicy:
    score = int(control["intensity_score"])
    return DestroyPolicy(
        operator_weights=_weights(_names(action_space, "destroy_operators"), control.get("operator_scores", [])),
        signal_weights=_weights(_names(action_space, "destroy_signals"), control.get("signal_scores", [])),
        intensity_score=score,
        remove_ratio=0.05 + 0.03 * score,
    )


def _compile_acceptance(control: Mapping[str, Any]) -> AcceptancePolicy:
    mode = str(control["mode"])
    score = int(control["intensity_score"])
    if mode == "greedy":
        return AcceptancePolicy(mode, score, 0.0, 0.0)
    if mode == "threshold":
        return AcceptancePolicy(mode, score, 0.02 * score, 0.5 * score)
    return AcceptancePolicy(mode, score, 0.05 * score, float(score))


def _compile_runtime_target(raw: Mapping[str, Any], intent_id: str, active_stage: StagePlan) -> Dict[str, Any]:
    return {
        "intent_id": intent_id,
        "intent_type": _require_stage_intent(active_stage, intent_id).get("intent_type", ""),
        "scope_kind": str(raw.get("scope_kind", "global")),
        "task_ids": _dedupe_ints(raw.get("task_ids", []) or []),
        "agent_ids": _dedupe_ints(raw.get("agent_ids", []) or []),
        "focus_metrics": _dedupe_strings(raw.get("focus_metrics", []) or []),
    }


def _require_stage_intent(active_stage: StagePlan, intent_id: str) -> Dict[str, Any]:
    for item in active_stage.target_intents:
        if str(item.get("intent_id", "")) == str(intent_id):
            return dict(item)
    raise AgentIOError(f"intent_id is not present in active stage: {intent_id}")


def _weights(names: List[str], items: Any) -> Dict[str, int]:
    selected = {str(item["name"]): int(item["score"]) for item in items or [] if isinstance(item, Mapping)}
    return {str(name): int(selected.get(str(name), 0)) for name in names}


def _names(space: Mapping[str, Any], key: str) -> List[str]:
    return [str(item.get("name")) if isinstance(item, Mapping) else str(item) for item in space.get(key, []) or []]


def _dedupe_ints(values: Any) -> List[int]:
    out: List[int] = []
    seen = set()
    for value in values:
        if isinstance(value, bool):
            continue
        item = int(value)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _dedupe_strings(values: Any) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values:
        item = str(value)
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _load_delta_rules(config: Config | None = None) -> Dict[str, Dict[str, float]]:
    rules = deepcopy(DEFAULT_DELTA_RULES)
    overrides = {} if config is None else config.extras.get("relaxation_delta_rules", {})
    if not isinstance(overrides, dict):
        raise AgentIOError("config.extras['relaxation_delta_rules'] must be an object")
    for violation_type, raw in overrides.items():
        if violation_type not in rules or not isinstance(raw, dict):
            raise AgentIOError(f"invalid relaxation delta rule: {violation_type}")
        for field in ("delta_fraction", "delta_cap"):
            if field in raw:
                value = float(raw[field])
                if not math.isfinite(value) or value < 0.0:
                    raise AgentIOError(f"{violation_type}.{field} must be a non-negative finite number")
                rules[violation_type][field] = value
    return rules


__all__ = [
    "AgentIOError",
    "compile_feasibility_policy",
    "compile_global_objective",
    "compile_protected_metric_bounds",
    "extract_json",
    "parse_validate_compile_step",
    "parse_validate_compile_supervisor",
]
