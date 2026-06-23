from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

from .config import Budget, Config
from .contract_monitor import check_contract_completion, update_contract_progress
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
from .outcome_auditor import verify_alns_action, verify_initial_construction, verify_review_request
from .policy_validator import (
    validate_solver_decision,
    validate_supervisor_kickoff,
    validate_supervisor_review,
)
from .prompts import get_solver_prompt, get_supervisor_kickoff_prompt, get_supervisor_review_prompt, get_system_prompt
from .schemas import (
    schema_text,
    solver_decision_schema_for_candidates,
    supervisor_kickoff_schema_for_limits,
    supervisor_review_schema_for_limits,
)
from .solution import AssignmentSolution, EvalResult
from .tools import (
    ContractProgress,
    SearchContract,
    alns_policy_from_manifest,
    build_initial_solution_with_insertion,
    compile_contract,
    compile_global_objective,
    compile_solver_control,
    derive_solver_request,
    insertion_policy_from_manifest,
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
        observation_id="O0",
    )
    state.memory.record_observation(kickoff_observation)
    kickoff_prompt = get_supervisor_kickoff_prompt(
        user_goal_text=user_goal_text,
        observation=kickoff_observation,
        json_schema=schema_text(supervisor_kickoff_schema_for_limits(kickoff_observation["next_contract_resource_limits"])),
    )
    kickoff_payload = _call_validated(
        client,
        state,
        "supervisor_kickoff",
        kickoff_observation,
        kickoff_prompt,
        lambda value: validate_supervisor_kickoff(value, kickoff_observation, base_candidates, cfg, budgets.remaining()),
        demo_supervisor_kickoff,
        allow_llm_fallback,
    )
    kickoff_raw = kickoff_payload["supervisor_decision"]
    state.global_objective_layers = compile_global_objective(cfg, kickoff_raw["global_objective"])
    _trace(state, "global_objective_applied", state.global_objective_layers)
    contract_seq = 1
    state.active_contract = compile_contract(kickoff_raw["next_contract"], "C001", cfg, kickoff_observation)
    state.contract_progress = ContractProgress("C001")
    _trace_contract_compile(state, state.active_contract)

    solver_action_index = 0
    stop_reason = "global_budget_exhausted"
    while not budgets.exhausted():
        assert state.active_contract is not None and state.contract_progress is not None
        contract = state.active_contract
        progress = state.contract_progress
        candidates = build_public_candidates(instance, cfg, state)
        working_summary = _working_summary(state, instance, cfg)
        best_summary = _best_summary(state, instance, cfg)
        landscape = _landscape(state, instance, cfg)
        observation_id = f"O{solver_action_index + 1}"
        solver_observation = build_solver_observation(
            active_contract=contract.as_dict(),
            contract_progress=progress.as_dict(),
            remaining_contract_resources=_contract_remaining(contract, progress),
            remaining_global_budget=budgets.remaining(),
            working_summary=working_summary,
            best_summary=best_summary,
            candidate_landscape=landscape,
            recent_memory=state.memory.for_solver(contract),
            candidates=candidates,
            last_verification=state.memory.last_verification(),
            observation_id=observation_id,
            step_index=solver_action_index,
        )
        state.memory.record_observation(solver_observation)
        solver_schema = solver_decision_schema_for_candidates(candidates, solver_observation)
        solver_prompt = get_solver_prompt(
            user_goal_text=user_goal_text,
            observation=solver_observation,
            json_schema=schema_text(solver_schema),
        )
        solver_payload = _call_validated(
            client,
            state,
            "solver",
            solver_observation,
            solver_prompt,
            lambda value: validate_solver_decision(value, solver_observation, candidates=candidates),
            demo_solver_decision,
            allow_llm_fallback,
            step_index=solver_action_index,
            contract_id=contract.contract_id,
        )
        budgets.step_calls += 1
        decision_id = state.memory.record_decision(solver_payload, solver_observation)
        trace_id = f"X{solver_action_index + 1}"
        manifest = compile_solver_control(
            solver_payload,
            contract,
            candidates,
            solver_observation,
            decision_id=decision_id,
            manifest_id=f"R{solver_action_index + 1}",
            trace_id=trace_id,
        )
        _trace(state, "runtime_control_manifest", manifest.as_dict(), solver_action_index, contract.contract_id)
        decision = solver_payload["solver_decision"]
        action = decision["action"]

        if action == "request_supervisor_review":
            trace = {"trace_id": trace_id, "kind": "review_request"}
            verification = verify_review_request(
                solver_payload,
                contract,
                state.memory.recent_verifications(contract.contract_id),
                manifest=manifest,
                decision_id=decision_id,
                verification_id=f"V{solver_action_index + 1}",
                trace_id=trace_id,
            )
        elif action == "construct_initial":
            trace, verification = _execute_initial_action(
                state,
                instance,
                cfg,
                manifest,
                budgets,
                rng_seed,
                solver_action_index,
                contract,
                decision_id,
                trace_id,
            )
        elif action == "run_alns":
            trace, verification = _execute_alns_action(
                state,
                instance,
                cfg,
                manifest,
                budgets,
                rng_seed,
                solver_action_index,
                contract,
                decision_id,
                trace_id,
            )
        else:
            raise OrchestratorError(f"unsupported solver action: {action}")

        _trace(state, "execution_trace", trace, solver_action_index, contract.contract_id)
        memory_item = state.memory.record_verified_action(solver_observation, solver_payload, manifest, trace, verification)
        verification = dict(memory_item["verification"])
        _trace(state, "outcome_verification", verification, solver_action_index, contract.contract_id)
        _trace(state, "memory_update", memory_item, solver_action_index, contract.contract_id)
        update_contract_progress(progress, verification)
        completion = check_contract_completion(
            contract,
            progress,
            state.memory.recent_verifications(contract.contract_id, limit=20),
            {"working": _working_summary(state, instance, cfg), "best_feasible": _best_summary(state, instance, cfg)},
        )
        _trace(state, "contract_progress", progress.as_dict(), solver_action_index, contract.contract_id)
        _trace(state, "contract_completion_check", completion, solver_action_index, contract.contract_id)

        if completion["completed"]:
            contract_memory = state.memory.record_contract_summary(contract, progress, completion)
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
                allow_llm_fallback,
                review_index=solver_action_index + 1,
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
    final_summary = solution_summary(
        final_solution, instance, cfg,
        contract_objective_layers=(state.active_contract.objective_layers if state.active_contract else state.global_objective_layers),
        global_objective_layers=state.global_objective_layers,
    )
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
    manifest: Any,
    budgets: GlobalBudgetState,
    rng_seed: int,
    solver_action_index: int,
    contract: SearchContract,
    decision_id: str,
    trace_id: str,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    insertion_policy = insertion_policy_from_manifest(manifest)
    _trace(state, "compiled_initial_policy", insertion_policy.as_dict(), solver_action_index, contract.contract_id)
    result = build_initial_solution_with_insertion(instance, cfg, insertion_policy, rng_seed, manifest=manifest.as_dict())
    state.working_solution = result.solution
    state.best_solution = result.solution.clone(deep=True) if result.evaluation.is_feasible else None
    budgets.solver_calls += 1
    trace = dict(result.trace)
    trace["trace_id"] = trace_id
    result.trace["trace_id"] = trace_id
    verification = verify_initial_construction(
        result,
        contract,
        manifest,
        decision_id=decision_id,
        verification_id=f"V{solver_action_index + 1}",
    )
    _trace(state, "initial_insertion_result", {"result": solution_summary(result.solution, instance, cfg, contract_objective_layers=contract.objective_layers, global_objective_layers=state.global_objective_layers), "trace": trace}, solver_action_index, contract.contract_id)
    return trace, verification


