from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..config import Config
from ..evaluator import evaluate
from ..models import Agent, Instance, Location, Task
from ..solution import AssignmentSolution
from .features import basic_insertion_feasibility_filter, insertion_lower_bound_filter
from .scoring import operator_score_to_prior, score_metric_preferences
from .types import (
    DESTROY_CANDIDATE_GENERATORS,
    REPAIR_TASK_SELECTORS,
    SEARCH_DIAGNOSIS_FIELDS,
    LandscapeFeatures,
    LandscapeMetricPreferences,
    MetricPreference,
    PositionFeatures,
    PositionMetricPreferences,
    InsertPosition,
    WeightedALNSPolicy,
)


_EPS = 1e-9
_BIG_M = 1e12
_ZERO_LANDSCAPE_FEATURES = LandscapeFeatures(
    cost_pressure=0.0,
    scarcity_pressure=0.0,
    coupling_pressure=0.0,
    mobility_opportunity=0.0,
    balance_pressure=0.0,
)
_ZERO_POSITION_FEATURES = PositionFeatures(
    insert_cost=0.0,
    future_slack=0.0,
    route_balance_gain=0.0,
    local_coupling_penalty=0.0,
    diversity_gain=0.0,
)


@dataclass(frozen=True)
class RepairBudget:
    max_tasks_considered: int
    max_positions_per_task: int
    strict_check_limit: int


@dataclass(frozen=True)
class RepairCandidate:
    tid: int
    agent_id: int
    position: int
    delta_distance: float
    delta_energy: float
    route_duration_after: float
    suffix_min_slack: float
    suffix_tardiness_total: float
    suffix_ratio: float
    energy_remaining_ratio: float
    depot_return_pressure: float
    route_pressure_after: float
    balance_improvement: float
    candidate_cost: float
    dominated: bool
    strict_feasible: bool
    position_features: PositionFeatures = _ZERO_POSITION_FEATURES
    position_score: float = 0.0


@dataclass(frozen=True)
class TaskRepairStats:
    tid: int
    candidate_count: int
    feasible_count: int
    feasible_agent_count: int
    best_cost: float
    sorted_feasible_candidates: Tuple[RepairCandidate, ...]
    task_priority: float
    time_window_width: float
    service_time: float
    energy_lb: float
    recent_fail_count: int
    recent_tw_fail_count: int
    recent_energy_fail_count: int
    recent_skill_fail_count: int
    landscape_features: LandscapeFeatures = _ZERO_LANDSCAPE_FEATURES
    task_score: float = 0.0


@dataclass(frozen=True)
class _RouteStop:
    start_time: float
    end_time: float
    slack: float
    tardiness: float


@dataclass(frozen=True)
class _RouteMetrics:
    duration: float
    energy: float
    distance: float
    min_slack: float


def enumerate_hard_filtered_positions(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
) -> List[InsertPosition]:
    positions = basic_insertion_feasibility_filter(sol, tid, instance, config, candidate_positions=None)
    if not positions:
        return []
    return insertion_lower_bound_filter(sol, tid, instance, config, candidate_positions=positions)


def compute_repair_candidate(
    sol: AssignmentSolution,
    tid: int,
    position: InsertPosition,
    instance: Instance,
    config: Config,
    route_pressure_before: Dict[int, float],
) -> RepairCandidate:
    return _strict_evaluate_repair_candidate(
        _build_lightweight_repair_candidate(
            sol=sol,
            tid=tid,
            position=position,
            instance=instance,
            config=config,
            route_pressure_before=route_pressure_before,
        ),
        sol=sol,
        instance=instance,
        config=config,
    )


