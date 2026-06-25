from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..config import Config
from ..evaluator import evaluate
from ..models import Agent, Instance, Location, Task
from ..solution import AssignmentSolution
from .features import basic_insertion_feasibility_filter, insertion_lower_bound_filter
from .types import (
    InsertionPolicy,
    LandscapeFeatures,
    PositionFeatures,
    InsertPosition,
)

_EPS = 1e-9
_BIG_M = 1e12
REGRET_K = 2
_ZERO_LANDSCAPE_FEATURES = LandscapeFeatures(
    cost_pressure=0.0,
    priority_loss=0.0,
    scarcity_pressure=0.0,
    coupling_pressure=0.0,
    mobility_opportunity=0.0,
    route_balance_pressure=0.0,
    violation_pressure=0.0,
    regret_pressure=0.0,
    bottleneck_pressure=0.0,
)
_ZERO_POSITION_FEATURES = PositionFeatures(
    insert_cost=0.0,
    future_slack=0.0,
    route_balance_gain=0.0,
    local_coupling_penalty=0.0,
    diversity_gain=0.0,
    violation_delta=0.0,
)


@dataclass(frozen=True, slots=True)
class InsertionContext:
    kind: str
    feasibility_mode: str = "strict"
    target_task_ids: Tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {"initial", "alns"}:
            raise ValueError(f"invalid insertion context kind: {self.kind}")
        if self.feasibility_mode not in {
            "strict",
            "relaxed_recoverable",
            "recovery_only",
        }:
            raise ValueError(
                f"invalid insertion feasibility mode: {self.feasibility_mode}"
            )


@dataclass(slots=True)
class TaskInsertionAttempt:
    task_id: int
    candidate_positions: int
    hard_feasible_positions: int
    evaluated_positions: int
    inserted: bool
    failure_reasons: Dict[str, int]
    chosen_agent_id: Optional[int] = None
    chosen_position: Optional[int] = None


@dataclass(slots=True)
class InsertionTrace:
    attempts: List[TaskInsertionAttempt]


@dataclass(frozen=True)
class InsertionCandidate:
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
    relaxed_admissible: bool = False
    quality_delta: Dict[str, float] = field(default_factory=dict)
    constraint_delta: Dict[str, float] = field(default_factory=dict)
    position_features: PositionFeatures = _ZERO_POSITION_FEATURES
    position_score: float = 0.0

    @property
    def task_id(self) -> str:
        return str(self.tid)


@dataclass(frozen=True)
class TaskInsertionStats:
    tid: int
    candidate_count: int
    feasible_count: int
    feasible_agent_count: int
    best_cost: float
    sorted_feasible_candidates: Tuple[InsertionCandidate, ...]
    sorted_relaxed_candidates: Tuple[InsertionCandidate, ...]
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
    positions = basic_insertion_feasibility_filter(
        sol, tid, instance, config, candidate_positions=None
    )
    if not positions:
        return []
    return insertion_lower_bound_filter(
        sol, tid, instance, config, candidate_positions=positions
    )


