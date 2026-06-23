# LLM-ALNS Execution Report

> Status: finished    

## Run Config

```json
{
  "instance": "T100",
  "instance_path": "D:\\SJTU\\Smart\\LLM_Task_Assign\\llm_task_assign_code\\sar_alloc\\data\\instances\\demo\\seed42_T100_A6.json",
  "time_limit_sec": 10.0,
  "max_iters": 50,
  "max_step_calls": 4,
  "max_solver_calls": 4,
  "seed": 0,
  "dummy_llm": true,
  "allow_llm_fallback": false
}
```


---

## Live Timeline

### #001 [RUN] RUN_START

<details>
<summary>Open payload</summary>

```json
{
  "case_file": "case.json",
  "llm_mode": "dummy",
  "run_config": {
    "instance": "T100",
    "instance_path": "D:\\SJTU\\Smart\\LLM_Task_Assign\\llm_task_assign_code\\sar_alloc\\data\\instances\\demo\\seed42_T100_A6.json",
    "time_limit_sec": 10.0,
    "max_iters": 50,
    "max_step_calls": 4,
    "max_solver_calls": 4,
    "seed": 0,
    "dummy_llm": true,
    "allow_llm_fallback": false
  },
  "global_budget": {
    "step_calls": 4.0,
    "solver_calls": 4.0,
    "time_sec": 10.0,
    "iters": 50.0
  }
}
```

</details>

### #002 [PUB] PUBLIC_CANDIDATES

<details>
<summary>Open public candidates</summary>

```json
{
  "objective_candidates": [
    {
      "name": "missed_priority",
      "description": "Global solution quality metric."
    },
    {
      "name": "unassigned_count",
      "description": "Global solution quality metric."
    },
    {
      "name": "energy_total",
      "description": "Global solution quality metric."
    },
    {
      "name": "total_distance",
      "description": "Global solution quality metric."
    },
    {
      "name": "makespan",
      "description": "Global solution quality metric."
    },
    {
      "name": "route_balance",
      "description": "Global solution quality metric."
    }
  ],
  "insertion_operator_candidates": [
    {
      "name": "greedy_insertion",
      "description": "Public insertion operator."
    },
    {
      "name": "scarcity_first_insertion",
      "description": "Public insertion operator."
    },
    {
      "name": "regret_insertion",
      "description": "Public insertion operator."
    },
    {
      "name": "bottleneck_insertion",
      "description": "Public insertion operator."
    },
    {
      "name": "diversified_insertion",
      "description": "Public insertion operator."
    }
  ],
  "insertion_task_signal_candidates": [
    {
      "name": "priority_loss",
      "description": "Prefer unassigned tasks with high missed priority."
    },
    {
      "name": "scarcity_pressure",
      "description": "Prefer unassigned tasks with scarce feasible insertion options."
    },
    {
      "name": "regret_pressure",
      "description": "Prefer tasks whose alternatives are much worse than the best option."
    },
    {
      "name": "bottleneck_pressure",
      "description": "Prefer tasks with few feasible agents or positions."
    },
    {
      "name": "mobility_opportunity",
      "description": "Prefer tasks with better reassignment or insertion opportunity."
    }
  ],
  "insertion_position_signal_candidates": [
    {
      "name": "insert_cost",
      "description": "Public insertion-position signal."
    },
    {
      "name": "future_slack",
      "description": "Public insertion-position signal."
    },
    {
      "name": "route_balance_gain",
      "description": "Public insertion-position signal."
    },
    {
      "name": "local_coupling_penalty",
      "description": "Public insertion-position signal."
    },
    {
      "name": "diversity_gain",
      "description": "Public insertion-position signal."
    }
  ],
  "destroy_operator_candidates": [
    {
      "name": "random_removal",
      "description": "Public destroy operator."
    },
    {
      "name": "worst_task_removal",
      "description": "Public destroy operator."
    },
    {
      "name": "related_cluster_removal",
      "description": "Public destroy operator."
    },
    {
      "name": "critical_block_removal",
      "description": "Public destroy operator."
    },
    {
      "name": "route_rebalance_removal",
      "description": "Public destroy operator."
    }
  ],
  "destroy_signal_candidates": [
    {
      "name": "cost_pressure",
      "description": "Prefer removing assigned structures with high cost release."
    },
    {
      "name": "coupling_pressure",
      "description": "Prefer removing strongly related local structures."
    },
    {
      "name": "route_balance_pressure",
      "description": "Prefer removing from overloaded or imbalanced routes."
    },
    {
      "name": "mobility_opportunity",
      "description": "Prefer removing tasks that are easy to reinsert elsewhere."
    },
    {
      "name": "scarcity_protection",
      "description": "Protect scarce assigned tasks from removal by reducing their destroy score."
    }
  ],
  "acceptance_candidates": [
    {
      "name": "greedy",
      "description": "Public ALNS acceptance mode."
    },
    {
      "name": "threshold",
      "description": "Public ALNS acceptance mode."
    },
    {
      "name": "sa",
      "description": "Public ALNS acceptance mode."
    }
  ],
  "feasibility_mode_candidates": [
    {
      "name": "strict",
      "description": ""
    },
    {
      "name": "relaxed_recoverable",
      "description": ""
    },
    {
      "name": "recovery_only",
      "description": ""
    }
  ],
  "relaxable_violation_candidates": [
    {
      "name": "time_window",
      "description": ""
    },
    {
      "name": "energy",
      "description": ""
    }
  ]
}
```

</details>

### #003 [OBS] SUPERVISOR_KICKOFF_OBSERVATION

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O0",
  "frame_type": "supervisor_kickoff",
  "role": "supervisor",
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "budget_caps": {
    "max_solver_actions": 4,
    "max_time_sec": 10.0,
    "max_iters": 50
  },
  "problem_profile": {
    "num_tasks": 100,
    "num_agents": 6,
    "priority_mass": 198.0,
    "high_priority_task_count": 36,
    "zero_capable_task_count": 0,
    "static_capability_scarce_task_count": 0,
    "static_capability_scarce_priority_mass": 0,
    "time_window_risk": "low",
    "energy_risk": "low",
    "dominant_risk": "energy"
  },
  "relaxation_reference": {
    "time_window_median_width": 100.0,
    "agent_energy_median": 13967.103715264191
  },
  "allowed_contract_types": [
    "initial_construction"
  ],
  "allowed_objective_metrics": [
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance"
  ],
  "next_contract_resource_limits": {
    "max_solver_actions_allowed": 4,
    "max_time_sec_allowed": 10.0,
    "max_iters_allowed": 50
  }
}
```

</details>

### #004 [PROMPT] SUPERVISOR_KICKOFF_PROMPT

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SUPERVISOR_KICKOFF

INSTRUCTION:
You are the stage supervisor. Use only the observation fields. Output a global objective and one executable initial contract. Operational fields will be compiled and enforced. Put human-readable text only in explanation.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O0",
    "frame_type": "supervisor_kickoff",
    "role": "supervisor",
    "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
    "budget_caps": {
      "max_solver_actions": 4,
      "max_time_sec": 10.0,
      "max_iters": 50
    },
    "problem_profile": {
      "num_tasks": 100,
      "num_agents": 6,
      "priority_mass": 198.0,
      "high_priority_task_count": 36,
      "zero_capable_task_count": 0,
      "static_capability_scarce_task_count": 0,
      "static_capability_scarce_priority_mass": 0,
      "time_window_risk": "low",
      "energy_risk": "low",
      "dominant_risk": "energy"
    },
    "relaxation_reference": {
      "time_window_median_width": 100.0,
      "agent_energy_median": 13967.103715264191
    },
    "allowed_contract_types": [
      "initial_construction"
    ],
    "allowed_objective_metrics": [
      "missed_priority",
      "unassigned_count",
      "energy_total",
      "total_distance",
      "makespan",
      "route_balance"
    ],
    "next_contract_resource_limits": {
      "max_solver_actions_allowed": 4,
      "max_time_sec_allowed": 10.0,
      "max_iters_allowed": 50
    }
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "Supervisor kickoff decision at the beginning of a run.",
  "properties": {
    "supervisor_decision": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "const": "start_run"
        },
        "global_objective": {
          "type": "object",
          "description": "Run-level objective used to compare global best solutions.",
          "properties": {
            "objective_layers": {
              "type": "array",
              "description": "Ordered global quality metrics. Earlier metrics dominate later metrics.",
              "minItems": 1,
              "maxItems": 4,
              "items": {
                "type": "string",
                "enum": [
                  "missed_priority",
                  "unassigned_count",
                  "energy_total",
                  "total_distance",
                  "makespan",
                  "route_balance"
                ]
              }
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "objective_layers"
          ],
          "additionalProperties": false
        },
        "next_contract": {
          "type": "object",
          "description": "A supervisor-issued executable search contract.",
          "properties": {
            "contract_type": {
              "type": "string",
              "enum": [
                "initial_construction",
                "alns_search",
                "recovery",
                "final_refinement"
              ]
            },
            "objective_layers": {
              "type": "array",
              "minItems": 1,
              "maxItems": 4,
              "items": {
                "type": "string",
                "enum": [
                  "missed_priority",
                  "unassigned_count",
                  "energy_total",
                  "total_distance",
                  "makespan",
                  "route_balance"
                ]
              }
            },
            "feasibility_control": {
              "type": "object",
              "description": "Stage-level feasibility handling selected by Supervisor.",
              "properties": {
                "mode": {
                  "type": "string",
                  "enum": [
                    "strict",
                    "relaxed_recoverable",
                    "recovery_only"
                  ],
                  "description": "Feasibility mode for this contract."
                },
                "relaxation_ratios": {
                  "type": "array",
                  "description": "Temporary recoverable relaxation ratios. Used by relaxed_recoverable.",
                  "maxItems": 2,
                  "items": {
                    "type": "object",
                    "description": "One temporary recoverable relaxation allowance.",
                    "properties": {
                      "violation_type": {
                        "type": "string",
                        "enum": [
                          "time_window",
                          "energy"
                        ],
                        "description": "Relaxable violation type."
                      },
                      "max_ratio": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 0.3,
                        "description": "Normalized temporary allowance for this violation type."
                      }
                    },
                    "required": [
                      "violation_type",
                      "max_ratio"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "mode",
                "relaxation_ratios"
              ],
              "additionalProperties": false
            },
            "target_policy": {
              "type": "object",
              "description": "Executable target preference for the next contract.",
              "properties": {
                "preferred_target_kinds": {
                  "type": "array",
                  "minItems": 0,
                  "maxItems": 4,
                  "items": {
                    "type": "string",
                    "enum": [
                      "unassigned_priority",
                      "insertion_scarce_unassigned",
                      "energy_debt",
                      "time_window_debt",
                      "route_balance"
                    ]
                  }
                }
              },
              "required": [
                "preferred_target_kinds"
              ],
              "additionalProperties": false
            },
            "protected_metrics": {
              "type": "array",
              "maxItems": 4,
              "items": {
                "type": "object",
                "description": "Hard non-worsening bound for this contract. max_worsen is measured relative to contract_start_quality. A violating candidate is ineligible for trial acceptance, action-best, returned-working, or best updates.",
                "properties": {
                  "metric": {
                    "type": "string",
                    "enum": [
                      "missed_priority",
                      "unassigned_count",
                      "energy_total",
                      "total_distance",
                      "makespan",
                      "route_balance"
                    ]
                  },
                  "max_worsen": {
                    "type": "number",
                    "minimum": 0.0
                  }
                },
                "required": [
                  "metric",
                  "max_worsen"
                ],
                "additionalProperties": false
              }
            },
            "resource_policy": {
              "type": "object",
              "description": "Executable resource limits for this contract.",
              "properties": {
                "min_actions": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 4
                },
                "max_actions": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 4
                },
                "max_iters": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 50
                },
                "max_time_sec": {
                  "type": "number",
                  "exclusiveMinimum": 0,
                  "maximum": 10.0
                }
              },
              "required": [
                "min_actions",
                "max_actions",
                "max_iters",
                "max_time_sec"
              ],
              "additionalProperties": false
            },
            "exit_conditions": {
              "type": "object",
              "description": "Typed success and failure conditions.",
              "properties": {
                "success": {
                  "type": "array",
                  "maxItems": 4,
                  "items": {
                    "type": "object",
                    "description": "Typed condition evaluated by ContractMonitor.",
                    "properties": {
                      "condition_id": {
                        "type": "string",
                        "description": "Stable id unique inside this contract condition set."
                      },
                      "source": {
                        "type": "string",
                        "enum": [
                          "progress.solver_actions",
                          "progress.iters_used",
                          "progress.time_used_sec",
                          "last.intent_status",
                          "last.dominant_blocker",
                          "last.improvement_flags.run_global_best_improved",
                          "aggregate.achieved",
                          "aggregate.partial",
                          "aggregate.not_achieved",
                          "aggregate.regressed",
                          "aggregate.solver_requested_review",
                          "working.is_feasible",
                          "working.missed_priority",
                          "working.unassigned_count",
                          "working.energy_total",
                          "working.total_distance",
                          "working.makespan",
                          "working.route_balance",
                          "best_feasible.exists",
                          "best_feasible.missed_priority",
                          "best_feasible.unassigned_count",
                          "best_feasible.energy_total",
                          "best_feasible.total_distance",
                          "best_feasible.makespan",
                          "best_feasible.route_balance"
                        ],
                        "description": "Executable source path read by ContractMonitor."
                      },
                      "op": {
                        "type": "string",
                        "enum": [
                          "<",
                          "<=",
                          "==",
                          "!=",
                          ">=",
                          ">"
                        ]
                      },
                      "value": {
                        "type": [
                          "number",
                          "string",
                          "boolean"
                        ]
                      },
                      "window": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20
                      }
                    },
                    "required": [
                      "condition_id",
                      "source",
                      "op",
                      "value",
                      "window"
                    ],
                    "additionalProperties": false
                  }
                },
                "failure": {
                  "type": "array",
                  "maxItems": 4,
                  "items": {
                    "type": "object",
                    "description": "Typed condition evaluated by ContractMonitor.",
                    "properties": {
                      "condition_id": {
                        "type": "string",
                        "description": "Stable id unique inside this contract condition set."
                      },
                      "source": {
                        "type": "string",
                        "enum": [
                          "progress.solver_actions",
                          "progress.iters_used",
                          "progress.time_used_sec",
                          "last.intent_status",
                          "last.dominant_blocker",
                          "last.improvement_flags.run_global_best_improved",
                          "aggregate.achieved",
                          "aggregate.partial",
                          "aggregate.not_achieved",
                          "aggregate.regressed",
                          "aggregate.solver_requested_review",
                          "working.is_feasible",
                          "working.missed_priority",
                          "working.unassigned_count",
                          "working.energy_total",
                          "working.total_distance",
                          "working.makespan",
                          "working.route_balance",
                          "best_feasible.exists",
                          "best_feasible.missed_priority",
                          "best_feasible.unassigned_count",
                          "best_feasible.energy_total",
                          "best_feasible.total_distance",
                          "best_feasible.makespan",
                          "best_feasible.route_balance"
                        ],
                        "description": "Executable source path read by ContractMonitor."
                      },
                      "op": {
                        "type": "string",
                        "enum": [
                          "<",
                          "<=",
                          "==",
                          "!=",
                          ">=",
                          ">"
                        ]
                      },
                      "value": {
                        "type": [
                          "number",
                          "string",
                          "boolean"
                        ]
                      },
                      "window": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20
                      }
                    },
                    "required": [
                      "condition_id",
                      "source",
                      "op",
                      "value",
                      "window"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "success",
                "failure"
              ],
              "additionalProperties": false
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "contract_type",
            "objective_layers",
            "feasibility_control",
            "target_policy",
            "protected_metrics",
            "resource_policy",
            "exit_conditions"
          ],
          "additionalProperties": false
        }
      },
      "required": [
        "action",
        "global_objective",
        "next_contract"
      ],
      "additionalProperties": false
    }
  },
  "required": [
    "supervisor_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #005 [RAW] SUPERVISOR_KICKOFF_RAW_OUTPUT

<details>
<summary>Open raw LLM output</summary>

```text
{"supervisor_decision": {"action": "start_run", "global_objective": {"objective_layers": ["missed_priority", "unassigned_count", "energy_total"], "explanation": {"summary": "Prioritize coverage, then energy."}}, "next_contract": {"contract_type": "initial_construction", "objective_layers": ["missed_priority", "unassigned_count", "energy_total"], "feasibility_control": {"mode": "strict", "relaxation_ratios": []}, "target_policy": {"preferred_target_kinds": ["unassigned_priority", "energy_debt"]}, "protected_metrics": [{"metric": "unassigned_count", "max_worsen": 0}], "resource_policy": {"min_actions": 1, "max_actions": 1, "max_time_sec": 5.0, "max_iters": 1}, "exit_conditions": {"success": [{"condition_id": "S_initial", "source": "last.intent_status", "op": "==", "value": "achieved", "window": 1}], "failure": [{"condition_id": "F_initial", "source": "last.intent_status", "op": "==", "value": "not_achieved", "window": 1}]}, "explanation": {"stage_summary": "Build a coverage-oriented initial solution."}}}}
```

</details>

### #006 [OK] SUPERVISOR_KICKOFF_VALIDATED_PAYLOAD

```json
{
  "supervisor_decision": {
    "action": "start_run",
    "global_objective": {
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "explanation": {
        "summary": "Prioritize coverage, then energy."
      }
    },
    "next_contract": {
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_control": {
        "mode": "strict",
        "relaxation_ratios": []
      },
      "target_policy": {
        "preferred_target_kinds": [
          "unassigned_priority",
          "energy_debt"
        ]
      },
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "resource_policy": {
        "min_actions": 1,
        "max_actions": 1,
        "max_time_sec": 5.0,
        "max_iters": 1
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "S_initial",
            "source": "last.intent_status",
            "op": "==",
            "value": "achieved",
            "window": 1
          }
        ],
        "failure": [
          {
            "condition_id": "F_initial",
            "source": "last.intent_status",
            "op": "==",
            "value": "not_achieved",
            "window": 1
          }
        ]
      },
      "explanation": {
        "stage_summary": "Build a coverage-oriented initial solution."
      }
    }
  }
}
```

### #007 [TRACE] GLOBAL_OBJECTIVE_APPLIED

<details>
<summary>Open payload</summary>

```json
[
  {
    "name": "missed_priority",
    "metric": "missed_priority",
    "direction": "min"
  },
  {
    "name": "unassigned_count",
    "metric": "unassigned_count",
    "direction": "min"
  },
  {
    "name": "energy_total",
    "metric": "energy_total",
    "direction": "min"
  }
]
```

</details>

### #008 [OK] VALIDATED_FEASIBILITY_CONTROL | C001

```json
{
  "mode": "strict",
  "relaxation_ratios": []
}
```

### #009 [COMP] COMPILED_FEASIBILITY_POLICY | C001

```json
{
  "mode": "strict"
}
```

### #010 [COMP] COMPILED_CONTRACT | C001

```json
{
  "contract_id": "C001",
  "contract_type": "initial_construction",
  "objective_layers": [
    {
      "metric": "missed_priority",
      "direction": "min"
    },
    {
      "metric": "unassigned_count",
      "direction": "min"
    },
    {
      "metric": "energy_total",
      "direction": "min"
    }
  ],
  "feasibility_control": {
    "mode": "strict",
    "relaxation_ratios": [],
    "compiled_policy_summary": {}
  },
  "feasibility_policy": {
    "mode": "strict"
  },
  "target_policy": {
    "preferred_target_kinds": [
      "unassigned_priority",
      "energy_debt"
    ]
  },
  "protected_metrics": [
    {
      "metric": "unassigned_count",
      "max_worsen": 0
    }
  ],
  "protected_metric_baseline": {
    "missed_priority": 198.0,
    "unassigned_count": 100.0,
    "energy_total": 0.0,
    "total_distance": 0.0,
    "makespan": 0.0,
    "route_balance": 0.0
  },
  "resource_policy": {
    "min_actions": 1,
    "max_actions": 1,
    "max_time_sec": 5.0,
    "max_iters": 1
  },
  "exit_conditions": {
    "success": [
      {
        "condition_id": "S_initial",
        "source": "last.intent_status",
        "op": "==",
        "value": "achieved",
        "window": 1
      }
    ],
    "failure": [
      {
        "condition_id": "F_initial",
        "source": "last.intent_status",
        "op": "==",
        "value": "not_achieved",
        "window": 1
      }
    ]
  },
  "explanation": {
    "stage_summary": "Build a coverage-oriented initial solution."
  }
}
```

### #011 [OBS] SOLVER_OBSERVATION | C001 / SOLVER 000

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O1",
  "frame_type": "solver_initial_construction",
  "role": "solver",
  "step_index": 0,
  "contract_view": {
    "contract_id": "C001",
    "contract_type": "initial_construction",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 198.0,
      "unassigned_count": 100.0,
      "energy_total": 0.0,
      "total_distance": 0.0,
      "makespan": 0.0,
      "route_balance": 0.0
    },
    "remaining_resources": {
      "actions": 1,
      "time_sec": 5.0,
      "iters": 1,
      "min_actions_remaining": 1
    }
  },
  "task_buildability_view": {
    "target_buckets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 100,
        "priority_mass": 198.0,
        "top_tasks": [
          {
            "task_id": 0,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 5,
            "priority": 3.0,
            "capable_agents": 4,
            "candidate_positions": 4,
            "feasible_positions": 4,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 11,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 12,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 14,
            "priority": 3.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          }
        ],
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "priority_loss",
            "scarcity_pressure"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack",
            "insert_cost"
          ]
        }
      },
      {
        "target_id": "T_scarce_unassigned",
        "kind": "insertion_scarce_unassigned",
        "task_count": 3,
        "priority_mass": 5.0,
        "top_tasks": [
          {
            "task_id": 14,
            "priority": 3.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 1,
            "priority": 1.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 15,
            "priority": 1.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          }
        ],
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ]
        }
      }
    ],
    "inactive_target_summary": []
  },
  "insertion_position_landscape": {
    "candidate_position_count": {
      "p25": 3.0,
      "p50": 4.0,
      "p75": 5.0,
      "low_count": 0,
      "zero_count": 0
    },
    "feasible_position_count": {
      "p25": 3.0,
      "p50": 4.0,
      "p75": 5.0,
      "low_count": 0,
      "zero_count": 0
    },
    "top_failed_tasks": []
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "task_count": 100,
      "priority_mass": 198.0,
      "top_tasks": [
        {
          "task_id": 0,
          "priority": 3.0,
          "capable_agents": 3,
          "candidate_positions": 3,
          "feasible_positions": 3,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 5,
          "priority": 3.0,
          "capable_agents": 4,
          "candidate_positions": 4,
          "feasible_positions": 4,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 11,
          "priority": 3.0,
          "capable_agents": 3,
          "candidate_positions": 3,
          "feasible_positions": 3,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 12,
          "priority": 3.0,
          "capable_agents": 3,
          "candidate_positions": 3,
          "feasible_positions": 3,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 14,
          "priority": 3.0,
          "capable_agents": 2,
          "candidate_positions": 2,
          "feasible_positions": 2,
          "dominant_reason": "limited_insertion_options"
        }
      ],
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "priority_loss",
          "scarcity_pressure"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack",
          "insert_cost"
        ]
      }
    },
    {
      "target_id": "T_scarce_unassigned",
      "kind": "insertion_scarce_unassigned",
      "task_count": 3,
      "priority_mass": 5.0,
      "top_tasks": [
        {
          "task_id": 14,
          "priority": 3.0,
          "capable_agents": 2,
          "candidate_positions": 2,
          "feasible_positions": 2,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 2,
          "feasible_positions": 2,
          "dominant_reason": "limited_insertion_options"
        },
        {
          "task_id": 15,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 2,
          "feasible_positions": 2,
          "dominant_reason": "limited_insertion_options"
        }
      ],
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ]
      }
    },
    {
      "target_id": "contract_review",
      "kind": "contract_review",
      "recommended_controls": {}
    }
  ],
  "last_action_verification": {
    "exists": false
  },
  "action_space": {
    "allowed_actions": [
      "construct_initial",
      "request_supervisor_review"
    ],
    "allowed_insertion_operators": [
      "greedy_insertion",
      "scarcity_first_insertion",
      "regret_insertion",
      "bottleneck_insertion",
      "diversified_insertion"
    ],
    "allowed_task_signals": [
      "priority_loss",
      "scarcity_pressure",
      "regret_pressure",
      "bottleneck_pressure",
      "mobility_opportunity"
    ],
    "allowed_position_signals": [
      "insert_cost",
      "future_slack",
      "route_balance_gain",
      "local_coupling_penalty",
      "diversity_gain"
    ]
  },
  "usable_memory": []
}
```

