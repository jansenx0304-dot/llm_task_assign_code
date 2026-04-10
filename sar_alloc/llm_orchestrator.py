from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .config import Budget, Config
from .console import info, json_block, kv, section, stop, subsection, text_block, warning
from .models import Instance
from .operators import WeightedALNSPolicy
from .prompts import get_next_action_prompt, get_objective_layer_prompt, get_system_prompt
from .schemas import NEXT_ACTION_SCHEMA, OBJECTIVE_LAYER_SCHEMA, SCHEMA_CONSTRAINTS
from .solution import AssignmentSolution
from .tools import (
    apply_objective,
    available_metrics,
    build_initial_solution,
    compare,
    compile_weighted_alns_policy,
    instance_summary,
    solve_assignment,
    solution_summary,
)
from .tools.llm_utils import format_available_metrics


DEFAULT_MAX_STAGNATION_STEPS = 3
DEFAULT_MAX_AGENT_STEPS = 6
MEANINGFUL_MIN_TIME_SEC = 0.25
MEANINGFUL_MIN_ITERS = 10
CANONICAL_METRIC_KEYS = (
    "violation_total",
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
)
RUN_ALNS_ACTION = "run_alns"


class LLMClientProtocol:
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:  # pragma: no cover
        raise NotImplementedError


@dataclass
class BudgetState:
    total: Dict[str, Optional[float]]
    used: Dict[str, float]
    remaining: Dict[str, Optional[float]]

    @classmethod
    def from_budget(cls, budget: Budget, max_solver_calls: int) -> "BudgetState":
        total = {
            "time_limit_sec": _as_optional_float(budget.time_limit_sec),
            "max_iters": _as_optional_float(budget.max_iters),
            "solver_calls": float(max_solver_calls),
        }
        used = {"time_limit_sec": 0.0, "max_iters": 0.0, "solver_calls": 0.0}
        return cls(total=total, used=used, remaining=dict(total))

    def can_run_solver(self) -> bool:
        if (self.remaining.get("solver_calls") or 0.0) <= 0:
            return False
        for key in ("time_limit_sec", "max_iters"):
            total = self.total.get(key)
            if total is not None and (self.remaining.get(key) or 0.0) <= 0:
                return False
        return True

    def clamp_request(self, budget_request: Dict[str, Any], default_request: Dict[str, Any]) -> Tuple[Budget, Dict[str, Any]]:
        request = _sanitize_budget_request(budget_request)
        defaults = _sanitize_budget_request(default_request)
        allocated: Dict[str, Any] = {}
        for key in ("time_limit_sec", "max_iters"):
            value = request.get(key, defaults.get(key, 1.0 if key == "time_limit_sec" else 60))
            remaining = self.remaining.get(key)
            if remaining is not None:
                value = min(float(value), float(remaining))
            allocated[key] = int(max(1, round(value))) if key == "max_iters" else float(max(1e-6, float(value)))
        return Budget(time_limit_sec=float(allocated["time_limit_sec"]), max_iters=int(allocated["max_iters"])), allocated

    def consume_solver_usage(self, actual_iters_used: int, actual_time_used_sec: float, solver_calls: int = 1) -> None:
        usage_deltas = {
            "solver_calls": float(_as_non_negative_int(solver_calls)),
            "max_iters": float(_as_non_negative_int(actual_iters_used)),
            "time_limit_sec": _as_non_negative_float(actual_time_used_sec),
        }
        for key, delta in usage_deltas.items():
            self.used[key] += delta
            total = self.total.get(key)
            if total is None:
                self.remaining[key] = None
                continue
            self.remaining[key] = max(0.0, float(total or 0.0) - self.used[key])

    def to_prompt_dict(self) -> Dict[str, Any]:
        return {"total_budget": _round_dict(self.total), "used_budget": _round_dict(self.used), "remaining_budget": _round_dict(self.remaining)}

    def to_compact_prompt_dict(self) -> Dict[str, Any]:
        return {
            "remaining_time_sec": _round_number(self.remaining.get("time_limit_sec")),
            "remaining_iters": _round_number(self.remaining.get("max_iters")),
            "remaining_solver_calls": _round_number(self.remaining.get("solver_calls")),
        }


@dataclass
class StepRecord:
    step_id: int
    action_type: str
    action_payload: Dict[str, Any]
    budget_request: Dict[str, Any]
    budget_allocated: Dict[str, Any]
    rationale: str
    compare_vs_incumbent: Optional[int]
    advanced_incumbent: bool
    lex_key_changed: bool
    stop: bool
    result_summary: str
    solver_diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    objective_layers: List[Dict[str, Any]]
    objective_from_llm: bool = False
    incumbent_solution: Optional[AssignmentSolution] = None
    incumbent_summary: Optional[Dict[str, Any]] = None
    previous_incumbent_summary: Optional[Dict[str, Any]] = None
    current_init_method: Optional[str] = None
    current_weighted_policy: Dict[str, Any] = field(default_factory=dict)
    history: List[StepRecord] = field(default_factory=list)
    consecutive_flat_steps: int = 0

    def search_state(self) -> Dict[str, Any]:
        last = self.history[-1] if self.history else None
        return {
            "step_count": len(self.history),
            "incumbent_exists": self.incumbent_summary is not None,
            "current_init_method": self.current_init_method,
            "current_weighted_policy": self.current_weighted_policy,
            "last_action": None if last is None else {
                "action_type": last.action_type,
                "action_payload": last.action_payload,
                "rationale": last.rationale,
            },
        }


