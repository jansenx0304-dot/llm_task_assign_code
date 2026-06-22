from __future__ import annotations

"""Move-level destroy operators for weighted ALNS."""

import math
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from ..config import Config
from ..constraint_checker import check_constraints
from ..models import Instance, Location
from ..solution import AssignmentSolution
from .features import enumerate_filtered_insert_positions
from .types import (
    DESTROY_OPERATOR_NAMES,
    DestroyPolicy,
    LandscapeFeatures,
)


_EPS = 1e-9
LANDSCAPE_METRIC_FIELDS = (
    "cost_pressure", "priority_loss", "scarcity_pressure", "coupling_pressure",
    "mobility_opportunity", "route_balance_pressure", "violation_pressure",
    "regret_pressure", "bottleneck_pressure",
)


@dataclass(frozen=True, slots=True)
class DestroyStrength:
    min_k: int
    target_k: int
    max_k: int


@dataclass(frozen=True, slots=True)
class DestroyMove:
    operator_name: str
    shape: str
    task_ids: Tuple[int, ...]
    affected_routes: Tuple[int, ...]
    features: LandscapeFeatures
    score: float
    metadata: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "operator_name": str(self.operator_name),
            "shape": str(self.shape),
            "task_ids": [int(tid) for tid in self.task_ids],
            "affected_routes": [int(aid) for aid in self.affected_routes],
            "features": self.features.as_dict(),
            "score": float(self.score),
            "metadata": dict(self.metadata),
        }


DestroyOperator = Callable[
    [AssignmentSolution, Instance, Config, DestroyPolicy, DestroyStrength, random.Random],
    List[DestroyMove],
]


def compute_destroy_strength(sol: AssignmentSolution, strength_ratio: float) -> DestroyStrength:
    assigned_count = len(sol.all_assigned_tasks())
    if assigned_count <= 0:
        return DestroyStrength(min_k=0, target_k=0, max_k=0)
    target_k = _clamp_int(round(float(strength_ratio) * assigned_count), 1, assigned_count)
    min_k = _clamp_int(math.floor(0.7 * target_k), 1, assigned_count)
    max_k = _clamp_int(math.ceil(1.3 * target_k), min_k, assigned_count)
    return DestroyStrength(min_k=int(min_k), target_k=int(target_k), max_k=int(max_k))


