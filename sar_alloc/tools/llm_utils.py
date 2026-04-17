from __future__ import annotations

"""Utilities that expose controlled problem/solver views to the LLM layer."""

import math
import random
from typing import Any, Dict, List, Optional, Tuple

from ..config import Config, ObjectiveLayer
from ..evaluator import evaluate
from ..models import Agent, Instance, Task
from ..operators import (
    ACCEPTANCE_MODES,
    DESTROY_CANDIDATE_GENERATORS,
    METRIC_FIELDS,
    METRIC_WEIGHT_BOUNDS,
    OPERATOR_PRIOR_BOUNDS,
    POLICY_BOUNDS,
    REPAIR_POSITION_SELECTORS,
    REPAIR_TASK_SELECTORS,
    MetricWeights,
    WeightedALNSPolicy,
)
from ..schemas import SCHEMA_CONSTRAINTS
from ..solution import AssignmentSolution


_EPS = 1e-9
_OPERATOR_INTENT_FIELDS: Tuple[str, ...] = tuple(
    str(name)
    for name in (SCHEMA_CONSTRAINTS.get("next_action", {}).get("operator_intent_fields", []) or [])
)
_OPERATOR_INTENT_MAX_WORDS = int(
    SCHEMA_CONSTRAINTS.get("next_action", {}).get("operator_intent_max_words", 12) or 12
)