</details>

### #012 [PROMPT] SOLVER_PROMPT | C001 / SOLVER 000

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SOLVER

INSTRUCTION:
Choose one allowed action. If executing a solver action, choose one target_id from decision_targets and choose controls only from action_space. Every operational field will be compiled and executed exactly. Each score name must be selected from the enum of that exact output field. Do not move names between destroy operator, destroy signal, insertion operator, task signal, and position signal fields.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O1",
    "frame_type": "solver_initial_construction",
    "role": "solver",
    "step_index": 0,
    "contract_view": {
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 198.0,
        "unassigned_count": 100.0,
        "energy_total": 0.0,
        "total_distance": 0.0,
        "makespan": 0.0,
        "route_balance": 0.0
      },
      "remaining_resources": {
        "actions": 1,
        "time_sec": 5.0,
        "iters": 1,
        "min_actions_remaining": 1
      }
    },
    "task_buildability_view": {
      "target_buckets": [
        {
          "target_id": "T_unassigned_priority",
          "kind": "unassigned_priority",
          "task_count": 100,
          "priority_mass": 198.0,
          "top_tasks": [
            {
              "task_id": 0,
              "priority": 3.0,
              "capable_agents": 3,
              "candidate_positions": 3,
              "feasible_positions": 3,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 5,
              "priority": 3.0,
              "capable_agents": 4,
              "candidate_positions": 4,
              "feasible_positions": 4,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 11,
              "priority": 3.0,
              "capable_agents": 3,
              "candidate_positions": 3,
              "feasible_positions": 3,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 12,
              "priority": 3.0,
              "capable_agents": 3,
              "candidate_positions": 3,
              "feasible_positions": 3,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 14,
              "priority": 3.0,
              "capable_agents": 2,
              "candidate_positions": 2,
              "feasible_positions": 2,
              "dominant_reason": "limited_insertion_options"
            }
          ],
          "recommended_controls": {
            "insertion_control.task_signal_scores": [
              "priority_loss",
              "scarcity_pressure"
            ],
            "insertion_control.position_signal_scores": [
              "future_slack",
              "insert_cost"
            ]
          }
        },
        {
          "target_id": "T_scarce_unassigned",
          "kind": "insertion_scarce_unassigned",
          "task_count": 3,
          "priority_mass": 5.0,
          "top_tasks": [
            {
              "task_id": 14,
              "priority": 3.0,
              "capable_agents": 2,
              "candidate_positions": 2,
              "feasible_positions": 2,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 1,
              "priority": 1.0,
              "capable_agents": 2,
              "candidate_positions": 2,
              "feasible_positions": 2,
              "dominant_reason": "limited_insertion_options"
            },
            {
              "task_id": 15,
              "priority": 1.0,
              "capable_agents": 2,
              "candidate_positions": 2,
              "feasible_positions": 2,
              "dominant_reason": "limited_insertion_options"
            }
          ],
          "recommended_controls": {
            "insertion_control.task_signal_scores": [
              "scarcity_pressure",
              "priority_loss"
            ],
            "insertion_control.position_signal_scores": [
              "future_slack"
            ]
          }
        }
      ],
      "inactive_target_summary": []
    },
    "insertion_position_landscape": {
      "candidate_position_count": {
        "p25": 3.0,
        "p50": 4.0,
        "p75": 5.0,
        "low_count": 0,
        "zero_count": 0
      },
      "feasible_position_count": {
        "p25": 3.0,
        "p50": 4.0,
        "p75": 5.0,
        "low_count": 0,
        "zero_count": 0
      },
      "top_failed_tasks": []
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 100,
        "priority_mass": 198.0,
        "top_tasks": [
          {
            "task_id": 0,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 5,
            "priority": 3.0,
            "capable_agents": 4,
            "candidate_positions": 4,
            "feasible_positions": 4,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 11,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 12,
            "priority": 3.0,
            "capable_agents": 3,
            "candidate_positions": 3,
            "feasible_positions": 3,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 14,
            "priority": 3.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          }
        ],
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "priority_loss",
            "scarcity_pressure"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack",
            "insert_cost"
          ]
        }
      },
      {
        "target_id": "T_scarce_unassigned",
        "kind": "insertion_scarce_unassigned",
        "task_count": 3,
        "priority_mass": 5.0,
        "top_tasks": [
          {
            "task_id": 14,
            "priority": 3.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 1,
            "priority": 1.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          },
          {
            "task_id": 15,
            "priority": 1.0,
            "capable_agents": 2,
            "candidate_positions": 2,
            "feasible_positions": 2,
            "dominant_reason": "limited_insertion_options"
          }
        ],
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ]
        }
      },
      {
        "target_id": "contract_review",
        "kind": "contract_review",
        "recommended_controls": {}
      }
    ],
    "last_action_verification": {
      "exists": false
    },
    "action_space": {
      "allowed_actions": [
        "construct_initial",
        "request_supervisor_review"
      ],
      "allowed_insertion_operators": [
        "greedy_insertion",
        "scarcity_first_insertion",
        "regret_insertion",
        "bottleneck_insertion",
        "diversified_insertion"
      ],
      "allowed_task_signals": [
        "priority_loss",
        "scarcity_pressure",
        "regret_pressure",
        "bottleneck_pressure",
        "mobility_opportunity"
      ],
      "allowed_position_signals": [
        "insert_cost",
        "future_slack",
        "route_balance_gain",
        "local_coupling_penalty",
        "diversity_gain"
      ]
    },
    "usable_memory": []
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "One Solver decision under the active supervisor contract.",
  "properties": {
    "solver_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "construct_initial"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_scarce_unassigned",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "insertion_control": {
              "type": "object",
              "description": "Executable insertion controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for insertion operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for insertion operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "greedy_insertion",
                          "scarcity_first_insertion",
                          "regret_insertion",
                          "bottleneck_insertion",
                          "diversified_insertion"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "task_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing the next task.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing the next task.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "priority_loss",
                          "scarcity_pressure",
                          "regret_pressure",
                          "bottleneck_pressure",
                          "mobility_opportunity"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "position_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing an insertion position.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing an insertion position.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "insert_cost",
                          "future_slack",
                          "route_balance_gain",
                          "local_coupling_penalty",
                          "diversity_gain"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "operator_scores",
                "task_signal_scores",
                "position_signal_scores"
              ],
              "additionalProperties": false
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id",
            "insertion_control"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "request_supervisor_review"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_scarce_unassigned",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "solver_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #013 [RAW] SOLVER_RAW_OUTPUT | C001 / SOLVER 000

<details>
<summary>Open raw LLM output</summary>

```text
{"solver_decision": {"action": "construct_initial", "target_id": "T_unassigned_priority", "insertion_control": {"operator_scores": [{"name": "scarcity_first_insertion", "score": 8}, {"name": "regret_insertion", "score": 7}], "task_signal_scores": [{"name": "priority_loss", "score": 9}, {"name": "scarcity_pressure", "score": 8}], "position_signal_scores": [{"name": "insert_cost", "score": 8}, {"name": "future_slack", "score": 7}]}, "explanation": {"reason_summary": "Use priority and scarcity aware construction."}}}
```

</details>

### #014 [OK] SOLVER_VALIDATED_PAYLOAD | C001 / SOLVER 000

```json
{
  "solver_decision": {
    "action": "construct_initial",
    "target_id": "T_unassigned_priority",
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 8
        },
        {
          "name": "regret_insertion",
          "score": 7
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 8
        }
      ],
      "position_signal_scores": [
        {
          "name": "insert_cost",
          "score": 8
        },
        {
          "name": "future_slack",
          "score": 7
        }
      ]
    },
    "explanation": {
      "reason_summary": "Use priority and scarcity aware construction."
    }
  }
}
```

### #015 [COMP] RUNTIME_CONTROL_MANIFEST | C001 / SOLVER 000

```json
{
  "manifest_id": "R1",
  "source_decision_id": "D1",
  "contract_id": "C001",
  "action": "construct_initial",
  "target_id": "T_unassigned_priority",
  "trace_id": "X1",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 1,
      "max_time_sec": 5.0,
      "max_iters": 1
    },
    "protected_metric_baseline": {
      "missed_priority": 198.0,
      "unassigned_count": 100.0,
      "energy_total": 0.0,
      "total_distance": 0.0,
      "makespan": 0.0,
      "route_balance": 0.0
    },
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 100.0,
        "max_worsen": 0.0
      }
    ],
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #016 [COMP] COMPILED_INITIAL_POLICY | C001 / SOLVER 000

```json
{
  "operator_weights": {
    "greedy_insertion": 2,
    "scarcity_first_insertion": 8,
    "regret_insertion": 7,
    "bottleneck_insertion": 2,
    "diversified_insertion": 2
  },
  "task_signal_weights": {
    "priority_loss": 9,
    "scarcity_pressure": 8,
    "regret_pressure": 0,
    "bottleneck_pressure": 0,
    "mobility_opportunity": 0
  },
  "position_signal_weights": {
    "insert_cost": 8,
    "future_slack": 7,
    "route_balance_gain": 0,
    "local_coupling_penalty": 0,
    "diversity_gain": 0
  }
}
```

### #017 [INIT] INITIAL_INSERTION_RESULT | C001 / SOLVER 000

```json
{
  "result": {
    "is_feasible": true,
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      }
    },
    "quality_summary": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "feasibility_summary": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_by_type": {
        "capability": 0.0,
        "time_window": 0.0,
        "energy": 0.0
      },
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      }
    }
  },
  "trace": {
    "trace_id": "X1",
    "kind": "initial_insertion",
    "candidate_task_count": 100,
    "attempted_task_count": 4930,
    "inserted_task_count": 84,
    "uninserted_task_count": 16,
    "zero_candidate_task_count": 701,
    "hard_filter_rejected_count": 6,
    "top_failed_tasks": [
      {
        "task_id": 1,
        "priority": 1.0,
        "capable_agents": 2,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 8,
        "priority": 1.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 9,
        "priority": 1.0,
        "capable_agents": 5,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 19,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 22,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      }
    ],
    "dominant_failure_reason": "no_candidate",
    "operator_use": {
      "bottleneck_insertion": 13,
      "regret_insertion": 33,
      "scarcity_first_insertion": 23,
      "diversified_insertion": 10,
      "greedy_insertion": 5
    },
    "protected_metric_passed": true,
    "protected_metric_violations": []
  }
}
```

### #018 [SOLVER] EXECUTION_TRACE | C001 / SOLVER 000

```json
{
  "trace_id": "X1",
  "kind": "initial_insertion",
  "candidate_task_count": 100,
  "attempted_task_count": 4930,
  "inserted_task_count": 84,
  "uninserted_task_count": 16,
  "zero_candidate_task_count": 701,
  "hard_filter_rejected_count": 6,
  "top_failed_tasks": [
    {
      "task_id": 1,
      "priority": 1.0,
      "capable_agents": 2,
      "candidate_positions": 0,
      "hard_feasible_positions": 0,
      "hard_filter_rejections": {
        "no_candidate_position": 1
      },
      "dominant_reason": "no_candidate_position"
    },
    {
      "task_id": 8,
      "priority": 1.0,
      "capable_agents": 3,
      "candidate_positions": 0,
      "hard_feasible_positions": 0,
      "hard_filter_rejections": {
        "no_candidate_position": 1
      },
      "dominant_reason": "no_candidate_position"
    },
    {
      "task_id": 9,
      "priority": 1.0,
      "capable_agents": 5,
      "candidate_positions": 0,
      "hard_feasible_positions": 0,
      "hard_filter_rejections": {
        "no_candidate_position": 1
      },
      "dominant_reason": "no_candidate_position"
    },
    {
      "task_id": 19,
      "priority": 2.0,
      "capable_agents": 3,
      "candidate_positions": 0,
      "hard_feasible_positions": 0,
      "hard_filter_rejections": {
        "no_candidate_position": 1
      },
      "dominant_reason": "no_candidate_position"
    },
    {
      "task_id": 22,
      "priority": 2.0,
      "capable_agents": 3,
      "candidate_positions": 0,
      "hard_feasible_positions": 0,
      "hard_filter_rejections": {
        "no_candidate_position": 1
      },
      "dominant_reason": "no_candidate_position"
    }
  ],
  "dominant_failure_reason": "no_candidate",
  "operator_use": {
    "bottleneck_insertion": 13,
    "regret_insertion": 33,
    "scarcity_first_insertion": 23,
    "diversified_insertion": 10,
    "greedy_insertion": 5
  },
  "protected_metric_passed": true,
  "protected_metric_violations": []
}
```

### #019 [AUDIT] OUTCOME_VERIFICATION | C001 / SOLVER 000

```json
{
  "verification_id": "V1",
  "contract_id": "C001",
  "decision_id": "D1",
  "manifest_id": "R1",
  "trace_id": "X1",
  "action": "construct_initial",
  "target_id": "T_unassigned_priority",
  "protected_metric_baseline": {
    "missed_priority": 198.0,
    "unassigned_count": 100.0,
    "energy_total": 0.0,
    "total_distance": 0.0,
    "makespan": 0.0,
    "route_balance": 0.0
  },
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316
    },
    "best_feasible": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316
    }
  },
  "debt_delta": {},
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "none",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false,
    "protected_metric_problem": false
  },
  "event_tags": [
    "initial_feasible"
  ],
  "improvement_flags": {
    "working_contract_improved": false,
    "action_best_contract_improved": false,
    "run_global_best_improved": false,
    "protected_metrics_passed": true
  },
  "objective_keys": {
    "contract": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        18.0,
        16.0,
        61731.554843921316
      ]
    },
    "global": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        18.0,
        16.0,
        61731.554843921316
      ]
    }
  },
  "trace": {
    "trace_id": "X1",
    "kind": "initial_insertion",
    "candidate_task_count": 100,
    "attempted_task_count": 4930,
    "inserted_task_count": 84,
    "uninserted_task_count": 16,
    "zero_candidate_task_count": 701,
    "hard_filter_rejected_count": 6,
    "top_failed_tasks": [
      {
        "task_id": 1,
        "priority": 1.0,
        "capable_agents": 2,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 8,
        "priority": 1.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 9,
        "priority": 1.0,
        "capable_agents": 5,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 19,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 22,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      }
    ],
    "dominant_failure_reason": "no_candidate",
    "operator_use": {
      "bottleneck_insertion": 13,
      "regret_insertion": 33,
      "scarcity_first_insertion": 23,
      "diversified_insertion": 10,
      "greedy_insertion": 5
    },
    "protected_metric_passed": true,
    "protected_metric_violations": []
  }
}
```

### #020 [MEM] MEMORY_UPDATE | C001 / SOLVER 000

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M1",
  "kind": "verified_action",
  "contract_id": "C001",
  "observation_id": "O1",
  "decision_id": "D1",
  "manifest_id": "R1",
  "trace_id": "X1",
  "verification_id": "V1",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_operator_top": [],
    "destroy_signal_top": [],
    "insertion_operator_top": [
      "scarcity_first_insertion",
      "regret_insertion"
    ],
    "insertion_task_signal_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insertion_position_signal_top": [
      "insert_cost",
      "future_slack"
    ],
    "acceptance": ""
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "run_global_best_improved": false,
    "metric_delta": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316
    }
  },
  "manifest": {
    "manifest_id": "R1",
    "source_decision_id": "D1",
    "contract_id": "C001",
    "action": "construct_initial",
    "target_id": "T_unassigned_priority",
    "trace_id": "X1",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 1,
        "max_time_sec": 5.0,
        "max_iters": 1
      },
      "protected_metric_baseline": {
        "missed_priority": 198.0,
        "unassigned_count": 100.0,
        "energy_total": 0.0,
        "total_distance": 0.0,
        "makespan": 0.0,
        "route_balance": 0.0
      },
      "protected_metric_bounds": [
        {
          "metric": "unassigned_count",
          "baseline": 100.0,
          "max_worsen": 0.0
        }
      ],
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X1",
    "kind": "initial_insertion",
    "candidate_task_count": 100,
    "attempted_task_count": 4930,
    "inserted_task_count": 84,
    "uninserted_task_count": 16,
    "zero_candidate_task_count": 701,
    "hard_filter_rejected_count": 6,
    "top_failed_tasks": [
      {
        "task_id": 1,
        "priority": 1.0,
        "capable_agents": 2,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 8,
        "priority": 1.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 9,
        "priority": 1.0,
        "capable_agents": 5,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 19,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      },
      {
        "task_id": 22,
        "priority": 2.0,
        "capable_agents": 3,
        "candidate_positions": 0,
        "hard_feasible_positions": 0,
        "hard_filter_rejections": {
          "no_candidate_position": 1
        },
        "dominant_reason": "no_candidate_position"
      }
    ],
    "dominant_failure_reason": "no_candidate",
    "operator_use": {
      "bottleneck_insertion": 13,
      "regret_insertion": 33,
      "scarcity_first_insertion": 23,
      "diversified_insertion": 10,
      "greedy_insertion": 5
    },
    "protected_metric_passed": true,
    "protected_metric_violations": []
  },
  "verification": {
    "verification_id": "V1",
    "contract_id": "C001",
    "decision_id": "D1",
    "manifest_id": "R1",
    "trace_id": "X1",
    "action": "construct_initial",
    "target_id": "T_unassigned_priority",
    "protected_metric_baseline": {
      "missed_priority": 198.0,
      "unassigned_count": 100.0,
      "energy_total": 0.0,
      "total_distance": 0.0,
      "makespan": 0.0,
      "route_balance": 0.0
    },
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316
      },
      "best_feasible": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316
      }
    },
    "debt_delta": {},
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "none",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false,
      "protected_metric_problem": false
    },
    "event_tags": [
      "initial_feasible"
    ],
    "improvement_flags": {
      "working_contract_improved": false,
      "action_best_contract_improved": false,
      "run_global_best_improved": false,
      "protected_metrics_passed": true
    },
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      }
    },
    "trace": {
      "trace_id": "X1",
      "kind": "initial_insertion",
      "candidate_task_count": 100,
      "attempted_task_count": 4930,
      "inserted_task_count": 84,
      "uninserted_task_count": 16,
      "zero_candidate_task_count": 701,
      "hard_filter_rejected_count": 6,
      "top_failed_tasks": [
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 8,
          "priority": 1.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 9,
          "priority": 1.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 19,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 22,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "dominant_failure_reason": "no_candidate",
      "operator_use": {
        "bottleneck_insertion": 13,
        "regret_insertion": 33,
        "scarcity_first_insertion": 23,
        "diversified_insertion": 10,
        "greedy_insertion": 5
      },
      "protected_metric_passed": true,
      "protected_metric_violations": []
    }
  }
}
```

