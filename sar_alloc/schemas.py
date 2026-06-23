from __future__ import annotations

"""JSON-schema dictionaries for the executable LLM surface."""

import json
from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Optional

from .control_surface import QUALITY_METRICS

CONSTRAINT_METRICS = (
    "violation_total",
    "violation_capability",
    "violation_time_window",
    "violation_energy",
    "recoverable_violation_total",
    "unrecoverable_violation_total",
)
CONTRACT_TYPES = (
    "initial_construction",
    "alns_search",
    "recovery",
    "final_refinement",
)
FEASIBILITY_MODES = (
    "strict",
    "relaxed_recoverable",
    "recovery_only",
)
RELAXABLE_VIOLATION_TYPES = (
    "time_window",
    "energy",
)
SUPPORTED_CONDITION_SOURCES = (
    "progress.solver_actions",
    "progress.iters_used",
    "progress.time_used_sec",
    "last.intent_status",
    "last.dominant_blocker",
    "last.best_improved",
    "aggregate.achieved",
    "aggregate.partial",
    "aggregate.not_achieved",
    "aggregate.regressed",
    "aggregate.solver_requested_review",
    "working.is_feasible",
    "working.missed_priority",
    "working.unassigned_count",
    "working.energy_total",
    "working.total_distance",
    "working.makespan",
    "working.route_balance",
    "best_feasible.exists",
    "best_feasible.missed_priority",
    "best_feasible.unassigned_count",
    "best_feasible.energy_total",
    "best_feasible.total_distance",
    "best_feasible.makespan",
    "best_feasible.route_balance",
)


def _string(description: str) -> Dict[str, Any]:
    return {"type": "string", "description": description}


EXPLANATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Human-readable explanation ignored by validator/compiler/runtime.",
    "additionalProperties": {"type": "string"},
}

SPARSE_SCORE_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "A sparse executable score item.",
    "properties": {
        "name": _string("Candidate name from the current action_space."),
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "description": "Executable emphasis score from 0 to 10.",
        },
    },
    "required": ["name", "score"],
    "additionalProperties": False,
}


def _score_array(description: str) -> Dict[str, Any]:
    return {
        "type": "array",
        "description": description,
        "minItems": 0,
        "maxItems": 3,
        "items": deepcopy(SPARSE_SCORE_ITEM_SCHEMA),
    }


def _enum_string(names: Iterable[str], description: str) -> Dict[str, Any]:
    """Return a string schema restricted to the supplied candidate names."""
    return {
        "type": "string",
        "enum": list(dict.fromkeys(str(name) for name in names)),
        "description": description,
    }


def _score_item_schema(names: Iterable[str], description: str) -> Dict[str, Any]:
    return {
        "type": "object",
        "description": description,
        "properties": {
            "name": _enum_string(names, "Candidate name allowed for this exact score field."),
            "score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 10,
                "description": "Executable emphasis score from 0 to 10.",
            },
        },
        "required": ["name", "score"],
        "additionalProperties": False,
    }


def _score_array_for(names: Iterable[str], description: str, max_items: int = 3) -> Dict[str, Any]:
    names = tuple(names)
    return {
        "type": "array",
        "description": description,
        "minItems": 0,
        "maxItems": max_items,
        "items": _score_item_schema(names, description),
    }


INSERTION_CONTROL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Executable insertion controls.",
    "properties": {
        "operator_scores": _score_array("Sparse emphasis scores for insertion operators."),
        "task_signal_scores": _score_array("Sparse emphasis scores for choosing the next task."),
        "position_signal_scores": _score_array("Sparse emphasis scores for choosing an insertion position."),
    },
    "required": ["operator_scores", "task_signal_scores", "position_signal_scores"],
    "additionalProperties": False,
}

DESTROY_CONTROL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Executable destroy controls.",
    "properties": {
        "operator_scores": _score_array("Sparse emphasis scores for destroy operators."),
        "signal_scores": _score_array("Sparse emphasis scores for destroy signals."),
        "intensity_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "description": "Removal intensity from 0 to 10.",
        },
    },
    "required": ["operator_scores", "signal_scores", "intensity_score"],
    "additionalProperties": False,
}

ACCEPTANCE_CONTROL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Executable acceptance control.",
    "properties": {
        "mode": _string("Acceptance mode from action_space.allowed_acceptance_modes."),
        "intensity_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "description": "Acceptance exploration intensity.",
        },
    },
    "required": ["mode", "intensity_score"],
    "additionalProperties": False,
}

