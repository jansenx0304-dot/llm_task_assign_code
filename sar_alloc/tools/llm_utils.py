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
    LANDSCAPE_METRIC_FIELDS,
    METRIC_DIRECTIONS,
    POLICY_BOUNDS,
    REPAIR_POSITION_METRIC_FIELDS,
    REPAIR_TASK_SELECTORS,
    SEARCH_DIAGNOSIS_FIELDS,
    LandscapeMetricPreferences,
    MetricPreference,
    PositionMetricPreferences,
    WeightedALNSPolicy,
    operator_score_to_prior,
    score_to_range,
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
        }

    max_layers = max(1, min(int(config.eval.objective_policy.max_layers), 5))
    if len(layers_raw) > max_layers:
        return {
            "ok": False,
            "error": f"objective_spec.layers must contain at most {max_layers} layers",
        }

    normalized: List[ObjectiveLayer] = []
    for item in layers_raw:
        if not isinstance(item, dict):
            return {"ok": False, "error": "objective_spec.layers entries must be objects"}

        name = str(item.get("name", "")).strip()
        metric = str(item.get("metric", "")).strip()
        direction = str(item.get("direction", "")).strip()
        if not name:
            return {"ok": False, "error": "objective layer name must be a non-empty string"}
        if metric not in _ALLOWED_OBJECTIVE_METRICS:
            return {"ok": False, "error": f"unknown objective metric: {metric}"}
        if direction not in ("min", "max"):
            return {"ok": False, "error": "objective layer direction must be min|max"}

        normalized.append(ObjectiveLayer(name=name, metric=metric, direction=direction))

    config.eval.objective_policy.layers = normalized
    return {
        "ok": True,
        "applied_layers": [
            {"name": layer.name, "metric": layer.metric, "direction": layer.direction}
            for layer in normalized
        ],
    }