</details>

### #021 [CONTRACT] CONTRACT_PROGRESS | C001 / SOLVER 000

```json
{
  "contract_id": "C001",
  "solver_actions": 1,
  "time_used_sec": 0.0,
  "iters_used": 0,
  "verification_ids": [
    "V1"
  ],
  "intent_status_counts": {
    "achieved": 1
  },
  "dominant_blocker_counts": {
    "none": 1
  },
  "condition_report": [
    {
      "condition_id": "S_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "achieved",
      "window": 1,
      "passed": true
    },
    {
      "condition_id": "F_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "not_achieved",
      "window": 1,
      "passed": false
    }
  ]
}
```

### #022 [CONTRACT] CONTRACT_COMPLETION_CHECK | C001 / SOLVER 000

```json
{
  "completion_status": "success",
  "completion_reason": "success_condition_passed:S_initial",
  "condition_report": [
    {
      "condition_id": "S_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "achieved",
      "window": 1,
      "passed": true
    },
    {
      "condition_id": "F_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "not_achieved",
      "window": 1,
      "passed": false
    }
  ],
  "completed": true
}
```

### #023 [CONTRACT] CONTRACT_END | C001

```json
{
  "completion": {
    "completion_status": "success",
    "completion_reason": "success_condition_passed:S_initial",
    "condition_report": [
      {
        "condition_id": "S_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "achieved",
        "window": 1,
        "passed": true
      },
      {
        "condition_id": "F_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "not_achieved",
        "window": 1,
        "passed": false
      }
    ],
    "completed": true
  },
  "memory_update": {
    "summary_id": "CS1",
    "kind": "contract_summary",
    "contract_id": "C001",
    "contract_type": "initial_construction",
    "objective_layers": [
      {
        "metric": "missed_priority",
        "direction": "min"
      },
      {
        "metric": "unassigned_count",
        "direction": "min"
      },
      {
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 198.0,
      "unassigned_count": 100.0,
      "energy_total": 0.0,
      "total_distance": 0.0,
      "makespan": 0.0,
      "route_balance": 0.0
    },
    "progress": {
      "contract_id": "C001",
      "solver_actions": 1,
      "time_used_sec": 0.0,
      "iters_used": 0,
      "verification_ids": [
        "V1"
      ],
      "intent_status_counts": {
        "achieved": 1
      },
      "dominant_blocker_counts": {
        "none": 1
      },
      "condition_report": [
        {
          "condition_id": "S_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "achieved",
          "window": 1,
          "passed": true
        },
        {
          "condition_id": "F_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "not_achieved",
          "window": 1,
          "passed": false
        }
      ]
    },
    "completion": {
      "completion_status": "success",
      "completion_reason": "success_condition_passed:S_initial",
      "condition_report": [
        {
          "condition_id": "S_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "achieved",
          "window": 1,
          "passed": true
        },
        {
          "condition_id": "F_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "not_achieved",
          "window": 1,
          "passed": false
        }
      ],
      "completed": true
    }
  }
}
```

### #024 [OBS] SUPERVISOR_REVIEW_OBSERVATION | C001

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O_review_1",
  "frame_type": "supervisor_review",
  "role": "supervisor",
  "budget_caps": {
    "max_solver_actions": 3,
    "max_time_sec": 10.0,
    "max_iters": 50
  },
  "completed_contract": {
    "contract_id": "C001",
    "contract_type": "initial_construction",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 198.0,
      "unassigned_count": 100.0,
      "energy_total": 0.0,
      "total_distance": 0.0,
      "makespan": 0.0,
      "route_balance": 0.0
    }
  },
  "contract_completion": {
    "completion_status": "success",
    "completion_reason": "success_condition_passed:S_initial",
    "condition_report": [
      {
        "condition_id": "S_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "achieved",
        "window": 1,
        "passed": true
      },
      {
        "condition_id": "F_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "not_achieved",
        "window": 1,
        "passed": false
      }
    ],
    "completed": true
  },
  "condition_report": [
    {
      "condition_id": "S_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "achieved",
      "window": 1,
      "passed": true
    },
    {
      "condition_id": "F_initial",
      "source": "last.intent_status",
      "actual": "achieved",
      "op": "==",
      "expected": "not_achieved",
      "window": 1,
      "passed": false
    }
  ],
  "stage_verification_summary": {
    "verification_ids": [
      "V1"
    ],
    "intent_status_counts": {
      "achieved": 1
    },
    "dominant_blocker_counts": {
      "none": 1
    },
    "last": {
      "exists": true,
      "verification_id": "V1",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316
      },
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "global_best_updates": 0
      }
    }
  },
  "solution_position": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "none",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      }
    }
  },
  "usable_memory": [
    {
      "summary_id": "CS1",
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "completion_status": "success",
      "condition_report": [
        {
          "condition_id": "S_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "achieved",
          "window": 1,
          "passed": true
        },
        {
          "condition_id": "F_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "not_achieved",
          "window": 1,
          "passed": false
        }
      ]
    },
    {
      "record_id": "M1",
      "contract_id": "C001",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    }
  ],
  "relaxation_reference": {
    "time_window_median_width": 100.0,
    "agent_energy_median": 13967.103715264191
  },
  "allowed_contract_types": [
    "alns_search",
    "recovery",
    "final_refinement"
  ],
  "allowed_objective_metrics": [
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance"
  ],
  "next_contract_resource_limits": {
    "max_solver_actions_allowed": 3,
    "max_time_sec_allowed": 10.0,
    "max_iters_allowed": 50
  }
}
```

</details>

### #025 [PROMPT] SUPERVISOR_REVIEW_PROMPT | C001

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SUPERVISOR_REVIEW

INSTRUCTION:
Use condition_report, stage_verification_summary, solution_position, and budget_caps to decide whether to stop or issue the next executable contract. Put human-readable text only in contract_review or explanation.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O_review_1",
    "frame_type": "supervisor_review",
    "role": "supervisor",
    "budget_caps": {
      "max_solver_actions": 3,
      "max_time_sec": 10.0,
      "max_iters": 50
    },
    "completed_contract": {
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 198.0,
        "unassigned_count": 100.0,
        "energy_total": 0.0,
        "total_distance": 0.0,
        "makespan": 0.0,
        "route_balance": 0.0
      }
    },
    "contract_completion": {
      "completion_status": "success",
      "completion_reason": "success_condition_passed:S_initial",
      "condition_report": [
        {
          "condition_id": "S_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "achieved",
          "window": 1,
          "passed": true
        },
        {
          "condition_id": "F_initial",
          "source": "last.intent_status",
          "actual": "achieved",
          "op": "==",
          "expected": "not_achieved",
          "window": 1,
          "passed": false
        }
      ],
      "completed": true
    },
    "condition_report": [
      {
        "condition_id": "S_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "achieved",
        "window": 1,
        "passed": true
      },
      {
        "condition_id": "F_initial",
        "source": "last.intent_status",
        "actual": "achieved",
        "op": "==",
        "expected": "not_achieved",
        "window": 1,
        "passed": false
      }
    ],
    "stage_verification_summary": {
      "verification_ids": [
        "V1"
      ],
      "intent_status_counts": {
        "achieved": 1
      },
      "dominant_blocker_counts": {
        "none": 1
      },
      "last": {
        "exists": true,
        "verification_id": "V1",
        "intent_status": "achieved",
        "dominant_blocker": "none",
        "metric_delta": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316
        },
        "debt_delta": {},
        "trace_counts": {
          "candidate_trials": 0,
          "feasibility_rejected": 0,
          "accepted": 0,
          "global_best_updates": 0
        }
      }
    },
    "solution_position": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "none",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        }
      }
    },
    "usable_memory": [
      {
        "summary_id": "CS1",
        "contract_id": "C001",
        "contract_type": "initial_construction",
        "completion_status": "success",
        "condition_report": [
          {
            "condition_id": "S_initial",
            "source": "last.intent_status",
            "actual": "achieved",
            "op": "==",
            "expected": "achieved",
            "window": 1,
            "passed": true
          },
          {
            "condition_id": "F_initial",
            "source": "last.intent_status",
            "actual": "achieved",
            "op": "==",
            "expected": "not_achieved",
            "window": 1,
            "passed": false
          }
        ]
      },
      {
        "record_id": "M1",
        "contract_id": "C001",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      }
    ],
    "relaxation_reference": {
      "time_window_median_width": 100.0,
      "agent_energy_median": 13967.103715264191
    },
    "allowed_contract_types": [
      "alns_search",
      "recovery",
      "final_refinement"
    ],
    "allowed_objective_metrics": [
      "missed_priority",
      "unassigned_count",
      "energy_total",
      "total_distance",
      "makespan",
      "route_balance"
    ],
    "next_contract_resource_limits": {
      "max_solver_actions_allowed": 3,
      "max_time_sec_allowed": 10.0,
      "max_iters_allowed": 50
    }
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "Supervisor decision after a contract has ended.",
  "properties": {
    "supervisor_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "issue_contract"
            },
            "contract_review": {
              "type": "object",
              "description": "Human-readable review ignored by runtime.",
              "properties": {
                "outcome_summary": {
                  "type": "string",
                  "description": "What happened during the completed contract."
                },
                "main_lesson": {
                  "type": "string",
                  "description": "Most important lesson for the next stage."
                }
              },
              "required": [
                "outcome_summary",
                "main_lesson"
              ],
              "additionalProperties": false
            },
            "next_contract": {
              "type": "object",
              "description": "A supervisor-issued executable search contract.",
              "properties": {
                "contract_type": {
                  "type": "string",
                  "enum": [
                    "initial_construction",
                    "alns_search",
                    "recovery",
                    "final_refinement"
                  ]
                },
                "objective_layers": {
                  "type": "array",
                  "minItems": 1,
                  "maxItems": 4,
                  "items": {
                    "type": "string",
                    "enum": [
                      "missed_priority",
                      "unassigned_count",
                      "energy_total",
                      "total_distance",
                      "makespan",
                      "route_balance"
                    ]
                  }
                },
                "feasibility_control": {
                  "type": "object",
                  "description": "Stage-level feasibility handling selected by Supervisor.",
                  "properties": {
                    "mode": {
                      "type": "string",
                      "enum": [
                        "strict",
                        "relaxed_recoverable",
                        "recovery_only"
                      ],
                      "description": "Feasibility mode for this contract."
                    },
                    "relaxation_ratios": {
                      "type": "array",
                      "description": "Temporary recoverable relaxation ratios. Used by relaxed_recoverable.",
                      "maxItems": 2,
                      "items": {
                        "type": "object",
                        "description": "One temporary recoverable relaxation allowance.",
                        "properties": {
                          "violation_type": {
                            "type": "string",
                            "enum": [
                              "time_window",
                              "energy"
                            ],
                            "description": "Relaxable violation type."
                          },
                          "max_ratio": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 0.3,
                            "description": "Normalized temporary allowance for this violation type."
                          }
                        },
                        "required": [
                          "violation_type",
                          "max_ratio"
                        ],
                        "additionalProperties": false
                      }
                    }
                  },
                  "required": [
                    "mode",
                    "relaxation_ratios"
                  ],
                  "additionalProperties": false
                },
                "target_policy": {
                  "type": "object",
                  "description": "Executable target preference for the next contract.",
                  "properties": {
                    "preferred_target_kinds": {
                      "type": "array",
                      "minItems": 0,
                      "maxItems": 4,
                      "items": {
                        "type": "string",
                        "enum": [
                          "unassigned_priority",
                          "insertion_scarce_unassigned",
                          "energy_debt",
                          "time_window_debt",
                          "route_balance"
                        ]
                      }
                    }
                  },
                  "required": [
                    "preferred_target_kinds"
                  ],
                  "additionalProperties": false
                },
                "protected_metrics": {
                  "type": "array",
                  "maxItems": 4,
                  "items": {
                    "type": "object",
                    "description": "Hard non-worsening bound for this contract. max_worsen is measured relative to contract_start_quality. A violating candidate is ineligible for trial acceptance, action-best, returned-working, or best updates.",
                    "properties": {
                      "metric": {
                        "type": "string",
                        "enum": [
                          "missed_priority",
                          "unassigned_count",
                          "energy_total",
                          "total_distance",
                          "makespan",
                          "route_balance"
                        ]
                      },
                      "max_worsen": {
                        "type": "number",
                        "minimum": 0.0
                      }
                    },
                    "required": [
                      "metric",
                      "max_worsen"
                    ],
                    "additionalProperties": false
                  }
                },
                "resource_policy": {
                  "type": "object",
                  "description": "Executable resource limits for this contract.",
                  "properties": {
                    "min_actions": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 3
                    },
                    "max_actions": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 3
                    },
                    "max_iters": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 50
                    },
                    "max_time_sec": {
                      "type": "number",
                      "exclusiveMinimum": 0,
                      "maximum": 10.0
                    }
                  },
                  "required": [
                    "min_actions",
                    "max_actions",
                    "max_iters",
                    "max_time_sec"
                  ],
                  "additionalProperties": false
                },
                "exit_conditions": {
                  "type": "object",
                  "description": "Typed success and failure conditions.",
                  "properties": {
                    "success": {
                      "type": "array",
                      "maxItems": 4,
                      "items": {
                        "type": "object",
                        "description": "Typed condition evaluated by ContractMonitor.",
                        "properties": {
                          "condition_id": {
                            "type": "string",
                            "description": "Stable id unique inside this contract condition set."
                          },
                          "source": {
                            "type": "string",
                            "enum": [
                              "progress.solver_actions",
                              "progress.iters_used",
                              "progress.time_used_sec",
                              "last.intent_status",
                              "last.dominant_blocker",
                              "last.improvement_flags.run_global_best_improved",
                              "aggregate.achieved",
                              "aggregate.partial",
                              "aggregate.not_achieved",
                              "aggregate.regressed",
                              "aggregate.solver_requested_review",
                              "working.is_feasible",
                              "working.missed_priority",
                              "working.unassigned_count",
                              "working.energy_total",
                              "working.total_distance",
                              "working.makespan",
                              "working.route_balance",
                              "best_feasible.exists",
                              "best_feasible.missed_priority",
                              "best_feasible.unassigned_count",
                              "best_feasible.energy_total",
                              "best_feasible.total_distance",
                              "best_feasible.makespan",
                              "best_feasible.route_balance"
                            ],
                            "description": "Executable source path read by ContractMonitor."
                          },
                          "op": {
                            "type": "string",
                            "enum": [
                              "<",
                              "<=",
                              "==",
                              "!=",
                              ">=",
                              ">"
                            ]
                          },
                          "value": {
                            "type": [
                              "number",
                              "string",
                              "boolean"
                            ]
                          },
                          "window": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20
                          }
                        },
                        "required": [
                          "condition_id",
                          "source",
                          "op",
                          "value",
                          "window"
                        ],
                        "additionalProperties": false
                      }
                    },
                    "failure": {
                      "type": "array",
                      "maxItems": 4,
                      "items": {
                        "type": "object",
                        "description": "Typed condition evaluated by ContractMonitor.",
                        "properties": {
                          "condition_id": {
                            "type": "string",
                            "description": "Stable id unique inside this contract condition set."
                          },
                          "source": {
                            "type": "string",
                            "enum": [
                              "progress.solver_actions",
                              "progress.iters_used",
                              "progress.time_used_sec",
                              "last.intent_status",
                              "last.dominant_blocker",
                              "last.improvement_flags.run_global_best_improved",
                              "aggregate.achieved",
                              "aggregate.partial",
                              "aggregate.not_achieved",
                              "aggregate.regressed",
                              "aggregate.solver_requested_review",
                              "working.is_feasible",
                              "working.missed_priority",
                              "working.unassigned_count",
                              "working.energy_total",
                              "working.total_distance",
                              "working.makespan",
                              "working.route_balance",
                              "best_feasible.exists",
                              "best_feasible.missed_priority",
                              "best_feasible.unassigned_count",
                              "best_feasible.energy_total",
                              "best_feasible.total_distance",
                              "best_feasible.makespan",
                              "best_feasible.route_balance"
                            ],
                            "description": "Executable source path read by ContractMonitor."
                          },
                          "op": {
                            "type": "string",
                            "enum": [
                              "<",
                              "<=",
                              "==",
                              "!=",
                              ">=",
                              ">"
                            ]
                          },
                          "value": {
                            "type": [
                              "number",
                              "string",
                              "boolean"
                            ]
                          },
                          "window": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20
                          }
                        },
                        "required": [
                          "condition_id",
                          "source",
                          "op",
                          "value",
                          "window"
                        ],
                        "additionalProperties": false
                      }
                    }
                  },
                  "required": [
                    "success",
                    "failure"
                  ],
                  "additionalProperties": false
                },
                "explanation": {
                  "type": "object",
                  "description": "Human-readable explanation ignored by validator/compiler/runtime.",
                  "additionalProperties": {
                    "type": "string"
                  }
                }
              },
              "required": [
                "contract_type",
                "objective_layers",
                "feasibility_control",
                "target_policy",
                "protected_metrics",
                "resource_policy",
                "exit_conditions"
              ],
              "additionalProperties": false
            }
          },
          "required": [
            "action",
            "contract_review",
            "next_contract"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "stop_run"
            },
            "contract_review": {
              "type": "object",
              "description": "Human-readable review ignored by runtime.",
              "properties": {
                "outcome_summary": {
                  "type": "string",
                  "description": "What happened during the completed contract."
                },
                "main_lesson": {
                  "type": "string",
                  "description": "Most important lesson for the next stage."
                }
              },
              "required": [
                "outcome_summary",
                "main_lesson"
              ],
              "additionalProperties": false
            },
            "stop_explanation": {
              "type": "string",
              "description": "Why the supervisor decides the run should stop."
            }
          },
          "required": [
            "action",
            "contract_review",
            "stop_explanation"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "supervisor_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #026 [RAW] SUPERVISOR_REVIEW_RAW_OUTPUT | C001

<details>
<summary>Open raw LLM output</summary>

```text
{"supervisor_decision": {"action": "issue_contract", "contract_review": {"outcome_summary": "The previous contract produced verified feedback.", "main_lesson": "The next decision should use condition_report and verified outcomes."}, "next_contract": {"contract_type": "alns_search", "objective_layers": ["missed_priority", "unassigned_count", "energy_total"], "feasibility_control": {"mode": "strict", "relaxation_ratios": []}, "target_policy": {"preferred_target_kinds": ["unassigned_priority", "energy_debt"]}, "protected_metrics": [{"metric": "unassigned_count", "max_worsen": 0}], "resource_policy": {"min_actions": 3, "max_actions": 3, "max_time_sec": 1.0, "max_iters": 3}, "exit_conditions": {"success": [{"condition_id": "S_best", "source": "last.improvement_flags.run_global_best_improved", "op": "==", "value": true, "window": 1}], "failure": [{"condition_id": "F_no_gain", "source": "aggregate.not_achieved", "op": ">=", "value": 3, "window": 3}]}, "explanation": {"stage_summary": "Run a short ALNS contract using verified feedback."}}}}
```

</details>

### #027 [OK] SUPERVISOR_REVIEW_VALIDATED_PAYLOAD | C001

```json
{
  "supervisor_decision": {
    "action": "issue_contract",
    "contract_review": {
      "outcome_summary": "The previous contract produced verified feedback.",
      "main_lesson": "The next decision should use condition_report and verified outcomes."
    },
    "next_contract": {
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_control": {
        "mode": "strict",
        "relaxation_ratios": []
      },
      "target_policy": {
        "preferred_target_kinds": [
          "unassigned_priority",
          "energy_debt"
        ]
      },
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "resource_policy": {
        "min_actions": 3,
        "max_actions": 3,
        "max_time_sec": 1.0,
        "max_iters": 3
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "S_best",
            "source": "last.improvement_flags.run_global_best_improved",
            "op": "==",
            "value": true,
            "window": 1
          }
        ],
        "failure": [
          {
            "condition_id": "F_no_gain",
            "source": "aggregate.not_achieved",
            "op": ">=",
            "value": 3,
            "window": 3
          }
        ]
      },
      "explanation": {
        "stage_summary": "Run a short ALNS contract using verified feedback."
      }
    }
  }
}
```

### #028 [OK] VALIDATED_FEASIBILITY_CONTROL | C002

```json
{
  "mode": "strict",
  "relaxation_ratios": []
}
```

### #029 [COMP] COMPILED_FEASIBILITY_POLICY | C002

```json
{
  "mode": "strict"
}
```

### #030 [COMP] COMPILED_CONTRACT | C002

```json
{
  "contract_id": "C002",
  "contract_type": "alns_search",
  "objective_layers": [
    {
      "metric": "missed_priority",
      "direction": "min"
    },
    {
      "metric": "unassigned_count",
      "direction": "min"
    },
    {
      "metric": "energy_total",
      "direction": "min"
    }
  ],
  "feasibility_control": {
    "mode": "strict",
    "relaxation_ratios": [],
    "compiled_policy_summary": {}
  },
  "feasibility_policy": {
    "mode": "strict"
  },
  "target_policy": {
    "preferred_target_kinds": [
      "unassigned_priority",
      "energy_debt"
    ]
  },
  "protected_metrics": [
    {
      "metric": "unassigned_count",
      "max_worsen": 0
    }
  ],
  "protected_metric_baseline": {
    "missed_priority": 18.0,
    "unassigned_count": 16.0,
    "energy_total": 61731.554843921316,
    "total_distance": 56668.05133123227,
    "makespan": 21963.819830943008,
    "route_balance": 0.22961073240459418
  },
  "resource_policy": {
    "min_actions": 3,
    "max_actions": 3,
    "max_time_sec": 1.0,
    "max_iters": 3
  },
  "exit_conditions": {
    "success": [
      {
        "condition_id": "S_best",
        "source": "last.improvement_flags.run_global_best_improved",
        "op": "==",
        "value": true,
        "window": 1
      }
    ],
    "failure": [
      {
        "condition_id": "F_no_gain",
        "source": "aggregate.not_achieved",
        "op": ">=",
        "value": 3,
        "window": 3
      }
    ]
  },
  "explanation": {
    "stage_summary": "Run a short ALNS contract using verified feedback."
  }
}
```

### #031 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 001

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O2",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 1,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "remaining_resources": {
      "actions": 3,
      "time_sec": 1.0,
      "iters": 3,
      "min_actions_remaining": 3
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "none",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V1",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316
    },
    "debt_delta": {},
    "trace_counts": {
      "candidate_trials": 0,
      "feasibility_rejected": 0,
      "accepted": 0,
      "global_best_updates": 0
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "task_count": 16,
      "priority_mass": 18.0,
      "top_tasks": [
        {
          "task_id": 19,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 22,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 57,
          "priority": 2.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 61,
          "priority": 2.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 87,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        }
      ],
      "metric_pressure": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "priority_loss",
          "scarcity_pressure"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack",
          "insert_cost"
        ],
        "destroy_control.signal_scores": [
          "mobility_opportunity",
          "scarcity_protection"
        ]
      }
    },
    {
      "target_id": "T_energy_debt",
      "kind": "energy_debt",
      "metric_pressure": {
        "energy_ratio": 0.0
      },
      "recommended_controls": {
        "destroy_control.signal_scores": [
          "cost_pressure",
          "mobility_opportunity"
        ],
        "insertion_control.position_signal_scores": [
          "insert_cost",
          "future_slack"
        ],
        "acceptance_control.mode": [
          "threshold"
        ]
      }
    },
    {
      "target_id": "contract_review",
      "kind": "contract_review",
      "recommended_controls": {}
    }
  ],
  "action_space": {
    "allowed_actions": [
      "run_alns",
      "request_supervisor_review"
    ],
    "allowed_insertion_operators": [
      "greedy_insertion",
      "scarcity_first_insertion",
      "regret_insertion",
      "bottleneck_insertion",
      "diversified_insertion"
    ],
    "allowed_task_signals": [
      "priority_loss",
      "scarcity_pressure",
      "regret_pressure",
      "bottleneck_pressure",
      "mobility_opportunity"
    ],
    "allowed_position_signals": [
      "insert_cost",
      "future_slack",
      "route_balance_gain",
      "local_coupling_penalty",
      "diversity_gain"
    ],
    "allowed_destroy_operators": [
      "random_removal",
      "worst_task_removal",
      "related_cluster_removal",
      "critical_block_removal",
      "route_rebalance_removal"
    ],
    "allowed_destroy_signals": [
      "cost_pressure",
      "coupling_pressure",
      "route_balance_pressure",
      "mobility_opportunity",
      "scarcity_protection"
    ],
    "allowed_acceptance_modes": [
      "greedy",
      "threshold",
      "sa"
    ]
  },
  "usable_memory": []
}
```

