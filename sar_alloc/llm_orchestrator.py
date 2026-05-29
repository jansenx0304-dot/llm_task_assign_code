from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import Budget, Config
from .console import stop, warning
from .demo_policy import (
    demo_build_initial_action,
    demo_objective_plan,
    demo_run_alns_action,
    demo_stop_action,
)
from .models import Instance
from .operators.destroy import build_destroy_landscape
from .operators.repair import build_repair_landscape
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
from .tools.llm_utils import (
    format_available_metrics,
    llm_parse_operator_intent as parse_operator_intent,
)


DEFAULT_MAX_STAGNATION_STEPS = 3
DEFAULT_MAX_AGENT_STEPS = 6
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


class OrchestratorError(RuntimeError):
    """Raised when the LLM-driven orchestration cannot proceed safely."""


class LLMOutputError(ValueError):
    """Raised when an LLM response is not strict JSON or fails schema checks."""


@dataclass
class OrchestratorRuntime:
    allow_llm_fallback: bool = False
    artifact_dir: Optional[Path] = None
    llm_fallback_used: bool = False
    llm_fallback_reasons: List[str] = field(default_factory=list)
    objective_prompt: str = ""
    objective_raw_text: str = ""
    objective_plan: Dict[str, Any] = field(default_factory=dict)
    objective_from_llm: bool = False

    def use_fallback(self, stage: str, reason: str) -> None:
        self.llm_fallback_used = True
        detail = f"{stage}: {reason}"
        self.llm_fallback_reasons.append(detail)
        warning("LLM fallback has been used.")
        warning(f"LLM fallback reason: {detail}")


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

    def clamp_request(self, budget_request: Dict[str, Any]) -> Tuple[Budget, Dict[str, Any]]:
        allocated: Dict[str, Any] = {}
        time_value = float(budget_request["time_limit_sec"])
        remaining_time = self.remaining.get("time_limit_sec")
        if remaining_time is not None:
            time_value = min(time_value, float(remaining_time))
        allocated["time_limit_sec"] = float(max(1e-6, time_value))

        max_iters: Optional[int] = None
        if "max_iters" in budget_request:
            max_iters = int(budget_request["max_iters"])
        elif self.remaining.get("max_iters") is not None:
            max_iters = int(max(1, round(float(self.remaining["max_iters"] or 0.0))))
        if max_iters is not None:
            remaining_iters = self.remaining.get("max_iters")
            if remaining_iters is not None:
                max_iters = min(max_iters, int(max(1, round(float(remaining_iters)))))
            allocated["max_iters"] = int(max(1, max_iters))
        else:
            allocated["max_iters"] = None

        return Budget(time_limit_sec=allocated["time_limit_sec"], max_iters=max_iters), allocated

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
    action_from_llm: bool
    llm_prompt: str
    llm_raw_text: str
    strict_action_plan: Dict[str, Any]
    compiled_policy: Dict[str, Any]
    operator_intent: Optional[Dict[str, str]]
    action_payload: Dict[str, Any]
    budget_request: Dict[str, Any]
    budget_allocated: Dict[str, Any]
    rationale: str
    compare_vs_incumbent: Optional[int]
    advanced_incumbent: bool
    lex_key_changed: bool
    stop: bool
    result_summary: str
    candidate_summary: Optional[Dict[str, Any]] = None
    incumbent_summary_after: Optional[Dict[str, Any]] = None
    decision_context: Dict[str, Any] = field(default_factory=dict)
    solver_request_summary: Dict[str, Any] = field(default_factory=dict)
    solver_result_summary: Dict[str, Any] = field(default_factory=dict)
    solver_diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    objective_layers: List[Dict[str, Any]]
    objective_from_llm: bool = False
    incumbent_solution: Optional[AssignmentSolution] = None
    incumbent_summary: Optional[Dict[str, Any]] = None
    previous_incumbent_summary: Optional[Dict[str, Any]] = None
    current_weighted_policy: Dict[str, Any] = field(default_factory=dict)
    history: List[StepRecord] = field(default_factory=list)
    consecutive_flat_steps: int = 0

    def search_state(self) -> Dict[str, Any]:
        last = self.history[-1] if self.history else None
        return {
            "step_count": len(self.history),
            "incumbent_exists": self.incumbent_summary is not None,
            "current_weighted_policy": self.current_weighted_policy,
            "last_action": None if last is None else {
                "action_type": last.action_type,
                "operator_intent": last.operator_intent,
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
    allow_llm_fallback: bool = False,
    artifact_dir: Optional[Path] = None,
) -> AssignmentSolution:
    """Run the LLM-controlled optimization loop.

    The orchestrator asks the LLM for an objective plan, then for one action per
    step. In real mode, malformed or incomplete LLM output raises immediately
    unless `allow_llm_fallback` is explicitly enabled by the caller.
    """
    cfg = config or Config()
    total_budget = budget or Budget()
    max_steps = _resolve_positive_int(max_agent_steps) or DEFAULT_MAX_AGENT_STEPS
    solver_calls = _resolve_positive_int(max_solver_calls) or max_steps
    runtime = OrchestratorRuntime(
        allow_llm_fallback=bool(allow_llm_fallback),
        artifact_dir=artifact_dir,
    )
    orchestrator_t0 = time.time()

    objective_from_llm = _stage_build_objective(client, user_goal_text, cfg, runtime)
    inst_sum = instance_summary(instance=instance)
    budget_state = BudgetState.from_budget(total_budget, max_solver_calls=solver_calls)
    state = AgentState(
        objective_layers=_objective_layers_prompt_view(cfg.eval.objective_policy.layers),
        objective_from_llm=objective_from_llm,
    )
    print(
        f"[AGENT] max_steps={max_steps} solver_calls={solver_calls} "
        f"max_stagnation={max_stagnation_steps}"
    )

    step_id = 0
    while step_id < max_steps:
        if not budget_state.can_run_solver() and state.incumbent_solution is not None:
            stop(f"Hard stop before step {step_id}: solver budget exhausted.")
            break

        allowed_actions = _allowed_actions(state, budget_state)
        action = _stage_decide_next_action(client, user_goal_text, inst_sum, state, budget_state, allowed_actions, instance, cfg, runtime, step_id)
        _log_step_action(step_id, action)
        record = _execute_action(action, state, budget_state, instance, cfg, rng_seed, step_id, runtime)
        state.history.append(record)

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
        return _finalize_run_solution(state.incumbent_solution, state, budget_state, orchestrator_t0, runtime)
    raise OrchestratorError(
        "No incumbent solution was produced. The LLM action sequence stopped "
        "before a solution-building action completed."
    )


def _finalize_run_solution(
    solution: AssignmentSolution,
    state: AgentState,
    budget_state: BudgetState,
    started_at: float,
    runtime: OrchestratorRuntime,
) -> AssignmentSolution:
    run_summary = _build_run_summary(state, budget_state, started_at, runtime)
    solution.run_summary = run_summary
    solution.run_artifact = _build_run_artifact_core(state, budget_state, runtime, run_summary)
    return solution


def _build_run_summary(state: AgentState, budget_state: BudgetState, started_at: float, runtime: OrchestratorRuntime) -> Dict[str, Any]:
    solver_records = [record for record in state.history if record.solver_diagnostics]
    best_update_count = sum(_as_non_negative_int(record.solver_diagnostics.get("best_update_count", 0)) for record in solver_records)
    return {
        "orchestrator_elapsed_sec": _round_number(max(0.0, time.time() - started_at)),
        "total_solver_time_sec": _round_number(budget_state.used.get("time_limit_sec", 0.0)),
        "total_solver_iters": _as_non_negative_int(budget_state.used.get("max_iters", 0)),
        "total_solver_calls": _as_non_negative_int(budget_state.used.get("solver_calls", 0)),
        "agent_steps_executed": len(state.history),
        "alns_steps_executed": len(solver_records),
        "best_update_count": best_update_count,
        "final_action": state.history[-1].action_type if state.history else None,
        "remaining_budget": _round_dict(budget_state.remaining),
        "objective_tiers": list(state.objective_layers),
        "llm_fallback_used": bool(runtime.llm_fallback_used),
        "llm_fallback_reasons": list(runtime.llm_fallback_reasons),
    }


def _build_run_artifact_core(
    state: AgentState,
    budget_state: BudgetState,
    runtime: OrchestratorRuntime,
    run_summary: Dict[str, Any],
) -> Dict[str, Any]:
    solver_records = [record for record in state.history if record.solver_diagnostics]
    last_solver = solver_records[-1].solver_diagnostics if solver_records else {}
    return {
        "objective": {
            "llm_prompt": runtime.objective_prompt,
            "llm_raw_text": runtime.objective_raw_text,
            "strict_objective_plan": dict(runtime.objective_plan),
            "from_llm": bool(runtime.objective_from_llm),
        },
        "llm_steps": [_llm_step_artifact(record) for record in state.history],
        "iteration_trace": _collect_iteration_trace(solver_records),
        "operator_statistics": {
            "destroy_operator_summary": dict(last_solver.get("destroy_operator_summary", {}) or {}),
            "repair_operator_summary": dict(last_solver.get("repair_operator_summary", {}) or {}),
            "operator_weights": dict(last_solver.get("operator_weights", {}) or {}),
        },
        "diagnostics": {
            "run_summary": dict(run_summary),
            "budget": budget_state.to_prompt_dict(),
            "llm_fallback_used": bool(runtime.llm_fallback_used),
            "llm_fallback_reasons": list(runtime.llm_fallback_reasons),
            "last_solver": _condense_solver_diagnostics(last_solver),
        },
    }


def _llm_step_artifact(record: StepRecord) -> Dict[str, Any]:
    return {
        "step": int(record.step_id),
        "action_type": record.action_type,
        "llm_prompt": record.llm_prompt,
        "llm_raw_text": record.llm_raw_text,
        "strict_action_plan": dict(record.strict_action_plan),
        "compiled_policy": dict(record.compiled_policy),
        "decision_context": dict(record.decision_context),
        "solver_request_summary": dict(record.solver_request_summary),
        "solver_result_summary": dict(record.solver_result_summary),
    }


def _collect_iteration_trace(records: List[StepRecord]) -> List[Dict[str, Any]]:
    trace: List[Dict[str, Any]] = []
    for record in records:
        for item in list(record.solver_diagnostics.get("iteration_trace", []) or []):
            if isinstance(item, dict):
                current = dict(item)
                current["agent_step"] = int(record.step_id)
                trace.append(current)
    return trace


def _stage_build_objective(
    client: LLMClientProtocol,
    user_goal_text: str,
    cfg: Config,
    runtime: OrchestratorRuntime,
) -> bool:
    prompt = get_objective_layer_prompt(user_goal_text, format_available_metrics(available_metrics()), OBJECTIVE_LAYER_SCHEMA)
    runtime.objective_prompt = prompt
    try:
        raw = _call_llm(client, get_system_prompt(), prompt)
    except Exception as exc:
        if not runtime.allow_llm_fallback:
            raise
        runtime.use_fallback("objective_call", str(exc))
        runtime.objective_raw_text = f"LLM call failed: {exc}"
        parsed = demo_objective_plan()
        objective_from_llm = False
        runtime.objective_plan = dict(parsed)
        runtime.objective_from_llm = False
        result = apply_objective(cfg, parsed)
        if not bool(result.get("ok", False)):
            raise LLMOutputError(str(result.get("error", "invalid objective payload")))
        _log_active_objective(cfg, objective_from_llm=False, rationale=_sanitize_rationale(parsed.get("rationale")))
        return False
    runtime.objective_raw_text = raw
    try:
        parsed = parse_objective_plan(raw)
        objective_from_llm = True
    except LLMOutputError as exc:
        if not runtime.allow_llm_fallback:
            raise
        runtime.use_fallback("objective", str(exc))
        parsed = demo_objective_plan()
        objective_from_llm = False

    result = apply_objective(cfg, parsed)
    if not bool(result.get("ok", False)):
        raise LLMOutputError(str(result.get("error", "invalid objective payload")))
    runtime.objective_plan = dict(parsed)
    runtime.objective_from_llm = bool(objective_from_llm)
    _log_active_objective(
        cfg,
        objective_from_llm=objective_from_llm,
        rationale=_sanitize_rationale(parsed.get("rationale")),
    )
    return objective_from_llm


def _stage_decide_next_action(
    client: LLMClientProtocol,
    user_goal_text: str,
    inst_sum: Dict[str, Any],
    state: AgentState,
    budget_state: BudgetState,
    allowed_actions: List[str],
    instance: Instance,
    cfg: Config,
    runtime: OrchestratorRuntime,
    step_id: int,
) -> Dict[str, Any]:
    current_summary = _build_incumbent_metrics_summary(state.incumbent_summary)
    delta_summary = _build_delta_from_prev_incumbent(state.objective_layers, state.incumbent_summary, state.previous_incumbent_summary)
    progress_summary = _build_search_progress_summary(state)
    last_destroy_summary = _last_destroy_operator_summary(state)
    recent_repair_summary = _last_repair_summary(state)
    destroy_landscape = build_destroy_landscape(
        state.incumbent_solution,
        instance,
        cfg,
        strength_ratio=_current_strength_ratio(state),
        recent_destroy_summary=last_destroy_summary,
    )
    repair_landscape = build_repair_landscape(
        state.incumbent_solution,
        instance,
        cfg,
        recent_repair_summary=recent_repair_summary,
    )
    decision_context = _decision_context_log_view(
        state=state,
        allowed_actions=allowed_actions,
        current_summary=current_summary,
        delta_summary=delta_summary,
        progress_summary=progress_summary,
        destroy_landscape=destroy_landscape,
        repair_landscape=repair_landscape,
        budget_state=budget_state,
    )
    prompt = get_next_action_prompt(
        user_goal_text=user_goal_text,
        objective_layers=state.objective_layers,
        instance_summary=inst_sum,
        current_search_state=state.search_state(),
        current_incumbent_metrics=current_summary,
        delta_from_prev_incumbent=delta_summary,
        search_progress=progress_summary,
        destroy_landscape=destroy_landscape,
        remaining_budget=budget_state.to_compact_prompt_dict(),
        allowed_actions=allowed_actions,
        json_schema=NEXT_ACTION_SCHEMA,
        repair_landscape=repair_landscape,
    )
    try:
        raw = _call_llm(client, get_system_prompt(), prompt)
    except Exception as exc:
        if not runtime.allow_llm_fallback:
            raise
        runtime.use_fallback("action_call", str(exc))
        action = _demo_action_for_state(state, budget_state, allowed_actions)
        action = _prepare_action_plan(action, allowed_actions)
        action["_action_from_llm"] = False
        action["_llm_prompt"] = prompt
        action["_llm_raw_text"] = f"LLM call failed: {exc}"
        action["_decision_context"] = decision_context
        return action
    try:
        action = parse_action_plan(raw, allowed_actions)
        action_from_llm = True
    except LLMOutputError as exc:
        if not runtime.allow_llm_fallback:
            raise
        runtime.use_fallback("action", str(exc))
        action = _demo_action_for_state(state, budget_state, allowed_actions)
        action = _prepare_action_plan(action, allowed_actions)
        action_from_llm = False

    action["_action_from_llm"] = action_from_llm
    action["_llm_prompt"] = prompt
    action["_llm_raw_text"] = raw
    action["_decision_context"] = decision_context
    return action


def _log_active_objective(cfg: Config, *, objective_from_llm: bool, rationale: str = "") -> None:
    del rationale
    print(
        f"[OBJ] from_llm={_bool_text(objective_from_llm)} "
        f"layers={_format_objective_layers(_objective_layers_prompt_view(cfg.eval.objective_policy.layers))}"
    )


def parse_objective_plan(raw_text: str) -> Dict[str, Any]:
    """Parse and validate the LLM objective-plan JSON.

    Args:
        raw_text: Raw text returned by the LLM.

    Returns:
        A validated objective plan dictionary using the current project schema.

    Raises:
        LLMOutputError: If the text is not strict JSON, is not an object, has
            missing/unknown fields, or references illegal metrics/directions.
    """
    parsed = _parse_strict_json_object(raw_text, "objective")
    validation_error = _validate_objective_spec(parsed)
    if validation_error is not None:
        raise LLMOutputError(f"Invalid objective plan: {validation_error}")
    return parsed


def parse_action_plan(raw_text: str, allowed_actions: List[str]) -> Dict[str, Any]:
    """Parse, validate, and compile an LLM action-plan JSON object.

    Args:
        raw_text: Raw text returned by the LLM.
        allowed_actions: Action names allowed in the current orchestrator state.

    Returns:
        A normalized action dictionary. `run_alns` actions include the compiled
        `WeightedALNSPolicy` under `_compiled_policy`.

    Raises:
        LLMOutputError: If JSON parsing, schema validation, or policy
            compilation fails.
    """
    parsed = _parse_strict_json_object(raw_text, "action")
    return _prepare_action_plan(parsed, allowed_actions)


def _prepare_action_plan(parsed: Dict[str, Any], allowed_actions: List[str]) -> Dict[str, Any]:
    validation_error = _validate_action_spec(parsed, allowed_actions)
    if validation_error is not None:
        raise LLMOutputError(f"Invalid action plan: {validation_error}")

    action_type = str(parsed["action_type"]).strip()
    payload = dict(parsed["action_payload"])
    budget_request = dict(parsed["budget_request"])
    operator_intent = _parse_operator_intent_from_action(parsed)
    if operator_intent is None:
        raise LLMOutputError("Invalid action plan: operator_intent failed validation")
    strict_action_plan = {
        "rationale": _sanitize_rationale(parsed.get("rationale")),
        "operator_intent": dict(parsed.get("operator_intent", {}) or {}),
        "action_type": action_type,
        "action_payload": dict(payload),
        "budget_request": dict(budget_request),
    }

    normalized: Dict[str, Any] = {
        "action_type": action_type,
        "operator_intent": operator_intent,
        "action_payload": dict(payload),
        "budget_request": budget_request,
        "rationale": _sanitize_rationale(parsed.get("rationale")),
        "_strict_action_plan": strict_action_plan,
    }

    if action_type == RUN_ALNS_ACTION:
        compiled = compile_weighted_alns_policy(payload)
        if not bool(compiled.get("ok", False)):
            raise LLMOutputError(
                f"Invalid action plan: {compiled.get('error', 'invalid run_alns policy')}"
            )
        normalized["_compiled_policy"] = compiled["policy"]
        normalized["_compiled_policy_dict"] = dict(compiled["applied"])
    return normalized


def _decision_context_log_view(
    *,
    state: AgentState,
    allowed_actions: List[str],
    current_summary: Dict[str, Any],
    delta_summary: Dict[str, Any],
    progress_summary: Dict[str, Any],
    destroy_landscape: Dict[str, Any],
    repair_landscape: Dict[str, Any],
    budget_state: BudgetState,
) -> Dict[str, Any]:
    return {
        "step_count": len(state.history),
        "allowed_actions": list(allowed_actions),
        "current_search_state": state.search_state(),
        "current_incumbent_metrics": current_summary,
        "delta_from_prev_incumbent": delta_summary,
        "search_progress": progress_summary,
        "destroy_landscape": destroy_landscape,
        "repair_landscape": repair_landscape,
        "remaining_budget": budget_state.to_compact_prompt_dict(),
    }


def _step_result_log_view(record: StepRecord, budget_state: BudgetState) -> Dict[str, Any]:
    return {
        "step_id": int(record.step_id),
        "action_type": record.action_type,
        "action_from_llm": bool(record.action_from_llm),
        "llm_raw_text": record.llm_raw_text,
        "strict_action_plan": dict(record.strict_action_plan),
        "compiled_policy": dict(record.compiled_policy),
        "operator_intent": record.operator_intent,
        "rationale": record.rationale,
        "action_payload": record.action_payload,
        "budget_request": record.budget_request,
        "budget_allocated": record.budget_allocated,
        "solver_request_summary": dict(record.solver_request_summary),
        "solver_result_summary": dict(record.solver_result_summary),
        "compare_vs_incumbent": record.compare_vs_incumbent,
        "advanced_incumbent": bool(record.advanced_incumbent),
        "lex_key_changed": bool(record.lex_key_changed),
        "stop": bool(record.stop),
        "candidate_summary": _compact_solution_summary(record.candidate_summary),
        "incumbent_summary_after": _compact_solution_summary(record.incumbent_summary_after),
        "solver_diagnostics": _condense_solver_diagnostics(record.solver_diagnostics),
        "remaining_budget": _round_dict(budget_state.remaining),
        "result_summary": record.result_summary,
    }


def _execute_action(
    action: Dict[str, Any],
    state: AgentState,
    budget_state: BudgetState,
    instance: Instance,
    cfg: Config,
    rng_seed: int,
    step_id: int,
    runtime: OrchestratorRuntime,
) -> StepRecord:
    prev_solution = state.incumbent_solution
    prev_eval = getattr(prev_solution, "eval", None)
    action_type = str(action["action_type"]).strip()
    action_from_llm = bool(action.get("_action_from_llm", False))
    llm_prompt = str(action.get("_llm_prompt", "") or "")
    llm_raw_text = str(action.get("_llm_raw_text", "") or "")
    strict_action_plan = dict(action.get("_strict_action_plan", {}) or {})
    compiled_policy = dict(action.get("_compiled_policy_dict", {}) or {})
    decision_context = dict(action.get("_decision_context", {}) or {})
    operator_intent = _parse_operator_intent_from_action(action)
    payload = dict(action.get("action_payload", {}))
    budget_request = dict(action.get("budget_request", {}))
    rationale = _sanitize_rationale(action.get("rationale"))
    should_stop = False
    result_summary = "No action executed."
    budget_allocated: Dict[str, Any] = {}
    solver_diagnostics: Dict[str, Any] = {}
    actual_usage: Dict[str, Any] = {}
    solver_request_summary: Dict[str, Any] = {}
    solver_result_summary: Dict[str, Any] = {}
    new_solution: Optional[AssignmentSolution] = None
    candidate_summary: Optional[Dict[str, Any]] = None
    incumbent_summary_after = state.incumbent_summary

    if action_type == "stop":
        should_stop = True
        result_summary = "Controller requested stop."
    elif action_type == "build_initial_solution":
        _log_algorithm_input_source(
            phase="build_initial_solution",
            objective_from_llm=state.objective_from_llm,
            action_from_llm=action_from_llm,
        )
        payload = {}
        new_solution = build_initial_solution(instance=instance, config=cfg, rng_seed=rng_seed + step_id)
        state.current_weighted_policy = {}
        result_summary = "Built initial incumbent."
    elif action_type == RUN_ALNS_ACTION:
        policy = action["_compiled_policy"]
        init_solution = prev_solution
        prefix = ""
        requested_budget = dict(budget_request)
        slice_budget, budget_allocated = budget_state.clamp_request(requested_budget)
        _log_algorithm_input_source(
            phase=RUN_ALNS_ACTION,
            objective_from_llm=state.objective_from_llm,
            action_from_llm=action_from_llm,
        )
        solver_request = {
            "operator_intent": operator_intent,
            "policy": payload,
            "requested_budget": dict(requested_budget),
            "granted_budget": dict(budget_allocated),
        }
        solver_request_summary = dict(solver_request)
        _log_solver_request(
            requested_budget=dict(requested_budget),
            granted_budget=dict(budget_allocated),
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
        solver_result_summary = {
            "actual_usage": dict(actual_usage),
            "diagnostics": _condense_solver_diagnostics(solver_diagnostics),
        }
        _log_solver_budget(requested_budget, budget_allocated, actual_usage, budget_state)
        state.current_weighted_policy = policy.as_dict()
        result_summary = f"{prefix}Executed weighted ALNS."
    else:
        should_stop = True
        result_summary = f"Illegal action '{action_type}' after normalization. Stopped."

    compare_vs_incumbent: Optional[int] = None
    advanced = False
    lex_changed = False
    if new_solution is not None and getattr(new_solution, "eval", None) is not None:
        solver_diagnostics = dict(getattr(new_solution, "solver_diagnostics", {}) or {})
        new_summary = solution_summary(solution=new_solution, instance=instance, config=cfg)
        candidate_summary = new_summary
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
        incumbent_summary_after = state.incumbent_summary
        result_summary = (
            f"{result_summary} candidate_feasible={bool(new_summary.get('is_feasible', False))}, "
            f"candidate_lex_key={new_summary.get('lex_key', [])}"
        )
        if not advanced and prev_eval is not None:
            result_summary = f"{result_summary}, incumbent_kept=true"
        if not solver_result_summary:
            solver_result_summary = {
                "candidate_summary": _compact_solution_summary(candidate_summary),
            }
    else:
        incumbent_summary_after = state.incumbent_summary

    return StepRecord(
        step_id=step_id,
        action_type=action_type,
        action_from_llm=action_from_llm,
        llm_prompt=llm_prompt,
        llm_raw_text=llm_raw_text,
        strict_action_plan=strict_action_plan,
        compiled_policy=compiled_policy,
        operator_intent=operator_intent,
        action_payload=payload,
        budget_request=budget_request,
        budget_allocated=budget_allocated,
        rationale=rationale,
        compare_vs_incumbent=compare_vs_incumbent,
        advanced_incumbent=advanced,
        lex_key_changed=lex_changed,
        stop=should_stop,
        result_summary=result_summary,
        candidate_summary=candidate_summary,
        incumbent_summary_after=incumbent_summary_after,
        decision_context=decision_context,
        solver_request_summary=solver_request_summary,
        solver_result_summary=solver_result_summary,
        solver_diagnostics=solver_diagnostics,
    )


def _allowed_actions(state: AgentState, budget_state: BudgetState) -> List[str]:
    if not budget_state.can_run_solver():
        return ["build_initial_solution", "stop"] if state.incumbent_solution is None else ["stop"]
    return ["build_initial_solution", "stop"] if state.incumbent_solution is None else [RUN_ALNS_ACTION, "stop"]


def _demo_action_for_state(
    state: AgentState,
    budget_state: BudgetState,
    allowed_actions: List[str],
) -> Dict[str, Any]:
    if state.incumbent_solution is None and "build_initial_solution" in allowed_actions:
        return demo_build_initial_action()
    if RUN_ALNS_ACTION in allowed_actions and budget_state.can_run_solver():
        remaining_time = budget_state.remaining.get("time_limit_sec")
        remaining_iters = budget_state.remaining.get("max_iters")
        time_limit = 1.0 if remaining_time is None else max(1e-6, min(1.0, float(remaining_time)))
        max_iters = None if remaining_iters is None else max(1, min(60, int(remaining_iters)))
        return demo_run_alns_action(time_limit_sec=time_limit, max_iters=max_iters)
    return demo_stop_action()


def _objective_layers_prompt_view(layers: List[Any]) -> List[Dict[str, Any]]:
    return [
        {
            "name": str(layer.name),
            "metric": str(layer.metric),
            "direction": str(layer.direction),
        }
        for layer in layers
    ]


def _build_incumbent_metrics_summary(summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not summary:
        return {"exists": False, "is_feasible": None, "lex_key": [], "metrics": {key: None for key in CANONICAL_METRIC_KEYS}}
    metrics = dict(summary.get("metrics", {}) or {})
    return {"exists": True, "is_feasible": bool(summary.get("is_feasible", False)), "lex_key": list(summary.get("lex_key", []) or []), "metrics": {key: _round_number(float(metrics[key])) if key in metrics else None for key in CANONICAL_METRIC_KEYS}}


def _compact_solution_summary(summary: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not summary:
        return None
    metrics = dict(summary.get("metrics", {}) or {})
    return {
        "is_feasible": bool(summary.get("is_feasible", False)),
        "lex_key": list(summary.get("lex_key", []) or []),
        "metrics": {
            key: _round_number(float(metrics[key])) if key in metrics else None
            for key in CANONICAL_METRIC_KEYS
        },
    }


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
            first_advanced = len(deltas)
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
            "operator_intent": last.operator_intent,
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


def _current_strength_ratio(state: AgentState) -> float:
    policy = dict(state.current_weighted_policy or {})
    try:
        value = float(policy.get("strength_ratio", 0.15))
    except Exception:
        return 0.15
    return value if value > 0 else 0.15


def _last_destroy_operator_summary(state: AgentState) -> Dict[str, Any]:
    last_solver = next((record for record in reversed(state.history) if record.solver_diagnostics), None)
    if last_solver is None:
        return {}
    summary = last_solver.solver_diagnostics.get("destroy_operator_summary", {})
    return dict(summary) if isinstance(summary, dict) else {}


def _last_repair_summary(state: AgentState) -> Dict[str, Any]:
    last_solver = next((record for record in reversed(state.history) if record.solver_diagnostics), None)
    if last_solver is None:
        return {}
    summary = last_solver.solver_diagnostics.get("last_repair", {})
    return dict(summary) if isinstance(summary, dict) else {}


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
        f"{_top_weight_name(payload.get('destroy_operator_scores', {}))}:"
        f"{_top_weight_name(payload.get('repair_operator_scores', {}))}"
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
        "last_destroy_move": dict(diagnostics.get("last_destroy_move", {}) or {}),
        "last_repair": dict(diagnostics.get("last_repair", {}) or {}),
        "destroy_operator_summary": dict(diagnostics.get("destroy_operator_summary", {}) or {}),
        "repair_operator_summary": dict(diagnostics.get("repair_operator_summary", {}) or {}),
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


def _call_llm(client: LLMClientProtocol, system_prompt: str, user_prompt: str) -> str:
    return client.chat([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])


def _log_algorithm_input_source(phase: str, objective_from_llm: bool, action_from_llm: bool) -> None:
    del phase, objective_from_llm, action_from_llm


def _log_step_action(step_id: int, action: Dict[str, Any]) -> None:
    action_type = str(action.get("action_type", "")).strip()
    parts = [
        f"[STEP {int(step_id)}]",
        f"action={action_type}",
        f"from_llm={_bool_text(action.get('_action_from_llm', False))}",
    ]
    budget_request = dict(action.get("budget_request", {}) or {})
    if action_type == RUN_ALNS_ACTION:
        if "time_limit_sec" in budget_request:
            parts.append(f"time={_round_number(float(budget_request['time_limit_sec']))}")
        if "max_iters" in budget_request:
            parts.append(f"iters={int(budget_request['max_iters'])}")
    print(" ".join(parts))


def _log_solver_request(requested_budget: Dict[str, Any], granted_budget: Dict[str, Any]) -> None:
    print(
        "[SOLVER] "
        f"requested_time={_round_number(_as_optional_float(requested_budget.get('time_limit_sec')))} "
        f"granted_time={_round_number(_as_optional_float(granted_budget.get('time_limit_sec')))} "
        f"requested_iters={_format_optional_int(requested_budget.get('max_iters'))} "
        f"granted_iters={_format_optional_int(granted_budget.get('max_iters'))}"
    )


def _log_solver_budget(
    requested_budget: Dict[str, Any],
    granted_budget: Dict[str, Any],
    actual_usage: Dict[str, Any],
    budget_state: BudgetState,
) -> None:
    del requested_budget, granted_budget
    print(
        "[BUDGET] "
        f"actual_time={actual_usage.get('actual_time_used_sec')} "
        f"actual_iters={actual_usage.get('actual_iters_used')} "
        f"remaining_time={_round_number(budget_state.remaining.get('time_limit_sec'))} "
        f"remaining_iters={_round_number(budget_state.remaining.get('max_iters'))} "
        f"remaining_solver_calls={_round_number(budget_state.remaining.get('solver_calls'))}"
    )


def _extract_solver_actual_usage(diagnostics: Dict[str, Any]) -> Tuple[int, float]:
    actual_iters_used = _as_non_negative_int(diagnostics.get("actual_iters_used", diagnostics.get("total_iters", 0)))
    actual_time_used_sec = _as_non_negative_float(diagnostics.get("actual_time_used_sec", diagnostics.get("elapsed_sec", 0.0)))
    return actual_iters_used, actual_time_used_sec


def _validate_objective_spec(parsed: Dict[str, Any]) -> Optional[str]:
    unknown_top_level = sorted(str(key) for key in parsed.keys() if str(key) not in {"rationale", "layers"})
    if unknown_top_level:
        return f"unknown field '{unknown_top_level[0]}'"
    if "rationale" not in parsed:
        return "missing field 'rationale'"
    if not isinstance(parsed.get("rationale"), str) or not str(parsed.get("rationale")).strip():
        return "field 'rationale' must be a non-empty string"
    if "layers" not in parsed:
        return "missing field 'layers'"
    layers = parsed.get("layers")
    if not isinstance(layers, list):
        return "field 'layers' must be a list"
    if not layers:
        return "field 'layers' must be a non-empty list"
    if len(layers) > 6:
        return "field 'layers' must contain at most 6 layers"

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
    first = layers[0]
    if first.get("metric") != "violation_total" or first.get("direction") != "min":
        return "first objective layer must be violation_total with direction min"
    return None


def _validate_action_spec(parsed: Dict[str, Any], allowed_actions: List[str]) -> Optional[str]:
    unknown_top_level = sorted(
        str(key)
        for key in parsed.keys()
        if str(key) not in {"rationale", "operator_intent", "action_type", "action_payload", "budget_request"}
    )
    if unknown_top_level:
        return f"unknown field '{unknown_top_level[0]}'"
    if "rationale" not in parsed:
        return "missing field 'rationale'"
    if not isinstance(parsed.get("rationale"), str) or not str(parsed.get("rationale")).strip():
        return "field 'rationale' must be a non-empty string"
    operator_intent_error = _validate_required_short_phrase_map(
        parsed=parsed,
        field_name="operator_intent",
        required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("operator_intent_fields", []),
        max_words=int(SCHEMA_CONSTRAINTS.get("next_action", {}).get("operator_intent_max_words", 12) or 12),
    )
    if operator_intent_error is not None:
        return operator_intent_error
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

    if "budget_request" not in parsed:
        return "missing field 'budget_request'"
    budget_request = parsed.get("budget_request")
    if not isinstance(budget_request, dict):
        return "field 'budget_request' must be an object"
    budget_error = _validate_budget_request_spec(budget_request, require_time_limit_sec=(action_type == RUN_ALNS_ACTION))
    if budget_error is not None:
        return budget_error

    if action_type == "build_initial_solution":
        unknown_payload_fields = sorted(str(key) for key in payload.keys())
        if unknown_payload_fields:
            return f"unknown field 'action_payload.{unknown_payload_fields[0]}'"
        return None

    if action_type == RUN_ALNS_ACTION:
        allowed_payload_fields = {
            "search_diagnosis_scores",
            "destroy_operator_scores",
            "repair_operator_scores",
            "destroy_metric_preferences",
            "repair_task_metric_preferences",
            "repair_position_metric_preferences",
            "destroy_strength_score",
            "candidate_budget_score",
            "exploration_score",
            "acceptance",
            "accept_level",
            "reaction_factor",
            "prior_mix_lambda",
        }
        unknown_payload_fields = sorted(str(key) for key in payload.keys() if str(key) not in allowed_payload_fields)
        if unknown_payload_fields:
            return f"unknown field 'action_payload.{unknown_payload_fields[0]}'"
        for field_name in (
            "search_diagnosis_scores",
            "destroy_operator_scores",
            "repair_operator_scores",
            "destroy_metric_preferences",
            "repair_task_metric_preferences",
            "repair_position_metric_preferences",
            "destroy_strength_score",
            "candidate_budget_score",
            "exploration_score",
            "acceptance",
            "accept_level",
            "reaction_factor",
            "prior_mix_lambda",
        ):
            if field_name not in payload:
                return f"missing field 'action_payload.{field_name}'"

        nested_error = _validate_required_int_score_map(
            payload=payload,
            field_name="search_diagnosis_scores",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("search_diagnosis_scores", []),
        )
        if nested_error is not None:
            return nested_error
        nested_error = _validate_required_int_score_map(
            payload=payload,
            field_name="destroy_operator_scores",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("destroy_operator_scores", []),
        )
        if nested_error is not None:
            return nested_error
        nested_error = _validate_required_int_score_map(
            payload=payload,
            field_name="repair_operator_scores",
            required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get("repair_operator_scores", []),
        )
        if nested_error is not None:
            return nested_error
        for field_name, metric_key in (
            ("destroy_metric_preferences", "landscape_metric_fields"),
            ("repair_task_metric_preferences", "landscape_metric_fields"),
            ("repair_position_metric_preferences", "repair_position_metric_fields"),
        ):
            nested_error = _validate_metric_preferences(
                payload=payload,
                field_name=field_name,
                required_keys=SCHEMA_CONSTRAINTS.get("next_action", {}).get(metric_key, []),
            )
            if nested_error is not None:
                return nested_error

        acceptance = payload.get("acceptance")
        if not isinstance(acceptance, str):
            return "field 'action_payload.acceptance' must be a string"
        allowed_acceptance = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("acceptance", []) or [])
        if acceptance not in allowed_acceptance:
            return f"field 'action_payload.acceptance' has illegal enum value '{acceptance}'"

        for field_name in ("destroy_strength_score", "candidate_budget_score", "exploration_score"):
            if not _is_plain_int(payload.get(field_name)):
                return f"field 'action_payload.{field_name}' must be an integer"
            if int(payload.get(field_name)) < 0 or int(payload.get(field_name)) > 10:
                return f"field 'action_payload.{field_name}' must be in [0, 10]"
        for field_name in ("accept_level", "reaction_factor", "prior_mix_lambda"):
            if not _is_plain_number(payload.get(field_name)):
                return f"field 'action_payload.{field_name}' must be numeric"
        return None
    if payload:
        first_key = sorted(str(key) for key in payload.keys())[0]
        return f"unknown field 'action_payload.{first_key}'"
    return None


def _validate_required_int_score_map(payload: Dict[str, Any], field_name: str, required_keys: List[str]) -> Optional[str]:
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
        if not _is_plain_int(raw.get(key)):
            return f"field 'action_payload.{field_name}.{key}' must be an integer"
        if int(raw.get(key)) < 0 or int(raw.get(key)) > 10:
            return f"field 'action_payload.{field_name}.{key}' must be in [0, 10]"
    return None


def _validate_metric_preferences(payload: Dict[str, Any], field_name: str, required_keys: List[str]) -> Optional[str]:
    raw = payload.get(field_name)
    if not isinstance(raw, dict):
        return f"field 'action_payload.{field_name}' must be an object"
    allowed_keys = {str(key) for key in required_keys}
    unknown_keys = sorted(str(key) for key in raw.keys() if str(key) not in allowed_keys)
    if unknown_keys:
        return f"unknown field 'action_payload.{field_name}.{unknown_keys[0]}'"
    directions = tuple(SCHEMA_CONSTRAINTS.get("next_action", {}).get("metric_directions", []) or [])
    for key in required_keys:
        if key not in raw:
            return f"missing field 'action_payload.{field_name}.{key}'"
        item = raw.get(key)
        if not isinstance(item, dict):
            return f"field 'action_payload.{field_name}.{key}' must be an object"
        unknown_item = sorted(str(name) for name in item.keys() if str(name) not in {"score", "direction"})
        if unknown_item:
            return f"unknown field 'action_payload.{field_name}.{key}.{unknown_item[0]}'"
        for child in ("score", "direction"):
            if child not in item:
                return f"missing field 'action_payload.{field_name}.{key}.{child}'"
        if not _is_plain_int(item.get("score")):
            return f"field 'action_payload.{field_name}.{key}.score' must be an integer"
        if int(item.get("score")) < 0 or int(item.get("score")) > 10:
            return f"field 'action_payload.{field_name}.{key}.score' must be in [0, 10]"
        direction = item.get("direction")
        if not isinstance(direction, str):
            return f"field 'action_payload.{field_name}.{key}.direction' must be a string"
        if direction not in directions:
            return f"field 'action_payload.{field_name}.{key}.direction' has illegal enum value '{direction}'"
    return None


def _validate_required_short_phrase_map(
    *,
    parsed: Dict[str, Any],
    field_name: str,
    required_keys: List[str],
    max_words: int,
) -> Optional[str]:
    raw = parsed.get(field_name)
    if raw is None:
        return f"missing field '{field_name}'"
    if not isinstance(raw, dict):
        return f"field '{field_name}' must be an object"
    allowed_keys = {str(key) for key in required_keys}
    unknown_keys = sorted(str(key) for key in raw.keys() if str(key) not in allowed_keys)
    if unknown_keys:
        return f"unknown field '{field_name}.{unknown_keys[0]}'"
    for key in required_keys:
        if key not in raw:
            return f"missing field '{field_name}.{key}'"
        value = raw.get(key)
        if not isinstance(value, str):
            return f"field '{field_name}.{key}' must be a string"
        normalized = " ".join(value.strip().split())
        if not normalized:
            return f"field '{field_name}.{key}' must be a non-empty string"
        if len(normalized.split()) > int(max_words):
            return f"field '{field_name}.{key}' must be at most {int(max_words)} words"
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
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return True


def _is_plain_int(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int)


def _parse_strict_json_object(text: str, kind: str) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise LLMOutputError(f"{kind} response is empty")
    try:
        obj = json.loads(text.strip())
    except json.JSONDecodeError as exc:
        raise LLMOutputError(f"{kind} response is not valid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise LLMOutputError(
            f"{kind} response must be a JSON object, got {type(obj).__name__}"
        )
    return obj


def _round_number(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if abs(float(value) - round(float(value))) < 1e-9:
        return float(round(float(value)))
    return round(float(value), 4)


def _round_dict(data: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    return {key: _round_number(value) for key, value in data.items()}


def _bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def _format_optional_int(value: Any) -> str:
    if value is None:
        return "None"
    return str(_as_non_negative_int(value))


def _format_objective_layers(layers: List[Dict[str, Any]]) -> str:
    return " > ".join(str(layer.get("metric", "")) for layer in layers)


def _action_log_view(action: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(action, dict):
        return {}
    return {
        "action_type": action.get("action_type"),
        "operator_intent": action.get("operator_intent"),
        "action_payload": action.get("action_payload"),
        "budget_request": action.get("budget_request"),
        "rationale": action.get("rationale"),
    }


def _action_summary_log_view(action: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(action, dict):
        return {}
    return {
        "action_type": action.get("action_type"),
        "operator_intent": action.get("operator_intent"),
        "rationale": action.get("rationale"),
    }


def _parse_operator_intent_from_action(action: Dict[str, Any]) -> Optional[Dict[str, str]]:
    if not isinstance(action, dict):
        return None
    parsed = parse_operator_intent(action.get("operator_intent"))
    if bool(parsed.get("ok", False)):
        return dict(parsed.get("applied", {}))
    if action.get("operator_intent") is not None:
        warning(f"Invalid operator_intent after validation: {parsed.get('error', 'unknown error')}")
    return None


def _sanitize_rationale(value: Any, fallback: str = "") -> str:
    if isinstance(value, str):
        normalized = " ".join(value.strip().split())
        if normalized:
            return normalized
    return fallback


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
