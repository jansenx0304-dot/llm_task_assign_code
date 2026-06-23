from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Dict, List, Tuple

from .config import Config
from .models import Agent, Instance, Task
from .solution import AssignmentSolution

_EPS = 1e-9


@dataclass(frozen=True)
class ConstraintReport:
    is_feasible: bool
    violation_total: float
    violation_capability: float
    violation_time_window: float
    violation_energy: float
    recoverable_violation_total: float
    unrecoverable_violation_total: float
    violation_by_type: Dict[str, float] = field(default_factory=dict)
    violation_by_task: Dict[str, Dict[str, float]] = field(default_factory=dict)
    violation_by_route: Dict[str, Dict[str, float]] = field(default_factory=dict)
    violation_ratio_by_type: Dict[str, float] = field(default_factory=dict)
    violation_details_by_type: Dict[str, List[Dict[str, float]]] = field(
        default_factory=dict
    )


def check_constraints(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    *,
    update_solution_schedule: bool = True,
) -> Tuple[ConstraintReport, Dict[str, Tuple[float, float]]]:
    travel_energy_per_time = (
        float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5
    )
    min_time_window_ref = _reference_floor(config, "min_time_window_ref")
    min_energy_ref = _reference_floor(config, "min_energy_ref")
    schedule: Dict[str, Tuple[float, float]] = {}

    by_type = {"capability": 0.0, "time_window": 0.0, "energy": 0.0}
    by_task: Dict[str, Dict[str, float]] = {}
    by_route: Dict[str, Dict[str, float]] = {}
    time_window_details: List[Dict[str, float]] = []
    energy_details: List[Dict[str, float]] = []
    time_window_lateness_sum = 0.0
    time_window_ref_sum = 0.0
    energy_over_sum = 0.0
    energy_ref_sum = 0.0

    for aid in instance.all_agent_ids():
        agent = instance.agent_by_id(aid)
        route = [int(tid) for tid in solution.routes.get(aid, [])]
        route_key = str(aid)
        by_route[route_key] = {"capability": 0.0, "time_window": 0.0, "energy": 0.0}

        cur_loc = instance.depot.loc
        cur_time = 0.0
        agent_energy = 0.0
        task_energy: List[Tuple[int, float]] = []

        for tid in route:
            task = instance.task_by_id(tid)
            task_key = str(tid)
            by_task.setdefault(
                task_key, {"capability": 0.0, "time_window": 0.0, "energy": 0.0}
            )

            cap_def = _capability_deficit(agent, task)
            if cap_def > 0:
                _add_violation(
                    by_type,
                    by_task,
                    by_route,
                    task_key,
                    route_key,
                    "capability",
                    cap_def,
                )

            dist = instance.distance(cur_loc, task.loc)
            t_travel = instance.travel_time(agent, cur_loc, task.loc)
            cur_time += t_travel
            e_travel = agent.travel_energy_rate * (
                t_travel if travel_energy_per_time else dist
            )
            agent_energy += e_travel
            task_energy.append((tid, e_travel))

            if cur_time < task.tw_start:
                wait = task.tw_start - cur_time
                cur_time += wait
                e_wait = agent.standby_power * wait
                agent_energy += e_wait
                task_energy[-1] = (tid, task_energy[-1][1] + e_wait)

            service_start = cur_time
            service_end = service_start + task.service_time
            cur_time = service_end
            late = max(0.0, service_start - task.tw_end)
            time_ref = max(
                float(task.tw_end) - float(task.tw_start), min_time_window_ref
            )
            time_window_lateness_sum += late
            time_window_ref_sum += time_ref
            time_window_details.append(
                {
                    "task_id": int(task.id),
                    "lateness": float(late),
                    "time_ref": float(time_ref),
                    "ratio": float(late / time_ref),
                }
            )
            if late > 0:
                _add_violation(
                    by_type, by_task, by_route, task_key, route_key, "time_window", late
                )

            e_service = _service_energy(agent, task)
            agent_energy += e_service
            task_energy[-1] = (tid, task_energy[-1][1] + e_service)
            schedule[f"{aid}:{tid}"] = (service_start, service_end)
            cur_loc = task.loc

        if config.eval.include_depot_legs and route:
            dist_back = instance.distance(cur_loc, instance.depot.loc)
            t_back = instance.travel_time(agent, cur_loc, instance.depot.loc)
            e_back = agent.travel_energy_rate * (
                t_back if travel_energy_per_time else dist_back
            )
            agent_energy += e_back
            task_energy[-1] = (task_energy[-1][0], task_energy[-1][1] + e_back)

        excess = max(0.0, agent_energy - agent.init_energy)
        energy_ref = max(float(agent.init_energy), min_energy_ref)
        energy_over_sum += excess
        energy_ref_sum += energy_ref
        energy_details.append(
            {
                "agent_id": int(agent.id),
                "energy_over": float(excess),
                "energy_ref": float(energy_ref),
                "ratio": float(excess / energy_ref),
            }
        )
        if excess > _EPS and task_energy:
            total_task_energy = sum(max(0.0, energy) for _, energy in task_energy)
            if total_task_energy <= _EPS:
                share = excess / float(len(task_energy))
                for tid, _ in task_energy:
                    _add_violation(
                        by_type, by_task, by_route, str(tid), route_key, "energy", share
                    )
            else:
                for tid, energy in task_energy:
                    portion = excess * max(0.0, energy) / total_task_energy
                    _add_violation(
                        by_type,
                        by_task,
                        by_route,
                        str(tid),
                        route_key,
                        "energy",
                        portion,
                    )

    by_task = {
        tid: _clean_violation_map(values)
        for tid, values in by_task.items()
        if sum(values.values()) > _EPS
    }
    by_route = {
        aid: _clean_violation_map(values)
        for aid, values in by_route.items()
        if sum(values.values()) > _EPS
    }
    by_type = _clean_violation_map(by_type)

    capability = float(by_type.get("capability", 0.0))
    time_window = float(by_type.get("time_window", 0.0))
    energy = float(by_type.get("energy", 0.0))
    total = capability + time_window + energy
    recoverable = time_window + energy
    unrecoverable = capability
    ratio_by_type = {
        "time_window": (
            float(time_window_lateness_sum / time_window_ref_sum)
            if time_window_ref_sum > _EPS
            else 0.0
        ),
        "energy": (
            float(energy_over_sum / energy_ref_sum) if energy_ref_sum > _EPS else 0.0
        ),
    }

    if update_solution_schedule:
        solution.schedule = {
            (int(pair.split(":", 1)[0]), int(pair.split(":", 1)[1])): value
            for pair, value in schedule.items()
        }

    return (
        ConstraintReport(
            is_feasible=bool(total <= _EPS),
            violation_total=float(total),
            violation_capability=float(capability),
            violation_time_window=float(time_window),
            violation_energy=float(energy),
            recoverable_violation_total=float(recoverable),
            unrecoverable_violation_total=float(unrecoverable),
            violation_by_type=by_type,
            violation_by_task=by_task,
            violation_by_route=by_route,
            violation_ratio_by_type=ratio_by_type,
            violation_details_by_type={
                "time_window": time_window_details,
                "energy": energy_details,
            },
        ),
        schedule,
    )