GLOBAL_OBJECTIVE_SHAPE: Dict[str, Any] = {
    "type": "object",
    "description": "Run-level objective used to compare global best solutions.",
    "properties": {
        "objective_layers": {
            "type": "array",
            "description": "Ordered global quality metrics. Earlier metrics dominate later metrics.",
            "minItems": 1,
            "maxItems": 4,
            "items": {"type": "string", "enum": list(QUALITY_METRICS)},
        },
        "explanation": EXPLANATION_SCHEMA,
    },
    "required": ["objective_layers"],
    "additionalProperties": False,
}

RELAXATION_RATIO_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "One temporary recoverable relaxation allowance.",
    "properties": {
        "violation_type": {
            "type": "string",
            "enum": list(RELAXABLE_VIOLATION_TYPES),
            "description": "Relaxable violation type.",
        },
        "max_ratio": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 0.30,
            "description": "Normalized temporary allowance for this violation type.",
        },
    },
    "required": ["violation_type", "max_ratio"],
    "additionalProperties": False,
}

FEASIBILITY_CONTROL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Stage-level feasibility handling selected by Supervisor.",
    "properties": {
        "mode": {
            "type": "string",
            "enum": list(FEASIBILITY_MODES),
            "description": "Feasibility mode for this contract.",
        },
        "relaxation_ratios": {
            "type": "array",
            "description": "Temporary recoverable relaxation ratios. Used by relaxed_recoverable.",
            "maxItems": 2,
            "items": RELAXATION_RATIO_ITEM_SCHEMA,
        },
    },
    "required": ["mode", "relaxation_ratios"],
    "additionalProperties": False,
}

TARGET_POLICY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Executable target preference for the next contract.",
    "properties": {
        "preferred_target_kinds": {
            "type": "array",
            "minItems": 0,
            "maxItems": 4,
            "items": {
                "type": "string",
                "enum": ["unassigned_priority", "scarce_unassigned", "energy_debt", "time_window_debt", "route_balance"],
            },
        }
    },
    "required": ["preferred_target_kinds"],
    "additionalProperties": False,
}

PROTECTED_METRIC_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "A metric that may not worsen beyond the provided amount.",
    "properties": {
        "metric": {"type": "string", "enum": list(QUALITY_METRICS)},
        "max_worsen": {"type": "number", "minimum": 0.0},
    },
    "required": ["metric", "max_worsen"],
    "additionalProperties": False,
}

RESOURCE_POLICY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Executable resource limits for this contract.",
    "properties": {
        "min_actions": {"type": "integer", "minimum": 1, "maximum": 20},
        "max_actions": {"type": "integer", "minimum": 1},
        "max_iters": {"type": "integer", "minimum": 1},
        "max_time_sec": {"type": "number", "exclusiveMinimum": 0},
    },
    "required": ["min_actions", "max_actions", "max_iters", "max_time_sec"],
    "additionalProperties": False,
}

CONDITION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Typed condition evaluated by ContractMonitor.",
    "properties": {
        "condition_id": _string("Stable id unique inside this contract condition set."),
        "source": {
            "type": "string",
            "enum": list(SUPPORTED_CONDITION_SOURCES),
            "description": "Executable source path read by ContractMonitor.",
        },
        "op": {"type": "string", "enum": ["<", "<=", "==", "!=", ">=", ">"]},
        "value": {"type": ["number", "string", "boolean"]},
        "window": {"type": "integer", "minimum": 1, "maximum": 20},
    },
    "required": ["condition_id", "source", "op", "value", "window"],
    "additionalProperties": False,
}

EXIT_CONDITIONS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Typed success and failure conditions.",
    "properties": {
        "success": {"type": "array", "maxItems": 4, "items": CONDITION_SCHEMA},
        "failure": {"type": "array", "maxItems": 4, "items": CONDITION_SCHEMA},
    },
    "required": ["success", "failure"],
    "additionalProperties": False,
}

CONTRACT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "A supervisor-issued executable search contract.",
    "properties": {
        "contract_type": {"type": "string", "enum": list(CONTRACT_TYPES)},
        "objective_layers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "items": {"type": "string", "enum": list(QUALITY_METRICS)},
        },
        "feasibility_control": FEASIBILITY_CONTROL_SCHEMA,
        "target_policy": TARGET_POLICY_SCHEMA,
        "protected_metrics": {
            "type": "array",
            "maxItems": 4,
            "items": PROTECTED_METRIC_SCHEMA,
        },
        "resource_policy": RESOURCE_POLICY_SCHEMA,
        "exit_conditions": EXIT_CONDITIONS_SCHEMA,
        "explanation": EXPLANATION_SCHEMA,
    },
    "required": [
        "contract_type",
        "objective_layers",
        "feasibility_control",
        "target_policy",
        "protected_metrics",
        "resource_policy",
        "exit_conditions",
    ],
    "additionalProperties": False,
}

