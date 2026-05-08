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
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from ..config import Budget, Config
from ..console import info, success
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


@dataclass(frozen=True, slots=True)
class _ScoredInsertCandidate:
    position: InsertPosition
    insert_score: float


@dataclass(frozen=True, slots=True)
class _TaskFeasibleInsertAnalysis:
    tid: int
    ranked_candidates: Tuple[_ScoredInsertCandidate, ...]
    feasible_candidates: Tuple[_ScoredInsertCandidate, ...]
    checked_candidate_count: int
    prefix_failures_before_first_feasible: int
    all_candidates_checked: bool

    @property
    def feasible_count(self) -> int:
        return len(self.feasible_candidates)

    @property
    def best_feasible_candidate(self) -> Optional[_ScoredInsertCandidate]:
        if not self.feasible_candidates:
            return None
        return self.feasible_candidates[0]

    @property
    def best_feasible_position(self) -> Optional[InsertPosition]:
        candidate = self.best_feasible_candidate
        if candidate is None:
            return None
        return candidate.position

    @property
    def best_feasible_score(self) -> Optional[float]:
        candidate = self.best_feasible_candidate
        if candidate is None:
            return None
        return float(candidate.insert_score)

    @property
    def second_best_feasible_score(self) -> Optional[float]:
        if len(self.feasible_candidates) < 2:
            return None
        return float(self.feasible_candidates[1].insert_score)


