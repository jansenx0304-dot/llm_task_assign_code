from __future__ import annotations

"""JSON-schema dictionaries for every public LLM response."""

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
COMPLETION_EVENTS = (
    "initial_solution_built",
    "initial_solution_failed",
    "quality_improved",
    "quality_flat",
    "quality_worsened",
    "global_best_improved",
    "no_admissible_candidate",
    "feasibility_recovered",
    "recovery_debt_reduced",
)


def _string(description: str) -> Dict[str, Any]:
    return {"type": "string", "description": description}


SPARSE_SCORE_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "A sparse score item emphasizing one public candidate.",
    "properties": {
        "name": _string("Candidate name from the corresponding public candidate list."),
        "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "description": "Emphasis score from 0 to 10.",
        },
        "reason": _string("Short reason for emphasizing this candidate now."),
    },
    "required": ["name", "score", "reason"],
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
    "description": "Unified insertion control used for initial construction and ALNS insertion.",
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
    "description": "Sparse control for selecting and scoring task removals.",
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
    "description": "Acceptance mode and exploration intensity for one ALNS action.",
    "properties": {
        "mode": _string("Acceptance candidate name."),
        "intensity_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 10,
            "description": "Acceptance exploration intensity.",
        },
        "reason": _string("Short reason for this acceptance choice."),
    },
    "required": ["mode", "intensity_score", "reason"],
    "additionalProperties": False,
}

DECISION_BASIS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Auditable evidence supporting this decision.",
    "properties": {
        "evidence_refs": {
            "type": "array",
            "description": "Evidence ids from the current observation.",
            "minItems": 1,
            "maxItems": 6,
            "items": {"type": "string"},
        },
        "memory_refs": {
            "type": "array",
            "description": "Memory ids used by the decision. Empty when no memory is used.",
            "maxItems": 6,
            "items": {"type": "string"},
        },
        "summary": _string("Short explanation of how the evidence supports the decision."),
    },
    "required": ["evidence_refs", "memory_refs", "summary"],
    "additionalProperties": False,
}

OBJECTIVE_SELECTION_BASIS_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Basis for one selected global objective layer.",
    "properties": {
        "metric": {
            "type": "string",
            "enum": list(QUALITY_METRICS),
            "description": "Selected global objective metric.",
        },
        "data_refs": {
            "type": "array",
            "description": "Observation refs supporting this metric choice.",
            "minItems": 1,
            "maxItems": 4,
            "items": {"type": "string"},
        },
        "reason": _string("Why this metric belongs in the global objective."),
    },
    "required": ["metric", "data_refs", "reason"],
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
        "selection_basis": {
            "type": "array",
            "description": "Basis for each objective layer, in the same order as objective_layers.",
            "minItems": 1,
            "maxItems": 4,
            "items": OBJECTIVE_SELECTION_BASIS_ITEM_SCHEMA,
        },
    },
    "required": ["objective_layers", "selection_basis"],
    "additionalProperties": False,
}

STAGE_GOAL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor diagnosis and intent for the next stage.",
    "properties": {
        "summary": _string("One-sentence description of this stage."),
        "main_problem": _string("Main search obstacle this stage should address."),
        "search_intent": _string("Concrete search direction for Solver during this stage."),
    },
    "required": ["summary", "main_problem", "search_intent"],
    "additionalProperties": False,
}

STAGE_GUIDANCE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Stage-level guidance passed from Supervisor to Solver.",
    "properties": {
        "instruction": _string("Main instruction Solver should follow in this contract."),
        "preferred_search_direction": _string("Concrete direction Solver should favor when choosing one action."),
        "protect": _string("Current solution qualities Solver should preserve while searching."),
        "success_signal": _string("Observable sign that this contract is working."),
        "failure_signal": _string("Observable sign that this contract should end or change direction."),
    },
    "required": [
        "instruction",
        "preferred_search_direction",
        "protect",
        "success_signal",
        "failure_signal",
    ],
    "additionalProperties": False,
}

