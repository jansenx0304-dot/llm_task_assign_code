from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from .config import Config, ObjectiveLayer
from .models import Agent, Instance, Task
from .schemas import CONSTRAINT_METRICS, QUALITY_METRICS
from .solution import AssignmentSolution, EvalResult

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
    violation_details_by_type: Dict[str, List[Dict[str, float]]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProtectedMetricCheck:
    passed: bool
    violations: list[Dict[str, float | str]]

    def as_dict(self) -> Dict[str, Any]:
        return {"passed": self.passed, "violations": list(self.violations)}


def check_constraints(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    *,
    update_solution_schedule: bool = True,
) -> Tuple[ConstraintReport, Dict[str, Tuple[float, float]]]:
    travel_energy_per_time = float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5
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
            by_task.setdefault(task_key, {"capability": 0.0, "time_window": 0.0, "energy": 0.0})

            cap_def = _capability_deficit(agent, task)
            if cap_def > 0:
                _add_violation(by_type, by_task, by_route, task_key, route_key, "capability", cap_def)

            dist = instance.distance(cur_loc, task.loc)
            t_travel = instance.travel_time(agent, cur_loc, task.loc)
            cur_time += t_travel
            e_travel = agent.travel_energy_rate * (t_travel if travel_energy_per_time else dist)
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
            time_ref = max(float(task.tw_end) - float(task.tw_start), min_time_window_ref)
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
                _add_violation(by_type, by_task, by_route, task_key, route_key, "time_window", late)

            e_service = _service_energy(agent, task)
            agent_energy += e_service
            task_energy[-1] = (tid, task_energy[-1][1] + e_service)
            schedule[f"{aid}:{tid}"] = (service_start, service_end)
            cur_loc = task.loc

        if config.eval.include_depot_legs and route:
            dist_back = instance.distance(cur_loc, instance.depot.loc)
            t_back = instance.travel_time(agent, cur_loc, instance.depot.loc)
            e_back = agent.travel_energy_rate * (t_back if travel_energy_per_time else dist_back)
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
                    _add_violation(by_type, by_task, by_route, str(tid), route_key, "energy", share)
            else:
                for tid, energy in task_energy:
                    portion = excess * max(0.0, energy) / total_task_energy
                    _add_violation(by_type, by_task, by_route, str(tid), route_key, "energy", portion)

    by_task = {tid: _clean_violation_map(values) for tid, values in by_task.items() if sum(values.values()) > _EPS}
    by_route = {aid: _clean_violation_map(values) for aid, values in by_route.items() if sum(values.values()) > _EPS}
    by_type = _clean_violation_map(by_type)

    capability = float(by_type.get("capability", 0.0))
    time_window = float(by_type.get("time_window", 0.0))
    energy = float(by_type.get("energy", 0.0))
    total = capability + time_window + energy
    recoverable = time_window + energy
    unrecoverable = capability
    ratio_by_type = {
        "time_window": float(time_window_lateness_sum / time_window_ref_sum) if time_window_ref_sum > _EPS else 0.0,
        "energy": float(energy_over_sum / energy_ref_sum) if energy_ref_sum > _EPS else 0.0,
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
            violation_details_by_type={"time_window": time_window_details, "energy": energy_details},
        ),
        schedule,
    )


def check_protected_metrics(
    quality: Mapping[str, Any],
    bounds: Iterable[Mapping[str, Any]],
) -> ProtectedMetricCheck:
    violations: list[Dict[str, float | str]] = []
    for raw_bound in bounds:
        metric = str(raw_bound["metric"])
        baseline = float(raw_bound["baseline"])
        max_worsen = float(raw_bound.get("max_worsen", 0.0) or 0.0)
        actual = float(quality[metric])
        delta = actual - baseline
        if delta > max_worsen + _EPS:
            violations.append(
                {
                    "metric": metric,
                    "baseline": baseline,
                    "actual": actual,
                    "delta": delta,
                    "max_worsen": max_worsen,
                }
            )
    return ProtectedMetricCheck(passed=not violations, violations=violations)


def evaluation_quality(evaluation: Any) -> Dict[str, float]:
    metrics = getattr(evaluation, "quality_metrics", {}) or {}
    return {str(name): float(value) for name, value in metrics.items()}