def run_orchestrator(
    client: LLMClientProtocol,
    instance: Instance,
    user_goal_text: str,
    config: Optional[Config] = None,
    budget: Optional[Budget] = None,
    rng_seed: int = 0,
    max_agent_steps: Optional[int] = None,
    max_solver_calls: Optional[int] = None,
    max_stagnation_steps: int = DEFAULT_MAX_STAGNATION_STEPS,
) -> AssignmentSolution:
    cfg = config or Config()
    total_budget = budget or Budget()
    max_steps = _resolve_positive_int(max_agent_steps) or DEFAULT_MAX_AGENT_STEPS
    solver_calls = _resolve_positive_int(max_solver_calls) or max_steps

    objective_from_llm = _stage_build_objective(client, user_goal_text, cfg)
    inst_sum = instance_summary(instance=instance)
    budget_state = BudgetState.from_budget(total_budget, max_solver_calls=solver_calls)
    state = AgentState(
        objective_layers=_objective_layers_prompt_view(cfg.eval.objective_policy.layers),
        objective_from_llm=objective_from_llm,
    )

    step_id = 0
    while step_id < max_steps:
        if not budget_state.can_run_solver() and state.incumbent_solution is not None:
            stop(f"Hard stop before step {step_id}: solver budget exhausted.")
            break

        allowed_actions = _allowed_actions(state, budget_state)
        section(f"Agent Step {step_id}")

        action = _stage_decide_next_action(client, user_goal_text, inst_sum, state, budget_state, allowed_actions, cfg)
        record = _execute_action(action, state, budget_state, instance, cfg, rng_seed, step_id)
        state.history.append(record)

        subsection(f"Step {step_id} Result")
        kv("action", record.action_type)
        kv("rationale", record.rationale)
        kv("compare_vs_incumbent", record.compare_vs_incumbent)
        kv("advanced_incumbent", record.advanced_incumbent)
        kv("lex_key_changed", record.lex_key_changed)
        kv("stop", record.stop)
        kv("result", record.result_summary)

        if record.advanced_incumbent:
            state.consecutive_flat_steps = 0
        elif record.action_type != "stop":
            state.consecutive_flat_steps += 1
        if record.stop:
            break
        if state.consecutive_flat_steps >= max(1, int(max_stagnation_steps)):
            stop(f"Soft stop after step {step_id}: no forward movement for {state.consecutive_flat_steps} steps.")
            break
        step_id += 1

    if state.incumbent_solution is not None:
        return state.incumbent_solution
    warning("No incumbent solution produced by the agent loop. Falling back to a safe initial solution.")
    _log_algorithm_input_source(
        phase="build_initial_solution",
        objective_from_llm=state.objective_from_llm,
        action_from_llm=False,
    )
    return _safe_build_initial_solution("insert", instance, cfg, rng_seed)


def _stage_build_objective(client: LLMClientProtocol, user_goal_text: str, cfg: Config) -> bool:
    prompt = get_objective_layer_prompt(user_goal_text, format_available_metrics(available_metrics()), OBJECTIVE_LAYER_SCHEMA)
    text_block("Prompt", prompt)
    raw = _call_llm(client, get_system_prompt(), prompt)
    text_block("LLM Output", raw)
    parsed, parse_error = _parse_json_obj_with_reason(raw)
    if parse_error is not None:
        _log_llm_fallback("objective", "parse", parse_error)
        return False
    validation_error = _validate_objective_spec(parsed)
    if validation_error is not None:
        _log_llm_fallback("objective", "validation", validation_error)
        return False
    result = apply_objective(cfg, parsed)
    if not bool(result.get("ok", False)):
        _log_llm_fallback("objective", "validation", str(result.get("error", "invalid objective payload")))
        return False
    kv("objective_rationale", _sanitize_rationale(parsed.get("rationale"), fallback="No rationale provided."))
    return True