def _build_lightweight_repair_candidate(
    sol: AssignmentSolution,
    tid: int,
    position: InsertPosition,
    instance: Instance,
    config: Config,
    route_pressure_before: Dict[int, float],
) -> RepairCandidate:
    aid = int(position.agent_id)
    pos = int(position.position)
    task = instance.task_by_id(int(tid))
    agent = instance.agent_by_id(aid)
    route_before = list(int(x) for x in sol.routes.get(aid, []))
    route_after = list(route_before)
    route_after.insert(pos, int(tid))

    prev_loc, next_loc = _insertion_neighbor_locs(instance, config, route_before, pos)
    delta_distance = _distance_delta(instance, prev_loc, task.loc, next_loc)
    delta_energy = _energy_delta(config, instance, agent, prev_loc, task, next_loc)

    states_after, metrics_after = _simulate_route(instance, config, aid, route_after)
    suffix = states_after[pos:]
    suffix_min_slack = min((state.slack for state in suffix), default=float(task.tw_end) - float(task.tw_start))
    suffix_tardiness_total = sum(float(state.tardiness) for state in suffix)
    suffix_ratio = float(len(route_before) - pos + 1) / max(1.0, float(len(route_before) + 1))
    energy_remaining_ratio = (float(agent.init_energy) - float(metrics_after.energy)) / max(float(agent.init_energy), _EPS)

    depot_return_pressure = 0.0
    if bool(config.eval.include_depot_legs) and route_after:
        last_task = instance.task_by_id(int(route_after[-1]))
        depot_return_energy = _travel_energy(config, instance, agent, last_task.loc, instance.depot.loc)
        depot_return_pressure = depot_return_energy / max(
            float(agent.init_energy) - float(metrics_after.energy) + depot_return_energy,
            _EPS,
        )

    routes_after = {int(a): list(int(t) for t in route) for a, route in sol.routes.items()}
    routes_after[aid] = route_after
    pressure_after = _route_pressure_map_for_routes(routes_after, instance, config)
    route_pressure_after = float(pressure_after.get(aid, 0.0))
    balance_improvement = max(route_pressure_before.values(), default=0.0) - max(pressure_after.values(), default=0.0)

    tw_risk = 1.0 / (1.0 + max(0.0, suffix_min_slack)) + suffix_tardiness_total
    candidate_cost = float(delta_distance) + 0.1 * float(delta_energy) + float(tw_risk) + 0.1 * float(suffix_ratio)

    return RepairCandidate(
        tid=int(tid),
        agent_id=aid,
        position=pos,
        delta_distance=float(delta_distance),
        delta_energy=float(delta_energy),
        route_duration_after=float(metrics_after.duration),
        suffix_min_slack=float(suffix_min_slack),
        suffix_tardiness_total=float(suffix_tardiness_total),
        suffix_ratio=float(suffix_ratio),
        energy_remaining_ratio=float(energy_remaining_ratio),
        depot_return_pressure=float(depot_return_pressure),
        route_pressure_after=float(route_pressure_after),
        balance_improvement=float(balance_improvement),
        candidate_cost=float(candidate_cost),
        dominated=False,
        strict_feasible=False,
    )


def _strict_evaluate_repair_candidate(
    candidate: RepairCandidate,
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
) -> RepairCandidate:
    trial = sol.clone(deep=True)
    trial.add_task(int(candidate.agent_id), int(candidate.tid), position=int(candidate.position))
    ev = evaluate(trial, instance, config, update_solution_schedule=False)
    return replace(candidate, strict_feasible=bool(ev.is_feasible))


def score_repair_positions_before_strict(
    sol: AssignmentSolution,
    tid: int,
    positions: Sequence[InsertPosition],
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    route_pressure_before: Dict[int, float],
) -> List[RepairCandidate]:
    candidates = [
        _build_lightweight_repair_candidate(
            sol=sol,
            tid=int(tid),
            position=position,
            instance=instance,
            config=config,
            route_pressure_before=route_pressure_before,
        )
        for position in positions
    ]
    if not candidates:
        return []

    raw_rows: Dict[int, Dict[str, float]] = {}
    ordered_by_cost = sorted(
        enumerate(candidates),
        key=lambda item: (float(item[1].candidate_cost), int(item[1].agent_id), int(item[1].position)),
    )
    rank_by_index = {index: rank for rank, (index, _) in enumerate(ordered_by_cost)}
    denom = max(1, len(candidates) - 1)
    for index, candidate in enumerate(candidates):
        raw_rows[index] = {
            "insert_cost": float(candidate.candidate_cost),
            "future_slack": max(0.0, float(candidate.suffix_min_slack)) + float(candidate.energy_remaining_ratio),
            "route_balance_gain": float(candidate.balance_improvement),
            "local_coupling_penalty": (
                float(candidate.suffix_ratio)
                + float(candidate.suffix_tardiness_total)
                + float(candidate.depot_return_pressure)
            ),
            "diversity_gain": float(rank_by_index[index]) / float(denom),
        }

    normalized = _normalize_rows(raw_rows)
    scored: List[RepairCandidate] = []
    preferences = policy.repair_position_metric_preferences.preferences_dict()
    for index, candidate in enumerate(candidates):
        features = PositionFeatures(**normalized[index])
        position_score = score_metric_preferences(features.as_dict(), preferences)
        scored.append(replace(candidate, position_features=features, position_score=float(position_score)))
    return scored


