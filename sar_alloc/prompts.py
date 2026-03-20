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

Your job for this turn is to choose exactly one high-level search action.

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
2. The current solution is the incumbent carried over from the previous outer iteration. Choose the next high-level move for improving that incumbent.
3. You are a closed-loop optimization agent choosing one high-level action for the orchestrator.
4. The orchestrator maps each high-level action to a fixed execution template with solver family, solver parameters, and a default budget slice.
5. Do not output any extra low-level solver parameters. Only output fields defined in the schema.
6. Choose exactly one action from allowed actions.
7. Use build_initial_solution only when there is no incumbent and an initial feasible solution still needs to be constructed.
8. run_alns is the high-level action for large-neighborhood search.
9. For run_alns, action_payload.search_mode=exploit means a more conservative move focused on improving near the current incumbent.
10. For run_alns, action_payload.search_mode=explore means a more aggressive move aimed at escaping the current region and widening the search.
11. run_vnd is the high-level action for local neighborhood descent and local refinement.
12. stop should be chosen only when remaining budget is too small for a meaningful next step, or recent history suggests continuing has very low marginal value.
13. action_payload.strength semantics:
   - light = more conservative, shorter, and cheaper
   - medium = default balanced choice
   - strong = deeper, stronger, and more expensive
14. If remaining budget is limited, prefer light or medium over strong.
15. Treat the remaining budget as a hard limit for this turn.
16. Never request more than the remaining budget in any budget field. In particular, budget_request.time_limit_sec must be <= remaining_time_sec, budget_request.max_iters must be <= remaining_iters, and you must not assume any hidden extra budget.
17. budget_request only adjusts the next step's budget slice. It does not control low-level solver parameters.
18. Request budget only for the next action, and ask only for the minimum budget likely needed to test the move.
19. Include only fields needed for the chosen action.
20. build_initial_solution uses action_payload.init_method = insert|sweep.
21. run_alns uses action_payload.search_mode = exploit|explore and action_payload.strength = light|medium|strong.
22. run_vnd uses action_payload.strength = light|medium|strong.
23. stop should use an empty payload.
24. Output JSON only and follow the schema exactly.

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