CONTRACT_REVIEW_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Human-readable review ignored by runtime.",
    "properties": {
        "outcome_summary": _string("What happened during the completed contract."),
        "main_lesson": _string("Most important lesson for the next stage."),
    },
    "required": ["outcome_summary", "main_lesson"],
    "additionalProperties": False,
}

SUPERVISOR_KICKOFF_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor kickoff decision at the beginning of a run.",
    "properties": {
        "supervisor_decision": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "const": "start_run"},
                "global_objective": GLOBAL_OBJECTIVE_SHAPE,
                "next_contract": CONTRACT_SCHEMA,
            },
            "required": ["action", "global_objective", "next_contract"],
            "additionalProperties": False,
        }
    },
    "required": ["supervisor_decision"],
    "additionalProperties": False,
}

SUPERVISOR_REVIEW_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor decision after a contract has ended.",
    "properties": {
        "supervisor_decision": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "const": "issue_contract"},
                        "contract_review": CONTRACT_REVIEW_SCHEMA,
                        "next_contract": CONTRACT_SCHEMA,
                    },
                    "required": ["action", "contract_review", "next_contract"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "const": "stop_run"},
                        "contract_review": CONTRACT_REVIEW_SCHEMA,
                        "stop_explanation": _string("Why the supervisor decides the run should stop."),
                    },
                    "required": ["action", "contract_review", "stop_explanation"],
                    "additionalProperties": False,
                },
            ]
        }
    },
    "required": ["supervisor_decision"],
    "additionalProperties": False,
}

_SOLVER_DECISION_SCHEMA_TEMPLATE: Dict[str, Any] = {
    "type": "object",
    "description": "One Solver decision under the active supervisor contract.",
    "properties": {
        "solver_decision": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "const": "construct_initial"},
                        "target_id": _string("Target id from decision_targets."),
                        "insertion_control": INSERTION_CONTROL_SCHEMA,
                        "explanation": EXPLANATION_SCHEMA,
                    },
                    "required": ["action", "target_id", "insertion_control"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "const": "run_alns"},
                        "target_id": _string("Target id from decision_targets."),
                        "destroy_control": DESTROY_CONTROL_SCHEMA,
                        "insertion_control": INSERTION_CONTROL_SCHEMA,
                        "acceptance_control": ACCEPTANCE_CONTROL_SCHEMA,
                        "explanation": EXPLANATION_SCHEMA,
                    },
                    "required": [
                        "action",
                        "target_id",
                        "destroy_control",
                        "insertion_control",
                        "acceptance_control",
                    ],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "const": "request_supervisor_review"},
                        "target_id": _string("Target id from decision_targets, usually contract_review."),
                        "explanation": EXPLANATION_SCHEMA,
                    },
                    "required": ["action", "target_id"],
                    "additionalProperties": False,
                },
            ]
        }
    },
    "required": ["solver_decision"],
    "additionalProperties": False,
}