@dataclass(frozen=True, slots=True)
class _TaskRegretEstimate:
    tid: int
    feasible_count: int
    regret: float
    best_feasible_score: float
    second_best_feasible_score: Optional[float]
    insertion_analysis: _TaskFeasibleInsertAnalysis


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
    info(
        "alns_start "
        f"acceptance={policy.acceptance} "
        f"strength_ratio={float(policy.strength_ratio)} "
        f"budget_time_limit_sec={budget.time_limit_sec} "
        f"budget_max_iters={budget.max_iters} "
        f"init_feasible={bool(cur_ev.is_feasible)} "
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
    generators: Dict[str, CandidateGenerator] = {
        "global_assigned": _cand_global_assigned,
        "random_subset": _cand_random_subset,
        "route_segment": _cand_route_segment,
        "route_tail": _cand_route_tail,
        "single_route": _cand_single_route,
    }
    repair_task_ops = {
        "weighted_priority_order": repair_with_weighted_priority,
        "regret2_order": _repair_with_regret2,
    }

    destroy_priors = _sanitize_operator_prior_map(policy.destroy_generator_priors, generators.keys(), default_weight=1.0)
    repair_task_priors = _sanitize_operator_prior_map(policy.repair_task_selector_priors, repair_task_ops.keys(), default_weight=1.0)
    prior_mix_lambda = float(policy.prior_mix_lambda)

    d_w = {name: 1.0 for name in generators}
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
    regret2_repair_summary = _init_regret2_repair_summary()

    restore_every = _clamp_int(int(30 + 70 * (1.0 - accept_level)), 20, 120)
    infeasible_streak = 0
    iteration = 0
    started_at = time.perf_counter()

    while _budget_ok(budget, started_at, iteration):
        iteration += 1
        d_final = _blend_operator_weights(d_w, destroy_priors, prior_mix_lambda)
        r_final = _blend_operator_weights(r_w, repair_task_priors, prior_mix_lambda)
        d_name = _roulette_select(d_final, rng)
        r_name = _roulette_select(r_final, rng)
        d_used[d_name] += 1
        r_used[r_name] += 1

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
        partial.solver_diagnostics = {}
        partial.normalize(instance)

        trial = repair_task_ops[r_name](partial, instance, config, policy, rng)
        trial_regret2_stats = dict((getattr(trial, "solver_diagnostics", {}) or {}).get("last_regret2_repair", {}) or {})
        if r_name == "regret2_order" and trial_regret2_stats:
            _accumulate_regret2_repair_summary(regret2_repair_summary, trial_regret2_stats)

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
        if iteration % 20 == 0:
            trial_unassigned_tids = sorted(int(tid) for tid in trial.unassigned)
            message = (
                f"alns_progress iter={iteration} "
                f"destroy={d_name} repair={r_name} "
                f"accepted={bool(accepted)} feasible={bool(ev_trial.is_feasible)} "
                f"lex_key={ev_trial.lex_key} "
                f"unassigned_count={len(trial_unassigned_tids)} "
                f"unassigned_tids={trial_unassigned_tids}"
            )
            if r_name == "regret2_order" and trial_regret2_stats:
                message = f"{message} {_format_regret2_repair_log(trial_regret2_stats)}"
            info(message)

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

        best_updated = False
        best_feasible_updated = False

        if compare(ev_trial, best_ev, config) < 0:
            best = trial.clone(deep=True)
            best_ev = ev_trial
            best_updated = True
            reward = max(reward, 5.0)

        if ev_trial.is_feasible and (best_feasible_ev is None or compare(ev_trial, best_feasible_ev, config) < 0):
            best_feasible = trial.clone(deep=True)
            best_feasible_ev = ev_trial
            best_feasible_updated = True
            best_update_iters.append(iteration)
            best_update_lex_keys.append(list(best_feasible_ev.lex_key or ()))
            reward = max(reward, 5.0)

        if best_updated:
            message = (
                f"alns_best_update iter={iteration} "
                f"feasible={bool(best_ev.is_feasible)} "
                f"lex_key={best_ev.lex_key}"
            )
            if best_feasible_updated:
                message += " best_feasible_updated=true"
            success(message)

        d_score[d_name] += reward
        r_score[r_name] += reward

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
        regret2_repair_summary=_finalize_regret2_repair_summary(regret2_repair_summary),
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
        },
    )
    success(
        "alns_complete "
        f"returned_source={returned_source} "
        f"total_iters={iteration} "
        f"best_update_count={len(best_update_iters)} "
        f"actual_time_used_sec={round(actual_time_used_sec, 4)} "
        f"returned_feasible={bool(getattr(returned.eval, 'is_feasible', False))}"
    )
    return _attach_solver_diagnostics(
        returned,
        diagnostics,
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
            score_remove_features(features[int(tid)], policy.remove_metric_weights),
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


def repair_with_weighted_priority(
    partial: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    """Repair in weighted task order with insert-score-driven position choice."""
    sol = partial.clone(deep=True)
    ordered_tasks = _order_tasks_weighted_priority(sol, instance, config, policy, rng)
    for tid in ordered_tasks:
        analysis = _find_best_feasible_insertion(sol, tid, instance, config, policy)
        choice = analysis.best_feasible_position if analysis is not None else None
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
    """Repair by regret-2 over strictly feasible insertion positions."""
    sol = partial.clone(deep=True)
    round_stats: List[Dict[str, Any]] = []
    tasks_inserted = 0

    while sol.unassigned:
        chosen: Optional[_TaskRegretEstimate] = None
        ordered_tids = _order_tasks_weighted_priority(sol, instance, config, policy, rng)
        task_scans_by_tid: Dict[int, Dict[str, Any]] = {}
        repairable: List[Tuple[int, Tuple[_ScoredInsertCandidate, ...]]] = []
        for tid in ordered_tids:
            task_id = int(tid)
            ranked_candidates = tuple(_rank_insert_positions_by_score(sol, task_id, instance, config, policy))
            if not ranked_candidates:
                task_scans_by_tid[task_id] = {
                    "tid": task_id,
                    "ranked_position_count": 0,
                    "positions_checked": 0,
                    "feasible_position_count": 0,
                }
                continue
            repairable.append((task_id, ranked_candidates))

        for task_id, ranked_candidates in repairable:
            assert ranked_candidates
            analysis = _collect_feasible_insert_positions(
                sol,
                task_id,
                instance,
                config,
                policy,
                ranked_candidates=ranked_candidates,
            )
            task_scans_by_tid[task_id] = {
                "tid": task_id,
                "ranked_position_count": int(len(ranked_candidates)),
                "positions_checked": int(analysis.checked_candidate_count),
                "feasible_position_count": int(analysis.feasible_count),
            }
            regret = _compute_regret2_from_feasible_positions(analysis)
            if regret is None:
                continue
            best_feasible_score = analysis.best_feasible_score
            assert best_feasible_score is not None
            candidate = _TaskRegretEstimate(
                tid=task_id,
                feasible_count=int(analysis.feasible_count),
                regret=float(regret),
                best_feasible_score=float(best_feasible_score),
                second_best_feasible_score=analysis.second_best_feasible_score,
                insertion_analysis=analysis,
            )
            if _is_higher_regret_priority(candidate, chosen):
                chosen = candidate

        round_stats.append(
            {
                "remaining_unassigned": int(len(sol.unassigned)),
                "task_count": int(len(ordered_tids)),
                "selected_tid": (None if chosen is None else int(chosen.tid)),
                "task_scans": [task_scans_by_tid[int(tid)] for tid in ordered_tids],
            }
        )

        if chosen is None:
            break

        chosen_position = chosen.insertion_analysis.best_feasible_position
        assert chosen_position is not None

        sol.add_task(int(chosen_position.agent_id), int(chosen.tid), position=int(chosen_position.position))
        sol.unassigned.discard(int(chosen.tid))
        tasks_inserted += 1

    sol.solver_diagnostics["last_regret2_repair"] = _build_regret2_repair_stats(
        rounds=round_stats,
        tasks_inserted=tasks_inserted,
    )

    return sol


def _build_regret2_repair_stats(
    *,
    rounds: Sequence[Dict[str, Any]],
    tasks_inserted: int,
) -> Dict[str, Any]:
    round_count = len(rounds)
    total_tasks_analyzed = sum(int(round_stat.get("task_count", 0)) for round_stat in rounds)
    total_positions_checked = sum(
        int(task_scan.get("positions_checked", 0))
        for round_stat in rounds
        for task_scan in list(round_stat.get("task_scans", []) or [])
    )
    return {
        "round_count": int(round_count),
        "tasks_inserted": int(tasks_inserted),
        "total_tasks_analyzed": int(total_tasks_analyzed),
        "avg_tasks_analyzed_per_round": round(float(total_tasks_analyzed) / float(round_count), 4) if round_count else 0.0,
        "total_positions_checked": int(total_positions_checked),
        "avg_positions_checked_per_task": round(float(total_positions_checked) / float(total_tasks_analyzed), 4) if total_tasks_analyzed else 0.0,
        "rounds": [dict(round_stat) for round_stat in rounds],
    }


def _format_regret2_repair_log(stats: Dict[str, Any]) -> str:
    rounds = list(stats.get("rounds", []) or [])
    if not rounds:
        return "regret2=full, rounds=0"

    last_round = dict(rounds[-1])
    task_scans = list(last_round.get("task_scans", []) or [])
    preview_limit = 8
    preview = ", ".join(
        f"{int(scan.get('tid', -1))}:{int(scan.get('positions_checked', 0))}"
        for scan in task_scans[:preview_limit]
    )
    if len(task_scans) > preview_limit:
        preview = f"{preview}, ...+{len(task_scans) - preview_limit}" if preview else f"...+{len(task_scans) - preview_limit}"

    return (
        "regret2=full, "
        f"tasks={int(last_round.get('task_count', 0))}, "
        f"pos_checks=[{preview}], "
        f"rounds={int(stats.get('round_count', 0))}, "
        f"avg_pos={float(stats.get('avg_positions_checked_per_task', 0.0)):.2f}"
    )


def _init_regret2_repair_summary() -> Dict[str, Any]:
    return {
        "calls": 0,
        "total_repair_rounds": 0,
        "total_tasks_analyzed": 0,
        "total_positions_checked": 0,
        "last_call": {},
    }


def _accumulate_regret2_repair_summary(summary: Dict[str, Any], call_stats: Dict[str, Any]) -> None:
    summary["calls"] = int(summary.get("calls", 0)) + 1
    summary["total_repair_rounds"] = int(summary.get("total_repair_rounds", 0)) + int(call_stats.get("round_count", 0))
    summary["total_tasks_analyzed"] = int(summary.get("total_tasks_analyzed", 0)) + int(call_stats.get("total_tasks_analyzed", 0))
    summary["total_positions_checked"] = int(summary.get("total_positions_checked", 0)) + int(call_stats.get("total_positions_checked", 0))
    summary["last_call"] = dict(call_stats)


def _finalize_regret2_repair_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    calls = int(summary.get("calls", 0))
    if calls <= 0:
        return {}

    total_rounds = int(summary.get("total_repair_rounds", 0))
    total_tasks = int(summary.get("total_tasks_analyzed", 0))
    finalized = dict(summary)
    finalized["avg_tasks_analyzed_per_round"] = round(float(total_tasks) / float(total_rounds), 4) if total_rounds else 0.0
    finalized["avg_positions_checked_per_task"] = (
        round(float(int(summary.get("total_positions_checked", 0))) / float(total_tasks), 4)
        if total_tasks
        else 0.0
    )
    return finalized


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
            score_reinsert_task_features(features[int(tid)], policy.reinsert_metric_weights),
            int(tid),
        )
        for tid in tasks
    ]
    scored.sort(key=lambda item: (-float(item[0]), int(item[1])))
    return [tid for _, tid in scored]


