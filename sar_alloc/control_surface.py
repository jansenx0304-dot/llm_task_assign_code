"""Single registry for the public, executable LLM control surface."""

from __future__ import annotations

from typing import Dict, Tuple

from .operators.types import (
    ACCEPTANCE_MODES,
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
)

QUALITY_METRICS: Tuple[str, ...] = (
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance",
)

FIELD_CANDIDATES: Dict[str, Tuple[str, ...]] = {
    "destroy_control.operator_scores": DESTROY_OPERATOR_NAMES,
    "destroy_control.signal_scores": DESTROY_SIGNAL_NAMES,
    "insertion_control.operator_scores": INSERTION_OPERATOR_NAMES,
    "insertion_control.task_signal_scores": INSERTION_TASK_SIGNAL_NAMES,
    "insertion_control.position_signal_scores": INSERTION_POSITION_SIGNAL_NAMES,
    "acceptance_control.mode": ACCEPTANCE_MODES,
}

OBSERVATION_BLOCK_CONSUMERS: Dict[str, Tuple[str, ...]] = {
    "run_context": ("prompt", "memory.trace_link"),
    "active_contract": ("action_gate", "compiler", "contract_monitor"),
    "execution_state": ("hard_action_gate", "resource_gate", "contract_monitor"),
    "solution_evidence": ("llm_decision",),
    "candidate_landscape": ("llm_decision",),
    "control_catalog": ("schema.enums", "validator", "compiler"),
    "recent_memory": ("llm_decision",),
    "last_verification": ("llm_decision",),
}

SUPERVISOR_KICKOFF_BLOCK_CONSUMERS: Dict[str, Tuple[str, ...]] = {
    "run_context": ("prompt", "trace"),
    "problem_profile": ("supervisor_decision",),
    "relaxation_reference": ("feasibility_control_decision",),
    "action_space": ("schema.enums", "validator", "contract_compiler"),
}

SUPERVISOR_REVIEW_BLOCK_CONSUMERS: Dict[str, Tuple[str, ...]] = {
    "run_context": ("prompt", "trace"),
    "completed_contract": ("supervisor_decision", "contract_audit"),
    "completed_progress": ("supervisor_decision", "contract_audit"),
    "contract_result": ("supervisor_decision", "contract_monitor"),
    "verification_summary": ("supervisor_decision",),
    "solution_state": ("supervisor_decision",),
    "recent_memory": ("supervisor_decision",),
    "relaxation_reference": ("feasibility_control_decision",),
    "action_space": ("schema.enums", "validator", "contract_compiler"),
}

SOLVER_OUTPUT_FIELD_CONSUMERS: Dict[str, Tuple[str, ...]] = {
    "action": ("validator", "compiler", "orchestrator"),
    "situation_assessment": ("validator", "compiler", "trace"),
    "intent_id": ("validator", "compiler", "trace"),
    "destroy_control": ("validator", "compiler", "destroy_operator"),
    "insertion_control": ("validator", "compiler", "insertion_operator"),
    "acceptance_control": ("validator", "compiler", "acceptance_runtime"),
    "solver_budget": ("validator", "compiler", "runtime"),
    "expected_effects": ("validator", "compiler", "verifier_trace"),
    "review_request": ("validator", "compiler", "contract_monitor"),
    "explanation": ("validator", "audit_only"),
}

SUPERVISOR_OUTPUT_FIELD_CONSUMERS: Dict[str, Tuple[str, ...]] = {
    "action": ("validator", "orchestrator"),
    "global_objective": ("validator", "global_objective_compiler"),
    "next_contract.contract_type": ("validator", "action_gate"),
    "next_contract.objective_layers": ("validator", "solver_comparator"),
    "next_contract.feasibility_control": ("validator", "compiler", "runtime"),
    "next_contract.situation_assessment": ("validator", "trace"),
    "next_contract.target_intents": ("validator", "solver_intent_enum", "trace"),
    "next_contract.protected_metrics": ("validator", "runtime_hard_gate"),
    "next_contract.resource_policy": ("validator", "solver_budget", "contract_monitor"),
    "next_contract.exit_conditions": ("validator", "contract_monitor"),
    "contract_review": ("validator", "audit_only"),
    "stop_explanation": ("validator", "audit_only"),
    "explanation": ("validator", "audit_only"),
}


__all__ = [
    "ACCEPTANCE_MODES",
    "DESTROY_OPERATOR_NAMES",
    "DESTROY_SIGNAL_NAMES",
    "FIELD_CANDIDATES",
    "INSERTION_OPERATOR_NAMES",
    "INSERTION_POSITION_SIGNAL_NAMES",
    "INSERTION_TASK_SIGNAL_NAMES",
    "OBSERVATION_BLOCK_CONSUMERS",
    "QUALITY_METRICS",
    "SOLVER_OUTPUT_FIELD_CONSUMERS",
    "SUPERVISOR_KICKOFF_BLOCK_CONSUMERS",
    "SUPERVISOR_OUTPUT_FIELD_CONSUMERS",
    "SUPERVISOR_REVIEW_BLOCK_CONSUMERS",
]