</details>

### #032 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 001

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SOLVER

INSTRUCTION:
Choose one allowed action. If executing a solver action, choose one target_id from decision_targets and choose controls only from action_space. Every operational field will be compiled and executed exactly. Each score name must be selected from the enum of that exact output field. Do not move names between destroy operator, destroy signal, insertion operator, task signal, and position signal fields.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O2",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 1,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "remaining_resources": {
        "actions": 3,
        "time_sec": 1.0,
        "iters": 3,
        "min_actions_remaining": 3
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "none",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V1",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316
      },
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "global_best_updates": 0
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 16,
        "priority_mass": 18.0,
        "top_tasks": [
          {
            "task_id": 19,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 22,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 57,
            "priority": 2.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 61,
            "priority": 2.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 87,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          }
        ],
        "metric_pressure": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "priority_loss",
            "scarcity_pressure"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack",
            "insert_cost"
          ],
          "destroy_control.signal_scores": [
            "mobility_opportunity",
            "scarcity_protection"
          ]
        }
      },
      {
        "target_id": "T_energy_debt",
        "kind": "energy_debt",
        "metric_pressure": {
          "energy_ratio": 0.0
        },
        "recommended_controls": {
          "destroy_control.signal_scores": [
            "cost_pressure",
            "mobility_opportunity"
          ],
          "insertion_control.position_signal_scores": [
            "insert_cost",
            "future_slack"
          ],
          "acceptance_control.mode": [
            "threshold"
          ]
        }
      },
      {
        "target_id": "contract_review",
        "kind": "contract_review",
        "recommended_controls": {}
      }
    ],
    "action_space": {
      "allowed_actions": [
        "run_alns",
        "request_supervisor_review"
      ],
      "allowed_insertion_operators": [
        "greedy_insertion",
        "scarcity_first_insertion",
        "regret_insertion",
        "bottleneck_insertion",
        "diversified_insertion"
      ],
      "allowed_task_signals": [
        "priority_loss",
        "scarcity_pressure",
        "regret_pressure",
        "bottleneck_pressure",
        "mobility_opportunity"
      ],
      "allowed_position_signals": [
        "insert_cost",
        "future_slack",
        "route_balance_gain",
        "local_coupling_penalty",
        "diversity_gain"
      ],
      "allowed_destroy_operators": [
        "random_removal",
        "worst_task_removal",
        "related_cluster_removal",
        "critical_block_removal",
        "route_rebalance_removal"
      ],
      "allowed_destroy_signals": [
        "cost_pressure",
        "coupling_pressure",
        "route_balance_pressure",
        "mobility_opportunity",
        "scarcity_protection"
      ],
      "allowed_acceptance_modes": [
        "greedy",
        "threshold",
        "sa"
      ]
    },
    "usable_memory": []
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "One Solver decision under the active supervisor contract.",
  "properties": {
    "solver_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "run_alns"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "destroy_control": {
              "type": "object",
              "description": "Executable destroy controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "random_removal",
                          "worst_task_removal",
                          "related_cluster_removal",
                          "critical_block_removal",
                          "route_rebalance_removal"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy signals.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy signals.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "cost_pressure",
                          "coupling_pressure",
                          "route_balance_pressure",
                          "mobility_opportunity",
                          "scarcity_protection"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Removal intensity from 0 to 10."
                }
              },
              "required": [
                "operator_scores",
                "signal_scores",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "insertion_control": {
              "type": "object",
              "description": "Executable insertion controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for insertion operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for insertion operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "greedy_insertion",
                          "scarcity_first_insertion",
                          "regret_insertion",
                          "bottleneck_insertion",
                          "diversified_insertion"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "task_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing the next task.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing the next task.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "priority_loss",
                          "scarcity_pressure",
                          "regret_pressure",
                          "bottleneck_pressure",
                          "mobility_opportunity"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "position_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing an insertion position.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing an insertion position.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "insert_cost",
                          "future_slack",
                          "route_balance_gain",
                          "local_coupling_penalty",
                          "diversity_gain"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "operator_scores",
                "task_signal_scores",
                "position_signal_scores"
              ],
              "additionalProperties": false
            },
            "acceptance_control": {
              "type": "object",
              "description": "Executable acceptance control.",
              "properties": {
                "mode": {
                  "type": "string",
                  "enum": [
                    "greedy",
                    "threshold",
                    "sa"
                  ],
                  "description": "Acceptance mode allowed for the current action space."
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Acceptance exploration intensity."
                }
              },
              "required": [
                "mode",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id",
            "destroy_control",
            "insertion_control",
            "acceptance_control"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "request_supervisor_review"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "solver_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #033 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 001

<details>
<summary>Open raw LLM output</summary>

```text
{"solver_decision": {"action": "run_alns", "target_id": "T_unassigned_priority", "destroy_control": {"operator_scores": [{"name": "related_cluster_removal", "score": 8}], "signal_scores": [{"name": "coupling_pressure", "score": 8}], "intensity_score": 5}, "insertion_control": {"operator_scores": [{"name": "scarcity_first_insertion", "score": 8}, {"name": "regret_insertion", "score": 7}], "task_signal_scores": [{"name": "priority_loss", "score": 9}, {"name": "scarcity_pressure", "score": 8}], "position_signal_scores": [{"name": "insert_cost", "score": 8}, {"name": "future_slack", "score": 7}]}, "acceptance_control": {"mode": "threshold", "intensity_score": 4}, "explanation": {"reason_summary": "Run one bounded local rebuild."}}}
```

</details>

### #034 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 001

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "related_cluster_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "coupling_pressure",
          "score": 8
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 8
        },
        {
          "name": "regret_insertion",
          "score": 7
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 8
        }
      ],
      "position_signal_scores": [
        {
          "name": "insert_cost",
          "score": 8
        },
        {
          "name": "future_slack",
          "score": 7
        }
      ]
    },
    "acceptance_control": {
      "mode": "threshold",
      "intensity_score": 4
    },
    "explanation": {
      "reason_summary": "Run one bounded local rebuild."
    }
  }
}
```

### #035 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 001

```json
{
  "manifest_id": "R2",
  "source_decision_id": "D2",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "trace_id": "X2",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 3,
      "max_actions": 3,
      "max_time_sec": 1.0,
      "max_iters": 3
    },
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 2,
        "related_cluster_removal": 8,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 8,
        "route_balance_pressure": 0,
        "mobility_opportunity": 0,
        "scarcity_protection": 0
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "threshold",
      "intensity_score": 4,
      "threshold": 2.0,
      "worsening_allowance": 0.08
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.worst_task_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0",
    "destroy.signal_weights.mobility_opportunity=0",
    "destroy.signal_weights.scarcity_protection=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #036 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 001

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 2,
      "related_cluster_removal": 8,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 8,
      "route_balance_pressure": 0,
      "mobility_opportunity": 0,
      "scarcity_protection": 0
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 8,
      "regret_insertion": 7,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 8,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 8,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "threshold",
    "intensity_score": 4,
    "accept_level": 0.08,
    "exploration_score": 2.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #037 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 001

```json
{
  "time_limit_sec": 0.3333333333333333,
  "max_iters": 1
}
```

### #038 [SOLVER] SOLVER_RESULT | C002 / SOLVER 001

```json
{
  "working_solution": {
    "is_feasible": true,
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      }
    },
    "quality_summary": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "feasibility_summary": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_by_type": {
        "capability": 0.0,
        "time_window": 0.0,
        "energy": 0.0
      },
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      }
    }
  },
  "diagnostics": {
    "algorithm": "weighted_alns",
    "policy": {
      "destroy_policy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "threshold",
        "intensity_score": 4,
        "accept_level": 0.08,
        "exploration_score": 2.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 1,
    "actual_iters_used": 1,
    "actual_time_used_sec": 0.5296286000011605,
    "best_update_count": 0,
    "best_update_iters": [],
    "best_update_objective_keys": [],
    "first_best_iter": null,
    "last_best_iter": null,
    "plateau_iters_after_last_update": 1,
    "initial_solution_feasible": true,
    "returned_solution_source": "action_best_feasible",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 1,
      "accepted": false,
      "accept_mode": "threshold",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy.",
      "delta_soft": 0.027494588994127003,
      "threshold": 0.0196
    },
    "last_destroy_move": {
      "operator_name": "route_rebalance_removal",
      "shape": "route",
      "task_ids": [
        0,
        18,
        2,
        71,
        5,
        88,
        42,
        91,
        75,
        44,
        11,
        12,
        13,
        14,
        15,
        16,
        30,
        33
      ],
      "affected_routes": [
        5
      ],
      "features": {
        "cost_pressure": 0.4095804613796368,
        "priority_loss": 1.0,
        "scarcity_pressure": 1.0,
        "coupling_pressure": 0.0,
        "mobility_opportunity": 0.11019252222238218,
        "route_balance_pressure": 0.8747359116126976,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 0.0,
      "metadata": {
        "route_id": 5,
        "route_len": 18,
        "route_cost": 28718.739066663606
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "greedy_insertion": 4,
        "bottleneck_insertion": 1,
        "regret_insertion": 6,
        "scarcity_first_insertion": 6,
        "diversified_insertion": 1
      },
      "unassigned_before": 34,
      "unassigned_after": 16,
      "inserted_count": 18,
      "failed_count": 16,
      "tasks_analyzed": 475,
      "positions_generated": 343,
      "positions_strict_checked": 343,
      "strict_feasible_positions": 342,
      "failure_breakdown": {
        "no_candidate": 175,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 8,
          "priority": 1.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 9,
          "priority": 1.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 19,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 22,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 475.3839,
      "operator": "greedy_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        },
        "action_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        },
        "global_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        },
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy.",
        "protected_metric_passed": true,
        "protected_metric_violations": [],
        "rejection_reason": "acceptance_rejected"
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 0.0,
      "worst_task_removal": 0.0,
      "related_cluster_removal": 0.0,
      "critical_block_removal": 0.0,
      "route_rebalance_removal": 1.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 34.0,
      "tasks_reinserted": 18.0,
      "tasks_left_unassigned": 16.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 175.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 1.0,
          "worst_task_removal": 1.0,
          "related_cluster_removal": 1.0,
          "critical_block_removal": 1.0,
          "route_rebalance_removal": 1.0
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 2.0,
          "related_cluster_removal": 8.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.189207115002721,
          "worst_task_removal": 1.189207115002721,
          "related_cluster_removal": 1.681792830507429,
          "critical_block_removal": 1.189207115002721,
          "route_rebalance_removal": 1.189207115002721
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 8.0,
          "regret_insertion": 7.0,
          "bottleneck_insertion": 2.0,
          "diversified_insertion": 2.0
        }
      }
    },
    "feasibility_policy": {
      "mode": "strict"
    },
    "violation_ratios": {
      "energy": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      },
      "time_window": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      }
    },
    "feasibility_rejection_reasons": {},
    "protected_metric_rejections": 0,
    "protected_metric_rejection_reasons": {},
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "execution_trace": {
      "trace_id": "X2",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 0,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 1
        },
        "removed_task_count_avg": 18.0
      },
      "repair": {
        "candidate_tasks_total": 34,
        "tasks_reinserted": 18,
        "tasks_left_unassigned": 16,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 175
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 1,
        "accepted_trials": 0,
        "global_best_improved_trials": 0
      },
      "rejection_reasons": {}
    },
    "solution_flow": {
      "initial_working": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        }
      },
      "final_current": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        },
        "is_feasible": true
      },
      "action_best_feasible": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        },
        "is_feasible": true
      },
      "returned_solution_source": "action_best_feasible",
      "protected_metric_result": {
        "passed": true,
        "violations": []
      }
    },
    "accepted_trial_count": 0,
    "rejected_trial_count": 1
  }
}
```

### #039 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 001

```json
{
  "trace_id": "X2",
  "kind": "alns",
  "iters": 1,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 0,
      "worst_task_removal": 0,
      "related_cluster_removal": 0,
      "critical_block_removal": 0,
      "route_rebalance_removal": 1
    },
    "removed_task_count_avg": 18.0
  },
  "repair": {
    "candidate_tasks_total": 34,
    "tasks_reinserted": 18,
    "tasks_left_unassigned": 16,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 175
    }
  },
  "trial_flow": {
    "candidate_trials": 1,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "protected_metric_rejected": 0,
    "admissible_trials": 1,
    "acceptance_rejected": 1,
    "accepted_trials": 0,
    "global_best_improved_trials": 0
  },
  "rejection_reasons": {}
}
```

### #040 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 001

```json
{
  "verification_id": "V2",
  "contract_id": "C002",
  "decision_id": "D2",
  "manifest_id": "R2",
  "trace_id": "X2",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "protected_metric_baseline": {
    "missed_priority": 18.0,
    "unassigned_count": 16.0,
    "energy_total": 61731.554843921316,
    "total_distance": 56668.05133123227,
    "makespan": 21963.819830943008,
    "route_balance": 0.22961073240459418
  },
  "intent_status": "not_achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    },
    "best_feasible": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    }
  },
  "debt_delta": {
    "energy": 0.0,
    "time_window": 0.0
  },
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "acceptance_rejected_trials",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": true,
    "quality_problem": false,
    "protected_metric_problem": false
  },
  "event_tags": [
    "acceptance_rejected_trials",
    "no_accepted_trial"
  ],
  "improvement_flags": {
    "working_contract_improved": false,
    "action_best_contract_improved": false,
    "run_global_best_improved": false,
    "protected_metrics_passed": true
  },
  "objective_keys": {
    "contract": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        18.0,
        16.0,
        61731.554843921316
      ]
    },
    "global": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        18.0,
        16.0,
        61731.554843921316
      ]
    }
  },
  "trace": {
    "trace_id": "X2",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 0,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 1
      },
      "removed_task_count_avg": 18.0
    },
    "repair": {
      "candidate_tasks_total": 34,
      "tasks_reinserted": 18,
      "tasks_left_unassigned": 16,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 175
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 1,
      "accepted_trials": 0,
      "global_best_improved_trials": 0
    },
    "rejection_reasons": {}
  }
}
```

