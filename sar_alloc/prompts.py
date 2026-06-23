from __future__ import annotations

import json
from typing import Any, Dict


SYSTEM_PROMPT = (
    "You control a task-assignment optimizer. Return exactly one JSON object "
    "matching the requested schema. Do not use markdown or add extra fields."
)


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def get_supervisor_kickoff_prompt(*, user_goal_text: str, observation: Dict[str, Any], json_schema: str) -> str:
    return _prompt(
        "SUPERVISOR_KICKOFF",
        (
            "You are the stage supervisor. Use only the observation fields. Output a "
            "global objective and one executable initial contract. Operational fields "
            "will be compiled and enforced. Put human-readable text only in explanation."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_supervisor_review_prompt(*, user_goal_text: str, observation: Dict[str, Any], json_schema: str) -> str:
    return _prompt(
        "SUPERVISOR_REVIEW",
        (
            "Use condition_report, stage_verification_summary, solution_position, and "
            "budget_caps to decide whether to stop or issue the next executable contract. "
            "Put human-readable text only in contract_review or explanation."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_solver_prompt(*, user_goal_text: str, observation: Dict[str, Any], json_schema: str) -> str:
    return _prompt(
        "SOLVER",
        (
            "Choose one allowed action. If executing a solver action, choose one target_id "
            "from decision_targets and choose controls only from action_space. Every "
            "operational field will be compiled and executed exactly."
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