def _rank_insert_positions_by_score(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
) -> List[_ScoredInsertCandidate]:
    """Rank loosely filtered insertion positions by insert score.

    The filters only remove obviously bad positions. The returned order is the
    formal position-choice priority used by weighted-priority repair and regret-2.
    """
    positions = enumerate_filtered_insert_positions(sol, tid, instance, config)
    if not positions:
        return []

    feature_map = compute_insert_candidate_features_batch(sol, tid, positions, instance, config)
    ranked = [
        _ScoredInsertCandidate(
            position=position,
            insert_score=score_insert_candidate_features(feature_map[position], policy.insert_metric_weights),
        )
        for position in positions
    ]
    ranked.sort(
        key=lambda item: (
            float(item.insert_score),
            int(item.position.agent_id),
            int(item.position.position),
        )
    )
    return ranked


def _strict_eval_insert_candidate(
    sol: AssignmentSolution,
    tid: int,
    candidate: _ScoredInsertCandidate,
    instance: Instance,
    config: Config,
) -> bool:
    """Run strict feasibility evaluation for one scored insertion candidate."""
    trial = sol.clone(deep=True)
    position = candidate.position
    trial.add_task(int(position.agent_id), int(tid), position=int(position.position))
    ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)
    return bool(ev_trial.is_feasible)


