from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

from .config import Budget, Config
from .contract_monitor import check_contract_completion, update_contract_events
from .demo_policy import demo_solver_decision, demo_supervisor_kickoff, demo_supervisor_review
from .evaluator import compare_quality, evaluate
from .llm_public_interface import build_public_candidates
from .memory import RunMemory
from .models import Instance
from .observation import (
    build_solver_observation,
    build_supervisor_kickoff_observation,
    build_supervisor_review_observation,
)
from .operators.destroy import build_destroy_landscape
from .operators.insertion import build_insertion_landscape
from .outcome_auditor import audit_initial_result, audit_outcome
from .policy_validator import (
    validate_solver_decision,
    validate_supervisor_kickoff,
    validate_supervisor_review,
)
from .prompts import get_solver_prompt, get_supervisor_kickoff_prompt, get_supervisor_review_prompt, get_system_prompt
from .schemas import (
    SOLVER_DECISION_SCHEMA,
    schema_text,
    supervisor_kickoff_schema_for_limits,
    supervisor_review_schema_for_limits,
)
from .solution import AssignmentSolution, EvalResult
from .tools import (
    ContractProgress,
    SearchContract,
    build_initial_solution_with_insertion,
    compile_contract,
    compile_global_objective,
    compile_insertion_control,
    compile_solver_control,
    derive_solver_request,
    instance_summary,
    solution_summary,
    solve_assignment,
)


class LLMClientProtocol(Protocol):
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


class OrchestratorError(RuntimeError):
    pass


class LLMOutputError(ValueError):
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
class AgentState:
    global_objective_layers: List[Dict[str, str]] = field(default_factory=list)
    working_solution: Optional[AssignmentSolution] = None
    best_solution: Optional[AssignmentSolution] = None
    active_contract: Optional[SearchContract] = None
    contract_progress: Optional[ContractProgress] = None
    memory: RunMemory = field(default_factory=RunMemory)
    trace_events: List[Dict[str, Any]] = field(default_factory=list)
    trace_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    llm_fallback_used: bool = False


