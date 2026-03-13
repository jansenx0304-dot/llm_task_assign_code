# sar_alloc/prompts.py
"""
Prompt templates for the LLM orchestrator.
"""

from __future__ import annotations

from typing import Iterable


def get_system_prompt() -> str:
    return (
        "You are an optimization expert for multi-agent task assignment. "
        "You must follow the requested JSON schemas strictly and return JSON only."
    )


def get_objective_layer_prompt(
    user_goal_text: str,
    available_metrics: str,
    json_schema: str,
) -> str:
    return f"""
Given:
- User goal (natural language): {user_goal_text}
- Available metrics:
{available_metrics}
- Objective JSON schema:
{json_schema}

Rules:
- Keep feasibility as the first layer.
- All other layers must reflect the user goal in priority order.
- Each layer metric must be chosen only from the available metrics using exact names.
- Max layers: 5.

Task:
Create the lexicographic objective layers.

Output JSON only.
""".strip()


def get_next_action_prompt(
    user_goal_text: str,
    instance_summary: str,
    state_snapshot: str,
    budget_state: str,
    recent_history: str,
    objective_layers: str,
    allowed_actions: Iterable[str],
    json_schema: str,
) -> str:
    allowed = ", ".join(str(x) for x in allowed_actions)
    return f"""
You are controlling a closed-loop optimization agent with the cycle:
Observe -> Think -> Act -> Check -> Repeat.

Your job for this turn is to choose exactly one next action.

Inputs:
- User goal:
{user_goal_text}

- Objective layers (locked, read-only):
{objective_layers}

- Static instance features:
{instance_summary}

- Current search state:
{state_snapshot}

- Remaining budget:
{budget_state}

- Recent decisions:
{recent_history}

- Allowed actions for this turn: {allowed}

Rules:
1. Objective layers are locked. Do not modify them.
2. Choose exactly one action from allowed actions.
3. If there is no current solution, do not choose modify_solver_params.
4. Avoid repeating a recently unsuccessful move without a clear parameter change.
5. Treat the remaining budget as a hard limit for this turn.
6. Never request more than the remaining budget in any budget field. In particular, budget_request.time_limit_sec must be <= remaining_time_sec, budget_request.max_iters must be <= remaining_iters, and you must not assume any hidden extra budget.
7. Request budget only for the next action, and ask only for the minimum budget likely needed to test the move.
8. If remaining budget is too small for a meaningful solver run, or recent steps show low marginal value, choose stop.
9. Include only fields needed for the chosen action.
10. Output JSON only and follow the schema exactly.

Output schema:
{json_schema}
""".strip()


def get_toolchain_selection_prompt(
    user_goal_text: str,
    instance_summary: str,
    objective_layers: str,
    json_schema: str,
) -> str:
    return f"""
Legacy prompt. Prefer the next-action prompt in the new closed-loop agent.

User goal: {user_goal_text}
Instance summary: {instance_summary}
Objective layers: {objective_layers}
Output schema: {json_schema}

Choose a single best toolchain decision. Output JSON only.
""".strip()


def get_hyperparameter_tuning_prompt(
    solver_alg: str,
    instance_summary: str,
    solution_summary: str,
    json_schema: str,
) -> str:
    return f"""
Legacy prompt. Prefer the next-action prompt in the new closed-loop agent.

Inputs:
- solver_alg: {solver_alg}
- instance summary:
{instance_summary}
- solution summary:
{solution_summary}

Output schema:
{json_schema}

Return JSON only.
""".strip()
