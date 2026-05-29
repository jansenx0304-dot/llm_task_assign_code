"""Compact prompt templates for the LLM orchestrator."""

from __future__ import annotations

import json
from typing import Iterable


SYSTEM_PROMPT = (
    "You control a multi-agent task-assignment optimizer. "
    "Return exactly one JSON object matching the requested schema. "
    "No markdown, no prose outside JSON, no extra fields."
)


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def get_objective_layer_prompt(
    user_goal_text: str,
    available_metrics: str,
    json_schema: str,
) -> str:
    payload = {
        "user_goal": user_goal_text,
        "available_metrics": available_metrics,
    }

    return f"""
TASK: choose a locked lexicographic objective.

RULES:
- First layer must be violation_total with direction=min.
- Use only available metric names.
- At most 5 layers; avoid redundant layers.
- Earlier layers strictly dominate later layers.

INPUT:
{_json(payload)}

OUTPUT SCHEMA:
{json_schema}
""".strip()


def get_next_action_prompt(
    user_goal_text: str,
    objective_layers: object,
    instance_summary: object,
    current_search_state: object,
    current_incumbent_metrics: object,
    delta_from_prev_incumbent: object,
    search_progress: object,
    destroy_landscape: object,
    remaining_budget: object,
    allowed_actions: Iterable[str],
    json_schema: str,
    repair_landscape: dict | None = None,
) -> str:
    context = {
        "user_goal": user_goal_text,
        "locked_objective_layers": objective_layers,
        "instance_summary": instance_summary,
        "current_search_state": current_search_state,
        "current_incumbent_metrics": current_incumbent_metrics,
        "delta_from_previous_incumbent": delta_from_prev_incumbent,
        "search_progress": search_progress,
        "destroy_landscape": destroy_landscape,
        "repair_landscape": repair_landscape or {},
        "remaining_budget": remaining_budget,
        "allowed_actions": list(str(x) for x in allowed_actions),
    }

    return f"""
TASK: choose the next controller action.

DECISION RULES:
- Choose exactly one action_type from allowed_actions.
- Do not change or reinterpret locked_objective_layers.
- Lexicographic rule: never trade a worse earlier layer for a better later layer.
- If no incumbent exists, choose build_initial_solution.
- Choose stop only when progress is exhausted or remaining budget is too small.
- For run_alns, give a complete policy and a positive budget_request.time_limit_sec not exceeding remaining_budget.

ALNS POLICY ROLES:
- operator_intent.remove: assigned tasks worth removing.
- operator_intent.reinsert: unassigned tasks to reconsider earlier.
- operator_intent.insert: insertion positions worth trying first.
- Each intent phrase must be short and different.
- Use integer scores from 0 to 10.
- Do not output raw continuous metric weights.
- For metric preferences, bind score and direction inside each metric object.
- prefer_high means candidates with larger metric values are preferred.
- prefer_low means candidates with smaller metric values are preferred.
- avoid_high means high values are risky and should be actively avoided.
- neutral means the metric should have no strong effect.
- destroy_operator_scores bias the sampling of destroy operators.
- destroy_metric_preferences rank complete destroy moves after a destroy operator has generated structurally valid moves.
- critical_block_removal always removes a continuous route block.
- route_rebalance_removal always removes a whole route within the destroy strength range.
- repair_operator_scores bias sampling among five repair operators:
  feasible_greedy_repair fast low-cost feasible repair;
  scarcity_first_repair prioritizes tasks with few feasible positions;
  regret_k_repair prioritizes high opportunity-loss tasks;
  bottleneck_targeted_repair targets the strongest non-neutral repair task metric;
  diversified_random_repair increases diversity when progress stagnates.
- repair_task_metric_preferences rank which removed task should be repaired first.
- repair_position_metric_preferences rank insertion positions.
- Use score variation: avoid assigning the same score to every operator.
- The solver compares feasible complete solutions; do not reason about infeasible repair.
- Use scores to bias operator sampling; do not select one deterministic operator.

CONTEXT:
{_json(context)}

OUTPUT SCHEMA:
{json_schema}
""".strip()


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)