RELAXATION_RATIO_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "One temporary recoverable relaxation allowance.",
    "properties": {
        "type": {
            "type": "string",
            "enum": list(RELAXABLE_VIOLATION_TYPES),
            "description": "Relaxable violation type.",
        },
        "limit_ratio": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 0.30,
            "description": "Normalized temporary allowance for this type.",
        },
        "reason": _string("Why this relaxation helps the current contract."),
    },
    "required": ["type", "limit_ratio", "reason"],
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

COMPLETION_RULE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "One event rule for ending the current contract.",
    "properties": {
        "event": {
            "type": "string",
            "enum": list(COMPLETION_EVENTS),
            "description": "Outcome event name observed by the program auditor.",
        },
        "count": {
            "type": "integer",
            "minimum": 1,
            "maximum": 20,
            "description": "Required count for this event after min_solver_actions is reached.",
        },
        "scope": {
            "type": "string",
            "enum": ["total", "consecutive"],
            "description": "Whether the event count is total within the contract or consecutive.",
        },
    },
    "required": ["event", "count", "scope"],
    "additionalProperties": False,
}

COMPLETION_POLICY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Stage completion policy defined by Supervisor and checked by the program monitor.",
    "properties": {
        "min_solver_actions": {
            "type": "integer",
            "minimum": 1,
            "maximum": 20,
            "description": "Minimum Solver actions before event-based completion can end this contract.",
        },
        "max_solver_actions": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum Solver actions allowed in this contract.",
        },
        "max_time_sec": {
            "type": "number",
            "exclusiveMinimum": 0,
            "description": "Maximum solver execution time assigned to this contract.",
        },
        "max_iters": {
            "type": "integer",
            "minimum": 1,
            "description": "Maximum internal solver iterations assigned to this contract.",
        },
        "success_rules": {
            "type": "array",
            "description": "Events that end this contract as successful after min_solver_actions is reached.",
            "minItems": 1,
            "maxItems": 3,
            "items": COMPLETION_RULE_SCHEMA,
        },
        "failure_rules": {
            "type": "array",
            "description": "Events that end this contract for supervisor review after min_solver_actions is reached.",
            "minItems": 1,
            "maxItems": 3,
            "items": COMPLETION_RULE_SCHEMA,
        },
    },
    "required": [
        "min_solver_actions",
        "max_solver_actions",
        "max_time_sec",
        "max_iters",
        "success_rules",
        "failure_rules",
    ],
    "additionalProperties": False,
}

CONTRACT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "A supervisor-issued stage contract executed by Solver.",
    "properties": {
        "contract_type": {
            "type": "string",
            "enum": list(CONTRACT_TYPES),
            "description": "Type of stage to execute.",
        },
        "stage_goal": STAGE_GOAL_SCHEMA,
        "stage_objective_layers": {
            "type": "array",
            "description": "Ordered quality metrics used inside this stage.",
            "minItems": 1,
            "maxItems": 4,
            "items": {"type": "string", "enum": list(QUALITY_METRICS)},
        },
        "feasibility_control": FEASIBILITY_CONTROL_SCHEMA,
        "guidance": STAGE_GUIDANCE_SCHEMA,
        "completion_policy": COMPLETION_POLICY_SCHEMA,
    },
    "required": [
        "contract_type",
        "stage_goal",
        "stage_objective_layers",
        "feasibility_control",
        "guidance",
        "completion_policy",
    ],
    "additionalProperties": False,
}

SUPERVISOR_KICKOFF_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor kickoff decision at the beginning of a run.",
    "properties": {
        "supervisor_decision": {
            "type": "object",
            "description": "Start the run by setting global objective and first contract.",
            "properties": {
                "action": {
                    "type": "string",
                    "const": "start_run",
                    "description": "Start the run.",
                },
                "global_objective": GLOBAL_OBJECTIVE_SHAPE,
                "next_contract": CONTRACT_SCHEMA,
                "decision_basis": DECISION_BASIS_SCHEMA,
            },
            "required": ["action", "global_objective", "next_contract", "decision_basis"],
            "additionalProperties": False,
        }
    },
    "required": ["supervisor_decision"],
    "additionalProperties": False,
}