def evaluate(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> EvalResult:
    travel_energy_per_time = (
        float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5
    )
    total_distance = 0.0
    total_time = 0.0
    makespan = 0.0
    travel_energy = 0.0
    standby_energy = 0.0
    service_energy = 0.0
    route_counts: List[float] = []

    missed_priority = sum(
        float(instance.task_by_id(int(tid)).priority) for tid in solution.unassigned
    )
    unassigned_count = float(len(solution.unassigned))

    for aid in instance.all_agent_ids():
        agent = instance.agent_by_id(aid)
        route = [int(tid) for tid in solution.routes.get(aid, [])]
        route_counts.append(float(len(route)))
        cur_loc = instance.depot.loc
        cur_time = 0.0

        for tid in route:
            task = instance.task_by_id(tid)
            dist = instance.distance(cur_loc, task.loc)
            t_travel = instance.travel_time(agent, cur_loc, task.loc)
            total_distance += dist
            cur_time += t_travel
            total_time += t_travel

            e_travel = agent.travel_energy_rate * (
                t_travel if travel_energy_per_time else dist
            )
            travel_energy += e_travel

            if cur_time < task.tw_start:
                wait = task.tw_start - cur_time
                cur_time += wait
                total_time += wait
                standby_energy += agent.standby_power * wait

            service_start = cur_time
            cur_time = service_start + task.service_time
            total_time += task.service_time
            service_energy += _service_energy(agent, task)
            cur_loc = task.loc

        if config.eval.include_depot_legs and route:
            dist_back = instance.distance(cur_loc, instance.depot.loc)
            t_back = instance.travel_time(agent, cur_loc, instance.depot.loc)
            total_distance += dist_back
            cur_time += t_back
            total_time += t_back
            travel_energy += agent.travel_energy_rate * (
                t_back if travel_energy_per_time else dist_back
            )

        makespan = max(makespan, cur_time)

    constraint_report, _ = check_constraints(
        solution,
        instance,
        config,
        update_solution_schedule=update_solution_schedule,
    )
    quality_metrics = {
        "missed_priority": float(missed_priority),
        "unassigned_count": float(unassigned_count),
        "energy_total": float(travel_energy + standby_energy + service_energy),
        "total_distance": float(total_distance),
        "makespan": float(makespan),
        "route_balance": float(_coefficient_of_variation(route_counts)),
    }
    ev = EvalResult(
        quality_metrics=quality_metrics, constraint_report=constraint_report
    )
    solution.eval = ev
    return ev


def compare_quality(
    eval_a: EvalResult, eval_b: EvalResult, objective_layers: Iterable[Any]
) -> int:
    for layer in _normalize_layers(objective_layers):
        metric = str(layer["metric"])
        if metric in CONSTRAINT_METRICS:
            raise ValueError(
                f"constraint metric is not allowed in quality comparison: {metric}"
            )
        if metric not in QUALITY_METRICS:
            raise ValueError(f"unknown quality metric: {metric}")
        va = float(eval_a.get_quality_metric(metric))
        vb = float(eval_b.get_quality_metric(metric))
        diff = va - vb
        if str(layer["direction"]) == "max":
            diff = -diff
        if diff < -_EPS:
            return -1
        if diff > _EPS:
            return 1
    return 0


def compare(a: EvalResult, b: EvalResult, config: Config) -> int:
    return compare_quality(a, b, config.eval.objective_policy.layers)


def build_lex_key(
    metrics: Dict[str, float], objective_layers: Iterable[Any]
) -> Tuple[float, ...]:
    key_values: List[float] = []
    for layer in _normalize_layers(objective_layers):
        metric = str(layer["metric"])
        if metric in CONSTRAINT_METRICS:
            raise ValueError(f"constraint metric is not allowed in objective: {metric}")
        value = float(metrics.get(metric, 0.0))
        if str(layer["direction"]) == "max":
            value = -value
        key_values.append(value)
    return tuple(key_values)


def build_objective_keys(
    evaluation: EvalResult,
    stage_objective_layers: Iterable[Any],
    global_objective_layers: Iterable[Any],
) -> Dict[str, Dict[str, Any]]:
    """Build the two explicitly scoped objective keys used by the closed loop."""
    stage_layers = _normalize_layers(stage_objective_layers)
    global_layers = _normalize_layers(global_objective_layers)
    metrics = {
        item["metric"]: float(evaluation.get_quality_metric(item["metric"]))
        for item in stage_layers + global_layers
    }
    return {
        "stage": {
            "layers": [item["metric"] for item in stage_layers],
            "key": list(build_lex_key(metrics, stage_layers)),
        },
        "global": {
            "layers": [item["metric"] for item in global_layers],
            "key": list(build_lex_key(metrics, global_layers)),
        },
    }


def _normalize_layers(objective_layers: Iterable[Any]) -> List[Dict[str, str]]:
    layers: List[Dict[str, str]] = []
    for raw in objective_layers:
        if isinstance(raw, ObjectiveLayer):
            metric = raw.metric
            direction = raw.direction
        elif isinstance(raw, dict):
            metric = str(raw.get("metric", ""))
            direction = str(raw.get("direction", ""))
        else:
            metric = str(getattr(raw, "metric", ""))
            direction = str(getattr(raw, "direction", ""))
        if not metric:
            continue
        if direction not in {"min", "max"}:
            raise ValueError(f"illegal objective direction: {direction}")
        layers.append({"metric": metric, "direction": direction})
    if not layers:
        raise ValueError("Objective policy has no layers.")
    return layers


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
    by_route.setdefault(route_key, {"capability": 0.0, "time_window": 0.0, "energy": 0.0})
    by_task[task_key][violation_type] = by_task[task_key].get(violation_type, 0.0) + amount
    by_route[route_key][violation_type] = by_route[route_key].get(violation_type, 0.0) + amount


def _clean_violation_map(values: Dict[str, float]) -> Dict[str, float]:
    return {key: float(value) for key, value in values.items() if abs(float(value)) > _EPS}


def _capability_deficit(agent: Agent, task: Task) -> float:
    return float(len(task.skill_req - agent.skills))


def _service_energy(agent: Any, task: Any) -> float:
    return sum(
        float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0))
        for skill in task.skill_req & agent.skills
    )


def _coefficient_of_variation(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if abs(mean) <= _EPS:
        return 0.0
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return float((var**0.5) / mean)


def _reference_floor(config: Config, name: str) -> float:
    value = float(config.extras.get(name, 1e-6))
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"config.extras['{name}'] must be a positive finite number")
    return value