def _stage_decide_next_action(client: LLMClientProtocol, user_goal_text: str, inst_sum: Dict[str, Any], state: AgentState, budget_state: BudgetState, allowed_actions: List[str], cfg: Config) -> Dict[str, Any]:
    current_summary = _build_incumbent_metrics_summary(state.incumbent_summary)
    delta_summary = _build_delta_from_prev_incumbent(state.objective_layers, state.incumbent_summary, state.previous_incumbent_summary)
    progress_summary = _build_search_progress_summary(state)
    prompt = get_next_action_prompt(
        user_goal_text=user_goal_text,
        objective_layers=state.objective_layers,
        instance_summary=inst_sum,
        current_search_state=state.search_state(),
        current_incumbent_metrics=current_summary,
        delta_from_prev_incumbent=delta_summary,
        search_progress=progress_summary,
        remaining_budget=budget_state.to_compact_prompt_dict(),
        allowed_actions=allowed_actions,
        json_schema=NEXT_ACTION_SCHEMA,
    )
    text_block("Next Action Prompt", prompt)
    raw = _call_llm(client, get_system_prompt(), prompt)
    text_block("Next Action Output", raw)
    parsed, parse_error = _parse_json_obj_with_reason(raw)
    if parse_error is not None:
        _log_llm_fallback("action", "parse", parse_error)
        parsed = {}
        action_from_llm = False
    else:
        validation_error = _validate_action_spec(parsed, allowed_actions)
        action_from_llm = validation_error is None
        if validation_error is not None:
            _log_llm_fallback("action", "validation", validation_error)
    normalized = _normalize_action(parsed, allowed_actions, state, budget_state, cfg)
    normalized["_action_from_llm"] = action_from_llm
    return normalized


def _execute_action(action: Dict[str, Any], state: AgentState, budget_state: BudgetState, instance: Instance, cfg: Config, rng_seed: int, step_id: int) -> StepRecord:
    prev_solution = state.incumbent_solution
    prev_eval = getattr(prev_solution, "eval", None)
    action_type = str(action["action_type"]).strip()
    payload = dict(action.get("action_payload", {}))
    budget_request = dict(action.get("budget_request", {}))
    rationale = _sanitize_rationale(action.get("rationale"), fallback=_default_action_rationale(action_type))
    should_stop = False
    result_summary = "No action executed."
    budget_allocated: Dict[str, Any] = {}
    solver_diagnostics: Dict[str, Any] = {}
    actual_usage: Dict[str, Any] = {}
    new_solution: Optional[AssignmentSolution] = None

    if action_type == "stop":
        should_stop = True
        result_summary = "LLM chose stop."
    elif action_type == "build_initial_solution":
        _log_algorithm_input_source(
            phase="build_initial_solution",
            objective_from_llm=state.objective_from_llm,
            action_from_llm=bool(action.get("_action_from_llm", False)),
        )
        init_method = _sanitize_init_method(payload.get("init_method"))
        new_solution = _safe_build_initial_solution(init_method, instance, cfg, rng_seed + step_id)
        state.current_init_method = init_method
        state.current_weighted_policy = {}
        result_summary = f"Built incumbent solution with init_method={init_method}."
    elif action_type == RUN_ALNS_ACTION:
        policy = action.get("_compiled_policy")
        if not isinstance(policy, WeightedALNSPolicy):
            compiled = compile_weighted_alns_policy(cfg, payload)
            policy = compiled["policy"]
            payload = dict(compiled["applied"])
        init_solution = prev_solution
        prefix = ""
        if init_solution is None:
            fallback_init = _sanitize_init_method(state.current_init_method or "insert")
            _log_algorithm_input_source(
                phase="build_initial_solution",
                objective_from_llm=state.objective_from_llm,
                action_from_llm=bool(action.get("_action_from_llm", False)),
            )
            init_solution = _safe_build_initial_solution(fallback_init, instance, cfg, rng_seed + step_id)
            state.current_init_method = fallback_init
            prefix = f"Built fallback incumbent with init_method={fallback_init} before running weighted ALNS. "
        default_budget = {"time_limit_sec": cfg.solver.weighted_alns.default_time_limit_sec, "max_iters": cfg.solver.weighted_alns.default_max_iters}
        requested_budget = dict(budget_request)
        slice_budget, budget_allocated = budget_state.clamp_request(requested_budget, default_budget)
        _log_algorithm_input_source(
            phase=RUN_ALNS_ACTION,
            objective_from_llm=state.objective_from_llm,
            action_from_llm=bool(action.get("_action_from_llm", False)),
        )
        new_solution = solve_assignment(instance=instance, init_solution=init_solution, config=cfg, budget=slice_budget, policy=policy, rng_seed=rng_seed + step_id)
        solver_diagnostics = dict(getattr(new_solution, "solver_diagnostics", {}) or {})
        actual_iters_used, actual_time_used_sec = _extract_solver_actual_usage(solver_diagnostics)
        budget_state.consume_solver_usage(actual_iters_used=actual_iters_used, actual_time_used_sec=actual_time_used_sec, solver_calls=1)
        actual_usage = {
            "actual_time_used_sec": _round_number(actual_time_used_sec),
            "actual_iters_used": int(actual_iters_used),
            "solver_calls": 1,
        }
        _log_solver_budget(requested_budget, budget_allocated, actual_usage, budget_state)
        state.current_weighted_policy = policy.as_dict()
        result_summary = (
            f"{prefix}Executed weighted ALNS with {json.dumps(policy.as_dict(), ensure_ascii=True)}. "
            f"requested_budget={json.dumps(requested_budget, ensure_ascii=True)}, "
            f"granted_budget={json.dumps(budget_allocated, ensure_ascii=True)}, "
            f"actual_usage={json.dumps(actual_usage, ensure_ascii=True)}"
        )
    else:
        should_stop = True
        result_summary = f"Illegal action '{action_type}' after normalization. Stopped."

    compare_vs_incumbent: Optional[int] = None
    advanced = False
    lex_changed = False
    if new_solution is not None and getattr(new_solution, "eval", None) is not None:
        solver_diagnostics = dict(getattr(new_solution, "solver_diagnostics", {}) or {})
        new_summary = solution_summary(solution=new_solution, instance=instance, config=cfg)
        if prev_eval is None:
            compare_vs_incumbent = -1
            advanced = True
        else:
            compare_vs_incumbent = compare(new_solution.eval, prev_eval, cfg)
            advanced = compare_vs_incumbent < 0
            lex_changed = tuple(new_solution.eval.lex_key or ()) != tuple(prev_eval.lex_key or ())
        if prev_eval is None and getattr(new_solution.eval, "lex_key", None) is not None:
            lex_changed = True
        if advanced:
            state.previous_incumbent_summary = state.incumbent_summary
            state.incumbent_solution = new_solution
            state.incumbent_summary = new_summary
        result_summary = f"{result_summary} feasible={bool(new_summary.get('is_feasible', False))}, lex_key={new_summary.get('lex_key', [])}"
        if not advanced and prev_eval is not None:
            result_summary = f"{result_summary}, incumbent_kept=true"
        if solver_diagnostics:
            result_summary = f"{result_summary}, solver_diag={json.dumps(_condense_solver_diagnostics(solver_diagnostics), ensure_ascii=True)}"

    return StepRecord(step_id=step_id, action_type=action_type, action_payload=payload, budget_request=budget_request, budget_allocated=budget_allocated, rationale=rationale, compare_vs_incumbent=compare_vs_incumbent, advanced_incumbent=advanced, lex_key_changed=lex_changed, stop=should_stop, result_summary=result_summary, solver_diagnostics=solver_diagnostics)


