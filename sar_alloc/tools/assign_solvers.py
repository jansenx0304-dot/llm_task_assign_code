from __future__ import annotations

"""Weighted ALNS solver with separate operator-level scoring profiles.

Reinsert-task score decides which task to repair next. Insert score decides the
order of filtered insertion positions. Repair scans the full ranked candidate
sets.
"""

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from ..config import Budget, Config
from ..evaluator import compare, evaluate as _evaluate_raw
from ..models import Instance
from ..operators import (
    LandscapeFeatures,
    WeightedALNSPolicy,
)
from ..operators.destroy import (
    DESTROY_OPERATORS,
    DestroyMove,
    DestroyOperator,
    compute_destroy_strength,
    enumerate_random_removal,
)
from ..operators.repair import (
    repair_with_bottleneck_targeted,
    repair_with_diversified_random,
    repair_with_feasible_greedy,
    repair_with_regret_k,
    repair_with_scarcity_first,
)
from ..solution import AssignmentSolution, EvalResult


@dataclass
class _EvalStats:
    n: int = 0
    t: float = 0.0


EVAL_STATS = _EvalStats()

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
    policy: WeightedALNSPolicy,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Run weighted ALNS from an incumbent using an already validated policy."""
    rng = random.Random(int(rng_seed))

    cur = init_solution.clone(deep=True)
    cur.normalize(instance)
    cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)
    print(
        "[ALNS] start "
        f"acceptance={policy.acceptance} "
        f"strength_ratio={float(policy.strength_ratio)} "
        f"time_limit={budget.time_limit_sec} "
        f"iters={budget.max_iters} "
        f"init_feasible={_bool_text(cur_ev.is_feasible)} "
        f"init_lex_key={cur_ev.lex_key}"
    )

    best = cur.clone(deep=True)
    best_ev = cur_ev
    return _solve_weighted_alns(instance, cur, cur_ev, best, best_ev, config, budget, policy, rng)


def _solve_weighted_alns(
    instance: Instance,
    cur: AssignmentSolution,
    cur_ev: EvalResult,
    best: AssignmentSolution,
    best_ev: EvalResult,
    config: Config,
    budget: Budget,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    destroy_ops: Dict[str, DestroyOperator] = dict(DESTROY_OPERATORS)
    repair_task_ops = {
        "feasible_greedy_repair": repair_with_feasible_greedy,
        "scarcity_first_repair": repair_with_scarcity_first,
        "regret_k_repair": repair_with_regret_k,
        "bottleneck_targeted_repair": repair_with_bottleneck_targeted,
        "diversified_random_repair": repair_with_diversified_random,
    }

    destroy_priors = dict(policy.destroy_operator_priors)
    repair_task_priors = dict(policy.repair_operator_priors)
    prior_mix_lambda = float(policy.prior_mix_lambda)

    d_w = {name: 1.0 for name in destroy_ops}
    r_w = {name: 1.0 for name in repair_task_ops}

    d_score = {name: 0.0 for name in d_w}
    r_score = {name: 0.0 for name in r_w}

    d_used = {name: 0 for name in d_w}
    r_used = {name: 0 for name in r_w}

    if budget.max_iters is not None:
        segment_len = _clamp_int(int(0.10 * int(budget.max_iters)), 10, 200)
    else:
        segment_len = 50

    reaction = float(policy.reaction_factor)
    accept_level = float(policy.accept_level)
    temperature = 0.05 + 0.50 * accept_level
    cooling = _clamp_float(0.999 - 0.02 * accept_level, 0.90, 0.9999)
    initial_solution_feasible = bool(best_ev.is_feasible)

    best_feasible: Optional[AssignmentSolution] = best.clone(deep=True) if best_ev.is_feasible else None
    best_feasible_ev: Optional[EvalResult] = best_ev if best_ev.is_feasible else None

    best_update_iters: List[int] = []
    best_update_lex_keys: List[List[float]] = []
    last_acceptance_decision: Optional[Dict[str, Any]] = None
    destroy_operator_stats = _init_destroy_operator_stats(d_w.keys())
    repair_operator_summary = _init_repair_operator_summary(r_w.keys())
    iteration_trace: List[Dict[str, Any]] = []
    last_destroy_move: Optional[Dict[str, Any]] = None
    last_repair: Optional[Dict[str, Any]] = None

    iteration = 0
    started_at = time.perf_counter()

    while _budget_ok(budget, started_at, iteration):
        iteration += 1
        d_final = _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda)
        r_final = _blend_operator_weights(r_w, repair_task_priors, prior_mix_lambda)
        d_name = _roulette_select(d_final, rng)
        r_name = _roulette_select(r_final, rng)
        r_used[r_name] += 1

        move = select_destroy_move(
            sol=cur,
            instance=instance,
            config=config,
            policy=policy,
            operator=destroy_ops[d_name],
            rng=rng,
        )
        actual_d_name = str(move.operator_name)
        d_used[actual_d_name] += 1
        removed = list(int(tid) for tid in move.task_ids)
        last_destroy_move = move.as_dict()

        partial = cur.clone(deep=True)
        _remove_tasks(partial, removed)
        partial.solver_diagnostics = {"last_destroy_move": last_destroy_move}
        partial.normalize(instance)

        trial = repair_task_ops[r_name](partial, instance, config, policy, rng)
        trial.solver_diagnostics["last_destroy_move"] = last_destroy_move
        last_repair = dict((getattr(trial, "solver_diagnostics", {}) or {}).get("last_repair", {}) or {})

        trial.normalize(instance)
        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)

        acceptance = _alns_accept(
            cur_ev=cur_ev,
            trial_ev=ev_trial,
            config=config,
            mode=policy.acceptance,
            rng=rng,
            temperature=temperature,
            accept_level=accept_level,
        )
        accepted = acceptance.accepted
        last_acceptance_decision = acceptance.as_dict()
        if iteration % 100 == 0:
            message = (
                f"[ALNS] iter={iteration} "
                f"destroy={actual_d_name} repair={r_name} "
                f"accepted={_bool_text(accepted)} feasible={_bool_text(ev_trial.is_feasible)} "
                f"lex_key={ev_trial.lex_key} "
                f"unassigned={len(trial.unassigned)}"
            )
            print(message)

        reward = 0.0
        if accepted:
            cur = trial
            cur_ev = ev_trial
            reward = max(reward, 0.2)

        best_improved = False
        if compare(ev_trial, best_ev, config) < 0:
            best = trial.clone(deep=True)
            best_ev = ev_trial
            reward = max(reward, 5.0)
            best_improved = True

        if ev_trial.is_feasible and (best_feasible_ev is None or compare(ev_trial, best_feasible_ev, config) < 0):
            best_feasible = trial.clone(deep=True)
            best_feasible_ev = ev_trial
            best_update_iters.append(iteration)
            best_update_lex_keys.append(list(best_feasible_ev.lex_key or ()))
            reward = max(reward, 5.0)
            best_improved = True

        iteration_trace.append(
            {
                "iteration": int(iteration),
                "destroy_operator": actual_d_name,
                "repair_operator": r_name,
                "accepted": bool(accepted),
                "current_objective": _trace_objective(cur_ev),
                "current_lex_key": _trace_lex_key(cur_ev),
                "best_objective": _trace_objective(best_ev),
                "best_lex_key": _trace_lex_key(best_ev),
                "violation_total": float(ev_trial.get_metric("violation_total")),
            }
        )

        d_score[actual_d_name] += reward
        r_score[r_name] += reward
        _accumulate_destroy_operator_stats(
            destroy_operator_stats,
            move=move,
            accepted=accepted,
            best_improved=best_improved,
            reward=reward,
        )
        _accumulate_repair_operator_summary(
            repair_operator_summary,
            operator_name=r_name,
            last_repair=last_repair,
            accepted=accepted,
            best_improved=best_improved,
        )

        if policy.acceptance == "sa":
            temperature = max(1e-9, temperature * cooling)

        if iteration % segment_len == 0:
            _update_weights(d_w, d_score, d_used, reaction)
            _update_weights(r_w, r_score, r_used, reaction)
            _reset_segment_scores(d_score, d_used)
            _reset_segment_scores(r_score, r_used)

    returned = best_feasible if best_feasible is not None else best
    returned_source = "best_feasible" if best_feasible is not None else "best_overall"
    evaluate(returned, instance, config, update_solution_schedule=True)
    actual_time_used_sec = max(0.0, time.perf_counter() - started_at)
    diagnostics = _build_solver_diagnostics(
        policy=policy,
        total_iters=iteration,
        actual_time_used_sec=actual_time_used_sec,
        best_update_iters=best_update_iters,
        best_update_lex_keys=best_update_lex_keys,
        returned_solution_source=returned_source,
        initial_solution_feasible=initial_solution_feasible,
        returned_solution_feasible=bool(getattr(returned.eval, "is_feasible", False)),
        last_acceptance_decision=last_acceptance_decision,
        last_destroy_move=last_destroy_move,
        destroy_operator_summary=_finalize_destroy_operator_stats(destroy_operator_stats),
        repair_operator_summary=_finalize_repair_operator_summary(repair_operator_summary),
        iteration_trace=iteration_trace,
        last_repair=last_repair,
        operator_weights={
            "destroy_operators": {
                "adaptive": d_w,
                "llm_score_prior": destroy_priors,
                "fused_final": _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda),
            },
            "repair_operators": {
                "adaptive": r_w,
                "llm_score_prior": repair_task_priors,
                "fused_final": _blend_operator_weights(r_w, repair_task_priors, prior_mix_lambda),
            },
        },
    )
    print(
        "[ALNS] done "
        f"returned_source={returned_source} "
        f"total_iters={iteration} "
        f"best_update_count={len(best_update_iters)} "
        f"actual_time_used_sec={round(actual_time_used_sec, 4)} "
        f"returned_feasible={_bool_text(getattr(returned.eval, 'is_feasible', False))}"
    )
    return _attach_solver_diagnostics(
        returned,
        diagnostics,
    )


def select_destroy_move(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    operator: DestroyOperator,
    rng: random.Random,
) -> DestroyMove:
    assigned = list(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned:
        return DestroyMove(
            operator_name="random_removal",
            shape="random",
            task_ids=(),
            affected_routes=(),
            features=LandscapeFeatures(
                cost_pressure=0.0,
                scarcity_pressure=0.0,
                coupling_pressure=0.0,
                mobility_opportunity=0.0,
                balance_pressure=0.0,
            ),
            score=0.0,
            metadata={"target_k": 0},
        )
    strength = compute_destroy_strength(sol, policy.strength_ratio)
    moves = operator(sol, instance, config, policy, strength, rng)
    if not moves:
        moves = enumerate_random_removal(sol, instance, config, policy, strength, rng)
    if not moves:
        raise RuntimeError("destroy selection failed: random_removal produced no move for a non-empty solution")
    moves = sorted(moves, key=lambda move: -float(move.score))
    top_m = min(5, len(moves))
    rank_weights = [1.0, 0.7, 0.5, 0.35, 0.25][:top_m]
    total = sum(rank_weights)
    threshold = rng.random() * total
    acc = 0.0
    for move, weight in zip(moves[:top_m], rank_weights):
        acc += weight
        if acc >= threshold:
            return move
    return moves[top_m - 1]


def _init_destroy_operator_stats(operator_names: Sequence[str]) -> Dict[str, Dict[str, float]]:
    return {
        str(name): {
            "used": 0.0,
            "accepted": 0.0,
            "best_improved": 0.0,
            "total_score": 0.0,
            "removed_count_sum": 0.0,
            "cost_pressure_sum": 0.0,
            "scarcity_pressure_sum": 0.0,
            "coupling_pressure_sum": 0.0,
            "mobility_opportunity_sum": 0.0,
            "balance_pressure_sum": 0.0,
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
    bucket["best_improved"] += 1.0 if best_improved else 0.0
    bucket["total_score"] += float(reward)
    bucket["removed_count_sum"] += float(len(move.task_ids))
    bucket["cost_pressure_sum"] += float(features.cost_pressure)
    bucket["scarcity_pressure_sum"] += float(features.scarcity_pressure)
    bucket["coupling_pressure_sum"] += float(features.coupling_pressure)
    bucket["mobility_opportunity_sum"] += float(features.mobility_opportunity)
    bucket["balance_pressure_sum"] += float(features.balance_pressure)


def _finalize_destroy_operator_stats(summary: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for name, bucket in summary.items():
        used = int(bucket.get("used", 0.0))
        denom = max(1.0, float(used))
        out[str(name)] = {
            "used": used,
            "accepted": int(bucket.get("accepted", 0.0)),
            "best_improved": int(bucket.get("best_improved", 0.0)),
            "total_score": round(float(bucket.get("total_score", 0.0)), 6),
            "mean_removed_count": round(float(bucket.get("removed_count_sum", 0.0)) / denom, 6) if used else 0.0,
            "mean_cost_pressure": round(float(bucket.get("cost_pressure_sum", 0.0)) / denom, 6) if used else 0.0,
            "mean_scarcity_pressure": round(float(bucket.get("scarcity_pressure_sum", 0.0)) / denom, 6) if used else 0.0,
            "mean_coupling_pressure": round(float(bucket.get("coupling_pressure_sum", 0.0)) / denom, 6) if used else 0.0,
            "mean_mobility_opportunity": round(float(bucket.get("mobility_opportunity_sum", 0.0)) / denom, 6) if used else 0.0,
            "mean_balance_pressure": round(float(bucket.get("balance_pressure_sum", 0.0)) / denom, 6) if used else 0.0,
        }
    return out


def _init_repair_operator_summary(operator_names: Sequence[str]) -> Dict[str, Dict[str, float]]:
    return {
        str(name): {
            "used": 0.0,
            "accepted": 0.0,
            "best_improved": 0.0,
            "inserted_sum": 0.0,
            "unassigned_before_sum": 0.0,
            "unassigned_after_sum": 0.0,
            "tasks_analyzed_sum": 0.0,
            "positions_checked_sum": 0.0,
            "time_ms_sum": 0.0,
        }
        for name in operator_names
    }


def _accumulate_repair_operator_summary(
    summary: Dict[str, Dict[str, float]],
    *,
    operator_name: str,
    last_repair: Optional[Dict[str, Any]],
    accepted: bool,
    best_improved: bool,
) -> None:
    name = str(operator_name)
    if name not in summary:
        summary[name] = _init_repair_operator_summary([name])[name]
    bucket = summary[name]
    repair = dict(last_repair or {})
    bucket["used"] += 1.0
    bucket["accepted"] += 1.0 if accepted else 0.0
    bucket["best_improved"] += 1.0 if best_improved else 0.0
    bucket["inserted_sum"] += float(repair.get("inserted_count", 0) or 0)
    bucket["unassigned_before_sum"] += float(repair.get("unassigned_before", 0) or 0)
    bucket["unassigned_after_sum"] += float(repair.get("unassigned_after", 0) or 0)
    bucket["tasks_analyzed_sum"] += float(repair.get("tasks_analyzed", 0) or 0)
    bucket["positions_checked_sum"] += float(repair.get("positions_strict_checked", 0) or 0)
    bucket["time_ms_sum"] += float(repair.get("time_ms", 0.0) or 0.0)


def _finalize_repair_operator_summary(summary: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for name, bucket in summary.items():
        out[str(name)] = {
            "used": int(bucket.get("used", 0.0)),
            "accepted": int(bucket.get("accepted", 0.0)),
            "best_improved": int(bucket.get("best_improved", 0.0)),
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


def _attach_solver_diagnostics(solution: AssignmentSolution, diagnostics: Dict[str, Any]) -> AssignmentSolution:
    solution.solver_diagnostics = diagnostics
    return solution


def _build_solver_diagnostics(
    *,
    policy: WeightedALNSPolicy,
    total_iters: int,
    actual_time_used_sec: float,
    best_update_iters: List[int],
    best_update_lex_keys: List[List[float]],
    returned_solution_source: str,
    initial_solution_feasible: bool,
    returned_solution_feasible: bool,
    operator_weights: Dict[str, Any],
    last_acceptance_decision: Optional[Dict[str, Any]],
    last_destroy_move: Optional[Dict[str, Any]],
    destroy_operator_summary: Dict[str, Any],
    repair_operator_summary: Dict[str, Any],
    iteration_trace: List[Dict[str, Any]],
    last_repair: Optional[Dict[str, Any]],
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
        "best_update_lex_keys": [list(x) for x in best_update_lex_keys],
        "first_best_iter": int(best_update_iters[0]) if best_update_iters else None,
        "last_best_iter": int(last_best_iter) if last_best_iter is not None else None,
        "plateau_iters_after_last_update": int(total_iters - last_best_iter) if last_best_iter is not None else int(total_iters),
        "initial_solution_feasible": bool(initial_solution_feasible),
        "returned_solution_source": returned_solution_source,
        "returned_solution_feasible": bool(returned_solution_feasible),
        "last_acceptance_decision": dict(last_acceptance_decision or {}),
        "last_destroy_move": dict(last_destroy_move or {}),
        "last_repair": dict(last_repair or {}),
        "iteration_trace": list(iteration_trace),
        "destroy_operator_summary": _numericize_weight_tree(destroy_operator_summary),
        "repair_operator_summary": _numericize_weight_tree(repair_operator_summary),
        "operator_weights": _numericize_weight_tree(operator_weights),
    }
    return diagnostics


@dataclass(slots=True)
class _AcceptanceDecision:
    compare_result: int
    accepted: bool
    accept_mode: str
    delta_soft: Optional[float] = None
    temperature: Optional[float] = None
    threshold: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "compare_result": int(self.compare_result),
            "accepted": bool(self.accepted),
            "accept_mode": str(self.accept_mode),
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
    config: Config,
    mode: str,
    rng: random.Random,
    temperature: float,
    accept_level: float,
) -> _AcceptanceDecision:
    # compare(...) is the only ordering decision. Soft delta is auxiliary and is
    # only consulted for worse moves (cmp > 0).
    cmp = compare(trial_ev, cur_ev, config)
    if cmp < 0:
        return _AcceptanceDecision(compare_result=cmp, accepted=True, accept_mode=mode)
    if cmp == 0:
        return _AcceptanceDecision(compare_result=cmp, accepted=True, accept_mode=mode)

    if mode == "greedy":
        return _AcceptanceDecision(compare_result=cmp, accepted=False, accept_mode=mode)

    delta_soft = _acceptance_soft_delta(cur_ev, trial_ev, config)
    if mode == "threshold":
        threshold = _threshold_acceptance_limit(cur_ev, trial_ev, accept_level)
        return _AcceptanceDecision(
            compare_result=cmp,
            accepted=(delta_soft <= threshold),
            accept_mode=mode,
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
            delta_soft=delta_soft,
            temperature=float(temperature),
        )

def _acceptance_soft_delta(cur_ev: EvalResult, trial_ev: EvalResult, config: Config) -> float:
    """Auxiliary scalar for worse-move soft acceptance only."""
    layers = list(getattr(config.eval.objective_policy, "layers", []) or [])
    eps = 1e-9
    for layer in layers:
        metric = str(layer.metric)
        direction = str(layer.direction)
        cur_value = _oriented_metric_value(cur_ev, metric, direction)
        trial_value = _oriented_metric_value(trial_ev, metric, direction)
        if abs(trial_value - cur_value) > eps:
            scale = max(1.0, abs(cur_value), abs(trial_value))
            return max(0.0, (trial_value - cur_value) / scale)

    return 0.0


def _oriented_metric_value(ev: EvalResult, metric: str, direction: str) -> float:
    value = float(ev.get_metric(metric))
    return -value if str(direction).lower() == "max" else value


def _threshold_acceptance_limit(cur_ev: EvalResult, trial_ev: EvalResult, accept_level: float) -> float:
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
        fused[str(name)] = (rule ** (1.0 - lam)) * (prior ** lam)
    return fused


def _numericize_weight_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {
            str(key): _numericize_weight_tree(value)
            for key, value in node.items()
        }
    if isinstance(node, (list, tuple)):
        return [_numericize_weight_tree(value) for value in node]
    if isinstance(node, (int, float)):
        return float(node)
    return node


def _trace_lex_key(ev: EvalResult) -> List[float]:
    return [float(value) for value in list(ev.lex_key or ())]


def _trace_objective(ev: EvalResult) -> float:
    lex_key = _trace_lex_key(ev)
    if lex_key:
        return float(lex_key[0])
    return float(ev.get_metric("violation_total"))


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
        weights[name] = (1.0 - float(reaction)) * float(weights[name]) + float(reaction) * max(0.0, avg)
        weights[name] = max(1e-6, float(weights[name]))


def _reset_segment_scores(scores: Dict[str, float], used: Dict[str, int]) -> None:
    for name in list(scores.keys()):
        scores[name] = 0.0
        used[name] = 0


def _budget_ok(budget: Budget, started_at: float, iteration: int) -> bool:
    if budget.time_limit_sec is not None and (time.perf_counter() - started_at) >= float(budget.time_limit_sec):
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
