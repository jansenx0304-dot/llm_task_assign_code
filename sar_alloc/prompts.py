from __future__ import annotations

import json
from typing import Any, Dict

SYSTEM_PROMPT = (
    "You control a task-assignment optimizer. Return exactly one JSON object "
    "matching the requested schema. Do not use markdown or add extra fields."
)


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def get_supervisor_kickoff_prompt(
    *, user_goal_text: str, observation: Dict[str, Any], json_schema: str
) -> str:
    return _prompt(
        "SUPERVISOR_KICKOFF",
        (
            "You are the stage supervisor. Use only the observation fields. Output a "
            "global objective, evidence-bound decision_basis, situation_summary, "
            "and one executable initial contract with LLM-created target_intents. "
            "Observation is evidence only; it contains no recommended strategy. "
            "Every decision_basis evidence_ref must be a dot-path that exists in "
            "the current observation."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_supervisor_review_prompt(
    *, user_goal_text: str, observation: Dict[str, Any], json_schema: str
) -> str:
    return _prompt(
        "SUPERVISOR_REVIEW",
        (
            "Use contract_result, verification_summary, solution_state, recent_memory, "
            "and hard resource constraints to decide whether to stop or issue the next "
            "executable contract. If issuing a contract, create target_intents yourself "
            "from evidence. Cite existing observation dot-paths in decision_basis and "
            "reference basis_ids from situation_summary and expected_effects."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_solver_prompt(
    *, user_goal_text: str, observation: Dict[str, Any], json_schema: str
) -> str:
    return _prompt(
        "SOLVER",
        (
            "Choose one hard-executable action. Observation is an evidence packet and "
            "contains no recommended strategy. If executing a solver action, choose one "
            "intent_id from active_contract.target_intents, write evidence-bound "
            "decision_basis and situation_summary, choose runtime_target from "
            "targetable_evidence, "
            "and choose controls only from control_catalog. runtime_target binds the "
            "intent to concrete visible tasks/routes/metrics for this action. Use only "
            "task_ids in targetable_evidence.visible_task_ids and agent_ids in "
            "targetable_evidence.visible_agent_ids; use global scope only when no local "
            "target is justified by the evidence. Operator scores are LLM priors, "
            "not hard filters. The ALNS runtime may keep a small exploration probability "
            "for low-prior operators to avoid premature search collapse. Use high scores "
            "to express preference, not exclusive permission. Recent operator usage and "
            "effectiveness are provided in observation; adjust priors based on that "
            "feedback. Signal scores are direct scoring coefficients for this decision. "
            "A missing or zero signal score means that signal should not directly "
            "contribute to the current scoring formula. Do not move names between destroy "
            "operator, destroy signal, insertion operator, task signal, and position "
            "signal fields. expected_effects must cite decision_basis basis_ids."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def _prompt(role: str, instruction: str, context: Dict[str, Any], schema: str) -> str:
    return (
        f"ROLE: {role}\n\nINSTRUCTION:\n{instruction}\n\n"
        f"CONTEXT:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"OUTPUT JSON SCHEMA:\n{schema}"
    )


__all__ = [
    "get_system_prompt",
    "get_supervisor_kickoff_prompt",
    "get_supervisor_review_prompt",
    "get_solver_prompt",
]
