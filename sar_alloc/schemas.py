# sar_alloc/schemas.py
"""
JSON schema snippets used in prompts.
"""

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
  "action_type": "build_initial_solution|run_alns|run_vnd|stop",
  "action_payload": {},
  "// build_initial_solution payload": {"init_method": "insert|sweep"},
  "// run_alns payload": {
    "search_mode": "exploit|explore",
    "strength": "light|medium|strong"
  },
  "// run_vnd payload": {
    "strength": "light|medium|strong"
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
            "run_alns",
            "run_vnd",
            "stop",
        ],
        "init_method": ["insert", "sweep"],
        "search_mode": ["exploit", "explore"],
        "strength": ["light", "medium", "strong"],
    },
    "alns_params": {
        "destroy_frac": (0.02, 0.40),
        "reaction_factor": (0.05, 0.40),
        "acceptance": ["greedy", "threshold", "sa"],
        "accept_level": (0.0, 1.0),
    },
    "vnd_params": {
        "local_search_passes": (1, 8),
    },
}
