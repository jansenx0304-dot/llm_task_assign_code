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
            "global objective, your situation_assessment, and one executable initial "
            "contract with LLM-created target_intents. Observation is evidence only; "
            "it contains no recommended strategy."
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
            "Use contract_result, verification_summary, solution_evidence, and hard "
            "resource constraints to decide whether to stop or issue the next executable "
            "contract. If issuing a contract, create target_intents yourself from evidence."
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
            "intent_id from active_contract.target_intents, write your own "
            "situation_assessment, and choose controls only from control_catalog. Every "
            "nonzero operator/signal weight must appear explicitly in your control output; "
            "unmentioned weights execute as zero. Do not move names between destroy "
            "operator, destroy signal, insertion operator, task signal, and position "
            "signal fields."
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
