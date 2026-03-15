# sar_alloc/llm_orchestrator.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .config import Budget, Config
from .console import json_block, kv, section, stop, subsection, text_block, warning
from .models import Instance
from .prompts import (
    get_next_action_prompt,
    get_objective_layer_prompt,
    get_system_prompt,
)
from .schemas import NEXT_ACTION_SCHEMA, OBJECTIVE_LAYER_SCHEMA
from .solution import AssignmentSolution
from .tools import (
    apply_objective,
    apply_solver_params,
    available_metrics,
    build_initial_solution,
    compare,
    instance_summary,
    solution_summary,
    solve_assignment,
)
from .tools.llm_utils import (
    format_available_metrics,
    format_instance_summary,
    format_objective_layers_text,
)

DEFAULT_HISTORY_WINDOW = 3
DEFAULT_MAX_NO_IMPROVE = 3
DEFAULT_MAX_AGENT_STEPS = 6
DEFAULT_SOLVER_MAX_ITERS = 60
DEFAULT_SOLVER_TIME_SEC = 1.0
DEFAULT_MODE_STRENGTH = "medium"
MEANINGFUL_MIN_TIME_SEC = 0.25
MEANINGFUL_MIN_ITERS = 10
INTENSIFY_STALL_THRESHOLD = 2
STRONG_MIN_TIME_SEC = DEFAULT_SOLVER_TIME_SEC
STRONG_MIN_ITERS = DEFAULT_SOLVER_MAX_ITERS


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
        used = {
            "time_limit_sec": 0.0,
            "max_iters": 0.0,
            "solver_calls": 0.0,
        }
        remaining = dict(total)
        return cls(total=total, used=used, remaining=remaining)

    def exhausted(self) -> bool:
        if (self.remaining.get("solver_calls") or 0.0) <= 0:
            return True
        for key in ("time_limit_sec", "max_iters"):
            total = self.total.get(key)
            if total is not None and (self.remaining.get(key) or 0.0) <= 0:
                return True
        return False

    def can_run_solver(self) -> bool:
        return not self.exhausted()

    def clamp_request(
        self,
        budget_request: Dict[str, Any],
        default_request: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Budget, Dict[str, Any]]:
        request = _sanitize_budget_request(budget_request)
        defaults = _sanitize_budget_request(default_request or {})
        allocated: Dict[str, Any] = {}

        for key in ("time_limit_sec", "max_iters"):
            requested = request.get(key)
            remaining = self.remaining.get(key)
            default_value = defaults.get(key, self._default_for_key(key, remaining))

            if requested is None:
                value = default_value
            else:
                value = requested

            if remaining is not None:
                value = min(float(value), float(remaining))

            if key == "max_iters":
                value = int(max(1, round(float(value))))
            else:
                value = float(max(1e-6, float(value)))

            allocated[key] = value

        if allocated["max_iters"] <= 0:
            allocated["max_iters"] = 1

        slice_budget = Budget(
            time_limit_sec=float(allocated["time_limit_sec"]),
            max_iters=int(allocated["max_iters"]),
        )
        return slice_budget, allocated

    def consume_solver_slice(self, slice_budget: Budget) -> None:
        self.used["solver_calls"] += 1.0
        self.remaining["solver_calls"] = max(0.0, (self.total["solver_calls"] or 0.0) - self.used["solver_calls"])

        for key, value in (
            ("time_limit_sec", slice_budget.time_limit_sec),
            ("max_iters", slice_budget.max_iters),
        ):
            if value is None:
                continue
            self.used[key] += float(value)
            if self.total.get(key) is not None:
                self.remaining[key] = max(0.0, float(self.total[key] or 0.0) - self.used[key])
            else:
                self.remaining[key] = None

    def to_prompt_dict(self) -> Dict[str, Any]:
        return {
            "total_budget": _round_budget_dict(self.total),
            "used_budget": _round_budget_dict(self.used),
            "remaining_budget": _round_budget_dict(self.remaining),
        }

    def to_compact_prompt_dict(self) -> Dict[str, Any]:
        return {
            "remaining_time_sec": _round_number(self.remaining.get("time_limit_sec")),
            "remaining_iters": _round_number(self.remaining.get("max_iters")),
            "remaining_solver_calls": _round_number(self.remaining.get("solver_calls")),
        }

    def _default_for_key(self, key: str, remaining: Optional[float]) -> float:
        if key == "time_limit_sec":
            base = DEFAULT_SOLVER_TIME_SEC
        elif key == "max_iters":
            base = float(DEFAULT_SOLVER_MAX_ITERS)
        else:
            base = float(DEFAULT_SOLVER_MAX_ITERS)

        if remaining is None:
            return base
        return max(1.0, min(base, float(remaining)))