### #041 [MEM] MEMORY_UPDATE | C002 / SOLVER 001

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M2",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O2",
  "decision_id": "D2",
  "manifest_id": "R2",
  "trace_id": "X2",
  "verification_id": "V2",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_operator_top": [
      "related_cluster_removal",
      "critical_block_removal"
    ],
    "destroy_signal_top": [
      "coupling_pressure"
    ],
    "insertion_operator_top": [
      "scarcity_first_insertion",
      "regret_insertion"
    ],
    "insertion_task_signal_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insertion_position_signal_top": [
      "insert_cost",
      "future_slack"
    ],
    "acceptance": "threshold:4"
  },
  "outcome_fingerprint": {
    "intent_status": "not_achieved",
    "dominant_blocker": "acceptance_rejected_trials",
    "run_global_best_improved": false,
    "metric_delta": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    }
  },
  "manifest": {
    "manifest_id": "R2",
    "source_decision_id": "D2",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "trace_id": "X2",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 3,
        "max_actions": 3,
        "max_time_sec": 1.0,
        "max_iters": 3
      },
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "protected_metric_bounds": [
        {
          "metric": "unassigned_count",
          "baseline": 16.0,
          "max_worsen": 0.0
        }
      ],
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "threshold",
        "intensity_score": 4,
        "threshold": 2.0,
        "worsening_allowance": 0.08
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.worst_task_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0",
      "destroy.signal_weights.mobility_opportunity=0",
      "destroy.signal_weights.scarcity_protection=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X2",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 0,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 1
      },
      "removed_task_count_avg": 18.0
    },
    "repair": {
      "candidate_tasks_total": 34,
      "tasks_reinserted": 18,
      "tasks_left_unassigned": 16,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 175
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 1,
      "accepted_trials": 0,
      "global_best_improved_trials": 0
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V2",
    "contract_id": "C002",
    "decision_id": "D2",
    "manifest_id": "R2",
    "trace_id": "X2",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "intent_status": "not_achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      },
      "best_feasible": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      }
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "acceptance_rejected_trials",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": true,
      "quality_problem": false,
      "protected_metric_problem": false
    },
    "event_tags": [
      "acceptance_rejected_trials",
      "no_accepted_trial"
    ],
    "improvement_flags": {
      "working_contract_improved": false,
      "action_best_contract_improved": false,
      "run_global_best_improved": false,
      "protected_metrics_passed": true
    },
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          18.0,
          16.0,
          61731.554843921316
        ]
      }
    },
    "trace": {
      "trace_id": "X2",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 0,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 1
        },
        "removed_task_count_avg": 18.0
      },
      "repair": {
        "candidate_tasks_total": 34,
        "tasks_reinserted": 18,
        "tasks_left_unassigned": 16,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 175
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 1,
        "accepted_trials": 0,
        "global_best_improved_trials": 0
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #042 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 001

```json
{
  "contract_id": "C002",
  "solver_actions": 1,
  "time_used_sec": 0.333333,
  "iters_used": 1,
  "verification_ids": [
    "V2"
  ],
  "intent_status_counts": {
    "not_achieved": 1
  },
  "dominant_blocker_counts": {
    "acceptance_rejected_trials": 1
  },
  "condition_report": []
}
```

### #043 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 001

```json
{
  "completion_status": "continue",
  "completion_reason": "min_actions_not_reached",
  "condition_report": [],
  "completed": false
}
```

### #044 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 002

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O3",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 2,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "remaining_resources": {
      "actions": 2,
      "time_sec": 0.6666666666666667,
      "iters": 2,
      "min_actions_remaining": 2
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "none",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V2",
    "intent_status": "not_achieved",
    "dominant_blocker": "acceptance_rejected_trials",
    "metric_delta": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 1,
      "feasibility_rejected": 0,
      "accepted": 0,
      "global_best_updates": 0
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "task_count": 16,
      "priority_mass": 18.0,
      "top_tasks": [
        {
          "task_id": 19,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 22,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 57,
          "priority": 2.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 61,
          "priority": 2.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 87,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        }
      ],
      "metric_pressure": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "priority_loss",
          "scarcity_pressure"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack",
          "insert_cost"
        ],
        "destroy_control.signal_scores": [
          "mobility_opportunity",
          "scarcity_protection"
        ]
      }
    },
    {
      "target_id": "T_energy_debt",
      "kind": "energy_debt",
      "metric_pressure": {
        "energy_ratio": 0.0
      },
      "recommended_controls": {
        "destroy_control.signal_scores": [
          "cost_pressure",
          "mobility_opportunity"
        ],
        "insertion_control.position_signal_scores": [
          "insert_cost",
          "future_slack"
        ],
        "acceptance_control.mode": [
          "threshold"
        ]
      }
    },
    {
      "target_id": "contract_review",
      "kind": "contract_review",
      "recommended_controls": {}
    }
  ],
  "action_space": {
    "allowed_actions": [
      "run_alns",
      "request_supervisor_review"
    ],
    "allowed_insertion_operators": [
      "greedy_insertion",
      "scarcity_first_insertion",
      "regret_insertion",
      "bottleneck_insertion",
      "diversified_insertion"
    ],
    "allowed_task_signals": [
      "priority_loss",
      "scarcity_pressure",
      "regret_pressure",
      "bottleneck_pressure",
      "mobility_opportunity"
    ],
    "allowed_position_signals": [
      "insert_cost",
      "future_slack",
      "route_balance_gain",
      "local_coupling_penalty",
      "diversity_gain"
    ],
    "allowed_destroy_operators": [
      "random_removal",
      "worst_task_removal",
      "related_cluster_removal",
      "critical_block_removal",
      "route_rebalance_removal"
    ],
    "allowed_destroy_signals": [
      "cost_pressure",
      "coupling_pressure",
      "route_balance_pressure",
      "mobility_opportunity",
      "scarcity_protection"
    ],
    "allowed_acceptance_modes": [
      "greedy",
      "threshold",
      "sa"
    ]
  },
  "usable_memory": [
    {
      "record_id": "M2",
      "target_kind": "unassigned_priority",
      "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
      "outcome": "missed_priority +0, unassigned_count +0, energy_total +0, accepted 0/1, blocker acceptance_rejected_trials"
    }
  ]
}
```

</details>

### #045 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 002

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SOLVER

INSTRUCTION:
Choose one allowed action. If executing a solver action, choose one target_id from decision_targets and choose controls only from action_space. Every operational field will be compiled and executed exactly. Each score name must be selected from the enum of that exact output field. Do not move names between destroy operator, destroy signal, insertion operator, task signal, and position signal fields.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O3",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 2,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "remaining_resources": {
        "actions": 2,
        "time_sec": 0.6666666666666667,
        "iters": 2,
        "min_actions_remaining": 2
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "none",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 61731.554843921316,
          "total_distance": 56668.05133123227,
          "makespan": 21963.819830943008,
          "route_balance": 0.22961073240459418
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V2",
      "intent_status": "not_achieved",
      "dominant_blocker": "acceptance_rejected_trials",
      "metric_delta": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 1,
        "feasibility_rejected": 0,
        "accepted": 0,
        "global_best_updates": 0
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 16,
        "priority_mass": 18.0,
        "top_tasks": [
          {
            "task_id": 19,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 22,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 57,
            "priority": 2.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 61,
            "priority": 2.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 87,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          }
        ],
        "metric_pressure": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "priority_loss",
            "scarcity_pressure"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack",
            "insert_cost"
          ],
          "destroy_control.signal_scores": [
            "mobility_opportunity",
            "scarcity_protection"
          ]
        }
      },
      {
        "target_id": "T_energy_debt",
        "kind": "energy_debt",
        "metric_pressure": {
          "energy_ratio": 0.0
        },
        "recommended_controls": {
          "destroy_control.signal_scores": [
            "cost_pressure",
            "mobility_opportunity"
          ],
          "insertion_control.position_signal_scores": [
            "insert_cost",
            "future_slack"
          ],
          "acceptance_control.mode": [
            "threshold"
          ]
        }
      },
      {
        "target_id": "contract_review",
        "kind": "contract_review",
        "recommended_controls": {}
      }
    ],
    "action_space": {
      "allowed_actions": [
        "run_alns",
        "request_supervisor_review"
      ],
      "allowed_insertion_operators": [
        "greedy_insertion",
        "scarcity_first_insertion",
        "regret_insertion",
        "bottleneck_insertion",
        "diversified_insertion"
      ],
      "allowed_task_signals": [
        "priority_loss",
        "scarcity_pressure",
        "regret_pressure",
        "bottleneck_pressure",
        "mobility_opportunity"
      ],
      "allowed_position_signals": [
        "insert_cost",
        "future_slack",
        "route_balance_gain",
        "local_coupling_penalty",
        "diversity_gain"
      ],
      "allowed_destroy_operators": [
        "random_removal",
        "worst_task_removal",
        "related_cluster_removal",
        "critical_block_removal",
        "route_rebalance_removal"
      ],
      "allowed_destroy_signals": [
        "cost_pressure",
        "coupling_pressure",
        "route_balance_pressure",
        "mobility_opportunity",
        "scarcity_protection"
      ],
      "allowed_acceptance_modes": [
        "greedy",
        "threshold",
        "sa"
      ]
    },
    "usable_memory": [
      {
        "record_id": "M2",
        "target_kind": "unassigned_priority",
        "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
        "outcome": "missed_priority +0, unassigned_count +0, energy_total +0, accepted 0/1, blocker acceptance_rejected_trials"
      }
    ]
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "One Solver decision under the active supervisor contract.",
  "properties": {
    "solver_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "run_alns"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "destroy_control": {
              "type": "object",
              "description": "Executable destroy controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "random_removal",
                          "worst_task_removal",
                          "related_cluster_removal",
                          "critical_block_removal",
                          "route_rebalance_removal"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy signals.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy signals.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "cost_pressure",
                          "coupling_pressure",
                          "route_balance_pressure",
                          "mobility_opportunity",
                          "scarcity_protection"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Removal intensity from 0 to 10."
                }
              },
              "required": [
                "operator_scores",
                "signal_scores",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "insertion_control": {
              "type": "object",
              "description": "Executable insertion controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for insertion operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for insertion operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "greedy_insertion",
                          "scarcity_first_insertion",
                          "regret_insertion",
                          "bottleneck_insertion",
                          "diversified_insertion"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "task_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing the next task.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing the next task.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "priority_loss",
                          "scarcity_pressure",
                          "regret_pressure",
                          "bottleneck_pressure",
                          "mobility_opportunity"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "position_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing an insertion position.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing an insertion position.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "insert_cost",
                          "future_slack",
                          "route_balance_gain",
                          "local_coupling_penalty",
                          "diversity_gain"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "operator_scores",
                "task_signal_scores",
                "position_signal_scores"
              ],
              "additionalProperties": false
            },
            "acceptance_control": {
              "type": "object",
              "description": "Executable acceptance control.",
              "properties": {
                "mode": {
                  "type": "string",
                  "enum": [
                    "greedy",
                    "threshold",
                    "sa"
                  ],
                  "description": "Acceptance mode allowed for the current action space."
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Acceptance exploration intensity."
                }
              },
              "required": [
                "mode",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id",
            "destroy_control",
            "insertion_control",
            "acceptance_control"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "request_supervisor_review"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "solver_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #046 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 002

<details>
<summary>Open raw LLM output</summary>

```text
{"solver_decision": {"action": "run_alns", "target_id": "T_unassigned_priority", "destroy_control": {"operator_scores": [{"name": "related_cluster_removal", "score": 8}], "signal_scores": [{"name": "coupling_pressure", "score": 8}], "intensity_score": 5}, "insertion_control": {"operator_scores": [{"name": "scarcity_first_insertion", "score": 8}, {"name": "regret_insertion", "score": 7}], "task_signal_scores": [{"name": "priority_loss", "score": 9}, {"name": "scarcity_pressure", "score": 8}], "position_signal_scores": [{"name": "insert_cost", "score": 8}, {"name": "future_slack", "score": 7}]}, "acceptance_control": {"mode": "threshold", "intensity_score": 4}, "explanation": {"reason_summary": "Run one bounded local rebuild."}}}
```

</details>

### #047 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 002

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "related_cluster_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "coupling_pressure",
          "score": 8
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 8
        },
        {
          "name": "regret_insertion",
          "score": 7
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 8
        }
      ],
      "position_signal_scores": [
        {
          "name": "insert_cost",
          "score": 8
        },
        {
          "name": "future_slack",
          "score": 7
        }
      ]
    },
    "acceptance_control": {
      "mode": "threshold",
      "intensity_score": 4
    },
    "explanation": {
      "reason_summary": "Run one bounded local rebuild."
    }
  }
}
```

### #048 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 002

```json
{
  "manifest_id": "R3",
  "source_decision_id": "D3",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "trace_id": "X3",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 3,
      "max_actions": 3,
      "max_time_sec": 1.0,
      "max_iters": 3
    },
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 2,
        "related_cluster_removal": 8,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 8,
        "route_balance_pressure": 0,
        "mobility_opportunity": 0,
        "scarcity_protection": 0
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "threshold",
      "intensity_score": 4,
      "threshold": 2.0,
      "worsening_allowance": 0.08
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.worst_task_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0",
    "destroy.signal_weights.mobility_opportunity=0",
    "destroy.signal_weights.scarcity_protection=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #049 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 002

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 2,
      "related_cluster_removal": 8,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 8,
      "route_balance_pressure": 0,
      "mobility_opportunity": 0,
      "scarcity_protection": 0
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 8,
      "regret_insertion": 7,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 8,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 8,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "threshold",
    "intensity_score": 4,
    "accept_level": 0.08,
    "exploration_score": 2.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #050 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 002

```json
{
  "time_limit_sec": 0.33333333333333337,
  "max_iters": 1
}
```

### #051 [SOLVER] SOLVER_RESULT | C002 / SOLVER 002

```json
{
  "working_solution": {
    "is_feasible": true,
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      }
    },
    "quality_summary": {
      "missed_priority": 15.0,
      "unassigned_count": 14.0,
      "energy_total": 62031.7252777921,
      "total_distance": 56702.56307069573,
      "makespan": 21963.819830943008,
      "route_balance": 0.18311646218632116
    },
    "feasibility_summary": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_by_type": {
        "capability": 0.0,
        "time_window": 0.0,
        "energy": 0.0
      },
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      }
    }
  },
  "diagnostics": {
    "algorithm": "weighted_alns",
    "policy": {
      "destroy_policy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "threshold",
        "intensity_score": 4,
        "accept_level": 0.08,
        "exploration_score": 2.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 1,
    "actual_iters_used": 1,
    "actual_time_used_sec": 0.7102508999996644,
    "best_update_count": 1,
    "best_update_iters": [
      1
    ],
    "best_update_objective_keys": [
      {
        "contract": {
          "layers": [
            "missed_priority",
            "unassigned_count",
            "energy_total"
          ],
          "key": [
            15.0,
            14.0,
            62031.7252777921
          ]
        },
        "global": {
          "layers": [
            "missed_priority",
            "unassigned_count",
            "energy_total"
          ],
          "key": [
            15.0,
            14.0,
            62031.7252777921
          ]
        }
      }
    ],
    "first_best_iter": 1,
    "last_best_iter": 1,
    "plateau_iters_after_last_update": 0,
    "initial_solution_feasible": true,
    "returned_solution_source": "action_best_feasible",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": -1,
      "accepted": true,
      "accept_mode": "threshold",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "worst_task_removal",
      "shape": "task_set",
      "task_ids": [
        0,
        2,
        3,
        4,
        5,
        6,
        7,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        20
      ],
      "affected_routes": [
        0,
        1,
        2,
        4,
        5
      ],
      "features": {
        "cost_pressure": 1.0,
        "priority_loss": 1.0,
        "scarcity_pressure": 0.7646323319915161,
        "coupling_pressure": 1.0,
        "mobility_opportunity": 0.011509176200872853,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 8.0,
      "metadata": {
        "target_k": 17
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "scarcity_first_insertion": 4,
        "regret_insertion": 9,
        "greedy_insertion": 3,
        "bottleneck_insertion": 2,
        "diversified_insertion": 1
      },
      "unassigned_before": 33,
      "unassigned_after": 14,
      "inserted_count": 19,
      "failed_count": 14,
      "tasks_analyzed": 470,
      "positions_generated": 381,
      "positions_strict_checked": 381,
      "strict_feasible_positions": 381,
      "failure_breakdown": {
        "no_candidate": 194,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 6,
          "priority": 1.0,
          "capable_agents": 4,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 7,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 8,
          "priority": 1.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 9,
          "priority": 1.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 528.2709,
      "operator": "regret_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "action_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "global_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy.",
        "protected_metric_passed": true,
        "protected_metric_violations": [],
        "rejection_reason": null
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 0.0,
      "worst_task_removal": 1.0,
      "related_cluster_removal": 0.0,
      "critical_block_removal": 0.0,
      "route_rebalance_removal": 0.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 33.0,
      "tasks_reinserted": 19.0,
      "tasks_left_unassigned": 14.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 194.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 1.0,
          "worst_task_removal": 1.0,
          "related_cluster_removal": 1.0,
          "critical_block_removal": 1.0,
          "route_rebalance_removal": 1.0
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 2.0,
          "related_cluster_removal": 8.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.189207115002721,
          "worst_task_removal": 1.189207115002721,
          "related_cluster_removal": 1.681792830507429,
          "critical_block_removal": 1.189207115002721,
          "route_rebalance_removal": 1.189207115002721
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 8.0,
          "regret_insertion": 7.0,
          "bottleneck_insertion": 2.0,
          "diversified_insertion": 2.0
        }
      }
    },
    "feasibility_policy": {
      "mode": "strict"
    },
    "violation_ratios": {
      "energy": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      },
      "time_window": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      }
    },
    "feasibility_rejection_reasons": {},
    "protected_metric_rejections": 0,
    "protected_metric_rejection_reasons": {},
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "execution_trace": {
      "trace_id": "X3",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 1,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 0
        },
        "removed_task_count_avg": 17.0
      },
      "repair": {
        "candidate_tasks_total": 33,
        "tasks_reinserted": 19,
        "tasks_left_unassigned": 14,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 194
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 0,
        "accepted_trials": 1,
        "global_best_improved_trials": 1
      },
      "rejection_reasons": {}
    },
    "solution_flow": {
      "initial_working": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        }
      },
      "final_current": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "is_feasible": true
      },
      "action_best_feasible": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "is_feasible": true
      },
      "returned_solution_source": "action_best_feasible",
      "protected_metric_result": {
        "passed": true,
        "violations": []
      }
    },
    "accepted_trial_count": 1,
    "rejected_trial_count": 0
  }
}
```

### #052 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 002

```json
{
  "trace_id": "X3",
  "kind": "alns",
  "iters": 1,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 0,
      "worst_task_removal": 1,
      "related_cluster_removal": 0,
      "critical_block_removal": 0,
      "route_rebalance_removal": 0
    },
    "removed_task_count_avg": 17.0
  },
  "repair": {
    "candidate_tasks_total": 33,
    "tasks_reinserted": 19,
    "tasks_left_unassigned": 14,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 194
    }
  },
  "trial_flow": {
    "candidate_trials": 1,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "protected_metric_rejected": 0,
    "admissible_trials": 1,
    "acceptance_rejected": 0,
    "accepted_trials": 1,
    "global_best_improved_trials": 1
  },
  "rejection_reasons": {}
}
```

### #053 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 002

```json
{
  "verification_id": "V3",
  "contract_id": "C002",
  "decision_id": "D3",
  "manifest_id": "R3",
  "trace_id": "X3",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "protected_metric_baseline": {
    "missed_priority": 18.0,
    "unassigned_count": 16.0,
    "energy_total": 61731.554843921316,
    "total_distance": 56668.05133123227,
    "makespan": 21963.819830943008,
    "route_balance": 0.22961073240459418
  },
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": -3.0,
      "unassigned_count": -2.0,
      "energy_total": 300.1704338707859
    },
    "best_feasible": {
      "missed_priority": -3.0,
      "unassigned_count": -2.0,
      "energy_total": 300.1704338707859
    }
  },
  "debt_delta": {
    "energy": 0.0,
    "time_window": 0.0
  },
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "none",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false,
    "protected_metric_problem": false
  },
  "event_tags": [
    "working_quality_improved",
    "best_feasible_improved"
  ],
  "improvement_flags": {
    "working_contract_improved": true,
    "action_best_contract_improved": true,
    "run_global_best_improved": true,
    "protected_metrics_passed": true
  },
  "objective_keys": {
    "contract": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        15.0,
        14.0,
        62031.7252777921
      ]
    },
    "global": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        15.0,
        14.0,
        62031.7252777921
      ]
    }
  },
  "trace": {
    "trace_id": "X3",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 1,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 0
      },
      "removed_task_count_avg": 17.0
    },
    "repair": {
      "candidate_tasks_total": 33,
      "tasks_reinserted": 19,
      "tasks_left_unassigned": 14,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 194
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 0,
      "accepted_trials": 1,
      "global_best_improved_trials": 1
    },
    "rejection_reasons": {}
  }
}
```

### #054 [MEM] MEMORY_UPDATE | C002 / SOLVER 002

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M3",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O3",
  "decision_id": "D3",
  "manifest_id": "R3",
  "trace_id": "X3",
  "verification_id": "V3",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_operator_top": [
      "related_cluster_removal",
      "critical_block_removal"
    ],
    "destroy_signal_top": [
      "coupling_pressure"
    ],
    "insertion_operator_top": [
      "scarcity_first_insertion",
      "regret_insertion"
    ],
    "insertion_task_signal_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insertion_position_signal_top": [
      "insert_cost",
      "future_slack"
    ],
    "acceptance": "threshold:4"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "run_global_best_improved": true,
    "metric_delta": {
      "missed_priority": -3.0,
      "unassigned_count": -2.0,
      "energy_total": 300.1704338707859
    }
  },
  "manifest": {
    "manifest_id": "R3",
    "source_decision_id": "D3",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "trace_id": "X3",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 3,
        "max_actions": 3,
        "max_time_sec": 1.0,
        "max_iters": 3
      },
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "protected_metric_bounds": [
        {
          "metric": "unassigned_count",
          "baseline": 16.0,
          "max_worsen": 0.0
        }
      ],
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "threshold",
        "intensity_score": 4,
        "threshold": 2.0,
        "worsening_allowance": 0.08
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.worst_task_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0",
      "destroy.signal_weights.mobility_opportunity=0",
      "destroy.signal_weights.scarcity_protection=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X3",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 1,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 0
      },
      "removed_task_count_avg": 17.0
    },
    "repair": {
      "candidate_tasks_total": 33,
      "tasks_reinserted": 19,
      "tasks_left_unassigned": 14,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 194
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 0,
      "accepted_trials": 1,
      "global_best_improved_trials": 1
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V3",
    "contract_id": "C002",
    "decision_id": "D3",
    "manifest_id": "R3",
    "trace_id": "X3",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": -3.0,
        "unassigned_count": -2.0,
        "energy_total": 300.1704338707859
      },
      "best_feasible": {
        "missed_priority": -3.0,
        "unassigned_count": -2.0,
        "energy_total": 300.1704338707859
      }
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "none",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false,
      "protected_metric_problem": false
    },
    "event_tags": [
      "working_quality_improved",
      "best_feasible_improved"
    ],
    "improvement_flags": {
      "working_contract_improved": true,
      "action_best_contract_improved": true,
      "run_global_best_improved": true,
      "protected_metrics_passed": true
    },
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      }
    },
    "trace": {
      "trace_id": "X3",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 1,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 0
        },
        "removed_task_count_avg": 17.0
      },
      "repair": {
        "candidate_tasks_total": 33,
        "tasks_reinserted": 19,
        "tasks_left_unassigned": 14,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 194
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 0,
        "accepted_trials": 1,
        "global_best_improved_trials": 1
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #055 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 002

```json
{
  "contract_id": "C002",
  "solver_actions": 2,
  "time_used_sec": 0.666667,
  "iters_used": 2,
  "verification_ids": [
    "V2",
    "V3"
  ],
  "intent_status_counts": {
    "not_achieved": 1,
    "achieved": 1
  },
  "dominant_blocker_counts": {
    "acceptance_rejected_trials": 1,
    "none": 1
  },
  "condition_report": []
}
```

### #056 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 002

```json
{
  "completion_status": "continue",
  "completion_reason": "min_actions_not_reached",
  "condition_report": [],
  "completed": false
}
```

### #057 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 003

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O4",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 3,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "remaining_resources": {
      "actions": 1,
      "time_sec": 0.33333333333333326,
      "iters": 1,
      "min_actions_remaining": 1
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 15.0,
        "unassigned_count": 14.0,
        "energy_total": 62031.7252777921,
        "total_distance": 56702.56307069573,
        "makespan": 21963.819830943008,
        "route_balance": 0.18311646218632116
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "none",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 15.0,
        "unassigned_count": 14.0,
        "energy_total": 62031.7252777921,
        "total_distance": 56702.56307069573,
        "makespan": 21963.819830943008,
        "route_balance": 0.18311646218632116
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V3",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": -3.0,
      "unassigned_count": -2.0,
      "energy_total": 300.1704338707859
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 1,
      "feasibility_rejected": 0,
      "accepted": 1,
      "global_best_updates": 1
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "task_count": 14,
      "priority_mass": 15.0,
      "top_tasks": [
        {
          "task_id": 20,
          "priority": 3.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 7,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 61,
          "priority": 2.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 6,
          "priority": 1.0,
          "capable_agents": 4,
          "candidate_positions": 0,
          "feasible_positions": 0,
          "dominant_reason": "no_candidate_position"
        }
      ],
      "metric_pressure": {
        "missed_priority": 15.0,
        "unassigned_count": 14.0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "priority_loss",
          "scarcity_pressure"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack",
          "insert_cost"
        ],
        "destroy_control.signal_scores": [
          "mobility_opportunity",
          "scarcity_protection"
        ]
      }
    },
    {
      "target_id": "T_energy_debt",
      "kind": "energy_debt",
      "metric_pressure": {
        "energy_ratio": 0.0
      },
      "recommended_controls": {
        "destroy_control.signal_scores": [
          "cost_pressure",
          "mobility_opportunity"
        ],
        "insertion_control.position_signal_scores": [
          "insert_cost",
          "future_slack"
        ],
        "acceptance_control.mode": [
          "threshold"
        ]
      }
    },
    {
      "target_id": "contract_review",
      "kind": "contract_review",
      "recommended_controls": {}
    }
  ],
  "action_space": {
    "allowed_actions": [
      "run_alns",
      "request_supervisor_review"
    ],
    "allowed_insertion_operators": [
      "greedy_insertion",
      "scarcity_first_insertion",
      "regret_insertion",
      "bottleneck_insertion",
      "diversified_insertion"
    ],
    "allowed_task_signals": [
      "priority_loss",
      "scarcity_pressure",
      "regret_pressure",
      "bottleneck_pressure",
      "mobility_opportunity"
    ],
    "allowed_position_signals": [
      "insert_cost",
      "future_slack",
      "route_balance_gain",
      "local_coupling_penalty",
      "diversity_gain"
    ],
    "allowed_destroy_operators": [
      "random_removal",
      "worst_task_removal",
      "related_cluster_removal",
      "critical_block_removal",
      "route_rebalance_removal"
    ],
    "allowed_destroy_signals": [
      "cost_pressure",
      "coupling_pressure",
      "route_balance_pressure",
      "mobility_opportunity",
      "scarcity_protection"
    ],
    "allowed_acceptance_modes": [
      "greedy",
      "threshold",
      "sa"
    ]
  },
  "usable_memory": [
    {
      "record_id": "M2",
      "target_kind": "unassigned_priority",
      "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
      "outcome": "missed_priority +0, unassigned_count +0, energy_total +0, accepted 0/1, blocker acceptance_rejected_trials"
    },
    {
      "record_id": "M3",
      "target_kind": "unassigned_priority",
      "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
      "outcome": "missed_priority -3, unassigned_count -2, energy_total +300, accepted 1/1, blocker none"
    }
  ]
}
```