def collect_task_repair_stats(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    budget: RepairBudget,
    strict_checks_left: int,
    route_pressure_before: Dict[int, float],
    recent_task_failures: Optional[Dict[int, Dict[str, int]]],
    stop_after_feasible: Optional[int] = None,
) -> Tuple[TaskRepairStats, int, Dict[str, int]]:
    positions = enumerate_hard_filtered_positions(sol, int(tid), instance, config)
    candidate_count = len(positions)
    strict_left = max(0, int(strict_checks_left))
    checked = 0
    candidates: List[RepairCandidate] = []
    scored_positions = score_repair_positions_before_strict(
        sol=sol,
        tid=int(tid),
        positions=positions,
        instance=instance,
        config=config,
        policy=policy,
        route_pressure_before=route_pressure_before,
    )
    ranked_positions = sorted(
        scored_positions,
        key=lambda candidate: (-float(candidate.position_score), int(candidate.agent_id), int(candidate.position)),
    )
    top_positions = ranked_positions[: max(0, int(budget.max_positions_per_task))]

    for candidate in top_positions:
        if strict_left <= 0:
            break
        strict_candidate = _strict_evaluate_repair_candidate(
            candidate,
            sol,
            instance=instance,
            config=config,
        )
        candidates.append(strict_candidate)
        strict_left -= 1
        checked += 1
        if stop_after_feasible is not None:
            feasible_seen = sum(1 for item in candidates if item.strict_feasible)
            if feasible_seen >= int(stop_after_feasible):
                break

    candidates = _mark_dominated_candidates(candidates)
    feasible = [candidate for candidate in candidates if candidate.strict_feasible]
    feasible.sort(key=lambda candidate: (-float(candidate.position_score), int(candidate.agent_id), int(candidate.position)))

    task = instance.task_by_id(int(tid))
    failures = dict((recent_task_failures or {}).get(int(tid), {}) or {})
    best_cost = min((float(candidate.candidate_cost) for candidate in feasible), default=math.inf)
    stats = TaskRepairStats(
        tid=int(tid),
        candidate_count=int(candidate_count),
        feasible_count=int(len(feasible)),
        feasible_agent_count=int(len({int(candidate.agent_id) for candidate in feasible})),
        best_cost=float(best_cost),
        sorted_feasible_candidates=tuple(feasible),
        task_priority=float(task.priority),
        time_window_width=_time_window_width(task),
        service_time=float(task.service_time),
        energy_lb=_task_energy_lb(instance, config, task),
        recent_fail_count=int(failures.get("total", 0)),
        recent_tw_fail_count=int(failures.get("time_window", 0)),
        recent_energy_fail_count=int(failures.get("energy", 0)),
        recent_skill_fail_count=int(failures.get("skill", 0)),
    )
    diagnostics = {
        "positions_generated": int(candidate_count),
        "positions_strict_checked": int(checked),
        "strict_feasible_positions": int(len(feasible)),
    }
    return stats, int(strict_left), diagnostics


def budget_from_score(score: int) -> RepairBudget:
    s = float(score) / 10.0
    return RepairBudget(
        max_tasks_considered=round(8 + s * (40 - 8)),
        max_positions_per_task=round(4 + s * (20 - 4)),
        strict_check_limit=round(40 + s * (260 - 40)),
    )


def regret_k_from_budget(score: int) -> int:
    return 3 if int(score) >= 6 else 2


def build_repair_task_feature_rows(
    stats_by_tid: Mapping[int, TaskRepairStats],
) -> Dict[int, Dict[str, float]]:
    rows: Dict[int, Dict[str, float]] = {}
    for tid, stats in stats_by_tid.items():
        feasible = list(stats.sorted_feasible_candidates)
        route_balance = _mean([candidate.route_pressure_after for candidate in feasible]) if feasible else 0.0
        best_cost = float(stats.best_cost) if math.isfinite(float(stats.best_cost)) else _BIG_M
        rows[int(tid)] = {
            "cost_pressure": best_cost,
            "scarcity_pressure": (
                1.0 / (1.0 + float(stats.feasible_count))
                + 1.0 / (1.0 + float(stats.feasible_agent_count))
                + float(stats.recent_fail_count)
            ),
            "coupling_pressure": (
                float(stats.service_time) / max(float(stats.time_window_width), _EPS)
                + float(stats.recent_tw_fail_count)
                + float(stats.recent_energy_fail_count)
                + float(stats.recent_skill_fail_count)
            ),
            "mobility_opportunity": float(stats.feasible_count) + float(stats.feasible_agent_count),
            "balance_pressure": float(route_balance),
        }
    return rows


def _score_repair_task_stats(
    stats_by_tid: Mapping[int, TaskRepairStats],
    policy: WeightedALNSPolicy,
) -> Dict[int, TaskRepairStats]:
    normalized = _normalize_rows(build_repair_task_feature_rows(stats_by_tid))
    out: Dict[int, TaskRepairStats] = {}
    for tid, stats in stats_by_tid.items():
        features = LandscapeFeatures(**normalized.get(int(tid), _ZERO_LANDSCAPE_FEATURES.as_dict()))
        task_score = score_metric_preferences(
            features.as_dict(),
            policy.repair_task_metric_preferences.preferences_dict(),
        )
        out[int(tid)] = replace(stats, landscape_features=features, task_score=float(task_score))
    return out


def _normalize_rows(rows: Mapping[int, Mapping[str, float]]) -> Dict[int, Dict[str, float]]:
    if not rows:
        return {}
    names = tuple(next(iter(rows.values())).keys())
    mins: Dict[str, float] = {}
    maxs: Dict[str, float] = {}
    for name in names:
        values = [float(row[name]) for row in rows.values()]
        mins[name] = min(values)
        maxs[name] = max(values)
    normalized: Dict[int, Dict[str, float]] = {}
    for key, row in rows.items():
        current: Dict[str, float] = {}
        for name in names:
            lo = mins[name]
            hi = maxs[name]
            current[str(name)] = 0.0 if hi - lo <= _EPS else max(0.0, min(1.0, (float(row[name]) - lo) / (hi - lo)))
        normalized[int(key)] = current
    return normalized


