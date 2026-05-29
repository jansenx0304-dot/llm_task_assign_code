from __future__ import annotations

from typing import Dict, List, Tuple

from .config import Config, ObjectiveLayer, ObjectivePolicy
from .models import Agent, Instance, Task
from .solution import AssignmentSolution, EvalResult


_EPS = 1e-9


def evaluate(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> EvalResult:
    """Evaluate a solution under the LLM-selected objective policy.

    Args:
        solution: Assignment solution to score.
        instance: Task-assignment instance that defines agents, tasks, and
            travel/energy calculations.
        config: Run config. `config.eval.objective_policy.layers` must already
            have been populated from a validated LLM objective plan.
        update_solution_schedule: Whether to write the computed schedule back to
            the solution object.

    Returns:
        An `EvalResult` containing hard-constraint violations, soft metrics, and
        the lexicographic key used by comparisons.

    Raises:
        ValueError: If no objective layers were provided by the LLM.
    """
    travel_energy_per_time = float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5

    violations: Dict[str, float] = {}
    total_distance = 0.0
    total_time = 0.0
    makespan = 0.0
    travel_energy = 0.0
    standby_energy = 0.0
    service_energy = 0.0
    schedule = {} if update_solution_schedule else None

    unassigned_count = len(solution.unassigned)
    missed_priority = 0.0
    for tid in solution.unassigned:
        missed_priority += float(instance.task_by_id(tid).priority)

    for aid in instance.all_agent_ids():
        agent = instance.agent_by_id(aid)
        route = solution.routes.get(aid, [])
        cur_loc = instance.depot.loc
        cur_time = 0.0
        agent_energy = 0.0

        for tid in route:
            task = instance.task_by_id(tid)

            cap_def = _capability_deficit(agent, task)
            if cap_def > 0:
                violations["capability"] = violations.get("capability", 0.0) + cap_def

            dist = instance.distance(cur_loc, task.loc)
            t_travel = instance.travel_time(agent, cur_loc, task.loc)
            total_distance += dist
            cur_time += t_travel
            total_time += t_travel

            e_travel = agent.travel_energy_rate * (t_travel if travel_energy_per_time else dist)
            travel_energy += e_travel
            agent_energy += e_travel

            arrival = cur_time
            if arrival < task.tw_start:
                wait = task.tw_start - arrival
                cur_time += wait
                total_time += wait
                e_wait = agent.standby_power * wait
                standby_energy += e_wait
                agent_energy += e_wait

            service_start = cur_time
            service_end = service_start + task.service_time
            cur_time = service_end
            total_time += task.service_time

            late = max(0.0, service_start - task.tw_end)
            if late > 0:
                violations["time_window"] = violations.get("time_window", 0.0) + late

            e_service = _service_energy(agent, task)
            service_energy += e_service
            agent_energy += e_service

            if schedule is not None:
                schedule[(aid, tid)] = (service_start, service_end)
            cur_loc = task.loc

        if config.eval.include_depot_legs and len(route) > 0:
            dist_back = instance.distance(cur_loc, instance.depot.loc)
            t_back = instance.travel_time(agent, cur_loc, instance.depot.loc)
            total_distance += dist_back
            cur_time += t_back
            total_time += t_back
            e_back = agent.travel_energy_rate * (t_back if travel_energy_per_time else dist_back)
            travel_energy += e_back
            agent_energy += e_back

        if agent_energy - agent.init_energy > _EPS:
            violations["energy"] = violations.get("energy", 0.0) + (agent_energy - agent.init_energy)

        makespan = max(makespan, cur_time)

    violation_total = sum(violations.values()) if violations else 0.0
    total_energy = travel_energy + standby_energy + service_energy
    metrics: Dict[str, float] = {
        "violation_total": float(violation_total),
        "violation_capability": float(violations.get("capability", 0.0)),
        "violation_time_window": float(violations.get("time_window", 0.0)),
        "violation_energy": float(violations.get("energy", 0.0)),
        "missed_priority": float(missed_priority),
        "unassigned_count": float(unassigned_count),
        "energy_total": float(total_energy),
        "total_distance": float(total_distance),
        "makespan": float(makespan),
    }

    ev = EvalResult(
        is_feasible=bool(violation_total <= _EPS),
        violations=dict(violations),
        metrics=metrics,
        lex_key=_build_lex_key(metrics, config),
    )

    if update_solution_schedule and schedule is not None:
        solution.schedule = schedule
    solution.eval = ev
    return ev


def _build_lex_key(metrics: Dict[str, float], config: Config) -> Tuple[float, ...]:
    layers = _validated_layers(config.eval.objective_policy)
    key_values: List[float] = []
    for layer in layers:
        value = metrics.get(layer.metric, 0.0)
        if layer.direction == "max":
            value = -value
        key_values.append(float(value))
    return tuple(key_values)


def compare(a: EvalResult, b: EvalResult, config: Config) -> int:
    """Compare two evaluation results using the active lexicographic objective."""
    layers = _validated_layers(config.eval.objective_policy)
    for layer in layers:
        va = a.get_metric(layer.metric)
        vb = b.get_metric(layer.metric)
        diff = va - vb
        if layer.direction == "max":
            diff = -diff
        if diff < -_EPS:
            return -1
        if diff > _EPS:
            return 1
    return 0


def _capability_deficit(agent: Agent, task: Task) -> float:
    return float(len(task.skill_req - agent.skills))


def _service_energy(agent: Agent, task: Task) -> float:
    total_energy = 0.0
    for skill in task.skill_req & agent.skills:
        total_energy += task.service_time * agent.skill_energy_rate.get(skill, 1.0)
    return total_energy


def _validated_layers(policy: ObjectivePolicy) -> List[ObjectiveLayer]:
    layers = [layer for layer in policy.layers if isinstance(layer.metric, str) and layer.metric]
    if not layers:
        raise ValueError("Objective policy has no layers. LLM objective plan is required.")
    if len(layers) > policy.max_layers:
        layers = layers[: policy.max_layers]
    return layers
