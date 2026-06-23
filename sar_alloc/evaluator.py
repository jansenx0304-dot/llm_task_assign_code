from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from .config import Config, ObjectiveLayer, ObjectivePolicy
from .constraint_checker import check_constraints
from .models import Instance
from .schemas import CONSTRAINT_METRICS, QUALITY_METRICS
from .solution import AssignmentSolution, EvalResult


_EPS = 1e-9


def evaluate(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> EvalResult:
    travel_energy_per_time = float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5
    total_distance = 0.0
    total_time = 0.0
    makespan = 0.0
    travel_energy = 0.0
    standby_energy = 0.0
    service_energy = 0.0
    route_counts: List[float] = []

    missed_priority = sum(float(instance.task_by_id(int(tid)).priority) for tid in solution.unassigned)
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

            e_travel = agent.travel_energy_rate * (t_travel if travel_energy_per_time else dist)
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
            travel_energy += agent.travel_energy_rate * (t_back if travel_energy_per_time else dist_back)

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
    ev = EvalResult(quality_metrics=quality_metrics, constraint_report=constraint_report)
    solution.eval = ev
    return ev


def compare_quality(eval_a: EvalResult, eval_b: EvalResult, objective_layers: Iterable[Any]) -> int:
    for layer in _normalize_layers(objective_layers):
        metric = str(layer["metric"])
        if metric in CONSTRAINT_METRICS:
            raise ValueError(f"constraint metric is not allowed in quality comparison: {metric}")
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


def build_lex_key(metrics: Dict[str, float], objective_layers: Iterable[Any]) -> Tuple[float, ...]:
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
    contract_objective_layers: Iterable[Any],
    global_objective_layers: Iterable[Any],
) -> Dict[str, Dict[str, Any]]:
    """Build the two explicitly scoped objective keys used by the closed loop."""
    contract_layers = _normalize_layers(contract_objective_layers)
    global_layers = _normalize_layers(global_objective_layers)
    metrics = {
        item["metric"]: float(evaluation.get_quality_metric(item["metric"]))
        for item in contract_layers + global_layers
    }
    return {
        "contract": {
            "layers": [item["metric"] for item in contract_layers],
            "key": list(build_lex_key(metrics, contract_layers)),
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


def _service_energy(agent: Any, task: Any) -> float:
    return sum(float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0)) for skill in task.skill_req & agent.skills)


def _coefficient_of_variation(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if abs(mean) <= _EPS:
        return 0.0
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return float((var ** 0.5) / mean)