def _allowed_actions(state: AgentState, budget_state: BudgetState) -> List[str]:
    if not budget_state.can_run_solver():
        return ["build_initial_solution", "stop"] if state.incumbent_solution is None else ["stop"]
    return ["build_initial_solution", "stop"] if state.incumbent_solution is None else [RUN_ALNS_ACTION, "stop"]


def _normalize_action(parsed: Dict[str, Any], allowed_actions: List[str], state: AgentState, budget_state: BudgetState, cfg: Config) -> Dict[str, Any]:
    fallback = "build_initial_solution" if state.incumbent_solution is None else (RUN_ALNS_ACTION if RUN_ALNS_ACTION in allowed_actions else "stop")
    raw_rationale = _sanitize_rationale(parsed.get("rationale") if isinstance(parsed, dict) else None)
    action_type = str(parsed.get("action_type", "")).strip() if isinstance(parsed, dict) else ""
    if action_type not in allowed_actions:
        warning(f"Illegal or missing action '{action_type}', fallback to '{fallback}'.")
        action_type = fallback
        raw_rationale = f"Fallback to '{fallback}' because the LLM response did not choose an allowed action."
    payload = parsed.get("action_payload", {}) if isinstance(parsed, dict) else {}
    payload = payload if isinstance(payload, dict) else {}
    compiled_policy: Optional[WeightedALNSPolicy] = None
    if action_type == "build_initial_solution":
        normalized_payload = {"init_method": _sanitize_init_method(payload.get("init_method"))}
    elif action_type == RUN_ALNS_ACTION:
        compiled = compile_weighted_alns_policy(cfg, payload)
        normalized_payload = dict(compiled["applied"])
        compiled_policy = compiled["policy"]
    else:
        normalized_payload = {}
    budget_request = _sanitize_budget_request(parsed.get("budget_request", {}) if isinstance(parsed, dict) else {})
    if action_type == RUN_ALNS_ACTION:
        budget_request = _ensure_run_alns_budget_request(budget_request, cfg)
    out = {
        "action_type": action_type,
        "action_payload": normalized_payload,
        "budget_request": budget_request,
        "rationale": raw_rationale or _default_action_rationale(action_type),
    }
    if compiled_policy is not None:
        out["_compiled_policy"] = compiled_policy
    return _enforce_action_guardrails(out, allowed_actions, state, budget_state, cfg)


