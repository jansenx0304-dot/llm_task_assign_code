"""
Prompt templates for the LLM orchestrator.
"""

from __future__ import annotations

import json
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
You are defining the locked lexicographic objective for a closed-loop optimization controller.

Inputs:
- User goal: {user_goal_text}
- Available metrics:
{available_metrics}
- Output schema:
{json_schema}

Rules:
- Feasibility must be the first layer and use `violation_total`.
- Use only provided metric names exactly as written.
- Use at most 5 layers.
- Prefer a minimal, non-redundant objective.
- Earlier layers must strictly dominate later layers.

Return JSON only.
""".strip()


def get_next_action_prompt(
    user_goal_text: str,
    objective_layers: object,
    instance_summary: object,
    current_search_state: object,
    current_incumbent_metrics: object,
    delta_from_prev_incumbent: object,
    search_progress: object,
    remaining_budget: object,
    allowed_actions: Iterable[str],
    json_schema: str,
) -> str:
    allowed = list(str(x) for x in allowed_actions)
    return f"""
You are the controller of a closed-loop optimization process for multi-agent task assignment.

Objective layers are locked. Earlier layers dominate later layers strictly.

Inputs:
- User goal:
{user_goal_text}

- Locked objective layers:
{_render_block(objective_layers)}

- Instance summary:
{_render_block(instance_summary)}

- Current search state:
{_render_block(current_search_state)}

- Current incumbent metrics:
{_render_block(current_incumbent_metrics)}

- Delta from previous incumbent:
{_render_block(delta_from_prev_incumbent)}

- Search progress summary:
{_render_block(search_progress)}

- Remaining budget:
{_render_block(remaining_budget)}

- Allowed actions:
{_render_block(allowed)}

Rules:
1. Choose exactly one action from allowed_actions.
2. Objective layers are locked; optimize under them, never rewrite them.
3. Do not trade away a higher-priority unresolved layer for a lower-priority gain.
4. Use current incumbent metrics, deltas, and progress signals as the main evidence.
5. Request budget only for the next action and never exceed remaining_budget.
6. Output only fields defined in the schema.
7. Prefer stop only when remaining budget is too small for a meaningful step or continuing has clearly low marginal value.
8. If no incumbent exists, prefer build_initial_solution over search actions.

Heuristics:
- Continuous incumbent progress favors exploit-mode ALNS.
- Stagnation, repeated flat steps, or strong plateau signals favor stronger or exploratory ALNS.
- Use ALNS exploit for incumbent-centered search; use ALNS explore to escape a stuck region.

Output:
- Return JSON only.
- Follow this schema exactly:
{json_schema}
""".strip()


def _render_block(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=True, indent=2)
