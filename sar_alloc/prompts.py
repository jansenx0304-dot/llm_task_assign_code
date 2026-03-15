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
3. You are a high-level search mode selector, not a solver or parameter tuner.
4. Do not output solver names, operator families, or low-level numerical solver parameters.
5. The system will map your chosen high-level action to a concrete solver algorithm, solver parameters, and a default budget slice.
6. Choose exactly one action from allowed actions.
7. Use build_initial_solution only when there is no incumbent and an initial feasible solution still needs to be constructed.
8. improve_objective is the default action for normal incumbent-centered improvement.
9. intensify_search means a more local, conservative search around the current incumbent.
10. diversify_search means a broader, more exploratory search around the current incumbent.
11. For improve_objective, intensify_search, and diversify_search, you may set action_payload.mode_strength to light, medium, or strong.
12. mode_strength semantics:
   - light = more conservative, shorter, more local
   - medium = default balanced choice
   - strong = more aggressive, deeper, larger-range search
13. If remaining budget is limited, prefer light or medium over strong.
14. Treat the remaining budget as a hard limit for this turn.
15. Never request more than the remaining budget in any budget field. In particular, budget_request.time_limit_sec must be <= remaining_time_sec, budget_request.max_iters must be <= remaining_iters, and you must not assume any hidden extra budget.
16. budget_request only adjusts the next step's budget slice. It does not control low-level solver parameters.
17. Request budget only for the next action, and ask only for the minimum budget likely needed to test the move.
18. Choose stop only if remaining budget is too small for a meaningful next step, or recent history suggests the marginal value of continuing is very low.
19. Include only fields needed for the chosen action.
20. build_initial_solution uses action_payload.init_method = insert|sweep.
21. improve_objective, intensify_search, and diversify_search use action_payload.mode_strength = light|medium|strong.
22. stop should use an empty payload.
23. Output JSON only and follow the schema exactly.

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
