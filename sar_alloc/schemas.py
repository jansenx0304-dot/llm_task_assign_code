"""JSON schema snippets used in prompts and action validation."""

from __future__ import annotations

from .operators import (
    ACCEPTANCE_MODES,
    DESTROY_CANDIDATE_GENERATORS,
    METRIC_FIELDS,
    METRIC_WEIGHT_BOUNDS,
    OPERATOR_PRIOR_BOUNDS,
    POLICY_BOUNDS,
    REPAIR_TASK_SELECTORS,
)


OBJECTIVE_LAYER_SCHEMA = """{
  "rationale": "short string explaining why these layers match the user goal",
  "layers": [
    {
      "name": "feasibility",
      "metric": "...",
      "direction": "min|max"
    }
  ]
}"""


NEXT_ACTION_SCHEMA = """{
  "rationale": "short string explaining why this is the best next action now",
  "// operator_intent semantics": "required for every action_type; split remove / reinsert / insert before setting numeric controls",
  "operator_intent": {
    "remove": "short phrase, under 12 words: what assigned tasks are most useful to remove now",
    "reinsert": "short phrase, under 12 words: what unassigned tasks should be reconsidered earlier now",
    "insert": "short phrase, under 12 words: what insertion positions are most promising to try first now"
  },
  "action_type": "build_initial_solution|run_alns|stop",
  "action_payload": {},
  "// build_initial_solution payload": {},
  "// run_alns payload": {
    "destroy_generator_priors": {
      "global_assigned": "number in [0.10, 5.0]",
      "random_subset": "number in [0.10, 5.0]",
      "route_segment": "number in [0.10, 5.0]",
      "route_tail": "number in [0.10, 5.0]",
      "single_route": "number in [0.10, 5.0]"
    },
    "// repair task semantics": "task score only decides which task to repair next",
    "repair_task_selector_priors": {
      "weighted_priority_order": "number in [0.10, 5.0]",
      "regret2_order": "number in [0.10, 5.0]"
    },
    "// remove_metric_weights": "ranks destroy removal candidates",
    "remove_metric_weights": {
      "priority": "number in [0, 5]",
      "tw_tightness": "number in [0, 5]",
      "violation_risk": "number in [0, 8]",
      "energy_pressure": "number in [0, 5]",
      "detour_cost": "number in [0, 5]",
      "service_burden": "number in [0, 5]",
      "feasibility_scarcity": "number in [0, 5]",
      "route_instability": "number in [0, 3]"
    },
    "// reinsert_metric_weights": "ranks unassigned tasks for repair order",
    "reinsert_metric_weights": {
      "priority": "number in [0, 5]",
      "tw_tightness": "number in [0, 5]",
      "violation_risk": "number in [0, 8]",
      "energy_pressure": "number in [0, 5]",
      "detour_cost": "number in [0, 5]",
      "service_burden": "number in [0, 5]",
      "feasibility_scarcity": "number in [0, 5]",
      "route_instability": "number in [0, 3]"
    },
    "// insert_metric_weights": "ranks candidate insertion positions for a chosen task",
    "insert_metric_weights": {
      "priority": "number in [0, 5]",
      "tw_tightness": "number in [0, 5]",
      "violation_risk": "number in [0, 8]",
      "energy_pressure": "number in [0, 5]",
      "detour_cost": "number in [0, 5]",
      "service_burden": "number in [0, 5]",
      "feasibility_scarcity": "number in [0, 5]",
      "route_instability": "number in [0, 3]"
    },
    "strength_ratio": "number in [0.02, 0.40]",
    "acceptance": "greedy|threshold|sa",
    "accept_level": "number in [0, 1]",
    "reaction_factor": "number in [0.05, 0.40]",
    "prior_mix_lambda": "number in [0.20, 0.35]"
  },
  "// stop payload": {},
  "budget_request": {
    "time_limit_sec": "required positive number for run_alns",
    "max_iters": "optional positive integer"
  }
}"""


SCHEMA_CONSTRAINTS = {
    "next_action": {
        "action_type": [
            "build_initial_solution",
            "run_alns",
            "stop",
        ],
        "operator_intent_fields": ["remove", "reinsert", "insert"],
        "operator_intent_max_words": 12,
        "destroy_generator_priors": list(DESTROY_CANDIDATE_GENERATORS),
        "repair_task_selector_priors": list(REPAIR_TASK_SELECTORS),
        "acceptance": list(ACCEPTANCE_MODES),
        "metric_weight_maps": [
            "remove_metric_weights",
            "reinsert_metric_weights",
            "insert_metric_weights",
        ],
        "metric_fields": list(METRIC_FIELDS),
    },
    "metric_weight_bounds": dict(METRIC_WEIGHT_BOUNDS),
    "operator_prior_bounds": {
        "lower": OPERATOR_PRIOR_BOUNDS[0],
        "upper": OPERATOR_PRIOR_BOUNDS[1],
    },
    "policy_bounds": dict(POLICY_BOUNDS),
}