CONTRACT_REVIEW_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor interpretation of the completed contract.",
    "properties": {
        "outcome_summary": _string("What happened during the completed contract."),
        "main_lesson": _string("Most important lesson for the next stage."),
        "next_intent": _string("Why the next supervisor action is appropriate."),
    },
    "required": ["outcome_summary", "main_lesson", "next_intent"],
    "additionalProperties": False,
}

SUPERVISOR_REVIEW_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "description": "Supervisor decision after a contract has ended.",
    "properties": {
        "supervisor_decision": {
            "description": "Issue the next contract or stop the run.",
            "oneOf": [
                {
                    "type": "object",
                    "description": "Issue a new contract.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": "issue_contract",
                            "description": "Issue the next stage contract.",
                        },
                        "contract_review": CONTRACT_REVIEW_SCHEMA,
                        "next_contract": CONTRACT_SCHEMA,
                        "decision_basis": DECISION_BASIS_SCHEMA,
                    },
                    "required": ["action", "contract_review", "next_contract", "decision_basis"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "description": "Stop the full run and return the best solution.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": "stop_run",
                            "description": "Stop the run.",
                        },
                        "contract_review": CONTRACT_REVIEW_SCHEMA,
                        "stop_reason": _string("Why the supervisor decides the run should stop."),
                        "decision_basis": DECISION_BASIS_SCHEMA,
                    },
                    "required": ["action", "contract_review", "stop_reason", "decision_basis"],
                    "additionalProperties": False,
                },
            ],
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
            "description": "construct_initial, run_alns, or request_supervisor_review payload.",
            "oneOf": [
                {
                    "type": "object",
                    "description": "Construct the initial working solution.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": "construct_initial",
                            "description": "Execute initial insertion.",
                        },
                        "reason": _string("Reason this construction fits the active contract."),
                        "insertion_control": INSERTION_CONTROL_SCHEMA,
                        "decision_basis": DECISION_BASIS_SCHEMA,
                    },
                    "required": ["action", "reason", "insertion_control", "decision_basis"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "description": "Run one program-budgeted ALNS action.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": "run_alns",
                            "description": "Execute one ALNS action.",
                        },
                        "reason": _string("Reason this action fits the active contract."),
                        "destroy_control": DESTROY_CONTROL_SCHEMA,
                        "insertion_control": INSERTION_CONTROL_SCHEMA,
                        "acceptance_control": ACCEPTANCE_CONTROL_SCHEMA,
                        "decision_basis": DECISION_BASIS_SCHEMA,
                    },
                    "required": [
                        "action",
                        "reason",
                        "destroy_control",
                        "insertion_control",
                        "acceptance_control",
                        "decision_basis",
                    ],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "description": "End the active contract and request supervisor review.",
                    "properties": {
                        "action": {
                            "type": "string",
                            "const": "request_supervisor_review",
                            "description": "Request contract review.",
                        },
                        "reason": _string("Reason the active contract should be reconsidered."),
                        "decision_basis": DECISION_BASIS_SCHEMA,
                    },
                    "required": ["action", "reason", "decision_basis"],
                    "additionalProperties": False,
                },
            ],
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
        if isinstance(properties, dict) and "completion_policy" in properties:
            policy = properties["completion_policy"]
            if isinstance(policy, dict):
                policy_props = policy.get("properties", {})
                if isinstance(policy_props, dict):
                    if "max_solver_actions" in policy_props:
                        policy_props["max_solver_actions"]["maximum"] = int(resource_limits["max_solver_actions_allowed"])
                    if "min_solver_actions" in policy_props:
                        policy_props["min_solver_actions"]["maximum"] = min(20, int(resource_limits["max_solver_actions_allowed"]))
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
]
