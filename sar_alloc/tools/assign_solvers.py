from __future__ import annotations

"""Weighted ALNS solver with unified metric-driven local operator decisions."""

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from ..config import Budget, Config
from ..console import success
from ..evaluator import compare, evaluate as _evaluate_raw
from ..models import Instance
from ..operators import InsertPosition, WeightedALNSPolicy
from ..operators.features import (
    compute_insert_candidate_features_batch,
    compute_reinsert_task_features_batch,
    compute_task_remove_features_batch,
    enumerate_filtered_insert_positions,
)
from ..operators.scoring import (
    score_insert_candidate_features,
    score_reinsert_task_features,
    score_remove_features,
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


CandidateGenerator = Callable[[AssignmentSolution, Instance, Config, int, random.Random], List[int]]


def solve_assignment(
    instance: Instance,
    init_solution: AssignmentSolution,
    config: Config,
    budget: Budget,
    policy: WeightedALNSPolicy,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Run a weighted-operator ALNS search from the given incumbent."""
    rng = random.Random(int(rng_seed))

    cur = init_solution.clone(deep=True)
    cur.normalize(instance)
    cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)

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
    generators: Dict[str, CandidateGenerator] = {
        "global_assigned": _cand_global_assigned,
        "random_subset": _cand_random_subset,
        "route_segment": _cand_route_segment,
        "route_tail": _cand_route_tail,
        "single_route": _cand_single_route,
    }
    repair_task_ops = {
        "weighted_priority_order": _repair_with_weighted_priority,
        "regret2_order": _repair_with_regret2,
    }

    if policy.repair_position_selector != "filtered_best_position":
        raise ValueError(f"Unsupported repair position selector: {policy.repair_position_selector}")

    destroy_priors = _sanitize_operator_prior_map(policy.destroy_generator_priors, generators.keys(), default_weight=1.0)
    repair_task_priors = _sanitize_operator_prior_map(policy.repair_task_selector_priors, repair_task_ops.keys(), default_weight=1.0)
    p_name = str(policy.repair_position_selector)
    prior_mix_lambda = float(policy.prior_mix_lambda)

    d_w = {name: 1.0 for name in generators}
    r_w = {name: 1.0 for name in repair_task_ops}
    p_w = {p_name: 1.0}

    d_score = {name: 0.0 for name in d_w}
    r_score = {name: 0.0 for name in r_w}
    p_score = {name: 0.0 for name in p_w}

    d_used = {name: 0 for name in d_w}
    r_used = {name: 0 for name in r_w}
    p_used = {name: 0 for name in p_w}

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

    restore_every = _clamp_int(int(30 + 70 * (1.0 - accept_level)), 20, 120)
    infeasible_streak = 0
    iteration = 0
    started_at = time.time()

    while _budget_ok(budget, started_at, iteration):
        iteration += 1
        d_final = _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda)
        r_final = _blend_operator_weights(r_w, repair_task_priors, prior_mix_lambda)
        d_name = _roulette_select(d_final, rng)
        r_name = _roulette_select(r_final, rng)
        d_used[d_name] += 1
        r_used[r_name] += 1
        p_used[p_name] += 1

        removed = select_tasks_to_remove(
            sol=cur,
            instance=instance,
            config=config,
            policy=policy,
            generator=generators[d_name],
            rng=rng,
        )

        partial = cur.clone(deep=True)
        _remove_tasks(partial, removed)
        partial.normalize(instance)

        trial = repair_task_ops[r_name](partial, instance, config, policy, rng)

        trial.normalize(instance)
        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)

        accepted = _alns_accept(
            cur_ev=cur_ev,
            trial_ev=ev_trial,
            config=config,
            mode=policy.acceptance,
            rng=rng,
            temperature=temperature,
            accept_level=accept_level,
        )

        reward = 0.0
        if accepted:
            cur = trial
            cur_ev = ev_trial
            reward = max(reward, 0.2)

        infeasible_streak = 0 if cur_ev.is_feasible else (infeasible_streak + 1)
        if (not cur_ev.is_feasible) and (infeasible_streak >= restore_every or iteration % restore_every == 0):
            cur = _restore_feasibility(cur, instance, config, policy, rng)
            cur.normalize(instance)
            cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)
            infeasible_streak = 0 if cur_ev.is_feasible else 1

        if compare(ev_trial, best_ev, config) < 0:
            best = trial.clone(deep=True)
            best_ev = ev_trial
            reward = max(reward, 5.0)

        if ev_trial.is_feasible and (best_feasible_ev is None or compare(ev_trial, best_feasible_ev, config) < 0):
            best_feasible = trial.clone(deep=True)
            best_feasible_ev = ev_trial
            best_update_iters.append(iteration)
            best_update_lex_keys.append(list(best_feasible_ev.lex_key or ()))
            success(
                f"Weighted ALNS found a new best feasible solution at iter={iteration}, "
                f"lex_key={best_feasible_ev.lex_key}"
            )
            reward = max(reward, 5.0)

        d_score[d_name] += reward
        r_score[r_name] += reward
        p_score[p_name] += reward

        if policy.acceptance == "sa":
            temperature = max(1e-9, temperature * cooling)

        if iteration % segment_len == 0:
            _update_weights(d_w, d_score, d_used, reaction)
            _update_weights(r_w, r_score, r_used, reaction)
            _update_weights(p_w, p_score, p_used, reaction)
            _reset_segment_scores(d_score, d_used)
            _reset_segment_scores(r_score, r_used)
            _reset_segment_scores(p_score, p_used)

    returned = best_feasible if best_feasible is not None else best
    returned_source = "best_feasible" if best_feasible is not None else "best_overall"
    evaluate(returned, instance, config, update_solution_schedule=True)
    return _attach_solver_diagnostics(
        returned,
        _build_solver_diagnostics(
            policy=policy,
            total_iters=iteration,
            best_update_iters=best_update_iters,
            best_update_lex_keys=best_update_lex_keys,
            returned_solution_source=returned_source,
            initial_solution_feasible=initial_solution_feasible,
            returned_solution_feasible=bool(getattr(returned.eval, "is_feasible", False)),
            operator_weights={
                "destroy_candidate_generators": {
                    "adaptive": d_w,
                    "llm_prior": destroy_priors,
                    "fused_final": _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda),
                },
                "repair_task_selectors": {
                    "adaptive": r_w,
                    "llm_prior": repair_task_priors,
                    "fused_final": _blend_operator_weights(r_w, repair_task_priors, prior_mix_lambda),
                },
                "repair_position_selectors": {
                    "adaptive": p_w,
                },
            },
        ),
    )


def select_tasks_to_remove(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    generator: CandidateGenerator,
    rng: random.Random,
) -> List[int]:
    assigned = list(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned:
        return []

    k = _clamp_int(
        int(round(float(policy.strength_ratio) * max(1, len(assigned)))),
        1,
        len(assigned),
    )
    candidate_tids = list(dict.fromkeys(int(tid) for tid in generator(sol, instance, config, k, rng)))
    if not candidate_tids:
        return []

    features = compute_task_remove_features_batch(sol, candidate_tids, instance, config)
    scored = [
        (
            score_remove_features(features[int(tid)], policy.metric_weights),
            int(tid),
        )
        for tid in candidate_tids
    ]
    scored.sort(key=lambda item: (-float(item[0]), int(item[1])))
    return [tid for _, tid in scored[: min(k, len(scored))]]


def _cand_global_assigned(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    target_k: int,
    rng: random.Random,
) -> List[int]:
    del instance, config, target_k, rng
    return list(int(tid) for tid in sol.all_assigned_tasks())


def _cand_random_subset(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    target_k: int,
    rng: random.Random,
) -> List[int]:
    del instance, config
    assigned = list(int(tid) for tid in sol.all_assigned_tasks())
    rng.shuffle(assigned)
    subset_size = min(len(assigned), max(target_k, target_k * 2))
    return assigned[:subset_size]


def _cand_route_segment(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    target_k: int,
    rng: random.Random,
) -> List[int]:
    del instance, config
    return _structured_route_candidates(sol, target_k, rng, mode="segment")


def _cand_route_tail(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    target_k: int,
    rng: random.Random,
) -> List[int]:
    del instance, config
    return _structured_route_candidates(sol, target_k, rng, mode="tail")


def _cand_single_route(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    target_k: int,
    rng: random.Random,
) -> List[int]:
    del instance, config
    return _structured_route_candidates(sol, target_k, rng, mode="whole_route")


def _structured_route_candidates(sol: AssignmentSolution, target_k: int, rng: random.Random, mode: str) -> List[int]:
    nonempty_routes = [list(route) for route in sol.routes.values() if route]
    if not nonempty_routes:
        return []

    rng.shuffle(nonempty_routes)
    chosen: List[int] = []
    for route in nonempty_routes:
        if mode == "segment":
            if len(route) <= target_k:
                piece = list(route)
            else:
                seg_len = min(len(route), max(target_k, min(2 * target_k, len(route))))
                start = rng.randrange(0, len(route) - seg_len + 1)
                piece = list(route[start : start + seg_len])
        elif mode == "tail":
            if len(route) <= target_k:
                piece = list(route)
            else:
                tail_len = min(len(route), max(target_k, min(2 * target_k, len(route))))
                piece = list(route[-tail_len:])
        else:
            piece = list(route)

        for tid in piece:
            if int(tid) not in chosen:
                chosen.append(int(tid))
        if len(chosen) >= target_k:
            break
    return chosen


def _repair_with_weighted_priority(
    partial: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    """Repair in weighted task order, but restore exact-evaluate position choice.

    The weighted metrics still decide which unassigned task to try first. The
    final insertion position is selected only after exact trial construction and
    global evaluator comparison across all filtered positions.
    """
    sol = partial.clone(deep=True)
    ordered_tasks = _order_tasks_weighted_priority(sol, instance, config, policy, rng)
    for tid in ordered_tasks:
        choice = _select_best_feasible_position_by_eval(sol, tid, instance, config)
        if choice is not None:
            sol.add_task(int(choice.agent_id), int(tid), position=int(choice.position))
            sol.unassigned.discard(int(tid))
    return sol


def _repair_with_regret2(
    partial: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    """Restore classic regret-2 based on exact feasible insert evaluations.

    The weighted metrics can still help prioritize which task to inspect first,
    but best1/best2 and the final chosen insertion are derived from exact trial
    evaluation rather than from insertion feature scores.
    """
    sol = partial.clone(deep=True)

    while sol.unassigned:
        chosen_tid: Optional[int] = None
        chosen_position: Optional[InsertPosition] = None
        chosen_best_ev: Optional[EvalResult] = None
        chosen_regret = -float("inf")

        candidate_tids = _order_tasks_weighted_priority(sol, instance, config, policy, rng)
        for tid in candidate_tids:
            feasible_candidates = _collect_feasible_insert_evals(sol, int(tid), instance, config)
            if not feasible_candidates:
                continue

            best1: Optional[Tuple[InsertPosition, AssignmentSolution, EvalResult]] = None
            best2: Optional[Tuple[InsertPosition, AssignmentSolution, EvalResult]] = None
            for candidate in feasible_candidates:
                _, _, ev_candidate = candidate
                if best1 is None or compare(ev_candidate, best1[2], config) < 0:
                    best2 = best1
                    best1 = candidate
                elif best2 is None or compare(ev_candidate, best2[2], config) < 0:
                    best2 = candidate

            if best1 is None:
                continue

            best1_position, _, best1_ev = best1
            if best2 is None:
                regret = float("inf")
            else:
                regret = _cost_from_feasible_eval(best2[2], config) - _cost_from_feasible_eval(best1_ev, config)

            if regret > chosen_regret + 1e-12:
                chosen_tid = int(tid)
                chosen_position = best1_position
                chosen_best_ev = best1_ev
                chosen_regret = float(regret)
            elif abs(regret - chosen_regret) <= 1e-12:
                if chosen_best_ev is None or compare(best1_ev, chosen_best_ev, config) < 0:
                    chosen_tid = int(tid)
                    chosen_position = best1_position
                    chosen_best_ev = best1_ev

        if chosen_tid is None or chosen_position is None:
            break

        sol.add_task(int(chosen_position.agent_id), int(chosen_tid), position=int(chosen_position.position))
        sol.unassigned.discard(int(chosen_tid))

    return sol


def _order_tasks_weighted_priority(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> List[int]:
    del rng
    tasks = list(int(tid) for tid in sol.unassigned)
    if not tasks:
        return []
    features = compute_reinsert_task_features_batch(sol, tasks, instance, config)
    scored = [
        (
            score_reinsert_task_features(features[int(tid)], policy.metric_weights),
            int(tid),
        )
        for tid in tasks
    ]
    scored.sort(key=lambda item: (-float(item[0]), int(item[1])))
    return [tid for _, tid in scored]


def _select_best_feasible_position_by_eval(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
) -> Optional[InsertPosition]:
    """Exact-feasible insertion choice restored from the older ALNS behavior.

    Positions are still filtered cheaply first, but the final placement is chosen
    only by evaluating each trial solution and comparing feasible results.
    """
    best_position: Optional[InsertPosition] = None
    best_ev: Optional[EvalResult] = None

    for position, _, ev_trial in _collect_insert_trial_evals(sol, tid, instance, config):
        if not ev_trial.is_feasible:
            continue
        if best_ev is None or compare(ev_trial, best_ev, config) < 0:
            best_position = position
            best_ev = ev_trial

    return best_position


def _collect_insert_trial_evals(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    *,
    candidate_positions: Optional[Sequence[InsertPosition]] = None,
) -> List[Tuple[InsertPosition, AssignmentSolution, EvalResult]]:
    """Enumerate filtered insertion moves and evaluate the resulting trials."""
    positions = list(candidate_positions) if candidate_positions is not None else enumerate_filtered_insert_positions(sol, tid, instance, config)
    evaluated: List[Tuple[InsertPosition, AssignmentSolution, EvalResult]] = []

    for position in positions:
        trial = sol.clone(deep=True)
        trial.add_task(int(position.agent_id), int(tid), position=int(position.position))
        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)
        evaluated.append((position, trial, ev_trial))

    return evaluated


def _collect_feasible_insert_evals(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    *,
    candidate_positions: Optional[Sequence[InsertPosition]] = None,
) -> List[Tuple[InsertPosition, AssignmentSolution, EvalResult]]:
    return [
        candidate
        for candidate in _collect_insert_trial_evals(sol, tid, instance, config, candidate_positions=candidate_positions)
        if candidate[2].is_feasible
    ]


def _cost_from_feasible_eval(ev: EvalResult, config: Config) -> float:
    """Scalar regret cost for already-feasible trials; smaller is better."""
    return _soft_metric_value(ev, config, fallback_metric="energy_total")


def _select_filtered_best_position_by_score(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
) -> Optional[InsertPosition]:
    """Score-only helper retained for debugging/reference.

    Repair, regret2, and local search no longer rely on this function for final
    move decisions. Exact evaluator comparison drives those choices.
    """
    positions = enumerate_filtered_insert_positions(sol, tid, instance, config)
    if not positions:
        return None

    feature_map = compute_insert_candidate_features_batch(sol, tid, positions, instance, config)
    scored = [
        (
            score_insert_candidate_features(feature_map[position], policy.metric_weights),
            position,
        )
        for position in positions
    ]
    scored.sort(key=lambda item: (float(item[0]), int(item[1].agent_id), int(item[1].position)))
    return scored[0][1]


def _restore_feasibility(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
    max_remove: int = 8,
) -> AssignmentSolution:
    """Conservative feasibility restore restored to exact greedy repair behavior."""
    work = sol.clone(deep=True)
    work.normalize(instance)
    initial_ev = evaluate(work, instance, config, update_solution_schedule=False)
    if initial_ev.is_feasible:
        return work
    initial_violation = float(initial_ev.get_metric("violation_total"))

    removed_any = False
    current_ev = initial_ev
    for _ in range(int(max_remove)):
        candidates = [(int(aid), list(route)) for aid, route in work.routes.items() if route]
        if not candidates:
            break

        longest_len = max(len(route) for _, route in candidates)
        longest_routes = [(aid, route) for aid, route in candidates if len(route) == longest_len]
        aid, route = longest_routes[rng.randrange(len(longest_routes))]
        remove_pos = rng.randrange(len(route))
        tid = int(route[remove_pos])
        work.remove_task(int(aid), int(tid), to_unassigned=True)
        work.normalize(instance)
        current_ev = evaluate(work, instance, config, update_solution_schedule=False)
        removed_any = True
        if current_ev.is_feasible:
            break

    if not removed_any:
        return work

    violation_after_removal = float(current_ev.get_metric("violation_total"))
    repaired = _repair_with_weighted_priority(work, instance, config, policy, rng)
    repaired.normalize(instance)
    ev_repaired = evaluate(repaired, instance, config, update_solution_schedule=False)
    repaired_violation = float(ev_repaired.get_metric("violation_total"))

    if repaired_violation <= violation_after_removal or repaired_violation < initial_violation:
        return repaired
    return work


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
    best_update_iters: List[int],
    best_update_lex_keys: List[List[float]],
    returned_solution_source: str,
    initial_solution_feasible: bool,
    returned_solution_feasible: bool,
    operator_weights: Dict[str, Any],
) -> Dict[str, Any]:
    last_best_iter = best_update_iters[-1] if best_update_iters else None
    return {
        "algorithm": "weighted_alns",
        "policy": policy.as_dict(),
        "total_iters": int(total_iters),
        "best_update_count": len(best_update_iters),
        "best_update_iters": [int(x) for x in best_update_iters],
        "best_update_lex_keys": [list(x) for x in best_update_lex_keys],
        "first_best_iter": int(best_update_iters[0]) if best_update_iters else None,
        "last_best_iter": int(last_best_iter) if last_best_iter is not None else None,
        "plateau_iters_after_last_update": int(total_iters - last_best_iter) if last_best_iter is not None else int(total_iters),
        "initial_solution_feasible": bool(initial_solution_feasible),
        "returned_solution_source": returned_solution_source,
        "returned_solution_feasible": bool(returned_solution_feasible),
        "operator_weights": _numericize_weight_tree(operator_weights),
    }


def _alns_accept(
    cur_ev: EvalResult,
    trial_ev: EvalResult,
    config: Config,
    mode: str,
    rng: random.Random,
    temperature: float,
    accept_level: float,
) -> bool:
    tol = 1e-9
    if _deb_compare_eval(trial_ev, cur_ev, config, tol=tol) < 0:
        return True

    if mode == "greedy":
        return False

    if cur_ev.is_feasible and (not trial_ev.is_feasible):
        return False
    if (not cur_ev.is_feasible) and trial_ev.is_feasible:
        return True

    if cur_ev.is_feasible and trial_ev.is_feasible:
        soft_cur = _soft_metric_value(cur_ev, config, fallback_metric="energy_total")
        soft_trial = _soft_metric_value(trial_ev, config, fallback_metric="energy_total")
        denom = max(1.0, abs(soft_cur))
        delta_ratio = (soft_trial - soft_cur) / denom
        if mode == "threshold":
            return delta_ratio <= (0.01 + 0.12 * float(accept_level))
        if mode == "sa":
            if delta_ratio <= 0:
                return True
            return rng.random() < math.exp(-delta_ratio / max(1e-12, temperature))
        return False

    cur_violation = float(cur_ev.get_metric("violation_total"))
    trial_violation = float(trial_ev.get_metric("violation_total"))
    denom = max(1.0, abs(cur_violation))
    delta_ratio = (trial_violation - cur_violation) / denom
    if mode == "threshold":
        return delta_ratio <= (0.005 + 0.06 * float(accept_level))
    if mode == "sa":
        if delta_ratio <= 0:
            return True
        return rng.random() < math.exp(-delta_ratio / max(1e-12, temperature))
    return False


def _deb_compare_eval(a: EvalResult, b: Optional[EvalResult], config: Config, tol: float = 1e-9) -> int:
    if b is None:
        return -1
    if a.is_feasible and (not b.is_feasible):
        return -1
    if (not a.is_feasible) and b.is_feasible:
        return 1
    if a.is_feasible and b.is_feasible:
        c = compare(a, b, config)
        return -1 if c < 0 else (1 if c > 0 else 0)
    va = float(a.get_metric("violation_total"))
    vb = float(b.get_metric("violation_total"))
    if abs(va - vb) > tol:
        return -1 if va < vb else 1
    c = compare(a, b, config)
    return -1 if c < 0 else (1 if c > 0 else 0)


def _soft_metric_value(ev: EvalResult, config: Config, fallback_metric: str = "energy_total") -> float:
    layers = list(getattr(config.eval.objective_policy, "layers", []) or [])
    metric = fallback_metric
    direction = "min"
    if len(layers) >= 2:
        metric = str(layers[1].metric)
        direction = str(layers[1].direction)
    value = float(ev.get_metric(metric))
    return -value if direction == "max" else value


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
        prior = max(1e-9, float(llm_priors.get(str(name), 1.0)))
        fused[str(name)] = (rule ** (1.0 - lam)) * (prior ** lam)
    return fused


def _sanitize_operator_prior_map(
    priors: Dict[str, float],
    allowed_names: Sequence[str],
    *,
    default_weight: float,
) -> Dict[str, float]:
    sanitized: Dict[str, float] = {}
    source = priors if isinstance(priors, dict) else {}
    for name in allowed_names:
        sanitized[str(name)] = max(1e-9, float(source.get(str(name), default_weight)))
    return sanitized


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
    if budget.time_limit_sec is not None and (time.time() - started_at) >= float(budget.time_limit_sec):
        return False
    if budget.max_iters is not None and iteration >= int(budget.max_iters):
        return False
    return True


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(int(lo), min(int(hi), int(value)))


def _clamp_float(value: float, lo: float, hi: float) -> float:
    return max(float(lo), min(float(hi), float(value)))