def _scan_ranked_insert_candidates(
    sol: AssignmentSolution,
    tid: int,
    *,
    ranked_candidates: Sequence[_ScoredInsertCandidate],
    instance: Instance,
    config: Config,
    stop_after_first_feasible: bool,
) -> _TaskFeasibleInsertAnalysis:
    """Strictly scan scored insertion candidates in ranked order."""
    feasible_candidates: List[_ScoredInsertCandidate] = []
    prefix_failures_before_first_feasible = 0
    checked_candidate_count = 0

    for candidate in ranked_candidates:
        checked_candidate_count += 1
        is_feasible = _strict_eval_insert_candidate(sol, tid, candidate, instance, config)
        if is_feasible:
            feasible_candidates.append(candidate)
            if stop_after_first_feasible:
                break
            continue
        if not feasible_candidates:
            prefix_failures_before_first_feasible += 1

    analysis = _TaskFeasibleInsertAnalysis(
        tid=int(tid),
        ranked_candidates=tuple(ranked_candidates),
        feasible_candidates=tuple(feasible_candidates),
        checked_candidate_count=int(checked_candidate_count),
        prefix_failures_before_first_feasible=int(prefix_failures_before_first_feasible),
        all_candidates_checked=bool(checked_candidate_count == len(ranked_candidates)),
    )
    return analysis


def _collect_feasible_insert_positions(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    *,
    ranked_candidates: Sequence[_ScoredInsertCandidate],
) -> _TaskFeasibleInsertAnalysis:
    """Collect all strictly feasible insertion positions for one task."""
    del policy
    ranked = tuple(ranked_candidates)
    assert ranked
    return _scan_ranked_insert_candidates(
        sol,
        tid,
        ranked_candidates=ranked,
        instance=instance,
        config=config,
        stop_after_first_feasible=False,
    )