def llm_compile_weighted_alns_policy(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Strictly validate and compile an LLM-provided run_alns policy.

    The compiler never fills missing operator weights, never clamps illegal
    numeric values, and never supplies acceptance defaults. Callers should
    surface the returned error directly.
    """
    if not isinstance(payload, dict):
        return _policy_error("action_payload must be an object")

    allowed_fields = {
        "search_diagnosis_scores",
        "destroy_operator_scores",
        "repair_operator_scores",
        "destroy_metric_preferences",
        "repair_task_metric_preferences",
        "repair_position_metric_preferences",
        "destroy_strength_score",
        "candidate_budget_score",
        "exploration_score",
        "acceptance",
        "accept_level",
        "reaction_factor",
        "prior_mix_lambda",
    }
    for key in sorted(str(key) for key in payload.keys()):
        if key not in allowed_fields:
            return _policy_error(f"unknown field 'action_payload.{key}'")
    for key in sorted(allowed_fields):
        if key not in payload:
            return _policy_error(f"missing field 'action_payload.{key}'")

    search_diagnosis_scores = _compile_required_int_score_map(
        raw_value=payload["search_diagnosis_scores"],
        allowed=SEARCH_DIAGNOSIS_FIELDS,
        field_name="search_diagnosis_scores",
    )
    if isinstance(search_diagnosis_scores, str):
        return _policy_error(search_diagnosis_scores)

    destroy_operator_scores = _compile_required_int_score_map(
        raw_value=payload["destroy_operator_scores"],
        allowed=DESTROY_CANDIDATE_GENERATORS,
        field_name="destroy_operator_scores",
    )
    if isinstance(destroy_operator_scores, str):
        return _policy_error(destroy_operator_scores)

    repair_operator_scores = _compile_required_int_score_map(
        raw_value=payload["repair_operator_scores"],
        allowed=REPAIR_TASK_SELECTORS,
        field_name="repair_operator_scores",
    )
    if isinstance(repair_operator_scores, str):
        return _policy_error(repair_operator_scores)

    destroy_metric_preferences = _compile_metric_preferences(
        raw_value=payload["destroy_metric_preferences"],
        metric_fields=LANDSCAPE_METRIC_FIELDS,
        field_name="destroy_metric_preferences",
        preferences_cls=LandscapeMetricPreferences,
    )
    if isinstance(destroy_metric_preferences, str):
        return _policy_error(destroy_metric_preferences)
    repair_task_metric_preferences = _compile_metric_preferences(
        raw_value=payload["repair_task_metric_preferences"],
        metric_fields=LANDSCAPE_METRIC_FIELDS,
        field_name="repair_task_metric_preferences",
        preferences_cls=LandscapeMetricPreferences,
    )
    if isinstance(repair_task_metric_preferences, str):
        return _policy_error(repair_task_metric_preferences)
    repair_position_metric_preferences = _compile_metric_preferences(
        raw_value=payload["repair_position_metric_preferences"],
        metric_fields=REPAIR_POSITION_METRIC_FIELDS,
        field_name="repair_position_metric_preferences",
        preferences_cls=PositionMetricPreferences,
    )
    if isinstance(repair_position_metric_preferences, str):
        return _policy_error(repair_position_metric_preferences)

    acceptance = payload["acceptance"]
    if not isinstance(acceptance, str):
        return _policy_error("field 'action_payload.acceptance' must be a string")
    if acceptance not in ACCEPTANCE_MODES:
        return _policy_error(
            f"field 'action_payload.acceptance' has illegal enum value '{acceptance}'"
        )

    scalars: Dict[str, float] = {}
    for field_name in ("accept_level", "reaction_factor", "prior_mix_lambda"):
        lower, upper = POLICY_BOUNDS[field_name]
        value = _strict_number(
            value=payload[field_name],
            field_name=f"action_payload.{field_name}",
            lower=lower,
            upper=upper,
        )
        if isinstance(value, str):
            return _policy_error(value)
        scalars[field_name] = value

    int_scores: Dict[str, int] = {}
    for field_name in ("destroy_strength_score", "candidate_budget_score", "exploration_score"):
        value = _strict_int_score(payload[field_name], f"action_payload.{field_name}")
        if isinstance(value, str):
            return _policy_error(value)
        int_scores[field_name] = value

    destroy_operator_priors = {
        name: operator_score_to_prior(score)
        for name, score in destroy_operator_scores.items()
    }
    repair_operator_priors = {
        name: operator_score_to_prior(score)
        for name, score in repair_operator_scores.items()
    }
    strength_ratio = score_to_range(
        int_scores["destroy_strength_score"],
        POLICY_BOUNDS["strength_ratio"][0],
        POLICY_BOUNDS["strength_ratio"][1],
    )
    exploration_rate = score_to_range(int_scores["exploration_score"], 0.02, 0.30)

    policy = WeightedALNSPolicy(
        search_diagnosis_scores=search_diagnosis_scores,
        destroy_operator_scores=destroy_operator_scores,
        repair_operator_scores=repair_operator_scores,
        destroy_metric_preferences=destroy_metric_preferences,
        repair_task_metric_preferences=repair_task_metric_preferences,
        repair_position_metric_preferences=repair_position_metric_preferences,
        destroy_strength_score=int_scores["destroy_strength_score"],
        candidate_budget_score=int_scores["candidate_budget_score"],
        exploration_score=int_scores["exploration_score"],
        destroy_operator_priors=destroy_operator_priors,
        repair_operator_priors=repair_operator_priors,
        strength_ratio=strength_ratio,
        exploration_rate=exploration_rate,
        acceptance=acceptance,
        accept_level=scalars["accept_level"],
        reaction_factor=scalars["reaction_factor"],
        prior_mix_lambda=scalars["prior_mix_lambda"],
    )

    return {"ok": True, "policy": policy, "applied": policy.as_dict()}


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


def _policy_error(message: str) -> Dict[str, Any]:
    return {"ok": False, "error": message, "applied": {}}


def _compile_required_int_score_map(
    *,
    raw_value: Any,
    allowed: Tuple[str, ...],
    field_name: str,
) -> Dict[str, int] | str:
    if not isinstance(raw_value, dict):
        return f"field 'action_payload.{field_name}' must be an object"

    allowed_set = {str(name) for name in allowed}
    for key in sorted(str(key) for key in raw_value.keys()):
        if key not in allowed_set:
            return f"unknown field 'action_payload.{field_name}.{key}'"
    for key in allowed:
        if key not in raw_value:
            return f"missing field 'action_payload.{field_name}.{key}'"

    compiled: Dict[str, int] = {}
    for key in allowed:
        value = _strict_int_score(raw_value[key], f"action_payload.{field_name}.{key}")
        if isinstance(value, str):
            return value
        compiled[str(key)] = int(value)
    return compiled


def _compile_metric_preferences(
    *,
    raw_value: Any,
    metric_fields: Tuple[str, ...],
    field_name: str,
    preferences_cls: type[LandscapeMetricPreferences] | type[PositionMetricPreferences],
) -> LandscapeMetricPreferences | PositionMetricPreferences | str:
    if not isinstance(raw_value, dict):
        return f"field 'action_payload.{field_name}' must be an object"

    compiled: Dict[str, MetricPreference] = {}
    allowed_fields = set(metric_fields)
    for key in sorted(str(key) for key in raw_value.keys()):
        if key not in allowed_fields:
            return f"unknown field 'action_payload.{field_name}.{key}'"
    for name in metric_fields:
        if name not in raw_value:
            return f"missing field 'action_payload.{field_name}.{name}'"
        item = raw_value[name]
        if not isinstance(item, dict):
            return f"field 'action_payload.{field_name}.{name}' must be an object"
        item_keys = sorted(str(key) for key in item.keys())
        if item_keys != ["direction", "score"]:
            extra = [key for key in item_keys if key not in {"score", "direction"}]
            if extra:
                return f"unknown field 'action_payload.{field_name}.{name}.{extra[0]}'"
            missing = [key for key in ("score", "direction") if key not in item]
            return f"missing field 'action_payload.{field_name}.{name}.{missing[0]}'"
        score = _strict_int_score(item["score"], f"action_payload.{field_name}.{name}.score")
        if isinstance(score, str):
            return score
        direction = item["direction"]
        if not isinstance(direction, str):
            return f"field 'action_payload.{field_name}.{name}.direction' must be a string"
        if direction not in METRIC_DIRECTIONS:
            return f"field 'action_payload.{field_name}.{name}.direction' has illegal enum value '{direction}'"
        compiled[str(name)] = MetricPreference(score=int(score), direction=str(direction))
    return preferences_cls(**compiled)


def _strict_int_score(value: Any, field_name: str) -> int | str:
    if isinstance(value, bool) or not isinstance(value, int):
        return f"field '{field_name}' must be an integer"
    if int(value) < 0 or int(value) > 10:
        return f"field '{field_name}' must be in [0, 10]"
    return int(value)


def _strict_number(
    *,
    value: Any,
    lower: float,
    upper: float,
    field_name: str,
) -> float | str:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return f"field '{field_name}' must be numeric"
    numeric = float(value)
    if not math.isfinite(numeric):
        return f"field '{field_name}' must be finite"
    if numeric < float(lower) or numeric > float(upper):
        return f"field '{field_name}' must be in [{lower}, {upper}]"
    return numeric


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