</details>

### #058 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 003

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SOLVER

INSTRUCTION:
Choose one allowed action. If executing a solver action, choose one target_id from decision_targets and choose controls only from action_space. Every operational field will be compiled and executed exactly. Each score name must be selected from the enum of that exact output field. Do not move names between destroy operator, destroy signal, insertion operator, task signal, and position signal fields.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O4",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 3,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "remaining_resources": {
        "actions": 1,
        "time_sec": 0.33333333333333326,
        "iters": 1,
        "min_actions_remaining": 1
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 15.0,
          "unassigned_count": 14.0,
          "energy_total": 62031.7252777921,
          "total_distance": 56702.56307069573,
          "makespan": 21963.819830943008,
          "route_balance": 0.18311646218632116
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "none",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 15.0,
          "unassigned_count": 14.0,
          "energy_total": 62031.7252777921,
          "total_distance": 56702.56307069573,
          "makespan": 21963.819830943008,
          "route_balance": 0.18311646218632116
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V3",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": -3.0,
        "unassigned_count": -2.0,
        "energy_total": 300.1704338707859
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 1,
        "feasibility_rejected": 0,
        "accepted": 1,
        "global_best_updates": 1
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 14,
        "priority_mass": 15.0,
        "top_tasks": [
          {
            "task_id": 20,
            "priority": 3.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 7,
            "priority": 2.0,
            "capable_agents": 3,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 61,
            "priority": 2.0,
            "capable_agents": 5,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 1,
            "priority": 1.0,
            "capable_agents": 2,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          },
          {
            "task_id": 6,
            "priority": 1.0,
            "capable_agents": 4,
            "candidate_positions": 0,
            "feasible_positions": 0,
            "dominant_reason": "no_candidate_position"
          }
        ],
        "metric_pressure": {
          "missed_priority": 15.0,
          "unassigned_count": 14.0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "priority_loss",
            "scarcity_pressure"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack",
            "insert_cost"
          ],
          "destroy_control.signal_scores": [
            "mobility_opportunity",
            "scarcity_protection"
          ]
        }
      },
      {
        "target_id": "T_energy_debt",
        "kind": "energy_debt",
        "metric_pressure": {
          "energy_ratio": 0.0
        },
        "recommended_controls": {
          "destroy_control.signal_scores": [
            "cost_pressure",
            "mobility_opportunity"
          ],
          "insertion_control.position_signal_scores": [
            "insert_cost",
            "future_slack"
          ],
          "acceptance_control.mode": [
            "threshold"
          ]
        }
      },
      {
        "target_id": "contract_review",
        "kind": "contract_review",
        "recommended_controls": {}
      }
    ],
    "action_space": {
      "allowed_actions": [
        "run_alns",
        "request_supervisor_review"
      ],
      "allowed_insertion_operators": [
        "greedy_insertion",
        "scarcity_first_insertion",
        "regret_insertion",
        "bottleneck_insertion",
        "diversified_insertion"
      ],
      "allowed_task_signals": [
        "priority_loss",
        "scarcity_pressure",
        "regret_pressure",
        "bottleneck_pressure",
        "mobility_opportunity"
      ],
      "allowed_position_signals": [
        "insert_cost",
        "future_slack",
        "route_balance_gain",
        "local_coupling_penalty",
        "diversity_gain"
      ],
      "allowed_destroy_operators": [
        "random_removal",
        "worst_task_removal",
        "related_cluster_removal",
        "critical_block_removal",
        "route_rebalance_removal"
      ],
      "allowed_destroy_signals": [
        "cost_pressure",
        "coupling_pressure",
        "route_balance_pressure",
        "mobility_opportunity",
        "scarcity_protection"
      ],
      "allowed_acceptance_modes": [
        "greedy",
        "threshold",
        "sa"
      ]
    },
    "usable_memory": [
      {
        "record_id": "M2",
        "target_kind": "unassigned_priority",
        "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
        "outcome": "missed_priority +0, unassigned_count +0, energy_total +0, accepted 0/1, blocker acceptance_rejected_trials"
      },
      {
        "record_id": "M3",
        "target_kind": "unassigned_priority",
        "control_summary": "related_cluster_removal + coupling_pressure + scarcity_first_insertion + priority_loss + insert_cost + threshold:4",
        "outcome": "missed_priority -3, unassigned_count -2, energy_total +300, accepted 1/1, blocker none"
      }
    ]
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "One Solver decision under the active supervisor contract.",
  "properties": {
    "solver_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "run_alns"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "destroy_control": {
              "type": "object",
              "description": "Executable destroy controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "random_removal",
                          "worst_task_removal",
                          "related_cluster_removal",
                          "critical_block_removal",
                          "route_rebalance_removal"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for destroy signals.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for destroy signals.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "cost_pressure",
                          "coupling_pressure",
                          "route_balance_pressure",
                          "mobility_opportunity",
                          "scarcity_protection"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Removal intensity from 0 to 10."
                }
              },
              "required": [
                "operator_scores",
                "signal_scores",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "insertion_control": {
              "type": "object",
              "description": "Executable insertion controls.",
              "properties": {
                "operator_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for insertion operators.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for insertion operators.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "greedy_insertion",
                          "scarcity_first_insertion",
                          "regret_insertion",
                          "bottleneck_insertion",
                          "diversified_insertion"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "task_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing the next task.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing the next task.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "priority_loss",
                          "scarcity_pressure",
                          "regret_pressure",
                          "bottleneck_pressure",
                          "mobility_opportunity"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                },
                "position_signal_scores": {
                  "type": "array",
                  "description": "Sparse emphasis scores for choosing an insertion position.",
                  "minItems": 0,
                  "maxItems": 3,
                  "items": {
                    "type": "object",
                    "description": "Sparse emphasis scores for choosing an insertion position.",
                    "properties": {
                      "name": {
                        "type": "string",
                        "enum": [
                          "insert_cost",
                          "future_slack",
                          "route_balance_gain",
                          "local_coupling_penalty",
                          "diversity_gain"
                        ],
                        "description": "Candidate name allowed for this exact score field."
                      },
                      "score": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "description": "Executable emphasis score from 0 to 10."
                      }
                    },
                    "required": [
                      "name",
                      "score"
                    ],
                    "additionalProperties": false
                  }
                }
              },
              "required": [
                "operator_scores",
                "task_signal_scores",
                "position_signal_scores"
              ],
              "additionalProperties": false
            },
            "acceptance_control": {
              "type": "object",
              "description": "Executable acceptance control.",
              "properties": {
                "mode": {
                  "type": "string",
                  "enum": [
                    "greedy",
                    "threshold",
                    "sa"
                  ],
                  "description": "Acceptance mode allowed for the current action space."
                },
                "intensity_score": {
                  "type": "integer",
                  "minimum": 0,
                  "maximum": 10,
                  "description": "Acceptance exploration intensity."
                }
              },
              "required": [
                "mode",
                "intensity_score"
              ],
              "additionalProperties": false
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id",
            "destroy_control",
            "insertion_control",
            "acceptance_control"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "request_supervisor_review"
            },
            "target_id": {
              "type": "string",
              "enum": [
                "T_unassigned_priority",
                "T_energy_debt",
                "contract_review"
              ],
              "description": "Target id from current decision_targets."
            },
            "explanation": {
              "type": "object",
              "description": "Human-readable explanation ignored by validator/compiler/runtime.",
              "additionalProperties": {
                "type": "string"
              }
            }
          },
          "required": [
            "action",
            "target_id"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "solver_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #059 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 003

<details>
<summary>Open raw LLM output</summary>

```text
{"solver_decision": {"action": "run_alns", "target_id": "T_unassigned_priority", "destroy_control": {"operator_scores": [{"name": "related_cluster_removal", "score": 8}], "signal_scores": [{"name": "coupling_pressure", "score": 8}], "intensity_score": 5}, "insertion_control": {"operator_scores": [{"name": "scarcity_first_insertion", "score": 8}, {"name": "regret_insertion", "score": 7}], "task_signal_scores": [{"name": "priority_loss", "score": 9}, {"name": "scarcity_pressure", "score": 8}], "position_signal_scores": [{"name": "insert_cost", "score": 8}, {"name": "future_slack", "score": 7}]}, "acceptance_control": {"mode": "threshold", "intensity_score": 4}, "explanation": {"reason_summary": "Run one bounded local rebuild."}}}
```

</details>

### #060 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 003

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "related_cluster_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "coupling_pressure",
          "score": 8
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 8
        },
        {
          "name": "regret_insertion",
          "score": 7
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 8
        }
      ],
      "position_signal_scores": [
        {
          "name": "insert_cost",
          "score": 8
        },
        {
          "name": "future_slack",
          "score": 7
        }
      ]
    },
    "acceptance_control": {
      "mode": "threshold",
      "intensity_score": 4
    },
    "explanation": {
      "reason_summary": "Run one bounded local rebuild."
    }
  }
}
```

### #061 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 003

```json
{
  "manifest_id": "R4",
  "source_decision_id": "D4",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "trace_id": "X4",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 3,
      "max_actions": 3,
      "max_time_sec": 1.0,
      "max_iters": 3
    },
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 2,
        "related_cluster_removal": 8,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 8,
        "route_balance_pressure": 0,
        "mobility_opportunity": 0,
        "scarcity_protection": 0
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "threshold",
      "intensity_score": 4,
      "threshold": 2.0,
      "worsening_allowance": 0.08
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.worst_task_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0",
    "destroy.signal_weights.mobility_opportunity=0",
    "destroy.signal_weights.scarcity_protection=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #062 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 003

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 2,
      "related_cluster_removal": 8,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 8,
      "route_balance_pressure": 0,
      "mobility_opportunity": 0,
      "scarcity_protection": 0
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 8,
      "regret_insertion": 7,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 8,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 8,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "threshold",
    "intensity_score": 4,
    "accept_level": 0.08,
    "exploration_score": 2.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #063 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 003

```json
{
  "time_limit_sec": 0.33333333333333326,
  "max_iters": 1
}
```

### #064 [SOLVER] SOLVER_RESULT | C002 / SOLVER 003

```json
{
  "working_solution": {
    "is_feasible": true,
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      }
    },
    "quality_summary": {
      "missed_priority": 15.0,
      "unassigned_count": 14.0,
      "energy_total": 62031.7252777921,
      "total_distance": 56702.56307069573,
      "makespan": 21963.819830943008,
      "route_balance": 0.18311646218632116
    },
    "feasibility_summary": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_by_type": {
        "capability": 0.0,
        "time_window": 0.0,
        "energy": 0.0
      },
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      }
    }
  },
  "diagnostics": {
    "algorithm": "weighted_alns",
    "policy": {
      "destroy_policy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "threshold",
        "intensity_score": 4,
        "accept_level": 0.08,
        "exploration_score": 2.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 1,
    "actual_iters_used": 1,
    "actual_time_used_sec": 0.6337619000005361,
    "best_update_count": 0,
    "best_update_iters": [],
    "best_update_objective_keys": [],
    "first_best_iter": null,
    "last_best_iter": null,
    "plateau_iters_after_last_update": 1,
    "initial_solution_feasible": true,
    "returned_solution_source": "action_best_feasible",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 1,
      "accepted": true,
      "accept_mode": "threshold",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy.",
      "delta_soft": 0.003114906649773126,
      "threshold": 0.0196
    },
    "last_destroy_move": {
      "operator_name": "worst_task_removal",
      "shape": "task_set",
      "task_ids": [
        0,
        2,
        3,
        4,
        5,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        21,
        22
      ],
      "affected_routes": [
        0,
        1,
        2,
        4,
        5
      ],
      "features": {
        "cost_pressure": 1.0,
        "priority_loss": 1.0,
        "scarcity_pressure": 0.7254901960784313,
        "coupling_pressure": 1.0,
        "mobility_opportunity": 0.0,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 8.0,
      "metadata": {
        "target_k": 17
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "scarcity_first_insertion": 10,
        "greedy_insertion": 1,
        "diversified_insertion": 2,
        "regret_insertion": 4
      },
      "unassigned_before": 31,
      "unassigned_after": 14,
      "inserted_count": 17,
      "failed_count": 14,
      "tasks_analyzed": 405,
      "positions_generated": 309,
      "positions_strict_checked": 309,
      "strict_feasible_positions": 309,
      "failure_breakdown": {
        "no_candidate": 166,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 6,
          "priority": 1.0,
          "capable_agents": 4,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 7,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 8,
          "priority": 1.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 9,
          "priority": 1.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 446.1809,
      "operator": "regret_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62225.55206370113
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62225.55206370113
            ]
          }
        },
        "action_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "global_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy.",
        "protected_metric_passed": true,
        "protected_metric_violations": [],
        "rejection_reason": null
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 0.0,
      "worst_task_removal": 1.0,
      "related_cluster_removal": 0.0,
      "critical_block_removal": 0.0,
      "route_rebalance_removal": 0.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 31.0,
      "tasks_reinserted": 17.0,
      "tasks_left_unassigned": 14.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 166.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 1.0,
          "worst_task_removal": 1.0,
          "related_cluster_removal": 1.0,
          "critical_block_removal": 1.0,
          "route_rebalance_removal": 1.0
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 2.0,
          "related_cluster_removal": 8.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.189207115002721,
          "worst_task_removal": 1.189207115002721,
          "related_cluster_removal": 1.681792830507429,
          "critical_block_removal": 1.189207115002721,
          "route_rebalance_removal": 1.189207115002721
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 8.0,
          "regret_insertion": 7.0,
          "bottleneck_insertion": 2.0,
          "diversified_insertion": 2.0
        }
      }
    },
    "feasibility_policy": {
      "mode": "strict"
    },
    "violation_ratios": {
      "energy": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      },
      "time_window": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      }
    },
    "feasibility_rejection_reasons": {},
    "protected_metric_rejections": 0,
    "protected_metric_rejection_reasons": {},
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "execution_trace": {
      "trace_id": "X4",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 1,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 0
        },
        "removed_task_count_avg": 17.0
      },
      "repair": {
        "candidate_tasks_total": 31,
        "tasks_reinserted": 17,
        "tasks_left_unassigned": 14,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 166
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 0,
        "accepted_trials": 1,
        "global_best_improved_trials": 0
      },
      "rejection_reasons": {}
    },
    "solution_flow": {
      "initial_working": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        }
      },
      "final_current": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62225.55206370113
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62225.55206370113
            ]
          }
        },
        "is_feasible": true
      },
      "action_best_feasible": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "is_feasible": true
      },
      "returned_solution_source": "action_best_feasible",
      "protected_metric_result": {
        "passed": true,
        "violations": []
      }
    },
    "accepted_trial_count": 1,
    "rejected_trial_count": 0
  }
}
```

### #065 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 003

```json
{
  "trace_id": "X4",
  "kind": "alns",
  "iters": 1,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 0,
      "worst_task_removal": 1,
      "related_cluster_removal": 0,
      "critical_block_removal": 0,
      "route_rebalance_removal": 0
    },
    "removed_task_count_avg": 17.0
  },
  "repair": {
    "candidate_tasks_total": 31,
    "tasks_reinserted": 17,
    "tasks_left_unassigned": 14,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 166
    }
  },
  "trial_flow": {
    "candidate_trials": 1,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "protected_metric_rejected": 0,
    "admissible_trials": 1,
    "acceptance_rejected": 0,
    "accepted_trials": 1,
    "global_best_improved_trials": 0
  },
  "rejection_reasons": {}
}
```

### #066 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 003

```json
{
  "verification_id": "V4",
  "contract_id": "C002",
  "decision_id": "D4",
  "manifest_id": "R4",
  "trace_id": "X4",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "protected_metric_baseline": {
    "missed_priority": 18.0,
    "unassigned_count": 16.0,
    "energy_total": 61731.554843921316,
    "total_distance": 56668.05133123227,
    "makespan": 21963.819830943008,
    "route_balance": 0.22961073240459418
  },
  "intent_status": "not_achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    },
    "best_feasible": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    }
  },
  "debt_delta": {
    "energy": 0.0,
    "time_window": 0.0
  },
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "no_quality_gain",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": true,
    "protected_metric_problem": false
  },
  "event_tags": [
    "no_quality_gain"
  ],
  "improvement_flags": {
    "working_contract_improved": false,
    "action_best_contract_improved": false,
    "run_global_best_improved": false,
    "protected_metrics_passed": true
  },
  "objective_keys": {
    "contract": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        15.0,
        14.0,
        62031.7252777921
      ]
    },
    "global": {
      "layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "key": [
        15.0,
        14.0,
        62031.7252777921
      ]
    }
  },
  "trace": {
    "trace_id": "X4",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 1,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 0
      },
      "removed_task_count_avg": 17.0
    },
    "repair": {
      "candidate_tasks_total": 31,
      "tasks_reinserted": 17,
      "tasks_left_unassigned": 14,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 166
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 0,
      "accepted_trials": 1,
      "global_best_improved_trials": 0
    },
    "rejection_reasons": {}
  }
}
```