def _enforce_action_guardrails(action: Dict[str, Any], allowed_actions: List[str], state: AgentState, budget_state: BudgetState, cfg: Config) -> Dict[str, Any]:
    guarded = dict(action)
    if state.incumbent_solution is None and "build_initial_solution" in allowed_actions and guarded.get("action_type") != "build_initial_solution":
        warning("No incumbent is available; forcing action_type='build_initial_solution'.")
        return {
            "action_type": "build_initial_solution",
            "action_payload": {"init_method": "insert"},
            "budget_request": guarded.get("budget_request", {}),
            "rationale": "Forced build_initial_solution because no incumbent is available yet.",
        }
    if guarded.get("action_type") == "stop" and not _should_allow_stop(state, budget_state):
        fallback = "build_initial_solution" if state.incumbent_solution is None else RUN_ALNS_ACTION
        warning(f"Stop rejected by guardrails; forcing action_type='{fallback}'.")
        if fallback == "build_initial_solution":
            return {
                "action_type": fallback,
                "action_payload": {"init_method": "insert"},
                "budget_request": guarded.get("budget_request", {}),
                "rationale": "Stop was rejected by guardrails, so the controller forced build_initial_solution.",
            }
        compiled = compile_weighted_alns_policy(cfg, {})
        return {
            "action_type": fallback,
            "action_payload": dict(compiled["applied"]),
            "budget_request": _ensure_run_alns_budget_request(guarded.get("budget_request", {}), cfg),
            "rationale": "Stop was rejected by guardrails, so the controller forced run_alns.",
            "_compiled_policy": compiled["policy"],
        }
    if guarded.get("action_type") == RUN_ALNS_ACTION:
        guarded["budget_request"] = _ensure_run_alns_budget_request(guarded.get("budget_request", {}), cfg)
    guarded["rationale"] = _sanitize_rationale(guarded.get("rationale"), fallback=_default_action_rationale(str(guarded.get("action_type", ""))))
    return guarded


def _safe_build_initial_solution(method: str, instance: Instance, cfg: Config, rng_seed: int) -> AssignmentSolution:
    safe_method = _sanitize_init_method(method)
    try:
        return build_initial_solution(method=safe_method, instance=instance, config=cfg, rng_seed=rng_seed)
    except Exception:
        if safe_method != "insert":
            warning(f"Init method '{safe_method}' failed; fallback to 'insert'.")
            return build_initial_solution(method="insert", instance=instance, config=cfg, rng_seed=rng_seed)
        raise


def _sanitize_init_method(value: Any) -> str:
    method = str(value or "insert").strip().lower()
    return method if method in ("insert", "sweep") else "insert"


def _objective_layers_prompt_view(layers: List[Any]) -> List[Dict[str, Any]]:
    return [{"index": i + 1, "name": str(getattr(layer, "name", f"layer_{i + 1}")), "metric": str(getattr(layer, "metric", "")), "direction": str(getattr(layer, "direction", "min"))} for i, layer in enumerate(layers)]