def llm_solution_summary(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> Dict[str, Any]:
    ev = evaluate(solution, instance, config, update_solution_schedule=update_solution_schedule)
    layers = [
        {
            "name": layer.name,
            "metric": layer.metric,
            "direction": layer.direction,
        }
        for layer in config.eval.objective_policy.layers[: config.eval.objective_policy.max_layers]
        if layer.metric
    ]
    metrics = {
        name: float(ev.metrics.get(name, 0.0))
        for name in (
            "violation_total",
            "missed_priority",
            "unassigned_count",
            "energy_total",
            "total_distance",
            "makespan",
        )
    }
    return {
        "is_feasible": bool(ev.is_feasible),
        "lex_key": list(ev.lex_key or ()),
        "metrics": metrics,
        "objective_layers": layers,
    }


def llm_instance_summary(
    instance: Instance,
    rng_seed: int = 0,
) -> Dict[str, Any]:
    rng = random.Random(rng_seed)
    tasks = list(instance.tasks)
    agents = list(instance.agents)

    if not tasks or not agents:
        return {
            "version": 4,
            "n_tasks": len(tasks),
            "n_agents": len(agents),
            "skills": {"uncoverable_task_frac": 0.0, "hard_tasks_frac": 0.0},
            "time_window_risk": {"negative_slack_frac_lb": 0.0},
            "energy_risk": {"energy_tight_frac_lb": 0.0},
            "spatial": {"cluster_strength": 0.0, "radius95_to_depot": 0.0},
        }

    depot_loc = instance.depot.loc

    def can_do(agent: Agent, task: Task) -> bool:
        return set(task.skill_req).issubset(set(agent.skills))

    uncoverable = 0
    hard_tasks = 0
    for task in tasks:
        feasible_agents = [agent for agent in agents if can_do(agent, task)]
        if not feasible_agents:
            uncoverable += 1
        if len(feasible_agents) <= 1:
            hard_tasks += 1

    negative_slack = 0
    for task in tasks:
        best_arrival = min(
            float(instance.travel_time(agent, depot_loc, task.loc))
            for agent in agents
        )
        if max(float(task.tw_start), best_arrival) > float(task.tw_end) + _EPS:
            negative_slack += 1

    tight_energy = 0
    for task in tasks:
        best_ratio: Optional[float] = None
        for agent in agents:
            if not can_do(agent, task) or float(agent.init_energy) <= _EPS:
                continue
            service_energy = sum(
                float(task.service_time) * float(agent.skill_energy_rate.get(skill, 1.0))
                for skill in task.skill_req
            )
            travel_lb = float(agent.travel_energy_rate) * float(instance.distance(depot_loc, task.loc)) * 2.0
            ratio = (service_energy + travel_lb) / float(agent.init_energy)
            if best_ratio is None or ratio < best_ratio:
                best_ratio = ratio
        if best_ratio is not None and best_ratio > 0.85:
            tight_energy += 1

    d_to_depot = [float(instance.distance(depot_loc, task.loc)) for task in tasks]
    mean_dist = sum(d_to_depot) / max(1, len(d_to_depot))
    radius95 = _quantile(d_to_depot, 0.95)

    sample_size = max(2, min(len(tasks), int(14.0 * math.sqrt(len(tasks)))))
    pool_size = max(sample_size, min(len(tasks), int(40.0 * math.sqrt(len(tasks)))))
    nn_dist = _mean_nearest_neighbor_distance(instance, tasks, rng, sample_size, pool_size)
    cluster_strength = 0.0 if mean_dist <= _EPS else max(0.0, min(1.0, 1.0 - (nn_dist / (mean_dist + _EPS))))

    return {
        "version": 4,
        "n_tasks": len(tasks),
        "n_agents": len(agents),
        "skills": {
            "uncoverable_task_frac": uncoverable / max(1, len(tasks)),
            "hard_tasks_frac": hard_tasks / max(1, len(tasks)),
        },
        "time_window_risk": {
            "negative_slack_frac_lb": negative_slack / max(1, len(tasks)),
        },
        "energy_risk": {
            "energy_tight_frac_lb": tight_energy / max(1, len(tasks)),
        },
        "spatial": {
            "cluster_strength": float(cluster_strength),
            "radius95_to_depot": float(radius95),
        },
    }


_ALLOWED_OBJECTIVE_METRICS: Dict[str, str] = {
    "violation_total": "Total constraint violation (0 means feasible).",
    "unassigned_count": "Number of unassigned tasks.",
    "missed_priority": "Sum of priorities of unassigned tasks.",
    "energy_total": "Total energy used.",
    "total_distance": "Total travel distance.",
    "makespan": "Max route completion time over agents.",
}


def llm_available_metrics() -> Dict[str, Any]:
    return {
        "metrics": [
            {"name": name, "desc": desc}
            for name, desc in _ALLOWED_OBJECTIVE_METRICS.items()
        ],
    }


def llm_apply_objective(config: Config, objective_spec: Dict[str, Any]) -> Dict[str, Any]:
    layers_raw = objective_spec.get("layers")
    if not isinstance(layers_raw, list) or not layers_raw:
        return {
            "ok": False,
            "error": "objective_spec.layers must be a non-empty list",
            "allowed_metrics": sorted(_ALLOWED_OBJECTIVE_METRICS),
        }

    normalized: List[ObjectiveLayer] = []
    dropped: List[Dict[str, Any]] = []
    max_layers = max(1, min(int(config.eval.objective_policy.max_layers), 5))

    for index, item in enumerate(layers_raw):
        if len(normalized) >= max_layers:
            break
        if isinstance(item, str):
            metric = item
            direction = "min"
            name = item
        elif isinstance(item, dict):
            metric = str(item.get("metric", ""))
            direction = str(item.get("direction", "min"))
            name = str(item.get("name", metric or f"layer_{index + 1}"))
        else:
            dropped.append({"index": index, "reason": "layer must be string or object"})
            continue

        if metric not in _ALLOWED_OBJECTIVE_METRICS:
            dropped.append({"index": index, "reason": "unknown metric", "metric": metric})
            continue
        if direction not in ("min", "max"):
            dropped.append({"index": index, "reason": "direction must be min|max", "direction": direction})
            continue

        normalized.append(ObjectiveLayer(name=name, metric=metric, direction=direction))

    if not normalized:
        return {
            "ok": False,
            "error": "No valid objective layers after validation",
            "dropped_layers": dropped,
            "allowed_metrics": sorted(_ALLOWED_OBJECTIVE_METRICS),
        }

    config.eval.objective_policy.layers = normalized
    return {
        "ok": True,
        "applied_layers": [
            {"name": layer.name, "metric": layer.metric, "direction": layer.direction}
            for layer in normalized
        ],
        "dropped_layers": dropped,
    }


def llm_compile_weighted_alns_policy(config: Config, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and compile a strict weighted-ALNS action payload."""
    defaults = config.solver.weighted_alns
    raw = dict(payload or {}) if isinstance(payload, dict) else {}
    dropped: List[Dict[str, Any]] = []
    validation_errors: List[str] = []

    allowed_fields = {
        "destroy_generator_priors",
        "repair_task_selector_priors",
        "repair_position_selector",
        "remove_metric_weights",
        "reinsert_metric_weights",
        "insert_metric_weights",
        "strength_ratio",
        "acceptance",
        "accept_level",
        "reaction_factor",
        "prior_mix_lambda",
    }
    for key in raw.keys():
        if key not in allowed_fields:
            dropped.append({"field": key, "reason": "unknown field"})
            validation_errors.append(f"unknown field '{key}'")

    destroy_generator_priors = _compile_operator_prior_map(
        raw_value=raw.get("destroy_generator_priors"),
        defaults=defaults.destroy_generator_priors,
        allowed=DESTROY_CANDIDATE_GENERATORS,
        field_name="destroy_generator_priors",
        dropped=dropped,
    )
    repair_task_selector_priors = _compile_operator_prior_map(
        raw_value=raw.get("repair_task_selector_priors"),
        defaults=defaults.repair_task_selector_priors,
        allowed=REPAIR_TASK_SELECTORS,
        field_name="repair_task_selector_priors",
        dropped=dropped,
    )
    repair_position_selector = _pick_enum(
        raw_value=raw.get("repair_position_selector"),
        default=defaults.repair_position_selector,
        allowed=REPAIR_POSITION_SELECTORS,
        field_name="repair_position_selector",
        dropped=dropped,
    )
    acceptance = _pick_enum(
        raw_value=raw.get("acceptance"),
        default=defaults.acceptance,
        allowed=ACCEPTANCE_MODES,
        field_name="acceptance",
        dropped=dropped,
    )
    remove_metric_weights = _compile_metric_weight_map(
        raw_value=raw.get("remove_metric_weights"),
        field_name="remove_metric_weights",
        dropped=dropped,
        validation_errors=validation_errors,
    )
    reinsert_metric_weights = _compile_metric_weight_map(
        raw_value=raw.get("reinsert_metric_weights"),
        field_name="reinsert_metric_weights",
        dropped=dropped,
        validation_errors=validation_errors,
    )
    insert_metric_weights = _compile_metric_weight_map(
        raw_value=raw.get("insert_metric_weights"),
        field_name="insert_metric_weights",
        dropped=dropped,
        validation_errors=validation_errors,
    )
    if (
        remove_metric_weights is None
        or reinsert_metric_weights is None
        or insert_metric_weights is None
        or validation_errors
    ):
        return {
            "ok": False,
            "error": validation_errors[0] if validation_errors else "invalid metric weight maps",
            "applied": {},
            "dropped": dropped,
        }

    policy = WeightedALNSPolicy(
        destroy_generator_priors=destroy_generator_priors,
        repair_task_selector_priors=repair_task_selector_priors,
        repair_position_selector=repair_position_selector,
        remove_metric_weights=remove_metric_weights,
        reinsert_metric_weights=reinsert_metric_weights,
        insert_metric_weights=insert_metric_weights,
        strength_ratio=_clamp_number(
            raw_value=raw.get("strength_ratio", defaults.strength_ratio),
            default=defaults.strength_ratio,
            lower=POLICY_BOUNDS["strength_ratio"][0],
            upper=POLICY_BOUNDS["strength_ratio"][1],
            field_name="strength_ratio",
            dropped=dropped,
        ),
        acceptance=acceptance,
        accept_level=_clamp_number(
            raw_value=raw.get("accept_level", defaults.accept_level),
            default=defaults.accept_level,
            lower=POLICY_BOUNDS["accept_level"][0],
            upper=POLICY_BOUNDS["accept_level"][1],
            field_name="accept_level",
            dropped=dropped,
        ),
        reaction_factor=_clamp_number(
            raw_value=raw.get("reaction_factor", defaults.reaction_factor),
            default=defaults.reaction_factor,
            lower=POLICY_BOUNDS["reaction_factor"][0],
            upper=POLICY_BOUNDS["reaction_factor"][1],
            field_name="reaction_factor",
            dropped=dropped,
        ),
        prior_mix_lambda=_clamp_number(
            raw_value=raw.get("prior_mix_lambda", defaults.prior_mix_lambda),
            default=defaults.prior_mix_lambda,
            lower=POLICY_BOUNDS["prior_mix_lambda"][0],
            upper=POLICY_BOUNDS["prior_mix_lambda"][1],
            field_name="prior_mix_lambda",
            dropped=dropped,
        ),
    )

    return {
        "ok": True,
        "policy": policy,
        "applied": policy.as_dict(),
        "dropped": dropped,
    }


def llm_parse_operator_intent(raw: Any) -> Dict[str, Any]:
    dropped: List[Dict[str, Any]] = []
    validation_errors: List[str] = []
    if raw is None:
        return {
            "ok": False,
            "error": "missing field 'operator_intent'",
            "applied": None,
            "dropped": [{"field": "operator_intent", "reason": "missing field"}],
        }
    if not isinstance(raw, dict):
        return {
            "ok": False,
            "error": "field 'operator_intent' must be an object",
            "applied": None,
            "dropped": [{"field": "operator_intent", "reason": "must be an object"}],
        }

    compiled: Dict[str, str] = {}
    allowed_fields = set(_OPERATOR_INTENT_FIELDS)
    for key in raw.keys():
        field_name = str(key)
        if field_name not in allowed_fields:
            dropped.append({"field": f"operator_intent.{field_name}", "reason": "unknown field"})
            validation_errors.append(f"unknown field 'operator_intent.{field_name}'")

    for field_name in _OPERATOR_INTENT_FIELDS:
        if field_name not in raw:
            dropped.append({"field": f"operator_intent.{field_name}", "reason": "missing field"})
            validation_errors.append(f"missing field 'operator_intent.{field_name}'")
            continue
        value = raw.get(field_name)
        if not isinstance(value, str):
            dropped.append({"field": f"operator_intent.{field_name}", "reason": "must be a string"})
            validation_errors.append(f"field 'operator_intent.{field_name}' must be a string")
            continue
        normalized = " ".join(value.strip().split())
        if not normalized:
            dropped.append({"field": f"operator_intent.{field_name}", "reason": "must be a non-empty string"})
            validation_errors.append(f"field 'operator_intent.{field_name}' must be a non-empty string")
            continue
        if len(normalized.split()) > _OPERATOR_INTENT_MAX_WORDS:
            dropped.append(
                {
                    "field": f"operator_intent.{field_name}",
                    "reason": f"must be at most {_OPERATOR_INTENT_MAX_WORDS} words",
                }
            )
            validation_errors.append(
                f"field 'operator_intent.{field_name}' must be at most {_OPERATOR_INTENT_MAX_WORDS} words"
            )
            continue
        compiled[field_name] = normalized

    if len(compiled) != len(_OPERATOR_INTENT_FIELDS) or validation_errors:
        return {
            "ok": False,
            "error": validation_errors[0] if validation_errors else "invalid operator_intent",
            "applied": None,
            "dropped": dropped,
        }
    return {
        "ok": True,
        "operator_intent": compiled,
        "applied": dict(compiled),
        "dropped": dropped,
    }


def format_available_metrics(spec: Dict[str, Any]) -> str:
    lines = ["Available metrics:"]
    for item in spec.get("metrics", []) or []:
        lines.append(f"- {item.get('name', '')}: {item.get('desc', '')}")
    return "\n".join(lines).strip()


def format_instance_summary(summary: Dict[str, Any]) -> str:
    lines = [
        f"- Number of tasks: {summary.get('n_tasks', 0)}",
        f"- Number of agents: {summary.get('n_agents', 0)}",
        "",
        "Skill coverage:",
        f"- Tasks no agent can do: {summary.get('skills', {}).get('uncoverable_task_frac', 0.0):.2f}",
        f"- Bottleneck tasks (<=1 capable agent): {summary.get('skills', {}).get('hard_tasks_frac', 0.0):.2f}",
        "",
        "Time-window risk:",
        f"- Optimistically infeasible tasks: {summary.get('time_window_risk', {}).get('negative_slack_frac_lb', 0.0):.2f}",
        "",
        "Energy risk:",
        f"- Tight-energy tasks: {summary.get('energy_risk', {}).get('energy_tight_frac_lb', 0.0):.2f}",
        "",
        "Spatial structure:",
        f"- Cluster strength: {summary.get('spatial', {}).get('cluster_strength', 0.0):.2f}",
        f"- 95th percentile distance to depot: {summary.get('spatial', {}).get('radius95_to_depot', 0.0):.2f}",
    ]
    return "\n".join(lines).strip()


def format_solution_summary(summary: Dict[str, Any]) -> str:
    lines = [f"- Feasible: {bool(summary.get('is_feasible', False))}"]
    lines.append(f"- Lex key: {summary.get('lex_key', [])}")
    lines.append("- Metrics:")
    for key, value in (summary.get("metrics", {}) or {}).items():
        lines.append(f"  {key}: {float(value):.4f}")
    return "\n".join(lines)


def _pick_enum(
    *,
    raw_value: Any,
    default: str,
    allowed: Tuple[str, ...],
    field_name: str,
    dropped: List[Dict[str, Any]],
) -> str:
    value = str(raw_value or default).strip()
    if value in allowed:
        return value
    dropped.append({"field": field_name, "reason": f"must be one of {list(allowed)}", "value": str(raw_value)})
    return str(default)


def _compile_operator_prior_map(
    *,
    raw_value: Any,
    defaults: Dict[str, float],
    allowed: Tuple[str, ...],
    field_name: str,
    dropped: List[Dict[str, Any]],
) -> Dict[str, float]:
    lo, hi = OPERATOR_PRIOR_BOUNDS
    prior_raw = raw_value
    if prior_raw is None:
        prior_raw = {}
    if not isinstance(prior_raw, dict):
        dropped.append({"field": field_name, "reason": "must be an object"})
        prior_raw = {}

    compiled: Dict[str, float] = {}
    for name in allowed:
        compiled[str(name)] = _clamp_number(
            raw_value=prior_raw.get(name, defaults.get(name, 1.0)),
            default=defaults.get(name, 1.0),
            lower=lo,
            upper=hi,
            field_name=f"{field_name}.{name}",
            dropped=dropped,
        )

    for name in prior_raw.keys():
        if str(name) not in allowed:
            dropped.append({"field": f"{field_name}.{name}", "reason": "unknown field"})
    return compiled


def _compile_metric_weight_map(
    *,
    raw_value: Any,
    field_name: str,
    dropped: List[Dict[str, Any]],
    validation_errors: List[str],
) -> Optional[MetricWeights]:
    if not isinstance(raw_value, dict):
        dropped.append({"field": field_name, "reason": "must be an object"})
        validation_errors.append(f"field '{field_name}' must be an object")
        return None

    compiled: Dict[str, float] = {}
    metric_fields = set(METRIC_FIELDS)
    for name in raw_value.keys():
        normalized = str(name)
        if normalized not in metric_fields:
            dropped.append({"field": f"{field_name}.{normalized}", "reason": "unknown field"})
            validation_errors.append(f"unknown field '{field_name}.{normalized}'")

    for name in METRIC_FIELDS:
        if name not in raw_value:
            dropped.append({"field": f"{field_name}.{name}", "reason": "missing field"})
            validation_errors.append(f"missing field '{field_name}.{name}'")
            continue
        raw_metric_value = raw_value.get(name)
        if raw_metric_value is None or isinstance(raw_metric_value, bool):
            dropped.append({"field": f"{field_name}.{name}", "reason": "must be numeric", "value": repr(raw_metric_value)})
            validation_errors.append(f"field '{field_name}.{name}' must be numeric")
            continue
        try:
            numeric_value = float(raw_metric_value)
        except Exception:
            dropped.append({"field": f"{field_name}.{name}", "reason": "must be numeric", "value": repr(raw_metric_value)})
            validation_errors.append(f"field '{field_name}.{name}' must be numeric")
            continue

        lower, upper = METRIC_WEIGHT_BOUNDS[name]
        if numeric_value < lower or numeric_value > upper:
            dropped.append(
                {
                    "field": f"{field_name}.{name}",
                    "reason": f"clamped to [{lower}, {upper}]",
                    "value": numeric_value,
                }
            )
        compiled[name] = max(float(lower), min(float(upper), numeric_value))

    if len(compiled) != len(METRIC_FIELDS) or validation_errors:
        return None
    return MetricWeights(**compiled)


def _clamp_number(
    *,
    raw_value: Any,
    default: float,
    lower: float,
    upper: float,
    field_name: str,
    dropped: List[Dict[str, Any]],
) -> float:
    try:
        value = float(raw_value)
    except Exception:
        dropped.append({"field": field_name, "reason": "must be numeric", "value": repr(raw_value)})
        return float(default)
    if value < lower or value > upper:
        dropped.append({"field": field_name, "reason": f"clamped to [{lower}, {upper}]", "value": value})
    return max(float(lower), min(float(upper), value))


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(x) for x in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = max(0.0, min(1.0, float(q))) * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _mean_nearest_neighbor_distance(
    instance: Instance,
    tasks: List[Task],
    rng: random.Random,
    sample: int,
    pool: int,
) -> float:
    if len(tasks) <= 1:
        return 0.0

    locs = [task.loc for task in tasks]

    def dist(i: int, j: int) -> float:
        return float(instance.distance(locs[i], locs[j]))

    if len(tasks) <= 800:
        best: List[float] = []
        for i in range(len(tasks)):
            nearest = min(dist(i, j) for j in range(len(tasks)) if j != i)
            best.append(nearest)
        return sum(best) / max(1, len(best))

    pool_idx = list(range(len(tasks)))
    rng.shuffle(pool_idx)
    pool_idx = pool_idx[: max(2, min(pool, len(tasks)))]
    sample_idx = list(pool_idx[: max(2, min(sample, len(pool_idx)) )])

    best = []
    for i in sample_idx:
        nearest = min(dist(i, j) for j in pool_idx if j != i)
        best.append(nearest)
    return sum(best) / max(1, len(best))
