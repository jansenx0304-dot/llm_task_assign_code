"""JSON schema snippets used in prompts and action validation."""

from __future__ import annotations

from .operators import (
    ACCEPTANCE_MODES,
    DESTROY_CANDIDATE_GENERATORS,
    METRIC_FIELDS,
    METRIC_WEIGHT_BOUNDS,
    OPERATOR_PRIOR_BOUNDS,
    POLICY_BOUNDS,
    REPAIR_POSITION_SELECTORS,
    REPAIR_TASK_SELECTORS,
)


OBJECTIVE_LAYER_SCHEMA = """{
  "layers": [
    {
      "name": "feasibility",
      "metric": "...",
      "direction": "min|max"
    }
  ]
}"""


NEXT_ACTION_SCHEMA = """{
  "action_type": "build_initial_solution|run_weighted_alns|stop",
  "action_payload": {},
  "// build_initial_solution payload": {"init_method": "insert|sweep"},
  "// run_weighted_alns payload": {
    "destroy_generator_priors": {
      "global_assigned": "number in [0.10, 5.0]",
      "random_subset": "number in [0.10, 5.0]",
      "route_segment": "number in [0.10, 5.0]",
      "route_tail": "number in [0.10, 5.0]",
      "single_route": "number in [0.10, 5.0]"
    },
    "repair_task_selector_priors": {
      "weighted_priority_order": "number in [0.10, 5.0]",
      "regret2_order": "number in [0.10, 5.0]"
    },
    "repair_position_selector": "filtered_best_position",
    "strength_ratio": "number in [0.02, 0.40]",
    "metric_weights": {
      "priority": "number in [0, 5]",
      "tw_tightness": "number in [0, 5]",
      "violation_risk": "number in [0, 8]",
      "energy_pressure": "number in [0, 5]",
      "detour_cost": "number in [0, 5]",
      "service_burden": "number in [0, 5]",
      "feasibility_scarcity": "number in [0, 5]",
      "route_instability": "number in [0, 3]"
    },
    "acceptance": "greedy|threshold|sa",
    "accept_level": "number in [0, 1]",
    "reaction_factor": "number in [0.05, 0.40]",
    "prior_mix_lambda": "number in [0.20, 0.35]"
  },
  "// stop payload": {},
  "budget_request": {
    "time_limit_sec": "optional positive number",
    "max_iters": "optional positive integer"
  }
}"""


SCHEMA_CONSTRAINTS = {
    "next_action": {
        "action_type": [
            "build_initial_solution",
            "run_weighted_alns",
            "stop",
        ],
        "init_method": ["insert", "sweep"],
        "destroy_generator_priors": list(DESTROY_CANDIDATE_GENERATORS),
        "repair_task_selector_priors": list(REPAIR_TASK_SELECTORS),
        "repair_position_selector": list(REPAIR_POSITION_SELECTORS),
        "acceptance": list(ACCEPTANCE_MODES),
        "metric_fields": list(METRIC_FIELDS),
    },
    "metric_weights": dict(METRIC_WEIGHT_BOUNDS),
    "operator_prior_bounds": {
        "lower": OPERATOR_PRIOR_BOUNDS[0],
        "upper": OPERATOR_PRIOR_BOUNDS[1],
    },
    "policy_bounds": dict(POLICY_BOUNDS),
}
