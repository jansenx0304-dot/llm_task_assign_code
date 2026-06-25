"""Problem summaries and deterministic compilation of executable controls."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..config import Config, ObjectiveLayer
from ..evaluator import build_objective_keys, evaluate
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
from ..operators.types import (
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
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
    objective_layers: List[Dict[str, str]]
    feasibility_control: Dict[str, Any]
    feasibility_policy: Dict[str, Any]
    situation_assessment: Dict[str, str]
    target_intents: List[Dict[str, Any]]
    protected_metrics: List[Dict[str, Any]]
    resource_policy: Dict[str, Any]
    exit_conditions: Dict[str, List[Dict[str, Any]]]
    explanation: Dict[str, str] = field(default_factory=dict)
    protected_metric_baseline: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "objective_layers": [dict(item) for item in self.objective_layers],
            "feasibility_control": {
                **dict(self.feasibility_control),
                "relaxation_ratios": [
                    dict(item)
                    for item in self.feasibility_control.get("relaxation_ratios", [])
                ],
            },
            "feasibility_policy": dict(self.feasibility_policy),
            "situation_assessment": dict(self.situation_assessment),
            "target_intents": [dict(item) for item in self.target_intents],
            "protected_metrics": [dict(item) for item in self.protected_metrics],
            "protected_metric_baseline": dict(self.protected_metric_baseline),
            "resource_policy": dict(self.resource_policy),
            "exit_conditions": {
                "success": [
                    dict(item) for item in self.exit_conditions.get("success", [])
                ],
                "failure": [
                    dict(item) for item in self.exit_conditions.get("failure", [])
                ],
            },
            "explanation": dict(self.explanation),
        }


@dataclass(slots=True)
class ContractProgress:
    contract_id: str
    solver_actions: int = 0
    time_used_sec: float = 0.0
    iters_used: int = 0
    verification_ids: List[str] = field(default_factory=list)
    contract_objective_status_counts: Dict[str, int] = field(default_factory=dict)
    dominant_blocker_counts: Dict[str, int] = field(default_factory=dict)
    recent_contract_objective_statuses: List[str] = field(default_factory=list)
    recent_blockers: List[str] = field(default_factory=list)
    condition_report: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "solver_actions": self.solver_actions,
            "time_used_sec": round(self.time_used_sec, 6),
            "iters_used": self.iters_used,
            "verification_ids": list(self.verification_ids),
            "contract_objective_status_counts": dict(
                self.contract_objective_status_counts
            ),
            "dominant_blocker_counts": dict(self.dominant_blocker_counts),
            "recent_contract_objective_statuses": list(
                self.recent_contract_objective_statuses[-5:]
            ),
            "recent_blockers": list(self.recent_blockers[-5:]),
            "condition_report": [dict(item) for item in self.condition_report],
        }


@dataclass(slots=True)
class RuntimeControlManifest:
    manifest_id: str
    source_decision_id: str
    contract_id: str
    action: str
    intent_id: str
    trace_id: str
    compiled: Dict[str, Any]
    defaults_applied: List[str]
    validation_report: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "source_decision_id": self.source_decision_id,
            "contract_id": self.contract_id,
            "action": self.action,
            "intent_id": self.intent_id,
            "trace_id": self.trace_id,
            "compiled": _numericize(self.compiled),
            "defaults_applied": list(self.defaults_applied),
            "validation_report": dict(self.validation_report),
        }


def llm_solution_summary(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
    *,
    contract_objective_layers: Optional[List[Dict[str, Any]]] = None,
    global_objective_layers: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    ev = evaluate(
        solution, instance, config, update_solution_schedule=update_solution_schedule
    )
    report = ev.constraint_report
    global_layers = global_objective_layers or [
        {"metric": layer.metric, "direction": layer.direction}
        for layer in config.eval.objective_policy.layers
    ]
    contract_layers = contract_objective_layers or global_layers
    return {
        "is_feasible": bool(report.is_feasible),
        "objective_keys": build_objective_keys(ev, contract_layers, global_layers),
        "quality_summary": {
            name: float(ev.quality_metrics.get(name, 0.0)) for name in QUALITY_METRICS
        },
        "feasibility_summary": {
            "is_feasible": bool(report.is_feasible),
            "violation_total": float(report.violation_total),
            "violation_by_type": {
                "capability": float(report.violation_capability),
                "time_window": float(report.violation_time_window),
                "energy": float(report.violation_energy),
            },
            "recoverable_violation_total": float(report.recoverable_violation_total),
            "unrecoverable_violation_total": float(
                report.unrecoverable_violation_total
            ),
            "violation_ratio_by_type": {
                name: float(value)
                for name, value in report.violation_ratio_by_type.items()
            },
        },
    }


def llm_instance_summary(instance: Instance, rng_seed: int = 0) -> Dict[str, Any]:
    rng = random.Random(rng_seed)
    tasks = list(instance.tasks)
    agents = list(instance.agents)
    base = {
        "num_tasks": len(tasks),
        "num_agents": len(agents),
        "relaxation_scale_context": _relaxation_scale_context(tasks, agents),
    }
    if not tasks or not agents:
        return {
            **base,
            "skills": {},
            "time_window_risk": {},
            "energy_risk": {},
            "spatial": {},
        }

    def capable(agent: Agent, task: Task) -> bool:
        return set(task.skill_req).issubset(agent.skills)

    capable_counts = [
        sum(1 for agent in agents if capable(agent, task)) for task in tasks
    ]
    negative_slack = sum(
        1
        for task in tasks
        if min(
            instance.travel_time(agent, instance.depot.loc, task.loc)
            for agent in agents
        )
        > task.tw_end + _EPS
    )
    tight_energy = 0
    for task in tasks:
        ratios = []
        for agent in agents:
            if not capable(agent, task) or agent.init_energy <= _EPS:
                continue
            service = sum(
                task.service_time * agent.skill_energy_rate.get(skill, 1.0)
                for skill in task.skill_req
            )
            travel = (
                agent.travel_energy_rate
                * instance.distance(instance.depot.loc, task.loc)
                * 2.0
            )
            ratios.append((service + travel) / agent.init_energy)
        tight_energy += int(bool(ratios) and min(ratios) > 0.85)
    depot_distances = [
        instance.distance(instance.depot.loc, task.loc) for task in tasks
    ]
    mean_distance = sum(depot_distances) / len(depot_distances)
    nn_distance = _mean_nearest_neighbor_distance(
        instance, tasks, rng, min(len(tasks), max(2, int(14 * math.sqrt(len(tasks)))))
    )
    return {
        **base,
        "priority_mass": sum(float(task.priority) for task in tasks),
        "skills": {
            "skill_uncoverable_task_frac": sum(count == 0 for count in capable_counts)
            / len(tasks),
            "skill_bottleneck_task_frac": sum(count <= 1 for count in capable_counts)
            / len(tasks),
        },
        "time_window_risk": {"negative_slack_frac_lb": negative_slack / len(tasks)},
        "energy_risk": {"energy_tight_frac_lb": tight_energy / len(tasks)},
        "spatial": {
            "cluster_strength": (
                0.0
                if mean_distance <= _EPS
                else max(0.0, min(1.0, 1.0 - nn_distance / mean_distance))
            ),
            "radius95_to_depot": _quantile(depot_distances, 0.95),
        },
    }


def compile_global_objective(
    config: Config, raw_global_objective: Dict[str, Any]
) -> List[Dict[str, str]]:
    layers = [
        {"name": name, "metric": name, "direction": "min"}
        for name in raw_global_objective["objective_layers"]
    ]
    config.eval.objective_policy.layers = [ObjectiveLayer(**layer) for layer in layers]
    return layers


def compile_acceptance(control: Dict[str, Any]) -> AcceptancePolicy:
    mode = str(control["mode"])
    score = int(control["intensity_score"])
    if mode == "greedy":
        return AcceptancePolicy(mode, score, 0.0, 0.0)
    if mode == "threshold":
        return AcceptancePolicy(mode, score, 0.02 * score, 0.5 * score)
    return AcceptancePolicy(mode, score, 0.05 * score, float(score))


def compile_contract(
    raw_contract: Dict[str, Any],
    contract_id: str,
    config: Optional[Config] = None,
    observation: Optional[Dict[str, Any]] = None,
    protected_metric_baseline: Optional[Dict[str, Any]] = None,
) -> SearchContract:
    baseline = dict(
        protected_metric_baseline or _baseline_from_observation(observation) or {}
    )
    feasibility_control = dict(raw_contract["feasibility_control"])
    feasibility_control["relaxation_ratios"] = [
        dict(item) for item in feasibility_control.get("relaxation_ratios", [])
    ]
    feasibility_policy = compile_feasibility_control(feasibility_control, config)
    return SearchContract(
        contract_id=contract_id,
        contract_type=str(raw_contract["contract_type"]),
        objective_layers=[
            {"metric": str(name), "direction": "min"}
            for name in raw_contract["objective_layers"]
        ],
        feasibility_control=feasibility_control,
        feasibility_policy=feasibility_policy,
        situation_assessment=dict(raw_contract.get("situation_assessment", {}) or {}),
        target_intents=[
            dict(item) for item in raw_contract.get("target_intents", []) or []
        ],
        protected_metrics=[
            dict(item) for item in raw_contract.get("protected_metrics", [])
        ],
        resource_policy=dict(raw_contract["resource_policy"]),
        exit_conditions={
            "success": [
                dict(item)
                for item in raw_contract.get("exit_conditions", {}).get("success", [])
            ],
            "failure": [
                dict(item)
                for item in raw_contract.get("exit_conditions", {}).get("failure", [])
            ],
        },
        explanation=dict(raw_contract.get("explanation", {}) or {}),
        protected_metric_baseline={
            str(name): float(value) for name, value in baseline.items()
        },
    )


def _baseline_from_observation(observation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not observation:
        return {}
    direct = observation.get("protected_metric_baseline")
    if isinstance(direct, dict):
        return direct
    working = observation.get("working_summary", {}) or {}
    quality = working.get("quality_summary", {}) if isinstance(working, dict) else {}
    if isinstance(quality, dict) and quality:
        return quality
    profile = observation.get("problem_profile", {}) or {}
    if isinstance(profile, dict) and "num_tasks" in profile:
        return {
            "missed_priority": float(profile.get("priority_mass", 0.0) or 0.0),
            "unassigned_count": float(profile.get("num_tasks", 0.0) or 0.0),
            "energy_total": 0.0,
            "total_distance": 0.0,
            "makespan": 0.0,
            "route_balance": 0.0,
        }
    return {}


def compile_solver_control(
    solver_decision: Dict[str, Any],
    contract: SearchContract,
    candidates: PublicCandidates,
    observation: Optional[Dict[str, Any]] = None,
    *,
    decision_id: str = "D0",
    manifest_id: str = "R0",
    trace_id: Optional[str] = None,
) -> RuntimeControlManifest:
    if contract.protected_metrics and not contract.protected_metric_baseline:
        fallback = _baseline_from_observation(
            {
                "working_summary": dict(
                    (observation or {}).get("solution_evidence", {}).get("working", {})
                    or {}
                )
            }
        )
        if not fallback:
            fallback = dict(
                (observation or {})
                .get("working_summary", {})
                .get("quality_summary", {})
                or {}
            )
        if not fallback:
            fallback = dict(
                (observation or {})
                .get("solution_evidence", {})
                .get("working", {})
                .get("quality", {})
                or {}
            )
        contract.protected_metric_baseline = {
            str(name): float(value) for name, value in fallback.items()
        }
    decision = solver_decision.get("solver_decision", solver_decision)
    action = str(decision["action"])
    action_space = dict((observation or {}).get("control_catalog", {}) or {})
    intent_id = str(decision.get("intent_id", ""))
    intent = _intent_from_contract(contract, intent_id) if intent_id else {}
    solver_budget = dict(decision.get("solver_budget", {}) or {})
    compiled: Dict[str, Any] = {
        "llm_selected_intent": intent,
        "situation_assessment": dict(decision.get("situation_assessment", {}) or {}),
        "expected_effects": list(decision.get("expected_effects", []) or []),
        "feasibility": _manifest_feasibility(contract.feasibility_policy),
        "resource": _manifest_solver_budget(contract, solver_budget),
        "protected_metric_baseline": dict(contract.protected_metric_baseline),
        "protected_metric_bounds": [
            {
                "metric": str(item["metric"]),
                "baseline": float(
                    contract.protected_metric_baseline[str(item["metric"])]
                ),
                "max_worsen": float(item.get("max_worsen", 0.0) or 0.0),
            }
            for item in contract.protected_metrics
        ],
    }
    defaults: List[str] = []
    consumed = {
        "action",
        "intent_id",
        "situation_assessment",
        "solver_budget",
        "expected_effects",
        "explanation",
    }

    if action in {"construct_initial", "run_alns"}:
        insertion = _compile_insertion_manifest(
            decision["insertion_control"], action_space, candidates, defaults
        )
        compiled["insertion"] = insertion
        consumed.add("insertion_control")
    if action == "run_alns":
        destroy = _compile_destroy_manifest(
            decision["destroy_control"], action_space, candidates, defaults
        )
        acceptance = _compile_acceptance_manifest(decision["acceptance_control"])
        compiled["destroy"] = destroy
        compiled["acceptance"] = acceptance
        consumed |= {"destroy_control", "acceptance_control"}
    if action == "request_supervisor_review":
        compiled["review_request"] = dict(decision.get("review_request", {}) or {})
        consumed.add("review_request")

    operational = {key for key in decision if key != "explanation"}
    return RuntimeControlManifest(
        manifest_id=manifest_id,
        source_decision_id=decision_id,
        contract_id=contract.contract_id,
        action=action,
        intent_id=intent_id,
        trace_id=str(trace_id or f"X_{manifest_id}"),
        compiled=compiled,
        defaults_applied=defaults,
        validation_report={
            "all_candidate_names_valid": True,
            "all_operational_fields_consumed": operational.issubset(consumed),
            "explanation_ignored_by_runtime": "explanation" not in compiled,
            "intent_resolved": bool(
                not intent_id or intent.get("intent_id") == intent_id
            ),
            "nonzero_weights_from_llm": _nonzero_weights_have_llm_source(
                decision, compiled
            ),
        },
    )


def alns_policy_from_manifest(
    manifest: RuntimeControlManifest | Dict[str, Any],
) -> CompiledALNSPolicy:
    raw = (
        manifest.as_dict()
        if isinstance(manifest, RuntimeControlManifest)
        else dict(manifest)
    )
    compiled = raw["compiled"]
    if "destroy" not in compiled:
        raise ValueError("manifest does not contain destroy controls")
    destroy = compiled["destroy"]
    insertion = compiled["insertion"]
    acceptance = compiled["acceptance"]
    return CompiledALNSPolicy(
        destroy_policy=DestroyPolicy(
            operator_weights={
                str(k): int(v) for k, v in destroy["operator_weights"].items()
            },
            signal_weights={
                str(k): int(v) for k, v in destroy["signal_weights"].items()
            },
            intensity_score=int(destroy["intensity_score"]),
            remove_ratio=float(destroy["remove_ratio"]),
        ),
        insertion_policy=InsertionPolicy(
            operator_weights={
                str(k): int(v) for k, v in insertion["operator_weights"].items()
            },
            task_signal_weights={
                str(k): int(v) for k, v in insertion["task_signal_weights"].items()
            },
            position_signal_weights={
                str(k): int(v) for k, v in insertion["position_signal_weights"].items()
            },
        ),
        acceptance_policy=AcceptancePolicy(
            mode=str(acceptance["mode"]),
            intensity_score=int(acceptance["intensity_score"]),
            accept_level=float(acceptance["worsening_allowance"]),
            exploration_score=float(acceptance["threshold"]),
        ),
    )


def insertion_policy_from_manifest(
    manifest: RuntimeControlManifest | Dict[str, Any],
) -> InsertionPolicy:
    raw = (
        manifest.as_dict()
        if isinstance(manifest, RuntimeControlManifest)
        else dict(manifest)
    )
    insertion = raw["compiled"]["insertion"]
    return InsertionPolicy(
        operator_weights={
            str(k): int(v) for k, v in insertion["operator_weights"].items()
        },
        task_signal_weights={
            str(k): int(v) for k, v in insertion["task_signal_weights"].items()
        },
        position_signal_weights={
            str(k): int(v) for k, v in insertion["position_signal_weights"].items()
        },
    )


def derive_solver_request(
    contract: SearchContract, progress: ContractProgress
) -> SolverRequest:
    policy = contract.resource_policy
    remaining_actions = max(1, int(policy["max_actions"]) - progress.solver_actions)
    remaining_time = max(1e-6, float(policy["max_time_sec"]) - progress.time_used_sec)
    remaining_iters = max(1, int(policy["max_iters"]) - progress.iters_used)
    return SolverRequest(
        time_limit_sec=remaining_time / remaining_actions,
        max_iters=max(1, remaining_iters // remaining_actions),
    )


def solver_request_from_manifest(
    manifest: RuntimeControlManifest | Dict[str, Any],
) -> SolverRequest:
    raw = manifest.as_dict() if isinstance(manifest, RuntimeControlManifest) else manifest
    resource = dict((raw.get("compiled", {}) or {}).get("resource", {}) or {})
    return SolverRequest(
        time_limit_sec=max(1e-6, float(resource.get("max_time_sec", 1e-6) or 1e-6)),
        max_iters=max(1, int(resource.get("max_iters", 1) or 1)),
    )


def _compile_insertion_manifest(
    control: Dict[str, Any],
    action_space: Dict[str, Any],
    candidates: PublicCandidates,
    defaults: List[str],
) -> Dict[str, Any]:
    operator_names = _names_from_space(
        action_space,
        "insertion_operators",
        candidates,
        "insertion_operator_candidates",
        INSERTION_OPERATOR_NAMES,
    )
    task_names = _names_from_space(
        action_space,
        "insertion_task_signals",
        candidates,
        "insertion_task_signal_candidates",
        INSERTION_TASK_SIGNAL_NAMES,
    )
    position_names = _names_from_space(
        action_space,
        "insertion_position_signals",
        candidates,
        "insertion_position_signal_candidates",
        INSERTION_POSITION_SIGNAL_NAMES,
    )
    return {
        "operator_weights": _weights_with_defaults(
            operator_names,
            control["operator_scores"],
            2,
            "insertion.operator_weights",
            defaults,
        ),
        "task_signal_weights": _weights_with_defaults(
            task_names,
            control["task_signal_scores"],
            0,
            "insertion.task_signal_weights",
            defaults,
        ),
        "position_signal_weights": _weights_with_defaults(
            position_names,
            control["position_signal_scores"],
            0,
            "insertion.position_signal_weights",
            defaults,
        ),
    }


def _compile_destroy_manifest(
    control: Dict[str, Any],
    action_space: Dict[str, Any],
    candidates: PublicCandidates,
    defaults: List[str],
) -> Dict[str, Any]:
    operator_names = _names_from_space(
        action_space,
        "destroy_operators",
        candidates,
        "destroy_operator_candidates",
        DESTROY_OPERATOR_NAMES,
    )
    signal_names = _names_from_space(
        action_space,
        "destroy_signals",
        candidates,
        "destroy_signal_candidates",
        DESTROY_SIGNAL_NAMES,
    )
    score = int(control["intensity_score"])
    return {
        "operator_weights": _weights_with_defaults(
            operator_names,
            control["operator_scores"],
            2,
            "destroy.operator_weights",
            defaults,
        ),
        "signal_weights": _weights_with_defaults(
            signal_names,
            control["signal_scores"],
            0,
            "destroy.signal_weights",
            defaults,
        ),
        "intensity_score": score,
        "remove_ratio": 0.05 + 0.03 * score,
    }


def _compile_acceptance_manifest(control: Dict[str, Any]) -> Dict[str, Any]:
    policy = compile_acceptance(control)
    return {
        "mode": policy.mode,
        "intensity_score": policy.intensity_score,
        "threshold": policy.exploration_score,
        "worsening_allowance": policy.accept_level,
    }


def _manifest_feasibility(policy: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mode": str(policy.get("mode", "strict")),
        "per_type": {
            str(name): {
                "limit_ratio": float(values.get("limit_ratio", 0.0)),
                "delta_ratio": float(values.get("delta_ratio", 0.0)),
            }
            for name, values in dict(policy.get("per_type", {}) or {}).items()
        },
    }


def feasibility_policy_from_manifest(
    manifest: RuntimeControlManifest | Dict[str, Any],
) -> Dict[str, Any]:
    raw = manifest.as_dict() if isinstance(manifest, RuntimeControlManifest) else manifest
    feasibility = dict((raw.get("compiled", {}) or {}).get("feasibility", {}) or {})
    return {
        "mode": str(feasibility.get("mode", "strict")),
        "per_type": {
            str(name): {
                "limit_ratio": float(values.get("limit_ratio", 0.0)),
                "delta_ratio": float(values.get("delta_ratio", 0.0)),
            }
            for name, values in dict(feasibility.get("per_type", {}) or {}).items()
        },
    }


def _intent_from_contract(
    contract: SearchContract, intent_id: str
) -> Dict[str, Any]:
    for item in contract.target_intents:
        if not isinstance(item, dict) or str(item.get("intent_id", "")) != intent_id:
            continue
        return dict(item)
    raise ValueError(f"intent_id is not present in active contract: {intent_id}")


def _manifest_solver_budget(
    contract: SearchContract, solver_budget: Dict[str, Any]
) -> Dict[str, Any]:
    policy = dict(contract.resource_policy)
    return {
        "max_time_sec": min(
            float(policy.get("max_time_sec", 1e-6)),
            float(solver_budget.get("max_time_sec", policy.get("max_time_sec", 1e-6))),
        ),
        "max_iters": min(
            int(policy.get("max_iters", 1)),
            int(solver_budget.get("max_iters", policy.get("max_iters", 1))),
        ),
    }


def _weights_with_defaults(
    names: Sequence[str],
    items: List[Dict[str, Any]],
    default: int,
    prefix: str,
    defaults: List[str],
) -> Dict[str, int]:
    del default, prefix, defaults
    selected = {str(item["name"]): int(item["score"]) for item in items}
    out: Dict[str, int] = {}
    for name in names:
        out[str(name)] = selected.get(str(name), 0)
    return out


def _nonzero_weights_have_llm_source(
    decision: Dict[str, Any], compiled: Dict[str, Any]
) -> bool:
    selected: set[tuple[str, str, str]] = set()
    mapping = (
        ("destroy_control", "operator_scores", "destroy", "operator_weights"),
        ("destroy_control", "signal_scores", "destroy", "signal_weights"),
        ("insertion_control", "operator_scores", "insertion", "operator_weights"),
        ("insertion_control", "task_signal_scores", "insertion", "task_signal_weights"),
        (
            "insertion_control",
            "position_signal_scores",
            "insertion",
            "position_signal_weights",
        ),
    )
    for control_key, score_key, compiled_key, weights_key in mapping:
        for item in (decision.get(control_key, {}) or {}).get(score_key, []) or []:
            if isinstance(item, dict) and int(item.get("score", 0) or 0) > 0:
                selected.add((compiled_key, weights_key, str(item.get("name", ""))))
    for compiled_key, weights_key in (
        ("destroy", "operator_weights"),
        ("destroy", "signal_weights"),
        ("insertion", "operator_weights"),
        ("insertion", "task_signal_weights"),
        ("insertion", "position_signal_weights"),
    ):
        for name, value in dict(
            (compiled.get(compiled_key, {}) or {}).get(weights_key, {}) or {}
        ).items():
            if int(value) > 0 and (compiled_key, weights_key, str(name)) not in selected:
                return False
    return True


def _names_from_space(
    action_space: Dict[str, Any],
    action_key: str,
    candidates: PublicCandidates,
    candidate_key: str,
    fallback: Sequence[str],
) -> List[str]:
    if action_space.get(action_key):
        return [
            str(item.get("name")) if isinstance(item, dict) else str(item)
            for item in action_space.get(action_key, [])
        ]
    return (
        list(candidates.names(candidate_key))
        if candidates is not None
        else list(fallback)
    )


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    position = max(0.0, min(1.0, q)) * (len(ordered) - 1)
    lo, hi = math.floor(position), math.ceil(position)
    return (
        ordered[lo]
        if lo == hi
        else ordered[lo] * (hi - position) + ordered[hi] * (position - lo)
    )


def _mean_nearest_neighbor_distance(
    instance: Instance, tasks: List[Task], rng: random.Random, sample: int
) -> float:
    if len(tasks) <= 1:
        return 0.0
    selected = tasks if sample >= len(tasks) else rng.sample(tasks, sample)
    return sum(
        min(
            instance.distance(task.loc, other.loc)
            for other in tasks
            if other.id != task.id
        )
        for task in selected
    ) / len(selected)


def _relaxation_scale_context(tasks: List[Task], agents: List[Agent]) -> Dict[str, Any]:
    time_ref = _quantile(
        [max(0.0, float(task.tw_end) - float(task.tw_start)) for task in tasks], 0.5
    )
    energy_ref = _quantile(
        [max(0.0, float(agent.init_energy)) for agent in agents], 0.5
    )
    return {
        "time_window_median_width": float(time_ref),
        "agent_energy_median": float(energy_ref),
    }


def _numericize(node: Any) -> Any:
    if isinstance(node, dict):
        return {str(key): _numericize(value) for key, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [_numericize(value) for value in node]
    if isinstance(node, (int, float)):
        return float(node) if isinstance(node, float) else int(node)
    return node


__all__ = [
    "QUALITY_METRICS",
    "SearchContract",
    "ContractProgress",
    "RuntimeControlManifest",
    "llm_solution_summary",
    "llm_instance_summary",
    "compile_global_objective",
    "compile_acceptance",
    "compile_solver_control",
    "feasibility_policy_from_manifest",
    "alns_policy_from_manifest",
    "insertion_policy_from_manifest",
    "compile_contract",
    "derive_solver_request",
    "solver_request_from_manifest",
]
