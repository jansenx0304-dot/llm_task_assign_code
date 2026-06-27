"""Main agent flow: observe -> prompt/schema -> LLM -> agent_io -> execute -> evaluate -> trace."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Protocol

from .agent_io import (
    AgentIOError,
    compile_protected_metric_bounds,
    parse_validate_compile_step,
    parse_validate_compile_supervisor,
)
from .config import Budget, Config
from .evaluator import check_protected_metrics, compare_quality, evaluate, evaluation_quality
from .models import Instance
from .observation import build_step_observation, build_supervisor_observation, solution_summary
from .operators import CompiledALNSPolicy
from .prompts import step_prompt, supervisor_prompt, system_prompt
from .schemas import step_schema, supervisor_schema
from .solution import AssignmentSolution
from .step_agent import RuntimeControl
from .supervisor import StageCompletion, StagePlan
from .tools.assign_solvers import solve_assignment
from .tools.init_solutions import build_initial_solution_with_insertion
from .trace import RunTrace, StepRecord


class AgentClient(Protocol):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        ...


class OrchestratorError(RuntimeError):
    pass


@dataclass(slots=True)
class GlobalBudgetState:
    max_step_calls: int
    max_solver_calls: int
    max_time_sec: float
    max_iters: int
    step_calls: int = 0
    solver_calls: int = 0
    time_used_sec: float = 0.0
    iters_used: int = 0

    def exhausted(self) -> bool:
        return (
            self.step_calls >= self.max_step_calls
            or self.solver_calls >= self.max_solver_calls
            or self.time_used_sec >= self.max_time_sec
            or self.iters_used >= self.max_iters
        )

    def remaining(self) -> Dict[str, float]:
        return {
            "step_calls": float(max(0, self.max_step_calls - self.step_calls)),
            "solver_calls": float(max(0, self.max_solver_calls - self.solver_calls)),
            "time_sec": max(0.0, self.max_time_sec - self.time_used_sec),
            "iters": float(max(0, self.max_iters - self.iters_used)),
        }

    def apply_result(self, result: Mapping[str, Any]) -> None:
        self.solver_calls += 1
        self.time_used_sec += float(result.get("time_sec_used", 0.0) or 0.0)
        self.iters_used += int(result.get("iters_used", 0) or 0)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "used": {
                "step_calls": self.step_calls,
                "solver_calls": self.solver_calls,
                "time_sec": round(self.time_used_sec, 6),
                "iters": self.iters_used,
            },
            "remaining": self.remaining(),
        }


@dataclass(slots=True)
class RunState:
    instance: Instance
    config: Config
    global_budget: GlobalBudgetState
    rng_seed: int
    instance_name: str = ""
    global_objective_layers: list[Dict[str, str]] = field(default_factory=list)
    working_solution: AssignmentSolution | None = None
    best_solution: AssignmentSolution | None = None
    active_stage: StagePlan | None = None
    records: RunTrace = field(default_factory=RunTrace)
    last_result: Dict[str, Any] | None = None
    last_completion: StageCompletion | None = None
    step_index: int = 0
    _observation_counter: int = 0

    @property
    def working_summary(self) -> Dict[str, Any]:
        solution = self.working_solution or AssignmentSolution.empty_from_instance(self.instance, put_all_unassigned=True)
        return solution_summary(
            solution,
            self.instance,
            self.config,
            stage_objective_layers=(self.active_stage.objective_layers if self.active_stage else self.global_objective_layers),
            global_objective_layers=self.global_objective_layers,
        )

    @property
    def best_summary(self) -> Optional[Dict[str, Any]]:
        if self.best_solution is None:
            return None
        return solution_summary(
            self.best_solution,
            self.instance,
            self.config,
            stage_objective_layers=(self.active_stage.objective_layers if self.active_stage else self.global_objective_layers),
            global_objective_layers=self.global_objective_layers,
        )

    def next_observation_id(self) -> str:
        self._observation_counter += 1
        return f"O{self._observation_counter:03d}"


def run_orchestrator(
    client: AgentClient,
    instance: Instance,
    user_goal_text: str,
    config: Optional[Config] = None,
    budget: Optional[Budget] = None,
    rng_seed: int = 0,
    max_agent_steps: Optional[int] = None,
    max_solver_calls: Optional[int] = None,
    max_stagnation_steps: int = 3,
    artifact_dir: Optional[Path] = None,
    llm_mode: Optional[str] = None,
    run_config: Optional[Dict[str, Any]] = None,
    case_file: str = "case.json",
    trace_callback: Optional[Callable[[StepRecord], None]] = None,
) -> AssignmentSolution:
    del max_stagnation_steps, artifact_dir, llm_mode, case_file
    cfg = config or Config()
    total = budget or Budget(time_limit_sec=10.0, max_iters=500)
    state = RunState(
        instance=instance,
        config=cfg,
        global_budget=GlobalBudgetState(
            max_step_calls=max(1, int(max_agent_steps or 6)),
            max_solver_calls=max(1, int(max_solver_calls or 4)),
            max_time_sec=max(1e-6, float(total.time_limit_sec or 10.0)),
            max_iters=max(1, int(total.max_iters or 500)),
        ),
        rng_seed=rng_seed,
        instance_name=str((run_config or {}).get("instance", "")),
    )
    started_at = time.time()
    stage_index = 1

    stopped = _supervisor_turn(
        client,
        state,
        user_goal_text=user_goal_text,
        phase="kickoff",
        stage_index=stage_index,
        trace_callback=trace_callback,
    )
    if stopped or state.active_stage is None:
        raise OrchestratorError("supervisor kickoff did not issue a stage")

    stop_reason = "global_budget_exhausted"
    while not state.global_budget.exhausted() and state.active_stage is not None:
        active_stage = state.active_stage
        obs = build_step_observation(instance=instance, run_state=state, active_stage=active_stage)
        schema = step_schema(obs["action_space"], active_stage.as_observation())
        raw = _chat(client, step_prompt(user_goal=user_goal_text, observation=obs, schema=schema))
        try:
            decision, control = parse_validate_compile_step(
                raw_text=raw,
                schema=schema,
                observation=obs,
                active_stage=active_stage,
                config=cfg,
            )
        except AgentIOError as exc:
            _add_record(
                state,
                StepRecord(
                    step_id=_next_step_id(state),
                    phase="step",
                    observation_id=_obs_id(obs),
                    observation=obs,
                    stage_id=active_stage.stage_id,
                    raw_output=raw,
                    error=str(exc),
                ),
                trace_callback,
            )
            raise OrchestratorError(f"step LLM output invalid: {exc}") from exc

        state.global_budget.step_calls += 1
        if control.action == "request_supervisor_review":
            _add_record(
                state,
                StepRecord(
                    step_id=_next_step_id(state),
                    phase="step_review_request",
                    observation_id=_obs_id(obs),
                    observation=obs,
                    stage_id=active_stage.stage_id,
                    raw_output=raw,
                    parsed=decision.raw,
                    decision=decision.as_dict(),
                    control=control.as_dict(),
                    result={"control_flow": "review_requested"},
                ),
                trace_callback,
            )
            stage_index += 1
            stopped = _supervisor_turn(
                client,
                state,
                user_goal_text=user_goal_text,
                phase="review",
                stage_index=stage_index,
                trace_callback=trace_callback,
                completed_stage=active_stage,
            )
            if stopped:
                stop_reason = "supervisor_stop"
                break
            continue

        result = execute_runtime_control(control, instance=instance, config=cfg, state=state, rng_seed=rng_seed)
        state.global_budget.apply_result(result)
        active_stage.apply_result(result)
        state.last_result = result
        completion = active_stage.is_complete(state)
        state.last_completion = completion
        _add_record(
            state,
            StepRecord(
                step_id=_next_step_id(state),
                phase="step",
                observation_id=_obs_id(obs),
                observation=obs,
                stage_id=active_stage.stage_id,
                raw_output=raw,
                parsed=decision.raw,
                decision=decision.as_dict(),
                control=control.as_dict(),
                result=result,
                completion=completion.as_dict(),
            ),
            trace_callback,
        )
        state.step_index += 1
        if completion.completed:
            stage_index += 1
            stopped = _supervisor_turn(
                client,
                state,
                user_goal_text=user_goal_text,
                phase="review",
                stage_index=stage_index,
                trace_callback=trace_callback,
                completed_stage=active_stage,
            )
            if stopped:
                stop_reason = "supervisor_stop"
                break

    final_solution = state.best_solution or state.working_solution
    if final_solution is None:
        final_solution = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    final_solution.run_summary = {
        "stop_reason": stop_reason,
        "objective_tiers": state.global_objective_layers,
        "budget": state.global_budget.as_dict(),
        "elapsed_sec": round(time.time() - started_at, 6),
    }
    final_solution.run_artifact = {
        "records": state.records.as_artifact(),
        "final_result": solution_summary(
            final_solution,
            instance,
            cfg,
            stage_objective_layers=(state.active_stage.objective_layers if state.active_stage else state.global_objective_layers),
            global_objective_layers=state.global_objective_layers,
        ),
    }
    return final_solution


def execute_runtime_control(
    control: RuntimeControl,
    *,
    instance: Instance,
    config: Config,
    state: RunState,
    rng_seed: int,
) -> Dict[str, Any]:
    if control.action == "construct_initial":
        return _execute_initial(control, instance=instance, config=config, state=state, rng_seed=rng_seed)
    if control.action == "run_alns":
        return _execute_alns(control, instance=instance, config=config, state=state, rng_seed=rng_seed)
    raise ValueError("request_supervisor_review is control flow, not an executable action")


def _supervisor_turn(
    client: AgentClient,
    state: RunState,
    *,
    user_goal_text: str,
    phase: str,
    stage_index: int,
    trace_callback: Optional[Callable[[StepRecord], None]],
    completed_stage: StagePlan | None = None,
) -> bool:
    obs = build_supervisor_observation(
        phase=phase,
        instance=state.instance,
        run_state=state,
        completed_stage=completed_stage,
    )
    schema = supervisor_schema(phase, obs["action_space"])
    raw = _chat(client, supervisor_prompt(phase=phase, user_goal=user_goal_text, observation=obs, schema=schema))
    try:
        decision = parse_validate_compile_supervisor(
            raw_text=raw,
            schema=schema,
            observation=obs,
            phase=phase,
            config=state.config,
            stage_index=stage_index,
        )
    except AgentIOError as exc:
        _add_record(
            state,
            StepRecord(
                step_id=_next_step_id(state),
                phase=f"supervisor_{phase}",
                observation_id=_obs_id(obs),
                observation=obs,
                stage_id=None if completed_stage is None else completed_stage.stage_id,
                raw_output=raw,
                error=str(exc),
            ),
            trace_callback,
        )
        raise OrchestratorError(f"supervisor LLM output invalid: {exc}") from exc

    if decision.global_objective:
        state.global_objective_layers = decision.global_objective
    if decision.action == "stop_run":
        _add_record(
            state,
            StepRecord(
                step_id=_next_step_id(state),
                phase=f"supervisor_{phase}",
                observation_id=_obs_id(obs),
                observation=obs,
                stage_id=None if completed_stage is None else completed_stage.stage_id,
                raw_output=raw,
                parsed=decision.raw,
                decision={
                    "action": "stop_run",
                    "decision_evidence": dict(decision.raw.get("decision_evidence", {}) or {}),
                    "stop_explanation": decision.raw.get("stop_explanation", ""),
                },
            ),
            trace_callback,
        )
        state.active_stage = None
        return True

    state.active_stage = decision.next_stage
    _add_record(
        state,
        StepRecord(
            step_id=_next_step_id(state),
            phase=f"supervisor_{phase}",
            observation_id=_obs_id(obs),
            observation=obs,
            stage_id=None if state.active_stage is None else state.active_stage.stage_id,
            raw_output=raw,
            parsed=decision.raw,
            decision=decision.as_dict(),
            control=None if state.active_stage is None else state.active_stage.as_observation(),
        ),
        trace_callback,
    )
    return False


def _execute_initial(control: RuntimeControl, *, instance: Instance, config: Config, state: RunState, rng_seed: int) -> Dict[str, Any]:
    active_stage = _require_active_stage(state)
    before_solution = state.working_solution.clone(deep=True) if state.working_solution is not None else AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    before_eval = evaluate(before_solution, instance, config, update_solution_schedule=True)
    started = time.perf_counter()
    result = build_initial_solution_with_insertion(
        instance,
        config,
        control.insertion_policy,
        rng_seed,
        runtime_context={
            "trace_id": f"X{state.step_index + 1}",
            "runtime_target": dict(control.runtime_target),
            "feasibility_policy": dict(control.feasibility_policy or {}),
        },
    )
    elapsed = time.perf_counter() - started
    protected = _protected_check(active_stage, result.evaluation)
    if protected["passed"]:
        state.working_solution = result.solution
        state.best_solution = result.solution.clone(deep=True) if result.evaluation.is_feasible else None
    else:
        state.working_solution = before_solution
        result.trace["rejection_reason"] = "protected_metric_violated"
    after_eval = evaluate(state.working_solution, instance, config, update_solution_schedule=True)
    trace = dict(result.trace)
    trace["protected_metric_violations"] = list(protected["violations"])
    trace["protected_metric_passed"] = bool(protected["passed"])
    return _build_action_result(
        control,
        stage_id=active_stage.stage_id,
        before_eval=before_eval,
        after_eval=after_eval,
        protected_passed=protected["passed"],
        accepted=protected["passed"],
        time_sec_used=elapsed,
        iters_used=1,
        trace=trace,
    )


def _execute_alns(control: RuntimeControl, *, instance: Instance, config: Config, state: RunState, rng_seed: int) -> Dict[str, Any]:
    if state.working_solution is None:
        raise ValueError("run_alns requested before a working solution exists")
    active_stage = _require_active_stage(state)
    before_solution = state.working_solution.clone(deep=True)
    before_eval = evaluate(before_solution, instance, config, update_solution_schedule=True)
    result = solve_assignment(
        instance=instance,
        init_solution=state.working_solution,
        config=config,
        budget=Budget(
            time_limit_sec=float(control.solver_budget["max_time_sec"]),
            max_iters=int(control.solver_budget["max_iters"]),
        ),
        policy=CompiledALNSPolicy(
            destroy_policy=control.destroy_policy,
            insertion_policy=control.insertion_policy,
            acceptance_policy=control.acceptance_policy,
        ),
        rng_seed=rng_seed + state.step_index + 1,
        stage_objective_layers=active_stage.objective_layers,
        feasibility_policy=control.feasibility_policy,
        global_objective_layers=state.global_objective_layers,
        trace_id=f"X{state.step_index + 1}",
        protected_metric_bounds=compile_protected_metric_bounds(
            active_stage.protected_metrics,
            active_stage.protected_metric_baseline,
        ),
        runtime_target=control.runtime_target,
    )
    state.working_solution = result.working_solution
    if result.global_best_feasible is not None:
        candidate_eval = evaluate(result.global_best_feasible, instance, config, update_solution_schedule=True)
        current_best_eval = None if state.best_solution is None else evaluate(state.best_solution, instance, config, update_solution_schedule=True)
        if current_best_eval is None or compare_quality(candidate_eval, current_best_eval, state.global_objective_layers) < 0:
            state.best_solution = result.global_best_feasible.clone(deep=True)
    after_eval = evaluate(state.working_solution, instance, config, update_solution_schedule=True)
    protected = _protected_check(active_stage, after_eval)
    diagnostics = dict(result.diagnostics or {})
    return _build_action_result(
        control,
        stage_id=active_stage.stage_id,
        before_eval=before_eval,
        after_eval=after_eval,
        protected_passed=protected["passed"],
        accepted=True,
        time_sec_used=float(diagnostics.get("actual_time_used_sec", 0.0) or 0.0),
        iters_used=int(diagnostics.get("actual_iters_used", 0) or 0),
        trace=dict(result.trace),
    )


def _build_action_result(
    control: RuntimeControl,
    *,
    stage_id: str,
    before_eval: Any,
    after_eval: Any,
    protected_passed: bool,
    accepted: bool,
    time_sec_used: float,
    iters_used: int,
    trace: Dict[str, Any],
) -> Dict[str, Any]:
    before_quality = {str(k): float(v) for k, v in before_eval.quality_metrics.items()}
    after_quality = {str(k): float(v) for k, v in after_eval.quality_metrics.items()}
    return {
        "action": control.action,
        "stage_id": stage_id,
        "intent_id": control.intent_id,
        "before_quality": before_quality,
        "after_quality": after_quality,
        "quality_delta": {
            name: after_quality.get(name, 0.0) - before_quality.get(name, 0.0)
            for name in sorted(set(before_quality) | set(after_quality))
        },
        "before_feasible": bool(before_eval.is_feasible),
        "after_feasible": bool(after_eval.is_feasible),
        "protected_passed": bool(protected_passed),
        "accepted": bool(accepted),
        "time_sec_used": round(float(time_sec_used), 6),
        "iters_used": int(iters_used),
        "trace": trace,
    }


def _protected_check(active_stage: StagePlan, evaluation: Any) -> Dict[str, Any]:
    if not active_stage.protected_metrics:
        return {"passed": True, "violations": []}
    check = check_protected_metrics(
        evaluation_quality(evaluation),
        compile_protected_metric_bounds(active_stage.protected_metrics, active_stage.protected_metric_baseline),
    )
    return check.as_dict()


def _chat(client: AgentClient, prompt: str) -> str:
    return client.chat(
        [{"role": "system", "content": system_prompt()}, {"role": "user", "content": prompt}],
        temperature=0.0,
    )


def _require_active_stage(state: RunState) -> StagePlan:
    if state.active_stage is None:
        raise OrchestratorError("no active stage")
    return state.active_stage


def _obs_id(observation: Mapping[str, Any]) -> str | None:
    return (observation.get("run_context", {}) or {}).get("observation_id")


def _next_step_id(state: RunState) -> str:
    return f"S{len(state.records.steps) + 1:03d}"


def _add_record(state: RunState, record: StepRecord, callback: Optional[Callable[[StepRecord], None]]) -> None:
    state.records.add(record)
    if callback is not None:
        callback(record)


__all__ = ["AgentClient", "GlobalBudgetState", "OrchestratorError", "RunState", "execute_runtime_control", "run_orchestrator"]