def run_orchestrator(
    client: LLMClientProtocol,
    instance: Instance,
    user_goal_text: str,
    config: Optional[Config] = None,
    budget: Optional[Budget] = None,
    rng_seed: int = 0,
    max_agent_steps: Optional[int] = None,
    max_solver_calls: Optional[int] = None,
    max_stagnation_steps: int = 3,
    allow_llm_fallback: bool = False,
    artifact_dir: Optional[Path] = None,
    llm_mode: Optional[str] = None,
    run_config: Optional[Dict[str, Any]] = None,
    case_file: str = "case.json",
    trace_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> AssignmentSolution:
    del max_stagnation_steps, artifact_dir
    cfg = config or Config()
    total = budget or Budget(time_limit_sec=10.0, max_iters=500)
    budgets = GlobalBudgetState(
        max_step_calls=max(1, int(max_agent_steps or 6)),
        max_solver_calls=max(1, int(max_solver_calls or 4)),
        max_time_sec=max(1e-6, float(total.time_limit_sec or 10.0)),
        max_iters=max(1, int(total.max_iters or 500)),
    )
    state = AgentState(trace_callback=trace_callback)
    started_at = time.time()
    base_candidates = build_public_candidates(instance, cfg)
    inst_summary = instance_summary(instance, rng_seed=rng_seed)
    relaxation_context = dict(inst_summary.get("relaxation_scale_context", {}) or {})
    _trace(state, "run_start", {"case_file": case_file, "llm_mode": llm_mode or "api", "run_config": run_config or {}, "global_budget": budgets.remaining()})
    _trace(state, "public_candidates", base_candidates.as_dict())

    kickoff_observation = build_supervisor_kickoff_observation(
        instance=instance,
        instance_summary=inst_summary,
        candidates=base_candidates,
        user_goal_text=user_goal_text,
        remaining_global_budget=budgets.remaining(),
        relaxation_scale_context=relaxation_context,
    )
    kickoff_prompt = get_supervisor_kickoff_prompt(
        user_goal_text=user_goal_text,
        observation=kickoff_observation,
        json_schema=schema_text(
            supervisor_kickoff_schema_for_limits(kickoff_observation["next_contract_resource_limits"])
        ),
    )
    kickoff_payload = _call_validated(
        client,
        state,
        "supervisor_kickoff",
        kickoff_observation,
        kickoff_prompt,
        lambda value: validate_supervisor_kickoff(
            value,
            base_candidates,
            kickoff_observation["evidence_items"],
            kickoff_observation["memory_items"],
            cfg,
            budgets.remaining(),
        ),
        demo_supervisor_kickoff,
        allow_llm_fallback,
    )
    kickoff_raw = kickoff_payload["supervisor_decision"]
    state.global_objective_layers = compile_global_objective(cfg, kickoff_raw["global_objective"])
    _trace(state, "global_objective_applied", state.global_objective_layers)
    contract_seq = 1
    state.active_contract = compile_contract(kickoff_raw["next_contract"], "C001", cfg)
    state.contract_progress = ContractProgress("C001")
    _trace_contract_compile(state, state.active_contract)

    solver_action_index = 0
    stop_reason = "global_budget_exhausted"
    last_contract_events: List[str] = []
    while not budgets.exhausted():
        assert state.active_contract is not None and state.contract_progress is not None
        contract = state.active_contract
        progress = state.contract_progress
        candidates = build_public_candidates(instance, cfg, state)
        working_summary = {} if state.working_solution is None else solution_summary(state.working_solution, instance, cfg)
        best_summary = None if state.best_solution is None else solution_summary(state.best_solution, instance, cfg)
        landscape = {} if state.working_solution is None else _public_landscape(
            build_destroy_landscape(state.working_solution, instance, cfg),
            build_insertion_landscape(state.working_solution, instance, cfg),
        )
        solver_observation = build_solver_observation(
            active_contract=contract.as_dict(),
            contract_progress=progress.as_dict(),
            remaining_contract_resources=_contract_remaining(contract, progress),
            remaining_global_budget=budgets.remaining(),
            working_summary=working_summary,
            best_summary=best_summary,
            candidate_landscape=landscape,
            recent_memory=state.memory.for_solver(),
            candidates=candidates,
        )
        solver_prompt = get_solver_prompt(
            user_goal_text=user_goal_text,
            observation=solver_observation,
            json_schema=schema_text(SOLVER_DECISION_SCHEMA),
        )
        solver_payload = _call_validated(
            client,
            state,
            "solver",
            solver_observation,
            solver_prompt,
            lambda value: validate_solver_decision(
                value,
                candidates,
                contract.contract_type,
                evidence_items=solver_observation["evidence_items"],
                memory_items=solver_observation["memory_items"],
            ),
            demo_solver_decision,
            allow_llm_fallback,
            step_index=solver_action_index,
            contract_id=contract.contract_id,
        )
        budgets.step_calls += 1
        decision = solver_payload["solver_decision"]
        action = decision["action"]
        completion = {"completed": False, "reason": "", "result": "running"}
        outcome: Dict[str, Any] = {"events": []}

        if action == "request_supervisor_review":
            completion = {"completed": True, "reason": "solver_requested_review", "result": "requested_review"}
            last_contract_events = []
            memory_item = state.memory.record_solver_action(contract.contract_id, solver_action_index, solver_payload, [])
            _trace(state, "memory_update", memory_item, solver_action_index, contract.contract_id)
        elif action == "construct_initial":
            outcome = _execute_initial_action(
                state,
                instance,
                cfg,
                candidates,
                solver_payload,
                budgets,
                progress,
                rng_seed,
                solver_action_index,
                contract,
            )
            last_contract_events = list(outcome["events"])
            update_contract_events(progress, last_contract_events)
            completion = check_contract_completion(contract, progress)
        elif action == "run_alns":
            outcome = _execute_alns_action(
                state,
                instance,
                cfg,
                candidates,
                solver_payload,
                budgets,
                progress,
                rng_seed,
                solver_action_index,
                contract,
            )
            last_contract_events = list(outcome["events"])
            update_contract_events(progress, last_contract_events)
            completion = check_contract_completion(contract, progress)
        else:
            raise OrchestratorError(f"unsupported solver action: {action}")

        _trace(state, "contract_progress", progress.as_dict(), solver_action_index, contract.contract_id)
        _trace(state, "contract_completion_check", completion, solver_action_index, contract.contract_id)

        if completion["completed"]:
            contract_memory = state.memory.record_contract(contract.as_dict(), progress.as_dict(), last_contract_events, completion)
            _trace(state, "contract_end", {"completion": completion, "memory_update": contract_memory}, contract_id=contract.contract_id)
            review_decision = _call_supervisor_review(
                client,
                state,
                instance,
                cfg,
                budgets,
                user_goal_text,
                relaxation_context,
                contract,
                progress,
                completion,
                last_contract_events,
                allow_llm_fallback,
            )
            if review_decision["action"] == "stop_run":
                stop_reason = "supervisor_stop"
                break
            contract_seq += 1
            next_contract_id = f"C{contract_seq:03d}"
            state.active_contract = compile_contract(review_decision["next_contract"], next_contract_id, cfg)
            state.contract_progress = ContractProgress(next_contract_id)
            _trace_contract_compile(state, state.active_contract)
        solver_action_index += 1

    final_solution = state.best_solution or state.working_solution
    if final_solution is None:
        raise OrchestratorError("orchestrator produced no solution")
    final_summary = solution_summary(final_solution, instance, cfg)
    run_summary = {
        "stop_reason": stop_reason,
        "objective_tiers": state.global_objective_layers,
        "budget": budgets.as_dict(),
        "llm_fallback_used": state.llm_fallback_used,
        "elapsed_sec": round(time.time() - started_at, 6),
    }
    _trace(state, "final_result", {"summary": final_summary, "run_summary": run_summary})
    final_solution.run_summary = run_summary
    final_solution.run_artifact = {"trace_events": state.trace_events, "memory": state.memory.as_dict(), "final_result": final_summary}
    return final_solution


def _execute_initial_action(
    state: AgentState,
    instance: Instance,
    cfg: Config,
    candidates: Any,
    solver_payload: Dict[str, Any],
    budgets: GlobalBudgetState,
    progress: ContractProgress,
    rng_seed: int,
    solver_action_index: int,
    contract: SearchContract,
) -> Dict[str, Any]:
    initial_policy = compile_insertion_control(solver_payload["solver_decision"]["insertion_control"], candidates)
    _trace(state, "compiled_initial_policy", initial_policy.as_dict(), solver_action_index, contract.contract_id)
    state.working_solution = build_initial_solution_with_insertion(instance, cfg, initial_policy, rng_seed)
    initial_eval = _eval(state.working_solution, instance, cfg)
    state.best_solution = state.working_solution.clone(deep=True) if initial_eval.is_feasible else None
    used_time = 0.0
    budgets.solver_calls += 1
    budgets.time_used_sec += used_time
    progress.solver_actions += 1
    progress.time_used_sec += used_time
    progress.iters_used += 1
    summary = solution_summary(state.working_solution, instance, cfg)
    outcome = audit_initial_result(initial_eval=initial_eval)
    _trace(state, "initial_insertion_result", {"input": "empty_solution + all_tasks", "context": "initial_construction", "result": summary}, solver_action_index, contract.contract_id)
    _trace(state, "outcome_audit", outcome, solver_action_index, contract.contract_id)
    memory_item = state.memory.record_solver_action(contract.contract_id, solver_action_index, solver_payload, outcome["events"])
    _trace(state, "memory_update", memory_item, solver_action_index, contract.contract_id)
    return outcome


def _execute_alns_action(
    state: AgentState,
    instance: Instance,
    cfg: Config,
    candidates: Any,
    solver_payload: Dict[str, Any],
    budgets: GlobalBudgetState,
    progress: ContractProgress,
    rng_seed: int,
    solver_action_index: int,
    contract: SearchContract,
) -> Dict[str, Any]:
    if state.working_solution is None:
        raise OrchestratorError("run_alns requested before a working solution exists")
    compiled_policy = compile_solver_control(solver_payload, candidates)
    solver_request = derive_solver_request(contract, progress)
    compiled_policy_payload = compiled_policy.as_dict()
    solver_decision = solver_payload["solver_decision"]
    compiled_policy_payload["llm_operator_scores"] = {
        "destroy": list(solver_decision["destroy_control"]["operator_scores"]),
        "insertion": list(solver_decision["insertion_control"]["operator_scores"]),
    }
    _trace(state, "compiled_solver_policy", compiled_policy_payload, solver_action_index, contract.contract_id)
    _trace(state, "solver_request", solver_request.as_dict(), solver_action_index, contract.contract_id)
    before_working_eval = _eval(state.working_solution, instance, cfg)
    before_best_eval = None if state.best_solution is None else _eval(state.best_solution, instance, cfg)
    result = solve_assignment(
        instance=instance,
        init_solution=state.working_solution,
        config=cfg,
        budget=Budget(time_limit_sec=solver_request.time_limit_sec, max_iters=solver_request.max_iters),
        policy=compiled_policy,
        rng_seed=rng_seed + solver_action_index + 1,
        contract_objective_layers=contract.stage_objective_layers,
        feasibility_policy=contract.feasibility_policy,
        global_objective_layers=state.global_objective_layers,
    )
    state.working_solution = result.final_current
    after_working_eval = _eval(state.working_solution, instance, cfg)
    candidate_best = result.best_feasible
    if candidate_best is not None:
        candidate_best_eval = _eval(candidate_best, instance, cfg)
        if before_best_eval is None or compare_quality(candidate_best_eval, before_best_eval, state.global_objective_layers) < 0:
            state.best_solution = candidate_best.clone(deep=True)
    after_best_eval = None if state.best_solution is None else _eval(state.best_solution, instance, cfg)
    diagnostics = dict(result.diagnostics)
    diagnostics["accepted_trial_count"] = result.accepted_trial_count
    diagnostics["rejected_trial_count"] = result.rejected_trial_count
    used_time = min(
        float(diagnostics.get("actual_time_used_sec", 0.0) or 0.0),
        float(solver_request.time_limit_sec),
    )
    used_iters = int(diagnostics.get("actual_iters_used", 0) or 0)
    budgets.solver_calls += 1
    budgets.time_used_sec += used_time
    budgets.iters_used += used_iters
    progress.solver_actions += 1
    progress.time_used_sec += used_time
    progress.iters_used += used_iters
    outcome = audit_outcome(
        before_working_eval=before_working_eval,
        after_working_eval=after_working_eval,
        before_best_eval=before_best_eval,
        after_best_eval=after_best_eval,
        contract_objective_layers=contract.stage_objective_layers,
        global_objective_layers=state.global_objective_layers,
        solver_diagnostics=diagnostics,
        solver_events=result.events,
    )
    _trace(state, "solver_result", {"working_solution": solution_summary(state.working_solution, instance, cfg), "diagnostics": diagnostics}, solver_action_index, contract.contract_id)
    _trace(state, "outcome_audit", outcome, solver_action_index, contract.contract_id)
    memory_item = state.memory.record_solver_action(contract.contract_id, solver_action_index, solver_payload, outcome["events"])
    _trace(state, "memory_update", memory_item, solver_action_index, contract.contract_id)
    return outcome


def _call_supervisor_review(
    client: LLMClientProtocol,
    state: AgentState,
    instance: Instance,
    cfg: Config,
    budgets: GlobalBudgetState,
    user_goal_text: str,
    relaxation_context: Dict[str, Any],
    contract: SearchContract,
    progress: ContractProgress,
    completion: Dict[str, Any],
    last_contract_events: List[str],
    allow_llm_fallback: bool,
) -> Dict[str, Any]:
    candidates = build_public_candidates(instance, cfg, state)
    working_summary = {} if state.working_solution is None else solution_summary(state.working_solution, instance, cfg)
    best_summary = None if state.best_solution is None else solution_summary(state.best_solution, instance, cfg)
    landscape = {} if state.working_solution is None else _public_landscape(
        build_destroy_landscape(state.working_solution, instance, cfg),
        build_insertion_landscape(state.working_solution, instance, cfg),
    )
    completed_result = {
        "completion_reason": completion.get("reason", ""),
        "completion_result": completion.get("result", ""),
        "last_outcome_events": list(last_contract_events),
    }
    observation = build_supervisor_review_observation(
        remaining_global_budget=budgets.remaining(),
        completed_contract=contract.as_dict(),
        completed_contract_progress=progress.as_dict(),
        completed_contract_result=completed_result,
        working_summary=working_summary,
        best_summary=best_summary,
        candidate_landscape=landscape,
        recent_memory=state.memory.for_supervisor(),
        candidates=candidates,
        relaxation_scale_context=relaxation_context,
    )
    prompt = get_supervisor_review_prompt(
        user_goal_text=user_goal_text,
        observation=observation,
        json_schema=schema_text(
            supervisor_review_schema_for_limits(observation["next_contract_resource_limits"])
        ),
    )
    payload = _call_validated(
        client,
        state,
        "supervisor_review",
        observation,
        prompt,
        lambda value: validate_supervisor_review(
            value,
            candidates,
            observation["evidence_items"],
            observation["memory_items"],
            cfg,
            budgets.remaining(),
        ),
        demo_supervisor_review,
        allow_llm_fallback,
        contract_id=contract.contract_id,
    )
    return payload["supervisor_decision"]


def _call_validated(
    client: LLMClientProtocol,
    state: AgentState,
    role: str,
    observation: Dict[str, Any],
    prompt: str,
    validator: Any,
    fallback_factory: Any,
    allow_fallback: bool,
    step_index: Optional[int] = None,
    contract_id: Optional[str] = None,
) -> Dict[str, Any]:
    _trace(state, f"{role}_observation", observation, step_index, contract_id)
    _trace(state, f"{role}_prompt", prompt, step_index, contract_id, payload_type="text")
    raw = ""
    try:
        raw = client.chat([{"role": "system", "content": get_system_prompt()}, {"role": "user", "content": prompt}], temperature=0.0)
        _trace(state, f"{role}_raw_output", raw, step_index, contract_id, payload_type="text")
        parsed = _parse_json(raw, role)
        validator(parsed)
    except Exception as exc:
        if not allow_fallback:
            raise LLMOutputError(f"{role} output failed validation: {exc}") from exc
        parsed = fallback_factory(observation)
        validator(parsed)
        state.llm_fallback_used = True
        _trace(state, f"{role}_fallback", {"reason": str(exc), "payload": parsed}, step_index, contract_id)
    _trace(state, f"{role}_validated_payload", parsed, step_index, contract_id)
    return parsed


def _parse_json(raw: str, role: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMOutputError(f"{role} returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LLMOutputError(f"{role} must return one JSON object")
    return value


def _contract_remaining(contract: SearchContract, progress: ContractProgress) -> Dict[str, Any]:
    policy = contract.completion_policy
    return {
        "solver_actions": max(0, int(policy["max_solver_actions"]) - progress.solver_actions),
        "time_sec": max(0.0, float(policy["max_time_sec"]) - progress.time_used_sec),
        "iters": max(0, int(policy["max_iters"]) - progress.iters_used),
        "min_solver_actions_remaining": max(0, int(policy["min_solver_actions"]) - progress.solver_actions),
    }


def _trace_contract_compile(state: AgentState, contract: SearchContract) -> None:
    _trace(state, "validated_feasibility_control", contract.feasibility_control, contract_id=contract.contract_id)
    _trace(state, "compiled_feasibility_policy", contract.feasibility_policy, contract_id=contract.contract_id)
    _trace(state, "compiled_contract", contract.as_dict(), contract_id=contract.contract_id)


def _eval(solution: AssignmentSolution, instance: Instance, config: Config) -> EvalResult:
    return evaluate(solution, instance, config, update_solution_schedule=True)


def _public_landscape(destroy: Dict[str, Any], insertion: Dict[str, Any]) -> Dict[str, Any]:
    candidate_stats = dict(insertion.get("candidate_stats", {}) or {})
    route_structure = dict(destroy.get("route_structure", {}) or {})
    return {
        "average_candidate_positions": float(candidate_stats.get("avg_candidate_positions", 0.0) or 0.0),
        "average_feasible_positions": float(candidate_stats.get("avg_feasible_positions", 0.0) or 0.0),
        "hard_to_insert_tasks": int(candidate_stats.get("no_feasible_tasks", 0) or 0),
        "zero_candidate_tasks": int(candidate_stats.get("zero_candidate_tasks", 0) or 0),
        "route_imbalance_level": str(route_structure.get("route_load_imbalance_level", "unknown")),
        "route_cost_imbalance_level": str(route_structure.get("route_cost_imbalance_level", "unknown")),
    }


def _trace(
    state: AgentState,
    event_type: str,
    payload: Any,
    step_index: Optional[int] = None,
    contract_id: Optional[str] = None,
    payload_type: str = "json",
) -> None:
    event = {
        "index": len(state.trace_events) + 1,
        "event_type": event_type,
        "payload_type": payload_type,
        "payload": payload,
        "step_index": step_index,
        "contract_id": contract_id,
    }
    state.trace_events.append(event)
    if state.trace_callback is not None:
        try:
            state.trace_callback(event)
        except Exception:
            pass


__all__ = ["AgentState", "GlobalBudgetState", "LLMOutputError", "OrchestratorError", "run_orchestrator"]