def compute_insertion_candidate(
    sol: AssignmentSolution,
    tid: int,
    position: InsertPosition,
    instance: Instance,
    config: Config,
    route_pressure_before: Dict[int, float],
) -> InsertionCandidate:
    return _strict_evaluate_insertion_candidate(
        _build_lightweight_insertion_candidate(
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


def _build_lightweight_insertion_candidate(
    sol: AssignmentSolution,
    tid: int,
    position: InsertPosition,
    instance: Instance,
    config: Config,
    route_pressure_before: Dict[int, float],
) -> InsertionCandidate:
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
    suffix_min_slack = min(
        (state.slack for state in suffix),
        default=float(task.tw_end) - float(task.tw_start),
    )
    suffix_tardiness_total = sum(float(state.tardiness) for state in suffix)
    suffix_ratio = float(len(route_before) - pos + 1) / max(
        1.0, float(len(route_before) + 1)
    )
    energy_remaining_ratio = (
        float(agent.init_energy) - float(metrics_after.energy)
    ) / max(float(agent.init_energy), _EPS)

    depot_return_pressure = 0.0
    if bool(config.eval.include_depot_legs) and route_after:
        last_task = instance.task_by_id(int(route_after[-1]))
        depot_return_energy = _travel_energy(
            config, instance, agent, last_task.loc, instance.depot.loc
        )
        depot_return_pressure = depot_return_energy / max(
            float(agent.init_energy)
            - float(metrics_after.energy)
            + depot_return_energy,
            _EPS,
        )

    routes_after = {
        int(a): list(int(t) for t in route) for a, route in sol.routes.items()
    }
    routes_after[aid] = route_after
    pressure_after = _route_pressure_map_for_routes(routes_after, instance, config)
    route_pressure_after = float(pressure_after.get(aid, 0.0))
    balance_improvement = max(route_pressure_before.values(), default=0.0) - max(
        pressure_after.values(), default=0.0
    )

    tw_risk = 1.0 / (1.0 + max(0.0, suffix_min_slack)) + suffix_tardiness_total
    candidate_cost = (
        float(delta_distance)
        + 0.1 * float(delta_energy)
        + float(tw_risk)
        + 0.1 * float(suffix_ratio)
    )

    return InsertionCandidate(
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


def _strict_evaluate_insertion_candidate(
    candidate: InsertionCandidate,
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
) -> InsertionCandidate:
    trial = sol.clone(deep=True)
    trial.add_task(
        int(candidate.agent_id), int(candidate.tid), position=int(candidate.position)
    )
    ev = evaluate(trial, instance, config, update_solution_schedule=False)
    report = ev.constraint_report
    relaxed = bool(
        report.violation_capability <= _EPS
        and report.unrecoverable_violation_total <= _EPS
        and report.violation_total > _EPS
    )
    return replace(
        candidate,
        strict_feasible=bool(ev.is_feasible),
        relaxed_admissible=relaxed,
        quality_delta=dict(ev.quality_metrics),
        constraint_delta={
            "violation_total": float(report.violation_total),
            "violation_capability": float(report.violation_capability),
            "violation_time_window": float(report.violation_time_window),
            "violation_energy": float(report.violation_energy),
        },
    )


def score_insert_positions(
    sol: AssignmentSolution,
    tid: int,
    positions: Sequence[InsertPosition],
    instance: Instance,
    config: Config,
    policy: InsertionPolicy,
    route_pressure_before: Dict[int, float],
) -> List[InsertionCandidate]:
    candidates = [
        _build_lightweight_insertion_candidate(
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
        key=lambda item: (
            float(item[1].candidate_cost),
            int(item[1].agent_id),
            int(item[1].position),
        ),
    )
    rank_by_index = {index: rank for rank, (index, _) in enumerate(ordered_by_cost)}
    denom = max(1, len(candidates) - 1)
    for index, candidate in enumerate(candidates):
        raw_rows[index] = {
            "insert_cost": float(candidate.candidate_cost),
            "future_slack": max(0.0, float(candidate.suffix_min_slack))
            + float(candidate.energy_remaining_ratio),
            "route_balance_gain": float(candidate.balance_improvement),
            "local_coupling_penalty": (
                float(candidate.suffix_ratio)
                + float(candidate.suffix_tardiness_total)
                + float(candidate.depot_return_pressure)
            ),
            "diversity_gain": float(rank_by_index[index]) / float(denom),
            "violation_delta": 0.0,
        }

    normalized = _normalize_rows(raw_rows)
    scored: List[InsertionCandidate] = []
    for index, candidate in enumerate(candidates):
        features = PositionFeatures(**normalized[index])
        weights = policy.position_signal_weights
        position_score = (
            -weights.get("insert_cost", 0) * features.insert_cost
            + weights.get("future_slack", 0) * features.future_slack
            + weights.get("route_balance_gain", 0) * features.route_balance_gain
            - weights.get("local_coupling_penalty", 0) * features.local_coupling_penalty
            + weights.get("diversity_gain", 0) * features.diversity_gain
        )
        scored.append(
            replace(
                candidate,
                position_features=features,
                position_score=float(position_score),
            )
        )
    return scored


def collect_task_insertion_stats(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    policy: InsertionPolicy,
    route_pressure_before: Dict[int, float],
    recent_task_failures: Optional[Dict[int, Dict[str, int]]],
) -> Tuple[TaskInsertionStats, Dict[str, int]]:
    positions = enumerate_hard_filtered_positions(sol, int(tid), instance, config)
    candidate_count = len(positions)
    checked = 0
    candidates: List[InsertionCandidate] = []
    scored_positions = score_insert_positions(
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
        key=lambda candidate: (
            -float(candidate.position_score),
            int(candidate.agent_id),
            int(candidate.position),
        ),
    )

    for candidate in ranked_positions:
        strict_candidate = _strict_evaluate_insertion_candidate(
            candidate,
            sol,
            instance=instance,
            config=config,
        )
        candidates.append(strict_candidate)
        checked += 1

    candidates = _mark_dominated_candidates(candidates)
    feasible = [candidate for candidate in candidates if candidate.strict_feasible]
    relaxed = [
        candidate
        for candidate in candidates
        if candidate.strict_feasible or candidate.relaxed_admissible
    ]
    feasible.sort(
        key=lambda candidate: (
            -float(candidate.position_score),
            int(candidate.agent_id),
            int(candidate.position),
        )
    )
    relaxed.sort(
        key=lambda candidate: (
            0 if candidate.strict_feasible else 1,
            float(
                candidate.constraint_delta.get("violation_total", 0.0)
                if candidate.constraint_delta
                else 0.0
            ),
            -float(candidate.position_score),
            int(candidate.agent_id),
            int(candidate.position),
        )
    )

    task = instance.task_by_id(int(tid))
    failures = dict((recent_task_failures or {}).get(int(tid), {}) or {})
    best_cost = min(
        (float(candidate.candidate_cost) for candidate in feasible), default=math.inf
    )
    stats = TaskInsertionStats(
        tid=int(tid),
        candidate_count=int(candidate_count),
        feasible_count=int(len(feasible)),
        feasible_agent_count=int(
            len({int(candidate.agent_id) for candidate in feasible})
        ),
        best_cost=float(best_cost),
        sorted_feasible_candidates=tuple(feasible),
        sorted_relaxed_candidates=tuple(relaxed),
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
    return stats, diagnostics


def score_candidate_tasks(
    stats_by_tid: Mapping[int, TaskInsertionStats],
) -> Dict[int, Dict[str, float]]:
    rows: Dict[int, Dict[str, float]] = {}
    for tid, stats in stats_by_tid.items():
        feasible = list(stats.sorted_feasible_candidates)
        route_balance = (
            _mean([candidate.route_pressure_after for candidate in feasible])
            if feasible
            else 0.0
        )
        best_cost = (
            float(stats.best_cost) if math.isfinite(float(stats.best_cost)) else _BIG_M
        )
        rows[int(tid)] = {
            "cost_pressure": best_cost,
            "priority_loss": float(stats.task_priority),
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
            "mobility_opportunity": float(stats.feasible_count)
            + float(stats.feasible_agent_count),
            "route_balance_pressure": float(route_balance),
            "violation_pressure": float(
                stats.recent_tw_fail_count + stats.recent_energy_fail_count
            ),
            "regret_pressure": 0.0,
            "bottleneck_pressure": 1.0 / (1.0 + float(stats.feasible_agent_count)),
        }
    return rows


def _score_candidate_task_stats(
    stats_by_tid: Mapping[int, TaskInsertionStats],
    policy: InsertionPolicy,
) -> Dict[int, TaskInsertionStats]:
    normalized = _normalize_rows(score_candidate_tasks(stats_by_tid))
    out: Dict[int, TaskInsertionStats] = {}
    for tid, stats in stats_by_tid.items():
        features = LandscapeFeatures(
            **normalized.get(int(tid), _ZERO_LANDSCAPE_FEATURES.as_dict())
        )
        weights = policy.task_signal_weights
        task_score = (
            weights.get("priority_loss", 0) * features.priority_loss
            + weights.get("scarcity_pressure", 0) * features.scarcity_pressure
            + weights.get("regret_pressure", 0) * features.regret_pressure
            + weights.get("bottleneck_pressure", 0) * features.bottleneck_pressure
            + weights.get("mobility_opportunity", 0) * features.mobility_opportunity
        )
        out[int(tid)] = replace(
            stats, landscape_features=features, task_score=float(task_score)
        )
    return out


def _normalize_rows(
    rows: Mapping[int, Mapping[str, float]],
) -> Dict[int, Dict[str, float]]:
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
            current[str(name)] = (
                0.0
                if hi - lo <= _EPS
                else max(0.0, min(1.0, (float(row[name]) - lo) / (hi - lo)))
            )
        normalized[int(key)] = current
    return normalized


def _normalize_value_map(values: Mapping[int, float]) -> Dict[int, float]:
    if not values:
        return {}
    lo = min(float(value) for value in values.values())
    hi = max(float(value) for value in values.values())
    if hi - lo <= _EPS:
        return {int(key): 0.0 for key in values}
    return {
        int(key): max(0.0, min(1.0, (float(value) - lo) / (hi - lo)))
        for key, value in values.items()
    }


def _default_insertion_policy() -> InsertionPolicy:
    return InsertionPolicy(
        operator_weights={
            "greedy_insertion": 6,
            "scarcity_first_insertion": 8,
            "regret_insertion": 6,
            "bottleneck_insertion": 4,
            "diversified_insertion": 2,
        },
        task_signal_weights={
            "priority_loss": 8,
            "scarcity_pressure": 8,
            "regret_pressure": 5,
            "bottleneck_pressure": 4,
            "mobility_opportunity": 2,
        },
        position_signal_weights={
            "insert_cost": 8,
            "future_slack": 7,
            "route_balance_gain": 5,
            "local_coupling_penalty": 5,
            "diversity_gain": 2,
        },
    )


def build_insertion_landscape(
    sol: Optional[AssignmentSolution],
    instance: Instance,
    config: Config,
    recent_insertion_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if sol is None:
        return {}
    unassigned = sorted(int(tid) for tid in sol.unassigned)
    policy = _default_insertion_policy()
    candidate_counts: List[int] = []
    feasible_counts: List[int] = []
    task_stats: Dict[int, TaskInsertionStats] = {}
    route_pressure_before = _route_pressure_map(sol, instance, config)
    for tid in unassigned:
        stats, _ = collect_task_insertion_stats(
            sol,
            tid,
            instance,
            config,
            policy,
            route_pressure_before,
            None,
        )
        candidate_counts.append(stats.candidate_count)
        feasible_counts.append(stats.feasible_count)
        task_stats[int(tid)] = stats
    scarce_capability_threshold = max(1, int(math.ceil(0.25 * len(instance.agents))))
    scarce_position_threshold = 1
    scarce_ids = [
        tid
        for tid in unassigned
        if _count_basic_feasible_agents(instance, config, instance.task_by_id(tid))
        <= scarce_capability_threshold
        or task_stats[tid].feasible_count <= scarce_position_threshold
    ]

    def bucket(task_ids: Sequence[int]) -> Dict[str, Any]:
        ordered = sorted(
            (int(tid) for tid in task_ids),
            key=lambda tid: (-float(instance.task_by_id(tid).priority), tid),
        )
        return {
            "task_ids": ordered,
            "task_count": len(task_ids),
            "priority_mass": float(
                sum(instance.task_by_id(int(tid)).priority for tid in task_ids)
            ),
            "top_tasks": [
                {
                    "task_id": tid,
                    "priority": float(instance.task_by_id(tid).priority),
                    "capable_agents": _count_basic_feasible_agents(
                        instance, config, instance.task_by_id(tid)
                    ),
                    "candidate_positions": int(task_stats[tid].candidate_count),
                    "feasible_positions": int(task_stats[tid].feasible_count),
                    "dominant_reason": (
                        "no_candidate_position"
                        if task_stats[tid].candidate_count == 0
                        else (
                            "no_feasible_position"
                            if task_stats[tid].feasible_count == 0
                            else "limited_insertion_options"
                        )
                    ),
                }
                for tid in ordered[:5]
            ],
        }

    return {
        "unassigned_count": len(unassigned),
        "assigned_count": len(sol.all_assigned_tasks()),
        "candidate_stats": {
            "zero_candidate_tasks": sum(value == 0 for value in candidate_counts),
            "no_feasible_tasks": sum(value == 0 for value in feasible_counts),
            "one_feasible_position_tasks": sum(value == 1 for value in feasible_counts),
            "avg_candidate_positions": _mean(candidate_counts),
            "avg_feasible_positions": _mean(feasible_counts),
            "candidate_position_percentiles": {
                "p25": _percentile(candidate_counts, 0.25),
                "p50": _percentile(candidate_counts, 0.50),
                "p75": _percentile(candidate_counts, 0.75),
            },
            "feasible_position_percentiles": {
                "p25": _percentile(feasible_counts, 0.25),
                "p50": _percentile(feasible_counts, 0.50),
                "p75": _percentile(feasible_counts, 0.75),
            },
        },
        "target_buckets": {
            "unassigned_priority": bucket(unassigned),
            "insertion_scarce_unassigned": bucket(scarce_ids),
        },
        "task_pressure": _task_pressure_summary(sol, instance, config),
        "route_pressure": _route_pressure_summary(sol, instance, config),
        "recent_insertion_feedback": dict(recent_insertion_summary or {}),
    }


def run_insertion_kernel(
    partial_solution: AssignmentSolution,
    candidate_tasks: Sequence[int],
    insertion_policy: InsertionPolicy,
    context: InsertionContext,
    *,
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> AssignmentSolution:
    out = partial_solution.clone(deep=True)
    pending = {
        int(tid) for tid in candidate_tasks if int(tid) not in out.all_assigned_tasks()
    }
    out.unassigned.update(pending)
    out.normalize(instance)
    diagnostics = _new_insertion_diagnostics(context, insertion_policy, len(pending))
    latest_attempts: Dict[int, TaskInsertionAttempt] = {}
    started_at = time.perf_counter()

    while pending:
        route_pressure_before = _route_pressure_map(out, instance, config)
        stats_by_tid: Dict[int, TaskInsertionStats] = {}
        ordered_tasks = sorted(pending)
        for tid in ordered_tasks:
            stats, diag = collect_task_insertion_stats(
                out,
                tid,
                instance,
                config,
                insertion_policy,
                route_pressure_before,
                None,
            )
            stats_by_tid[tid] = stats
            latest_attempts[int(tid)] = TaskInsertionAttempt(
                task_id=int(tid),
                candidate_positions=int(stats.candidate_count),
                hard_feasible_positions=int(stats.feasible_count),
                evaluated_positions=int(diag.get("positions_strict_checked", 0) or 0),
                inserted=False,
                failure_reasons=_failure_reasons(stats),
            )
            _add_stats_diagnostics(diagnostics, stats, diag)

        stats_by_tid = _score_candidate_task_stats(stats_by_tid, insertion_policy)
        operator_name = _weighted_choice(insertion_policy.operator_weights, rng)
        choice = _choose_for_context(
            operator_name,
            stats_by_tid,
            insertion_policy,
            context,
            out,
            instance,
            config,
            rng,
        )
        if choice is None:
            break
        stats, candidate = choice
        out.add_task(candidate.agent_id, stats.tid, position=candidate.position)
        latest_attempts[int(stats.tid)] = TaskInsertionAttempt(
            task_id=int(stats.tid),
            candidate_positions=int(stats.candidate_count),
            hard_feasible_positions=int(stats.feasible_count),
            evaluated_positions=int(
                len(stats.sorted_feasible_candidates)
                + len(stats.sorted_relaxed_candidates)
            ),
            inserted=True,
            failure_reasons={},
            chosen_agent_id=int(candidate.agent_id),
            chosen_position=int(candidate.position),
        )
        pending.discard(stats.tid)
        diagnostics["inserted_count"] += 1
        diagnostics["operator_use"][operator_name] = (
            diagnostics["operator_use"].get(operator_name, 0) + 1
        )
        diagnostics["operator"] = operator_name

    diagnostics["unassigned_after"] = len(out.unassigned)
    diagnostics["failed_count"] = len(pending)
    diagnostics["top_failed_tasks"] = _top_failed_attempts(latest_attempts, instance)
    diagnostics["time_ms"] = round((time.perf_counter() - started_at) * 1000.0, 4)
    out.solver_diagnostics = dict(out.solver_diagnostics or {})
    out.solver_diagnostics["last_insertion"] = diagnostics
    out.normalize(instance)
    return out


def _choose_for_context(
    operator_name: str,
    stats_by_tid: Dict[int, TaskInsertionStats],
    policy: InsertionPolicy,
    context: InsertionContext,
    current: AssignmentSolution,
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> Optional[Tuple[TaskInsertionStats, InsertionCandidate]]:
    available: Dict[int, Tuple[InsertionCandidate, ...]] = {}
    current_violation = float(
        evaluate(
            current, instance, config, update_solution_schedule=False
        ).constraint_report.violation_total
    )
    for tid, stats in stats_by_tid.items():
        candidates = stats.sorted_feasible_candidates
        if context.feasibility_mode != "strict" and not candidates:
            candidates = stats.sorted_relaxed_candidates
        if context.feasibility_mode == "recovery_only":
            candidates = tuple(
                candidate
                for candidate in stats.sorted_relaxed_candidates
                if float(candidate.constraint_delta.get("violation_total", math.inf))
                < current_violation - _EPS
            )
        if candidates:
            available[tid] = candidates
    if not available:
        return None

    eligible = [stats_by_tid[tid] for tid in available]
    targeted = [
        item for item in eligible if int(item.tid) in set(context.target_task_ids)
    ]
    if targeted:
        eligible = targeted
    if operator_name == "regret_insertion":
        regrets = {
            stats.tid: _candidate_regret(available[stats.tid], REGRET_K)
            for stats in eligible
        }
        normalized = _normalize_value_map(regrets)
        stats = max(
            eligible,
            key=lambda item: (
                item.task_score + normalized.get(item.tid, 0.0),
                -item.tid,
            ),
        )
    elif operator_name == "scarcity_first_insertion":
        stats = max(
            eligible,
            key=lambda item: (
                item.task_score + item.landscape_features.scarcity_pressure,
                -item.tid,
            ),
        )
    elif operator_name == "bottleneck_insertion":
        top_signal = max(
            policy.task_signal_weights,
            key=lambda name: (policy.task_signal_weights[name], name),
        )
        stats = max(
            eligible,
            key=lambda item: (
                item.task_score + getattr(item.landscape_features, top_signal),
                -item.tid,
            ),
        )
    elif operator_name == "diversified_insertion":
        stats = _sample_rank_weighted(
            eligible, key=lambda item: (item.task_score, -item.tid), rng=rng
        )
    else:
        stats = max(
            eligible,
            key=lambda item: (
                max(candidate.position_score for candidate in available[item.tid]),
                item.task_score,
                -item.tid,
            ),
        )

    positions = list(available[stats.tid])
    if operator_name == "diversified_insertion":
        candidate = _sample_rank_weighted(
            positions,
            key=lambda item: (item.position_score, -item.agent_id, -item.position),
            rng=rng,
        )
    else:
        candidate = max(
            positions,
            key=lambda item: (item.position_score, -item.agent_id, -item.position),
        )
    return stats, candidate


def _candidate_regret(candidates: Sequence[InsertionCandidate], k: int) -> float:
    scores = sorted(
        (candidate.position_score for candidate in candidates), reverse=True
    )
    if not scores:
        return 0.0
    return scores[0] - scores[min(k - 1, len(scores) - 1)]


def _weighted_choice(weights: Dict[str, int], rng: random.Random) -> str:
    positive = [(name, max(0, int(weight))) for name, weight in weights.items()]
    total = sum(weight for _, weight in positive)
    if total <= 0:
        return sorted(weights)[0]
    target = rng.uniform(0.0, total)
    running = 0.0
    for name, weight in positive:
        running += weight
        if target <= running:
            return name
    return positive[-1][0]


def _sample_rank_weighted(
    items: Sequence[Any], *, key: Any, rng: random.Random, alpha: float = 0.75
) -> Any:
    ordered = sorted(items, key=key, reverse=True)
    if not ordered:
        raise ValueError("cannot sample from empty items")
    weights = [1.0 / ((rank + 1) ** float(alpha)) for rank in range(len(ordered))]
    total = sum(weights)
    threshold = rng.random() * total
    acc = 0.0
    for item, weight in zip(ordered, weights):
        acc += weight
        if acc >= threshold:
            return item
    return ordered[-1]


def _new_insertion_diagnostics(
    context: InsertionContext, policy: InsertionPolicy, unassigned_before: int
) -> Dict[str, Any]:
    return {
        "context": context.kind,
        "feasibility_mode": context.feasibility_mode,
        "target_task_ids": [int(tid) for tid in context.target_task_ids],
        "operator_weights": dict(policy.operator_weights),
        "task_signal_weights": dict(policy.task_signal_weights),
        "position_signal_weights": dict(policy.position_signal_weights),
        "operator_use": {},
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
        "top_failed_tasks": [],
        "time_ms": 0.0,
    }


def _add_stats_diagnostics(
    diagnostics: Dict[str, Any], stats: TaskInsertionStats, diag: Dict[str, int]
) -> None:
    diagnostics["tasks_analyzed"] += 1
    diagnostics["positions_generated"] += int(diag.get("positions_generated", 0))
    diagnostics["positions_strict_checked"] += int(
        diag.get("positions_strict_checked", 0)
    )
    diagnostics["strict_feasible_positions"] += int(
        diag.get("strict_feasible_positions", 0)
    )
    breakdown = diagnostics["failure_breakdown"]
    if stats.candidate_count == 0:
        breakdown["no_candidate"] += 1
    elif stats.feasible_count == 0:
        breakdown["no_feasible"] += 1


def _failure_reasons(stats: TaskInsertionStats) -> Dict[str, int]:
    if stats.candidate_count == 0:
        return {"no_candidate_position": 1}
    if stats.feasible_count == 0:
        return {"no_feasible_position": 1}
    return {}


def _top_failed_attempts(
    attempts: Dict[int, TaskInsertionAttempt], instance: Instance, limit: int = 5
) -> List[Dict[str, Any]]:
    failed = [attempt for attempt in attempts.values() if not attempt.inserted]
    failed.sort(key=lambda item: (-sum(item.failure_reasons.values()), item.task_id))
    out: List[Dict[str, Any]] = []
    for attempt in failed[:limit]:
        task = instance.task_by_id(int(attempt.task_id))
        reasons = dict(attempt.failure_reasons)
        dominant = (
            max(reasons.items(), key=lambda item: int(item[1]))[0]
            if reasons
            else "none"
        )
        out.append(
            {
                "task_id": int(attempt.task_id),
                "priority": float(task.priority),
                "capable_agents": sum(
                    1
                    for agent in instance.agents
                    if set(task.skill_req).issubset(agent.skills)
                ),
                "candidate_positions": int(attempt.candidate_positions),
                "hard_feasible_positions": int(attempt.hard_feasible_positions),
                "hard_filter_rejections": reasons,
                "dominant_reason": dominant,
            }
        )
    return out


def _mark_dominated_candidates(
    candidates: Sequence[InsertionCandidate],
) -> List[InsertionCandidate]:
    marked: List[InsertionCandidate] = []
    for current in candidates:
        dominated = any(
            _dominates(other, current) for other in candidates if other is not current
        )
        marked.append(replace(current, dominated=bool(dominated)))
    return marked


def _dominates(lhs: InsertionCandidate, rhs: InsertionCandidate) -> bool:
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
    prev_loc = (
        instance.depot.loc
        if int(position) == 0
        else instance.task_by_id(int(route[int(position) - 1])).loc
    )
    if int(position) < len(route):
        next_loc: Optional[Location] = instance.task_by_id(
            int(route[int(position)])
        ).loc
    elif bool(config.eval.include_depot_legs):
        next_loc = instance.depot.loc
    else:
        next_loc = None
    return prev_loc, next_loc


def _distance_delta(
    instance: Instance,
    prev_loc: Location,
    task_loc: Location,
    next_loc: Optional[Location],
) -> float:
    if next_loc is not None:
        return (
            float(instance.distance(prev_loc, task_loc))
            + float(instance.distance(task_loc, next_loc))
            - float(instance.distance(prev_loc, next_loc))
        )
    return float(instance.distance(prev_loc, task_loc))


def _energy_delta(
    config: Config,
    instance: Instance,
    agent: Agent,
    prev_loc: Location,
    task: Task,
    next_loc: Optional[Location],
) -> float:
    if next_loc is not None:
        return (
            _travel_energy(config, instance, agent, prev_loc, task.loc)
            + _travel_energy(config, instance, agent, task.loc, next_loc)
            - _travel_energy(config, instance, agent, prev_loc, next_loc)
            + _service_energy(agent, task)
        )
    return _travel_energy(
        config, instance, agent, prev_loc, task.loc
    ) + _service_energy(agent, task)


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
        total_energy += _travel_energy(
            config, instance, agent, current_loc, instance.depot.loc
        )
        current_time += time_back

    return stops, _RouteMetrics(
        duration=float(current_time),
        energy=float(total_energy),
        distance=float(total_distance),
        min_slack=min((stop.slack for stop in stops), default=math.inf),
    )


def _route_pressure_map(
    sol: AssignmentSolution, instance: Instance, config: Config
) -> Dict[int, float]:
    routes = {
        int(aid): list(int(tid) for tid in sol.routes.get(int(aid), []))
        for aid in instance.all_agent_ids()
    }
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
        _, metrics = _simulate_route(
            instance, config, int(aid), list(routes.get(int(aid), []))
        )
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


def _route_pressure_summary(
    sol: AssignmentSolution, instance: Instance, config: Config
) -> Dict[str, float]:
    pressure = _route_pressure_map(sol, instance, config)
    values = list(float(x) for x in pressure.values())
    min_energy_ratio = math.inf
    min_slack = math.inf
    for aid in instance.all_agent_ids():
        _, metrics = _simulate_route(
            instance, config, int(aid), list(sol.routes.get(int(aid), []))
        )
        agent = instance.agent_by_id(int(aid))
        min_energy_ratio = min(
            min_energy_ratio,
            (float(agent.init_energy) - float(metrics.energy))
            / max(float(agent.init_energy), _EPS),
        )
        min_slack = min(min_slack, float(metrics.min_slack))
    return {
        "max_pressure": max(values) if values else 0.0,
        "pressure_std": _std(values),
        "min_energy_ratio": (
            0.0 if math.isinf(min_energy_ratio) else float(min_energy_ratio)
        ),
        "min_slack": 0.0 if math.isinf(min_slack) else float(min_slack),
    }


def _task_pressure_summary(
    sol: AssignmentSolution, instance: Instance, config: Config
) -> Dict[str, int]:
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
        "high_priority_unassigned": int(
            sum(1 for task in tasks if float(task.priority) >= 0.75 * max_priority)
        ),
        "tight_tw_unassigned": int(
            sum(1 for task in tasks if _time_window_width(task) <= median_width)
        ),
        "skill_scarce_unassigned": int(
            sum(
                1
                for task in tasks
                if _count_basic_feasible_agents(instance, config, task) <= scarce_limit
            )
        ),
        "energy_heavy_unassigned": int(
            sum(
                1
                for task in tasks
                if _task_energy_lb(instance, config, task) >= median_energy
            )
        ),
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
        energy = _travel_energy(
            config, instance, agent, instance.depot.loc, task.loc
        ) + _service_energy(agent, task)
        if bool(config.eval.include_depot_legs):
            energy += _travel_energy(
                config, instance, agent, task.loc, instance.depot.loc
            )
        best = min(best, float(energy))
    return float(best if math.isfinite(best) else _BIG_M)


def _travel_energy(
    config: Config, instance: Instance, agent: Agent, a: Location, b: Location
) -> float:
    if float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5:
        return float(agent.travel_energy_rate) * float(
            instance.travel_time(agent, a, b)
        )
    return float(agent.travel_energy_rate) * float(instance.distance(a, b))


def _service_energy(agent: Agent, task: Task) -> float:
    return sum(
        float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0))
        for skill in set(task.skill_req) & set(agent.skills)
    )


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


def _percentile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    position = max(0.0, min(1.0, float(q))) * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _std(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return math.sqrt(
        sum((float(value) - mean) ** 2 for value in values) / max(1, len(values))
    )


__all__ = [
    "InsertionContext",
    "TaskInsertionAttempt",
    "InsertionTrace",
    "InsertionCandidate",
    "TaskInsertionStats",
    "build_insertion_landscape",
    "score_candidate_tasks",
    "collect_task_insertion_stats",
    "compute_insertion_candidate",
    "enumerate_hard_filtered_positions",
    "run_insertion_kernel",
    "score_insert_positions",
]
