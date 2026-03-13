# sar_alloc/tools/init_solutions.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from ..config import Config
from ..console import success
from ..evaluator import compare, evaluate
from ..models import Agent, Instance, Task
from ..solution import AssignmentSolution


def build_initial_solution(
    method: str,
    instance: Instance,
    config: Config,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Build an initial solution with a supported construction heuristic."""
    rng = random.Random(rng_seed)
    chosen = method or getattr(config.init, "method", None)

    if chosen == "insert":
        return build_insert(instance, config, rng)

    if chosen == "sweep":
        return build_sweep(instance, config, rng)

    raise ValueError(f"Unknown init method: {chosen}")


def build_insert(instance: Instance, config: Config, rng: random.Random) -> AssignmentSolution:
    """Greedy insertion with optional randomized restricted candidate list."""
    sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    for aid in instance.all_agent_ids():
        sol.routes.setdefault(aid, [])

    tasks = list(instance.tasks)
    tasks.sort(
        key=lambda t: (
            float(t.tw_end),
            float(t.tw_end) - float(t.tw_start),
            float(t.service_time),
            int(t.id),
        )
    )

    agents = list(instance.agents)
    if bool(config.init.randomized):
        rng.shuffle(agents)

    rcl_k = max(1, int(getattr(config.init, "rcl_k", 1)))
    use_rcl = bool(config.init.randomized) and rcl_k > 1

    assigned = 0
    for task in tasks:
        candidate_agents = [a for a in agents if can_do(a, task)]
        if not candidate_agents:
            continue

        feasible_moves: List[Move] = []
        for agent in candidate_agents:
            aid = agent.id
            route_len = len(sol.routes.get(aid, []))
            for pos in positions_to_try(route_len):
                trial = make_trial_insert(sol, aid, task.id, pos)
                ev = evaluate(trial, instance, config, update_solution_schedule=False)
                if not ev.is_feasible:
                    continue
                feasible_moves.append(Move(aid=aid, tid=task.id, pos=pos, ev=ev))

        if not feasible_moves:
            continue

        chosen = select_move(feasible_moves, config, rng, rcl_k if use_rcl else 1)
        sol.add_task(chosen.aid, chosen.tid, position=chosen.pos)
        assigned += 1

    evaluate(sol, instance, config, update_solution_schedule=True)
    success(
        f"Initial solution ready: method=insert, assigned={assigned}, "
        f"unassigned={len(instance.tasks) - assigned}"
    )
    return sol


def build_sweep(instance: Instance, config: Config, rng: random.Random) -> AssignmentSolution:
    """Angular sweep over tasks, inserting feasible tasks into each agent route."""
    sol = AssignmentSolution.empty_from_instance(instance, put_all_unassigned=True)
    for aid in instance.all_agent_ids():
        sol.routes.setdefault(aid, [])

    depot = instance.depot.loc
    task_ids = [t.id for t in instance.tasks]
    task_ids.sort(key=lambda tid: polar_angle(depot, instance.task_by_id(tid).loc))

    agents = list(instance.agents)
    if bool(config.init.randomized):
        rng.shuffle(agents)

    remaining = set(task_ids)
    rcl_k = max(1, int(getattr(config.init, "rcl_k", 1)))
    use_rcl = bool(config.init.randomized) and rcl_k > 1

    assigned = 0
    for agent in agents:
        aid = agent.id
        sol.routes.setdefault(aid, [])

        for tid in task_ids:
            if tid not in remaining:
                continue

            task = instance.task_by_id(tid)
            if not can_do(agent, task):
                continue

            route_len = len(sol.routes[aid])
            feasible_moves: List[Move] = []
            for pos in positions_to_try(route_len):
                trial = make_trial_insert(sol, aid, tid, pos)
                ev = evaluate(trial, instance, config, update_solution_schedule=False)
                if not ev.is_feasible:
                    continue
                feasible_moves.append(Move(aid=aid, tid=tid, pos=pos, ev=ev))

            if not feasible_moves:
                continue

            chosen = select_move(feasible_moves, config, rng, rcl_k if use_rcl else 1)
            sol.add_task(chosen.aid, chosen.tid, position=chosen.pos)
            remaining.remove(tid)
            assigned += 1

    if hasattr(sol, "unassigned"):
        sol.unassigned = set(remaining)

    evaluate(sol, instance, config, update_solution_schedule=True)
    success(
        f"Initial solution ready: method=sweep, assigned={assigned}, "
        f"unassigned={len(remaining)}"
    )
    return sol


@dataclass(frozen=True, slots=True)
class Move:
    aid: int
    tid: int
    pos: int
    ev: object


def select_move(moves: List[Move], config: Config, rng: random.Random, rcl_k: int) -> Move:
    """Pick the best move, or sample from the top-k when randomized construction is enabled."""
    moves_sorted = sorted(moves, key=CmpKey(config))
    k = max(1, min(int(rcl_k), len(moves_sorted)))
    if k == 1:
        return moves_sorted[0]
    return rng.choice(moves_sorted[:k])


class CmpKey:
    __slots__ = ("config",)

    def __init__(self, config: Config):
        self.config = config

    def __call__(self, cand: Move) -> "ComparableEval":
        return ComparableEval(cand.ev, self.config)


class ComparableEval:
    __slots__ = ("ev", "config")

    def __init__(self, ev: object, config: Config):
        self.ev = ev
        self.config = config

    def __lt__(self, other: "ComparableEval") -> bool:
        return compare(self.ev, other.ev, self.config) < 0


def positions_to_try(route_len: int) -> Iterable[int]:
    """Try a small fixed set of insertion positions: tail, head, and middle."""
    if route_len <= 0:
        return (0,)

    mid = route_len // 2
    seen = set()
    out = []
    for p in (route_len, 0, mid):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return tuple(out)


def make_trial_insert(sol: AssignmentSolution, aid: int, tid: int, pos: int) -> AssignmentSolution:
    """Clone only the touched route and mutable state before testing an insertion."""
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


def polar_angle(center: Tuple[float, float], loc: Tuple[float, float]) -> float:
    """Compute the angle from center to loc in [0, 2*pi)."""
    dx = loc[0] - center[0]
    dy = loc[1] - center[1]
    ang = math.atan2(dy, dx)
    return ang + 2.0 * math.pi if ang < 0 else ang