def _find_best_feasible_insertion(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    *,
    ranked_candidates: Optional[Sequence[_ScoredInsertCandidate]] = None,
) -> Optional[_TaskFeasibleInsertAnalysis]:
    """Return the first strictly feasible insertion in insert-score order."""
    ranked = tuple(ranked_candidates) if ranked_candidates is not None else tuple(_rank_insert_positions_by_score(sol, tid, instance, config, policy))
    if not ranked:
        return None
    analysis = _scan_ranked_insert_candidates(
        sol,
        tid,
        ranked_candidates=ranked,
        instance=instance,
        config=config,
        stop_after_first_feasible=True,
    )
    if analysis.best_feasible_position is None:
        return None
    return analysis


def _compute_regret2_from_feasible_positions(analysis: _TaskFeasibleInsertAnalysis) -> Optional[float]:
    """Compute regret-2 from strictly feasible insertion positions only."""
    if analysis.feasible_count == 0:
        return None
    if analysis.feasible_count == 1:
        return float("inf")
    best_score = analysis.best_feasible_score
    second_best_score = analysis.second_best_feasible_score
    if best_score is None or second_best_score is None:
        return None
    return float(second_best_score) - float(best_score)


def _is_higher_regret_priority(
    candidate: _TaskRegretEstimate,
    incumbent: Optional[_TaskRegretEstimate],
) -> bool:
    """Prefer single-feasible tasks, otherwise maximize regret-2."""
    if incumbent is None:
        return True

    candidate_single = candidate.feasible_count == 1
    incumbent_single = incumbent.feasible_count == 1
    if candidate_single != incumbent_single:
        return candidate_single
    if candidate_single and incumbent_single:
        return candidate.best_feasible_score < incumbent.best_feasible_score - 1e-12

    if candidate.regret > incumbent.regret + 1e-12:
        return True
    if abs(candidate.regret - incumbent.regret) <= 1e-12 and candidate.best_feasible_score < incumbent.best_feasible_score - 1e-12:
        return True
    return False


def _restore_feasibility(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
    max_remove: int = 8,
) -> AssignmentSolution:
    """Conservative feasibility restore using the formal repair selector."""
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
    repaired = repair_with_weighted_priority(work, instance, config, policy, rng)
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
    actual_time_used_sec: float,
    best_update_iters: List[int],
    best_update_lex_keys: List[List[float]],
    returned_solution_source: str,
    initial_solution_feasible: bool,
    returned_solution_feasible: bool,
    operator_weights: Dict[str, Any],
    last_acceptance_decision: Optional[Dict[str, Any]],
    regret2_repair_summary: Optional[Dict[str, Any]],
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
        "operator_weights": _numericize_weight_tree(operator_weights),
    }
    if regret2_repair_summary:
        diagnostics["regret2_repair"] = dict(regret2_repair_summary)
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

    return _AcceptanceDecision(compare_result=cmp, accepted=False, accept_mode=mode)


def _acceptance_soft_delta(cur_ev: EvalResult, trial_ev: EvalResult, config: Config) -> float:
    """Auxiliary scalar for worse-move soft acceptance only."""
    layers = list(getattr(config.eval.objective_policy, "layers", []) or [])
    if not layers:
        cur_value = _oriented_metric_value(cur_ev, "energy_total", "min")
        trial_value = _oriented_metric_value(trial_ev, "energy_total", "min")
        scale = max(1.0, abs(cur_value), abs(trial_value))
        return max(0.0, (trial_value - cur_value) / scale)

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


def _soft_metric_value(ev: EvalResult, config: Config, fallback_metric: str = "energy_total") -> float:
    """Oriented scalar helper used by regret cost for already-feasible trials."""
    layers = list(getattr(config.eval.objective_policy, "layers", []) or [])
    metric = fallback_metric
    direction = "min"
    if len(layers) >= 2:
        metric = str(layers[1].metric)
        direction = str(layers[1].direction)
    return _oriented_metric_value(ev, metric, direction)


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
    if budget.time_limit_sec is not None and (time.perf_counter() - started_at) >= float(budget.time_limit_sec):
        return False
    if budget.max_iters is not None and iteration >= int(budget.max_iters):
        return False
    return True


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(int(lo), min(int(hi), int(value)))


def _clamp_float(value: float, lo: float, hi: float) -> float:
    return max(float(lo), min(float(hi), float(value)))
