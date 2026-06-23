from __future__ import annotations

"""JSON-schema dictionaries for the executable LLM surface."""

import json
from copy import deepcopy
from typing import Any, Dict


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
COMPLETION_SOURCES = (
    "last.intent_status",
    "last.dominant_blocker",
    "last.protected_metric_result.passed",
    "last.trace.trial_flow.accepted_trials",
    "last.trace.trial_flow.best_improved_trials",
    "aggregate.intent_status.achieved",
    "aggregate.intent_status.partially_achieved",
    "aggregate.intent_status.not_achieved",
    "aggregate.dominant_blocker.no_candidate_position",
    "aggregate.dominant_blocker.hard_filter_blocked",
    "aggregate.dominant_blocker.feasibility_rejected_trials",
    "aggregate.dominant_blocker.acceptance_rejected_trials",
    "progress.solver_actions",
    "progress.iters_used",
    "progress.time_used_sec",
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
        "source": _string("Supported source path read from OutcomeVerification/progress."),
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

SOLVER_DECISION_SCHEMA: Dict[str, Any] = {
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
    "supervisor_kickoff_schema_for_limits",
    "supervisor_review_schema_for_limits",
]