### #067 [MEM] MEMORY_UPDATE | C002 / SOLVER 003

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M4",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O4",
  "decision_id": "D4",
  "manifest_id": "R4",
  "trace_id": "X4",
  "verification_id": "V4",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_operator_top": [
      "related_cluster_removal",
      "critical_block_removal"
    ],
    "destroy_signal_top": [
      "coupling_pressure"
    ],
    "insertion_operator_top": [
      "scarcity_first_insertion",
      "regret_insertion"
    ],
    "insertion_task_signal_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insertion_position_signal_top": [
      "insert_cost",
      "future_slack"
    ],
    "acceptance": "threshold:4"
  },
  "outcome_fingerprint": {
    "intent_status": "not_achieved",
    "dominant_blocker": "no_quality_gain",
    "run_global_best_improved": false,
    "metric_delta": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": 0.0
    }
  },
  "manifest": {
    "manifest_id": "R4",
    "source_decision_id": "D4",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "trace_id": "X4",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 3,
        "max_actions": 3,
        "max_time_sec": 1.0,
        "max_iters": 3
      },
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      },
      "protected_metric_bounds": [
        {
          "metric": "unassigned_count",
          "baseline": 16.0,
          "max_worsen": 0.0
        }
      ],
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "threshold",
        "intensity_score": 4,
        "threshold": 2.0,
        "worsening_allowance": 0.08
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.worst_task_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0",
      "destroy.signal_weights.mobility_opportunity=0",
      "destroy.signal_weights.scarcity_protection=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X4",
    "kind": "alns",
    "iters": 1,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 0,
        "worst_task_removal": 1,
        "related_cluster_removal": 0,
        "critical_block_removal": 0,
        "route_rebalance_removal": 0
      },
      "removed_task_count_avg": 17.0
    },
    "repair": {
      "candidate_tasks_total": 31,
      "tasks_reinserted": 17,
      "tasks_left_unassigned": 14,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 166
      }
    },
    "trial_flow": {
      "candidate_trials": 1,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "protected_metric_rejected": 0,
      "admissible_trials": 1,
      "acceptance_rejected": 0,
      "accepted_trials": 1,
      "global_best_improved_trials": 0
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V4",
    "contract_id": "C002",
    "decision_id": "D4",
    "manifest_id": "R4",
    "trace_id": "X4",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "intent_status": "not_achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      },
      "best_feasible": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      }
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "no_quality_gain",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": true,
      "protected_metric_problem": false
    },
    "event_tags": [
      "no_quality_gain"
    ],
    "improvement_flags": {
      "working_contract_improved": false,
      "action_best_contract_improved": false,
      "run_global_best_improved": false,
      "protected_metrics_passed": true
    },
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      }
    },
    "trace": {
      "trace_id": "X4",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 1,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 0
        },
        "removed_task_count_avg": 17.0
      },
      "repair": {
        "candidate_tasks_total": 31,
        "tasks_reinserted": 17,
        "tasks_left_unassigned": 14,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 166
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 0,
        "accepted_trials": 1,
        "global_best_improved_trials": 0
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #068 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 003

```json
{
  "contract_id": "C002",
  "solver_actions": 3,
  "time_used_sec": 1.0,
  "iters_used": 3,
  "verification_ids": [
    "V2",
    "V3",
    "V4"
  ],
  "intent_status_counts": {
    "not_achieved": 2,
    "achieved": 1
  },
  "dominant_blocker_counts": {
    "acceptance_rejected_trials": 1,
    "none": 1,
    "no_quality_gain": 1
  },
  "condition_report": [
    {
      "condition_id": "S_best",
      "source": "last.improvement_flags.run_global_best_improved",
      "actual": false,
      "op": "==",
      "expected": true,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "F_no_gain",
      "source": "aggregate.not_achieved",
      "actual": 2,
      "op": ">=",
      "expected": 3,
      "window": 3,
      "passed": false
    }
  ]
}
```

### #069 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 003

```json
{
  "completion_status": "resource_exhausted",
  "completion_reason": "max_actions_reached",
  "condition_report": [
    {
      "condition_id": "S_best",
      "source": "last.improvement_flags.run_global_best_improved",
      "actual": false,
      "op": "==",
      "expected": true,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "F_no_gain",
      "source": "aggregate.not_achieved",
      "actual": 2,
      "op": ">=",
      "expected": 3,
      "window": 3,
      "passed": false
    }
  ],
  "completed": true
}
```

### #070 [CONTRACT] CONTRACT_END | C002

```json
{
  "completion": {
    "completion_status": "resource_exhausted",
    "completion_reason": "max_actions_reached",
    "condition_report": [
      {
        "condition_id": "S_best",
        "source": "last.improvement_flags.run_global_best_improved",
        "actual": false,
        "op": "==",
        "expected": true,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "F_no_gain",
        "source": "aggregate.not_achieved",
        "actual": 2,
        "op": ">=",
        "expected": 3,
        "window": 3,
        "passed": false
      }
    ],
    "completed": true
  },
  "memory_update": {
    "summary_id": "CS2",
    "kind": "contract_summary",
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      {
        "metric": "missed_priority",
        "direction": "min"
      },
      {
        "metric": "unassigned_count",
        "direction": "min"
      },
      {
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    },
    "progress": {
      "contract_id": "C002",
      "solver_actions": 3,
      "time_used_sec": 1.0,
      "iters_used": 3,
      "verification_ids": [
        "V2",
        "V3",
        "V4"
      ],
      "intent_status_counts": {
        "not_achieved": 2,
        "achieved": 1
      },
      "dominant_blocker_counts": {
        "acceptance_rejected_trials": 1,
        "none": 1,
        "no_quality_gain": 1
      },
      "condition_report": [
        {
          "condition_id": "S_best",
          "source": "last.improvement_flags.run_global_best_improved",
          "actual": false,
          "op": "==",
          "expected": true,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "F_no_gain",
          "source": "aggregate.not_achieved",
          "actual": 2,
          "op": ">=",
          "expected": 3,
          "window": 3,
          "passed": false
        }
      ]
    },
    "completion": {
      "completion_status": "resource_exhausted",
      "completion_reason": "max_actions_reached",
      "condition_report": [
        {
          "condition_id": "S_best",
          "source": "last.improvement_flags.run_global_best_improved",
          "actual": false,
          "op": "==",
          "expected": true,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "F_no_gain",
          "source": "aggregate.not_achieved",
          "actual": 2,
          "op": ">=",
          "expected": 3,
          "window": 3,
          "passed": false
        }
      ],
      "completed": true
    }
  }
}
```

### #071 [OBS] SUPERVISOR_REVIEW_OBSERVATION | C002

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O_review_4",
  "frame_type": "supervisor_review",
  "role": "supervisor",
  "budget_caps": {
    "max_solver_actions": 0,
    "max_time_sec": 9.0,
    "max_iters": 47
  },
  "completed_contract": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [
      {
        "metric": "unassigned_count",
        "max_worsen": 0
      }
    ],
    "protected_metric_baseline": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 61731.554843921316,
      "total_distance": 56668.05133123227,
      "makespan": 21963.819830943008,
      "route_balance": 0.22961073240459418
    }
  },
  "contract_completion": {
    "completion_status": "resource_exhausted",
    "completion_reason": "max_actions_reached",
    "condition_report": [
      {
        "condition_id": "S_best",
        "source": "last.improvement_flags.run_global_best_improved",
        "actual": false,
        "op": "==",
        "expected": true,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "F_no_gain",
        "source": "aggregate.not_achieved",
        "actual": 2,
        "op": ">=",
        "expected": 3,
        "window": 3,
        "passed": false
      }
    ],
    "completed": true
  },
  "condition_report": [
    {
      "condition_id": "S_best",
      "source": "last.improvement_flags.run_global_best_improved",
      "actual": false,
      "op": "==",
      "expected": true,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "F_no_gain",
      "source": "aggregate.not_achieved",
      "actual": 2,
      "op": ">=",
      "expected": 3,
      "window": 3,
      "passed": false
    }
  ],
  "stage_verification_summary": {
    "verification_ids": [
      "V2",
      "V3",
      "V4"
    ],
    "intent_status_counts": {
      "not_achieved": 2,
      "achieved": 1
    },
    "dominant_blocker_counts": {
      "acceptance_rejected_trials": 1,
      "none": 1,
      "no_quality_gain": 1
    },
    "last": {
      "exists": true,
      "verification_id": "V4",
      "intent_status": "not_achieved",
      "dominant_blocker": "no_quality_gain",
      "metric_delta": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": 0.0
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 1,
        "feasibility_rejected": 0,
        "accepted": 1,
        "global_best_updates": 0
      }
    }
  },
  "solution_position": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 15.0,
        "unassigned_count": 14.0,
        "energy_total": 62031.7252777921,
        "total_distance": 56702.56307069573,
        "makespan": 21963.819830943008,
        "route_balance": 0.18311646218632116
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "none",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 15.0,
        "unassigned_count": 14.0,
        "energy_total": 62031.7252777921,
        "total_distance": 56702.56307069573,
        "makespan": 21963.819830943008,
        "route_balance": 0.18311646218632116
      }
    }
  },
  "usable_memory": [
    {
      "summary_id": "CS2",
      "contract_id": "C002",
      "contract_type": "alns_search",
      "completion_status": "resource_exhausted",
      "condition_report": [
        {
          "condition_id": "S_best",
          "source": "last.improvement_flags.run_global_best_improved",
          "actual": false,
          "op": "==",
          "expected": true,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "F_no_gain",
          "source": "aggregate.not_achieved",
          "actual": 2,
          "op": ">=",
          "expected": 3,
          "window": 3,
          "passed": false
        }
      ]
    },
    {
      "record_id": "M1",
      "contract_id": "C001",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M2",
      "contract_id": "C002",
      "intent_status": "not_achieved",
      "dominant_blocker": "acceptance_rejected_trials"
    },
    {
      "record_id": "M3",
      "contract_id": "C002",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M4",
      "contract_id": "C002",
      "intent_status": "not_achieved",
      "dominant_blocker": "no_quality_gain"
    }
  ],
  "relaxation_reference": {
    "time_window_median_width": 100.0,
    "agent_energy_median": 13967.103715264191
  },
  "allowed_contract_types": [
    "alns_search",
    "recovery",
    "final_refinement"
  ],
  "allowed_objective_metrics": [
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance"
  ],
  "next_contract_resource_limits": {
    "max_solver_actions_allowed": 0,
    "max_time_sec_allowed": 9.0,
    "max_iters_allowed": 47
  }
}
```

</details>

### #072 [PROMPT] SUPERVISOR_REVIEW_PROMPT | C002

<details>
<summary>Open generated prompt</summary>

```text
ROLE: SUPERVISOR_REVIEW

INSTRUCTION:
Use condition_report, stage_verification_summary, solution_position, and budget_caps to decide whether to stop or issue the next executable contract. Put human-readable text only in contract_review or explanation.

CONTEXT:
{
  "user_goal": "Prioritize valuable task coverage, then reduce resource use.",
  "observation": {
    "observation_id": "O_review_4",
    "frame_type": "supervisor_review",
    "role": "supervisor",
    "budget_caps": {
      "max_solver_actions": 0,
      "max_time_sec": 9.0,
      "max_iters": 47
    },
    "completed_contract": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [
        {
          "metric": "unassigned_count",
          "max_worsen": 0
        }
      ],
      "protected_metric_baseline": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 61731.554843921316,
        "total_distance": 56668.05133123227,
        "makespan": 21963.819830943008,
        "route_balance": 0.22961073240459418
      }
    },
    "contract_completion": {
      "completion_status": "resource_exhausted",
      "completion_reason": "max_actions_reached",
      "condition_report": [
        {
          "condition_id": "S_best",
          "source": "last.improvement_flags.run_global_best_improved",
          "actual": false,
          "op": "==",
          "expected": true,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "F_no_gain",
          "source": "aggregate.not_achieved",
          "actual": 2,
          "op": ">=",
          "expected": 3,
          "window": 3,
          "passed": false
        }
      ],
      "completed": true
    },
    "condition_report": [
      {
        "condition_id": "S_best",
        "source": "last.improvement_flags.run_global_best_improved",
        "actual": false,
        "op": "==",
        "expected": true,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "F_no_gain",
        "source": "aggregate.not_achieved",
        "actual": 2,
        "op": ">=",
        "expected": 3,
        "window": 3,
        "passed": false
      }
    ],
    "stage_verification_summary": {
      "verification_ids": [
        "V2",
        "V3",
        "V4"
      ],
      "intent_status_counts": {
        "not_achieved": 2,
        "achieved": 1
      },
      "dominant_blocker_counts": {
        "acceptance_rejected_trials": 1,
        "none": 1,
        "no_quality_gain": 1
      },
      "last": {
        "exists": true,
        "verification_id": "V4",
        "intent_status": "not_achieved",
        "dominant_blocker": "no_quality_gain",
        "metric_delta": {
          "missed_priority": 0.0,
          "unassigned_count": 0.0,
          "energy_total": 0.0
        },
        "debt_delta": {
          "energy": 0.0,
          "time_window": 0.0
        },
        "trace_counts": {
          "candidate_trials": 1,
          "feasibility_rejected": 0,
          "accepted": 1,
          "global_best_updates": 0
        }
      }
    },
    "solution_position": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 15.0,
          "unassigned_count": 14.0,
          "energy_total": 62031.7252777921,
          "total_distance": 56702.56307069573,
          "makespan": 21963.819830943008,
          "route_balance": 0.18311646218632116
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "none",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 15.0,
          "unassigned_count": 14.0,
          "energy_total": 62031.7252777921,
          "total_distance": 56702.56307069573,
          "makespan": 21963.819830943008,
          "route_balance": 0.18311646218632116
        }
      }
    },
    "usable_memory": [
      {
        "summary_id": "CS2",
        "contract_id": "C002",
        "contract_type": "alns_search",
        "completion_status": "resource_exhausted",
        "condition_report": [
          {
            "condition_id": "S_best",
            "source": "last.improvement_flags.run_global_best_improved",
            "actual": false,
            "op": "==",
            "expected": true,
            "window": 1,
            "passed": false
          },
          {
            "condition_id": "F_no_gain",
            "source": "aggregate.not_achieved",
            "actual": 2,
            "op": ">=",
            "expected": 3,
            "window": 3,
            "passed": false
          }
        ]
      },
      {
        "record_id": "M1",
        "contract_id": "C001",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M2",
        "contract_id": "C002",
        "intent_status": "not_achieved",
        "dominant_blocker": "acceptance_rejected_trials"
      },
      {
        "record_id": "M3",
        "contract_id": "C002",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M4",
        "contract_id": "C002",
        "intent_status": "not_achieved",
        "dominant_blocker": "no_quality_gain"
      }
    ],
    "relaxation_reference": {
      "time_window_median_width": 100.0,
      "agent_energy_median": 13967.103715264191
    },
    "allowed_contract_types": [
      "alns_search",
      "recovery",
      "final_refinement"
    ],
    "allowed_objective_metrics": [
      "missed_priority",
      "unassigned_count",
      "energy_total",
      "total_distance",
      "makespan",
      "route_balance"
    ],
    "next_contract_resource_limits": {
      "max_solver_actions_allowed": 0,
      "max_time_sec_allowed": 9.0,
      "max_iters_allowed": 47
    }
  }
}

