"""LLM output schemas and public action-space enumerations."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Mapping

from .operators.types import (
    ACCEPTANCE_MODES,
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
)

QUALITY_METRICS = (
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance",
)
CONSTRAINT_METRICS = (
    "violation_total",
    "violation_capability",
    "violation_time_window",
    "violation_energy",
    "recoverable_violation_total",
    "unrecoverable_violation_total",
)
STAGE_TYPES = ("initial_construction", "alns_search", "recovery", "final_refinement")
FEASIBILITY_MODES = ("strict", "relaxed_recoverable", "recovery_only")
RELAXABLE_VIOLATION_TYPES = ("time_window", "energy")
STEP_BASIS_NAMES = {
    "run_context": (
        "observation_id",
        "phase",
        "instance",
        "step_index",
        "stage_id",
    ),
    "active_stage": (
        "stage_id",
        "stage_type",
        "objective_layers",
        "target_intents",
        "feasibility_policy",
        "protected_metrics",
        "protected_metric_baseline",
        "resource_policy",
        "progress",
        "remaining",
    ),
    "execution_state": (
        "hard_executable_actions",
        "hard_inexecutable_actions",
        "working_solution_exists",
        "remaining_stage_resources",
        "remaining_global_resources",
    ),
    "solution_evidence": (
        "working_is_feasible",
        "best_feasible_exists",
        "missed_priority",
        "unassigned_count",
        "energy_total",
        "total_distance",
        "makespan",
        "route_balance",
        "feasibility_summary",
    ),
    "destroy_facts": (
        "removable_task_count",
        "non_empty_route_count",
        "route_len_distribution",
        "route_cost_distribution",
        "operator_candidate_counts",
    ),
    "insertion_facts": (
        "unassigned_task_count",
        "unassigned_task_ids",
        "candidate_position_count_distribution",
        "feasible_position_count_distribution",
        "unassigned_task_facts",
        "hard_failure_counts",
        "truncation",
    ),
    "targetable_evidence": (
        "visible_task_ids",
        "visible_agent_ids",
        "target_catalog",
    ),
    "control_catalog": (
        "insertion_operators",
        "insertion_task_signals",
        "insertion_position_signals",
        "destroy_operators",
        "destroy_signals",
        "acceptance_modes",
    ),
    "recent_records": (
        "recent_actions",
        "recent_quality_delta",
        "recent_acceptance",
    ),
    "runtime_feedback": (
        "last_result",
        "last_action",
        "last_quality_delta",
        "last_accepted",
        "last_protected_passed",
        "last_trace_counts",
    ),
}
SUPERVISOR_BASIS_NAMES = {
    "run_context": (
        "observation_id",
        "phase",
        "instance",
        "remaining_global_resources",
    ),
    "problem_profile": (
        "num_tasks",
        "num_agents",
        "priority_mass",
        "high_priority_task_count",
        "zero_capable_task_count",
        "static_capability_scarce_task_count",
        "time_window_negative_slack_frac_lb",
        "static_capable_count_distribution",
        "spatial",
    ),
    "solution_state": (
        "working_is_feasible",
        "best_feasible_exists",
        "missed_priority",
        "unassigned_count",
        "energy_total",
        "total_distance",
        "makespan",
        "route_balance",
        "feasibility_summary",
    ),
    "recent_records": (
        "recent_actions",
        "recent_quality",
        "recent_completion",
    ),
    "action_space": (
        "next_stage_resource_limits",
        "stage_types",
        "objective_metrics",
        "feasibility_modes",
        "relaxable_violation_types",
    ),
    "completed_stage": (
        "stage_id",
        "stage_type",
        "objective_layers",
        "target_intents",
        "feasibility_policy",
        "protected_metrics",
        "resource_policy",
        "progress",
        "remaining",
    ),
    "completed_result": (
        "completed",
        "status",
        "reason",
    ),
}


def build_action_space(instance: Any | None = None, config: Any | None = None) -> Dict[str, Any]:
    del instance, config
    return {
        "actions": ["construct_initial", "run_alns", "request_supervisor_review"],
        "supervisor_actions": ["issue_stage", "stop_run"],
        "stage_types": list(STAGE_TYPES),
        "objective_metrics": list(QUALITY_METRICS),
        "feasibility_modes": list(FEASIBILITY_MODES),
        "relaxable_violation_types": list(RELAXABLE_VIOLATION_TYPES),
        "insertion_operators": list(INSERTION_OPERATOR_NAMES),
        "insertion_task_signals": list(INSERTION_TASK_SIGNAL_NAMES),
        "insertion_position_signals": list(INSERTION_POSITION_SIGNAL_NAMES),
        "destroy_operators": list(DESTROY_OPERATOR_NAMES),
        "destroy_signals": list(DESTROY_SIGNAL_NAMES),
        "acceptance_modes": list(ACCEPTANCE_MODES),
    }


def schema_text(schema: Dict[str, Any]) -> str:
    return json.dumps(schema, ensure_ascii=False, indent=2)


def supervisor_schema(phase: str, action_space: Mapping[str, Any]) -> Dict[str, Any]:
    """Schema for supervisor kickoff/review decisions."""
    space = dict(action_space or {})
    stage_types = _values(space, "stage_types", STAGE_TYPES)
    if phase == "kickoff":
        stage_types = [name for name in stage_types if name == "initial_construction"]
    metrics = _values(space, "objective_metrics", QUALITY_METRICS)
    feasibility_modes = _values(space, "feasibility_modes", FEASIBILITY_MODES)
    relaxable = _values(space, "relaxable_violation_types", RELAXABLE_VIOLATION_TYPES)
    resource_limits = dict(space.get("next_stage_resource_limits", {}) or {})

    stage = _stage_schema(stage_types, metrics, feasibility_modes, relaxable)
    _apply_resource_limits(stage, resource_limits)
    issue = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "const": "issue_stage"},
            "decision_evidence": _decision_evidence_schema(SUPERVISOR_BASIS_NAMES, metrics),
            "global_objective": _global_objective_schema(metrics),
            "next_stage": stage,
        },
        "required": ["action", "decision_evidence", "global_objective", "next_stage"],
        "additionalProperties": False,
    }
    stop = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "const": "stop_run"},
            "decision_evidence": _decision_evidence_schema(SUPERVISOR_BASIS_NAMES, metrics),
            "stop_explanation": {"type": "string"},
        },
        "required": ["action", "decision_evidence", "stop_explanation"],
        "additionalProperties": False,
    }
    branches = [issue] if phase == "kickoff" else [issue, stop]
    if _no_stage_budget(resource_limits) and phase != "kickoff":
        branches = [stop]
    return {
        "type": "object",
        "properties": {"supervisor_decision": {"oneOf": branches}},
        "required": ["supervisor_decision"],
        "additionalProperties": False,
    }


def step_schema(action_space: Mapping[str, Any], active_stage: Mapping[str, Any]) -> Dict[str, Any]:
    """Schema for one step-agent decision under the active stage."""
    space = dict(action_space or {})
    allowed_actions = _values(space, "hard_executable_actions", space.get("actions", []))
    if not allowed_actions:
        allowed_actions = ["request_supervisor_review"]
    intent_ids = [
        str(item["intent_id"])
        for item in active_stage.get("target_intents", []) or []
        if isinstance(item, Mapping) and item.get("intent_id")
    ]
    branches = []
    if "construct_initial" in allowed_actions:
        branches.append(
            _step_action_schema(
                "construct_initial",
                intent_ids,
                insertion=True,
                destroy=False,
                acceptance=False,
                action_space=space,
            )
        )
    if "run_alns" in allowed_actions:
        branches.append(
            _step_action_schema(
                "run_alns",
                intent_ids,
                insertion=True,
                destroy=True,
                acceptance=True,
                action_space=space,
            )
        )
    if "request_supervisor_review" in allowed_actions:
        branches.append(_review_request_schema())
    return {
        "type": "object",
        "properties": {"step_decision": {"oneOf": branches}},
        "required": ["step_decision"],
        "additionalProperties": False,
    }


def _global_objective_schema(metrics: Iterable[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "objective_layers": {
                "type": "array",
                "minItems": 1,
                "maxItems": 4,
                "items": {"type": "string", "enum": list(metrics)},
            }
        },
        "required": ["objective_layers"],
        "additionalProperties": False,
    }


def _stage_schema(
    stage_types: Iterable[str],
    metrics: Iterable[str],
    feasibility_modes: Iterable[str],
    relaxable: Iterable[str],
) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "stage_type": {"type": "string", "enum": list(stage_types)},
            "objective_layers": {
                "type": "array",
                "minItems": 1,
                "maxItems": 4,
                "items": {"type": "string", "enum": list(metrics)},
            },
            "feasibility_control": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": list(feasibility_modes)},
                    "relaxation_ratios": {
                        "type": "array",
                        "maxItems": 2,
                        "items": {
                            "type": "object",
                            "properties": {
                                "violation_type": {"type": "string", "enum": list(relaxable)},
                                "max_ratio": {"type": "number", "minimum": 0.0, "maximum": 0.3},
                            },
                            "required": ["violation_type", "max_ratio"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["mode", "relaxation_ratios"],
                "additionalProperties": False,
            },
            "target_intents": {
                "type": "array",
                "minItems": 1,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "properties": {
                        "intent_id": {"type": "string"},
                        "intent_type": {
                            "type": "string",
                            "enum": ["construction", "recovery", "improvement", "diversification", "review"],
                        },
                        "rationale": {"type": "string"},
                    },
                    "required": ["intent_id", "intent_type", "rationale"],
                    "additionalProperties": False,
                },
            },
            "protected_metrics": {
                "type": "array",
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string", "enum": list(metrics)},
                        "max_worsen": {"type": "number", "minimum": 0.0},
                    },
                    "required": ["metric", "max_worsen"],
                    "additionalProperties": False,
                },
            },
            "resource_policy": {
                "type": "object",
                "properties": {
                    "min_actions": {"type": "integer", "minimum": 1},
                    "max_actions": {"type": "integer", "minimum": 1},
                    "max_iters": {"type": "integer", "minimum": 1},
                    "max_time_sec": {"type": "number", "exclusiveMinimum": 0},
                    "require_feasible": {"type": "boolean"},
                    "metric_thresholds": {
                        "type": "object",
                        "additionalProperties": {"type": "number"},
                    },
                },
                "required": ["min_actions", "max_actions", "max_iters", "max_time_sec", "require_feasible", "metric_thresholds"],
                "additionalProperties": False,
            },
        },
        "required": [
            "stage_type",
            "objective_layers",
            "feasibility_control",
            "target_intents",
            "protected_metrics",
            "resource_policy",
        ],
        "additionalProperties": False,
    }


def _step_action_schema(
    action: str,
    intent_ids: Iterable[str],
    *,
    insertion: bool,
    destroy: bool,
    acceptance: bool,
    action_space: Mapping[str, Any],
) -> Dict[str, Any]:
    properties: Dict[str, Any] = {
        "action": {"type": "string", "const": action},
        "decision_evidence": _decision_evidence_schema(STEP_BASIS_NAMES, QUALITY_METRICS),
        "intent_id": {"type": "string", "enum": list(intent_ids)},
        "runtime_target": _runtime_target_schema(),
        "solver_budget": {
            "type": "object",
            "properties": {
                "max_iters": {"type": "integer", "minimum": 1},
                "max_time_sec": {"type": "number", "exclusiveMinimum": 0},
            },
            "required": ["max_iters", "max_time_sec"],
            "additionalProperties": False,
        },
    }
    required = list(properties)
    if insertion:
        properties["insertion_control"] = _insertion_control_schema(action_space)
        required.append("insertion_control")
    if destroy:
        properties["destroy_control"] = _destroy_control_schema(action_space)
        required.append("destroy_control")
    if acceptance:
        properties["acceptance_control"] = _acceptance_control_schema(action_space)
        required.append("acceptance_control")
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def _review_request_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "action": {"type": "string", "const": "request_supervisor_review"},
            "decision_evidence": _decision_evidence_schema(STEP_BASIS_NAMES, QUALITY_METRICS),
            "review_request": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "minLength": 1, "maxLength": 240},
                },
                "required": ["reason"],
                "additionalProperties": False,
            },
        },
        "required": ["action", "decision_evidence", "review_request"],
        "additionalProperties": False,
    }


def _runtime_target_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "scope_kind": {"type": "string", "enum": ["global", "task_scope", "route_scope", "mixed_scope"]},
            "task_ids": {"type": "array", "maxItems": 8, "items": {"type": "integer"}},
            "agent_ids": {"type": "array", "maxItems": 6, "items": {"type": "integer"}},
            "focus_metrics": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "string", "enum": list(QUALITY_METRICS)}},
        },
        "required": ["scope_kind", "task_ids", "agent_ids", "focus_metrics"],
        "additionalProperties": False,
    }


def _insertion_control_schema(action_space: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "operator_scores": _score_array(_values(action_space, "insertion_operators", INSERTION_OPERATOR_NAMES)),
            "task_signal_scores": _score_array(_values(action_space, "insertion_task_signals", INSERTION_TASK_SIGNAL_NAMES)),
            "position_signal_scores": _score_array(_values(action_space, "insertion_position_signals", INSERTION_POSITION_SIGNAL_NAMES)),
        },
        "required": ["operator_scores", "task_signal_scores", "position_signal_scores"],
        "additionalProperties": False,
    }


def _destroy_control_schema(action_space: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "operator_scores": _score_array(_values(action_space, "destroy_operators", DESTROY_OPERATOR_NAMES)),
            "signal_scores": _score_array(_values(action_space, "destroy_signals", DESTROY_SIGNAL_NAMES)),
            "intensity_score": {"type": "integer", "minimum": 0, "maximum": 10},
        },
        "required": ["operator_scores", "signal_scores", "intensity_score"],
        "additionalProperties": False,
    }


def _acceptance_control_schema(action_space: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": _values(action_space, "acceptance_modes", ACCEPTANCE_MODES)},
            "intensity_score": {"type": "integer", "minimum": 0, "maximum": 10},
        },
        "required": ["mode", "intensity_score"],
        "additionalProperties": False,
    }


def _score_array(names: Iterable[str]) -> Dict[str, Any]:
    return {
        "type": "array",
        "minItems": 0,
        "maxItems": 3,
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "enum": list(names)},
                "score": {"type": "integer", "minimum": 0, "maximum": 10},
            },
            "required": ["name", "score"],
            "additionalProperties": False,
        },
    }


def _decision_evidence_schema(basis_names: Mapping[str, Iterable[str]], metrics: Iterable[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "basis": {
                "type": "array",
                "minItems": 1,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "enum": list(basis_names)},
                        "name": {"type": "string"},
                    },
                    "required": ["source", "name"],
                    "additionalProperties": False,
                },
            },
            "argument": {
                "type": "array",
                "minItems": 1,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string", "minLength": 1, "maxLength": 220},
                        "uses": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 3,
                            "items": {"type": "integer", "minimum": 0},
                        },
                    },
                    "required": ["claim", "uses"],
                    "additionalProperties": False,
                },
            },
            "control_intent": {"type": "string", "minLength": 1, "maxLength": 280},
            "expected_effects": {
                "type": "array",
                "minItems": 0,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string", "enum": list(metrics)},
                        "direction": {"type": "string", "enum": ["decrease", "increase", "maintain"]},
                    },
                    "required": ["metric", "direction"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["basis", "argument", "control_intent", "expected_effects"],
        "additionalProperties": False,
    }


def _values(space: Mapping[str, Any], key: str, default: Iterable[str]) -> list[str]:
    raw = space.get(key, default)
    out = []
    for item in raw or []:
        out.append(str(item.get("name")) if isinstance(item, Mapping) else str(item))
    return list(dict.fromkeys(out))


def _apply_resource_limits(schema: Dict[str, Any], limits: Mapping[str, Any]) -> None:
    if not limits:
        return
    policy = schema["properties"]["resource_policy"]["properties"]
    if "max_solver_actions_allowed" in limits:
        max_actions = int(float(limits["max_solver_actions_allowed"]))
        policy["max_actions"]["maximum"] = max_actions
        policy["min_actions"]["maximum"] = max_actions
    if "max_iters_allowed" in limits:
        policy["max_iters"]["maximum"] = int(float(limits["max_iters_allowed"]))
    if "max_time_sec_allowed" in limits:
        policy["max_time_sec"]["maximum"] = float(limits["max_time_sec_allowed"])


def _no_stage_budget(limits: Mapping[str, Any]) -> bool:
    if not limits:
        return False
    return any(
        float(limits.get(key, 0) or 0) <= 0
        for key in ("max_solver_actions_allowed", "max_time_sec_allowed", "max_iters_allowed")
    )


__all__ = [
    "QUALITY_METRICS",
    "CONSTRAINT_METRICS",
    "STEP_BASIS_NAMES",
    "SUPERVISOR_BASIS_NAMES",
    "build_action_space",
    "schema_text",
    "supervisor_schema",
    "step_schema",
]
