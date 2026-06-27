"""Prompt builders for the simplified agent loop."""

from __future__ import annotations

import json
from typing import Any, Dict


def system_prompt() -> str:
    return (
        "You control a task-assignment optimizer. Return exactly one JSON object "
        "that matches the provided schema. Use only the observation as evidence. "
        "Do not add markdown or fields outside the schema."
    )


def supervisor_prompt(
    *,
    phase: str,
    user_goal: str,
    observation: Dict[str, Any],
    schema: Dict[str, Any],
) -> str:
    return _prompt(
        role="SUPERVISOR",
        instruction=(
            f"Phase is {phase}. Set or revise the global objective, issue the next "
            "stage, or stop the run. Supervisor does not choose runtime operators. "
            "decision_basis evidence_refs must be dot-paths present in the observation."
        ),
        context={"user_goal": user_goal, "observation": observation},
        schema=schema,
    )


def step_prompt(
    *,
    user_goal: str,
    observation: Dict[str, Any],
    schema: Dict[str, Any],
) -> str:
    return _prompt(
        role="STEP",
        instruction=(
            "Choose one hard-executable action from execution_state. If executing, "
            "choose an intent_id from active_stage, runtime_target ids only from "
            "targetable_evidence, and controls only from control_catalog. Operator "
            "scores are preference weights, not hard filters. decision_basis "
            "evidence_refs must be dot-paths present in the observation."
        ),
        context={"user_goal": user_goal, "observation": observation},
        schema=schema,
    )


def _prompt(role: str, instruction: str, context: Dict[str, Any], schema: Dict[str, Any]) -> str:
    return (
        f"ROLE: {role}\n\n"
        f"INSTRUCTION:\n{instruction}\n\n"
        f"CONTEXT:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"OUTPUT JSON SCHEMA:\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )


__all__ = ["system_prompt", "supervisor_prompt", "step_prompt"]
