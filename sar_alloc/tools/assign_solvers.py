"""Weighted ALNS solver with separate operator-level scoring profiles.

Reinsert-task score decides which task to insertion next. Insert score decides the
order of filtered insertion positions. Insertion scans the full ranked candidate
sets.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from ..config import Budget, Config
from ..console import info, subsection
from ..evaluator import build_objective_keys, compare_quality, evaluate as _evaluate_raw
from ..feasibility_policy import check_feasibility_admissibility
from ..models import Instance
from ..operators import (
    DestroyPolicy,
    LandscapeFeatures,
    CompiledALNSPolicy,
)
from ..operators.destroy import (
    DESTROY_OPERATORS,
    DestroyMove,
    DestroyOperator,
    compute_destroy_strength,
    enumerate_random_removal,
)
from ..operators.insertion import InsertionContext, run_insertion_kernel
from ..protected_metrics import (
    ProtectedMetricBound,
    check_protected_metrics,
    evaluation_quality,
)
from ..solution import AssignmentSolution, EvalResult


@dataclass
class _EvalStats:
    n: int = 0
    t: float = 0.0


EVAL_STATS = _EvalStats()


@dataclass(frozen=True)
class ALNSResult:
    final_current: AssignmentSolution
    action_best_feasible: Optional[AssignmentSolution]
    global_best_feasible: Optional[AssignmentSolution]
    working_solution: AssignmentSolution
    accepted_trial_count: int
    rejected_trial_count: int
    events: List[str]
    trace: Dict[str, Any]
    diagnostics: Dict[str, Any]


ALNSExecutionResult = ALNSResult


def evaluate(*args, **kwargs):  # noqa: F811
    t0 = time.perf_counter()
    ev = _evaluate_raw(*args, **kwargs)
    EVAL_STATS.n += 1
    EVAL_STATS.t += time.perf_counter() - t0
    return ev


def solve_assignment(
    instance: Instance,
    init_solution: AssignmentSolution,
    config: Config,
    budget: Budget,
    policy: CompiledALNSPolicy,
    rng_seed: int = 0,
    contract_objective_layers: Optional[List[Dict[str, Any]]] = None,
    feasibility_policy: Optional[Dict[str, Any]] = None,
    global_objective_layers: Optional[List[Dict[str, Any]]] = None,
    trace_id: str = "X_solver",
    protected_metric_bounds: Optional[List[ProtectedMetricBound]] = None,
    runtime_target: Optional[Dict[str, Any]] = None,
) -> ALNSResult:
    """Run weighted ALNS from an incumbent using an already validated policy."""
    rng = random.Random(int(rng_seed))

    cur = init_solution.clone(deep=True)
    cur.normalize(instance)
    cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)
    subsection("ALNS START")
    info(
        f"acceptance={policy.acceptance_policy.mode} "
        f"strength_ratio={float(policy.destroy_policy.remove_ratio)} "
        f"time_limit={budget.time_limit_sec} "
        f"iters={budget.max_iters} "
        f"init_feasible={_bool_text(cur_ev.is_feasible)} "
        f"init_contract_key={build_objective_keys(cur_ev, contract_objective_layers or _config_objective_layers(config), global_objective_layers or _config_objective_layers(config))['contract']['key']}"
    )

    return _solve_weighted_alns(
        instance,
        cur,
        cur_ev,
        config,
        budget,
        policy,
        rng,
        contract_objective_layers=contract_objective_layers
        or _config_objective_layers(config),
        feasibility_policy=feasibility_policy or {"mode": "strict"},
        global_objective_layers=global_objective_layers
        or _config_objective_layers(config),
        trace_id=trace_id,
        protected_metric_bounds=list(protected_metric_bounds or []),
        runtime_target=dict(runtime_target or {}),
    )


def _solve_weighted_alns(
    instance: Instance,
    cur: AssignmentSolution,
    cur_ev: EvalResult,
    config: Config,
    budget: Budget,
    policy: CompiledALNSPolicy,
    rng: random.Random,
    *,
    contract_objective_layers: List[Dict[str, Any]],
    feasibility_policy: Dict[str, Any],
    global_objective_layers: List[Dict[str, Any]],
    trace_id: str,
    protected_metric_bounds: List[ProtectedMetricBound],
    runtime_target: Dict[str, Any],
) -> ALNSResult:
    destroy_ops: Dict[str, DestroyOperator] = dict(DESTROY_OPERATORS)
    destroy_priors = {
        name: max(0.1, float(score))
        for name, score in policy.destroy_policy.operator_weights.items()
    }
    prior_mix_lambda = float(policy.prior_mix_lambda)

    d_w = {name: 1.0 for name in destroy_ops}

    d_score = {name: 0.0 for name in d_w}

    d_used = {name: 0 for name in d_w}

    if budget.max_iters is not None:
        segment_len = _clamp_int(int(0.10 * int(budget.max_iters)), 10, 200)
    else:
        segment_len = 50

    reaction = float(policy.reaction_factor)
    accept_level = float(policy.acceptance_policy.accept_level)
    temperature = 0.05 + 0.50 * accept_level
    cooling = _clamp_float(0.999 - 0.02 * accept_level, 0.90, 0.9999)
    contract_start_solution = cur.clone(deep=True)
    contract_start_eval = cur_ev
    contract_start_constraint_report = cur_ev.constraint_report
    initial_solution_feasible = bool(cur_ev.is_feasible)
    initial_protected_check = check_protected_metrics(
        evaluation_quality(cur_ev), protected_metric_bounds
    )
    initial_working_objective_keys = build_objective_keys(
        cur_ev, contract_objective_layers, global_objective_layers
    )

    initial_is_eligible = bool(cur_ev.is_feasible and initial_protected_check.passed)
    action_best_feasible: Optional[AssignmentSolution] = (
        cur.clone(deep=True) if initial_is_eligible else None
    )
    action_best_feasible_ev: Optional[EvalResult] = (
        cur_ev if initial_is_eligible else None
    )
    global_best_feasible: Optional[AssignmentSolution] = (
        cur.clone(deep=True) if initial_is_eligible else None
    )
    global_best_feasible_ev: Optional[EvalResult] = (
        cur_ev if initial_is_eligible else None
    )

    best_update_iters: List[int] = []
    best_update_objective_keys: List[Dict[str, Any]] = []
    last_acceptance_decision: Optional[Dict[str, Any]] = None
    destroy_operator_stats = _init_destroy_operator_stats(d_w.keys())
    insertion_operator_summary = _init_insertion_operator_summary(
        policy.insertion_policy.operator_weights.keys()
    )
    iteration_trace: List[Dict[str, Any]] = []
    last_destroy_move: Optional[Dict[str, Any]] = None
    last_insertion: Optional[Dict[str, Any]] = None
    accepted_trial_count = 0
    rejected_trial_count = 0
    feasibility_rejection_reasons: Dict[str, int] = {}
    protected_metric_rejections = 0
    protected_metric_rejection_reasons: Dict[str, int] = {}
    events: List[str] = []
    trial_flow = {
        "candidate_trials": 0,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 0,
        "acceptance_rejected": 0,
        "accepted_trials": 0,
        "global_best_improved_trials": 0,
    }
    repair_failure_reasons: Dict[str, int] = {}
    removed_task_count_sum = 0.0

    iteration = 0
    started_at = time.perf_counter()

    while _budget_ok(budget, started_at, iteration):
        iteration += 1
        before_unassigned = {int(tid) for tid in cur.unassigned}
        before_focus_values = _focus_metric_values(cur_ev, runtime_target)
        d_final = _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda)
        d_name = _roulette_select(d_final, rng)

        move = select_destroy_move(
            sol=cur,
            instance=instance,
            config=config,
            policy=policy.destroy_policy,
            operator=destroy_ops[d_name],
            rng=rng,
            runtime_target=runtime_target,
        )
        actual_d_name = str(move.operator_name)
        d_used[actual_d_name] += 1
        removed = list(int(tid) for tid in move.task_ids)
        removed_task_count_sum += float(len(removed))
        last_destroy_move = move.as_dict()

        partial = cur.clone(deep=True)
        _remove_tasks(partial, removed)
        partial.solver_diagnostics = {"last_destroy_move": last_destroy_move}
        partial.normalize(instance)

        candidate_tasks = list(
            dict.fromkeys(removed + sorted(int(tid) for tid in partial.unassigned))
        )
        trial = run_insertion_kernel(
            partial_solution=partial,
            candidate_tasks=candidate_tasks,
            insertion_policy=policy.insertion_policy,
            context=InsertionContext(
                kind="alns",
                feasibility_mode=str(feasibility_policy.get("mode", "strict")),
                target_task_ids=tuple(
                    int(tid) for tid in runtime_target.get("task_ids", []) or []
                ),
                target_agent_ids=tuple(
                    int(aid) for aid in runtime_target.get("agent_ids", []) or []
                ),
            ),
            instance=instance,
            config=config,
            rng=rng,
        )
        trial.solver_diagnostics["last_destroy_move"] = last_destroy_move
        last_insertion = dict(
            (getattr(trial, "solver_diagnostics", {}) or {}).get("last_insertion", {})
            or {}
        )
        trial_flow["candidate_trials"] += 1
        if int(last_insertion.get("inserted_count", 0) or 0) == 0:
            trial_flow["hard_filter_failed"] += 1
            repair_failure_reasons["no_reinserted_task"] = (
                repair_failure_reasons.get("no_reinserted_task", 0) + 1
            )
        for name, count in dict(
            last_insertion.get("failure_breakdown", {}) or {}
        ).items():
            if int(count):
                repair_failure_reasons[str(name)] = repair_failure_reasons.get(
                    str(name), 0
                ) + int(count)

        trial.normalize(instance)
        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)
        iter_target_progress = _target_progress_from_snapshot(
            before_unassigned=before_unassigned,
            after_unassigned={int(tid) for tid in trial.unassigned},
            before_focus_values=before_focus_values,
            after_eval=ev_trial,
            runtime_target=runtime_target,
        )
        protected_check = check_protected_metrics(
            evaluation_quality(ev_trial), protected_metric_bounds
        )

        feasibility_decision = check_feasibility_admissibility(
            cur_ev.constraint_report,
            ev_trial.constraint_report,
            feasibility_policy,
        )
        events.extend(feasibility_decision.events)
        acceptance = _AcceptanceDecision(
            compare_result=0,
            accepted=False,
            accept_mode=policy.acceptance_policy.mode,
            feasibility_admissible=feasibility_decision.admissible,
            accept_scope=feasibility_decision.accept_scope,
            feasibility_reason=feasibility_decision.reason,
        )
        rejection_reason = ""
        if feasibility_decision.admissible and protected_check.passed:
            trial_flow["admissible_trials"] += 1
            acceptance = _alns_accept(
                cur_ev=cur_ev,
                trial_ev=ev_trial,
                objective_layers=contract_objective_layers,
                mode=policy.acceptance_policy.mode,
                rng=rng,
                temperature=temperature,
                accept_level=accept_level,
                feasibility_admissible=True,
                accept_scope=feasibility_decision.accept_scope,
                feasibility_reason=feasibility_decision.reason,
            )
        elif not feasibility_decision.admissible:
            trial_flow["feasibility_rejected"] += 1
            rejection_reason = feasibility_decision.reason
            feasibility_rejection_reasons[feasibility_decision.reason] = (
                feasibility_rejection_reasons.get(feasibility_decision.reason, 0) + 1
            )
        else:
            protected_metric_rejections += 1
            trial_flow["protected_metric_rejected"] += 1
            rejection_reason = "protected_metric_violated"
            events.append("protected_metric_violated")
            for violation in protected_check.violations:
                metric = str(violation["metric"])
                protected_metric_rejection_reasons[metric] = (
                    protected_metric_rejection_reasons.get(metric, 0) + 1
                )
        accepted = acceptance.accepted
        last_acceptance_decision = acceptance.as_dict()
        if iteration % 100 == 0:
            message = (
                f"[ALNS] iter={iteration} "
                f"destroy={actual_d_name} insertion=kernel "
                f"accepted={_bool_text(accepted)} feasible={_bool_text(ev_trial.is_feasible)} "
                f"contract_key={build_objective_keys(ev_trial, contract_objective_layers, global_objective_layers)['contract']['key']} "
                f"unassigned={len(trial.unassigned)}"
            )
            subsection("ALNS ITERATION")
            info(message)

        reward = 0.0
        if accepted:
            cur = trial
            cur_ev = ev_trial
            accepted_trial_count += 1
            trial_flow["accepted_trials"] += 1
            reward = max(reward, 0.2)
        else:
            rejected_trial_count += 1
            if feasibility_decision.admissible and protected_check.passed:
                trial_flow["acceptance_rejected"] += 1
                rejection_reason = "acceptance_rejected"

        if (
            protected_check.passed
            and ev_trial.is_feasible
            and (
                action_best_feasible_ev is None
                or compare_quality(
                    ev_trial, action_best_feasible_ev, contract_objective_layers
                )
                < 0
            )
        ):
            action_best_feasible = trial.clone(deep=True)
            action_best_feasible_ev = ev_trial

        best_improved = False
        if (
            protected_check.passed
            and ev_trial.is_feasible
            and (
                global_best_feasible_ev is None
                or compare_quality(
                    ev_trial, global_best_feasible_ev, global_objective_layers
                )
                < 0
            )
        ):
            global_best_feasible = trial.clone(deep=True)
            global_best_feasible_ev = ev_trial
            best_update_iters.append(iteration)
            best_update_objective_keys.append(
                build_objective_keys(
                    global_best_feasible_ev,
                    contract_objective_layers,
                    global_objective_layers,
                )
            )
            reward = max(reward, 5.0)
            best_improved = True
            trial_flow["global_best_improved_trials"] += 1

        iteration_trace.append(
            {
                "iteration": int(iteration),
                "destroy_operator": actual_d_name,
                "insertion_operator": "kernel",
                "accepted": bool(accepted),
                "current_objective_keys": build_objective_keys(
                    cur_ev, contract_objective_layers, global_objective_layers
                ),
                "action_best_objective_keys": (
                    None
                    if action_best_feasible_ev is None
                    else build_objective_keys(
                        action_best_feasible_ev,
                        contract_objective_layers,
                        global_objective_layers,
                    )
                ),
                "global_best_objective_keys": (
                    None
                    if global_best_feasible_ev is None
                    else build_objective_keys(
                        global_best_feasible_ev,
                        contract_objective_layers,
                        global_objective_layers,
                    )
                ),
                "violation_total": float(ev_trial.get_metric("violation_total")),
                "violation_ratio_by_type": dict(
                    ev_trial.constraint_report.violation_ratio_by_type
                ),
                "feasibility_reason": feasibility_decision.reason,
                "protected_metric_passed": protected_check.passed,
                "protected_metric_violations": list(protected_check.violations),
                "rejection_reason": rejection_reason or None,
                "destroy_target_metadata": dict(
                    (last_destroy_move or {}).get("metadata", {}) or {}
                ),
                "target_insertion": _compact_insertion_target(last_insertion),
                "target_progress": iter_target_progress,
            }
        )

        d_score[actual_d_name] += reward
        _accumulate_destroy_operator_stats(
            destroy_operator_stats,
            move=move,
            accepted=accepted,
            best_improved=best_improved,
            reward=reward,
        )
        _accumulate_insertion_operator_summary(
            insertion_operator_summary,
            operator_name=str(last_insertion.get("operator", "kernel")),
            last_insertion=last_insertion,
            accepted=accepted,
            best_improved=best_improved,
        )

        if policy.acceptance_policy.mode == "sa":
            temperature = max(1e-9, temperature * cooling)

        if iteration % segment_len == 0:
            _update_weights(d_w, d_score, d_used, reaction)
            _reset_segment_scores(d_score, d_used)

    final_current = cur.clone(deep=True)
    evaluate(final_current, instance, config, update_solution_schedule=True)
    if action_best_feasible is not None:
        evaluate(action_best_feasible, instance, config, update_solution_schedule=True)
    if global_best_feasible is not None:
        evaluate(global_best_feasible, instance, config, update_solution_schedule=True)
    if action_best_feasible is not None:
        working_solution = action_best_feasible.clone(deep=True)
        returned_source = "action_best_feasible"
    elif protected_metric_bounds:
        working_solution = contract_start_solution.clone(deep=True)
        evaluate(working_solution, instance, config, update_solution_schedule=True)
        returned_source = "contract_start_solution_due_to_protected_bounds"
    else:
        working_solution = final_current.clone(deep=True)
        returned_source = "final_current_no_feasible"
    returned_protected_check = check_protected_metrics(
        evaluation_quality(working_solution.eval), protected_metric_bounds
    )
    if not returned_protected_check.passed:
        raise AssertionError(
            "returned working solution violates protected metric bounds"
        )
    actual_time_used_sec = max(0.0, time.perf_counter() - started_at)
    trace = _build_execution_trace(
        trace_id=trace_id,
        total_iters=iteration,
        destroy_operator_summary=_finalize_destroy_operator_stats(
            destroy_operator_stats
        ),
        insertion_operator_summary=_finalize_insertion_operator_summary(
            insertion_operator_summary
        ),
        trial_flow=trial_flow,
        rejection_reasons={
            **feasibility_rejection_reasons,
            **(
                {"protected_metric_violated": protected_metric_rejections}
                if protected_metric_rejections
                else {}
            ),
        },
        repair_failure_reasons=repair_failure_reasons,
        removed_task_count_sum=removed_task_count_sum,
        operator_prior_trace={
            "llm_prior": dict(destroy_priors),
            "exploration_floor": 0.1,
            "adaptive_weight_before": dict(d_w),
            "final_sampling_weight": _blend_operator_weights(
                d_w, destroy_priors, prior_mix_lambda
            ),
        },
        runtime_target=runtime_target,
        feasibility_policy=feasibility_policy,
        feasibility_rejection_reasons=feasibility_rejection_reasons,
        final_constraint_report=working_solution.eval.constraint_report,
        initial_constraint_report=contract_start_constraint_report,
        protected_metric_bounds=[bound.as_dict() for bound in protected_metric_bounds],
        protected_metric_rejections=protected_metric_rejections,
        protected_metric_rejection_reasons=protected_metric_rejection_reasons,
        returned_protected_result=returned_protected_check.as_dict(),
        actual_time_used_sec=actual_time_used_sec,
        returned_solution_source=returned_source,
        iteration_trace=iteration_trace,
        last_insertion=last_insertion,
        before_solution=contract_start_solution,
        after_solution=working_solution,
        before_eval=contract_start_eval,
        after_eval=working_solution.eval,
    )
    diagnostics = _build_solver_diagnostics(
        policy=policy,
        total_iters=iteration,
        actual_time_used_sec=actual_time_used_sec,
        best_update_iters=best_update_iters,
        best_update_objective_keys=best_update_objective_keys,
        returned_solution_source=returned_source,
        initial_solution_feasible=initial_solution_feasible,
        returned_solution_feasible=bool(
            getattr(working_solution.eval, "is_feasible", False)
        ),
        last_acceptance_decision=last_acceptance_decision,
        last_destroy_move=last_destroy_move,
        destroy_operator_summary=trace["destroy"]["selected_operator_counts"],
        insertion_operator_summary=trace["repair"],
        iteration_trace=iteration_trace,
        last_insertion=last_insertion,
        operator_weights={
            "destroy_operators": {
                "adaptive": d_w,
                "llm_score_prior": destroy_priors,
                "fused_final": _blend_operator_weights(
                    d_w, destroy_priors, prior_mix_lambda
                ),
            },
            "insertion_operators": {
                "llm_weights": policy.insertion_policy.operator_weights
            },
        },
        feasibility_policy=feasibility_policy,
        final_constraint_report=working_solution.eval.constraint_report,
        feasibility_rejection_reasons=feasibility_rejection_reasons,
        protected_metric_rejections=protected_metric_rejections,
        protected_metric_rejection_reasons=protected_metric_rejection_reasons,
        protected_metric_bounds=[bound.as_dict() for bound in protected_metric_bounds],
        returned_protected_result=returned_protected_check.as_dict(),
        execution_trace=trace,
    )
    diagnostics["solution_flow"] = {
        "initial_working": {"objective_keys": initial_working_objective_keys},
        "final_current": {
            "objective_keys": build_objective_keys(
                final_current.eval, contract_objective_layers, global_objective_layers
            ),
            "is_feasible": bool(final_current.eval.is_feasible),
        },
        "action_best_feasible": (
            None
            if action_best_feasible is None
            else {
                "objective_keys": build_objective_keys(
                    action_best_feasible.eval,
                    contract_objective_layers,
                    global_objective_layers,
                ),
                "is_feasible": True,
            }
        ),
        "returned_solution_source": returned_source,
        "protected_metric_result": returned_protected_check.as_dict(),
    }
    subsection("ALNS DONE")
    info(
        f"returned_source={returned_source} "
        f"total_iters={iteration} "
        f"best_update_count={len(best_update_iters)} "
        f"actual_time_used_sec={round(actual_time_used_sec, 4)} "
        f"returned_feasible={_bool_text(getattr(working_solution.eval, 'is_feasible', False))}"
    )
    final_current.solver_diagnostics = diagnostics
    working_solution.solver_diagnostics = diagnostics
    if action_best_feasible is not None:
        action_best_feasible.solver_diagnostics = diagnostics
    if global_best_feasible is not None:
        global_best_feasible.solver_diagnostics = diagnostics
    return ALNSResult(
        final_current=final_current,
        action_best_feasible=action_best_feasible,
        global_best_feasible=global_best_feasible,
        working_solution=working_solution,
        accepted_trial_count=int(accepted_trial_count),
        rejected_trial_count=int(rejected_trial_count),
        events=_dedupe_events(events),
        trace=trace,
        diagnostics=diagnostics,
    )


def select_destroy_move(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    operator: DestroyOperator,
    rng: random.Random,
    runtime_target: Optional[Dict[str, Any]] = None,
) -> DestroyMove:
    target = dict(runtime_target or {})
    assigned = list(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned:
        return _with_target_metadata(
            DestroyMove(
                operator_name="random_removal",
                shape="random",
                task_ids=(),
                affected_routes=(),
                features=LandscapeFeatures(
                    cost_pressure=0.0,
                    priority_loss=0.0,
                    scarcity_pressure=0.0,
                    coupling_pressure=0.0,
                    mobility_opportunity=0.0,
                    route_balance_pressure=0.0,
                    violation_pressure=0.0,
                    regret_pressure=0.0,
                    bottleneck_pressure=0.0,
                ),
                score=0.0,
                metadata={"target_k": 0},
            ),
            **_target_destroy_metadata((), target, 0, 0, fallback=bool(_has_local_target(target))),
        )
    strength = compute_destroy_strength(sol, policy.remove_ratio)
    moves = operator(sol, instance, config, policy, strength, rng)
    if not moves:
        moves = enumerate_random_removal(sol, instance, config, policy, strength, rng)
    if not moves:
        raise RuntimeError(
            "destroy selection failed: random_removal produced no move for a non-empty solution"
        )
    moves = sorted(
        moves,
        key=lambda move: (-float(move.score), tuple(int(tid) for tid in move.task_ids)),
    )
    candidate_count_before = len(moves)
    target_moves = [
        move for move in moves if _is_target_related_destroy_move(move, target)
    ]
    fallback = bool(_has_local_target(target) and not target_moves)
    sample_pool = target_moves or moves
    selected = _sample_rank_weighted_destroy_move(sample_pool, rng)
    return _with_target_metadata(
        selected,
        **_target_destroy_metadata(
            selected,
            target,
            candidate_count_before,
            len(target_moves),
            fallback=fallback,
        ),
    )


def _is_target_related_destroy_move(
    move: DestroyMove, runtime_target: Dict[str, Any]
) -> bool:
    target_tasks = {int(tid) for tid in runtime_target.get("task_ids", []) or []}
    target_agents = {int(aid) for aid in runtime_target.get("agent_ids", []) or []}
    move_tasks = {int(tid) for tid in move.task_ids}
    move_agents = {int(aid) for aid in move.affected_routes}
    return bool(
        (target_tasks and move_tasks & target_tasks)
        or (target_agents and move_agents & target_agents)
    )


def _target_destroy_metadata(
    move: Any,
    runtime_target: Dict[str, Any],
    candidate_count_before: int,
    candidate_count_after: int,
    *,
    fallback: bool,
) -> Dict[str, Any]:
    target_tasks = {int(tid) for tid in runtime_target.get("task_ids", []) or []}
    target_agents = {int(aid) for aid in runtime_target.get("agent_ids", []) or []}
    move_tasks = {int(tid) for tid in getattr(move, "task_ids", ())}
    move_agents = {int(aid) for aid in getattr(move, "affected_routes", ())}
    task_hits = sorted(move_tasks & target_tasks)
    agent_hits = sorted(move_agents & target_agents)
    return {
        "target_related": bool(task_hits or agent_hits),
        "target_destroy_fallback": bool(fallback),
        "target_task_hit_count": len(task_hits),
        "target_agent_hit_count": len(agent_hits),
        "target_task_hits": task_hits[:20],
        "target_agent_hits": agent_hits[:20],
        "target_candidate_count_before_filter": int(candidate_count_before),
        "target_candidate_count_after_filter": int(candidate_count_after),
    }


def _with_target_metadata(move: DestroyMove, **metadata: Any) -> DestroyMove:
    return DestroyMove(
        operator_name=move.operator_name,
        shape=move.shape,
        task_ids=move.task_ids,
        affected_routes=move.affected_routes,
        features=move.features,
        score=move.score,
        metadata={**dict(move.metadata), **metadata},
    )


def _has_local_target(runtime_target: Dict[str, Any]) -> bool:
    return bool(
        runtime_target.get("task_ids", []) or runtime_target.get("agent_ids", [])
    )


def _sample_rank_weighted_destroy_move(
    moves: Sequence[DestroyMove],
    rng: random.Random,
    alpha: float = 0.75,
) -> DestroyMove:
    if not moves:
        raise ValueError("cannot sample destroy move from empty candidates")
    weights = [1.0 / ((rank + 1) ** float(alpha)) for rank in range(len(moves))]
    total = sum(weights)
    threshold = rng.random() * total
    acc = 0.0
    for move, weight in zip(moves, weights):
        acc += weight
        if acc >= threshold:
            return move
    return moves[-1]


def _init_destroy_operator_stats(
    operator_names: Sequence[str],
) -> Dict[str, Dict[str, float]]:
    return {
        str(name): {
            "used": 0.0,
            "accepted": 0.0,
            "global_best_improved": 0.0,
            "total_score": 0.0,
            "removed_count_sum": 0.0,
            "cost_pressure_sum": 0.0,
            "scarcity_pressure_sum": 0.0,
            "coupling_pressure_sum": 0.0,
            "mobility_opportunity_sum": 0.0,
            "route_balance_pressure_sum": 0.0,
        }
        for name in operator_names
    }


def _accumulate_destroy_operator_stats(
    summary: Dict[str, Dict[str, float]],
    *,
    move: DestroyMove,
    accepted: bool,
    best_improved: bool,
    reward: float,
) -> None:
    name = str(move.operator_name)
    if name not in summary:
        summary[name] = _init_destroy_operator_stats([name])[name]
    bucket = summary[name]
    features = move.features
    bucket["used"] += 1.0
    bucket["accepted"] += 1.0 if accepted else 0.0
    bucket["global_best_improved"] += 1.0 if best_improved else 0.0
    bucket["total_score"] += float(reward)
    bucket["removed_count_sum"] += float(len(move.task_ids))
    bucket["cost_pressure_sum"] += float(features.cost_pressure)
    bucket["scarcity_pressure_sum"] += float(features.scarcity_pressure)
    bucket["coupling_pressure_sum"] += float(features.coupling_pressure)
    bucket["mobility_opportunity_sum"] += float(features.mobility_opportunity)
    bucket["route_balance_pressure_sum"] += float(features.route_balance_pressure)


def _finalize_destroy_operator_stats(
    summary: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for name, bucket in summary.items():
        used = int(bucket.get("used", 0.0))
        denom = max(1.0, float(used))
        out[str(name)] = {
            "used": used,
            "accepted": int(bucket.get("accepted", 0.0)),
            "global_best_improved": int(bucket.get("global_best_improved", 0.0)),
            "total_score": round(float(bucket.get("total_score", 0.0)), 6),
            "mean_removed_count": (
                round(float(bucket.get("removed_count_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
            "mean_cost_pressure": (
                round(float(bucket.get("cost_pressure_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
            "mean_scarcity_pressure": (
                round(float(bucket.get("scarcity_pressure_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
            "mean_coupling_pressure": (
                round(float(bucket.get("coupling_pressure_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
            "mean_mobility_opportunity": (
                round(float(bucket.get("mobility_opportunity_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
            "mean_route_balance_pressure": (
                round(float(bucket.get("route_balance_pressure_sum", 0.0)) / denom, 6)
                if used
                else 0.0
            ),
        }
    return out


def _init_insertion_operator_summary(
    operator_names: Sequence[str],
) -> Dict[str, Dict[str, float]]:
    return {
        str(name): {
            "used": 0.0,
            "accepted": 0.0,
            "global_best_improved": 0.0,
            "inserted_sum": 0.0,
            "unassigned_before_sum": 0.0,
            "unassigned_after_sum": 0.0,
            "tasks_analyzed_sum": 0.0,
            "positions_checked_sum": 0.0,
            "time_ms_sum": 0.0,
        }
        for name in operator_names
    }


def _accumulate_insertion_operator_summary(
    summary: Dict[str, Dict[str, float]],
    *,
    operator_name: str,
    last_insertion: Optional[Dict[str, Any]],
    accepted: bool,
    best_improved: bool,
) -> None:
    name = str(operator_name)
    if name not in summary:
        summary[name] = _init_insertion_operator_summary([name])[name]
    bucket = summary[name]
    insertion = dict(last_insertion or {})
    bucket["used"] += 1.0
    bucket["accepted"] += 1.0 if accepted else 0.0
    bucket["global_best_improved"] += 1.0 if best_improved else 0.0
    bucket["inserted_sum"] += float(insertion.get("inserted_count", 0) or 0)
    bucket["unassigned_before_sum"] += float(insertion.get("unassigned_before", 0) or 0)
    bucket["unassigned_after_sum"] += float(insertion.get("unassigned_after", 0) or 0)
    bucket["tasks_analyzed_sum"] += float(insertion.get("tasks_analyzed", 0) or 0)
    bucket["positions_checked_sum"] += float(
        insertion.get("positions_strict_checked", 0) or 0
    )
    bucket["time_ms_sum"] += float(insertion.get("time_ms", 0.0) or 0.0)


def _finalize_insertion_operator_summary(
    summary: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for name, bucket in summary.items():
        out[str(name)] = {
            "used": int(bucket.get("used", 0.0)),
            "accepted": int(bucket.get("accepted", 0.0)),
            "global_best_improved": int(bucket.get("global_best_improved", 0.0)),
            "inserted_sum": int(bucket.get("inserted_sum", 0.0)),
            "unassigned_before_sum": int(bucket.get("unassigned_before_sum", 0.0)),
            "unassigned_after_sum": int(bucket.get("unassigned_after_sum", 0.0)),
            "tasks_analyzed_sum": int(bucket.get("tasks_analyzed_sum", 0.0)),
            "positions_checked_sum": int(bucket.get("positions_checked_sum", 0.0)),
            "time_ms_sum": round(float(bucket.get("time_ms_sum", 0.0)), 4),
        }
    return out


def _remove_tasks(sol: AssignmentSolution, tids: Sequence[int]) -> None:
    if not tids:
        return
    removed = set(int(tid) for tid in tids)
    for aid, route in list(sol.routes.items()):
        sol.routes[int(aid)] = [int(tid) for tid in route if int(tid) not in removed]
    for tid in removed:
        sol.unassigned.add(int(tid))
    sol.eval = None


def _build_solver_diagnostics(
    *,
    policy: CompiledALNSPolicy,
    total_iters: int,
    actual_time_used_sec: float,
    best_update_iters: List[int],
    best_update_objective_keys: List[Dict[str, Any]],
    returned_solution_source: str,
    initial_solution_feasible: bool,
    returned_solution_feasible: bool,
    operator_weights: Dict[str, Any],
    last_acceptance_decision: Optional[Dict[str, Any]],
    last_destroy_move: Optional[Dict[str, Any]],
    destroy_operator_summary: Dict[str, Any],
    insertion_operator_summary: Dict[str, Any],
    iteration_trace: List[Dict[str, Any]],
    last_insertion: Optional[Dict[str, Any]],
    feasibility_policy: Dict[str, Any],
    final_constraint_report: Any,
    feasibility_rejection_reasons: Dict[str, int],
    protected_metric_rejections: int,
    protected_metric_rejection_reasons: Dict[str, int],
    protected_metric_bounds: List[Dict[str, Any]],
    returned_protected_result: Dict[str, Any],
    execution_trace: Dict[str, Any],
) -> Dict[str, Any]:
    last_best_iter = best_update_iters[-1] if best_update_iters else None
    diagnostics = {
        "algorithm": "weighted_alns",
        "policy": policy.as_dict(),
        "total_iters": int(total_iters),
        "actual_iters_used": int(total_iters),
        "actual_time_used_sec": max(0.0, float(actual_time_used_sec)),
        "best_update_count": len(best_update_iters),
        "best_update_iters": [int(x) for x in best_update_iters],
        "best_update_objective_keys": list(best_update_objective_keys),
        "first_best_iter": int(best_update_iters[0]) if best_update_iters else None,
        "last_best_iter": int(last_best_iter) if last_best_iter is not None else None,
        "plateau_iters_after_last_update": (
            int(total_iters - last_best_iter)
            if last_best_iter is not None
            else int(total_iters)
        ),
        "initial_solution_feasible": bool(initial_solution_feasible),
        "returned_solution_source": returned_solution_source,
        "returned_solution_feasible": bool(returned_solution_feasible),
        "last_acceptance_decision": dict(last_acceptance_decision or {}),
        "last_destroy_move": dict(last_destroy_move or {}),
        "last_insertion": dict(last_insertion or {}),
        "iteration_trace": list(iteration_trace),
        "destroy_operator_summary": _numericize_weight_tree(destroy_operator_summary),
        "insertion_operator_summary": _numericize_weight_tree(
            insertion_operator_summary
        ),
        "operator_weights": _numericize_weight_tree(operator_weights),
        "feasibility_policy": _numericize_weight_tree(feasibility_policy),
        "violation_ratios": _violation_ratio_diagnostics(
            final_constraint_report,
            feasibility_policy,
        ),
        "feasibility_rejection_reasons": {
            str(reason): int(count)
            for reason, count in feasibility_rejection_reasons.items()
        },
        "protected_metric_rejections": int(protected_metric_rejections),
        "protected_metric_rejection_reasons": {
            str(metric): int(count)
            for metric, count in protected_metric_rejection_reasons.items()
        },
        "protected_metric_bounds": list(protected_metric_bounds),
        "protected_metric_result": dict(returned_protected_result),
        "execution_trace": dict(execution_trace),
    }
    return diagnostics


def _build_execution_trace(
    *,
    trace_id: str,
    total_iters: int,
    destroy_operator_summary: Dict[str, Any],
    insertion_operator_summary: Dict[str, Any],
    trial_flow: Dict[str, int],
    rejection_reasons: Dict[str, int],
    repair_failure_reasons: Dict[str, int],
    removed_task_count_sum: float,
    operator_prior_trace: Dict[str, Any],
    runtime_target: Dict[str, Any],
    feasibility_policy: Dict[str, Any],
    feasibility_rejection_reasons: Dict[str, int],
    final_constraint_report: Any,
    initial_constraint_report: Any,
    protected_metric_bounds: List[Dict[str, Any]],
    protected_metric_rejections: int,
    protected_metric_rejection_reasons: Dict[str, int],
    returned_protected_result: Dict[str, Any],
    actual_time_used_sec: float,
    returned_solution_source: str,
    iteration_trace: List[Dict[str, Any]],
    last_insertion: Optional[Dict[str, Any]],
    before_solution: AssignmentSolution,
    after_solution: AssignmentSolution,
    before_eval: EvalResult,
    after_eval: Optional[EvalResult],
) -> Dict[str, Any]:
    selected_counts = {
        str(name): int(values.get("used", 0) if isinstance(values, dict) else values)
        for name, values in destroy_operator_summary.items()
    }
    candidate_trials = max(1, int(trial_flow.get("candidate_trials", 0) or 0))
    tasks_reinserted = sum(
        int(values.get("inserted_sum", 0) or 0)
        for values in insertion_operator_summary.values()
        if isinstance(values, dict)
    )
    tasks_left = sum(
        int(values.get("unassigned_after_sum", 0) or 0)
        for values in insertion_operator_summary.values()
        if isinstance(values, dict)
    )
    dominant_repair = max(
        repair_failure_reasons.items(),
        key=lambda item: int(item[1]),
        default=("none", 0),
    )[0]
    target_engagement = _build_target_engagement(
        runtime_target=runtime_target,
        iteration_trace=iteration_trace,
        last_insertion=last_insertion,
    )
    target_agent_engagement = _target_agent_engagement_from_insertion(last_insertion)
    target_progress = _target_progress(
        before_solution=before_solution,
        after_solution=after_solution,
        before_eval=before_eval,
        after_eval=after_eval,
        runtime_target=runtime_target,
    )
    return {
        "trace_id": trace_id,
        "kind": "alns",
        "iters": int(total_iters),
        "actual_time_used_sec": float(actual_time_used_sec),
        "returned_solution_source": str(returned_solution_source),
        "runtime_target": dict(runtime_target),
        "target_engagement": target_engagement,
        "target_agent_engagement": target_agent_engagement,
        "target_progress": target_progress,
        "operator_prior_trace": {
            **dict(operator_prior_trace),
            "actual_usage": selected_counts,
            "accepted_usage": {
                str(name): int(values.get("accepted", 0) or 0)
                for name, values in destroy_operator_summary.items()
                if isinstance(values, dict)
            },
            "reward": {
                str(name): float(values.get("total_score", 0.0) or 0.0)
                for name, values in destroy_operator_summary.items()
                if isinstance(values, dict)
            },
        },
        "operator_effectiveness": {
            "destroy": _operator_effectiveness_destroy(destroy_operator_summary),
            "insertion": _operator_effectiveness_insertion(insertion_operator_summary),
        },
        "destroy": {
            "selected_operator_counts": selected_counts,
            "removed_task_count_avg": round(
                float(removed_task_count_sum) / candidate_trials, 6
            ),
        },
        "repair": {
            "candidate_tasks_total": int(tasks_reinserted + tasks_left),
            "tasks_reinserted": int(tasks_reinserted),
            "tasks_left_unassigned": int(tasks_left),
            "dominant_repair_failure": str(dominant_repair),
            "repair_failure_reasons": {
                str(k): int(v) for k, v in repair_failure_reasons.items()
            },
        },
        "trial_flow": {str(k): int(v) for k, v in trial_flow.items()},
        "rejection_reasons": {str(k): int(v) for k, v in rejection_reasons.items()},
        "feasibility_control": {
            "policy": _numericize_weight_tree(feasibility_policy),
            "rejection_reasons": {
                str(k): int(v) for k, v in feasibility_rejection_reasons.items()
            },
            "returned_violation_ratios": _violation_ratio_diagnostics(
                final_constraint_report, feasibility_policy
            ),
            "returned_check": _returned_feasibility_check(
                initial_constraint_report,
                final_constraint_report,
                feasibility_policy,
            ),
        },
        "protected_metrics": {
            "bounds": list(protected_metric_bounds),
            "rejected_trials": int(protected_metric_rejections),
            "rejection_reasons": {
                str(k): int(v) for k, v in protected_metric_rejection_reasons.items()
            },
            "returned_check": dict(returned_protected_result),
        },
    }


def _build_target_engagement(
    *,
    runtime_target: Dict[str, Any],
    iteration_trace: List[Dict[str, Any]],
    last_insertion: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    destroy_used = 0
    destroy_fallback = 0
    destroy_available = 0
    attempted: List[int] = []
    inserted: List[int] = []
    insertion_fallback = 0
    still_unassigned: List[int] = []
    for item in iteration_trace:
        metadata = dict(item.get("destroy_target_metadata", {}) or {})
        if metadata.get("target_related"):
            destroy_used += 1
        if metadata.get("target_destroy_fallback"):
            destroy_fallback += 1
        destroy_available += int(
            metadata.get("target_candidate_count_after_filter", 0) or 0
        )
        target_insertion = dict(item.get("target_insertion", {}) or {})
        attempted.extend(int(tid) for tid in target_insertion.get("target_tasks_attempted", []) or [])
        inserted.extend(int(tid) for tid in target_insertion.get("target_tasks_inserted", []) or [])
        insertion_fallback += int(
            target_insertion.get("target_insertion_fallback_count", 0) or 0
        )
        progress = dict(item.get("target_progress", {}) or {})
        still_unassigned = [
            int(tid) for tid in progress.get("target_tasks_still_unassigned", []) or []
        ]
    if last_insertion:
        attempted.extend(
            int(tid) for tid in last_insertion.get("target_tasks_attempted", []) or []
        )
        inserted.extend(
            int(tid) for tid in last_insertion.get("target_tasks_inserted", []) or []
        )
    return {
        "target_scope_kind": str(runtime_target.get("scope_kind", "global")),
        "target_task_count": len(runtime_target.get("task_ids", []) or []),
        "target_agent_count": len(runtime_target.get("agent_ids", []) or []),
        "target_destroy_moves_available": int(destroy_available),
        "target_destroy_moves_used": int(destroy_used),
        "target_destroy_fallback_count": int(destroy_fallback),
        "target_tasks_attempted": _unique_ints(attempted),
        "target_tasks_inserted": _unique_ints(inserted),
        "target_tasks_still_unassigned": _unique_ints(still_unassigned),
        "target_insertion_fallback_count": int(insertion_fallback),
    }


def _target_agent_engagement_from_insertion(
    last_insertion: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    engagement = dict(
        (last_insertion or {}).get("target_agent_engagement", {}) or {}
    )
    if engagement:
        return engagement
    return {
        "target_agent_ids": [],
        "candidate_positions_on_target_agents": 0,
        "attempts_on_target_agents": 0,
        "insertions_on_target_agents": 0,
        "fallback_count": 0,
        "fallback_reasons": {
            "no_feasible_position_on_target_agent": 0,
        },
    }


def _operator_effectiveness_destroy(
    summary: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    return {
        str(name): {
            "used": int(values.get("used", 0) or 0),
            "accepted": int(values.get("accepted", 0) or 0),
            "global_best_improved": int(values.get("global_best_improved", 0) or 0),
            "protected_rejects": 0,
            "mean_removed_count": float(values.get("mean_removed_count", 0.0) or 0.0),
            "total_reward": float(values.get("total_score", 0.0) or 0.0),
        }
        for name, values in summary.items()
        if isinstance(values, dict)
    }


def _operator_effectiveness_insertion(
    summary: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    return {
        str(name): {
            "used": int(values.get("used", 0) or 0),
            "accepted": int(values.get("accepted", 0) or 0),
            "inserted_sum": int(values.get("inserted_sum", 0) or 0),
            "positions_checked_sum": int(
                values.get("positions_checked_sum", 0) or 0
            ),
            "failed_insertions": int(values.get("unassigned_after_sum", 0) or 0),
        }
        for name, values in summary.items()
        if isinstance(values, dict)
    }


def _compact_insertion_target(last_insertion: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    insertion = dict(last_insertion or {})
    return {
        "target_task_ids": _unique_ints(insertion.get("target_task_ids", []) or []),
        "target_tasks_attempted": _unique_ints(
            insertion.get("target_tasks_attempted", []) or []
        ),
        "target_tasks_inserted": _unique_ints(
            insertion.get("target_tasks_inserted", []) or []
        ),
        "target_tasks_failed": _unique_ints(
            insertion.get("target_tasks_failed", []) or []
        ),
        "target_insertion_fallback_count": int(
            insertion.get("target_insertion_fallback_count", 0) or 0
        ),
        "target_agent_engagement": dict(
            insertion.get("target_agent_engagement", {}) or {}
        ),
    }


def _target_progress(
    *,
    before_solution: AssignmentSolution,
    after_solution: AssignmentSolution,
    before_eval: EvalResult,
    after_eval: Optional[EvalResult],
    runtime_target: Dict[str, Any],
) -> Dict[str, Any]:
    return _target_progress_from_snapshot(
        before_unassigned={int(tid) for tid in before_solution.unassigned},
        after_unassigned={int(tid) for tid in after_solution.unassigned},
        before_focus_values=_focus_metric_values(before_eval, runtime_target),
        after_eval=after_eval,
        runtime_target=runtime_target,
    )


def _target_progress_from_snapshot(
    *,
    before_unassigned: set[int],
    after_unassigned: set[int],
    before_focus_values: Dict[str, float],
    after_eval: Optional[EvalResult],
    runtime_target: Dict[str, Any],
) -> Dict[str, Any]:
    target_task_ids = _unique_ints(runtime_target.get("task_ids", []) or [])
    inserted = [
        tid for tid in target_task_ids
        if int(tid) in before_unassigned and int(tid) not in after_unassigned
    ]
    focus_delta: Dict[str, float] = {}
    if after_eval is not None:
        for metric, before_value in before_focus_values.items():
            focus_delta[str(metric)] = float(after_eval.get_metric(str(metric))) - float(before_value)
    return {
        "target_task_count": len(target_task_ids),
        "target_tasks_inserted": inserted[:20],
        "target_tasks_still_unassigned": [
            tid for tid in target_task_ids if int(tid) in after_unassigned
        ][:20],
        "focus_metric_delta": focus_delta,
    }


def _focus_metric_values(
    evaluation: EvalResult, runtime_target: Dict[str, Any]
) -> Dict[str, float]:
    return {
        str(metric): float(evaluation.get_metric(str(metric)))
        for metric in runtime_target.get("focus_metrics", []) or []
        if str(metric)
    }


def _unique_ints(values: Any, limit: int = 20) -> List[int]:
    out: List[int] = []
    seen = set()
    for value in values or []:
        if isinstance(value, bool):
            continue
        item = int(value)
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
        if len(out) >= limit:
            break
    return out


def _violation_ratio_diagnostics(
    report: Any,
    feasibility_policy: Dict[str, Any],
) -> Dict[str, Any]:
    per_type = dict(feasibility_policy.get("per_type", {}) or {})
    ratios = dict(getattr(report, "violation_ratio_by_type", {}) or {})
    details = dict(getattr(report, "violation_details_by_type", {}) or {})
    names = set(ratios) | set(per_type)
    return {
        name: {
            "total_ratio": float(ratios.get(name, 0.0)),
            "max_individual_ratio": max(
                (float(item.get("ratio", 0.0)) for item in details.get(name, [])),
                default=0.0,
            ),
            "limit_ratio": (
                None if name not in per_type else float(per_type[name]["limit_ratio"])
            ),
            "delta_ratio": (
                None if name not in per_type else float(per_type[name]["delta_ratio"])
            ),
        }
        for name in sorted(names)
    }


def _returned_feasibility_check(
    initial_report: Any,
    final_report: Any,
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    mode = str(policy.get("mode", "strict"))
    if mode == "strict":
        passed = bool(getattr(final_report, "is_feasible", False))
        reason = "feasible" if passed else "returned_working_is_infeasible"
    elif mode == "recovery_only":
        initial_total = float(getattr(initial_report, "violation_total", 0.0) or 0.0)
        final_total = float(getattr(final_report, "violation_total", 0.0) or 0.0)
        passed = bool(
            getattr(final_report, "is_feasible", False)
            or final_total < initial_total - 1e-9
        )
        reason = "recovery_progress" if passed else "recovery_non_reducing_return"
    else:
        per_type = dict(policy.get("per_type", {}) or {})
        ratios = dict(getattr(final_report, "violation_ratio_by_type", {}) or {})
        passed = bool(
            float(
                getattr(final_report, "unrecoverable_violation_total", 0.0) or 0.0
            )
            <= 1e-9
            and all(
                name in per_type
                and float(value) <= float(per_type[name]["limit_ratio"]) + 1e-9
                for name, value in ratios.items()
                if float(value) > 1e-9
            )
        )
        reason = "within_relaxation_limits" if passed else "relaxation_limit_exceeded"
    return {"mode": mode, "passed": passed, "reason": reason}


@dataclass(slots=True)
class _AcceptanceDecision:
    compare_result: int
    accepted: bool
    accept_mode: str
    feasibility_admissible: bool = True
    accept_scope: str = "working_and_best_candidate"
    feasibility_reason: str = ""
    delta_soft: Optional[float] = None
    temperature: Optional[float] = None
    threshold: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "compare_result": int(self.compare_result),
            "accepted": bool(self.accepted),
            "accept_mode": str(self.accept_mode),
            "feasibility_admissible": bool(self.feasibility_admissible),
            "accept_scope": str(self.accept_scope),
            "feasibility_reason": str(self.feasibility_reason),
        }
        if self.delta_soft is not None:
            data["delta_soft"] = float(self.delta_soft)
        if self.temperature is not None:
            data["temperature"] = float(self.temperature)
        if self.threshold is not None:
            data["threshold"] = float(self.threshold)
        return data


def _alns_accept(
    cur_ev: EvalResult,
    trial_ev: EvalResult,
    objective_layers: List[Dict[str, Any]],
    mode: str,
    rng: random.Random,
    temperature: float,
    accept_level: float,
    feasibility_admissible: bool,
    accept_scope: str,
    feasibility_reason: str,
) -> _AcceptanceDecision:
    # compare_quality(...) is the only ordering decision. Soft delta is auxiliary and is
    # only consulted for worse moves (cmp > 0).
    cmp = compare_quality(trial_ev, cur_ev, objective_layers)
    if cmp < 0:
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=True,
            accept_mode=mode,
            feasibility_admissible=feasibility_admissible,
            accept_scope=accept_scope,
            feasibility_reason=feasibility_reason,
        )
    if cmp == 0:
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=True,
            accept_mode=mode,
            feasibility_admissible=feasibility_admissible,
            accept_scope=accept_scope,
            feasibility_reason=feasibility_reason,
        )

    if mode == "greedy":
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=False,
            accept_mode=mode,
            feasibility_admissible=feasibility_admissible,
            accept_scope=accept_scope,
            feasibility_reason=feasibility_reason,
        )

    delta_soft = _acceptance_soft_delta(cur_ev, trial_ev, objective_layers)
    if mode == "threshold":
        threshold = _threshold_acceptance_limit(cur_ev, trial_ev, accept_level)
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=(delta_soft <= threshold),
            accept_mode=mode,
            feasibility_admissible=feasibility_admissible,
            accept_scope=accept_scope,
            feasibility_reason=feasibility_reason,
            delta_soft=delta_soft,
            threshold=threshold,
        )

    if mode == "sa":
        delta_soft = max(delta_soft, 1e-12)
        accepted = rng.random() < math.exp(-delta_soft / max(1e-12, temperature))
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=accepted,
            accept_mode=mode,
            feasibility_admissible=feasibility_admissible,
            accept_scope=accept_scope,
            feasibility_reason=feasibility_reason,
            delta_soft=delta_soft,
            temperature=float(temperature),
        )


def _acceptance_soft_delta(
    cur_ev: EvalResult, trial_ev: EvalResult, objective_layers: List[Dict[str, Any]]
) -> float:
    """Auxiliary scalar for worse-move soft acceptance only."""
    eps = 1e-9
    for layer in objective_layers:
        metric = str(layer.get("metric", ""))
        direction = str(layer.get("direction", "min"))
        cur_value = _oriented_metric_value(cur_ev, metric, direction)
        trial_value = _oriented_metric_value(trial_ev, metric, direction)
        if abs(trial_value - cur_value) > eps:
            scale = max(1.0, abs(cur_value), abs(trial_value))
            return max(0.0, (trial_value - cur_value) / scale)

    return 0.0


def _oriented_metric_value(ev: EvalResult, metric: str, direction: str) -> float:
    value = float(ev.get_quality_metric(metric))
    return -value if str(direction).lower() == "max" else value


def _threshold_acceptance_limit(
    cur_ev: EvalResult, trial_ev: EvalResult, accept_level: float
) -> float:
    cur_violation = float(cur_ev.get_metric("violation_total"))
    trial_violation = float(trial_ev.get_metric("violation_total"))
    if cur_violation <= 0.0 and trial_violation <= 0.0:
        return 0.01 + 0.12 * float(accept_level)
    return 0.005 + 0.06 * float(accept_level)


def _roulette_select(weights: Dict[str, float], rng: random.Random) -> str:
    items = list(weights.items())
    total = sum(max(0.0, weight) for _, weight in items)
    if total <= 0:
        return items[rng.randrange(len(items))][0]
    threshold = rng.random() * total
    acc = 0.0
    for name, weight in items:
        acc += max(0.0, weight)
        if acc >= threshold:
            return name
    return items[-1][0]


def _blend_operator_weights(
    rule_weights: Dict[str, float],
    llm_priors: Dict[str, float],
    mix_lambda: float,
) -> Dict[str, float]:
    lam = _clamp_float(float(mix_lambda), 0.0, 1.0)
    fused: Dict[str, float] = {}
    for name, rule_weight in rule_weights.items():
        rule = max(1e-9, float(rule_weight))
        prior = max(1e-9, float(llm_priors[str(name)]))
        fused[str(name)] = (rule ** (1.0 - lam)) * (prior**lam)
    return fused


def _numericize_weight_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {str(key): _numericize_weight_tree(value) for key, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [_numericize_weight_tree(value) for value in node]
    if isinstance(node, (int, float)):
        return float(node)
    return node


def _config_objective_layers(config: Config) -> List[Dict[str, Any]]:
    return [
        {"metric": str(layer.metric), "direction": str(layer.direction)}
        for layer in config.eval.objective_policy.layers
        if str(layer.metric)
    ]


def _dedupe_events(events: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for event in events:
        value = str(event)
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _update_weights(
    weights: Dict[str, float],
    scores: Dict[str, float],
    used: Dict[str, int],
    reaction: float,
) -> None:
    for name in list(weights.keys()):
        if used.get(name, 0) <= 0:
            continue
        avg = float(scores.get(name, 0.0)) / max(1, int(used.get(name, 0)))
        weights[name] = (1.0 - float(reaction)) * float(weights[name]) + float(
            reaction
        ) * max(0.0, avg)
        weights[name] = max(1e-6, float(weights[name]))


def _reset_segment_scores(scores: Dict[str, float], used: Dict[str, int]) -> None:
    for name in list(scores.keys()):
        scores[name] = 0.0
        used[name] = 0


def _budget_ok(budget: Budget, started_at: float, iteration: int) -> bool:
    if budget.time_limit_sec is not None and (
        time.perf_counter() - started_at
    ) >= float(budget.time_limit_sec):
        return False
    if budget.max_iters is not None and iteration >= int(budget.max_iters):
        return False
    return True


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(int(lo), min(int(hi), int(value)))


def _clamp_float(value: float, lo: float, hi: float) -> float:
    return max(float(lo), min(float(hi), float(value)))


def _bool_text(value: Any) -> str:
    return str(bool(value)).lower()