def _normalize_value_map(values: Mapping[int, float]) -> Dict[int, float]:
    if not values:
        return {}
    lo = min(float(value) for value in values.values())
    hi = max(float(value) for value in values.values())
    if hi - lo <= _EPS:
        return {int(key): 0.0 for key in values}
    return {int(key): max(0.0, min(1.0, (float(value) - lo) / (hi - lo))) for key, value in values.items()}


def _preview_repair_policy() -> WeightedALNSPolicy:
    return WeightedALNSPolicy(
        search_diagnosis_scores={name: 5 for name in SEARCH_DIAGNOSIS_FIELDS},
        destroy_operator_scores={name: 5 for name in DESTROY_CANDIDATE_GENERATORS},
        repair_operator_scores={name: 5 for name in REPAIR_TASK_SELECTORS},
        destroy_metric_preferences=LandscapeMetricPreferences(
            cost_pressure=MetricPreference(7, "prefer_high"),
            scarcity_pressure=MetricPreference(7, "avoid_high"),
            coupling_pressure=MetricPreference(6, "prefer_high"),
            mobility_opportunity=MetricPreference(6, "prefer_high"),
            balance_pressure=MetricPreference(5, "prefer_high"),
        ),
        repair_task_metric_preferences=LandscapeMetricPreferences(
            cost_pressure=MetricPreference(5, "prefer_high"),
            scarcity_pressure=MetricPreference(8, "prefer_high"),
            coupling_pressure=MetricPreference(6, "prefer_high"),
            mobility_opportunity=MetricPreference(4, "prefer_low"),
            balance_pressure=MetricPreference(5, "prefer_high"),
        ),
        repair_position_metric_preferences=PositionMetricPreferences(
            insert_cost=MetricPreference(8, "prefer_low"),
            future_slack=MetricPreference(7, "prefer_high"),
            route_balance_gain=MetricPreference(5, "prefer_high"),
            local_coupling_penalty=MetricPreference(5, "prefer_low"),
            diversity_gain=MetricPreference(3, "prefer_high"),
        ),
        destroy_strength_score=5,
        candidate_budget_score=10,
        exploration_score=3,
        destroy_operator_priors={name: operator_score_to_prior(5) for name in DESTROY_CANDIDATE_GENERATORS},
        repair_operator_priors={name: operator_score_to_prior(5) for name in REPAIR_TASK_SELECTORS},
        strength_ratio=0.18,
        exploration_rate=0.10,
        acceptance="sa",
        accept_level=0.25,
        reaction_factor=0.20,
        prior_mix_lambda=0.25,
    )


