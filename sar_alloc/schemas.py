"""Prompt schema text and validation constants for LLM outputs."""

from __future__ import annotations

from .operators import (
    ACCEPTANCE_MODES,
    DESTROY_CANDIDATE_GENERATORS,
    LANDSCAPE_METRIC_FIELDS,
    METRIC_DIRECTIONS,
    OPERATOR_PRIOR_BOUNDS,
    POLICY_BOUNDS,
    REPAIR_POSITION_METRIC_FIELDS,
    REPAIR_TASK_SELECTORS,
    SEARCH_DIAGNOSIS_FIELDS,
)


def _csv(values: object) -> str:
    return ", ".join(f"`{value}`" for value in values)


def _range(name: str) -> str:
    lower, upper = POLICY_BOUNDS[name]
    return f"[{lower}, {upper}]"


def _metric_preference_schema(fields: object) -> str:
    lines = []
    for name in fields:
        lines.append(f'  "{name}": {{"score": 0-10 integer, "direction": one of {_csv(METRIC_DIRECTIONS)}}}')
    return "{\n" + ",\n".join(lines) + "\n}"


OBJECTIVE_LAYER_SCHEMA = """{
  "rationale": "short string",
  "layers": [
    {"name": "feasibility", "metric": "violation_total", "direction": "min"}
  ]
}
Constraints: no extra fields; direction is "min" or "max"; first metric must be violation_total."""


NEXT_ACTION_SCHEMA = f"""Return only JSON. Required top-level fields:
- rationale: short string
- operator_intent: {{"remove": "<=12 words", "reinsert": "<=12 words", "insert": "<=12 words"}}
- action_type: one of {_csv(("build_initial_solution", "run_alns", "stop"))}
- action_payload: object
- budget_request: object

For build_initial_solution or stop:
- action_payload must be {{}}

For run_alns, action_payload must contain exactly:
- search_diagnosis_scores: keys {_csv(SEARCH_DIAGNOSIS_FIELDS)}, each a 0-10 integer
- destroy_operator_scores: keys {_csv(DESTROY_CANDIDATE_GENERATORS)}, each a 0-10 integer
- repair_operator_scores: keys {_csv(REPAIR_TASK_SELECTORS)}, each a 0-10 integer
- destroy_metric_preferences: all landscape metrics with bound preference objects:
{_metric_preference_schema(LANDSCAPE_METRIC_FIELDS)}
- repair_task_metric_preferences: all landscape metrics with bound preference objects:
{_metric_preference_schema(LANDSCAPE_METRIC_FIELDS)}
- repair_position_metric_preferences: all position metrics with bound preference objects:
{_metric_preference_schema(REPAIR_POSITION_METRIC_FIELDS)}
- destroy_strength_score: 0-10 integer
- candidate_budget_score: 0-10 integer
- exploration_score: 0-10 integer
- acceptance: one of {_csv(ACCEPTANCE_MODES)}
- accept_level: number in {_range("accept_level")}
- reaction_factor: number in {_range("reaction_factor")}
- prior_mix_lambda: number in {_range("prior_mix_lambda")}

Rules:
- Do not output raw continuous metric weights.
- Metric preferences must bind score and direction inside each metric object.
- Operator score maps must cover every candidate operator exactly.
- Metric preference maps must cover every metric exactly.
- Old ALNS policy fields are invalid.
- For run_alns, budget_request.time_limit_sec is required and positive; budget_request.max_iters is optional positive integer.
- No extra fields."""


SCHEMA_CONSTRAINTS = {
    "next_action": {
        "action_type": [
            "build_initial_solution",
            "run_alns",
            "stop",
        ],
        "operator_intent_fields": ["remove", "reinsert", "insert"],
        "operator_intent_max_words": 12,
        "search_diagnosis_scores": list(SEARCH_DIAGNOSIS_FIELDS),
        "destroy_operator_scores": list(DESTROY_CANDIDATE_GENERATORS),
        "repair_operator_scores": list(REPAIR_TASK_SELECTORS),
        "landscape_metric_fields": list(LANDSCAPE_METRIC_FIELDS),
        "repair_position_metric_fields": list(REPAIR_POSITION_METRIC_FIELDS),
        "metric_directions": list(METRIC_DIRECTIONS),
        "score_bounds": {"lower": 0, "upper": 10},
        "acceptance": list(ACCEPTANCE_MODES),
    },
    "operator_prior_bounds": {
        "lower": OPERATOR_PRIOR_BOUNDS[0],
        "upper": OPERATOR_PRIOR_BOUNDS[1],
    },
    "policy_bounds": dict(POLICY_BOUNDS),
}
