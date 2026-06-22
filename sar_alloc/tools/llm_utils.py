from __future__ import annotations

"""Problem summaries and deterministic compilation of public LLM controls."""

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..config import Config, ObjectiveLayer
from ..evaluator import evaluate
from ..feasibility_policy_compiler import compile_feasibility_control
from ..llm_public_interface import PublicCandidates
from ..models import Agent, Instance, Task
from ..operators import (
    AcceptancePolicy,
    CompiledALNSPolicy,
    DestroyPolicy,
    InsertionPolicy,
    SolverRequest,
)
from ..solution import AssignmentSolution


QUALITY_METRICS = (
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance",
)
_EPS = 1e-9


@dataclass(slots=True)
class SearchContract:
    contract_id: str
    contract_type: str
    stage_goal: Dict[str, str]
    stage_objective_layers: List[Dict[str, str]]
    guidance: Dict[str, str]
    feasibility_control: Dict[str, Any]
    feasibility_policy: Dict[str, Any]
    completion_policy: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "stage_goal": dict(self.stage_goal),
            "stage_objective_layers": list(self.stage_objective_layers),
            "guidance": dict(self.guidance),
            "feasibility_control": _contract_feasibility_view(
                self.feasibility_control,
                self.feasibility_policy,
            ),
            "feasibility_policy": dict(self.feasibility_policy),
            "completion_policy": dict(self.completion_policy),
        }


@dataclass(slots=True)
class ContractProgress:
    contract_id: str
    solver_actions: int = 0
    time_used_sec: float = 0.0
    iters_used: int = 0
    event_counts: Dict[str, int] = field(default_factory=dict)
    consecutive_event_counts: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "solver_actions": self.solver_actions,
            "time_used_sec": round(self.time_used_sec, 6),
            "iters_used": self.iters_used,
            "event_counts": dict(self.event_counts),
            "consecutive_event_counts": dict(self.consecutive_event_counts),
        }


def llm_solution_summary(solution: AssignmentSolution, instance: Instance, config: Config, update_solution_schedule: bool = True) -> Dict[str, Any]:
    ev = evaluate(solution, instance, config, update_solution_schedule=update_solution_schedule)
    report = ev.constraint_report
    return {
        "is_feasible": bool(report.is_feasible),
        "lex_key": list(ev.lex_key or ()),
        "quality_summary": {name: float(ev.quality_metrics.get(name, 0.0)) for name in QUALITY_METRICS},
        "feasibility_summary": {
            "is_feasible": bool(report.is_feasible),
            "violation_total": float(report.violation_total),
            "violation_by_type": {
                "capability": float(report.violation_capability),
                "time_window": float(report.violation_time_window),
                "energy": float(report.violation_energy),
            },
            "recoverable_violation_total": float(report.recoverable_violation_total),
            "unrecoverable_violation_total": float(report.unrecoverable_violation_total),
            "violation_ratio_by_type": {
                name: float(value)
                for name, value in report.violation_ratio_by_type.items()
            },
            "violation_details_by_type": {
                name: [dict(item) for item in items]
                for name, items in report.violation_details_by_type.items()
            },
        },
    }


