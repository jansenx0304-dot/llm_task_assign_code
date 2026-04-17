from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Sequence

from ..config import Config
from ..console import success
from ..evaluator import compare, evaluate
from ..models import Agent, Instance, Task
from ..operators import InsertPosition, score_insert_candidate_features, score_reinsert_task_features
from ..operators.features import (
    compute_insert_candidate_features_batch,
    compute_reinsert_task_features_batch,
)
from ..solution import AssignmentSolution, EvalResult


WEIGHTED_INSERT_METHOD = "weighted_insert"


@dataclass(frozen=True, slots=True)
class _ScoredTask:
    tid: int
    task_score: float


@dataclass(frozen=True, slots=True)
class _ScoredPosition:
    position: InsertPosition
    insert_score: float


@dataclass(frozen=True, slots=True)
class _StrictFeasibleMove:
    aid: int
    tid: int
    pos: int
    insert_score: float
    ev: EvalResult


@dataclass(slots=True)
class _InitBuildStats:
    attempted_tasks: int = 0
    successful_insertions: int = 0
    strict_position_evals: int = 0
    feasible_position_hits: int = 0


def build_initial_solution(
    method: str,
    instance: Instance,
    config: Config,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Build the weighted-insert initial solution."""
    rng = random.Random(rng_seed)
    safe_method = _sanitize_init_method(method or getattr(config.init, "method", None))
    if safe_method != WEIGHTED_INSERT_METHOD:
        raise ValueError(f"Unknown init method: {safe_method}")
    return build_weighted_insert(instance, config, rng)


def build_weighted_insert(instance: Instance, config: Config, rng: random.Random) -> AssignmentSolution:
    """Lightweight repair-style construction from the empty solution."""
    sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    stats = _InitBuildStats()

    while sol.unassigned:
        scored_tasks = _rank_unassigned_tasks(sol, instance, config)
        if not scored_tasks:
            break

        inserted_this_round = False
        for task_candidate in _task_attempt_order(scored_tasks, config, rng):
            stats.attempted_tasks += 1
            move = _find_best_task_insertion(sol, int(task_candidate.tid), instance, config, stats)
            if move is None:
                continue

            sol.add_task(int(move.aid), int(move.tid), position=int(move.pos))
            stats.successful_insertions += 1
            inserted_this_round = True
            break

        if not inserted_this_round:
            break

    sol.normalize(instance)
    ev = evaluate(sol, instance, config, update_solution_schedule=True)
    assigned = len(sol.all_assigned_tasks())
    success(
        f"init_solution_ready method={WEIGHTED_INSERT_METHOD} "
        f"assigned={assigned} "
        f"unassigned={len(sol.unassigned)} "
        f"attempted_tasks={stats.attempted_tasks} "
        f"successful_insertions={stats.successful_insertions} "
        f"strict_position_evals={stats.strict_position_evals} "
        f"feasible_position_hits={stats.feasible_position_hits} "
        f"lex_key={list(ev.lex_key or ())}"
    )
    return sol


def _rank_unassigned_tasks(sol: AssignmentSolution, instance: Instance, config: Config) -> List[_ScoredTask]:
    task_ids = list(int(tid) for tid in sol.unassigned)
    if not task_ids:
        return []

    weighted = config.solver.weighted_alns
    feature_map = compute_reinsert_task_features_batch(sol, task_ids, instance, config)
    scored = [
        _ScoredTask(
            tid=int(tid),
            task_score=score_reinsert_task_features(feature_map[int(tid)], weighted.reinsert_metric_weights),
        )
        for tid in task_ids
    ]
    scored.sort(key=lambda item: (-float(item.task_score), int(item.tid)))
    return scored


def _task_attempt_order(scored_tasks: Sequence[_ScoredTask], config: Config, rng: random.Random) -> List[_ScoredTask]:
    if not scored_tasks:
        return []

    task_top_k = _coerce_positive_int(getattr(config.init, "task_top_k", 1), default=1)
    prefix = list(scored_tasks[: min(task_top_k, len(scored_tasks))])
    if len(prefix) <= 1 or not bool(getattr(config.init, "randomized", False)):
        return prefix

    randomized_prefix_len = min(len(prefix), _coerce_positive_int(getattr(config.init, "rcl_k", 1), default=1))
    if randomized_prefix_len <= 1:
        return prefix

    chosen = prefix[rng.randrange(randomized_prefix_len)]
    return [chosen] + [candidate for candidate in prefix if candidate.tid != chosen.tid]


def _find_best_task_insertion(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
    stats: _InitBuildStats,
) -> Optional[_StrictFeasibleMove]:
    scored_positions = _rank_insert_positions(sol, tid, instance, config)
    if not scored_positions:
        return None

    position_top_k = _coerce_positive_int(getattr(config.init, "position_top_k", 1), default=1)
    strict_candidates = scored_positions[: min(position_top_k, len(scored_positions))]

    best_move: Optional[_StrictFeasibleMove] = None
    for candidate in strict_candidates:
        stats.strict_position_evals += 1
        trial = make_trial_insert(
            sol,
            int(candidate.position.agent_id),
            int(tid),
            int(candidate.position.position),
        )
        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)
        if not ev_trial.is_feasible:
            continue

        stats.feasible_position_hits += 1
        move = _StrictFeasibleMove(
            aid=int(candidate.position.agent_id),
            tid=int(tid),
            pos=int(candidate.position.position),
            insert_score=float(candidate.insert_score),
            ev=ev_trial,
        )
        if _is_better_move(move, best_move, config):
            best_move = move

    return best_move


def _rank_insert_positions(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
    config: Config,
) -> List[_ScoredPosition]:
    task = instance.task_by_id(int(tid))
    positions = _enumerate_all_insert_positions(sol, task, instance)
    if not positions:
        return []

    weighted = config.solver.weighted_alns
    feature_map = compute_insert_candidate_features_batch(sol, tid, positions, instance, config)
    scored = [
        _ScoredPosition(
            position=position,
            insert_score=score_insert_candidate_features(feature_map[position], weighted.insert_metric_weights),
        )
        for position in positions
    ]
    scored.sort(
        key=lambda item: (
            float(item.insert_score),
            int(item.position.agent_id),
            int(item.position.position),
        )
    )
    return scored


def _enumerate_all_insert_positions(
    sol: AssignmentSolution,
    task: Task,
    instance: Instance,
) -> List[InsertPosition]:
    positions: List[InsertPosition] = []
    for agent in instance.agents:
        if not can_do(agent, task):
            continue
        route_len = len(sol.routes.get(int(agent.id), []))
        for pos in range(route_len + 1):
            positions.append(InsertPosition(agent_id=int(agent.id), position=int(pos)))
    return positions


def _is_better_move(
    candidate: _StrictFeasibleMove,
    incumbent: Optional[_StrictFeasibleMove],
    config: Config,
) -> bool:
    if incumbent is None:
        return True

    cmp = compare(candidate.ev, incumbent.ev, config)
    if cmp < 0:
        return True
    if cmp > 0:
        return False
    if float(candidate.insert_score) < float(incumbent.insert_score) - 1e-12:
        return True
    if abs(float(candidate.insert_score) - float(incumbent.insert_score)) <= 1e-12:
        return (int(candidate.aid), int(candidate.pos), int(candidate.tid)) < (
            int(incumbent.aid),
            int(incumbent.pos),
            int(incumbent.tid),
        )
    return False


def make_trial_insert(sol: AssignmentSolution, aid: int, tid: int, pos: int) -> AssignmentSolution:
    """Clone only the touched mutable state before testing an insertion."""
    trial = sol.clone(deep=False)
    trial.routes = dict(getattr(trial, "routes", {}))
    trial.routes[aid] = list(sol.routes.get(aid, []))

    if hasattr(trial, "unassigned"):
        trial.unassigned = set(getattr(sol, "unassigned", set()))
    if hasattr(trial, "schedule"):
        trial.schedule = dict(getattr(sol, "schedule", {}))

    trial.add_task(aid, tid, position=pos)
    return trial


def can_do(agent: Agent, task: Task) -> bool:
    """Return whether the agent covers all required task skills."""
    return task.skill_req.issubset(agent.skills)


def _coerce_positive_int(value: object, default: int) -> int:
    try:
        numeric = int(value)
    except Exception:
        numeric = int(default)
    return max(1, numeric)


def _sanitize_init_method(value: object) -> str:
    method = str(value or WEIGHTED_INSERT_METHOD).strip().lower()
    if method in {WEIGHTED_INSERT_METHOD, "insert", "sweep"}:
        return WEIGHTED_INSERT_METHOD
    return WEIGHTED_INSERT_METHOD