@dataclass
class StepRecord:
    step_id: int
    action_type: str
    action_payload: Dict[str, Any]
    budget_request: Dict[str, Any]
    budget_allocated: Dict[str, Any]
    compare_vs_previous_current: Optional[int]
    compare_vs_previous_best: Optional[int]
    improved_current: bool
    improved_best: bool
    lex_key_changed: bool
    stop: bool
    result_summary: str
    solver_diagnostics: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    expected_effect: str = ""
    step_lex_key: List[float] = field(default_factory=list)
    step_feasible: Optional[bool] = None

    def prompt_view(self) -> Dict[str, Any]:
        view = {
            "step": self.step_id,
            "action": self.action_type,
            "payload": self.action_payload,
            "improved": self.improved_best,
            "lex": self.step_lex_key,
        }
        if self.step_feasible is not None:
            view["feasible"] = self.step_feasible
        if self.budget_request:
            view["budget"] = self.budget_request
        if self.stop:
            view["stop"] = True
        if self.solver_diagnostics:
            diag = _condense_solver_diagnostics(self.solver_diagnostics)
            view["diag"] = {
                "best_updates": diag.get("best_update_count"),
                "plateau_iters": diag.get("plateau_iters_after_last_improve"),
            }
        return view


@dataclass
class AgentState:
    objective_layers_text: str
    current_solution: Optional[AssignmentSolution] = None
    best_solution: Optional[AssignmentSolution] = None
    current_solution_summary_dict: Optional[Dict[str, Any]] = None
    best_solution_summary_dict: Optional[Dict[str, Any]] = None
    current_init_method: Optional[str] = None
    current_solver_alg: Optional[str] = None
    current_solver_params: Dict[str, Any] = field(default_factory=dict)
    history: List[StepRecord] = field(default_factory=list)
    consecutive_no_improve: int = 0

    def recent_history_text(self, limit: int = DEFAULT_HISTORY_WINDOW) -> str:
        if not self.history:
            return "No prior steps."
        records = [record.prompt_view() for record in self.history[-limit:]]
        return json.dumps(records, ensure_ascii=True, indent=2)

    def state_snapshot_text(self) -> str:
        current = self._summary_snapshot(self.current_solution_summary_dict)
        best = self._summary_snapshot(self.best_solution_summary_dict)
        is_current_best = bool(current and best and current == best)
        last_action = None
        if self.history:
            last_record = self.history[-1]
            last_action = {
                "action_type": last_record.action_type,
                "mode_strength": _extract_mode_strength(last_record.action_payload),
                "improved_best": last_record.improved_best,
            }
        return json.dumps(
            {
                "current": current,
                "best": best,
                "is_current_best": is_current_best,
                "search": {
                    "init_method": self.current_init_method,
                    "consecutive_no_improve": self.consecutive_no_improve,
                    "last_action": last_action,
                },
            },
            ensure_ascii=True,
            indent=2,
        )

    @staticmethod
    def _summary_snapshot(summary: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not summary:
            return None
        lex = summary.get("lex_key", []) or []
        return {
            "feasible": bool(summary.get("is_feasible", False)),
            "lex": [float(x) for x in lex],
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
    max_no_improve: int = DEFAULT_MAX_NO_IMPROVE,
) -> AssignmentSolution:
    max_steps = _resolve_max_agent_steps(max_agent_steps=max_agent_steps)
    solver_calls = _resolve_positive_int(max_solver_calls)
    if solver_calls is None:
        solver_calls = max_steps
    return run_agent_orchestrator(
        client=client,
        instance=instance,
        user_goal_text=user_goal_text,
        config=config,
        budget=budget,
        rng_seed=rng_seed,
        max_agent_steps=max_steps,
        max_solver_calls=solver_calls,
        max_no_improve=max(1, int(max_no_improve)),
    )


def run_agent_orchestrator(
    client: LLMClientProtocol,
    instance: Instance,
    user_goal_text: str,
    config: Optional[Config] = None,
    budget: Optional[Budget] = None,
    rng_seed: int = 0,
    max_agent_steps: int = DEFAULT_MAX_AGENT_STEPS,
    max_solver_calls: Optional[int] = None,
    max_no_improve: int = DEFAULT_MAX_NO_IMPROVE,
) -> AssignmentSolution:
    cfg = config or Config()
    total_budget = budget or Budget()
    max_agent_steps = _resolve_positive_int(max_agent_steps) or DEFAULT_MAX_AGENT_STEPS
    max_solver_calls = _resolve_positive_int(max_solver_calls)
    if max_solver_calls is None:
        max_solver_calls = max_agent_steps

    _stage_build_objective(client, user_goal_text, cfg)

    inst_sum = instance_summary(instance=instance)
    budget_state = BudgetState.from_budget(total_budget, max_solver_calls=max_solver_calls)
    state = AgentState(
        objective_layers_text=format_objective_layers_text(cfg.eval.objective_policy.layers),
    )

    step_id = 0
    while step_id < max_agent_steps:
        stop_reason = _stop_reason_before_step(state, budget_state)
        if stop_reason is not None:
            stop(f"Hard stop before step {step_id}: {stop_reason}.")
            break

        allowed_actions = _allowed_actions(state, budget_state)
        observe_dict = {
            "step_id": step_id,
            "allowed_actions": allowed_actions,
            "budget_state": budget_state.to_prompt_dict(),
            "current_solver_context": {
                "init_method": state.current_init_method,
                "solver_alg": state.current_solver_alg,
                "solver_params": state.current_solver_params,
                "consecutive_no_improve": state.consecutive_no_improve,
            },
        }
        section(f"Agent Step {step_id}", icon="🤖")
        json_block("Observation", observe_dict, icon="👀")

        action = _stage_decide_next_action(
            client=client,
            user_goal_text=user_goal_text,
            inst_summary=inst_sum,
            state=state,
            budget_state=budget_state,
            allowed_actions=allowed_actions,
        )

        step_record = _execute_action(
            action=action,
            state=state,
            budget_state=budget_state,
            instance=instance,
            cfg=cfg,
            rng_seed=rng_seed,
            step_id=step_id,
        )
        state.history.append(step_record)

        subsection(f"Step {step_id} Result", icon="🧠")
        kv("action", step_record.action_type, icon="🎬")
        kv("compare_vs_current", step_record.compare_vs_previous_current, icon="📊")
        kv("compare_vs_best", step_record.compare_vs_previous_best, icon="🏆")
        kv("improved_current", step_record.improved_current, icon="📈")
        kv("improved_best", step_record.improved_best, icon="🌟")
        kv("lex_key_changed", step_record.lex_key_changed, icon="🔑")
        kv("stop", step_record.stop, icon="🛑")
        kv("result", step_record.result_summary, icon="📝")

        if step_record.improved_best:
            state.consecutive_no_improve = 0
        elif step_record.action_type != "stop":
            state.consecutive_no_improve += 1

        if step_record.stop:
            break
        if state.consecutive_no_improve >= max_no_improve:
            stop(f"Soft stop after step {step_id}: no improvement for {state.consecutive_no_improve} steps.")
            break

        step_id += 1

    if state.best_solution is not None:
        return state.best_solution

    warning("No best solution produced by agent loop. Falling back to a safe initial solution.")
    fallback = _safe_build_initial_solution(
        method="insert",
        instance=instance,
        cfg=cfg,
        rng_seed=rng_seed,
    )
    return fallback


def _stage_build_objective(client: LLMClientProtocol, user_goal_text: str, cfg: Config) -> None:
    avail = available_metrics()
    sys = get_system_prompt()
    prompt = get_objective_layer_prompt(
        user_goal_text=user_goal_text,
        available_metrics=format_available_metrics(avail),
        json_schema=OBJECTIVE_LAYER_SCHEMA,
    )

    section("Objective Layer", icon="🎯")
    text_block("Prompt", prompt, icon="🧾")
    raw = _call_llm(client, sys, prompt)
    text_block("LLM Output", raw, icon="📤")

    obj = _parse_json_obj(raw, default={"layers": []})
    apply_objective(cfg, obj)


def _stage_decide_next_action(
    client: LLMClientProtocol,
    user_goal_text: str,
    inst_summary: Dict[str, Any],
    state: AgentState,
    budget_state: BudgetState,
    allowed_actions: List[str],
) -> Dict[str, Any]:
    sys = get_system_prompt()
    prompt = get_next_action_prompt(
        user_goal_text=user_goal_text,
        instance_summary=format_instance_summary(inst_summary),
        state_snapshot=state.state_snapshot_text(),
        budget_state=json.dumps(budget_state.to_compact_prompt_dict(), ensure_ascii=True, indent=2),
        recent_history=state.recent_history_text(),
        objective_layers=state.objective_layers_text,
        allowed_actions=allowed_actions,
        json_schema=NEXT_ACTION_SCHEMA,
    )

    text_block("Next Action Prompt", prompt, icon="🧾")
    raw = _call_llm(client, sys, prompt)
    text_block("Next Action Output", raw, icon="📤")

    parsed = _parse_json_obj(raw, default={})
    return _normalize_action(parsed, allowed_actions, state, budget_state)


def _execute_action(
    action: Dict[str, Any],
    state: AgentState,
    budget_state: BudgetState,
    instance: Instance,
    cfg: Config,
    rng_seed: int,
    step_id: int,
) -> StepRecord:
    previous_current = state.current_solution
    previous_best = state.best_solution
    previous_current_eval = getattr(previous_current, "eval", None)
    previous_best_eval = getattr(previous_best, "eval", None)

    action_type = str(action["action_type"])
    payload = dict(action.get("action_payload", {}))
    budget_request = dict(action.get("budget_request", {}))
    rationale = str(action.get("rationale", ""))
    expected_effect = str(action.get("expected_effect", ""))

    compare_vs_previous_current: Optional[int] = None
    compare_vs_previous_best: Optional[int] = None
    improved_current = False
    improved_best = False
    lex_key_changed = False
    stop = False
    result_summary = "No action executed."
    budget_allocated: Dict[str, Any] = {}
    solver_diagnostics: Dict[str, Any] = {}
    new_solution: Optional[AssignmentSolution] = None
    step_lex_key: List[float] = []
    step_feasible: Optional[bool] = None

    if action_type == "stop":
        stop = True
        result_summary = "LLM chose stop."
    elif action_type == "build_initial_solution":
        init_method = _sanitize_init_method(payload.get("init_method"))
        try:
            new_solution = _safe_build_initial_solution(
                method=init_method,
                instance=instance,
                cfg=cfg,
                rng_seed=rng_seed + step_id,
            )
            state.current_init_method = init_method
            state.current_solver_alg = None
            state.current_solver_params = {}
            result_summary = f"Built initial solution with init_method={init_method}."
        except Exception as exc:
            warning(f"Init action failed ({exc}); switching to stop.")
            stop = True
            result_summary = f"Init action failed and agent stopped: {exc}"
    elif action_type in ("improve_objective", "intensify_search", "diversify_search"):
        execution_plan = map_action_to_execution_plan(
            action_type=action_type,
            action_payload=payload,
            state=state,
        )
        solver_alg = _ensure_supported_solver_alg(execution_plan["solver_alg"])
        solver_params = _sanitize_solver_params(execution_plan.get("solver_params", {}))
        default_budget_request = _sanitize_budget_request(execution_plan.get("default_budget_request", {}))
        mode_strength = _sanitize_mode_strength(payload.get("mode_strength"))

        init_solution = previous_current
        if init_solution is None and previous_best is not None:
            init_solution = previous_best
        if init_solution is None:
            fallback_init_method = _sanitize_init_method(state.current_init_method or "insert")
            init_solution = _safe_build_initial_solution(
                method=fallback_init_method,
                instance=instance,
                cfg=cfg,
                rng_seed=rng_seed + step_id,
            )
            state.current_init_method = fallback_init_method

        cfg.solver.algorithm = solver_alg
        apply_result = apply_solver_params(cfg, solver_alg, solver_params)

        slice_budget, budget_allocated = budget_state.clamp_request(
            budget_request,
            default_request=default_budget_request,
        )
        budget_state.consume_solver_slice(slice_budget)

        try:
            new_solution = solve_assignment(
                algorithm=solver_alg,
                instance=instance,
                init_solution=init_solution,
                config=cfg,
                budget=slice_budget,
                rng_seed=rng_seed + step_id,
            )
        except Exception as exc:
            if solver_alg != "alns":
                warning(f"Solver '{solver_alg}' failed ({exc}); retrying with 'alns'.")
                solver_alg = "alns"
                cfg.solver.algorithm = solver_alg
                try:
                    new_solution = solve_assignment(
                        algorithm=solver_alg,
                        instance=instance,
                        init_solution=init_solution,
                        config=cfg,
                        budget=slice_budget,
                        rng_seed=rng_seed + step_id,
                    )
                except Exception as retry_exc:
                    warning(f"Fallback solver 'alns' also failed ({retry_exc}); switching to stop.")
                    stop = True
                    result_summary = f"Solver action failed and agent stopped: {retry_exc}"
            else:
                warning(f"Solver action failed ({exc}); switching to stop.")
                stop = True
                result_summary = f"Solver action failed and agent stopped: {exc}"

        state.current_solver_alg = solver_alg
        state.current_solver_params = dict(apply_result.get("applied", solver_params))
        if not stop:
            result_summary = (
                f"Executed high-level action={action_type} with mode_strength={mode_strength} "
                f"via solver={solver_alg} with params="
                f"{json.dumps(state.current_solver_params, ensure_ascii=True)} and budget="
                f"{json.dumps(budget_allocated, ensure_ascii=True)}."
            )
    else:
        stop = True
        result_summary = f"Illegal action '{action_type}' after normalization. Stopped."

    if new_solution is not None and getattr(new_solution, "eval", None) is not None:
        solver_diagnostics = dict(getattr(new_solution, "solver_diagnostics", {}) or {})
        new_summary_dict = solution_summary(solution=new_solution, instance=instance, config=cfg)
        state.current_solution = new_solution
        state.current_solution_summary_dict = new_summary_dict
        step_lex_key = [float(x) for x in (new_summary_dict.get("lex_key", []) or [])]
        step_feasible = bool(new_summary_dict.get("is_feasible", False))

        if previous_current_eval is None:
            improved_current = True
        else:
            compare_vs_previous_current = compare(new_solution.eval, previous_current_eval, cfg)
            improved_current = compare_vs_previous_current < 0
            lex_key_changed = tuple(new_solution.eval.lex_key or ()) != tuple(previous_current_eval.lex_key or ())

        if previous_best_eval is None:
            improved_best = True
            compare_vs_previous_best = -1
        else:
            compare_vs_previous_best = compare(new_solution.eval, previous_best_eval, cfg)
            improved_best = compare_vs_previous_best < 0

        if improved_best or previous_best is None:
            state.best_solution = new_solution.clone(deep=True)
            state.best_solution_summary_dict = solution_summary(solution=state.best_solution, instance=instance, config=cfg)
        elif state.best_solution is not None and state.best_solution_summary_dict is None:
            state.best_solution_summary_dict = solution_summary(solution=state.best_solution, instance=instance, config=cfg)

        if previous_current_eval is None and getattr(new_solution.eval, "lex_key", None) is not None:
            lex_key_changed = True

        result_summary = (
            f"{result_summary} feasible={bool(new_summary_dict.get('is_feasible', False))}, "
            f"lex_key={new_summary_dict.get('lex_key', [])}"
        )
        if solver_diagnostics:
            result_summary = (
                f"{result_summary}, solver_diag="
                f"{json.dumps(_condense_solver_diagnostics(solver_diagnostics), ensure_ascii=True)}"
            )
    elif state.best_solution is not None and state.best_solution_summary_dict is None:
        state.best_solution_summary_dict = solution_summary(solution=state.best_solution, instance=instance, config=cfg)

    return StepRecord(
        step_id=step_id,
        action_type=action_type,
        action_payload=payload,
        budget_request=budget_request,
        budget_allocated=budget_allocated,
        compare_vs_previous_current=compare_vs_previous_current,
        compare_vs_previous_best=compare_vs_previous_best,
        improved_current=improved_current,
        improved_best=improved_best,
        lex_key_changed=lex_key_changed,
        stop=stop,
        result_summary=result_summary,
        solver_diagnostics=solver_diagnostics,
        rationale=rationale,
        expected_effect=expected_effect,
        step_lex_key=step_lex_key,
        step_feasible=step_feasible,
    )


def _condense_solver_diagnostics(diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    best_iters = list(diagnostics.get("best_update_iters", []) or [])
    return {
        "algorithm": diagnostics.get("algorithm"),
        "total_iters": diagnostics.get("total_iters"),
        "best_update_count": diagnostics.get("best_update_count"),
        "first_best_iter": diagnostics.get("first_best_iter"),
        "last_best_iter": diagnostics.get("last_best_iter"),
        "plateau_iters_after_last_improve": diagnostics.get("plateau_iters_after_last_improve"),
        "best_update_iters_preview": best_iters[:8],
    }


def _allowed_actions(state: AgentState, budget_state: BudgetState) -> List[str]:
    if not budget_state.can_run_solver():
        return ["build_initial_solution", "stop"] if state.current_solution is None else ["stop"]
    if state.current_solution is None:
        return ["build_initial_solution", "stop"]
    return ["improve_objective", "intensify_search", "diversify_search", "stop"]


def _normalize_action(
    parsed: Dict[str, Any],
    allowed_actions: List[str],
    state: AgentState,
    budget_state: BudgetState,
) -> Dict[str, Any]:
    if state.current_solution is None and "build_initial_solution" in allowed_actions:
        fallback_action = "build_initial_solution"
    elif "improve_objective" in allowed_actions:
        fallback_action = "improve_objective"
    else:
        fallback_action = "stop"

    if not isinstance(parsed, dict):
        parsed = {}

    action_type = str(parsed.get("action_type", "")).strip()
    legal = action_type in allowed_actions
    if not legal:
        warning(f"Illegal or missing action '{action_type}', fallback to '{fallback_action}'.")
        action_type = fallback_action

    payload = parsed.get("action_payload", {})
    if not isinstance(payload, dict):
        payload = {}

    if action_type == "build_initial_solution":
        normalized_payload = {
            "init_method": _sanitize_init_method(payload.get("init_method")),
        }
    elif action_type in ("improve_objective", "intensify_search", "diversify_search"):
        normalized_payload = {
            "mode_strength": _sanitize_mode_strength(payload.get("mode_strength")),
        }
    else:
        normalized_payload = {}

    rationale = str(parsed.get("rationale", ""))
    expected_effect = str(parsed.get("expected_effect", ""))
    budget_request = _sanitize_budget_request(parsed.get("budget_request", {}))

    normalized = {
        "action_type": action_type,
        "action_payload": normalized_payload,
        "budget_request": budget_request,
        "rationale": rationale,
        "expected_effect": expected_effect,
    }
    return enforce_action_guardrails(normalized, allowed_actions, state, budget_state)


def map_action_to_execution_plan(
    action_type: str,
    action_payload: Dict[str, Any],
    state: AgentState,
) -> Dict[str, Any]:
    mode_strength = _sanitize_mode_strength(action_payload.get("mode_strength"))
    _ = state  # current presets are static, but mapping remains orchestrator-local

    plans = {
        "improve_objective": {
            "light": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.08,
                    "reaction_factor": 0.18,
                    "acceptance": "sa",
                    "accept_level": 0.18,
                },
                "default_budget_request": {
                    "time_limit_sec": 0.50,
                    "max_iters": 35,
                },
            },
            "medium": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.12,
                    "reaction_factor": 0.20,
                    "acceptance": "sa",
                    "accept_level": 0.30,
                },
                "default_budget_request": {
                    "time_limit_sec": DEFAULT_SOLVER_TIME_SEC,
                    "max_iters": DEFAULT_SOLVER_MAX_ITERS,
                },
            },
            "strong": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.18,
                    "reaction_factor": 0.24,
                    "acceptance": "sa",
                    "accept_level": 0.45,
                },
                "default_budget_request": {
                    "time_limit_sec": 1.50,
                    "max_iters": 90,
                },
            },
        },
        "intensify_search": {
            "light": {
                "solver_alg": "vnd",
                "solver_params": {
                    "local_search_passes": 2,
                },
                "default_budget_request": {
                    "time_limit_sec": 0.50,
                    "max_iters": 40,
                },
            },
            "medium": {
                "solver_alg": "vnd",
                "solver_params": {
                    "local_search_passes": 4,
                },
                "default_budget_request": {
                    "time_limit_sec": DEFAULT_SOLVER_TIME_SEC,
                    "max_iters": 80,
                },
            },
            "strong": {
                "solver_alg": "vnd",
                "solver_params": {
                    "local_search_passes": 6,
                },
                "default_budget_request": {
                    "time_limit_sec": 1.25,
                    "max_iters": 120,
                },
            },
        },
        "diversify_search": {
            "light": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.18,
                    "reaction_factor": 0.20,
                    "acceptance": "sa",
                    "accept_level": 0.45,
                },
                "default_budget_request": {
                    "time_limit_sec": 0.50,
                    "max_iters": 30,
                },
            },
            "medium": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.24,
                    "reaction_factor": 0.20,
                    "acceptance": "sa",
                    "accept_level": 0.60,
                },
                "default_budget_request": {
                    "time_limit_sec": 0.75,
                    "max_iters": 40,
                },
            },
            "strong": {
                "solver_alg": "alns",
                "solver_params": {
                    "destroy_frac": 0.32,
                    "reaction_factor": 0.24,
                    "acceptance": "sa",
                    "accept_level": 0.80,
                },
                "default_budget_request": {
                    "time_limit_sec": 1.00,
                    "max_iters": 55,
                },
            },
        },
    }

    if action_type in plans:
        return dict(plans[action_type][mode_strength])
    raise ValueError(f"Unsupported high-level action for execution plan: {action_type}")


