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
            "Start the run. Select the run-level global_objective and issue the first "
            "initial_construction contract. The contract must define stage_goal, "
            "stage_objective_layers, feasibility_control, guidance, and completion_policy. "
            "Do not choose destroy, insertion, acceptance, or per-action operator scores."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_supervisor_review_prompt(*, user_goal_text: str, observation: Dict[str, Any], json_schema: str) -> str:
    return _prompt(
        "SUPERVISOR_REVIEW",
        (
            "Review the completed contract and decide whether to issue the next contract "
            "or stop the run. A new contract must define the next stage goal, stage objective, "
            "feasibility mode, guidance, and completion policy. Do not choose low-level ALNS operators."
        ),
        {"user_goal": user_goal_text, "observation": observation},
        json_schema,
    )


def get_solver_prompt(*, user_goal_text: str, observation: Dict[str, Any], json_schema: str) -> str:
    return _prompt(
        "SOLVER",
        (
            "Act under the active supervisor contract. For initial_construction, output construct_initial. "
            "For alns_search, recovery, or final_refinement, output run_alns unless the contract is clearly inconsistent "
            "with the observation. Do not change global objective, stage objective, feasibility mode, or completion policy."
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