def llm_instance_summary(instance: Instance, rng_seed: int = 0) -> Dict[str, Any]:
    rng = random.Random(rng_seed)
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    if not tasks or not agents:
        return {
            "num_tasks": len(tasks),
            "num_agents": len(agents),
            "skills": {},
            "time_window_risk": {},
            "energy_risk": {},
            "spatial": {},
            "relaxation_scale_context": _relaxation_scale_context(tasks, agents),
        }

    def capable(agent: Agent, task: Task) -> bool:
        return set(task.skill_req).issubset(agent.skills)

    capable_counts = [sum(1 for agent in agents if capable(agent, task)) for task in tasks]
    negative_slack = sum(
        1 for task in tasks
        if min(instance.travel_time(agent, instance.depot.loc, task.loc) for agent in agents) > task.tw_end + _EPS
    )
    tight_energy = 0
    for task in tasks:
        ratios = []
        for agent in agents:
            if not capable(agent, task) or agent.init_energy <= _EPS:
                continue
            service = sum(task.service_time * agent.skill_energy_rate.get(skill, 1.0) for skill in task.skill_req)
            travel = agent.travel_energy_rate * instance.distance(instance.depot.loc, task.loc) * 2.0
            ratios.append((service + travel) / agent.init_energy)
        tight_energy += int(bool(ratios) and min(ratios) > 0.85)
    depot_distances = [instance.distance(instance.depot.loc, task.loc) for task in tasks]
    mean_distance = sum(depot_distances) / len(depot_distances)
    nn_distance = _mean_nearest_neighbor_distance(instance, tasks, rng, min(len(tasks), max(2, int(14 * math.sqrt(len(tasks))))))
    return {
        "num_tasks": len(tasks),
        "num_agents": len(agents),
        "skills": {
            "skill_uncoverable_task_frac": sum(count == 0 for count in capable_counts) / len(tasks),
            "skill_bottleneck_task_frac": sum(count <= 1 for count in capable_counts) / len(tasks),
        },
        "time_window_risk": {"negative_slack_frac_lb": negative_slack / len(tasks)},
        "energy_risk": {"energy_tight_frac_lb": tight_energy / len(tasks)},
        "spatial": {
            "cluster_strength": 0.0 if mean_distance <= _EPS else max(0.0, min(1.0, 1.0 - nn_distance / mean_distance)),
            "radius95_to_depot": _quantile(depot_distances, 0.95),
        },
        "relaxation_scale_context": _relaxation_scale_context(tasks, agents),
    }


def compile_global_objective(config: Config, raw_global_objective: Dict[str, Any]) -> List[Dict[str, str]]:
    layers = [
        {"name": name, "metric": name, "direction": "min"}
        for name in raw_global_objective["objective_layers"]
    ]
    config.eval.objective_policy.layers = [ObjectiveLayer(**layer) for layer in layers]
    return layers


def compile_insertion_control(control: Dict[str, Any], candidates: PublicCandidates) -> InsertionPolicy:
    operators = {name: 2 for name in candidates.names("insertion_operator_candidates")}
    task_signals = {name: 0 for name in candidates.names("insertion_task_signal_candidates")}
    position_signals = {name: 0 for name in candidates.names("insertion_position_signal_candidates")}
    for item in control["operator_scores"]:
        operators[item["name"]] = int(item["score"])
    for item in control["task_signal_scores"]:
        task_signals[item["name"]] = int(item["score"])
    for item in control["position_signal_scores"]:
        position_signals[item["name"]] = int(item["score"])
    return InsertionPolicy(operators, task_signals, position_signals)


def compile_destroy_control(control: Dict[str, Any], candidates: PublicCandidates) -> DestroyPolicy:
    operators = {name: 2 for name in candidates.names("destroy_operator_candidates")}
    signals = {name: 0 for name in candidates.names("destroy_signal_candidates")}
    for item in control["operator_scores"]:
        operators[item["name"]] = int(item["score"])
    for item in control["signal_scores"]:
        signals[item["name"]] = int(item["score"])
    score = int(control["intensity_score"])
    return DestroyPolicy(operators, signals, score, 0.05 + 0.03 * score)


def compile_acceptance(control: Dict[str, Any]) -> AcceptancePolicy:
    mode = str(control["mode"])
    score = int(control["intensity_score"])
    if mode == "greedy":
        return AcceptancePolicy(mode, score, 0.0, 0.0)
    if mode == "threshold":
        return AcceptancePolicy(mode, score, 0.02 * score, 0.5 * score)
    return AcceptancePolicy(mode, score, 0.05 * score, float(score))


def compile_solver_control(solver_decision: Dict[str, Any], candidates: PublicCandidates) -> CompiledALNSPolicy:
    decision = solver_decision["solver_decision"]
    return CompiledALNSPolicy(
        destroy_policy=compile_destroy_control(decision["destroy_control"], candidates),
        insertion_policy=compile_insertion_control(decision["insertion_control"], candidates),
        acceptance_policy=compile_acceptance(decision["acceptance_control"]),
    )