def enforce_action_guardrails(
    action: Dict[str, Any],
    allowed_actions: List[str],
    state: AgentState,
    budget_state: BudgetState,
) -> Dict[str, Any]:
    guarded = dict(action)
    action_type = str(guarded.get("action_type", "")).strip()

    if state.current_solution is None and "build_initial_solution" in allowed_actions and action_type != "build_initial_solution":
        warning("No incumbent is available; forcing action_type='build_initial_solution'.")
        guarded["action_type"] = "build_initial_solution"
        guarded["action_payload"] = {
            "init_method": _sanitize_init_method(
                guarded.get("action_payload", {}).get("init_method") if isinstance(guarded.get("action_payload"), dict) else None
            )
        }
        return guarded

    if action_type in ("improve_objective", "intensify_search", "diversify_search"):
        payload = guarded.get("action_payload", {})
        if not isinstance(payload, dict):
            payload = {}
        payload["mode_strength"] = _sanitize_mode_strength(payload.get("mode_strength"))
        guarded["action_payload"] = payload

        if payload["mode_strength"] == "strong" and _budget_too_small_for_strong_action(budget_state):
            warning("Remaining budget is too small for strong mode; downgrading mode_strength to 'medium'.")
            payload["mode_strength"] = "medium"

    intensify_repeats = sum(
        1
        for record in state.history[-2:]
        if record.action_type == "intensify_search" and not record.improved_best
    )
    if (
        action_type == "intensify_search"
        and state.consecutive_no_improve >= INTENSIFY_STALL_THRESHOLD
        and intensify_repeats >= 1
        and "diversify_search" in allowed_actions
    ):
        warning("Repeated unsuccessful intensification detected; downgrading to 'diversify_search'.")
        guarded["action_type"] = "diversify_search"
        fallback_strength = "strong"
        if _budget_too_small_for_strong_action(budget_state):
            fallback_strength = "medium"
        guarded["action_payload"] = {"mode_strength": fallback_strength}
        action_type = "diversify_search"

    if action_type == "stop" and not _should_allow_stop(state, budget_state):
        fallback_action = "build_initial_solution" if state.current_solution is None else "improve_objective"
        if fallback_action in allowed_actions:
            warning(f"Stop rejected by guardrails; forcing action_type='{fallback_action}'.")
            guarded["action_type"] = fallback_action
            if fallback_action == "build_initial_solution":
                guarded["action_payload"] = {
                    "init_method": _sanitize_init_method(
                        guarded.get("action_payload", {}).get("init_method") if isinstance(guarded.get("action_payload"), dict) else None
                    )
                }
            else:
                guarded["action_payload"] = {"mode_strength": DEFAULT_MODE_STRENGTH}

    return guarded