def enumerate_random_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    assigned = list(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned or strength.target_k <= 0:
        return []
    rng.shuffle(assigned)
    selected = tuple(assigned[: min(int(strength.target_k), len(assigned))])
    move = _make_move(
        operator_name="random_removal",
        shape="random",
        task_ids=selected,
        affected_routes=_affected_routes_for_tasks(sol, selected),
        metadata={"target_k": int(strength.target_k)},
    )
    return _score_moves([move], sol, instance, config, policy)


def enumerate_worst_task_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    del rng
    assigned = sorted(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned or strength.target_k <= 0:
        return []

    single_moves = [
        _make_move(
            operator_name="worst_task_removal",
            shape="task_set",
            task_ids=(int(tid),),
            affected_routes=_affected_routes_for_tasks(sol, (int(tid),)),
            metadata={"single_task_candidate": True},
        )
        for tid in assigned
    ]
    scored_single = _score_moves(single_moves, sol, instance, config, policy)
    scored_single.sort(key=lambda move: (-float(move.score), int(move.task_ids[0])))
    top_task_ids = tuple(int(move.task_ids[0]) for move in scored_single[: min(int(strength.target_k), len(scored_single))])
    if not top_task_ids:
        return []
    final = _make_move(
        operator_name="worst_task_removal",
        shape="task_set",
        task_ids=top_task_ids,
        affected_routes=_affected_routes_for_tasks(sol, top_task_ids),
        metadata={"target_k": int(strength.target_k)},
    )
    rescored = _score_moves([final] + scored_single, sol, instance, config, policy)
    return [rescored[0]]


def enumerate_related_cluster_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    del rng
    assigned = sorted(int(tid) for tid in sol.all_assigned_tasks())
    if not assigned or strength.target_k <= 0:
        return []
    if int(strength.target_k) >= len(assigned):
        move = _make_move(
            operator_name="related_cluster_removal",
            shape="cluster",
            task_ids=tuple(assigned),
            affected_routes=_affected_routes_for_tasks(sol, assigned),
            metadata={"target_k": int(strength.target_k), "seed_task": int(assigned[0])},
        )
        return _scored_moves([move], sol, instance, config, policy)

    single_moves = [
        _make_move(
            operator_name="related_cluster_removal",
            shape="cluster",
            task_ids=(int(tid),),
            affected_routes=_affected_routes_for_tasks(sol, (int(tid),)),
            metadata={"single_seed_candidate": True},
        )
        for tid in assigned
    ]
    seed_moves = _score_moves(single_moves, sol, instance, config, policy)
    seed_moves.sort(key=lambda move: (-float(move.score), int(move.task_ids[0])))
    assignment = _task_assignment_index(sol)
    distance_scale = _distance_scale(instance, assigned)
    time_scale = _time_scale(instance, assigned)

    moves: List[DestroyMove] = []
    for seed_move in seed_moves:
        seed = int(seed_move.task_ids[0])
        related = [
            (_relatedness(seed, other, sol, instance, assignment, distance_scale, time_scale), int(other))
            for other in assigned
            if int(other) != seed
        ]
        related.sort(key=lambda item: (-float(item[0]), int(item[1])))
        cluster = tuple([seed] + [int(tid) for _, tid in related[: max(0, int(strength.target_k) - 1)]])
        moves.append(
            _make_move(
                operator_name="related_cluster_removal",
                shape="cluster",
                task_ids=cluster,
                affected_routes=_affected_routes_for_tasks(sol, cluster),
                metadata={"target_k": int(strength.target_k), "seed_task": int(seed)},
            )
        )
    return _scored_moves(moves, sol, instance, config, policy)


def enumerate_critical_block_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    del rng
    if strength.min_k <= 0 or strength.max_k <= 0:
        return []
    moves: List[DestroyMove] = []
    for aid, route_raw in sol.routes.items():
        route = [int(tid) for tid in route_raw]
        if not route:
            continue
        for length in range(int(strength.min_k), min(int(strength.max_k), len(route)) + 1):
            for start in range(0, len(route) - length + 1):
                end = start + length
                block = tuple(route[start:end])
                moves.append(
                    _make_move(
                        operator_name="critical_block_removal",
                        shape="block",
                        task_ids=block,
                        affected_routes=(int(aid),),
                        metadata={
                            "route_id": int(aid),
                            "start": int(start),
                            "length": int(length),
                            "end_exclusive": int(end),
                            "is_tail": bool(end == len(route)),
                        },
                    )
                )
    return _scored_moves(moves, sol, instance, config, policy)


def enumerate_route_rebalance_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    del rng
    moves: List[DestroyMove] = []
    for aid, route_raw in sol.routes.items():
        route = tuple(int(tid) for tid in route_raw)
        route_len = len(route)
        if route_len <= 0 or route_len < int(strength.min_k) or route_len > int(strength.max_k):
            continue
        moves.append(
            _make_move(
                operator_name="route_rebalance_removal",
                shape="route",
                task_ids=route,
                affected_routes=(int(aid),),
                metadata={
                    "route_id": int(aid),
                    "route_len": int(route_len),
                    "route_cost": float(route_cost(instance, config, int(aid), route)),
                },
            )
        )
    return _scored_moves(moves, sol, instance, config, policy)


def enumerate_violation_removal(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
    strength: DestroyStrength,
    rng: random.Random,
) -> List[DestroyMove]:
    del rng
    report, _ = check_constraints(sol, instance, config, update_solution_schedule=False)
    contributions = []
    for tid_s, values in report.violation_by_task.items():
        total = sum(float(value) for value in dict(values).values())
        if total > _EPS:
            contributions.append((total, int(tid_s)))
    contributions.sort(key=lambda item: (-float(item[0]), int(item[1])))
    if not contributions or strength.target_k <= 0:
        return []
    selected = tuple(tid for _, tid in contributions[: min(int(strength.target_k), len(contributions))])
    move = _make_move(
        operator_name="violation_removal",
        shape="violation_task_set",
        task_ids=selected,
        affected_routes=_affected_routes_for_tasks(sol, selected),
        metadata={"target_k": int(strength.target_k), "source": "constraint_report.violation_by_task"},
    )
    return _score_moves([move], sol, instance, config, policy)


DESTROY_OPERATORS: Dict[str, DestroyOperator] = {
    "random_removal": enumerate_random_removal,
    "worst_task_removal": enumerate_worst_task_removal,
    "related_cluster_removal": enumerate_related_cluster_removal,
    "critical_block_removal": enumerate_critical_block_removal,
    "route_rebalance_removal": enumerate_route_rebalance_removal,
}


def build_destroy_landscape(
    sol: Optional[AssignmentSolution],
    instance: Instance,
    config: Config,
    *,
    strength_ratio: float = 0.15,
    recent_destroy_summary: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if sol is None:
        return {}

    strength = compute_destroy_strength(sol, strength_ratio)
    route_lengths = [len(route) for route in sol.routes.values() if route]
    route_costs = [
        float(route_cost(instance, config, int(aid), [int(tid) for tid in route]))
        for aid, route in sol.routes.items()
        if route
    ]
    policy = DestroyPolicy(
        operator_weights={name: 5 for name in DESTROY_OPERATOR_NAMES},
        signal_weights={
            "cost_pressure": 7,
            "coupling_pressure": 6,
            "route_balance_pressure": 5,
            "mobility_opportunity": 5,
            "scarcity_protection": 7,
        },
        intensity_score=5,
        remove_ratio=float(strength_ratio),
    )
    rng = random.Random(0)
    candidate_landscape: Dict[str, Any] = {}
    for name in (
        "worst_task_removal",
        "related_cluster_removal",
        "critical_block_removal",
        "route_rebalance_removal",
    ):
        moves = DESTROY_OPERATORS[name](sol, instance, config, policy, strength, rng)
        moves.sort(key=lambda move: -float(move.score))
        top = moves[0] if moves else None
        candidate_landscape[name] = {
            "available": bool(top is not None),
            "candidate_count_preview": int(len(moves)),
            "top_pattern": "none" if top is None else _top_pattern(top.features),
            "top_feature_levels": {} if top is None else _feature_levels(top.features),
        }

    return {
        "solution_policy": "feasible_solution_only",
        "destroy_operators": list(DESTROY_OPERATOR_NAMES),
        "destroy_signal_fields": list(policy.signal_weights),
        "strength_preview": {
            "assigned_count": int(len(sol.all_assigned_tasks())),
            "target_k_at_current_strength": int(strength.target_k),
            "min_k": int(strength.min_k),
            "max_k": int(strength.max_k),
        },
        "route_structure": {
            "nonempty_route_count": int(len(route_lengths)),
            "route_len_min": int(min(route_lengths)) if route_lengths else 0,
            "route_len_mean": _round(sum(route_lengths) / max(1, len(route_lengths))) if route_lengths else 0.0,
            "route_len_max": int(max(route_lengths)) if route_lengths else 0,
            "route_cost_imbalance_level": _cv_level(route_costs),
            "route_load_imbalance_level": _cv_level([float(x) for x in route_lengths]),
        },
        "candidate_move_landscape": candidate_landscape,
        "recent_destroy_feedback": _compact_recent_destroy_feedback(recent_destroy_summary or {}),
    }


def route_cost(instance: Instance, config: Config, aid: int, route: Sequence[int]) -> float:
    if not route:
        return 0.0
    agent = instance.agent_by_id(int(aid))
    total = 0.0
    prev_loc = instance.depot.loc
    for tid in route:
        task = instance.task_by_id(int(tid))
        total += _arc_cost(instance, config, agent.id, prev_loc, task.loc)
        prev_loc = task.loc
    if bool(config.eval.include_depot_legs):
        total += _arc_cost(instance, config, agent.id, prev_loc, instance.depot.loc)
    return float(total)


def _arc_cost(instance: Instance, config: Config, aid: int, loc_a: Location, loc_b: Location) -> float:
    agent = instance.agent_by_id(int(aid))
    travel_distance = float(instance.distance(loc_a, loc_b))
    travel_time = float(instance.travel_time(agent, loc_a, loc_b))
    if float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5:
        travel_energy = float(agent.travel_energy_rate) * travel_time
    else:
        travel_energy = float(agent.travel_energy_rate) * travel_distance
    return travel_distance + travel_time + travel_energy


def _scored_moves(
    moves: Sequence[DestroyMove],
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
) -> List[DestroyMove]:
    scored = _score_moves(moves, sol, instance, config, policy)
    scored.sort(key=lambda move: (-float(move.score), tuple(int(tid) for tid in move.task_ids)))
    return scored


def _score_moves(
    moves: Sequence[DestroyMove],
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    policy: DestroyPolicy,
) -> List[DestroyMove]:
    if not moves:
        return []
    raw_rows = _compute_raw_move_feature_rows(moves, sol, instance, config)
    normalized = _normalize_rows(raw_rows)
    out: List[DestroyMove] = []
    for index, move in enumerate(moves):
        features = LandscapeFeatures(**normalized[index])  # type: ignore[arg-type]
        out.append(
            DestroyMove(
                operator_name=move.operator_name,
                shape=move.shape,
                task_ids=tuple(int(tid) for tid in move.task_ids),
                affected_routes=tuple(int(aid) for aid in move.affected_routes),
                features=features,
                score=(
                    policy.signal_weights.get("cost_pressure", 0) * features.cost_pressure
                    + policy.signal_weights.get("coupling_pressure", 0) * features.coupling_pressure
                    + policy.signal_weights.get("route_balance_pressure", 0) * features.route_balance_pressure
                    + policy.signal_weights.get("mobility_opportunity", 0) * features.mobility_opportunity
                    - policy.signal_weights.get("scarcity_protection", 0) * features.scarcity_pressure
                ),
                metadata=dict(move.metadata),
            )
        )
    return out


def _compute_raw_move_feature_rows(
    moves: Sequence[DestroyMove],
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
) -> Dict[int, Dict[str, float]]:
    assigned = sorted(int(tid) for tid in sol.all_assigned_tasks())
    assignment = _task_assignment_index(sol)
    distance_scale = _distance_scale(instance, assigned)
    time_scale = _time_scale(instance, assigned)
    route_pressure = _route_pressure_by_aid(sol, instance, config)
    relocation_cache: Dict[int, float] = {}
    rows: Dict[int, Dict[str, float]] = {}
    for index, move in enumerate(moves):
        rows[index] = {
            "cost_pressure": _group_removal_cost_release(sol, instance, config, move.task_ids),
            "priority_loss": sum(float(instance.task_by_id(int(tid)).priority) for tid in move.task_ids),
            "mobility_opportunity": _move_mobility_opportunity(sol, instance, config, move.task_ids, assignment, relocation_cache),
            "coupling_pressure": _coupling_pressure(move, sol, instance, assignment, distance_scale, time_scale),
            "scarcity_pressure": _scarcity_pressure(sol, instance, config, move.task_ids, assignment, relocation_cache),
            "route_balance_pressure": _move_balance_pressure(move, route_pressure),
            "violation_pressure": 0.0,
            "regret_pressure": 0.0,
            "bottleneck_pressure": 0.0,
        }
    return rows


def _group_removal_cost_release(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    move_task_ids: Sequence[int],
) -> float:
    remove_set = {int(tid) for tid in move_task_ids}
    total_release = 0.0
    for aid, route_raw in sol.routes.items():
        route = [int(tid) for tid in route_raw]
        if not route or not any(tid in remove_set for tid in route):
            continue
        new_route = [int(tid) for tid in route if int(tid) not in remove_set]
        release = route_cost(instance, config, int(aid), route) - route_cost(instance, config, int(aid), new_route)
        total_release += float(release)
    return max(0.0, float(total_release))


def _move_mobility_opportunity(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    task_ids: Sequence[int],
    assignment: Mapping[int, Tuple[int, int]],
    cache: Dict[int, float],
) -> float:
    values = [
        _task_mobility_opportunity(sol, instance, config, int(tid), assignment, cache)
        for tid in task_ids
    ]
    return sum(values) / max(1, len(values))


def _task_mobility_opportunity(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    tid: int,
    assignment: Mapping[int, Tuple[int, int]],
    cache: Dict[int, float],
) -> float:
    if int(tid) in cache:
        return float(cache[int(tid)])
    if int(tid) not in assignment:
        cache[int(tid)] = 0.0
        return 0.0
    aid, _ = assignment[int(tid)]
    old_route = [int(x) for x in sol.routes.get(int(aid), [])]
    route_without_tid = [int(x) for x in old_route if int(x) != int(tid)]
    current_single_cost = route_cost(instance, config, int(aid), old_route) - route_cost(instance, config, int(aid), route_without_tid)

    tmp_sol = sol.clone(deep=True)
    tmp_sol.remove_task(int(aid), int(tid), to_unassigned=True)
    positions = enumerate_filtered_insert_positions(tmp_sol, int(tid), instance, config)
    if not positions:
        cache[int(tid)] = 0.0
        return 0.0

    best_delta: Optional[float] = None
    for position in positions:
        candidate_aid = int(position.agent_id)
        candidate_route = [int(x) for x in tmp_sol.routes.get(candidate_aid, [])]
        old_cost = route_cost(instance, config, candidate_aid, candidate_route)
        new_route = list(candidate_route)
        new_route.insert(int(position.position), int(tid))
        insert_delta = route_cost(instance, config, candidate_aid, new_route) - old_cost
        if best_delta is None or insert_delta < best_delta:
            best_delta = float(insert_delta)

    value = max(0.0, float(current_single_cost) - float(best_delta if best_delta is not None else 0.0))
    cache[int(tid)] = value
    return value


def _coupling_pressure(
    move: DestroyMove,
    sol: AssignmentSolution,
    instance: Instance,
    assignment: Mapping[int, Tuple[int, int]],
    distance_scale: float,
    time_scale: float,
) -> float:
    tids = [int(tid) for tid in move.task_ids]
    if len(tids) <= 1:
        return 0.0
    pairs = list(_pairs(tids))
    spatial = sum(_spatial_similarity(instance, a, b, distance_scale) for a, b in pairs) / max(1, len(pairs))
    tw = sum(_time_window_similarity(instance, a, b, time_scale) for a, b in pairs) / max(1, len(pairs))
    skill = sum(_skill_similarity(instance, a, b) for a, b in pairs) / max(1, len(pairs))
    if move.shape in ("block", "route"):
        route_structure = 1.0
    elif move.shape == "cluster":
        route_structure = sum(1.0 for a, b in pairs if _same_route(assignment, a, b)) / max(1, len(pairs))
    else:
        route_structure = 0.0
    return (float(spatial) + float(tw) + float(skill) + float(route_structure)) / 4.0


def _scarcity_pressure(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    task_ids: Sequence[int],
    assignment: Mapping[int, Tuple[int, int]],
    relocation_cache: Dict[int, float],
) -> float:
    values: List[float] = []
    for tid in task_ids:
        task = instance.task_by_id(int(tid))
        mobility = _task_mobility_opportunity(sol, instance, config, int(tid), assignment, relocation_cache)
        values.append(float(task.priority) + 1.0 / (1.0 + float(mobility)))
    return sum(values) / max(1, len(values))


def _route_pressure_by_aid(sol: AssignmentSolution, instance: Instance, config: Config) -> Dict[int, float]:
    entries: List[Tuple[int, float, int]] = []
    for aid, route_raw in sol.routes.items():
        route = [int(tid) for tid in route_raw]
        if route:
            entries.append((int(aid), route_cost(instance, config, int(aid), route), len(route)))
    if not entries:
        return {}
    mean_cost = sum(cost for _, cost, _ in entries) / max(1, len(entries))
    mean_len = sum(length for _, _, length in entries) / max(1, len(entries))
    out: Dict[int, float] = {}
    for aid, cost, length in entries:
        cost_pressure = max(0.0, float(cost) - mean_cost) / max(_EPS, mean_cost)
        load_pressure = max(0.0, float(length) - mean_len) / max(1.0, mean_len)
        out[int(aid)] = float(cost_pressure) + float(load_pressure)
    return out


def _move_balance_pressure(move: DestroyMove, route_pressure: Mapping[int, float]) -> float:
    if move.shape != "route" or not move.affected_routes:
        return 0.0
    return float(route_pressure.get(int(move.affected_routes[0]), 0.0))


def _relatedness(
    seed: int,
    other: int,
    sol: AssignmentSolution,
    instance: Instance,
    assignment: Mapping[int, Tuple[int, int]],
    distance_scale: float,
    time_scale: float,
) -> float:
    del sol
    same_route = 1.0 if _same_route(assignment, int(seed), int(other)) else 0.0
    return (
        _spatial_similarity(instance, int(seed), int(other), distance_scale)
        + _time_window_similarity(instance, int(seed), int(other), time_scale)
        + _skill_similarity(instance, int(seed), int(other))
        + same_route
    ) / 4.0


def _spatial_similarity(instance: Instance, a: int, b: int, distance_scale: float) -> float:
    task_a = instance.task_by_id(int(a))
    task_b = instance.task_by_id(int(b))
    d = float(instance.distance(task_a.loc, task_b.loc))
    return 1.0 / (1.0 + d / max(_EPS, float(distance_scale)))


def _time_window_similarity(instance: Instance, a: int, b: int, time_scale: float) -> float:
    task_a = instance.task_by_id(int(a))
    task_b = instance.task_by_id(int(b))
    mid_a = 0.5 * (float(task_a.tw_start) + float(task_a.tw_end))
    mid_b = 0.5 * (float(task_b.tw_start) + float(task_b.tw_end))
    dt = abs(mid_a - mid_b)
    return 1.0 / (1.0 + dt / max(_EPS, float(time_scale)))


def _skill_similarity(instance: Instance, a: int, b: int) -> float:
    set_a = set(instance.task_by_id(int(a)).skill_req)
    set_b = set(instance.task_by_id(int(b)).skill_req)
    union = set_a | set_b
    if not union:
        return 1.0
    return float(len(set_a & set_b)) / float(len(union))


def _same_route(assignment: Mapping[int, Tuple[int, int]], a: int, b: int) -> bool:
    return int(a) in assignment and int(b) in assignment and int(assignment[int(a)][0]) == int(assignment[int(b)][0])


def _distance_scale(instance: Instance, assigned: Sequence[int]) -> float:
    values = [
        float(instance.distance(instance.task_by_id(int(a)).loc, instance.task_by_id(int(b)).loc))
        for a, b in _pairs([int(tid) for tid in assigned])
    ]
    return _positive_median_or_one(values)


def _time_scale(instance: Instance, assigned: Sequence[int]) -> float:
    values = [
        max(0.0, float(instance.task_by_id(int(tid)).tw_end) - float(instance.task_by_id(int(tid)).tw_start))
        for tid in assigned
    ]
    return _positive_median_or_one(values)


def _positive_median_or_one(values: Sequence[float]) -> float:
    clean = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not clean:
        return 1.0
    mid = len(clean) // 2
    if len(clean) % 2:
        value = clean[mid]
    else:
        value = 0.5 * (clean[mid - 1] + clean[mid])
    return float(value) if value > _EPS else 1.0


def _normalize_rows(rows: Mapping[int, Mapping[str, float]]) -> Dict[int, Dict[str, float]]:
    if not rows:
        return {}
    mins: Dict[str, float] = {}
    maxs: Dict[str, float] = {}
    for name in LANDSCAPE_METRIC_FIELDS:
        values = [float(row[name]) for row in rows.values()]
        mins[name] = min(values)
        maxs[name] = max(values)
    normalized: Dict[int, Dict[str, float]] = {}
    for key, row in rows.items():
        current: Dict[str, float] = {}
        for name in LANDSCAPE_METRIC_FIELDS:
            lo = mins[name]
            hi = maxs[name]
            current[name] = 0.0 if hi - lo <= _EPS else max(0.0, min(1.0, (float(row[name]) - lo) / (hi - lo)))
        normalized[int(key)] = current
    return normalized


def _make_move(
    *,
    operator_name: str,
    shape: str,
    task_ids: Sequence[int],
    affected_routes: Sequence[int],
    metadata: Mapping[str, Any],
) -> DestroyMove:
    return DestroyMove(
        operator_name=str(operator_name),
        shape=str(shape),
        task_ids=tuple(int(tid) for tid in task_ids),
        affected_routes=tuple(int(aid) for aid in affected_routes),
        features=_zero_features(),
        score=0.0,
        metadata=dict(metadata),
    )


def _zero_features() -> LandscapeFeatures:
    return LandscapeFeatures(
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


def _task_assignment_index(sol: AssignmentSolution) -> Dict[int, Tuple[int, int]]:
    out: Dict[int, Tuple[int, int]] = {}
    for aid, route in sol.routes.items():
        for pos, tid in enumerate(route):
            out[int(tid)] = (int(aid), int(pos))
    return out


def _affected_routes_for_tasks(sol: AssignmentSolution, task_ids: Iterable[int]) -> Tuple[int, ...]:
    wanted = {int(tid) for tid in task_ids}
    routes: List[int] = []
    for aid, route in sol.routes.items():
        if any(int(tid) in wanted for tid in route):
            routes.append(int(aid))
    return tuple(sorted(routes))


def _pairs(values: Sequence[int]) -> Iterable[Tuple[int, int]]:
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            yield int(values[i]), int(values[j])


def _feature_levels(features: LandscapeFeatures) -> Dict[str, str]:
    return {name: _normalized_level(float(getattr(features, name))) for name in LANDSCAPE_METRIC_FIELDS}


def _top_pattern(features: LandscapeFeatures) -> str:
    levels = _feature_levels(features)
    if (
        levels["cost_pressure"] == "high"
        and levels["mobility_opportunity"] == "high"
        and levels["scarcity_pressure"] == "low"
    ):
        return "high-cost mobile structures with low scarcity risk"
    if levels["route_balance_pressure"] == "high":
        return "high route-balance pressure candidates"
    if levels["coupling_pressure"] == "high":
        return "strongly coupled local structures"
    return "mixed destroy candidates"


def _normalized_level(value: float) -> str:
    if float(value) < 0.33:
        return "low"
    if float(value) < 0.67:
        return "medium"
    return "high"


def _cv_level(values: Sequence[float]) -> str:
    if not values:
        return "low"
    mean = sum(float(x) for x in values) / max(1, len(values))
    if abs(mean) <= _EPS:
        cv = 0.0
    else:
        variance = sum((float(x) - mean) ** 2 for x in values) / max(1, len(values))
        cv = math.sqrt(max(0.0, variance)) / abs(mean)
    if cv < 0.15:
        return "low"
    if cv < 0.35:
        return "medium"
    return "high"


def _compact_recent_destroy_feedback(summary: Mapping[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name in DESTROY_OPERATOR_NAMES:
        raw = summary.get(name)
        if not isinstance(raw, Mapping):
            continue
        out[name] = {
            "used": int(raw.get("used", 0) or 0),
            "accepted": int(raw.get("accepted", 0) or 0),
            "best_improved": int(raw.get("best_improved", 0) or 0),
            "mean_removed_count": _round(float(raw.get("mean_removed_count", 0.0) or 0.0)),
        }
    return out


def _round(value: float) -> float:
    return round(float(value), 4)


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(int(lo), min(int(hi), int(value)))