def _build_incumbent_metrics_summary(summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not summary:
        return {"exists": False, "is_feasible": None, "lex_key": [], "metrics": {key: None for key in CANONICAL_METRIC_KEYS}}
    metrics = dict(summary.get("metrics", {}) or {})
    return {"exists": True, "is_feasible": bool(summary.get("is_feasible", False)), "lex_key": list(summary.get("lex_key", []) or []), "metrics": {key: _round_number(float(metrics[key])) if key in metrics else None for key in CANONICAL_METRIC_KEYS}}


def _build_delta_from_prev_incumbent(objective_layers: List[Dict[str, Any]], current_summary: Optional[Dict[str, Any]], previous_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not current_summary or not previous_summary:
        return {"has_previous_incumbent": False, "advanced": False, "layer_deltas": [], "first_advanced_layer": None}
    current_metrics = dict(current_summary.get("metrics", {}) or {})
    previous_metrics = dict(previous_summary.get("metrics", {}) or {})
    deltas: List[float] = []
    first_advanced: Optional[int] = None
    advanced = False
    for layer in objective_layers:
        delta = round(_oriented_layer_value(layer, current_metrics) - _oriented_layer_value(layer, previous_metrics), 6)
        deltas.append(float(delta))
        if first_advanced is None and delta < 0:
            first_advanced = int(layer.get("index") or len(deltas))
            advanced = True
            break
        if delta > 0:
            break
    return {"has_previous_incumbent": True, "advanced": advanced, "layer_deltas": deltas, "first_advanced_layer": first_advanced}


def _build_search_progress_summary(state: AgentState) -> Dict[str, Any]:
    last = state.history[-1] if state.history else None
    last_solver = next((record for record in reversed(state.history) if record.solver_diagnostics), None)
    diag = _condense_solver_diagnostics(last_solver.solver_diagnostics) if last_solver else {}
    total_iters = float(diag.get("total_iters") or 0.0)
    plateau = float(diag.get("plateau_iters_after_last_update") or 0.0)
    return {
        "last_action": None if last is None else {
            "action_type": last.action_type,
            "action_payload": last.action_payload,
            "rationale": last.rationale,
        },
        "last_step_advanced_incumbent": None if last is None else bool(last.advanced_incumbent),
        "consecutive_flat_steps": int(state.consecutive_flat_steps),
        "recent_same_action_repeat": _count_recent_same_action_repeat(state.history),
        "best_update_count": int(diag.get("update_count") or 0),
        "plateau_iters": int(plateau),
        "plateau_ratio": round(plateau / total_iters, 4) if total_iters > 0 else 0.0,
    }


def _count_recent_same_action_repeat(history: List[StepRecord]) -> int:
    if not history:
        return 0
    sig = _action_signature(history[-1])
    count = 0
    for record in reversed(history):
        if _action_signature(record) != sig:
            break
        count += 1
    return count


def _action_signature(record: StepRecord) -> str:
    if record.action_type != RUN_ALNS_ACTION:
        return record.action_type
    payload = record.action_payload if isinstance(record.action_payload, dict) else {}
    return (
        f"{RUN_ALNS_ACTION}:"
        f"{_top_weight_name(payload.get('destroy_generator_priors', {}))}:"
        f"{_top_weight_name(payload.get('repair_task_selector_priors', {}))}"
    )


def _condense_solver_diagnostics(diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    update_iters = list(diagnostics.get("best_update_iters", []) or [])
    return {
        "algorithm": diagnostics.get("algorithm"),
        "total_iters": diagnostics.get("total_iters"),
        "actual_iters_used": diagnostics.get("actual_iters_used", diagnostics.get("total_iters")),
        "actual_time_used_sec": diagnostics.get("actual_time_used_sec"),
        "update_count": diagnostics.get("best_update_count"),
        "first_update_iter": diagnostics.get("first_best_iter"),
        "last_update_iter": diagnostics.get("last_best_iter"),
        "plateau_iters_after_last_update": diagnostics.get("plateau_iters_after_last_update"),
        "update_iters_preview": update_iters[:8],
        "last_acceptance_decision": dict(diagnostics.get("last_acceptance_decision", {}) or {}),
    }


def _top_weight_name(weights: Any) -> str:
    if not isinstance(weights, dict) or not weights:
        return ""
    return str(
        max(
            weights.items(),
            key=lambda item: (float(item[1]), str(item[0])),
        )[0]
    )


def _oriented_layer_value(layer: Dict[str, Any], metrics: Dict[str, Any]) -> float:
    value = float(metrics.get(str(layer.get("metric", "")), 0.0) or 0.0)
    return -value if str(layer.get("direction", "min")) == "max" else value


def _should_allow_stop(state: AgentState, budget_state: BudgetState) -> bool:
    if not budget_state.can_run_solver():
        return True
    if (budget_state.remaining.get("time_limit_sec") or 0.0) < MEANINGFUL_MIN_TIME_SEC:
        return True
    if (budget_state.remaining.get("max_iters") or 0.0) < MEANINGFUL_MIN_ITERS:
        return True
    if state.consecutive_flat_steps >= DEFAULT_MAX_STAGNATION_STEPS:
        return True
    return False


def _sanitize_budget_request(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    out: Dict[str, Any] = {}
    for key in ("time_limit_sec", "max_iters"):
        if key not in value:
            continue
        try:
            numeric = float(value[key])
        except Exception:
            continue
        if numeric <= 0:
            continue
        out[key] = int(max(1, round(numeric))) if key == "max_iters" else float(numeric)
    return out


def _ensure_run_alns_budget_request(budget_request: Dict[str, Any], cfg: Config) -> Dict[str, Any]:
    normalized = _sanitize_budget_request(budget_request)
    if "time_limit_sec" not in normalized:
        normalized["time_limit_sec"] = float(cfg.solver.weighted_alns.default_time_limit_sec)
    return normalized


def _call_llm(client: LLMClientProtocol, system_prompt: str, user_prompt: str) -> str:
    return client.chat([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])


def _log_llm_fallback(kind: str, failure_type: str, reason: str) -> None:
    detail = str(reason).strip() or "unknown error"
    warning(f"[LLM][{kind}] {failure_type} failed: {detail}, fallback to default")


def _log_algorithm_input_source(phase: str, objective_from_llm: bool, action_from_llm: bool) -> None:
    info(
        f"[LLM][algorithm_input] phase={phase}, "
        f"objective_from_llm={str(bool(objective_from_llm)).lower()}, "
        f"action_from_llm={str(bool(action_from_llm)).lower()}"
    )


def _log_solver_budget(
    requested_budget: Dict[str, Any],
    granted_budget: Dict[str, Any],
    actual_usage: Dict[str, Any],
    budget_state: BudgetState,
) -> None:
    json_block(
        "Solver Budget",
        {
            "requested": dict(requested_budget),
            "granted": dict(granted_budget),
            "actual": dict(actual_usage),
            "remaining_budget": _round_dict(budget_state.remaining),
        },
    )


def _extract_solver_actual_usage(diagnostics: Dict[str, Any]) -> Tuple[int, float]:
    actual_iters_used = _as_non_negative_int(diagnostics.get("actual_iters_used", diagnostics.get("total_iters", 0)))
    actual_time_used_sec = _as_non_negative_float(diagnostics.get("actual_time_used_sec", diagnostics.get("elapsed_sec", 0.0)))
    return actual_iters_used, actual_time_used_sec


def _validate_objective_spec(parsed: Dict[str, Any]) -> Optional[str]:
    unknown_top_level = sorted(str(key) for key in parsed.keys() if str(key) not in {"rationale", "layers"})
    if unknown_top_level:
        return f"unknown field '{unknown_top_level[0]}'"
    if "layers" not in parsed:
        return "missing field 'layers'"
    layers = parsed.get("layers")
    if not isinstance(layers, list):
        return "field 'layers' must be a list"
    if not layers:
        return "field 'layers' must be a non-empty list"

    allowed_metrics = {
        str(item.get("name", "")).strip()
        for item in (available_metrics().get("metrics", []) or [])
    }
    for index, layer in enumerate(layers):
        prefix = f"layers[{index}]"
        if not isinstance(layer, dict):
            return f"field '{prefix}' must be an object"
        unknown_layer_fields = sorted(str(key) for key in layer.keys() if str(key) not in {"name", "metric", "direction"})
        if unknown_layer_fields:
            return f"unknown field '{prefix}.{unknown_layer_fields[0]}'"
        for field_name in ("name", "metric", "direction"):
            if field_name not in layer:
                return f"missing field '{prefix}.{field_name}'"
        if not isinstance(layer.get("name"), str) or not str(layer.get("name")).strip():
            return f"field '{prefix}.name' must be a non-empty string"
        if not isinstance(layer.get("metric"), str) or not str(layer.get("metric")).strip():
            return f"field '{prefix}.metric' must be a non-empty string"
        metric = str(layer.get("metric")).strip()
        if metric not in allowed_metrics:
            return f"field '{prefix}.metric' has illegal enum value '{metric}'"
        direction = layer.get("direction")
        if not isinstance(direction, str):
            return f"field '{prefix}.direction' must be a string"
        if direction not in ("min", "max"):
            return f"field '{prefix}.direction' has illegal enum value '{direction}'"
    return None


def _validate_action_spec(parsed: Dict[str, Any], allowed_actions: List[str]) -> Optional[str]:
    unknown_top_level = sorted(str(key) for key in parsed.keys() if str(key) not in {"rationale", "action_type", "action_payload", "budget_request"})
    if unknown_top_level:
        return f"unknown field '{unknown_top_level[0]}'"
    allowed_action_types = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("action_type", []) or [])
    if "action_type" not in parsed:
        return "missing field 'action_type'"
    action_type = parsed.get("action_type")
    if not isinstance(action_type, str):
        return "field 'action_type' must be a string"
    action_type = action_type.strip()
    if action_type not in allowed_action_types:
        return f"field 'action_type' has illegal enum value '{action_type}'"
    if action_type not in allowed_actions:
        return f"field 'action_type' is not allowed in current state: '{action_type}'"

    if "action_payload" not in parsed:
        return "missing field 'action_payload'"
    payload = parsed.get("action_payload")
    if not isinstance(payload, dict):
        return "field 'action_payload' must be an object"

    budget_request = parsed.get("budget_request", {})
    if "budget_request" in parsed and not isinstance(budget_request, dict):
        return "field 'budget_request' must be an object"
    budget_error = _validate_budget_request_spec(budget_request, require_time_limit_sec=(action_type == RUN_ALNS_ACTION))
    if budget_error is not None:
        return budget_error

    if action_type == "build_initial_solution":
        unknown_payload_fields = sorted(str(key) for key in payload.keys() if str(key) not in {"init_method"})
        if unknown_payload_fields:
            return f"unknown field 'action_payload.{unknown_payload_fields[0]}'"
        if "init_method" not in payload:
            return "missing field 'action_payload.init_method'"
        init_method = payload.get("init_method")
        if not isinstance(init_method, str):
            return "field 'action_payload.init_method' must be a string"
        allowed_init_methods = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("init_method", []) or [])
        if init_method not in allowed_init_methods:
            return f"field 'action_payload.init_method' has illegal enum value '{init_method}'"
        return None

    if action_type == RUN_ALNS_ACTION:
        allowed_payload_fields = {
            "destroy_generator_priors",
            "repair_task_selector_priors",
            "repair_position_selector",
            "metric_weights",
            "strength_ratio",
            "acceptance",
            "accept_level",
            "reaction_factor",
            "prior_mix_lambda",
        }
        unknown_payload_fields = sorted(str(key) for key in payload.keys() if str(key) not in allowed_payload_fields)
        if unknown_payload_fields:
            return f"unknown field 'action_payload.{unknown_payload_fields[0]}'"
        for field_name in (
            "destroy_generator_priors",
            "repair_task_selector_priors",
            "repair_position_selector",
            "metric_weights",
            "strength_ratio",
            "acceptance",
            "accept_level",
            "reaction_factor",
            "prior_mix_lambda",
        ):
            if field_name not in payload:
                return f"missing field 'action_payload.{field_name}'"

        nested_error = _validate_required_number_map(
            payload=payload,
            field_name="destroy_generator_priors",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("destroy_generator_priors", []),
        )
        if nested_error is not None:
            return nested_error
        nested_error = _validate_required_number_map(
            payload=payload,
            field_name="repair_task_selector_priors",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("repair_task_selector_priors", []),
        )
        if nested_error is not None:
            return nested_error
        nested_error = _validate_required_number_map(
            payload=payload,
            field_name="metric_weights",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("metric_fields", []),
        )
        if nested_error is not None:
            return nested_error

        repair_position_selector = payload.get("repair_position_selector")
        if not isinstance(repair_position_selector, str):
            return "field 'action_payload.repair_position_selector' must be a string"
        allowed_repair_position = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("repair_position_selector", []) or [])
        if repair_position_selector not in allowed_repair_position:
            return f"field 'action_payload.repair_position_selector' has illegal enum value '{repair_position_selector}'"

        acceptance = payload.get("acceptance")
        if not isinstance(acceptance, str):
            return "field 'action_payload.acceptance' must be a string"
        allowed_acceptance = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("acceptance", []) or [])
        if acceptance not in allowed_acceptance:
            return f"field 'action_payload.acceptance' has illegal enum value '{acceptance}'"

        for field_name in ("strength_ratio", "accept_level", "reaction_factor", "prior_mix_lambda"):
            if not _is_plain_number(payload.get(field_name)):
                return f"field 'action_payload.{field_name}' must be numeric"
        return None
    if payload:
        first_key = sorted(str(key) for key in payload.keys())[0]
        return f"unknown field 'action_payload.{first_key}'"
    return None


