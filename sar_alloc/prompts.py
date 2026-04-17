"""Prompt templates for the LLM orchestrator."""

from __future__ import annotations

import json
from typing import Iterable


def get_system_prompt() -> str:
    return (
        "You are an optimization expert for multi-agent task assignment. "
        "Return strict JSON only and never emit fields outside the requested schema. "
        "Always include the requested `rationale` field as a concise string."
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
- Include `rationale` as a concise explanation of why these layers match the user goal.

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

The lexicographic objective is already locked.
Earlier objective layers strictly dominate later layers.

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

ALNS control semantics:
- Before setting numeric controls, first decide three operator intents: `remove`, `reinsert`, `insert`.
- `operator_intent.remove` describes what kind of already-assigned tasks are most useful to remove now.
- `operator_intent.reinsert` describes what kind of unassigned tasks should be reconsidered earlier now.
- `operator_intent.insert` describes what kind of insertion positions are most promising to try first now.
- Each intent must be a very short phrase.
- Each phrase must be under 12 words.
- Do not make the three intents say the same thing.
- Do not provide long explanations.
- Destroy operators are sampled from the full destroy pool using positive prior weights; do not choose a single destroy operator.
- Repair task selectors are sampled from the full repair-task pool using positive prior weights; do not choose a single repair task selector.
- `repair_position_selector` must remain `filtered_best_position`.
- `build_initial_solution.init_method` must remain `weighted_insert`.
- `weighted_insert` is the only initial construction method. It starts from the empty solution and follows the same task-score / insert-score philosophy as weighted repair; do not request sweep.
- These are three separate metric profiles for three operator-level decisions, not one global preference.
- `remove_metric_weights` rank removal candidates only.
- `reinsert_metric_weights` rank unassigned tasks only.
- `insert_metric_weights` rank insertion positions only.
- Weak answers have poor operator-role separation.
- Avoid answers where `remove` / `reinsert` / `insert` mean nearly the same thing.
- Avoid making all three metric profiles nearly identical.
- Avoid uniformly high weights everywhere.
- Use only these metric names exactly as provided:
  `priority`, `tw_tightness`, `violation_risk`, `energy_pressure`,
  `detour_cost`, `service_burden`, `feasibility_scarcity`, `route_instability`.
- Do not invent metrics, operators, enums, or extra fields.

Decision rules:
1. Choose exactly one action from `allowed_actions`.
2. Never rewrite or reinterpret the locked objective.
3. Never accept a worse unresolved higher-priority layer in exchange for a better lower-priority layer.
4. Base the decision mainly on current incumbent metrics, recent deltas, progress signals, and remaining budget.
5. Request budget only for the next action and never exceed `remaining_budget`.
6. If `action_type` is `run_alns`, `budget_request.time_limit_sec` is required and must be positive. `budget_request.max_iters` is optional.
7. Prefer `stop` only when progress is clearly exhausted or the remaining budget is too small for a meaningful next step.
8. If no incumbent exists, prefer `build_initial_solution`.
9. When selecting `run_alns`, use the policy fields to express a search bias, not a hard deterministic choice.

Output requirements:
- Output exactly one JSON object.
- No prose outside the JSON.
- Always include `rationale` as a concise explanation of why this is the best next action now.
- `operator_intent` is required.
- Always include top-level `operator_intent`.
- Keep `rationale` grounded in the incumbent metrics, recent progress, and remaining budget.
- Follow this schema exactly:
{json_schema}
""".strip()


def _render_block(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=True, indent=2)