def _execute_alns_action(
    state: AgentState,
    instance: Instance,
    cfg: Config,
    manifest: Any,
    budgets: GlobalBudgetState,
    rng_seed: int,
    solver_action_index: int,
    contract: SearchContract,
    decision_id: str,
    trace_id: str,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    if state.working_solution is None:
        raise OrchestratorError("run_alns requested before a working solution exists")
    compiled_policy = alns_policy_from_manifest(manifest)
    solver_request = derive_solver_request(contract, state.contract_progress or ContractProgress(contract.contract_id))
    _trace(state, "compiled_solver_policy", compiled_policy.as_dict(), solver_action_index, contract.contract_id)
    _trace(state, "solver_request", solver_request.as_dict(), solver_action_index, contract.contract_id)
    before_working_eval = _eval(state.working_solution, instance, cfg)
    before_global_best_eval = None if state.best_solution is None else _eval(state.best_solution, instance, cfg)
    result = solve_assignment(
        instance=instance,
        init_solution=state.working_solution,
        config=cfg,
        budget=Budget(time_limit_sec=solver_request.time_limit_sec, max_iters=solver_request.max_iters),
        policy=compiled_policy,
        rng_seed=rng_seed + solver_action_index + 1,
        contract_objective_layers=contract.objective_layers,
        feasibility_policy=contract.feasibility_policy,
        global_objective_layers=state.global_objective_layers,
        trace_id=trace_id,
    )
    result.trace["trace_id"] = trace_id
    state.working_solution = result.working_solution
    after_working_eval = _eval(state.working_solution, instance, cfg)
    action_best_eval = None if result.action_best_feasible is None else _eval(result.action_best_feasible, instance, cfg)
    candidate_global = result.global_best_feasible
    if candidate_global is not None:
        candidate_global_eval = _eval(candidate_global, instance, cfg)
        if before_global_best_eval is None or compare_quality(candidate_global_eval, before_global_best_eval, state.global_objective_layers) < 0:
            state.best_solution = candidate_global.clone(deep=True)
    after_global_best_eval = None if state.best_solution is None else _eval(state.best_solution, instance, cfg)
    diagnostics = dict(result.diagnostics)
    diagnostics["accepted_trial_count"] = int(result.accepted_trial_count)
    diagnostics["rejected_trial_count"] = int(result.rejected_trial_count)
    used_time = min(float(diagnostics.get("actual_time_used_sec", 0.0) or 0.0), float(solver_request.time_limit_sec))
    used_iters = int(diagnostics.get("actual_iters_used", 0) or 0)
    budgets.solver_calls += 1
    budgets.time_used_sec += used_time
    budgets.iters_used += used_iters
    if state.contract_progress is not None:
        state.contract_progress.time_used_sec += used_time
    verification = verify_alns_action(
        before_working_eval=before_working_eval,
        after_working_eval=after_working_eval,
        before_best_feasible_eval=before_working_eval if before_working_eval.is_feasible else None,
        after_action_best_eval=action_best_eval,
        before_global_best_eval=before_global_best_eval,
        after_global_best_eval=after_global_best_eval,
        trace=dict(result.trace),
        contract=contract,
        manifest=manifest,
        decision_id=decision_id,
        verification_id=f"V{solver_action_index + 1}",
        global_objective_layers=state.global_objective_layers,
    )
    _trace(state, "solver_result", {"working_solution": solution_summary(state.working_solution, instance, cfg, contract_objective_layers=contract.objective_layers, global_objective_layers=state.global_objective_layers), "diagnostics": diagnostics}, solver_action_index, contract.contract_id)
    return dict(result.trace), verification


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
    allow_llm_fallback: bool,
    *,
    review_index: int,
) -> Dict[str, Any]:
    candidates = build_public_candidates(instance, cfg, state)
    observation = build_supervisor_review_observation(
        remaining_global_budget=budgets.remaining(),
        completed_contract=contract.as_dict(),
        completed_contract_progress=progress.as_dict(),
        completed_contract_result=completion,
        working_summary=_working_summary(state, instance, cfg),
        best_summary=_best_summary(state, instance, cfg),
        recent_memory=state.memory.for_supervisor(),
        candidates=candidates,
        relaxation_scale_context=relaxation_context,
        verifications=state.memory.recent_verifications(contract.contract_id, limit=20),
        observation_id=f"O_review_{review_index}",
    )
    state.memory.record_observation(observation)
    prompt = get_supervisor_review_prompt(
        user_goal_text=user_goal_text,
        observation=observation,
        json_schema=schema_text(supervisor_review_schema_for_limits(observation["next_contract_resource_limits"])),
    )
    payload = _call_validated(
        client,
        state,
        "supervisor_review",
        observation,
        prompt,
        lambda value: validate_supervisor_review(value, observation, candidates, cfg, budgets.remaining()),
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
    except Exception as first_exc:
        repair_exc: Optional[Exception] = None
        if raw:
            try:
                repair_prompt = _repair_prompt(prompt, raw, first_exc)
                _trace(state, f"{role}_repair_prompt", repair_prompt, step_index, contract_id, payload_type="text")
                repaired_raw = client.chat(
                    [{"role": "system", "content": get_system_prompt()}, {"role": "user", "content": repair_prompt}],
                    temperature=0.0,
                )
                _trace(state, f"{role}_repair_raw_output", repaired_raw, step_index, contract_id, payload_type="text")
                parsed = _parse_json(repaired_raw, f"{role}_repair")
                validator(parsed)
                _trace(state, f"{role}_repair_validated_payload", parsed, step_index, contract_id)
            except Exception as exc:
                repair_exc = exc
                _trace(
                    state,
                    f"{role}_repair_failed",
                    {"first_error": str(first_exc), "repair_error": str(exc)},
                    step_index,
                    contract_id,
                )
        else:
            repair_exc = first_exc

        if repair_exc is not None:
            reason = f"first attempt: {first_exc}; repair attempt: {repair_exc}"
            if not allow_fallback:
                raise LLMOutputError(f"{role} output failed validation after repair: {reason}") from repair_exc
            parsed = fallback_factory(observation)
            validator(parsed)
            state.llm_fallback_used = True
            _trace(state, f"{role}_fallback", {"reason": reason, "payload": parsed}, step_index, contract_id)
    _trace(state, f"{role}_validated_payload", parsed, step_index, contract_id)
    return parsed


def _repair_prompt(original_prompt: str, original_raw: str, validation_error: Exception) -> str:
    return (
        f"{original_prompt}\n\n"
        "REPAIR REQUEST:\n"
        "Your previous JSON failed parsing or validation. Return one corrected JSON object only. "
        "Keep the same observation and obey the exact output schema above.\n"
        f"VALIDATION ERROR:\n{validation_error}\n\n"
        f"PREVIOUS OUTPUT:\n{original_raw}"
    )


def _parse_json(raw: str, role: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMOutputError(f"{role} returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise LLMOutputError(f"{role} must return one JSON object")
    return value


def _contract_remaining(contract: SearchContract, progress: ContractProgress) -> Dict[str, Any]:
    policy = contract.resource_policy
    return {
        "actions": max(0, int(policy["max_actions"]) - progress.solver_actions),
        "time_sec": max(0.0, float(policy["max_time_sec"]) - progress.time_used_sec),
        "iters": max(0, int(policy["max_iters"]) - progress.iters_used),
        "min_actions_remaining": max(0, int(policy["min_actions"]) - progress.solver_actions),
    }


def _trace_contract_compile(state: AgentState, contract: SearchContract) -> None:
    _trace(state, "validated_feasibility_control", contract.feasibility_control, contract_id=contract.contract_id)
    _trace(state, "compiled_feasibility_policy", contract.feasibility_policy, contract_id=contract.contract_id)
    _trace(state, "compiled_contract", contract.as_dict(), contract_id=contract.contract_id)


def _working_summary(state: AgentState, instance: Instance, cfg: Config) -> Dict[str, Any]:
    contract_layers = state.active_contract.objective_layers if state.active_contract else state.global_objective_layers
    if state.working_solution is None:
        empty = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
        return solution_summary(empty, instance, cfg, contract_objective_layers=contract_layers, global_objective_layers=state.global_objective_layers)
    return solution_summary(state.working_solution, instance, cfg, contract_objective_layers=contract_layers, global_objective_layers=state.global_objective_layers)


def _best_summary(state: AgentState, instance: Instance, cfg: Config) -> Optional[Dict[str, Any]]:
    if state.best_solution is None:
        return None
    contract_layers = state.active_contract.objective_layers if state.active_contract else state.global_objective_layers
    return solution_summary(state.best_solution, instance, cfg, contract_objective_layers=contract_layers, global_objective_layers=state.global_objective_layers)


def _landscape(state: AgentState, instance: Instance, cfg: Config) -> Dict[str, Any]:
    sol = state.working_solution
    if sol is None:
        sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    return _public_landscape(build_destroy_landscape(sol, instance, cfg), build_insertion_landscape(sol, instance, cfg))


def _eval(solution: AssignmentSolution, instance: Instance, config: Config) -> EvalResult:
    return evaluate(solution, instance, config, update_solution_schedule=True)


def _public_landscape(destroy: Dict[str, Any], insertion: Dict[str, Any]) -> Dict[str, Any]:
    candidate_stats = dict(insertion.get("candidate_stats", {}) or {})
    route_structure = dict(destroy.get("route_structure", {}) or {})
    return {
        "unassigned_count": int(insertion.get("unassigned_count", 0) or 0),
        "assigned_count": int(insertion.get("assigned_count", 0) or 0),
        "candidate_stats": candidate_stats,
        "task_pressure": dict(insertion.get("task_pressure", {}) or {}),
        "target_buckets": dict(insertion.get("target_buckets", {}) or {}),
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