def _add_violation(
    by_type: Dict[str, float],
    by_task: Dict[str, Dict[str, float]],
    by_route: Dict[str, Dict[str, float]],
    task_key: str,
    route_key: str,
    violation_type: str,
    value: float,
) -> None:
    amount = float(value)
    by_type[violation_type] = by_type.get(violation_type, 0.0) + amount
    by_task.setdefault(task_key, {"capability": 0.0, "time_window": 0.0, "energy": 0.0})
    by_route.setdefault(
        route_key, {"capability": 0.0, "time_window": 0.0, "energy": 0.0}
    )
    by_task[task_key][violation_type] = (
        by_task[task_key].get(violation_type, 0.0) + amount
    )
    by_route[route_key][violation_type] = (
        by_route[route_key].get(violation_type, 0.0) + amount
    )


def _clean_violation_map(values: Dict[str, float]) -> Dict[str, float]:
    return {
        key: float(value) for key, value in values.items() if abs(float(value)) > _EPS
    }


def _capability_deficit(agent: Agent, task: Task) -> float:
    return float(len(task.skill_req - agent.skills))


def _service_energy(agent: Agent, task: Task) -> float:
    return sum(
        float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0))
        for skill in task.skill_req & agent.skills
    )


def _reference_floor(config: Config, name: str) -> float:
    value = float(config.extras.get(name, 1e-6))
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"config.extras['{name}'] must be a positive finite number")
    return value