def _safe_build_initial_solution(
    method: str,
    instance: Instance,
    cfg: Config,
    rng_seed: int,
) -> AssignmentSolution:
    safe_method = _sanitize_init_method(method)
    try:
        return build_initial_solution(
            method=safe_method,
            instance=instance,
            config=cfg,
            rng_seed=rng_seed,
        )
    except Exception as exc:
        if safe_method != "insert":
            warning(f"Init method '{safe_method}' failed ({exc}); fallback to 'insert'.")
            return build_initial_solution(
                method="insert",
                instance=instance,
                config=cfg,
                rng_seed=rng_seed,
            )
        raise


def _ensure_supported_solver_alg(solver_alg: str) -> str:
    return _sanitize_solver_alg(solver_alg)


def _sanitize_init_method(value: Any) -> str:
    method = str(value or "insert").strip().lower()
    if method not in ("insert", "sweep"):
        return "insert"
    return method


def _sanitize_mode_strength(value: Any) -> str:
    mode_strength = str(value or DEFAULT_MODE_STRENGTH).strip().lower()
    if mode_strength not in ("light", "medium", "strong"):
        return DEFAULT_MODE_STRENGTH
    return mode_strength


def _sanitize_solver_alg(value: Any) -> str:
    solver_alg = str(value or "alns").strip().lower()
    if solver_alg not in ("vnd", "alns"):
        return "alns"
    return solver_alg