OUTPUT JSON SCHEMA:
{
  "type": "object",
  "description": "Supervisor decision after a contract has ended.",
  "properties": {
    "supervisor_decision": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "issue_contract"
            },
            "contract_review": {
              "type": "object",
              "description": "Human-readable review ignored by runtime.",
              "properties": {
                "outcome_summary": {
                  "type": "string",
                  "description": "What happened during the completed contract."
                },
                "main_lesson": {
                  "type": "string",
                  "description": "Most important lesson for the next stage."
                }
              },
              "required": [
                "outcome_summary",
                "main_lesson"
              ],
              "additionalProperties": false
            },
            "next_contract": {
              "type": "object",
              "description": "A supervisor-issued executable search contract.",
              "properties": {
                "contract_type": {
                  "type": "string",
                  "enum": [
                    "initial_construction",
                    "alns_search",
                    "recovery",
                    "final_refinement"
                  ]
                },
                "objective_layers": {
                  "type": "array",
                  "minItems": 1,
                  "maxItems": 4,
                  "items": {
                    "type": "string",
                    "enum": [
                      "missed_priority",
                      "unassigned_count",
                      "energy_total",
                      "total_distance",
                      "makespan",
                      "route_balance"
                    ]
                  }
                },
                "feasibility_control": {
                  "type": "object",
                  "description": "Stage-level feasibility handling selected by Supervisor.",
                  "properties": {
                    "mode": {
                      "type": "string",
                      "enum": [
                        "strict",
                        "relaxed_recoverable",
                        "recovery_only"
                      ],
                      "description": "Feasibility mode for this contract."
                    },
                    "relaxation_ratios": {
                      "type": "array",
                      "description": "Temporary recoverable relaxation ratios. Used by relaxed_recoverable.",
                      "maxItems": 2,
                      "items": {
                        "type": "object",
                        "description": "One temporary recoverable relaxation allowance.",
                        "properties": {
                          "violation_type": {
                            "type": "string",
                            "enum": [
                              "time_window",
                              "energy"
                            ],
                            "description": "Relaxable violation type."
                          },
                          "max_ratio": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 0.3,
                            "description": "Normalized temporary allowance for this violation type."
                          }
                        },
                        "required": [
                          "violation_type",
                          "max_ratio"
                        ],
                        "additionalProperties": false
                      }
                    }
                  },
                  "required": [
                    "mode",
                    "relaxation_ratios"
                  ],
                  "additionalProperties": false
                },
                "target_policy": {
                  "type": "object",
                  "description": "Executable target preference for the next contract.",
                  "properties": {
                    "preferred_target_kinds": {
                      "type": "array",
                      "minItems": 0,
                      "maxItems": 4,
                      "items": {
                        "type": "string",
                        "enum": [
                          "unassigned_priority",
                          "insertion_scarce_unassigned",
                          "energy_debt",
                          "time_window_debt",
                          "route_balance"
                        ]
                      }
                    }
                  },
                  "required": [
                    "preferred_target_kinds"
                  ],
                  "additionalProperties": false
                },
                "protected_metrics": {
                  "type": "array",
                  "maxItems": 4,
                  "items": {
                    "type": "object",
                    "description": "Hard non-worsening bound for this contract. max_worsen is measured relative to contract_start_quality. A violating candidate is ineligible for trial acceptance, action-best, returned-working, or best updates.",
                    "properties": {
                      "metric": {
                        "type": "string",
                        "enum": [
                          "missed_priority",
                          "unassigned_count",
                          "energy_total",
                          "total_distance",
                          "makespan",
                          "route_balance"
                        ]
                      },
                      "max_worsen": {
                        "type": "number",
                        "minimum": 0.0
                      }
                    },
                    "required": [
                      "metric",
                      "max_worsen"
                    ],
                    "additionalProperties": false
                  }
                },
                "resource_policy": {
                  "type": "object",
                  "description": "Executable resource limits for this contract.",
                  "properties": {
                    "min_actions": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 0
                    },
                    "max_actions": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 0
                    },
                    "max_iters": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 47
                    },
                    "max_time_sec": {
                      "type": "number",
                      "exclusiveMinimum": 0,
                      "maximum": 9.0
                    }
                  },
                  "required": [
                    "min_actions",
                    "max_actions",
                    "max_iters",
                    "max_time_sec"
                  ],
                  "additionalProperties": false
                },
                "exit_conditions": {
                  "type": "object",
                  "description": "Typed success and failure conditions.",
                  "properties": {
                    "success": {
                      "type": "array",
                      "maxItems": 4,
                      "items": {
                        "type": "object",
                        "description": "Typed condition evaluated by ContractMonitor.",
                        "properties": {
                          "condition_id": {
                            "type": "string",
                            "description": "Stable id unique inside this contract condition set."
                          },
                          "source": {
                            "type": "string",
                            "enum": [
                              "progress.solver_actions",
                              "progress.iters_used",
                              "progress.time_used_sec",
                              "last.intent_status",
                              "last.dominant_blocker",
                              "last.improvement_flags.run_global_best_improved",
                              "aggregate.achieved",
                              "aggregate.partial",
                              "aggregate.not_achieved",
                              "aggregate.regressed",
                              "aggregate.solver_requested_review",
                              "working.is_feasible",
                              "working.missed_priority",
                              "working.unassigned_count",
                              "working.energy_total",
                              "working.total_distance",
                              "working.makespan",
                              "working.route_balance",
                              "best_feasible.exists",
                              "best_feasible.missed_priority",
                              "best_feasible.unassigned_count",
                              "best_feasible.energy_total",
                              "best_feasible.total_distance",
                              "best_feasible.makespan",
                              "best_feasible.route_balance"
                            ],
                            "description": "Executable source path read by ContractMonitor."
                          },
                          "op": {
                            "type": "string",
                            "enum": [
                              "<",
                              "<=",
                              "==",
                              "!=",
                              ">=",
                              ">"
                            ]
                          },
                          "value": {
                            "type": [
                              "number",
                              "string",
                              "boolean"
                            ]
                          },
                          "window": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20
                          }
                        },
                        "required": [
                          "condition_id",
                          "source",
                          "op",
                          "value",
                          "window"
                        ],
                        "additionalProperties": false
                      }
                    },
                    "failure": {
                      "type": "array",
                      "maxItems": 4,
                      "items": {
                        "type": "object",
                        "description": "Typed condition evaluated by ContractMonitor.",
                        "properties": {
                          "condition_id": {
                            "type": "string",
                            "description": "Stable id unique inside this contract condition set."
                          },
                          "source": {
                            "type": "string",
                            "enum": [
                              "progress.solver_actions",
                              "progress.iters_used",
                              "progress.time_used_sec",
                              "last.intent_status",
                              "last.dominant_blocker",
                              "last.improvement_flags.run_global_best_improved",
                              "aggregate.achieved",
                              "aggregate.partial",
                              "aggregate.not_achieved",
                              "aggregate.regressed",
                              "aggregate.solver_requested_review",
                              "working.is_feasible",
                              "working.missed_priority",
                              "working.unassigned_count",
                              "working.energy_total",
                              "working.total_distance",
                              "working.makespan",
                              "working.route_balance",
                              "best_feasible.exists",
                              "best_feasible.missed_priority",
                              "best_feasible.unassigned_count",
                              "best_feasible.energy_total",
                              "best_feasible.total_distance",
                              "best_feasible.makespan",
                              "best_feasible.route_balance"
                            ],
                            "description": "Executable source path read by ContractMonitor."
                          },
                          "op": {
                            "type": "string",
                            "enum": [
                              "<",
                              "<=",
                              "==",
                              "!=",
                              ">=",
                              ">"
                            ]
                          },
                          "value": {
                            "type": [
                              "number",
                              "string",
                              "boolean"
                            ]
                          },
                          "window": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20
                          }
                        },
                        "required": [
                          "condition_id",
                          "source",
                          "op",
                          "value",
                          "window"
                        ],
                        "additionalProperties": false
                      }
                    }
                  },
                  "required": [
                    "success",
                    "failure"
                  ],
                  "additionalProperties": false
                },
                "explanation": {
                  "type": "object",
                  "description": "Human-readable explanation ignored by validator/compiler/runtime.",
                  "additionalProperties": {
                    "type": "string"
                  }
                }
              },
              "required": [
                "contract_type",
                "objective_layers",
                "feasibility_control",
                "target_policy",
                "protected_metrics",
                "resource_policy",
                "exit_conditions"
              ],
              "additionalProperties": false
            }
          },
          "required": [
            "action",
            "contract_review",
            "next_contract"
          ],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": {
            "action": {
              "type": "string",
              "const": "stop_run"
            },
            "contract_review": {
              "type": "object",
              "description": "Human-readable review ignored by runtime.",
              "properties": {
                "outcome_summary": {
                  "type": "string",
                  "description": "What happened during the completed contract."
                },
                "main_lesson": {
                  "type": "string",
                  "description": "Most important lesson for the next stage."
                }
              },
              "required": [
                "outcome_summary",
                "main_lesson"
              ],
              "additionalProperties": false
            },
            "stop_explanation": {
              "type": "string",
              "description": "Why the supervisor decides the run should stop."
            }
          },
          "required": [
            "action",
            "contract_review",
            "stop_explanation"
          ],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": [
    "supervisor_decision"
  ],
  "additionalProperties": false
}
```

</details>

### #073 [RAW] SUPERVISOR_REVIEW_RAW_OUTPUT | C002

<details>
<summary>Open raw LLM output</summary>

```text
{"supervisor_decision": {"action": "stop_run", "contract_review": {"outcome_summary": "The search is complete.", "main_lesson": "The next decision should use condition_report and verified outcomes."}, "stop_explanation": "The search is complete."}}
```

</details>

### #074 [OK] SUPERVISOR_REVIEW_VALIDATED_PAYLOAD | C002

```json
{
  "supervisor_decision": {
    "action": "stop_run",
    "contract_review": {
      "outcome_summary": "The search is complete.",
      "main_lesson": "The next decision should use condition_report and verified outcomes."
    },
    "stop_explanation": "The search is complete."
  }
}
```

### #075 [FINAL] FINAL_RESULT

```json
{
  "summary": {
    "is_feasible": true,
    "objective_keys": {
      "contract": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      },
      "global": {
        "layers": [
          "missed_priority",
          "unassigned_count",
          "energy_total"
        ],
        "key": [
          15.0,
          14.0,
          62031.7252777921
        ]
      }
    },
    "quality_summary": {
      "missed_priority": 15.0,
      "unassigned_count": 14.0,
      "energy_total": 62031.7252777921,
      "total_distance": 56702.56307069573,
      "makespan": 21963.819830943008,
      "route_balance": 0.18311646218632116
    },
    "feasibility_summary": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_by_type": {
        "capability": 0.0,
        "time_window": 0.0,
        "energy": 0.0
      },
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      }
    }
  },
  "run_summary": {
    "stop_reason": "supervisor_stop",
    "objective_tiers": [
      {
        "name": "missed_priority",
        "metric": "missed_priority",
        "direction": "min"
      },
      {
        "name": "unassigned_count",
        "metric": "unassigned_count",
        "direction": "min"
      },
      {
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 4,
        "solver_calls": 4,
        "time_sec": 1.0,
        "iters": 3
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 0.0,
        "time_sec": 9.0,
        "iters": 47.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 9.699881
  }
}
```


---

## Final Solution

```json
{
  "routes": {
    "0": [
      84,
      68,
      35,
      36,
      55,
      56,
      21,
      90,
      92,
      93,
      94,
      46,
      98,
      66,
      67,
      81
    ],
    "1": [
      51,
      85,
      54,
      37,
      38,
      57,
      22,
      43,
      10,
      45,
      25,
      47,
      27,
      28,
      29,
      50,
      32
    ],
    "2": [
      52,
      53,
      2,
      5,
      40,
      89,
      24,
      13,
      64,
      26,
      48,
      31
    ],
    "3": [
      34,
      86,
      39,
      41,
      23,
      62,
      63,
      95,
      65,
      49
    ],
    "4": [
      17,
      69,
      70,
      3,
      4,
      73,
      74,
      76,
      77,
      78,
      79,
      80,
      82,
      83
    ],
    "5": [
      0,
      18,
      19,
      71,
      87,
      88,
      42,
      91,
      75,
      44,
      11,
      12,
      14,
      15,
      16,
      30,
      33
    ]
  },
  "unassigned": [
    1,
    6,
    7,
    8,
    9,
    20,
    58,
    59,
    60,
    61,
    72,
    96,
    97,
    99
  ],
  "schedule": {
    "0:84": [
      651.2569337979742,
      678.2489422970048
    ],
    "0:68": [
      753.4505211583295,
      942.5314887349475
    ],
    "0:35": [
      1778.2741728878516,
      2022.1487223699073
    ],
    "0:36": [
      2067.2383198972784,
      2338.1457731368605
    ],
    "0:55": [
      3094.6956885768295,
      3324.235156561147
    ],
    "0:56": [
      4220.374543579754,
      4551.597664750944
    ],
    "0:21": [
      5594.501348771404,
      5948.720833841435
    ],
    "0:90": [
      6871.543217199576,
      7067.226949745339
    ],
    "0:92": [
      8545.218855079145,
      8791.303388023422
    ],
    "0:93": [
      9048.034752443798,
      9214.560991149068
    ],
    "0:94": [
      9808.30204415559,
      9962.204644124591
    ],
    "0:46": [
      10862.84819991497,
      11107.980994755118
    ],
    "0:98": [
      11861.604607950774,
      12131.20275759871
    ],
    "0:66": [
      12590.802830392158,
      12929.70359803514
    ],
    "0:67": [
      13455.15147855146,
      13747.540341857926
    ],
    "0:81": [
      14931.920010866143,
      15151.896067681486
    ],
    "1:51": [
      355.6734210998373,
      574.5830050364287
    ],
    "1:85": [
      1699.970400733211,
      1877.2616448359518
    ],
    "1:54": [
      2589.799384637674,
      2828.6240246037473
    ],
    "1:37": [
      3307.9385293024066,
      3336.0110353504824
    ],
    "1:38": [
      3800.036753344065,
      4110.074475765327
    ],
    "1:57": [
      5043.915666935461,
      5380.510299479272
    ],
    "1:22": [
      6730.92378262174,
      6930.977846058505
    ],
    "1:43": [
      8260.18699953338,
      8455.561495194986
    ],
    "1:10": [
      9358.357604689314,
      9367.887869771841
    ],
    "1:45": [
      10142.40539181454,
      10270.335043171053
    ],
    "1:25": [
      10742.486199387695,
      10790.1116952907
    ],
    "1:47": [
      11973.457112774742,
      12212.811025722089
    ],
    "1:27": [
      13160.807994021114,
      13450.008173760609
    ],
    "1:28": [
      13704.561374893663,
      14013.93775887259
    ],
    "1:29": [
      14348.923338079558,
      14375.775968248847
    ],
    "1:50": [
      14866.779084421754,
      14940.15020870754
    ],
    "1:32": [
      18978.5474093071,
      19244.406903576626
    ],
    "2:52": [
      1139.9613114145436,
      1474.5029177042932
    ],
    "2:53": [
      1753.8981196610864,
      1842.8381978933796
    ],
    "2:2": [
      2479.001084975513,
      2690.282869475541
    ],
    "2:5": [
      4413.621920453816,
      4659.6742325653295
    ],
    "2:40": [
      5605.80004307104,
      5820.971973083092
    ],
    "2:89": [
      6259.258966933841,
      6566.397165424431
    ],
    "2:24": [
      9166.440909730358,
      9326.618022976543
    ],
    "2:13": [
      10658.139608068717,
      10759.858769859482
    ],
    "2:64": [
      11139.57380081059,
      11395.044418695139
    ],
    "2:26": [
      11898.486068961178,
      12249.119723065327
    ],
    "2:48": [
      13166.813568432706,
      13289.638764643152
    ],
    "2:31": [
      17596.18438878143,
      17736.08435391884
    ],
    "3:34": [
      746.9732363799544,
      945.1347586825343
    ],
    "3:86": [
      3501.3889561166334,
      3640.492520033431
    ],
    "3:39": [
      5359.425290840632,
      5560.976565104588
    ],
    "3:41": [
      6125.9702150498,
      6324.108373368476
    ],
    "3:23": [
      7534.233564955634,
      7861.354503501883
    ],
    "3:62": [
      9232.416555711921,
      9344.187586614802
    ],
    "3:63": [
      9914.823756087575,
      9994.289457164115
    ],
    "3:95": [
      10718.7434947172,
      10826.436104607412
    ],
    "3:65": [
      12007.99584736222,
      12185.730420001732
    ],
    "3:49": [
      14150.101680364638,
      14159.040897128541
    ],
    "4:17": [
      588.6270558304483,
      633.5464636235188
    ],
    "4:69": [
      2189.940816696422,
      2410.188683280179
    ],
    "4:70": [
      2658.1309381023575,
      2716.169614431001
    ],
    "4:3": [
      3226.4610879202455,
      3499.0311003173238
    ],
    "4:4": [
      3934.80882345902,
      4073.4285280283602
    ],
    "4:73": [
      5696.927719160241,
      5866.721592519108
    ],
    "4:74": [
      7085.683860351792,
      7242.350122121348
    ],
    "4:76": [
      9438.495244340866,
      9598.813371123299
    ],
    "4:77": [
      10247.016341119572,
      10286.463099800127
    ],
    "4:78": [
      11601.426624481057,
      11766.254299760476
    ],
    "4:79": [
      13191.559203027162,
      13429.001621388123
    ],
    "4:80": [
      13689.208039973113,
      13963.284651882957
    ],
    "4:82": [
      15370.447658703197,
      15699.27655520053
    ],
    "4:83": [
      16220.518373689501,
      16521.349546205958
    ],
    "5:0": [
      630.9651244710793,
      862.0850384988446
    ],
    "5:18": [
      1469.6495712682229,
      1674.000810004407
    ],
    "5:19": [
      2083.4267179682624,
      2418.0152807188365
    ],
    "5:71": [
      3211.961132334576,
      3239.4434864695218
    ],
    "5:87": [
      4587.353724330949,
      4727.569917722721
    ],
    "5:88": [
      5397.783901024961,
      5563.364151686739
    ],
    "5:42": [
      6667.515974371253,
      6947.923565420815
    ],
    "5:91": [
      7713.116056537147,
      7774.67465018621
    ],
    "5:75": [
      8342.82468791952,
      8685.206175374193
    ],
    "5:44": [
      9185.628516129489,
      9336.475691938418
    ],
    "5:11": [
      9939.71129904656,
      10041.406159545868
    ],
    "5:12": [
      10245.719122250066,
      10414.913953407196
    ],
    "5:14": [
      11138.16952974723,
      11409.945980186274
    ],
    "5:15": [
      11556.694971505876,
      11890.388441840118
    ],
    "5:16": [
      11968.728227735255,
      11992.551038323847
    ],
    "5:30": [
      16101.550701007767,
      16448.137986050406
    ],
    "5:33": [
      20597.466424408758,
      20838.21408407861
    ]
  },
  "eval": {
    "quality_metrics": {
      "missed_priority": 15.0,
      "unassigned_count": 14.0,
      "energy_total": 62031.7252777921,
      "total_distance": 56702.56307069573,
      "makespan": 21963.819830943008,
      "route_balance": 0.18311646218632116
    },
    "constraint_report": {
      "is_feasible": true,
      "violation_total": 0.0,
      "violation_capability": 0.0,
      "violation_time_window": 0.0,
      "violation_energy": 0.0,
      "recoverable_violation_total": 0.0,
      "unrecoverable_violation_total": 0.0,
      "violation_by_type": {},
      "violation_by_task": {},
      "violation_by_route": {},
      "violation_ratio_by_type": {
        "time_window": 0.0,
        "energy": 0.0
      },
      "violation_details_by_type": {
        "time_window": [
          {
            "task_id": 84,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 68,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 35,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 36,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 55,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 56,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 21,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 90,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 92,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 93,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 94,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 46,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 98,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 66,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 67,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 81,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 51,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 85,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 54,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 37,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 38,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 57,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 22,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 43,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 10,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 45,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 25,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 47,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 27,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 28,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 29,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 50,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 32,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 52,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 53,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 2,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 5,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 40,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 89,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 24,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 13,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 64,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 26,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 48,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 31,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 34,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 86,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 39,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 41,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 23,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 62,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 63,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 95,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 65,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 49,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 17,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 69,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 70,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 3,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 4,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 73,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 74,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 76,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 77,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 78,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 79,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 80,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 82,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 83,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 0,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 18,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 19,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 71,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 87,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 88,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 42,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 91,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 75,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 44,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 11,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 12,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 14,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 15,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 16,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 30,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 33,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          }
        ],
        "energy": [
          {
            "agent_id": 0,
            "energy_over": 0.0,
            "energy_ref": 13747.048592962716,
            "ratio": 0.0
          },
          {
            "agent_id": 1,
            "energy_over": 0.0,
            "energy_ref": 21093.130686946715,
            "ratio": 0.0
          },
          {
            "agent_id": 2,
            "energy_over": 0.0,
            "energy_ref": 12573.672803795207,
            "ratio": 0.0
          },
          {
            "agent_id": 3,
            "energy_over": 0.0,
            "energy_ref": 13996.04758308917,
            "ratio": 0.0
          },
          {
            "agent_id": 4,
            "energy_over": 0.0,
            "energy_ref": 14092.363794538154,
            "ratio": 0.0
          },
          {
            "agent_id": 5,
            "energy_over": 0.0,
            "energy_ref": 13938.159847439214,
            "ratio": 0.0
          }
        ]
      }
    }
  },
  "solver_diagnostics": {
    "algorithm": "weighted_alns",
    "policy": {
      "destroy_policy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 2,
          "related_cluster_removal": 8,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 8,
          "route_balance_pressure": 0,
          "mobility_opportunity": 0,
          "scarcity_protection": 0
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 8,
          "regret_insertion": 7,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 8,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 8,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "threshold",
        "intensity_score": 4,
        "accept_level": 0.08,
        "exploration_score": 2.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 1,
    "actual_iters_used": 1,
    "actual_time_used_sec": 0.7102508999996644,
    "best_update_count": 1,
    "best_update_iters": [
      1
    ],
    "best_update_objective_keys": [
      {
        "contract": {
          "layers": [
            "missed_priority",
            "unassigned_count",
            "energy_total"
          ],
          "key": [
            15.0,
            14.0,
            62031.7252777921
          ]
        },
        "global": {
          "layers": [
            "missed_priority",
            "unassigned_count",
            "energy_total"
          ],
          "key": [
            15.0,
            14.0,
            62031.7252777921
          ]
        }
      }
    ],
    "first_best_iter": 1,
    "last_best_iter": 1,
    "plateau_iters_after_last_update": 0,
    "initial_solution_feasible": true,
    "returned_solution_source": "action_best_feasible",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": -1,
      "accepted": true,
      "accept_mode": "threshold",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "worst_task_removal",
      "shape": "task_set",
      "task_ids": [
        0,
        2,
        3,
        4,
        5,
        6,
        7,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        20
      ],
      "affected_routes": [
        0,
        1,
        2,
        4,
        5
      ],
      "features": {
        "cost_pressure": 1.0,
        "priority_loss": 1.0,
        "scarcity_pressure": 0.7646323319915161,
        "coupling_pressure": 1.0,
        "mobility_opportunity": 0.011509176200872853,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 8.0,
      "metadata": {
        "target_k": 17
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 8,
        "regret_insertion": 7,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 8,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 8,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "scarcity_first_insertion": 4,
        "regret_insertion": 9,
        "greedy_insertion": 3,
        "bottleneck_insertion": 2,
        "diversified_insertion": 1
      },
      "unassigned_before": 33,
      "unassigned_after": 14,
      "inserted_count": 19,
      "failed_count": 14,
      "tasks_analyzed": 470,
      "positions_generated": 381,
      "positions_strict_checked": 381,
      "strict_feasible_positions": 381,
      "failure_breakdown": {
        "no_candidate": 194,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 1,
          "priority": 1.0,
          "capable_agents": 2,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 6,
          "priority": 1.0,
          "capable_agents": 4,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 7,
          "priority": 2.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 8,
          "priority": 1.0,
          "capable_agents": 3,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 9,
          "priority": 1.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 528.2709,
      "operator": "regret_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "action_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "global_best_objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy.",
        "protected_metric_passed": true,
        "protected_metric_violations": [],
        "rejection_reason": null
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 0.0,
      "worst_task_removal": 1.0,
      "related_cluster_removal": 0.0,
      "critical_block_removal": 0.0,
      "route_rebalance_removal": 0.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 33.0,
      "tasks_reinserted": 19.0,
      "tasks_left_unassigned": 14.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 194.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 1.0,
          "worst_task_removal": 1.0,
          "related_cluster_removal": 1.0,
          "critical_block_removal": 1.0,
          "route_rebalance_removal": 1.0
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 2.0,
          "related_cluster_removal": 8.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.189207115002721,
          "worst_task_removal": 1.189207115002721,
          "related_cluster_removal": 1.681792830507429,
          "critical_block_removal": 1.189207115002721,
          "route_rebalance_removal": 1.189207115002721
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 8.0,
          "regret_insertion": 7.0,
          "bottleneck_insertion": 2.0,
          "diversified_insertion": 2.0
        }
      }
    },
    "feasibility_policy": {
      "mode": "strict"
    },
    "violation_ratios": {
      "energy": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      },
      "time_window": {
        "total_ratio": 0.0,
        "max_individual_ratio": 0.0,
        "limit_ratio": null,
        "delta_ratio": null
      }
    },
    "feasibility_rejection_reasons": {},
    "protected_metric_rejections": 0,
    "protected_metric_rejection_reasons": {},
    "protected_metric_bounds": [
      {
        "metric": "unassigned_count",
        "baseline": 16.0,
        "max_worsen": 0.0
      }
    ],
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "execution_trace": {
      "trace_id": "X3",
      "kind": "alns",
      "iters": 1,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 0,
          "worst_task_removal": 1,
          "related_cluster_removal": 0,
          "critical_block_removal": 0,
          "route_rebalance_removal": 0
        },
        "removed_task_count_avg": 17.0
      },
      "repair": {
        "candidate_tasks_total": 33,
        "tasks_reinserted": 19,
        "tasks_left_unassigned": 14,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 194
        }
      },
      "trial_flow": {
        "candidate_trials": 1,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "protected_metric_rejected": 0,
        "admissible_trials": 1,
        "acceptance_rejected": 0,
        "accepted_trials": 1,
        "global_best_improved_trials": 1
      },
      "rejection_reasons": {}
    },
    "solution_flow": {
      "initial_working": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              18.0,
              16.0,
              61731.554843921316
            ]
          }
        }
      },
      "final_current": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "is_feasible": true
      },
      "action_best_feasible": {
        "objective_keys": {
          "contract": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          },
          "global": {
            "layers": [
              "missed_priority",
              "unassigned_count",
              "energy_total"
            ],
            "key": [
              15.0,
              14.0,
              62031.7252777921
            ]
          }
        },
        "is_feasible": true
      },
      "returned_solution_source": "action_best_feasible",
      "protected_metric_result": {
        "passed": true,
        "violations": []
      }
    }
  },
  "run_summary": {
    "stop_reason": "supervisor_stop",
    "objective_tiers": [
      {
        "name": "missed_priority",
        "metric": "missed_priority",
        "direction": "min"
      },
      {
        "name": "unassigned_count",
        "metric": "unassigned_count",
        "direction": "min"
      },
      {
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 4,
        "solver_calls": 4,
        "time_sec": 1.0,
        "iters": 3
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 0.0,
        "time_sec": 9.0,
        "iters": 47.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 9.699881
  }
}
```


## Final Summary

```json
{
  "instance": "T100",
  "llm_mode": "dummy",
  "hard_feasible": true,
  "violation_total": 0.0,
  "missed_priority": 15.0,
  "unassigned_count": 14,
  "energy_total": 62031.7252777921,
  "total_distance": 56702.56307069573,
  "makespan": 21963.819830943008,
  "quality_summary": {
    "missed_priority": 15.0,
    "unassigned_count": 14.0,
    "energy_total": 62031.7252777921,
    "total_distance": 56702.56307069573,
    "makespan": 21963.819830943008,
    "route_balance": 0.18311646218632116
  },
  "feasibility_summary": {
    "is_feasible": true,
    "violation_total": 0.0,
    "violation_by_type": {
      "capability": 0.0,
      "time_window": 0.0,
      "energy": 0.0
    },
    "recoverable_violation_total": 0.0,
    "unrecoverable_violation_total": 0.0,
    "violation_ratio_by_type": {
      "time_window": 0.0,
      "energy": 0.0
    }
  },
  "run_summary": {
    "stop_reason": "supervisor_stop",
    "objective_tiers": [
      {
        "name": "missed_priority",
        "metric": "missed_priority",
        "direction": "min"
      },
      {
        "name": "unassigned_count",
        "metric": "unassigned_count",
        "direction": "min"
      },
      {
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 4,
        "solver_calls": 4,
        "time_sec": 1.0,
        "iters": 3
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 0.0,
        "time_sec": 9.0,
        "iters": 47.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 9.699881
  },
  "elapsed_sec": 9.7014
}
```