def build_repair_landscape(
    sol: Optional[AssignmentSolution],
    instance: Instance,
    config: Config,
    recent_repair_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if sol is None:
        return {}

    unassigned = sorted(int(tid) for tid in sol.unassigned)
    assigned_count = len(sol.all_assigned_tasks())
    candidate_counts: List[int] = []
    feasible_counts: List[int] = []

    policy = _preview_repair_policy()
    budget = RepairBudget(max_tasks_considered=max(1, len(unassigned)), max_positions_per_task=10**9, strict_check_limit=10**9)
    route_pressure_before = _route_pressure_map(sol, instance, config)
    strict_left = budget.strict_check_limit
    for tid in unassigned:
        stats, strict_left, _ = collect_task_repair_stats(
            sol=sol,
            tid=tid,
            instance=instance,
            config=config,
            policy=policy,
            budget=budget,
            strict_checks_left=strict_left,
            route_pressure_before=route_pressure_before,
            recent_task_failures=None,
            stop_after_feasible=None,
        )
        candidate_counts.append(int(stats.candidate_count))
        feasible_counts.append(int(stats.feasible_count))

    task_pressure = _task_pressure_summary(sol, instance, config)
    route_pressure = _route_pressure_summary(sol, instance, config)
    return {
        "unassigned_count": int(len(unassigned)),
        "assigned_count": int(assigned_count),
        "candidate_stats": {
            "zero_candidate_tasks": int(sum(1 for value in candidate_counts if value == 0)),
            "no_feasible_tasks": int(sum(1 for value in feasible_counts if value == 0)),
            "one_feasible_position_tasks": int(sum(1 for value in feasible_counts if value == 1)),
            "avg_candidate_positions": _mean(candidate_counts),
            "avg_feasible_positions": _mean(feasible_counts),
        },
        "task_pressure": task_pressure,
        "route_pressure": route_pressure,
        "recent_repair_feedback": dict(recent_repair_summary or {}),
    }


def repair_with_feasible_greedy(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    del rng
    return _run_repair_operator(
        operator_name="feasible_greedy_repair",
        partial=sol,
        instance=instance,
        config=config,
        policy=policy,
        choose_candidate=_choose_feasible_greedy,
    )


def repair_with_scarcity_first(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    del rng
    return _run_repair_operator(
        operator_name="scarcity_first_repair",
        partial=sol,
        instance=instance,
        config=config,
        policy=policy,
        choose_candidate=_choose_scarcity_first,
    )


def repair_with_regret_k(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    del rng
    return _run_repair_operator(
        operator_name="regret_k_repair",
        partial=sol,
        instance=instance,
        config=config,
        policy=policy,
        choose_candidate=lambda stats_by_tid: _choose_regret_k(stats_by_tid, policy.candidate_budget_score),
    )


def repair_with_bottleneck_targeted(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    del rng
    bottleneck_metric = _top_non_neutral_landscape_metric(policy)

    def choose(stats_by_tid: Dict[int, TaskRepairStats]) -> Optional[Tuple[TaskRepairStats, RepairCandidate]]:
        feasible_stats = [stats for stats in stats_by_tid.values() if stats.feasible_count > 0]
        if not feasible_stats:
            return None
        metric_values = {stats.tid: getattr(stats.landscape_features, bottleneck_metric) for stats in feasible_stats}
        normalized = _normalize_value_map(metric_values)
        stats = max(
            feasible_stats,
            key=lambda item: (float(item.task_score) + float(normalized.get(item.tid, 0.0)), -int(item.tid)),
        )
        candidate = _best_position(stats)
        return stats, candidate

    return _run_repair_operator(
        operator_name="bottleneck_targeted_repair",
        partial=sol,
        instance=instance,
        config=config,
        policy=policy,
        choose_candidate=choose,
    )


def repair_with_diversified_random(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    rng: random.Random,
) -> AssignmentSolution:
    def choose(stats_by_tid: Dict[int, TaskRepairStats]) -> Optional[Tuple[TaskRepairStats, RepairCandidate]]:
        feasible_stats = [stats for stats in stats_by_tid.values() if stats.feasible_count > 0]
        if not feasible_stats:
            return None
        stats = _sample_from_top(feasible_stats, key=lambda item: (float(item.task_score), int(item.tid)), exploration_rate=policy.exploration_rate, rng=rng)
        candidate = _sample_from_top(
            list(stats.sorted_feasible_candidates),
            key=lambda item: (float(item.position_score), -int(item.agent_id), -int(item.position)),
            exploration_rate=policy.exploration_rate,
            rng=rng,
        )
        return stats, candidate

    return _run_repair_operator(
        operator_name="diversified_random_repair",
        partial=sol,
        instance=instance,
        config=config,
        policy=policy,
        choose_candidate=choose,
    )


def _run_repair_operator(
    *,
    operator_name: str,
    partial: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: WeightedALNSPolicy,
    choose_candidate: Any,
) -> AssignmentSolution:
    budget = budget_from_score(policy.candidate_budget_score)
    out = partial.clone(deep=True)
    diagnostics = _new_diagnostics(operator_name, policy, len(out.unassigned))
    start = time.perf_counter()
    recent_failures: Optional[Dict[int, Dict[str, int]]] = None

    while out.unassigned:
        route_pressure_before = _route_pressure_map(out, instance, config)
        strict_left = int(budget.strict_check_limit)
        stats_by_tid: Dict[int, TaskRepairStats] = {}
        for tid in sorted(int(tid) for tid in out.unassigned)[: int(budget.max_tasks_considered)]:
            stats, strict_left, diag = collect_task_repair_stats(
                out,
                tid,
                instance,
                config,
                policy,
                budget,
                strict_left,
                route_pressure_before,
                recent_failures,
            )
            stats_by_tid[int(tid)] = stats
            _add_stats_diagnostics(diagnostics, stats, diag)
            if strict_left <= 0:
                break

        stats_by_tid = _score_repair_task_stats(stats_by_tid, policy)
        choice = choose_candidate(stats_by_tid)
        if choice is None:
            break
        stats, candidate = choice
        out.add_task(int(candidate.agent_id), int(stats.tid), position=int(candidate.position))
        diagnostics["inserted_count"] += 1

    _finish_diagnostics(out, diagnostics, start)
    return out


def _choose_feasible_greedy(stats_by_tid: Dict[int, TaskRepairStats]) -> Optional[Tuple[TaskRepairStats, RepairCandidate]]:
    feasible_stats = [stats for stats in stats_by_tid.values() if stats.feasible_count > 0]
    if not feasible_stats:
        return None
    stats = max(
        feasible_stats,
        key=lambda item: (
            float(_best_position(item).position_score),
            float(item.task_score),
            -int(item.tid),
        ),
    )
    return stats, _best_position(stats)


def _choose_scarcity_first(stats_by_tid: Dict[int, TaskRepairStats]) -> Optional[Tuple[TaskRepairStats, RepairCandidate]]:
    feasible_stats = [stats for stats in stats_by_tid.values() if stats.feasible_count > 0]
    if not feasible_stats:
        return None
    stats = max(
        feasible_stats,
        key=lambda item: (
            float(item.task_score) + float(item.landscape_features.scarcity_pressure),
            -int(item.tid),
        ),
    )
    return stats, _best_position(stats)


def _choose_regret_k(stats_by_tid: Dict[int, TaskRepairStats], budget_score: int) -> Optional[Tuple[TaskRepairStats, RepairCandidate]]:
    feasible_stats = [stats for stats in stats_by_tid.values() if stats.feasible_count > 0]
    if not feasible_stats:
        return None
    k = regret_k_from_budget(budget_score)
    regrets = {stats.tid: _position_score_regret(stats, k) for stats in feasible_stats}
    normalized = _normalize_value_map(regrets)
    stats = max(
        feasible_stats,
        key=lambda item: (float(item.task_score) + float(normalized.get(item.tid, 0.0)), -int(item.tid)),
    )
    return stats, _best_position(stats)


def _position_score_regret(stats: TaskRepairStats, k: int) -> float:
    scores = sorted((float(candidate.position_score) for candidate in stats.sorted_feasible_candidates), reverse=True)
    if not scores:
        return 0.0
    index = min(max(0, int(k) - 1), len(scores) - 1)
    return float(scores[0] - scores[index])


def _top_non_neutral_landscape_metric(policy: WeightedALNSPolicy) -> str:
    options = [
        (name, pref)
        for name, pref in policy.repair_task_metric_preferences.preferences_dict().items()
        if str(pref.direction) != "neutral"
    ]
    if not options:
        return "cost_pressure"
    return max(options, key=lambda item: (int(item[1].score), str(item[0])))[0]


def _sample_from_top(items: Sequence[Any], *, key: Any, exploration_rate: float, rng: random.Random) -> Any:
    ordered = sorted(items, key=key, reverse=True)
    top_n = max(1, min(len(ordered), round(1 + float(exploration_rate) * 10)))
    return ordered[rng.randrange(top_n)]


def _best_position(stats: TaskRepairStats) -> RepairCandidate:
    return max(
        stats.sorted_feasible_candidates,
        key=lambda item: (float(item.position_score), -int(item.agent_id), -int(item.position)),
    )


def _new_diagnostics(operator_name: str, policy: WeightedALNSPolicy, unassigned_before: int) -> Dict[str, Any]:
    return {
        "operator": str(operator_name),
        "candidate_budget_score": int(policy.candidate_budget_score),
        "exploration_score": int(policy.exploration_score),
        "repair_task_metric_preferences": policy.repair_task_metric_preferences.as_dict(),
        "repair_position_metric_preferences": policy.repair_position_metric_preferences.as_dict(),
        "unassigned_before": int(unassigned_before),
        "unassigned_after": int(unassigned_before),
        "inserted_count": 0,
        "failed_count": 0,
        "tasks_analyzed": 0,
        "positions_generated": 0,
        "positions_strict_checked": 0,
        "strict_feasible_positions": 0,
        "failure_breakdown": {
            "no_candidate": 0,
            "no_feasible": 0,
            "time_window": 0,
            "energy": 0,
            "skill": 0,
        },
        "time_ms": 0.0,
    }


def _add_stats_diagnostics(diagnostics: Dict[str, Any], stats: TaskRepairStats, diag: Dict[str, int]) -> None:
    diagnostics["tasks_analyzed"] += 1
    diagnostics["positions_generated"] += int(diag.get("positions_generated", 0))
    diagnostics["positions_strict_checked"] += int(diag.get("positions_strict_checked", 0))
    diagnostics["strict_feasible_positions"] += int(diag.get("strict_feasible_positions", 0))
    breakdown = diagnostics["failure_breakdown"]
    if stats.candidate_count == 0:
        breakdown["no_candidate"] += 1
    elif stats.feasible_count == 0:
        breakdown["no_feasible"] += 1


def _finish_diagnostics(sol: AssignmentSolution, diagnostics: Dict[str, Any], start: float) -> None:
    diagnostics["unassigned_after"] = int(len(sol.unassigned))
    diagnostics["failed_count"] = int(len(sol.unassigned))
    diagnostics["time_ms"] = round(1000.0 * max(0.0, time.perf_counter() - start), 4)
    sol.solver_diagnostics["last_repair"] = diagnostics


def _mark_dominated_candidates(candidates: Sequence[RepairCandidate]) -> List[RepairCandidate]:
    marked: List[RepairCandidate] = []
    for current in candidates:
        dominated = any(_dominates(other, current) for other in candidates if other is not current)
        marked.append(replace(current, dominated=bool(dominated)))
    return marked


def _dominates(lhs: RepairCandidate, rhs: RepairCandidate) -> bool:
    no_worse = (
        lhs.delta_distance <= rhs.delta_distance + _EPS
        and lhs.delta_energy <= rhs.delta_energy + _EPS
        and lhs.suffix_ratio <= rhs.suffix_ratio + _EPS
        and lhs.suffix_min_slack + _EPS >= rhs.suffix_min_slack
    )
    strictly_better = (
        lhs.delta_distance < rhs.delta_distance - _EPS
        or lhs.delta_energy < rhs.delta_energy - _EPS
        or lhs.suffix_ratio < rhs.suffix_ratio - _EPS
        or lhs.suffix_min_slack > rhs.suffix_min_slack + _EPS
    )
    return bool(no_worse and strictly_better)


def _insertion_neighbor_locs(
    instance: Instance,
    config: Config,
    route: Sequence[int],
    position: int,
) -> Tuple[Location, Optional[Location]]:
    prev_loc = instance.depot.loc if int(position) == 0 else instance.task_by_id(int(route[int(position) - 1])).loc
    if int(position) < len(route):
        next_loc: Optional[Location] = instance.task_by_id(int(route[int(position)])).loc
    elif bool(config.eval.include_depot_legs):
        next_loc = instance.depot.loc
    else:
        next_loc = None
    return prev_loc, next_loc


def _distance_delta(instance: Instance, prev_loc: Location, task_loc: Location, next_loc: Optional[Location]) -> float:
    if next_loc is not None:
        return float(instance.distance(prev_loc, task_loc)) + float(instance.distance(task_loc, next_loc)) - float(instance.distance(prev_loc, next_loc))
    return float(instance.distance(prev_loc, task_loc))


def _energy_delta(config: Config, instance: Instance, agent: Agent, prev_loc: Location, task: Task, next_loc: Optional[Location]) -> float:
    if next_loc is not None:
        return (
            _travel_energy(config, instance, agent, prev_loc, task.loc)
            + _travel_energy(config, instance, agent, task.loc, next_loc)
            - _travel_energy(config, instance, agent, prev_loc, next_loc)
            + _service_energy(agent, task)
        )
    return _travel_energy(config, instance, agent, prev_loc, task.loc) + _service_energy(agent, task)


def _simulate_route(
    instance: Instance,
    config: Config,
    aid: int,
    route: Sequence[int],
) -> Tuple[List[_RouteStop], _RouteMetrics]:
    agent = instance.agent_by_id(int(aid))
    current_loc = instance.depot.loc
    current_time = 0.0
    total_distance = 0.0
    total_energy = 0.0
    stops: List[_RouteStop] = []

    for tid in route:
        task = instance.task_by_id(int(tid))
        dist = float(instance.distance(current_loc, task.loc))
        travel_time = float(instance.travel_time(agent, current_loc, task.loc))
        total_distance += dist
        total_energy += _travel_energy(config, instance, agent, current_loc, task.loc)
        current_time += travel_time

        if current_time < float(task.tw_start):
            wait = float(task.tw_start) - current_time
            current_time += wait
            total_energy += float(agent.standby_power) * wait

        start = current_time
        end = start + float(task.service_time)
        stops.append(
            _RouteStop(
                start_time=float(start),
                end_time=float(end),
                slack=float(task.tw_end) - float(start),
                tardiness=max(0.0, float(start) - float(task.tw_end)),
            )
        )
        total_energy += _service_energy(agent, task)
        current_time = end
        current_loc = task.loc

    if bool(config.eval.include_depot_legs) and route:
        dist_back = float(instance.distance(current_loc, instance.depot.loc))
        time_back = float(instance.travel_time(agent, current_loc, instance.depot.loc))
        total_distance += dist_back
        total_energy += _travel_energy(config, instance, agent, current_loc, instance.depot.loc)
        current_time += time_back

    return stops, _RouteMetrics(
        duration=float(current_time),
        energy=float(total_energy),
        distance=float(total_distance),
        min_slack=min((stop.slack for stop in stops), default=math.inf),
    )


def _route_pressure_map(sol: AssignmentSolution, instance: Instance, config: Config) -> Dict[int, float]:
    routes = {int(aid): list(int(tid) for tid in sol.routes.get(int(aid), [])) for aid in instance.all_agent_ids()}
    return _route_pressure_map_for_routes(routes, instance, config)


def _route_pressure_map_for_routes(
    routes: Mapping[int, Sequence[int]],
    instance: Instance,
    config: Config,
) -> Dict[int, float]:
    counts = [len(routes.get(int(aid), [])) for aid in instance.all_agent_ids()]
    durations: Dict[int, float] = {}
    energies: Dict[int, float] = {}
    slacks: Dict[int, float] = {}
    for aid in instance.all_agent_ids():
        _, metrics = _simulate_route(instance, config, int(aid), list(routes.get(int(aid), [])))
        durations[int(aid)] = float(metrics.duration)
        energies[int(aid)] = float(metrics.energy)
        slacks[int(aid)] = float(metrics.min_slack)

    mean_task_count = sum(counts) / max(1, len(counts))
    mean_route_duration = sum(durations.values()) / max(1, len(durations))
    out: Dict[int, float] = {}
    for aid in instance.all_agent_ids():
        route = list(routes.get(int(aid), []))
        agent = instance.agent_by_id(int(aid))
        p_n = len(route) / max(1.0, mean_task_count)
        p_t = durations[int(aid)] / max(1.0, mean_route_duration)
        p_e = energies[int(aid)] / max(float(agent.init_energy), _EPS)
        min_slack = slacks[int(aid)]
        p_s = 0.0 if math.isinf(min_slack) else 1.0 / (1.0 + max(0.0, min_slack))
        out[int(aid)] = float((p_n + p_t + p_e + p_s) / 4.0)
    return out


def _route_pressure_summary(sol: AssignmentSolution, instance: Instance, config: Config) -> Dict[str, float]:
    pressure = _route_pressure_map(sol, instance, config)
    values = list(float(x) for x in pressure.values())
    min_energy_ratio = math.inf
    min_slack = math.inf
    for aid in instance.all_agent_ids():
        _, metrics = _simulate_route(instance, config, int(aid), list(sol.routes.get(int(aid), [])))
        agent = instance.agent_by_id(int(aid))
        min_energy_ratio = min(min_energy_ratio, (float(agent.init_energy) - float(metrics.energy)) / max(float(agent.init_energy), _EPS))
        min_slack = min(min_slack, float(metrics.min_slack))
    return {
        "max_pressure": max(values) if values else 0.0,
        "pressure_std": _std(values),
        "min_energy_ratio": 0.0 if math.isinf(min_energy_ratio) else float(min_energy_ratio),
        "min_slack": 0.0 if math.isinf(min_slack) else float(min_slack),
    }


def _task_pressure_summary(sol: AssignmentSolution, instance: Instance, config: Config) -> Dict[str, int]:
    tids = sorted(int(tid) for tid in sol.unassigned)
    if not tids:
        return {
            "high_priority_unassigned": 0,
            "tight_tw_unassigned": 0,
            "skill_scarce_unassigned": 0,
            "energy_heavy_unassigned": 0,
        }
    tasks = [instance.task_by_id(tid) for tid in tids]
    max_priority = max(float(task.priority) for task in tasks)
    widths = [_time_window_width(task) for task in tasks]
    energy_lbs = [_task_energy_lb(instance, config, task) for task in tasks]
    median_width = _median(widths)
    median_energy = _median(energy_lbs)
    scarce_limit = max(1, int(math.ceil(0.25 * len(instance.agents))))
    return {
        "high_priority_unassigned": int(sum(1 for task in tasks if float(task.priority) >= 0.75 * max_priority)),
        "tight_tw_unassigned": int(sum(1 for task in tasks if _time_window_width(task) <= median_width)),
        "skill_scarce_unassigned": int(sum(1 for task in tasks if _count_basic_feasible_agents(instance, config, task) <= scarce_limit)),
        "energy_heavy_unassigned": int(sum(1 for task in tasks if _task_energy_lb(instance, config, task) >= median_energy)),
    }


def _count_basic_feasible_agents(instance: Instance, config: Config, task: Task) -> int:
    count = 0
    for agent in instance.agents:
        if not set(task.skill_req).issubset(set(agent.skills)):
            continue
        arrival = float(instance.travel_time(agent, instance.depot.loc, task.loc))
        if max(float(task.tw_start), arrival) <= float(task.tw_end) + _EPS:
            count += 1
    return count


def _task_energy_lb(instance: Instance, config: Config, task: Task) -> float:
    best = math.inf
    for agent in instance.agents:
        if not set(task.skill_req).issubset(set(agent.skills)):
            continue
        energy = _travel_energy(config, instance, agent, instance.depot.loc, task.loc) + _service_energy(agent, task)
        if bool(config.eval.include_depot_legs):
            energy += _travel_energy(config, instance, agent, task.loc, instance.depot.loc)
        best = min(best, float(energy))
    return float(best if math.isfinite(best) else _BIG_M)


def _travel_energy(config: Config, instance: Instance, agent: Agent, a: Location, b: Location) -> float:
    if float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5:
        return float(agent.travel_energy_rate) * float(instance.travel_time(agent, a, b))
    return float(agent.travel_energy_rate) * float(instance.distance(a, b))


def _service_energy(agent: Agent, task: Task) -> float:
    return sum(float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0)) for skill in set(task.skill_req) & set(agent.skills))


def _time_window_width(task: Task) -> float:
    return max(0.0, float(task.tw_end) - float(task.tw_start))


def _mean(values: Sequence[float]) -> float:
    return float(sum(float(x) for x in values) / max(1, len(values))) if values else 0.0


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(x) for x in values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def _std(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return math.sqrt(sum((float(value) - mean) ** 2 for value in values) / max(1, len(values)))


__all__ = [
    "RepairBudget",
    "RepairCandidate",
    "TaskRepairStats",
    "budget_from_score",
    "build_repair_landscape",
    "build_repair_task_feature_rows",
    "collect_task_repair_stats",
    "compute_repair_candidate",
    "enumerate_hard_filtered_positions",
    "regret_k_from_budget",
    "repair_with_bottleneck_targeted",
    "repair_with_diversified_random",
    "repair_with_feasible_greedy",
    "repair_with_regret_k",
    "repair_with_scarcity_first",
    "score_repair_positions_before_strict",
]