def _sanitize_solver_params(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return dict(value)


def _extract_mode_strength(payload: Dict[str, Any]) -> Optional[str]:
    if not isinstance(payload, dict):
        return None
    if "mode_strength" not in payload:
        return None
    return _sanitize_mode_strength(payload.get("mode_strength"))


def _budget_too_small_for_meaningful_solver(budget_state: BudgetState) -> bool:
    remaining_time = budget_state.remaining.get("time_limit_sec")
    remaining_iters = budget_state.remaining.get("max_iters")

    if remaining_time is not None and float(remaining_time) < MEANINGFUL_MIN_TIME_SEC:
        return True
    if remaining_iters is not None and float(remaining_iters) < MEANINGFUL_MIN_ITERS:
        return True
    return False


def _budget_too_small_for_strong_action(budget_state: BudgetState) -> bool:
    remaining_time = budget_state.remaining.get("time_limit_sec")
    remaining_iters = budget_state.remaining.get("max_iters")

    if remaining_time is not None and float(remaining_time) < STRONG_MIN_TIME_SEC:
        return True
    if remaining_iters is not None and float(remaining_iters) < STRONG_MIN_ITERS:
        return True
    return False


def _should_allow_stop(state: AgentState, budget_state: BudgetState) -> bool:
    if not budget_state.can_run_solver():
        return True
    if _budget_too_small_for_meaningful_solver(budget_state):
        return True
    if state.consecutive_no_improve >= DEFAULT_MAX_NO_IMPROVE:
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
        if key == "max_iters":
            out[key] = int(max(1, round(numeric)))
        else:
            out[key] = float(numeric)
    return out


def _call_llm(client: LLMClientProtocol, system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return client.chat(messages)


def _parse_json_obj(text: str, default: Dict[str, Any]) -> Dict[str, Any]:
    if not text:
        return default
    text = text.strip()

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return default

    try:
        obj = json.loads(match.group(0))
    except Exception:
        return default
    return obj if isinstance(obj, dict) else default


def _round_budget_dict(data: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    out: Dict[str, Optional[float]] = {}
    for key, value in data.items():
        out[key] = _round_number(value)
    return out


def _round_number(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if abs(float(value) - round(float(value))) < 1e-9:
        return float(round(float(value)))
    return round(float(value), 4)


def _as_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _resolve_max_agent_steps(
    *,
    max_agent_steps: Optional[int],
) -> int:
    explicit_steps = _resolve_positive_int(max_agent_steps)
    if explicit_steps is not None:
        return explicit_steps
    return DEFAULT_MAX_AGENT_STEPS


def _resolve_positive_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        numeric = int(value)
    except Exception:
        return None
    if numeric <= 0:
        return None
    return numeric


def _stop_reason_before_step(state: AgentState, budget_state: BudgetState) -> Optional[str]:
    if budget_state.can_run_solver():
        return None
    if state.current_solution is None:
        return None
    return "solver budget exhausted"