def solver_decision_schema_for_candidates(candidates: Any, observation: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Build a Solver schema whose executable fields use their own candidate enums."""
    action_space = observation.get("action_space") if isinstance(observation, Mapping) else None

    def allowed(action_key: str, candidate_key: str) -> tuple[str, ...]:
        if isinstance(action_space, Mapping) and action_key in action_space:
            values = action_space.get(action_key) or []
            return tuple(dict.fromkeys(str(value) for value in values))
        if candidates is not None and hasattr(candidates, "names"):
            return tuple(dict.fromkeys(str(value) for value in candidates.names(candidate_key)))
        if isinstance(candidates, Mapping):
            values = candidates.get(candidate_key) or []
            return tuple(dict.fromkeys(
                str(value.get("name")) if isinstance(value, Mapping) else str(value)
                for value in values
            ))
        return ()

    insertion = deepcopy(INSERTION_CONTROL_SCHEMA)
    insertion["properties"]["operator_scores"] = _score_array_for(
        allowed("allowed_insertion_operators", "insertion_operator_candidates"),
        "Sparse emphasis scores for insertion operators.",
    )
    insertion["properties"]["task_signal_scores"] = _score_array_for(
        allowed("allowed_task_signals", "insertion_task_signal_candidates"),
        "Sparse emphasis scores for choosing the next task.",
    )
    insertion["properties"]["position_signal_scores"] = _score_array_for(
        allowed("allowed_position_signals", "insertion_position_signal_candidates"),
        "Sparse emphasis scores for choosing an insertion position.",
    )

    destroy = deepcopy(DESTROY_CONTROL_SCHEMA)
    destroy["properties"]["operator_scores"] = _score_array_for(
        allowed("allowed_destroy_operators", "destroy_operator_candidates"),
        "Sparse emphasis scores for destroy operators.",
    )
    destroy["properties"]["signal_scores"] = _score_array_for(
        allowed("allowed_destroy_signals", "destroy_signal_candidates"),
        "Sparse emphasis scores for destroy signals.",
    )

    acceptance = deepcopy(ACCEPTANCE_CONTROL_SCHEMA)
    acceptance["properties"]["mode"] = _enum_string(
        allowed("allowed_acceptance_modes", "acceptance_candidates"),
        "Acceptance mode allowed for the current action space.",
    )

    schema = deepcopy(_SOLVER_DECISION_SCHEMA_TEMPLATE)
    branches = schema["properties"]["solver_decision"]["oneOf"]
    allowed_actions = None
    if isinstance(action_space, Mapping) and "allowed_actions" in action_space:
        allowed_actions = {str(value) for value in (action_space.get("allowed_actions") or [])}
        branches[:] = [
            branch for branch in branches
            if branch["properties"]["action"].get("const") in allowed_actions
        ]

    target_ids = []
    if isinstance(observation, Mapping):
        target_ids = [
            str(item["target_id"])
            for item in (observation.get("decision_targets") or [])
            if isinstance(item, Mapping) and item.get("target_id") is not None
        ]
    for branch in branches:
        properties = branch["properties"]
        if target_ids:
            properties["target_id"] = _enum_string(target_ids, "Target id from current decision_targets.")
        if "insertion_control" in properties:
            properties["insertion_control"] = deepcopy(insertion)
        if "destroy_control" in properties:
            properties["destroy_control"] = deepcopy(destroy)
        if "acceptance_control" in properties:
            properties["acceptance_control"] = deepcopy(acceptance)
    return schema


# Compatibility export only. Runtime Solver calls must use
# solver_decision_schema_for_candidates().
SOLVER_DECISION_SCHEMA = deepcopy(_SOLVER_DECISION_SCHEMA_TEMPLATE)


def schema_text(schema: Dict[str, Any]) -> str:
    return json.dumps(schema, ensure_ascii=False, indent=2)


def supervisor_kickoff_schema_for_limits(resource_limits: Dict[str, Any]) -> Dict[str, Any]:
    return _supervisor_schema_for_limits(SUPERVISOR_KICKOFF_SCHEMA, resource_limits)


def supervisor_review_schema_for_limits(resource_limits: Dict[str, Any]) -> Dict[str, Any]:
    return _supervisor_schema_for_limits(SUPERVISOR_REVIEW_SCHEMA, resource_limits)


def _supervisor_schema_for_limits(schema: Dict[str, Any], resource_limits: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(schema)
    _apply_contract_limits(out, resource_limits)
    return out


def _apply_contract_limits(node: Any, resource_limits: Dict[str, Any]) -> None:
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict) and "resource_policy" in properties:
            policy = properties["resource_policy"]
            policy_props = policy.get("properties", {}) if isinstance(policy, dict) else {}
            if isinstance(policy_props, dict):
                if "max_actions" in policy_props:
                    policy_props["max_actions"]["maximum"] = int(resource_limits["max_solver_actions_allowed"])
                if "min_actions" in policy_props:
                    policy_props["min_actions"]["maximum"] = min(20, int(resource_limits["max_solver_actions_allowed"]))
                if "max_time_sec" in policy_props:
                    policy_props["max_time_sec"]["maximum"] = float(resource_limits["max_time_sec_allowed"])
                if "max_iters" in policy_props:
                    policy_props["max_iters"]["maximum"] = int(resource_limits["max_iters_allowed"])
        for value in node.values():
            _apply_contract_limits(value, resource_limits)
    elif isinstance(node, list):
        for value in node:
            _apply_contract_limits(value, resource_limits)


__all__ = [
    "QUALITY_METRICS",
    "CONSTRAINT_METRICS",
    "SUPERVISOR_KICKOFF_SCHEMA",
    "SUPERVISOR_REVIEW_SCHEMA",
    "SOLVER_DECISION_SCHEMA",
    "CONTRACT_SCHEMA",
    "schema_text",
    "solver_decision_schema_for_candidates",
    "supervisor_kickoff_schema_for_limits",
    "supervisor_review_schema_for_limits",
]