def _validate_required_number_map(payload: Dict[str, Any], field_name: str, required_keys: List[str]) -> Optional[str]:
    raw = payload.get(field_name)
    if not isinstance(raw, dict):
        return f"field 'action_payload.{field_name}' must be an object"
    allowed_keys = {str(key) for key in required_keys}
    unknown_keys = sorted(str(key) for key in raw.keys() if str(key) not in allowed_keys)
    if unknown_keys:
        return f"unknown field 'action_payload.{field_name}.{unknown_keys[0]}'"
    for key in required_keys:
        if key not in raw:
            return f"missing field 'action_payload.{field_name}.{key}'"
        if not _is_plain_number(raw.get(key)):
            return f"field 'action_payload.{field_name}.{key}' must be numeric"
    return None


def _validate_budget_request_spec(budget_request: Dict[str, Any], require_time_limit_sec: bool = False) -> Optional[str]:
    unknown_fields = sorted(str(key) for key in budget_request.keys() if str(key) not in {"time_limit_sec", "max_iters"})
    if unknown_fields:
        return f"unknown field 'budget_request.{unknown_fields[0]}'"
    if require_time_limit_sec and "time_limit_sec" not in budget_request:
        return "missing field 'budget_request.time_limit_sec'"
    for key in ("time_limit_sec", "max_iters"):
        if key not in budget_request:
            continue
        value = budget_request.get(key)
        if not _is_plain_number(value):
            return f"field 'budget_request.{key}' must be numeric"
        if float(value) <= 0:
            return f"field 'budget_request.{key}' must be positive"
    return None