def compile_contract(
    raw_contract: Dict[str, Any],
    contract_id: str,
    config: Optional[Config] = None,
) -> SearchContract:
    feasibility_control = dict(raw_contract["feasibility_control"])
    feasibility_control["relaxation_ratios"] = [
        dict(item) for item in feasibility_control.get("relaxation_ratios", [])
    ]
    feasibility_policy = compile_feasibility_control(feasibility_control, config)
    return SearchContract(
        contract_id=contract_id,
        contract_type=str(raw_contract["contract_type"]),
        stage_goal=dict(raw_contract["stage_goal"]),
        stage_objective_layers=[
            {"metric": name, "direction": "min"}
            for name in raw_contract["stage_objective_layers"]
        ],
        guidance=dict(raw_contract["guidance"]),
        feasibility_control=feasibility_control,
        feasibility_policy=feasibility_policy,
        completion_policy=dict(raw_contract["completion_policy"]),
    )


def derive_solver_request(contract: SearchContract, progress: ContractProgress) -> SolverRequest:
    policy = contract.completion_policy
    remaining_actions = max(1, int(policy["max_solver_actions"]) - progress.solver_actions)
    remaining_time = max(1e-6, float(policy["max_time_sec"]) - progress.time_used_sec)
    remaining_iters = max(1, int(policy["max_iters"]) - progress.iters_used)
    return SolverRequest(
        time_limit_sec=remaining_time / remaining_actions,
        max_iters=max(1, remaining_iters // remaining_actions),
    )


def format_instance_summary(summary: Dict[str, Any]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in summary.items())


def format_solution_summary(summary: Dict[str, Any]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in summary.items())


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    position = max(0.0, min(1.0, q)) * (len(ordered) - 1)
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] if lo == hi else ordered[lo] * (hi - position) + ordered[hi] * (position - lo)


def _mean_nearest_neighbor_distance(instance: Instance, tasks: List[Task], rng: random.Random, sample: int) -> float:
    if len(tasks) <= 1:
        return 0.0
    selected = tasks if sample >= len(tasks) else rng.sample(tasks, sample)
    return sum(min(instance.distance(task.loc, other.loc) for other in tasks if other.id != task.id) for task in selected) / len(selected)


def _relaxation_scale_context(tasks: List[Task], agents: List[Agent]) -> Dict[str, Any]:
    time_ref = _quantile([max(0.0, float(task.tw_end) - float(task.tw_start)) for task in tasks], 0.5)
    energy_ref = _quantile([max(0.0, float(agent.init_energy)) for agent in agents], 0.5)
    return {
        "time_window": {
            "typical_reference": f"median task time window width = {time_ref:.6g}",
            "examples": [
                f"limit_ratio=0.05 ~= typical lateness {0.05 * time_ref:.6g}",
                f"limit_ratio=0.10 ~= typical lateness {0.10 * time_ref:.6g}",
            ],
        },
        "energy": {
            "typical_reference": f"median agent init_energy = {energy_ref:.6g}",
            "examples": [
                f"limit_ratio=0.05 ~= typical over-energy {0.05 * energy_ref:.6g}",
                f"limit_ratio=0.10 ~= typical over-energy {0.10 * energy_ref:.6g}",
            ],
        },
    }


def _contract_feasibility_view(
    control: Dict[str, Any],
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    view = dict(control)
    view["relaxation_ratios"] = [dict(item) for item in control.get("relaxation_ratios", [])]
    view["compiled_policy_summary"] = {
        name: dict(values)
        for name, values in dict(policy.get("per_type", {}) or {}).items()
    }
    return view


__all__ = [
    "QUALITY_METRICS",
    "SearchContract",
    "ContractProgress",
    "llm_solution_summary",
    "llm_instance_summary",
    "compile_global_objective",
    "compile_insertion_control",
    "compile_destroy_control",
    "compile_acceptance",
    "compile_solver_control",
    "compile_contract",
    "derive_solver_request",
    "format_instance_summary",
    "format_solution_summary",
]
