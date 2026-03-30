"""Prompt templates for the LLM orchestrator."""

from __future__ import annotations

import json
from typing import Iterable


def get_system_prompt() -> str:
    return (
        "You are an optimization expert for multi-agent task assignment. "
        "Return strict JSON only and never emit fields outside the requested schema."
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
{_render_block(user_goal_text)}

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

Weighted ALNS architecture rules:
1. Destroy operators are only candidate generators. They do not rank tasks themselves.
2. Repair is split into task ordering and the single allowed position selector `filtered_best_position`.
3. Task score and insert score use the same shared metric weight vector `metric_weights`, but they have different roles:
   - task score decides which unassigned task to try next,
   - insert score decides the ranking of filtered insertion positions.
4. Do not pick a single destroy operator or a single repair task selector.
   You must assign positive prior weights over the full destroy operator pool and repair-task pool.
5. The solver keeps those LLM priors fixed for this run and combines them with adaptive rule weights internally:
   `w_final = (w_rule)^(1-lambda) * (w_llm)^(lambda)`.
   Use higher prior weights to bias sampling frequency, not to hard-disable adaptive learning.
6. `violation_risk` means local time-window / feasibility pressure:
   - assigned task removal: current slack or tardiness pressure,
   - unassigned task reinsertion: best reachable slack lower-bound pressure,
   - insertion move: minimum slack or violation pressure on the impacted suffix.
7. Do not invent metrics beyond:
   `priority`, `tw_tightness`, `violation_risk`, `energy_pressure`,
   `detour_cost`, `service_burden`, `feasibility_scarcity`, `route_instability`.
8. `repair_position_selector` must be `filtered_best_position`, meaning:
   - first enumerate loosely filtered candidate positions,
   - then rank them by insert score,
   - then run progressive strict evaluation on that ranked list,
   - then choose the best checked strict-feasible position.
9. Strict evaluation is only a refinement and feasibility-certification step for checked candidates. It must not be treated as an all-candidate position-ranking pass.
10. Output only fields defined in the schema. No commentary, no extra keys.

Decision rules:
1. Choose exactly one action from `allowed_actions`.
2. Objective layers are locked; optimize under them and never rewrite them.
3. Do not trade away an unresolved higher-priority layer for a lower-priority gain.
4. Use current incumbent metrics, deltas, and progress signals as the main evidence.
5. Request budget only for the next action and never exceed `remaining_budget`.
6. Prefer `stop` only when remaining budget is too small for a meaningful step or progress is clearly exhausted.
7. If no incumbent exists, prefer `build_initial_solution`.

Output:
- Return JSON only.
- Follow this schema exactly:
{json_schema}
""".strip()


def _render_block(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=True, indent=2)