def _is_plain_number(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    try:
        float(value)
    except Exception:
        return False
    return True


def _parse_json_obj(text: str, default: Dict[str, Any]) -> Dict[str, Any]:
    parsed, error = _parse_json_obj_with_reason(text)
    return parsed if error is None else default


def _parse_json_obj_with_reason(text: str) -> Tuple[Dict[str, Any], Optional[str]]:
    if not text:
        return {}, "empty response"
    primary_error: Optional[str] = None
    try:
        obj = json.loads(text.strip())
        if isinstance(obj, dict):
            return obj, None
        primary_error = f"top-level JSON must be an object, got {type(obj).__name__}"
    except Exception as exc:
        primary_error = f"{type(exc).__name__}: {exc}"
    match = re.search(r"\{.*\}", str(text), flags=re.DOTALL)
    if not match:
        return {}, primary_error or "no JSON object found"
    try:
        obj = json.loads(match.group(0))
    except Exception as exc:
        return {}, primary_error or f"{type(exc).__name__}: {exc}"
    if not isinstance(obj, dict):
        return {}, f"top-level JSON must be an object, got {type(obj).__name__}"
    return obj, None


def _round_number(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if abs(float(value) - round(float(value))) < 1e-9:
        return float(round(float(value)))
    return round(float(value), 4)


def _round_dict(data: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    return {key: _round_number(value) for key, value in data.items()}


def _sanitize_rationale(value: Any, fallback: str = "") -> str:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        if normalized:
            return normalized
    return fallback


def _default_action_rationale(action_type: str) -> str:
    normalized = str(action_type).strip()
    if normalized == "build_initial_solution":
        return "Build an initial incumbent because no incumbent is available yet."
    if normalized == RUN_ALNS_ACTION:
        return "Run weighted ALNS to improve the incumbent under the remaining budget."
    if normalized == "stop":
        return "Stop because the remaining budget or recent progress is not enough for a meaningful next step."
    return "No rationale provided."


def _as_optional_float(value: Any) -> Optional[float]:
    try:
        return None if value is None else float(value)
    except Exception:
        return None


def _as_non_negative_float(value: Any) -> float:
    try:
        numeric = float(value)
    except Exception:
        return 0.0
    return max(0.0, numeric)


def _as_non_negative_int(value: Any) -> int:
    try:
        numeric = int(value)
    except Exception:
        return 0
    return max(0, numeric)


def _resolve_positive_int(value: Any) -> Optional[int]:
    try:
        numeric = int(value)
    except Exception:
        return None
    return numeric if numeric > 0 else None
