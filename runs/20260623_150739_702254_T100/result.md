# LLM-ALNS Execution Report

> Status: running

## Run Config

```json
{
  "instance": "T100",
  "instance_path": "D:\\SJTU\\Smart\\LLM_Task_Assign\\llm_task_assign_code\\sar_alloc\\data\\instances\\demo\\seed42_T100_A6.json",
  "time_limit_sec": 300.0,
  "max_iters": 2000,
  "max_step_calls": 10,
  "max_solver_calls": 20,
  "seed": 0,
  "dummy_llm": false,
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
  "llm_mode": "api",
  "run_config": {
    "instance": "T100",
    "instance_path": "D:\\SJTU\\Smart\\LLM_Task_Assign\\llm_task_assign_code\\sar_alloc\\data\\instances\\demo\\seed42_T100_A6.json",
    "time_limit_sec": 300.0,
    "max_iters": 2000,
    "max_step_calls": 10,
    "max_solver_calls": 20,
    "seed": 0,
    "dummy_llm": false,
    "allow_llm_fallback": false
  },
  "global_budget": {
    "step_calls": 10.0,
    "solver_calls": 20.0,
    "time_sec": 300.0,
    "iters": 2000.0
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
    "max_solver_actions": 10,
    "max_time_sec": 300.0,
    "max_iters": 2000
  },
  "problem_profile": {
    "num_tasks": 100,
    "num_agents": 6,
    "priority_mass": 198.0,
    "high_priority_task_count": 36,
    "zero_capable_task_count": 0,
    "scarce_task_count": 0,
    "scarce_priority_mass": 0,
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
    "max_solver_actions_allowed": 10,
    "max_time_sec_allowed": 300.0,
    "max_iters_allowed": 2000
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
      "max_solver_actions": 10,
      "max_time_sec": 300.0,
      "max_iters": 2000
    },
    "problem_profile": {
      "num_tasks": 100,
      "num_agents": 6,
      "priority_mass": 198.0,
      "high_priority_task_count": 36,
      "zero_capable_task_count": 0,
      "scarce_task_count": 0,
      "scarce_priority_mass": 0,
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
      "max_solver_actions_allowed": 10,
      "max_time_sec_allowed": 300.0,
      "max_iters_allowed": 2000
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
                      "scarce_unassigned",
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
                "description": "A metric that may not worsen beyond the provided amount.",
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
                  "maximum": 10
                },
                "max_actions": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 10
                },
                "max_iters": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 2000
                },
                "max_time_sec": {
                  "type": "number",
                  "exclusiveMinimum": 0,
                  "maximum": 300.0
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
                        "description": "Supported source path read from OutcomeVerification/progress."
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
                        "description": "Supported source path read from OutcomeVerification/progress."
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
{
  "supervisor_decision": {
    "action": "start_run",
    "global_objective": {
      "objective_layers": [
        "missed_priority",
        "energy_total"
      ],
      "explanation": {
        "rationale": "First minimize missed priority to maximize valuable task coverage, then minimize total energy to reduce resource use."
      }
    },
    "next_contract": {
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "energy_total"
      ],
      "feasibility_control": {
        "mode": "strict",
        "relaxation_ratios": []
      },
      "target_policy": {
        "preferred_target_kinds": [
          "unassigned_priority"
        ]
      },
      "protected_metrics": [],
      "resource_policy": {
        "min_actions": 1,
        "max_actions": 10,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "s1",
            "source": "missed_priority",
            "op": "==",
            "value": 0,
            "window": 1
          }
        ],
        "failure": [
          {
            "condition_id": "f1",
            "source": "total_actions",
            "op": ">=",
            "value": 10,
            "window": 1
          }
        ]
      },
      "explanation": {
        "purpose": "Initial construction contract to build a feasible solution prioritizing coverage of high-value tasks, then optimizing energy."
      }
    }
  }
}
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
        "energy_total"
      ],
      "explanation": {
        "rationale": "First minimize missed priority to maximize valuable task coverage, then minimize total energy to reduce resource use."
      }
    },
    "next_contract": {
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "energy_total"
      ],
      "feasibility_control": {
        "mode": "strict",
        "relaxation_ratios": []
      },
      "target_policy": {
        "preferred_target_kinds": [
          "unassigned_priority"
        ]
      },
      "protected_metrics": [],
      "resource_policy": {
        "min_actions": 1,
        "max_actions": 10,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "s1",
            "source": "missed_priority",
            "op": "==",
            "value": 0,
            "window": 1
          }
        ],
        "failure": [
          {
            "condition_id": "f1",
            "source": "total_actions",
            "op": ">=",
            "value": 10,
            "window": 1
          }
        ]
      },
      "explanation": {
        "purpose": "Initial construction contract to build a feasible solution prioritizing coverage of high-value tasks, then optimizing energy."
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
      "unassigned_priority"
    ]
  },
  "protected_metrics": [],
  "resource_policy": {
    "min_actions": 1,
    "max_actions": 10,
    "max_iters": 2000,
    "max_time_sec": 300.0
  },
  "exit_conditions": {
    "success": [
      {
        "condition_id": "s1",
        "source": "missed_priority",
        "op": "==",
        "value": 0,
        "window": 1
      }
    ],
    "failure": [
      {
        "condition_id": "f1",
        "source": "total_actions",
        "op": ">=",
        "value": 10,
        "window": 1
      }
    ]
  },
  "explanation": {
    "purpose": "Initial construction contract to build a feasible solution prioritizing coverage of high-value tasks, then optimizing energy."
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
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 10,
      "time_sec": 300.0,
      "iters": 2000,
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "task_count": 3,
        "priority_mass": 198.0,
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
          ]
        }
      }
    ],
    "zero_capable_task_count": 0
  },
  "insertion_position_landscape": {
    "candidate_position_count": {
      "p50": 4.14,
      "low_count": 0,
      "zero_count": 0
    },
    "feasible_position_count": {
      "p50": 4.14,
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "task_count": 3,
      "priority_mass": 198.0,
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 10,
        "time_sec": 300.0,
        "iters": 2000,
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
          "target_id": "T_scarce_unassigned",
          "kind": "scarce_unassigned",
          "task_count": 3,
          "priority_mass": 198.0,
          "recommended_controls": {
            "insertion_control.task_signal_scores": [
              "scarcity_pressure",
              "priority_loss"
            ],
            "insertion_control.position_signal_scores": [
              "future_slack"
            ],
            "destroy_control.signal_scores": [
              "scarcity_protection",
              "mobility_opportunity"
            ]
          }
        }
      ],
      "zero_capable_task_count": 0
    },
    "insertion_position_landscape": {
      "candidate_position_count": {
        "p50": 4.14,
        "low_count": 0,
        "zero_count": 0
      },
      "feasible_position_count": {
        "p50": 4.14,
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "task_count": 3,
        "priority_mass": 198.0,
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
{
  "solver_decision": {
    "action": "construct_initial",
    "target_id": "T_scarce_unassigned",
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "scarcity_pressure",
          "score": 10
        },
        {
          "name": "priority_loss",
          "score": 10
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 10
        }
      ]
    },
    "explanation": {
      "rationale": "Target scarce unassigned tasks first because they have high priority per task (198/3=66 each), maximizing valuable coverage with minimal resource use. Use scarcity-first insertion with strong scarcity and priority signals."
    }
  }
}
```

</details>

### #014 [OK] SOLVER_VALIDATED_PAYLOAD | C001 / SOLVER 000

```json
{
  "solver_decision": {
    "action": "construct_initial",
    "target_id": "T_scarce_unassigned",
    "insertion_control": {
      "operator_scores": [
        {
          "name": "scarcity_first_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "scarcity_pressure",
          "score": 10
        },
        {
          "name": "priority_loss",
          "score": 10
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 10
        }
      ]
    },
    "explanation": {
      "rationale": "Target scarce unassigned tasks first because they have high priority per task (198/3=66 each), maximizing valuable coverage with minimal resource use. Use scarcity-first insertion with strong scarcity and priority signals."
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
  "target_id": "T_scarce_unassigned",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 10,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 10,
        "regret_insertion": 2,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 10,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 0,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.regret_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.insert_cost=0",
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
    "scarcity_first_insertion": 10,
    "regret_insertion": 2,
    "bottleneck_insertion": 2,
    "diversified_insertion": 2
  },
  "task_signal_weights": {
    "priority_loss": 10,
    "scarcity_pressure": 10,
    "regret_pressure": 0,
    "bottleneck_pressure": 0,
    "mobility_opportunity": 0
  },
  "position_signal_weights": {
    "insert_cost": 0,
    "future_slack": 10,
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
    "lex_key": [
      18.0,
      71141.23098004144
    ],
    "quality_summary": {
      "missed_priority": 18.0,
      "unassigned_count": 16.0,
      "energy_total": 71141.23098004144,
      "total_distance": 66705.05148918818,
      "makespan": 22007.377762869848,
      "route_balance": 0.1649572197684645
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
    "trace_id": "",
    "kind": "initial_insertion",
    "candidate_task_count": 100,
    "attempted_task_count": 4930,
    "inserted_task_count": 84,
    "uninserted_task_count": 16,
    "zero_candidate_task_count": 665,
    "hard_filter_rejected_count": 3,
    "top_failed_tasks": [
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
        "task_id": 26,
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
        "task_id": 39,
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
        "task_id": 44,
        "priority": 2.0,
        "capable_agents": 5,
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
      "regret_insertion": 8,
      "scarcity_first_insertion": 45,
      "diversified_insertion": 12,
      "greedy_insertion": 6
    }
  }
}
```

### #018 [SOLVER] EXECUTION_TRACE | C001 / SOLVER 000

```json
{
  "trace_id": "",
  "kind": "initial_insertion",
  "candidate_task_count": 100,
  "attempted_task_count": 4930,
  "inserted_task_count": 84,
  "uninserted_task_count": 16,
  "zero_candidate_task_count": 665,
  "hard_filter_rejected_count": 3,
  "top_failed_tasks": [
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
      "task_id": 26,
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
      "task_id": 39,
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
      "task_id": 44,
      "priority": 2.0,
      "capable_agents": 5,
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
    "regret_insertion": 8,
    "scarcity_first_insertion": 45,
    "diversified_insertion": 12,
    "greedy_insertion": 6
  }
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
  "target_id": "T_scarce_unassigned",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 18.0,
      "energy_total": 71141.23098004144
    },
    "best_feasible": {
      "missed_priority": 18.0,
      "energy_total": 71141.23098004144
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
    "quality_problem": false
  },
  "event_tags": [
    "initial_feasible"
  ],
  "trace": {
    "trace_id": "X1",
    "kind": "initial_insertion",
    "candidate_task_count": 100,
    "attempted_task_count": 4930,
    "inserted_task_count": 84,
    "uninserted_task_count": 16,
    "zero_candidate_task_count": 665,
    "hard_filter_rejected_count": 3,
    "top_failed_tasks": [
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
        "task_id": 26,
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
        "task_id": 39,
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
        "task_id": 44,
        "priority": 2.0,
        "capable_agents": 5,
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
      "regret_insertion": 8,
      "scarcity_first_insertion": 45,
      "diversified_insertion": 12,
      "greedy_insertion": 6
    }
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
  "target_id": "T_scarce_unassigned",
  "target_kind": "scarce_unassigned",
  "control_fingerprint": {
    "destroy_top": [],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "diversity_gain"
    ],
    "acceptance": ""
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": false,
    "metric_delta": {
      "missed_priority": 18.0,
      "energy_total": 71141.23098004144
    }
  },
  "manifest": {
    "manifest_id": "R1",
    "source_decision_id": "D1",
    "contract_id": "C001",
    "action": "construct_initial",
    "target_id": "T_scarce_unassigned",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 10,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 10,
          "regret_insertion": 2,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 10,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 0,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.regret_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.insert_cost=0",
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
    "zero_candidate_task_count": 665,
    "hard_filter_rejected_count": 3,
    "top_failed_tasks": [
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
        "task_id": 26,
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
        "task_id": 39,
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
        "task_id": 44,
        "priority": 2.0,
        "capable_agents": 5,
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
      "regret_insertion": 8,
      "scarcity_first_insertion": 45,
      "diversified_insertion": 12,
      "greedy_insertion": 6
    }
  },
  "verification": {
    "verification_id": "V1",
    "contract_id": "C001",
    "decision_id": "D1",
    "manifest_id": "R1",
    "trace_id": "X1",
    "action": "construct_initial",
    "target_id": "T_scarce_unassigned",
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 18.0,
        "energy_total": 71141.23098004144
      },
      "best_feasible": {
        "missed_priority": 18.0,
        "energy_total": 71141.23098004144
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
      "quality_problem": false
    },
    "event_tags": [
      "initial_feasible"
    ],
    "trace": {
      "trace_id": "X1",
      "kind": "initial_insertion",
      "candidate_task_count": 100,
      "attempted_task_count": 4930,
      "inserted_task_count": 84,
      "uninserted_task_count": 16,
      "zero_candidate_task_count": 665,
      "hard_filter_rejected_count": 3,
      "top_failed_tasks": [
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
          "task_id": 26,
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
          "task_id": 39,
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
          "task_id": 44,
          "priority": 2.0,
          "capable_agents": 5,
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
        "regret_insertion": 8,
        "scarcity_first_insertion": 45,
        "diversified_insertion": 12,
        "greedy_insertion": 6
      }
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
  "metric_delta_total": {
    "missed_priority": 18.0,
    "energy_total": 71141.23098004144
  },
  "condition_report": [
    {
      "condition_id": "s1",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "f1",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 10,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #022 [CONTRACT] CONTRACT_COMPLETION_CHECK | C001 / SOLVER 000

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s1",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "f1",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 10,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #023 [OBS] SOLVER_OBSERVATION | C001 / SOLVER 001

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O2",
  "frame_type": "solver_initial_construction",
  "role": "solver",
  "step_index": 1,
  "contract_view": {
    "contract_id": "C001",
    "contract_type": "initial_construction",
    "objective_layers": [
      "missed_priority",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 9,
      "time_sec": 300.0,
      "iters": 2000,
      "min_actions_remaining": 0
    }
  },
  "task_buildability_view": {
    "target_buckets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 16,
        "priority_mass": 18.0,
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "task_count": 0,
        "priority_mass": 18.0,
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
          ]
        }
      }
    ],
    "zero_capable_task_count": 0
  },
  "insertion_position_landscape": {
    "candidate_position_count": {
      "p50": 0.0,
      "low_count": 0,
      "zero_count": 16
    },
    "feasible_position_count": {
      "p50": 0.0,
      "low_count": 0,
      "zero_count": 16
    },
    "top_failed_tasks": []
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "task_count": 16,
      "priority_mass": 18.0,
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "task_count": 0,
      "priority_mass": 18.0,
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
    "exists": true,
    "verification_id": "V1",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": 18.0,
      "energy_total": 71141.23098004144
    },
    "debt_delta": {},
    "trace_counts": {
      "candidate_trials": 0,
      "feasibility_rejected": 0,
      "accepted": 0,
      "best_improved": 0
    }
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
  "usable_memory": [
    {
      "record_id": "M1",
      "target_kind": "scarce_unassigned",
      "control_summary": "priority_loss + future_slack",
      "outcome": "missed_priority +18, energy_total +7.11e+04, accepted 0/0, blocker none"
    }
  ]
}
```

</details>

### #024 [PROMPT] SOLVER_PROMPT | C001 / SOLVER 001

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
    "frame_type": "solver_initial_construction",
    "role": "solver",
    "step_index": 1,
    "contract_view": {
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 9,
        "time_sec": 300.0,
        "iters": 2000,
        "min_actions_remaining": 0
      }
    },
    "task_buildability_view": {
      "target_buckets": [
        {
          "target_id": "T_unassigned_priority",
          "kind": "unassigned_priority",
          "task_count": 16,
          "priority_mass": 18.0,
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
          "target_id": "T_scarce_unassigned",
          "kind": "scarce_unassigned",
          "task_count": 0,
          "priority_mass": 18.0,
          "recommended_controls": {
            "insertion_control.task_signal_scores": [
              "scarcity_pressure",
              "priority_loss"
            ],
            "insertion_control.position_signal_scores": [
              "future_slack"
            ],
            "destroy_control.signal_scores": [
              "scarcity_protection",
              "mobility_opportunity"
            ]
          }
        }
      ],
      "zero_capable_task_count": 0
    },
    "insertion_position_landscape": {
      "candidate_position_count": {
        "p50": 0.0,
        "low_count": 0,
        "zero_count": 16
      },
      "feasible_position_count": {
        "p50": 0.0,
        "low_count": 0,
        "zero_count": 16
      },
      "top_failed_tasks": []
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "task_count": 16,
        "priority_mass": 18.0,
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "task_count": 0,
        "priority_mass": 18.0,
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
      "exists": true,
      "verification_id": "V1",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 18.0,
        "energy_total": 71141.23098004144
      },
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "best_improved": 0
      }
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
    "usable_memory": [
      {
        "record_id": "M1",
        "target_kind": "scarce_unassigned",
        "control_summary": "priority_loss + future_slack",
        "outcome": "missed_priority +18, energy_total +7.11e+04, accepted 0/0, blocker none"
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

### #025 [RAW] SOLVER_RAW_OUTPUT | C001 / SOLVER 001

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "request_supervisor_review",
    "target_id": "contract_review",
    "explanation": {
      "reason": "No feasible insertion positions exist for 16 tasks, previous attempts yielded 0 accepted tasks. Escalating to supervisor to adjust feasibility or relax constraints."
    }
  }
}
```

</details>

### #026 [OK] SOLVER_VALIDATED_PAYLOAD | C001 / SOLVER 001

```json
{
  "solver_decision": {
    "action": "request_supervisor_review",
    "target_id": "contract_review",
    "explanation": {
      "reason": "No feasible insertion positions exist for 16 tasks, previous attempts yielded 0 accepted tasks. Escalating to supervisor to adjust feasibility or relax constraints."
    }
  }
}
```

### #027 [COMP] RUNTIME_CONTROL_MANIFEST | C001 / SOLVER 001

```json
{
  "manifest_id": "R2",
  "source_decision_id": "D2",
  "contract_id": "C001",
  "action": "request_supervisor_review",
  "target_id": "contract_review",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 10,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "review_request": {
      "requested": 1
    }
  },
  "defaults_applied": [],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #028 [SOLVER] EXECUTION_TRACE | C001 / SOLVER 001

```json
{
  "trace_id": "",
  "kind": "review_request"
}
```

### #029 [AUDIT] OUTCOME_VERIFICATION | C001 / SOLVER 001

```json
{
  "verification_id": "V2",
  "contract_id": "C001",
  "decision_id": "D2",
  "manifest_id": "R2",
  "trace_id": "X2",
  "action": "request_supervisor_review",
  "target_id": "contract_review",
  "intent_status": "not_applicable",
  "metric_delta": {
    "working": {},
    "best_feasible": {}
  },
  "debt_delta": {},
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "solver_requested_review",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false
  },
  "event_tags": [],
  "trace": {
    "trace_id": "X2",
    "kind": "review_request"
  }
}
```

### #030 [MEM] MEMORY_UPDATE | C001 / SOLVER 001

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M2",
  "kind": "verified_action",
  "contract_id": "C001",
  "observation_id": "O2",
  "decision_id": "D2",
  "manifest_id": "R2",
  "trace_id": "X2",
  "verification_id": "V2",
  "target_id": "contract_review",
  "target_kind": "contract_review",
  "control_fingerprint": {
    "destroy_top": [],
    "insert_task_top": [],
    "insert_pos_top": [],
    "acceptance": ""
  },
  "outcome_fingerprint": {
    "intent_status": "not_applicable",
    "dominant_blocker": "solver_requested_review",
    "best_improved": false,
    "metric_delta": {}
  },
  "manifest": {
    "manifest_id": "R2",
    "source_decision_id": "D2",
    "contract_id": "C001",
    "action": "request_supervisor_review",
    "target_id": "contract_review",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 10,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "review_request": {
        "requested": 1
      }
    },
    "defaults_applied": [],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X2",
    "kind": "review_request"
  },
  "verification": {
    "verification_id": "V2",
    "contract_id": "C001",
    "decision_id": "D2",
    "manifest_id": "R2",
    "trace_id": "X2",
    "action": "request_supervisor_review",
    "target_id": "contract_review",
    "intent_status": "not_applicable",
    "metric_delta": {
      "working": {},
      "best_feasible": {}
    },
    "debt_delta": {},
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "solver_requested_review",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false
    },
    "event_tags": [],
    "trace": {
      "trace_id": "X2",
      "kind": "review_request"
    }
  }
}
```

</details>

### #031 [CONTRACT] CONTRACT_PROGRESS | C001 / SOLVER 001

```json
{
  "contract_id": "C001",
  "solver_actions": 2,
  "time_used_sec": 0.0,
  "iters_used": 0,
  "verification_ids": [
    "V1",
    "V2"
  ],
  "intent_status_counts": {
    "achieved": 1,
    "not_applicable": 1
  },
  "dominant_blocker_counts": {
    "none": 1,
    "solver_requested_review": 1
  },
  "metric_delta_total": {
    "missed_priority": 18.0,
    "energy_total": 71141.23098004144
  },
  "condition_report": [
    {
      "condition_id": "s1",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "f1",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 10,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #032 [CONTRACT] CONTRACT_COMPLETION_CHECK | C001 / SOLVER 001

```json
{
  "completion_status": "solver_requested_review",
  "completion_reason": "solver_requested_review",
  "condition_report": [
    {
      "condition_id": "s1",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "f1",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 10,
      "window": 1,
      "passed": false
    }
  ],
  "completed": true,
  "reason": "solver_requested_review",
  "result": "solver_requested_review"
}
```

### #033 [CONTRACT] CONTRACT_END | C001

```json
{
  "completion": {
    "completion_status": "solver_requested_review",
    "completion_reason": "solver_requested_review",
    "condition_report": [
      {
        "condition_id": "s1",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "f1",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 10,
        "window": 1,
        "passed": false
      }
    ],
    "completed": true,
    "reason": "solver_requested_review",
    "result": "solver_requested_review"
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
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "progress": {
      "contract_id": "C001",
      "solver_actions": 2,
      "time_used_sec": 0.0,
      "iters_used": 0,
      "verification_ids": [
        "V1",
        "V2"
      ],
      "intent_status_counts": {
        "achieved": 1,
        "not_applicable": 1
      },
      "dominant_blocker_counts": {
        "none": 1,
        "solver_requested_review": 1
      },
      "metric_delta_total": {
        "missed_priority": 18.0,
        "energy_total": 71141.23098004144
      },
      "condition_report": [
        {
          "condition_id": "s1",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "f1",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 10,
          "window": 1,
          "passed": false
        }
      ]
    },
    "completion": {
      "completion_status": "solver_requested_review",
      "completion_reason": "solver_requested_review",
      "condition_report": [
        {
          "condition_id": "s1",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "f1",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 10,
          "window": 1,
          "passed": false
        }
      ],
      "completed": true,
      "reason": "solver_requested_review",
      "result": "solver_requested_review"
    }
  }
}
```

### #034 [OBS] SUPERVISOR_REVIEW_OBSERVATION | C001

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O_review_2",
  "frame_type": "supervisor_review",
  "role": "supervisor",
  "budget_caps": {
    "max_solver_actions": 8,
    "max_time_sec": 300.0,
    "max_iters": 2000
  },
  "completed_contract": {
    "contract_id": "C001",
    "contract_type": "initial_construction",
    "objective_layers": [
      "missed_priority",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": []
  },
  "contract_completion": {
    "completion_status": "solver_requested_review",
    "completion_reason": "solver_requested_review",
    "condition_report": [
      {
        "condition_id": "s1",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "f1",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 10,
        "window": 1,
        "passed": false
      }
    ],
    "completed": true,
    "reason": "solver_requested_review",
    "result": "solver_requested_review"
  },
  "condition_report": [
    {
      "condition_id": "s1",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 1,
      "passed": false
    },
    {
      "condition_id": "f1",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 10,
      "window": 1,
      "passed": false
    }
  ],
  "stage_verification_summary": {
    "verification_ids": [
      "V1",
      "V2"
    ],
    "intent_status_counts": {
      "achieved": 1,
      "not_applicable": 1
    },
    "dominant_blocker_counts": {
      "none": 1,
      "solver_requested_review": 1
    },
    "last": {
      "exists": true,
      "verification_id": "V2",
      "intent_status": "not_applicable",
      "dominant_blocker": "solver_requested_review",
      "metric_delta": {},
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "best_improved": 0
      }
    }
  },
  "solution_position": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 71141.23098004144,
        "total_distance": 66705.05148918818,
        "makespan": 22007.377762869848,
        "route_balance": 0.1649572197684645
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 71141.23098004144,
        "total_distance": 66705.05148918818,
        "makespan": 22007.377762869848,
        "route_balance": 0.1649572197684645
      }
    }
  },
  "usable_memory": [
    {
      "summary_id": "CS1",
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "completion_status": "solver_requested_review",
      "condition_report": [
        {
          "condition_id": "s1",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "f1",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 10,
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
    },
    {
      "record_id": "M2",
      "contract_id": "C001",
      "intent_status": "not_applicable",
      "dominant_blocker": "solver_requested_review"
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
    "max_solver_actions_allowed": 8,
    "max_time_sec_allowed": 300.0,
    "max_iters_allowed": 2000
  }
}
```

</details>

### #035 [PROMPT] SUPERVISOR_REVIEW_PROMPT | C001

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
    "observation_id": "O_review_2",
    "frame_type": "supervisor_review",
    "role": "supervisor",
    "budget_caps": {
      "max_solver_actions": 8,
      "max_time_sec": 300.0,
      "max_iters": 2000
    },
    "completed_contract": {
      "contract_id": "C001",
      "contract_type": "initial_construction",
      "objective_layers": [
        "missed_priority",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": []
    },
    "contract_completion": {
      "completion_status": "solver_requested_review",
      "completion_reason": "solver_requested_review",
      "condition_report": [
        {
          "condition_id": "s1",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 1,
          "passed": false
        },
        {
          "condition_id": "f1",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 10,
          "window": 1,
          "passed": false
        }
      ],
      "completed": true,
      "reason": "solver_requested_review",
      "result": "solver_requested_review"
    },
    "condition_report": [
      {
        "condition_id": "s1",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 1,
        "passed": false
      },
      {
        "condition_id": "f1",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 10,
        "window": 1,
        "passed": false
      }
    ],
    "stage_verification_summary": {
      "verification_ids": [
        "V1",
        "V2"
      ],
      "intent_status_counts": {
        "achieved": 1,
        "not_applicable": 1
      },
      "dominant_blocker_counts": {
        "none": 1,
        "solver_requested_review": 1
      },
      "last": {
        "exists": true,
        "verification_id": "V2",
        "intent_status": "not_applicable",
        "dominant_blocker": "solver_requested_review",
        "metric_delta": {},
        "debt_delta": {},
        "trace_counts": {
          "candidate_trials": 0,
          "feasibility_rejected": 0,
          "accepted": 0,
          "best_improved": 0
        }
      }
    },
    "solution_position": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 71141.23098004144,
          "total_distance": 66705.05148918818,
          "makespan": 22007.377762869848,
          "route_balance": 0.1649572197684645
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 71141.23098004144,
          "total_distance": 66705.05148918818,
          "makespan": 22007.377762869848,
          "route_balance": 0.1649572197684645
        }
      }
    },
    "usable_memory": [
      {
        "summary_id": "CS1",
        "contract_id": "C001",
        "contract_type": "initial_construction",
        "completion_status": "solver_requested_review",
        "condition_report": [
          {
            "condition_id": "s1",
            "source": "missed_priority",
            "actual": null,
            "op": "==",
            "expected": 0,
            "window": 1,
            "passed": false
          },
          {
            "condition_id": "f1",
            "source": "total_actions",
            "actual": null,
            "op": ">=",
            "expected": 10,
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
      },
      {
        "record_id": "M2",
        "contract_id": "C001",
        "intent_status": "not_applicable",
        "dominant_blocker": "solver_requested_review"
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
      "max_solver_actions_allowed": 8,
      "max_time_sec_allowed": 300.0,
      "max_iters_allowed": 2000
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
                          "scarce_unassigned",
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
                    "description": "A metric that may not worsen beyond the provided amount.",
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
                      "maximum": 8
                    },
                    "max_actions": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 8
                    },
                    "max_iters": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 2000
                    },
                    "max_time_sec": {
                      "type": "number",
                      "exclusiveMinimum": 0,
                      "maximum": 300.0
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
                            "description": "Supported source path read from OutcomeVerification/progress."
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
                            "description": "Supported source path read from OutcomeVerification/progress."
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

### #036 [RAW] SUPERVISOR_REVIEW_RAW_OUTPUT | C001

<details>
<summary>Open raw LLM output</summary>

```text
{
  "supervisor_decision": {
    "action": "issue_contract",
    "contract_review": {
      "outcome_summary": "The initial construction produced a feasible solution with 18 missed priority tasks and 16 unassigned tasks. Solver requested review after failing to meet conditions for zero missed priority and sufficient actions. The solution is feasible but coverage is poor.",
      "main_lesson": "Priority coverage is the primary goal; need to assign all priority tasks even if it increases energy."
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
          "scarce_unassigned"
        ]
      },
      "protected_metrics": [],
      "resource_policy": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "s2",
            "source": "missed_priority",
            "op": "==",
            "value": 0,
            "window": 5
          }
        ],
        "failure": [
          {
            "condition_id": "f2",
            "source": "total_actions",
            "op": ">=",
            "value": 8,
            "window": 1
          }
        ]
      },
      "explanation": {
        "goal": "Eliminate all missed priority tasks even if energy increases",
        "reason_for_alns": "Feasible solution exists but coverage is poor; ALNS can explore neighborhood to improve assignment of priority tasks."
      }
    }
  }
}
```

</details>

### #037 [OK] SUPERVISOR_REVIEW_VALIDATED_PAYLOAD | C001

```json
{
  "supervisor_decision": {
    "action": "issue_contract",
    "contract_review": {
      "outcome_summary": "The initial construction produced a feasible solution with 18 missed priority tasks and 16 unassigned tasks. Solver requested review after failing to meet conditions for zero missed priority and sufficient actions. The solution is feasible but coverage is poor.",
      "main_lesson": "Priority coverage is the primary goal; need to assign all priority tasks even if it increases energy."
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
          "scarce_unassigned"
        ]
      },
      "protected_metrics": [],
      "resource_policy": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "exit_conditions": {
        "success": [
          {
            "condition_id": "s2",
            "source": "missed_priority",
            "op": "==",
            "value": 0,
            "window": 5
          }
        ],
        "failure": [
          {
            "condition_id": "f2",
            "source": "total_actions",
            "op": ">=",
            "value": 8,
            "window": 1
          }
        ]
      },
      "explanation": {
        "goal": "Eliminate all missed priority tasks even if energy increases",
        "reason_for_alns": "Feasible solution exists but coverage is poor; ALNS can explore neighborhood to improve assignment of priority tasks."
      }
    }
  }
}
```

### #038 [OK] VALIDATED_FEASIBILITY_CONTROL | C002

```json
{
  "mode": "strict",
  "relaxation_ratios": []
}
```

### #039 [COMP] COMPILED_FEASIBILITY_POLICY | C002

```json
{
  "mode": "strict"
}
```

### #040 [COMP] COMPILED_CONTRACT | C002

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
      "scarce_unassigned"
    ]
  },
  "protected_metrics": [],
  "resource_policy": {
    "min_actions": 1,
    "max_actions": 8,
    "max_iters": 2000,
    "max_time_sec": 300.0
  },
  "exit_conditions": {
    "success": [
      {
        "condition_id": "s2",
        "source": "missed_priority",
        "op": "==",
        "value": 0,
        "window": 5
      }
    ],
    "failure": [
      {
        "condition_id": "f2",
        "source": "total_actions",
        "op": ">=",
        "value": 8,
        "window": 1
      }
    ]
  },
  "explanation": {
    "goal": "Eliminate all missed priority tasks even if energy increases",
    "reason_for_alns": "Feasible solution exists but coverage is poor; ALNS can explore neighborhood to improve assignment of priority tasks."
  }
}
```

### #041 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 002

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
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 8,
      "time_sec": 300.0,
      "iters": 2000,
      "min_actions_remaining": 1
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 71141.23098004144,
        "total_distance": 66705.05148918818,
        "makespan": 22007.377762869848,
        "route_balance": 0.1649572197684645
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 18.0,
        "unassigned_count": 16.0,
        "energy_total": 71141.23098004144,
        "total_distance": 66705.05148918818,
        "makespan": 22007.377762869848,
        "route_balance": 0.1649572197684645
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V2",
    "intent_status": "not_applicable",
    "dominant_blocker": "solver_requested_review",
    "metric_delta": {},
    "debt_delta": {},
    "trace_counts": {
      "candidate_trials": 0,
      "feasibility_rejected": 0,
      "accepted": 0,
      "best_improved": 0
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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

### #042 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 002

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
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 8,
        "time_sec": 300.0,
        "iters": 2000,
        "min_actions_remaining": 1
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 71141.23098004144,
          "total_distance": 66705.05148918818,
          "makespan": 22007.377762869848,
          "route_balance": 0.1649572197684645
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 18.0,
          "unassigned_count": 16.0,
          "energy_total": 71141.23098004144,
          "total_distance": 66705.05148918818,
          "makespan": 22007.377762869848,
          "route_balance": 0.1649572197684645
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V2",
      "intent_status": "not_applicable",
      "dominant_blocker": "solver_requested_review",
      "metric_delta": {},
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "best_improved": 0
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
                "T_scarce_unassigned",
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

### #043 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 002

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        },
        {
          "name": "critical_block_removal",
          "score": 5
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 8
        },
        {
          "name": "cost_pressure",
          "score": 6
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        },
        {
          "name": "greedy_insertion",
          "score": 4
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 7
        },
        {
          "name": "regret_pressure",
          "score": 6
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 6
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Focus on T_unassigned_priority to reduce missed_priority and unassigned_count. Use worst/critical removal to target problematic tasks, and regret insertion with priority/scarcity signals to reinsert valuable tasks. Acceptance uses simulated annealing with moderate intensity to explore while improving coverage."
    }
  }
}
```

</details>

### #044 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 002

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        },
        {
          "name": "critical_block_removal",
          "score": 5
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 8
        },
        {
          "name": "cost_pressure",
          "score": 6
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        },
        {
          "name": "greedy_insertion",
          "score": 4
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 7
        },
        {
          "name": "regret_pressure",
          "score": 6
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 6
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Focus on T_unassigned_priority to reduce missed_priority and unassigned_count. Use worst/critical removal to target problematic tasks, and regret insertion with priority/scarcity signals to reinsert valuable tasks. Acceptance uses simulated annealing with moderate intensity to explore while improving coverage."
    }
  }
}
```

### #045 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 002

```json
{
  "manifest_id": "R3",
  "source_decision_id": "D3",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 4,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 6,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 8,
        "related_cluster_removal": 2,
        "critical_block_removal": 5,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 6,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 7,
        "scarcity_protection": 8
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 4,
      "threshold": 4.0,
      "worsening_allowance": 0.2
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #046 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 002

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 8,
      "related_cluster_removal": 2,
      "critical_block_removal": 5,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 6,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 7,
      "scarcity_protection": 8
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 4,
      "scarcity_first_insertion": 2,
      "regret_insertion": 8,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 7,
      "regret_pressure": 6,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 6,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 4,
    "accept_level": 0.2,
    "exploration_score": 4.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #047 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 002

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 250
}
```

### #048 [SOLVER] SOLVER_RESULT | C002 / SOLVER 002

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      11.0,
      68487.58677408994
    ],
    "quality_summary": {
      "missed_priority": 11.0,
      "unassigned_count": 11.0,
      "energy_total": 68487.58677408994,
      "total_distance": 62950.55595265201,
      "makespan": 22007.377762869848,
      "route_balance": 0.23163514750661013
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
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 5,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 6,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 8
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 4,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 6,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 4,
        "accept_level": 0.2,
        "exploration_score": 4.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 75,
    "actual_iters_used": 75,
    "actual_time_used_sec": 37.53910360000009,
    "best_update_count": 10,
    "best_update_iters": [
      2,
      5,
      8,
      14,
      15,
      27,
      67,
      69,
      70,
      75
    ],
    "best_update_lex_keys": [
      [
        18.0,
        69454.9493828088
      ],
      [
        14.0,
        69866.5222428003
      ],
      [
        13.0,
        69576.92971569924
      ],
      [
        13.0,
        69401.26534057548
      ],
      [
        13.0,
        69267.28516349307
      ],
      [
        12.0,
        68204.91250725322
      ],
      [
        11.0,
        70325.15226911448
      ],
      [
        11.0,
        69478.14784893728
      ],
      [
        11.0,
        68599.72768425269
      ],
      [
        11.0,
        68487.58677408994
      ]
    ],
    "first_best_iter": 2,
    "last_best_iter": 75,
    "plateau_iters_after_last_update": 0,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": -1,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "worst_task_removal",
      "shape": "task_set",
      "task_ids": [
        37,
        77,
        74,
        78,
        59,
        50,
        97,
        84,
        13,
        81,
        1,
        6,
        0,
        92,
        80,
        99,
        75,
        28
      ],
      "affected_routes": [
        0,
        1,
        2,
        3,
        4,
        5
      ],
      "features": {
        "cost_pressure": 1.0,
        "priority_loss": 1.0,
        "scarcity_pressure": 0.27792280469996844,
        "coupling_pressure": 1.0,
        "mobility_opportunity": 0.13447275963621766,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 4.717926879853776,
      "metadata": {
        "target_k": 18
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 4,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 6,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "greedy_insertion": 6,
        "regret_insertion": 8,
        "bottleneck_insertion": 3,
        "scarcity_first_insertion": 1
      },
      "unassigned_before": 29,
      "unassigned_after": 11,
      "inserted_count": 18,
      "failed_count": 11,
      "tasks_analyzed": 380,
      "positions_generated": 263,
      "positions_strict_checked": 263,
      "strict_feasible_positions": 259,
      "failure_breakdown": {
        "no_candidate": 209,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
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
          "task_id": 46,
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
          "task_id": 58,
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
          "task_id": 60,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 63,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 441.0306,
      "operator": "greedy_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 19.0,
        "current_lex_key": [
          19.0,
          69204.87302070363
        ],
        "best_feasible_objective": 18.0,
        "best_feasible_lex_key": [
          18.0,
          71141.23098004144
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 18.0,
        "current_lex_key": [
          18.0,
          69454.9493828088
        ],
        "best_feasible_objective": 18.0,
        "best_feasible_lex_key": [
          18.0,
          69454.9493828088
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 18.0,
        "current_lex_key": [
          18.0,
          69454.9493828088
        ],
        "best_feasible_objective": 18.0,
        "best_feasible_lex_key": [
          18.0,
          69454.9493828088
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 18.0,
        "current_lex_key": [
          18.0,
          69454.9493828088
        ],
        "best_feasible_objective": 18.0,
        "best_feasible_lex_key": [
          18.0,
          69454.9493828088
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69866.5222428003
        ],
        "best_feasible_objective": 14.0,
        "best_feasible_lex_key": [
          14.0,
          69866.5222428003
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69907.03717915685
        ],
        "best_feasible_objective": 14.0,
        "best_feasible_lex_key": [
          14.0,
          69866.5222428003
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69907.03717915685
        ],
        "best_feasible_objective": 14.0,
        "best_feasible_lex_key": [
          14.0,
          69866.5222428003
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69576.92971569924
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69576.92971569924
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69401.26534057548
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69401.26534057548
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69267.28516349307
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          69257.33825315542
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          69257.33825315542
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          68920.92461355809
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69401.18576231608
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          66786.4757362318
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          66744.79153819045
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 16.0,
        "current_lex_key": [
          16.0,
          67081.20517778778
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 16.0,
        "current_lex_key": [
          16.0,
          67081.20517778778
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          66744.79153819045
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          67842.50358061866
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 15.0,
        "current_lex_key": [
          15.0,
          66116.99634374768
        ],
        "best_feasible_objective": 13.0,
        "best_feasible_lex_key": [
          13.0,
          69267.28516349307
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68204.91250725322
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68204.91250725322
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69538.66837437476
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69538.66837437476
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69538.66837437476
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69538.66837437476
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70210.0084194282
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70210.0084194282
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70210.0084194282
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70210.0084194282
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70210.0084194282
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70165.17403060725
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70165.17403060725
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69701.06474924431
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69538.66837437476
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69951.48801169293
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          69951.48801169293
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69182.83219596234
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69182.83219596234
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69182.83219596234
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          68249.05656581883
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          67697.80188769771
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          68541.89183605374
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          68541.89183605374
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69213.23188110717
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70224.24501338816
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70224.24501338816
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70224.24501338816
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          70224.24501338816
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69462.90538808891
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69462.90538808891
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69462.90538808891
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69462.90538808891
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          70243.86661924089
        ],
        "best_feasible_objective": 12.0,
        "best_feasible_lex_key": [
          12.0,
          68204.91250725322
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          70325.15226911448
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          70325.15226911448
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          70325.15226911448
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          70325.15226911448
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          69478.14784893728
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          69478.14784893728
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 70,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68599.72768425269
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68599.72768425269
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 71,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68599.72768425269
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68599.72768425269
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 72,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68599.72768425269
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68599.72768425269
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 73,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68599.72768425269
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68599.72768425269
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 74,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68599.72768425269
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68599.72768425269
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 75,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68487.58677408994
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 12.0,
      "worst_task_removal": 19.0,
      "related_cluster_removal": 12.0,
      "critical_block_removal": 18.0,
      "route_rebalance_removal": 14.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 2183.0,
      "tasks_reinserted": 1222.0,
      "tasks_left_unassigned": 961.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 13594.0,
        "no_feasible": 29.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.8709333333333334,
          "worst_task_removal": 1.1609142857142858,
          "related_cluster_removal": 0.838857142857143,
          "critical_block_removal": 0.6957333333333334,
          "route_rebalance_removal": 0.6837142857142859
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 8.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 5.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.0721268770094807,
          "worst_task_removal": 1.8809299135682986,
          "related_cluster_removal": 1.042373841304568,
          "critical_block_removal": 1.1391334624812186,
          "route_rebalance_removal": 0.8941564004480634
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 4.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 8.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 75,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 19,
          "related_cluster_removal": 12,
          "critical_block_removal": 18,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 16.466667
      },
      "repair": {
        "candidate_tasks_total": 2183,
        "tasks_reinserted": 1222,
        "tasks_left_unassigned": 961,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 13594,
          "no_feasible": 29
        }
      },
      "trial_flow": {
        "candidate_trials": 75,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 75,
        "acceptance_rejected": 16,
        "accepted_trials": 59,
        "best_improved_trials": 10
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 59,
    "rejected_trial_count": 16
  }
}
```

### #049 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 002

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 75,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 12,
      "worst_task_removal": 19,
      "related_cluster_removal": 12,
      "critical_block_removal": 18,
      "route_rebalance_removal": 14
    },
    "removed_task_count_avg": 16.466667
  },
  "repair": {
    "candidate_tasks_total": 2183,
    "tasks_reinserted": 1222,
    "tasks_left_unassigned": 961,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 13594,
      "no_feasible": 29
    }
  },
  "trial_flow": {
    "candidate_trials": 75,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 75,
    "acceptance_rejected": 16,
    "accepted_trials": 59,
    "best_improved_trials": 10
  },
  "rejection_reasons": {}
}
```

### #050 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 002

```json
{
  "verification_id": "V3",
  "contract_id": "C002",
  "decision_id": "D3",
  "manifest_id": "R3",
  "trace_id": "X3",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": -7.0,
      "unassigned_count": -5.0,
      "energy_total": -2653.6442059514957
    },
    "best_feasible": {
      "missed_priority": -7.0,
      "unassigned_count": -5.0,
      "energy_total": -2653.6442059514957
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
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved",
    "best_feasible_improved"
  ],
  "trace": {
    "trace_id": "X3",
    "kind": "alns",
    "iters": 75,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 19,
        "related_cluster_removal": 12,
        "critical_block_removal": 18,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 16.466667
    },
    "repair": {
      "candidate_tasks_total": 2183,
      "tasks_reinserted": 1222,
      "tasks_left_unassigned": 961,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 13594,
        "no_feasible": 29
      }
    },
    "trial_flow": {
      "candidate_trials": 75,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 75,
      "acceptance_rejected": 16,
      "accepted_trials": 59,
      "best_improved_trials": 10
    },
    "rejection_reasons": {}
  }
}
```

### #051 [MEM] MEMORY_UPDATE | C002 / SOLVER 002

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
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:4"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": -7.0,
      "unassigned_count": -5.0,
      "energy_total": -2653.6442059514957
    }
  },
  "manifest": {
    "manifest_id": "R3",
    "source_decision_id": "D3",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 4,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 6,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 5,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 6,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 8
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 4,
        "threshold": 4.0,
        "worsening_allowance": 0.2
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
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
    "iters": 75,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 19,
        "related_cluster_removal": 12,
        "critical_block_removal": 18,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 16.466667
    },
    "repair": {
      "candidate_tasks_total": 2183,
      "tasks_reinserted": 1222,
      "tasks_left_unassigned": 961,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 13594,
        "no_feasible": 29
      }
    },
    "trial_flow": {
      "candidate_trials": 75,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 75,
      "acceptance_rejected": 16,
      "accepted_trials": 59,
      "best_improved_trials": 10
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
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": -7.0,
        "unassigned_count": -5.0,
        "energy_total": -2653.6442059514957
      },
      "best_feasible": {
        "missed_priority": -7.0,
        "unassigned_count": -5.0,
        "energy_total": -2653.6442059514957
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
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved",
      "best_feasible_improved"
    ],
    "trace": {
      "trace_id": "X3",
      "kind": "alns",
      "iters": 75,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 19,
          "related_cluster_removal": 12,
          "critical_block_removal": 18,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 16.466667
      },
      "repair": {
        "candidate_tasks_total": 2183,
        "tasks_reinserted": 1222,
        "tasks_left_unassigned": 961,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 13594,
          "no_feasible": 29
        }
      },
      "trial_flow": {
        "candidate_trials": 75,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 75,
        "acceptance_rejected": 16,
        "accepted_trials": 59,
        "best_improved_trials": 10
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #052 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 002

```json
{
  "contract_id": "C002",
  "solver_actions": 1,
  "time_used_sec": 37.5,
  "iters_used": 75,
  "verification_ids": [
    "V3"
  ],
  "intent_status_counts": {
    "achieved": 1
  },
  "dominant_blocker_counts": {
    "none": 1
  },
  "metric_delta_total": {
    "missed_priority": -7.0,
    "unassigned_count": -5.0,
    "energy_total": -2653.6442059514957
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #053 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 002

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #054 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 003

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
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 7,
      "time_sec": 262.5,
      "iters": 1925,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 11.0,
        "unassigned_count": 11.0,
        "energy_total": 68487.58677408994,
        "total_distance": 62950.55595265201,
        "makespan": 22007.377762869848,
        "route_balance": 0.23163514750661013
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 11.0,
        "unassigned_count": 11.0,
        "energy_total": 68487.58677408994,
        "total_distance": 62950.55595265201,
        "makespan": 22007.377762869848,
        "route_balance": 0.23163514750661013
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V3",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": -7.0,
      "unassigned_count": -5.0,
      "energy_total": -2653.6442059514957
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 75,
      "feasibility_rejected": 0,
      "accepted": 59,
      "best_improved": 10
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 11.0,
        "unassigned_count": 11.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M3",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
    }
  ]
}
```

</details>

### #055 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 003

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
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 7,
        "time_sec": 262.5,
        "iters": 1925,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 11.0,
          "unassigned_count": 11.0,
          "energy_total": 68487.58677408994,
          "total_distance": 62950.55595265201,
          "makespan": 22007.377762869848,
          "route_balance": 0.23163514750661013
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 11.0,
          "unassigned_count": 11.0,
          "energy_total": 68487.58677408994,
          "total_distance": 62950.55595265201,
          "makespan": 22007.377762869848,
          "route_balance": 0.23163514750661013
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V3",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": -7.0,
        "unassigned_count": -5.0,
        "energy_total": -2653.6442059514957
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 75,
        "feasibility_rejected": 0,
        "accepted": 59,
        "best_improved": 10
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 11.0,
          "unassigned_count": 11.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M3",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
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
                "T_scarce_unassigned",
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

### #056 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 003

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 6
        }
      ],
      "intensity_score": 6
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 7
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 8
        },
        {
          "name": "insert_cost",
          "score": 6
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 5
    },
    "explanation": {
      "rationale": "Continue improving priority coverage and energy based on previous successful pattern (worst_task_removal + priority_loss + future_slack + sa). Adapted with recommended signals for destroy and insertion to maintain momentum."
    }
  }
}
```

</details>

### #057 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 003

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 6
        }
      ],
      "intensity_score": 6
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 7
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 8
        },
        {
          "name": "insert_cost",
          "score": 6
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 5
    },
    "explanation": {
      "rationale": "Continue improving priority coverage and energy based on previous successful pattern (worst_task_removal + priority_loss + future_slack + sa). Adapted with recommended signals for destroy and insertion to maintain momentum."
    }
  }
}
```

### #058 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 003

```json
{
  "manifest_id": "R4",
  "source_decision_id": "D4",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 8,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 8,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 7,
        "scarcity_protection": 6
      },
      "intensity_score": 6,
      "remove_ratio": 0.22999999999999998
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 5,
      "threshold": 5.0,
      "worsening_allowance": 0.25
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #059 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 003

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 8,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 7,
      "scarcity_protection": 6
    },
    "intensity_score": 6,
    "remove_ratio": 0.22999999999999998
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 2,
      "regret_insertion": 8,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 7,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 6,
      "future_slack": 8,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 5,
    "accept_level": 0.25,
    "exploration_score": 5.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #060 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 003

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 275
}
```

### #061 [SOLVER] SOLVER_RESULT | C002 / SOLVER 003

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      7.0,
      68961.34654143231
    ],
    "quality_summary": {
      "missed_priority": 7.0,
      "unassigned_count": 9.0,
      "energy_total": 68961.34654143231,
      "total_distance": 63261.93672994429,
      "makespan": 22007.377762869848,
      "route_balance": 0.2884484560089382
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
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 6
        },
        "intensity_score": 6,
        "remove_ratio": 0.22999999999999998
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 8,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 5,
        "accept_level": 0.25,
        "exploration_score": 5.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 63,
    "actual_iters_used": 63,
    "actual_time_used_sec": 38.06649230000039,
    "best_update_count": 4,
    "best_update_iters": [
      8,
      9,
      41,
      63
    ],
    "best_update_lex_keys": [
      [
        11.0,
        67922.87145654936
      ],
      [
        10.0,
        68326.24122552625
      ],
      [
        9.0,
        67579.07148947372
      ],
      [
        7.0,
        68961.34654143231
      ]
    ],
    "first_best_iter": 8,
    "last_best_iter": 63,
    "plateau_iters_after_last_update": 0,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": -1,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "random_removal",
      "shape": "random",
      "task_ids": [
        98,
        23,
        92,
        90,
        29,
        14,
        35,
        51,
        28,
        52,
        45,
        13,
        48,
        44,
        95,
        75,
        22,
        37,
        50,
        21,
        17
      ],
      "affected_routes": [
        0,
        1,
        3,
        4,
        5
      ],
      "features": {
        "cost_pressure": 0.0,
        "priority_loss": 0.0,
        "scarcity_pressure": 0.0,
        "coupling_pressure": 0.0,
        "mobility_opportunity": 0.0,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 0.0,
      "metadata": {
        "target_k": 21
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 8,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "regret_insertion": 7,
        "greedy_insertion": 4,
        "bottleneck_insertion": 4,
        "scarcity_first_insertion": 4,
        "diversified_insertion": 3
      },
      "unassigned_before": 31,
      "unassigned_after": 9,
      "inserted_count": 22,
      "failed_count": 9,
      "tasks_analyzed": 460,
      "positions_generated": 388,
      "positions_strict_checked": 388,
      "strict_feasible_positions": 388,
      "failure_breakdown": {
        "no_candidate": 194,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 46,
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
          "task_id": 58,
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
          "task_id": 59,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 60,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 63,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 570.9108,
      "operator": "scarcity_first_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69197.26291132043
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69197.26291132043
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          69455.25757155262
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68883.44654659774
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68883.44654659774
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          68373.72532577245
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          67900.47786308301
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          68487.58677408994
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          67922.87145654936
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          67922.87145654936
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68326.24122552625
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68326.24122552625
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69845.4505010764
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69845.4505010764
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69845.4505010764
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70667.258041488
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70902.63378017007
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70880.05013749276
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70880.05013749276
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          72040.94083637549
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          72040.94083637549
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          72820.42571733892
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          71637.32978264359
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          71637.32978264359
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          71363.65574434916
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          71942.56069708789
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          72646.53555654662
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          72183.44298969365
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          72566.43386665786
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          71722.34391830183
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          71722.34391830183
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          70372.62271064831
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          71620.08242798122
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70339.19760922973
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69424.86113245437
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          67608.37954006699
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          68326.24122552625
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67579.07148947372
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67579.07148947372
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67579.07148947372
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67579.07148947372
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68540.96731917668
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68905.26480948238
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70657.5242694062
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          70595.61527127596
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          70595.61527127596
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69367.4113327174
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69367.4113327174
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69367.4113327174
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69705.73538512748
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69705.73538512748
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69849.65132274282
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69206.92387448896
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          67579.07148947372
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68961.34654143231
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68961.34654143231
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 17.0,
      "worst_task_removal": 14.0,
      "related_cluster_removal": 11.0,
      "critical_block_removal": 13.0,
      "route_rebalance_removal": 8.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1859.0,
      "tasks_reinserted": 1181.0,
      "tasks_left_unassigned": 678.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10869.0,
        "no_feasible": 9.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.7925714285714287,
          "worst_task_removal": 0.8880000000000001,
          "related_cluster_removal": 0.8458666666666667,
          "critical_block_removal": 0.6974285714285715,
          "route_rebalance_removal": 0.6960000000000002
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 8.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 0.9989328799659076,
          "worst_task_removal": 1.5384458729028812,
          "related_cluster_removal": 1.0488996297355089,
          "critical_block_removal": 0.9075745316519311,
          "route_rebalance_removal": 0.9061799078687115
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 8.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 63,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 17,
          "worst_task_removal": 14,
          "related_cluster_removal": 11,
          "critical_block_removal": 13,
          "route_rebalance_removal": 8
        },
        "removed_task_count_avg": 18.84127
      },
      "repair": {
        "candidate_tasks_total": 1859,
        "tasks_reinserted": 1181,
        "tasks_left_unassigned": 678,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 10869,
          "no_feasible": 9
        }
      },
      "trial_flow": {
        "candidate_trials": 63,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 63,
        "acceptance_rejected": 12,
        "accepted_trials": 51,
        "best_improved_trials": 4
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 51,
    "rejected_trial_count": 12
  }
}
```

### #062 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 003

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 63,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 17,
      "worst_task_removal": 14,
      "related_cluster_removal": 11,
      "critical_block_removal": 13,
      "route_rebalance_removal": 8
    },
    "removed_task_count_avg": 18.84127
  },
  "repair": {
    "candidate_tasks_total": 1859,
    "tasks_reinserted": 1181,
    "tasks_left_unassigned": 678,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 10869,
      "no_feasible": 9
    }
  },
  "trial_flow": {
    "candidate_trials": 63,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 63,
    "acceptance_rejected": 12,
    "accepted_trials": 51,
    "best_improved_trials": 4
  },
  "rejection_reasons": {}
}
```

### #063 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 003

```json
{
  "verification_id": "V4",
  "contract_id": "C002",
  "decision_id": "D4",
  "manifest_id": "R4",
  "trace_id": "X4",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": -4.0,
      "unassigned_count": -2.0,
      "energy_total": 473.7597673423734
    },
    "best_feasible": {
      "missed_priority": -4.0,
      "unassigned_count": -2.0,
      "energy_total": 473.7597673423734
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
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved",
    "best_feasible_improved"
  ],
  "trace": {
    "trace_id": "X4",
    "kind": "alns",
    "iters": 63,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 17,
        "worst_task_removal": 14,
        "related_cluster_removal": 11,
        "critical_block_removal": 13,
        "route_rebalance_removal": 8
      },
      "removed_task_count_avg": 18.84127
    },
    "repair": {
      "candidate_tasks_total": 1859,
      "tasks_reinserted": 1181,
      "tasks_left_unassigned": 678,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10869,
        "no_feasible": 9
      }
    },
    "trial_flow": {
      "candidate_trials": 63,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 63,
      "acceptance_rejected": 12,
      "accepted_trials": 51,
      "best_improved_trials": 4
    },
    "rejection_reasons": {}
  }
}
```

### #064 [MEM] MEMORY_UPDATE | C002 / SOLVER 003

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
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:5"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": -4.0,
      "unassigned_count": -2.0,
      "energy_total": 473.7597673423734
    }
  },
  "manifest": {
    "manifest_id": "R4",
    "source_decision_id": "D4",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 8,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 6
        },
        "intensity_score": 6,
        "remove_ratio": 0.22999999999999998
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 5,
        "threshold": 5.0,
        "worsening_allowance": 0.25
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
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
    "iters": 63,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 17,
        "worst_task_removal": 14,
        "related_cluster_removal": 11,
        "critical_block_removal": 13,
        "route_rebalance_removal": 8
      },
      "removed_task_count_avg": 18.84127
    },
    "repair": {
      "candidate_tasks_total": 1859,
      "tasks_reinserted": 1181,
      "tasks_left_unassigned": 678,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10869,
        "no_feasible": 9
      }
    },
    "trial_flow": {
      "candidate_trials": 63,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 63,
      "acceptance_rejected": 12,
      "accepted_trials": 51,
      "best_improved_trials": 4
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
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": -4.0,
        "unassigned_count": -2.0,
        "energy_total": 473.7597673423734
      },
      "best_feasible": {
        "missed_priority": -4.0,
        "unassigned_count": -2.0,
        "energy_total": 473.7597673423734
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
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved",
      "best_feasible_improved"
    ],
    "trace": {
      "trace_id": "X4",
      "kind": "alns",
      "iters": 63,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 17,
          "worst_task_removal": 14,
          "related_cluster_removal": 11,
          "critical_block_removal": 13,
          "route_rebalance_removal": 8
        },
        "removed_task_count_avg": 18.84127
      },
      "repair": {
        "candidate_tasks_total": 1859,
        "tasks_reinserted": 1181,
        "tasks_left_unassigned": 678,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 10869,
          "no_feasible": 9
        }
      },
      "trial_flow": {
        "candidate_trials": 63,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 63,
        "acceptance_rejected": 12,
        "accepted_trials": 51,
        "best_improved_trials": 4
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #065 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 003

```json
{
  "contract_id": "C002",
  "solver_actions": 2,
  "time_used_sec": 75.0,
  "iters_used": 138,
  "verification_ids": [
    "V3",
    "V4"
  ],
  "intent_status_counts": {
    "achieved": 2
  },
  "dominant_blocker_counts": {
    "none": 2
  },
  "metric_delta_total": {
    "missed_priority": -11.0,
    "unassigned_count": -7.0,
    "energy_total": -2179.8844386091223
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #066 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 003

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #067 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 004

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O5",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 4,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 6,
      "time_sec": 225.0,
      "iters": 1862,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 9.0,
        "energy_total": 68961.34654143231,
        "total_distance": 63261.93672994429,
        "makespan": 22007.377762869848,
        "route_balance": 0.2884484560089382
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 9.0,
        "energy_total": 68961.34654143231,
        "total_distance": 63261.93672994429,
        "makespan": 22007.377762869848,
        "route_balance": 0.2884484560089382
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V4",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": -4.0,
      "unassigned_count": -2.0,
      "energy_total": 473.7597673423734
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 63,
      "feasibility_rejected": 0,
      "accepted": 51,
      "best_improved": 4
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 7.0,
        "unassigned_count": 9.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M3",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
    },
    {
      "record_id": "M4",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
    }
  ]
}
```

</details>

### #068 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 004

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
    "observation_id": "O5",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 4,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 6,
        "time_sec": 225.0,
        "iters": 1862,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 9.0,
          "energy_total": 68961.34654143231,
          "total_distance": 63261.93672994429,
          "makespan": 22007.377762869848,
          "route_balance": 0.2884484560089382
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 9.0,
          "energy_total": 68961.34654143231,
          "total_distance": 63261.93672994429,
          "makespan": 22007.377762869848,
          "route_balance": 0.2884484560089382
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V4",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": -4.0,
        "unassigned_count": -2.0,
        "energy_total": 473.7597673423734
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 63,
        "feasibility_rejected": 0,
        "accepted": 51,
        "best_improved": 4
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 7.0,
          "unassigned_count": 9.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M3",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
      },
      {
        "record_id": "M4",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
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
                "T_scarce_unassigned",
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

### #069 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 004

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 5
        },
        {
          "name": "scarcity_protection",
          "score": 5
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 6
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 8
        },
        {
          "name": "scarcity_pressure",
          "score": 3
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 4
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Emulate memory M3 which reduced missed priority and energy. Focus on worst-task removal with priority and slack signals, SA acceptance."
    }
  }
}
```

</details>

### #070 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 004

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 5
        },
        {
          "name": "scarcity_protection",
          "score": 5
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 6
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 8
        },
        {
          "name": "scarcity_pressure",
          "score": 3
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 4
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Emulate memory M3 which reduced missed priority and energy. Focus on worst-task removal with priority and slack signals, SA acceptance."
    }
  }
}
```

### #071 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 004

```json
{
  "manifest_id": "R5",
  "source_decision_id": "D5",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 6,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 8,
        "scarcity_pressure": 3,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 4,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 8,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 5,
        "scarcity_protection": 5
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 4,
      "threshold": 4.0,
      "worsening_allowance": 0.2
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #072 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 004

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 8,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 5,
      "scarcity_protection": 5
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 2,
      "regret_insertion": 6,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 8,
      "scarcity_pressure": 3,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 4,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 4,
    "accept_level": 0.2,
    "exploration_score": 4.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #073 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 004

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 310
}
```

### #074 [SOLVER] SOLVER_RESULT | C002 / SOLVER 004

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      8.0,
      69503.21817816769
    ],
    "quality_summary": {
      "missed_priority": 8.0,
      "unassigned_count": 6.0,
      "energy_total": 69503.21817816769,
      "total_distance": 63868.693846301176,
      "makespan": 22007.377762869848,
      "route_balance": 0.20737860308104178
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
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 5,
          "scarcity_protection": 5
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 6,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 8,
          "scarcity_pressure": 3,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 4,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 4,
        "accept_level": 0.2,
        "exploration_score": 4.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 75,
    "actual_iters_used": 75,
    "actual_time_used_sec": 37.731712900000275,
    "best_update_count": 4,
    "best_update_iters": [
      5,
      11,
      14,
      23
    ],
    "best_update_lex_keys": [
      [
        7.0,
        68949.78834380633
      ],
      [
        7.0,
        67752.59860597232
      ],
      [
        7.0,
        67442.40192998158
      ],
      [
        7.0,
        67372.16721086697
      ]
    ],
    "first_best_iter": 5,
    "last_best_iter": 23,
    "plateau_iters_after_last_update": 52,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 1,
      "accepted": false,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy.",
      "delta_soft": 0.2,
      "temperature": 0.10351403414882408
    },
    "last_destroy_move": {
      "operator_name": "related_cluster_removal",
      "shape": "cluster",
      "task_ids": [
        30,
        12,
        22,
        11,
        99,
        33,
        7,
        19,
        0,
        13,
        18,
        16,
        64,
        37,
        49,
        43,
        10,
        32,
        27
      ],
      "affected_routes": [
        0,
        1,
        5
      ],
      "features": {
        "cost_pressure": 0.7641426526904417,
        "priority_loss": 0.6,
        "scarcity_pressure": 0.6249256093485497,
        "coupling_pressure": 0.3419904692432104,
        "mobility_opportunity": 0.5096754299635804,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": -0.5762508969248463,
      "metadata": {
        "target_k": 19,
        "seed_task": 30
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 6,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 8,
        "scarcity_pressure": 3,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 4,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "regret_insertion": 6,
        "greedy_insertion": 3,
        "diversified_insertion": 3,
        "bottleneck_insertion": 2,
        "scarcity_first_insertion": 6
      },
      "unassigned_before": 25,
      "unassigned_after": 5,
      "inserted_count": 20,
      "failed_count": 5,
      "tasks_analyzed": 315,
      "positions_generated": 344,
      "positions_strict_checked": 344,
      "strict_feasible_positions": 330,
      "failure_breakdown": {
        "no_candidate": 80,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
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
          "task_id": 25,
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
          "task_id": 85,
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
          "task_id": 86,
          "priority": 3.0,
          "capable_agents": 6,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 98,
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
      "time_ms": 504.3699,
      "operator": "diversified_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68961.34654143231
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68961.34654143231
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          69421.11040607726
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68961.34654143231
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          69421.11040607726
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68961.34654143231
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          69421.11040607726
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68961.34654143231
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68949.78834380633
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68949.78834380633
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68949.78834380633
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68949.78834380633
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68993.27080469416
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          68993.27080469416
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          68949.78834380633
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67752.59860597232
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67752.59860597232
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67899.90104820178
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67752.59860597232
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67899.90104820178
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67752.59860597232
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67442.40192998158
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67442.40192998158
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67988.06763946074
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67661.10434884032
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67661.10434884032
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67988.06763946074
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67988.06763946074
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67988.06763946074
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67988.06763946074
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67442.40192998158
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67372.16721086697
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67372.16721086697
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67372.16721086697
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67372.16721086697
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          67449.91582113242
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          70609.65073650134
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68182.52257963202
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68182.52257963202
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68182.52257963202
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68182.52257963202
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69847.06715253978
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69847.06715253978
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69847.06715253978
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          70207.95561058618
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          70560.7293641586
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69669.57078401445
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68997.10585229658
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69170.75927337591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70888.04198330695
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          71326.89639198038
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          71829.43319175919
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          71910.57086361591
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70096.19267973825
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          69999.7111720777
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          71465.41895586469
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          70706.51122386708
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69982.64876524487
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69982.64876524487
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71761.3262108489
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71761.3262108489
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69159.4994256853
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69159.4994256853
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69159.4994256853
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69159.4994256853
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67772.37945364804
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67772.37945364804
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67772.37945364804
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67772.37945364804
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 70,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67772.37945364804
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 71,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68417.4824871937
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 72,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68417.4824871937
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 73,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68417.4824871937
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 74,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 75,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          67372.16721086697
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 12.0,
      "worst_task_removal": 17.0,
      "related_cluster_removal": 16.0,
      "critical_block_removal": 17.0,
      "route_rebalance_removal": 13.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1875.0,
      "tasks_reinserted": 1220.0,
      "tasks_left_unassigned": 655.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9748.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 1.0826666666666669,
          "worst_task_removal": 0.7120000000000002,
          "related_cluster_removal": 0.6684444444444445,
          "critical_block_removal": 0.7007619047619048,
          "route_rebalance_removal": 0.7973333333333334
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 8.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.262201155160258,
          "worst_task_removal": 1.303564401465798,
          "related_cluster_removal": 0.8791368563794214,
          "critical_block_removal": 0.9108258803597449,
          "route_rebalance_removal": 1.0034308275676938
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 6.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 75,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 17,
          "related_cluster_removal": 16,
          "critical_block_removal": 17,
          "route_rebalance_removal": 13
        },
        "removed_task_count_avg": 16.48
      },
      "repair": {
        "candidate_tasks_total": 1875,
        "tasks_reinserted": 1220,
        "tasks_left_unassigned": 655,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 9748
        }
      },
      "trial_flow": {
        "candidate_trials": 75,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 75,
        "acceptance_rejected": 19,
        "accepted_trials": 56,
        "best_improved_trials": 4
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 56,
    "rejected_trial_count": 19
  }
}
```

### #075 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 004

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 75,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 12,
      "worst_task_removal": 17,
      "related_cluster_removal": 16,
      "critical_block_removal": 17,
      "route_rebalance_removal": 13
    },
    "removed_task_count_avg": 16.48
  },
  "repair": {
    "candidate_tasks_total": 1875,
    "tasks_reinserted": 1220,
    "tasks_left_unassigned": 655,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 9748
    }
  },
  "trial_flow": {
    "candidate_trials": 75,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 75,
    "acceptance_rejected": 19,
    "accepted_trials": 56,
    "best_improved_trials": 4
  },
  "rejection_reasons": {}
}
```

### #076 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 004

```json
{
  "verification_id": "V5",
  "contract_id": "C002",
  "decision_id": "D5",
  "manifest_id": "R5",
  "trace_id": "X5",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 1.0,
      "unassigned_count": -3.0,
      "energy_total": 541.8716367353773
    },
    "best_feasible": {
      "missed_priority": 0.0,
      "unassigned_count": 0.0,
      "energy_total": -1589.179330565341
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
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved",
    "best_feasible_improved"
  ],
  "trace": {
    "trace_id": "X5",
    "kind": "alns",
    "iters": 75,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 17,
        "related_cluster_removal": 16,
        "critical_block_removal": 17,
        "route_rebalance_removal": 13
      },
      "removed_task_count_avg": 16.48
    },
    "repair": {
      "candidate_tasks_total": 1875,
      "tasks_reinserted": 1220,
      "tasks_left_unassigned": 655,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9748
      }
    },
    "trial_flow": {
      "candidate_trials": 75,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 75,
      "acceptance_rejected": 19,
      "accepted_trials": 56,
      "best_improved_trials": 4
    },
    "rejection_reasons": {}
  }
}
```

### #077 [MEM] MEMORY_UPDATE | C002 / SOLVER 004

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M5",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O5",
  "decision_id": "D5",
  "manifest_id": "R5",
  "trace_id": "X5",
  "verification_id": "V5",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:4"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": 1.0,
      "unassigned_count": -3.0,
      "energy_total": 541.8716367353773
    }
  },
  "manifest": {
    "manifest_id": "R5",
    "source_decision_id": "D5",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 6,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 8,
          "scarcity_pressure": 3,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 4,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 5,
          "scarcity_protection": 5
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 4,
        "threshold": 4.0,
        "worsening_allowance": 0.2
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X5",
    "kind": "alns",
    "iters": 75,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 17,
        "related_cluster_removal": 16,
        "critical_block_removal": 17,
        "route_rebalance_removal": 13
      },
      "removed_task_count_avg": 16.48
    },
    "repair": {
      "candidate_tasks_total": 1875,
      "tasks_reinserted": 1220,
      "tasks_left_unassigned": 655,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9748
      }
    },
    "trial_flow": {
      "candidate_trials": 75,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 75,
      "acceptance_rejected": 19,
      "accepted_trials": 56,
      "best_improved_trials": 4
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V5",
    "contract_id": "C002",
    "decision_id": "D5",
    "manifest_id": "R5",
    "trace_id": "X5",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 1.0,
        "unassigned_count": -3.0,
        "energy_total": 541.8716367353773
      },
      "best_feasible": {
        "missed_priority": 0.0,
        "unassigned_count": 0.0,
        "energy_total": -1589.179330565341
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
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved",
      "best_feasible_improved"
    ],
    "trace": {
      "trace_id": "X5",
      "kind": "alns",
      "iters": 75,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 17,
          "related_cluster_removal": 16,
          "critical_block_removal": 17,
          "route_rebalance_removal": 13
        },
        "removed_task_count_avg": 16.48
      },
      "repair": {
        "candidate_tasks_total": 1875,
        "tasks_reinserted": 1220,
        "tasks_left_unassigned": 655,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 9748
        }
      },
      "trial_flow": {
        "candidate_trials": 75,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 75,
        "acceptance_rejected": 19,
        "accepted_trials": 56,
        "best_improved_trials": 4
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #078 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 004

```json
{
  "contract_id": "C002",
  "solver_actions": 3,
  "time_used_sec": 112.5,
  "iters_used": 213,
  "verification_ids": [
    "V3",
    "V4",
    "V5"
  ],
  "intent_status_counts": {
    "achieved": 3
  },
  "dominant_blocker_counts": {
    "none": 3
  },
  "metric_delta_total": {
    "missed_priority": -10.0,
    "unassigned_count": -10.0,
    "energy_total": -1638.012801873745
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #079 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 004

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #080 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 005

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O6",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 5,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 5,
      "time_sec": 187.5,
      "iters": 1787,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 8.0,
        "unassigned_count": 6.0,
        "energy_total": 69503.21817816769,
        "total_distance": 63868.693846301176,
        "makespan": 22007.377762869848,
        "route_balance": 0.20737860308104178
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 9.0,
        "energy_total": 67372.16721086697,
        "total_distance": 61668.87181534817,
        "makespan": 22007.377762869848,
        "route_balance": 0.2508288397915017
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V5",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": 1.0,
      "unassigned_count": -3.0,
      "energy_total": 541.8716367353773
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 75,
      "feasibility_rejected": 0,
      "accepted": 56,
      "best_improved": 4
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 8.0,
        "unassigned_count": 6.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M3",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
    },
    {
      "record_id": "M4",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
    },
    {
      "record_id": "M5",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
    }
  ]
}
```

</details>

### #081 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 005

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
    "observation_id": "O6",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 5,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 5,
        "time_sec": 187.5,
        "iters": 1787,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 8.0,
          "unassigned_count": 6.0,
          "energy_total": 69503.21817816769,
          "total_distance": 63868.693846301176,
          "makespan": 22007.377762869848,
          "route_balance": 0.20737860308104178
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 9.0,
          "energy_total": 67372.16721086697,
          "total_distance": 61668.87181534817,
          "makespan": 22007.377762869848,
          "route_balance": 0.2508288397915017
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V5",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 1.0,
        "unassigned_count": -3.0,
        "energy_total": 541.8716367353773
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 75,
        "feasibility_rejected": 0,
        "accepted": 56,
        "best_improved": 4
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 8.0,
          "unassigned_count": 6.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M3",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority -7, unassigned_count -5, energy_total -2.65e+03, accepted 59/75, blocker none"
      },
      {
        "record_id": "M4",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
      },
      {
        "record_id": "M5",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
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
                "T_scarce_unassigned",
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

### #082 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 005

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {"name": "worst_task_removal", "score": 10}
      ],
      "signal_scores": [
        {"name": "mobility_opportunity", "score": 5},
        {"name": "scarcity_protection", "score": 5}
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {"name": "regret_insertion", "score": 10}
      ],
      "task_signal_scores": [
        {"name": "priority_loss", "score": 10},
        {"name": "scarcity_pressure", "score": 5}
      ],
      "position_signal_scores": [
        {"name": "future_slack", "score": 10},
        {"name": "insert_cost", "score": 5}
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "reason": "Target unassigned priority to reduce missed_priority. Using worst_task_removal (similar to M3's success) with signals from recommendations, regret_insertion to prioritize high-priority tasks, and SA acceptance with intensity 4 to balance exploration."
    }
  }
}
```

</details>

### #083 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 005

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 10
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 5
        },
        {
          "name": "scarcity_protection",
          "score": 5
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 10
        },
        {
          "name": "scarcity_pressure",
          "score": 5
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 10
        },
        {
          "name": "insert_cost",
          "score": 5
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "reason": "Target unassigned priority to reduce missed_priority. Using worst_task_removal (similar to M3's success) with signals from recommendations, regret_insertion to prioritize high-priority tasks, and SA acceptance with intensity 4 to balance exploration."
    }
  }
}
```

### #084 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 005

```json
{
  "manifest_id": "R6",
  "source_decision_id": "D6",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 10,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 5,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 5,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 10,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 5,
        "scarcity_protection": 5
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 4,
      "threshold": 4.0,
      "worsening_allowance": 0.2
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #085 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 005

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 10,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 5,
      "scarcity_protection": 5
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 2,
      "regret_insertion": 10,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 10,
      "scarcity_pressure": 5,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 5,
      "future_slack": 10,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 4,
    "accept_level": 0.2,
    "exploration_score": 4.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #086 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 005

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 357
}
```

### #087 [SOLVER] SOLVER_RESULT | C002 / SOLVER 005

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      9.0,
      67345.60237694303
    ],
    "quality_summary": {
      "missed_priority": 9.0,
      "unassigned_count": 9.0,
      "energy_total": 67345.60237694303,
      "total_distance": 61371.11179257796,
      "makespan": 22007.377762869848,
      "route_balance": 0.2565410446138187
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
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 5,
          "scarcity_protection": 5
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 10,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 5,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 5,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 4,
        "accept_level": 0.2,
        "exploration_score": 4.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 69,
    "actual_iters_used": 69,
    "actual_time_used_sec": 37.6275945999987,
    "best_update_count": 2,
    "best_update_iters": [
      6,
      43
    ],
    "best_update_lex_keys": [
      [
        8.0,
        69467.72852906045
      ],
      [
        8.0,
        68136.04529586386
      ]
    ],
    "first_best_iter": 6,
    "last_best_iter": 43,
    "plateau_iters_after_last_update": 26,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": -1,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "related_cluster_removal",
      "shape": "cluster",
      "task_ids": [
        5,
        15,
        13,
        6,
        61,
        66,
        94,
        50,
        3,
        29,
        16,
        1,
        14,
        28,
        88,
        0,
        10,
        8
      ],
      "affected_routes": [
        0,
        2,
        5
      ],
      "features": {
        "cost_pressure": 0.18328370456544815,
        "priority_loss": 0.06666666666666667,
        "scarcity_pressure": 0.00020512996676729474,
        "coupling_pressure": 0.4643534381281642,
        "mobility_opportunity": 0.751820427861591,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 3.7580764894741185,
      "metadata": {
        "target_k": 18,
        "seed_task": 5
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 10,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 5,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 5,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "diversified_insertion": 6,
        "bottleneck_insertion": 1,
        "regret_insertion": 10,
        "scarcity_first_insertion": 1
      },
      "unassigned_before": 27,
      "unassigned_after": 9,
      "inserted_count": 18,
      "failed_count": 9,
      "tasks_analyzed": 342,
      "positions_generated": 301,
      "positions_strict_checked": 301,
      "strict_feasible_positions": 301,
      "failure_breakdown": {
        "no_candidate": 151,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 25,
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
          "task_id": 46,
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
          "task_id": 58,
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
          "task_id": 59,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 60,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 427.9233,
      "operator": "diversified_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69503.21817816769
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69503.21817816769
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69503.21817816769
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69503.21817816769
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69503.21817816769
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69503.21817816769
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69467.72852906045
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          69742.31347338314
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71814.87131000697
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          73605.21244374654
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          73605.21244374654
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          73605.21244374654
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          72367.30451323718
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71816.16404517922
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71655.99199583898
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71655.99199583898
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71655.99199583898
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          71655.99199583898
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68656.81996085476
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          69301.62484117674
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67325.37628509657
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66543.799531659
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66543.799531659
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67584.78081210039
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67584.78081210039
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67584.78081210039
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67584.78081210039
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67869.30270868566
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68514.68957332545
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68514.68957332545
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68514.68957332545
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68514.68957332545
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68725.9260532552
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67588.04564899536
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66743.95570063934
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          69467.72852906045
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          68136.04529586386
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67842.14039391452
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65358.75675433927
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64265.517777807785
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          64539.78371983703
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65383.87366819306
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65492.64765175974
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65267.27132062185
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68153.91271770246
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68040.37494254409
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          68853.45020081838
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67038.85147538211
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66829.8492791518
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67721.55388000506
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67721.55388000506
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67640.45604392656
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          67345.60237694303
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          68136.04529586386
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 12.0,
      "worst_task_removal": 20.0,
      "related_cluster_removal": 13.0,
      "critical_block_removal": 13.0,
      "route_rebalance_removal": 11.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1729.0,
      "tasks_reinserted": 1204.0,
      "tasks_left_unassigned": 525.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 8266.0,
        "no_feasible": 4.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.9657142857142857,
          "worst_task_removal": 0.8400000000000001,
          "related_cluster_removal": 0.8114285714285715,
          "critical_block_removal": 0.8400000000000001,
          "route_rebalance_removal": 0.8300000000000001
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 10.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.158494538843133,
          "worst_task_removal": 1.5603048719272223,
          "related_cluster_removal": 1.016705611792114,
          "critical_block_removal": 1.0434387559088079,
          "route_rebalance_removal": 1.0341084054963412
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 10.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 69,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 20,
          "related_cluster_removal": 13,
          "critical_block_removal": 13,
          "route_rebalance_removal": 11
        },
        "removed_task_count_avg": 17.710145
      },
      "repair": {
        "candidate_tasks_total": 1729,
        "tasks_reinserted": 1204,
        "tasks_left_unassigned": 525,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 8266,
          "no_feasible": 4
        }
      },
      "trial_flow": {
        "candidate_trials": 69,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 69,
        "acceptance_rejected": 11,
        "accepted_trials": 58,
        "best_improved_trials": 2
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 58,
    "rejected_trial_count": 11
  }
}
```

### #088 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 005

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 69,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 12,
      "worst_task_removal": 20,
      "related_cluster_removal": 13,
      "critical_block_removal": 13,
      "route_rebalance_removal": 11
    },
    "removed_task_count_avg": 17.710145
  },
  "repair": {
    "candidate_tasks_total": 1729,
    "tasks_reinserted": 1204,
    "tasks_left_unassigned": 525,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 8266,
      "no_feasible": 4
    }
  },
  "trial_flow": {
    "candidate_trials": 69,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 69,
    "acceptance_rejected": 11,
    "accepted_trials": 58,
    "best_improved_trials": 2
  },
  "rejection_reasons": {}
}
```

### #089 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 005

```json
{
  "verification_id": "V6",
  "contract_id": "C002",
  "decision_id": "D6",
  "manifest_id": "R6",
  "trace_id": "X6",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 1.0,
      "unassigned_count": 3.0,
      "energy_total": -2157.6158012246597
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
  "dominant_blocker": "none",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved"
  ],
  "trace": {
    "trace_id": "X6",
    "kind": "alns",
    "iters": 69,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 20,
        "related_cluster_removal": 13,
        "critical_block_removal": 13,
        "route_rebalance_removal": 11
      },
      "removed_task_count_avg": 17.710145
    },
    "repair": {
      "candidate_tasks_total": 1729,
      "tasks_reinserted": 1204,
      "tasks_left_unassigned": 525,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 8266,
        "no_feasible": 4
      }
    },
    "trial_flow": {
      "candidate_trials": 69,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 69,
      "acceptance_rejected": 11,
      "accepted_trials": 58,
      "best_improved_trials": 2
    },
    "rejection_reasons": {}
  }
}
```

### #090 [MEM] MEMORY_UPDATE | C002 / SOLVER 005

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M6",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O6",
  "decision_id": "D6",
  "manifest_id": "R6",
  "trace_id": "X6",
  "verification_id": "V6",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:4"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": 1.0,
      "unassigned_count": 3.0,
      "energy_total": -2157.6158012246597
    }
  },
  "manifest": {
    "manifest_id": "R6",
    "source_decision_id": "D6",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 10,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 5,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 5,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 5,
          "scarcity_protection": 5
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 4,
        "threshold": 4.0,
        "worsening_allowance": 0.2
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X6",
    "kind": "alns",
    "iters": 69,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 12,
        "worst_task_removal": 20,
        "related_cluster_removal": 13,
        "critical_block_removal": 13,
        "route_rebalance_removal": 11
      },
      "removed_task_count_avg": 17.710145
    },
    "repair": {
      "candidate_tasks_total": 1729,
      "tasks_reinserted": 1204,
      "tasks_left_unassigned": 525,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 8266,
        "no_feasible": 4
      }
    },
    "trial_flow": {
      "candidate_trials": 69,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 69,
      "acceptance_rejected": 11,
      "accepted_trials": 58,
      "best_improved_trials": 2
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V6",
    "contract_id": "C002",
    "decision_id": "D6",
    "manifest_id": "R6",
    "trace_id": "X6",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 1.0,
        "unassigned_count": 3.0,
        "energy_total": -2157.6158012246597
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
    "dominant_blocker": "none",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved"
    ],
    "trace": {
      "trace_id": "X6",
      "kind": "alns",
      "iters": 69,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 12,
          "worst_task_removal": 20,
          "related_cluster_removal": 13,
          "critical_block_removal": 13,
          "route_rebalance_removal": 11
        },
        "removed_task_count_avg": 17.710145
      },
      "repair": {
        "candidate_tasks_total": 1729,
        "tasks_reinserted": 1204,
        "tasks_left_unassigned": 525,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 8266,
          "no_feasible": 4
        }
      },
      "trial_flow": {
        "candidate_trials": 69,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 69,
        "acceptance_rejected": 11,
        "accepted_trials": 58,
        "best_improved_trials": 2
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #091 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 005

```json
{
  "contract_id": "C002",
  "solver_actions": 4,
  "time_used_sec": 150.0,
  "iters_used": 282,
  "verification_ids": [
    "V3",
    "V4",
    "V5",
    "V6"
  ],
  "intent_status_counts": {
    "achieved": 4
  },
  "dominant_blocker_counts": {
    "none": 4
  },
  "metric_delta_total": {
    "missed_priority": -9.0,
    "unassigned_count": -7.0,
    "energy_total": -3795.6286030984047
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #092 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 005

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #093 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 006

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O7",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 6,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 4,
      "time_sec": 150.0,
      "iters": 1718,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 9.0,
        "unassigned_count": 9.0,
        "energy_total": 67345.60237694303,
        "total_distance": 61371.11179257796,
        "makespan": 22007.377762869848,
        "route_balance": 0.2565410446138187
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 9.0,
        "energy_total": 67372.16721086697,
        "total_distance": 61668.87181534817,
        "makespan": 22007.377762869848,
        "route_balance": 0.2508288397915017
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V6",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": 1.0,
      "unassigned_count": 3.0,
      "energy_total": -2157.6158012246597
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 69,
      "feasibility_rejected": 0,
      "accepted": 58,
      "best_improved": 2
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 9.0,
        "unassigned_count": 9.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M4",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
    },
    {
      "record_id": "M5",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
    },
    {
      "record_id": "M6",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
    }
  ]
}
```

</details>

### #094 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 006

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
    "observation_id": "O7",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 6,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 4,
        "time_sec": 150.0,
        "iters": 1718,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 9.0,
          "unassigned_count": 9.0,
          "energy_total": 67345.60237694303,
          "total_distance": 61371.11179257796,
          "makespan": 22007.377762869848,
          "route_balance": 0.2565410446138187
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 9.0,
          "energy_total": 67372.16721086697,
          "total_distance": 61668.87181534817,
          "makespan": 22007.377762869848,
          "route_balance": 0.2508288397915017
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V6",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 1.0,
        "unassigned_count": 3.0,
        "energy_total": -2157.6158012246597
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 69,
        "feasibility_rejected": 0,
        "accepted": 58,
        "best_improved": 2
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 9.0,
          "unassigned_count": 9.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M4",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -4, unassigned_count -2, energy_total +474, accepted 51/63, blocker none"
      },
      {
        "record_id": "M5",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
      },
      {
        "record_id": "M6",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
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
                "T_scarce_unassigned",
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

### #095 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 006

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 10
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 10
        },
        {
          "name": "scarcity_protection",
          "score": 10
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "greedy_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 10
        },
        {
          "name": "scarcity_pressure",
          "score": 10
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 10
        },
        {
          "name": "insert_cost",
          "score": 10
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 5
    },
    "explanation": {
      "reason": "Replicate successful strategy from M4: worst_task_removal + priority_loss + future_slack + sa:5, targeting unassigned_priority with recommended signals to reduce missed_priority."
    }
  }
}
```

</details>

### #096 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 006

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 10
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 10
        },
        {
          "name": "scarcity_protection",
          "score": 10
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "greedy_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 10
        },
        {
          "name": "scarcity_pressure",
          "score": 10
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 10
        },
        {
          "name": "insert_cost",
          "score": 10
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 5
    },
    "explanation": {
      "reason": "Replicate successful strategy from M4: worst_task_removal + priority_loss + future_slack + sa:5, targeting unassigned_priority with recommended signals to reduce missed_priority."
    }
  }
}
```

### #097 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 006

```json
{
  "manifest_id": "R7",
  "source_decision_id": "D7",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 10,
        "scarcity_first_insertion": 2,
        "regret_insertion": 2,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 10,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 10,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 10,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 10,
        "scarcity_protection": 10
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 5,
      "threshold": 5.0,
      "worsening_allowance": 0.25
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.regret_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #098 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 006

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 10,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 10,
      "scarcity_protection": 10
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 10,
      "scarcity_first_insertion": 2,
      "regret_insertion": 2,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 10,
      "scarcity_pressure": 10,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 10,
      "future_slack": 10,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 5,
    "accept_level": 0.25,
    "exploration_score": 5.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #099 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 006

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 429
}
```

### #100 [SOLVER] SOLVER_RESULT | C002 / SOLVER 006

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      8.0,
      64996.23224987785
    ],
    "quality_summary": {
      "missed_priority": 8.0,
      "unassigned_count": 7.0,
      "energy_total": 64996.23224987785,
      "total_distance": 59372.17327882307,
      "makespan": 22007.377762869848,
      "route_balance": 0.23186944788008412
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
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 10,
          "scarcity_protection": 10
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 10,
          "scarcity_first_insertion": 2,
          "regret_insertion": 2,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 10,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 10,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 5,
        "accept_level": 0.25,
        "exploration_score": 5.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 76,
    "actual_iters_used": 76,
    "actual_time_used_sec": 38.17738939999981,
    "best_update_count": 8,
    "best_update_iters": [
      1,
      8,
      10,
      11,
      26,
      27,
      29,
      44
    ],
    "best_update_lex_keys": [
      [
        9.0,
        65127.77287545939
      ],
      [
        9.0,
        64821.28316284199
      ],
      [
        9.0,
        64049.89790690675
      ],
      [
        9.0,
        63765.376010321495
      ],
      [
        8.0,
        64723.329890372755
      ],
      [
        8.0,
        63611.49343462049
      ],
      [
        8.0,
        62339.76950957247
      ],
      [
        7.0,
        63085.92916812443
      ]
    ],
    "first_best_iter": 1,
    "last_best_iter": 44,
    "plateau_iters_after_last_update": 32,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 0,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "related_cluster_removal",
      "shape": "cluster",
      "task_ids": [
        32,
        16,
        10,
        0,
        19,
        7,
        14,
        99,
        27,
        83,
        28,
        87,
        3,
        11,
        50,
        5,
        6,
        18,
        15
      ],
      "affected_routes": [
        0,
        1,
        5
      ],
      "features": {
        "cost_pressure": 0.39483093454022056,
        "priority_loss": 0.5384615384615384,
        "scarcity_pressure": 0.5384615384615389,
        "coupling_pressure": 0.3357691173615551,
        "mobility_opportunity": 0.0,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": -5.384615384615389,
      "metadata": {
        "target_k": 19,
        "seed_task": 32
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 10,
        "scarcity_first_insertion": 2,
        "regret_insertion": 2,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 10,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 10,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "regret_insertion": 4,
        "greedy_insertion": 10,
        "scarcity_first_insertion": 1,
        "diversified_insertion": 2,
        "bottleneck_insertion": 2
      },
      "unassigned_before": 26,
      "unassigned_after": 7,
      "inserted_count": 19,
      "failed_count": 7,
      "tasks_analyzed": 330,
      "positions_generated": 290,
      "positions_strict_checked": 290,
      "strict_feasible_positions": 290,
      "failure_breakdown": {
        "no_candidate": 117,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 25,
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
          "task_id": 46,
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
          "task_id": 59,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 60,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 63,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 430.217,
      "operator": "greedy_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65127.77287545939
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65127.77287545939
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          65026.0474978257
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          64996.58387971225
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          64996.58387971225
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          63944.99825086735
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          63944.99825086735
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64821.28316284199
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64821.28316284199
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65296.132900789824
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64821.28316284199
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64049.89790690675
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64049.89790690675
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          63765.376010321495
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          63765.376010321495
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65321.32151653283
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65321.32151653283
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64723.329890372755
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64723.329890372755
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63611.49343462049
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          63611.49343462049
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63611.49343462049
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          63611.49343462049
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62339.76950957247
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62599.47845350863
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62599.47845350863
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63823.71005100893
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63806.92825972712
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62783.86304758176
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63965.40321883399
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63965.40321883399
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.123559936306
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.123559936306
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63952.38849492484
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 70,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 71,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 72,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 73,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 74,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 75,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 76,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 23.0,
      "worst_task_removal": 19.0,
      "related_cluster_removal": 9.0,
      "critical_block_removal": 11.0,
      "route_rebalance_removal": 14.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1973.0,
      "tasks_reinserted": 1319.0,
      "tasks_left_unassigned": 654.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10222.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.8250000000000001,
          "worst_task_removal": 1.1280000000000001,
          "related_cluster_removal": 1.1466666666666667,
          "critical_block_removal": 0.8400000000000001,
          "route_rebalance_removal": 1.1555555555555554
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 10.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.0294327018993874,
          "worst_task_removal": 1.9463987846063942,
          "related_cluster_removal": 1.3177571757279425,
          "critical_block_removal": 1.0434387559088079,
          "route_rebalance_removal": 1.3254111547145038
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 10.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 2.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 76,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 23,
          "worst_task_removal": 19,
          "related_cluster_removal": 9,
          "critical_block_removal": 11,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 17.486842
      },
      "repair": {
        "candidate_tasks_total": 1973,
        "tasks_reinserted": 1319,
        "tasks_left_unassigned": 654,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 10222
        }
      },
      "trial_flow": {
        "candidate_trials": 76,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 76,
        "acceptance_rejected": 14,
        "accepted_trials": 62,
        "best_improved_trials": 8
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 62,
    "rejected_trial_count": 14
  }
}
```

### #101 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 006

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 76,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 23,
      "worst_task_removal": 19,
      "related_cluster_removal": 9,
      "critical_block_removal": 11,
      "route_rebalance_removal": 14
    },
    "removed_task_count_avg": 17.486842
  },
  "repair": {
    "candidate_tasks_total": 1973,
    "tasks_reinserted": 1319,
    "tasks_left_unassigned": 654,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 10222
    }
  },
  "trial_flow": {
    "candidate_trials": 76,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 76,
    "acceptance_rejected": 14,
    "accepted_trials": 62,
    "best_improved_trials": 8
  },
  "rejection_reasons": {}
}
```

### #102 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 006

```json
{
  "verification_id": "V7",
  "contract_id": "C002",
  "decision_id": "D7",
  "manifest_id": "R7",
  "trace_id": "X7",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": -1.0,
      "unassigned_count": -2.0,
      "energy_total": -2349.37012706518
    },
    "best_feasible": {
      "missed_priority": 0.0,
      "unassigned_count": -2.0,
      "energy_total": -4286.238042742545
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
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved",
    "best_feasible_improved"
  ],
  "trace": {
    "trace_id": "X7",
    "kind": "alns",
    "iters": 76,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 23,
        "worst_task_removal": 19,
        "related_cluster_removal": 9,
        "critical_block_removal": 11,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 17.486842
    },
    "repair": {
      "candidate_tasks_total": 1973,
      "tasks_reinserted": 1319,
      "tasks_left_unassigned": 654,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10222
      }
    },
    "trial_flow": {
      "candidate_trials": 76,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 76,
      "acceptance_rejected": 14,
      "accepted_trials": 62,
      "best_improved_trials": 8
    },
    "rejection_reasons": {}
  }
}
```

### #103 [MEM] MEMORY_UPDATE | C002 / SOLVER 006

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M7",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O7",
  "decision_id": "D7",
  "manifest_id": "R7",
  "trace_id": "X7",
  "verification_id": "V7",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:5"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": -1.0,
      "unassigned_count": -2.0,
      "energy_total": -2349.37012706518
    }
  },
  "manifest": {
    "manifest_id": "R7",
    "source_decision_id": "D7",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 10,
          "scarcity_first_insertion": 2,
          "regret_insertion": 2,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 10,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 10,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 10,
          "scarcity_protection": 10
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 5,
        "threshold": 5.0,
        "worsening_allowance": 0.25
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.regret_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X7",
    "kind": "alns",
    "iters": 76,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 23,
        "worst_task_removal": 19,
        "related_cluster_removal": 9,
        "critical_block_removal": 11,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 17.486842
    },
    "repair": {
      "candidate_tasks_total": 1973,
      "tasks_reinserted": 1319,
      "tasks_left_unassigned": 654,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10222
      }
    },
    "trial_flow": {
      "candidate_trials": 76,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 76,
      "acceptance_rejected": 14,
      "accepted_trials": 62,
      "best_improved_trials": 8
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V7",
    "contract_id": "C002",
    "decision_id": "D7",
    "manifest_id": "R7",
    "trace_id": "X7",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": -1.0,
        "unassigned_count": -2.0,
        "energy_total": -2349.37012706518
      },
      "best_feasible": {
        "missed_priority": 0.0,
        "unassigned_count": -2.0,
        "energy_total": -4286.238042742545
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
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved",
      "best_feasible_improved"
    ],
    "trace": {
      "trace_id": "X7",
      "kind": "alns",
      "iters": 76,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 23,
          "worst_task_removal": 19,
          "related_cluster_removal": 9,
          "critical_block_removal": 11,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 17.486842
      },
      "repair": {
        "candidate_tasks_total": 1973,
        "tasks_reinserted": 1319,
        "tasks_left_unassigned": 654,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 10222
        }
      },
      "trial_flow": {
        "candidate_trials": 76,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 76,
        "acceptance_rejected": 14,
        "accepted_trials": 62,
        "best_improved_trials": 8
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #104 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 006

```json
{
  "contract_id": "C002",
  "solver_actions": 5,
  "time_used_sec": 187.5,
  "iters_used": 358,
  "verification_ids": [
    "V3",
    "V4",
    "V5",
    "V6",
    "V7"
  ],
  "intent_status_counts": {
    "achieved": 5
  },
  "dominant_blocker_counts": {
    "none": 5
  },
  "metric_delta_total": {
    "missed_priority": -10.0,
    "unassigned_count": -9.0,
    "energy_total": -6144.998730163585
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #105 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 006

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #106 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 007

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O8",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 7,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 3,
      "time_sec": 112.5,
      "iters": 1642,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 8.0,
        "unassigned_count": 7.0,
        "energy_total": 64996.23224987785,
        "total_distance": 59372.17327882307,
        "makespan": 22007.377762869848,
        "route_balance": 0.23186944788008412
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 7.0,
        "energy_total": 63085.92916812443,
        "total_distance": 57706.15906485565,
        "makespan": 22007.377762869848,
        "route_balance": 0.23186944788008412
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V7",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": -1.0,
      "unassigned_count": -2.0,
      "energy_total": -2349.37012706518
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 76,
      "feasibility_rejected": 0,
      "accepted": 62,
      "best_improved": 8
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 8.0,
        "unassigned_count": 7.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M5",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
    },
    {
      "record_id": "M6",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
    },
    {
      "record_id": "M7",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
    }
  ]
}
```

</details>

### #107 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 007

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
    "observation_id": "O8",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 7,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 3,
        "time_sec": 112.5,
        "iters": 1642,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 8.0,
          "unassigned_count": 7.0,
          "energy_total": 64996.23224987785,
          "total_distance": 59372.17327882307,
          "makespan": 22007.377762869848,
          "route_balance": 0.23186944788008412
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 7.0,
          "energy_total": 63085.92916812443,
          "total_distance": 57706.15906485565,
          "makespan": 22007.377762869848,
          "route_balance": 0.23186944788008412
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V7",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": -1.0,
        "unassigned_count": -2.0,
        "energy_total": -2349.37012706518
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 76,
        "feasibility_rejected": 0,
        "accepted": 62,
        "best_improved": 8
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 8.0,
          "unassigned_count": 7.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M5",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count -3, energy_total +542, accepted 56/75, blocker none"
      },
      {
        "record_id": "M6",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
      },
      {
        "record_id": "M7",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
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
                "T_scarce_unassigned",
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

### #108 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 007

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 7
        }
      ],
      "intensity_score": 6
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 8
        },
        {
          "name": "scarcity_pressure",
          "score": 6
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 5
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Continue improving coverage on T_unassigned_priority using proven destroy (worst_task_removal) and insertion (regret) with signals from memory and recommendations; moderate removal intensity and SA acceptance to balance exploration."
    }
  }
}
```

</details>

### #109 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 007

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 8
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 7
        },
        {
          "name": "scarcity_protection",
          "score": 7
        }
      ],
      "intensity_score": 6
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 8
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 8
        },
        {
          "name": "scarcity_pressure",
          "score": 6
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 7
        },
        {
          "name": "insert_cost",
          "score": 5
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 4
    },
    "explanation": {
      "strategy": "Continue improving coverage on T_unassigned_priority using proven destroy (worst_task_removal) and insertion (regret) with signals from memory and recommendations; moderate removal intensity and SA acceptance to balance exploration."
    }
  }
}
```

### #110 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 007

```json
{
  "manifest_id": "R8",
  "source_decision_id": "D8",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 8,
        "scarcity_pressure": 6,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 5,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 8,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 7,
        "scarcity_protection": 7
      },
      "intensity_score": 6,
      "remove_ratio": 0.22999999999999998
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 4,
      "threshold": 4.0,
      "worsening_allowance": 0.2
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #111 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 007

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 8,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 7,
      "scarcity_protection": 7
    },
    "intensity_score": 6,
    "remove_ratio": 0.22999999999999998
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 2,
      "regret_insertion": 8,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 8,
      "scarcity_pressure": 6,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 5,
      "future_slack": 7,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 4,
    "accept_level": 0.2,
    "exploration_score": 4.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #112 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 007

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 547
}
```

### #113 [SOLVER] SOLVER_RESULT | C002 / SOLVER 007

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      11.0,
      63871.387416660626
    ],
    "quality_summary": {
      "missed_priority": 11.0,
      "unassigned_count": 11.0,
      "energy_total": 63871.387416660626,
      "total_distance": 58241.49517519718,
      "makespan": 22007.377762869848,
      "route_balance": 0.26801933577250703
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
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 7
        },
        "intensity_score": 6,
        "remove_ratio": 0.22999999999999998
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 8,
          "scarcity_pressure": 6,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 5,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 4,
        "accept_level": 0.2,
        "exploration_score": 4.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 62,
    "actual_iters_used": 62,
    "actual_time_used_sec": 38.01232289999825,
    "best_update_count": 0,
    "best_update_iters": [],
    "best_update_lex_keys": [],
    "first_best_iter": null,
    "last_best_iter": null,
    "plateau_iters_after_last_update": 62,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 0,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "worst_task_removal",
      "shape": "task_set",
      "task_ids": [
        13,
        50,
        0,
        28,
        63,
        74,
        97,
        81,
        1,
        3,
        6,
        8,
        15,
        17,
        26,
        33,
        37,
        39,
        78,
        80
      ],
      "affected_routes": [
        0,
        1,
        2,
        3,
        4,
        5
      ],
      "features": {
        "cost_pressure": 1.0,
        "priority_loss": 1.0,
        "scarcity_pressure": 0.42524555248971885,
        "coupling_pressure": 1.0,
        "mobility_opportunity": 0.1256781674699377,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": -2.096971695138468,
      "metadata": {
        "target_k": 20
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 8,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 8,
        "scarcity_pressure": 6,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 5,
        "future_slack": 7,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "scarcity_first_insertion": 5,
        "regret_insertion": 9,
        "bottleneck_insertion": 5,
        "greedy_insertion": 1
      },
      "unassigned_before": 31,
      "unassigned_after": 11,
      "inserted_count": 20,
      "failed_count": 11,
      "tasks_analyzed": 441,
      "positions_generated": 354,
      "positions_strict_checked": 354,
      "strict_feasible_positions": 353,
      "failure_breakdown": {
        "no_candidate": 218,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
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
          "task_id": 25,
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
          "task_id": 46,
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
          "task_id": 58,
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
          "task_id": 59,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 516.6148,
      "operator": "regret_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66375.77882397948
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65314.28179694811
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66315.15349844735
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66315.15349844735
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66315.15349844735
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66315.15349844735
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66516.96036814695
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          66516.96036814695
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66582.93645612228
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66370.12729163494
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66370.12729163494
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66370.12729163494
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66219.44188006019
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66219.44188006019
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66219.44188006019
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66214.21812504937
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66734.79344746392
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66734.79344746392
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66421.6458489286
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66421.6458489286
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66421.6458489286
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66560.13586548179
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66808.54309505688
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66808.54309505688
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          66808.54309505688
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          68980.28307729182
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67165.90489341416
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67949.4369481989
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65736.41043298152
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65736.41043298152
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65736.41043298152
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66250.85669209585
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65736.41043298152
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65451.888536396254
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65451.888536396254
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65451.888536396254
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65451.888536396254
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65451.888536396254
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65992.51962606443
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65992.51962606443
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65841.83421448966
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65841.83421448966
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65841.83421448966
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66302.10541451615
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65178.46919485148
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65178.46919485148
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          63574.25122610898
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          63571.15193236685
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          63571.15193236685
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          64860.6409755988
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65348.58800240015
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65118.66363987109
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64996.23224987785
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 10.0,
      "worst_task_removal": 14.0,
      "related_cluster_removal": 14.0,
      "critical_block_removal": 12.0,
      "route_rebalance_removal": 12.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1744.0,
      "tasks_reinserted": 1159.0,
      "tasks_left_unassigned": 585.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9442.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.8177777777777778,
          "worst_task_removal": 0.8366666666666667,
          "related_cluster_removal": 0.8333333333333334,
          "critical_block_removal": 0.8363636363636364,
          "route_rebalance_removal": 0.8320000000000001
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 8.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.0226663771052988,
          "worst_task_removal": 1.471251256719183,
          "related_cluster_removal": 1.0372216288141305,
          "critical_block_removal": 1.0400491312068205,
          "route_rebalance_removal": 1.0359767137602578
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 8.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 62,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 10,
          "worst_task_removal": 14,
          "related_cluster_removal": 14,
          "critical_block_removal": 12,
          "route_rebalance_removal": 12
        },
        "removed_task_count_avg": 18.919355
      },
      "repair": {
        "candidate_tasks_total": 1744,
        "tasks_reinserted": 1159,
        "tasks_left_unassigned": 585,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 9442
        }
      },
      "trial_flow": {
        "candidate_trials": 62,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 62,
        "acceptance_rejected": 12,
        "accepted_trials": 50,
        "best_improved_trials": 0
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 50,
    "rejected_trial_count": 12
  }
}
```

### #114 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 007

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 62,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 10,
      "worst_task_removal": 14,
      "related_cluster_removal": 14,
      "critical_block_removal": 12,
      "route_rebalance_removal": 12
    },
    "removed_task_count_avg": 18.919355
  },
  "repair": {
    "candidate_tasks_total": 1744,
    "tasks_reinserted": 1159,
    "tasks_left_unassigned": 585,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 9442
    }
  },
  "trial_flow": {
    "candidate_trials": 62,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 62,
    "acceptance_rejected": 12,
    "accepted_trials": 50,
    "best_improved_trials": 0
  },
  "rejection_reasons": {}
}
```

### #115 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 007

```json
{
  "verification_id": "V8",
  "contract_id": "C002",
  "decision_id": "D8",
  "manifest_id": "R8",
  "trace_id": "X8",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 3.0,
      "unassigned_count": 4.0,
      "energy_total": -1124.8448332172266
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
  "dominant_blocker": "none",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false
  },
  "event_tags": [
    "working_quality_improved"
  ],
  "trace": {
    "trace_id": "X8",
    "kind": "alns",
    "iters": 62,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 10,
        "worst_task_removal": 14,
        "related_cluster_removal": 14,
        "critical_block_removal": 12,
        "route_rebalance_removal": 12
      },
      "removed_task_count_avg": 18.919355
    },
    "repair": {
      "candidate_tasks_total": 1744,
      "tasks_reinserted": 1159,
      "tasks_left_unassigned": 585,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9442
      }
    },
    "trial_flow": {
      "candidate_trials": 62,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 62,
      "acceptance_rejected": 12,
      "accepted_trials": 50,
      "best_improved_trials": 0
    },
    "rejection_reasons": {}
  }
}
```

### #116 [MEM] MEMORY_UPDATE | C002 / SOLVER 007

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M8",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O8",
  "decision_id": "D8",
  "manifest_id": "R8",
  "trace_id": "X8",
  "verification_id": "V8",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:4"
  },
  "outcome_fingerprint": {
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "best_improved": false,
    "metric_delta": {
      "missed_priority": 3.0,
      "unassigned_count": 4.0,
      "energy_total": -1124.8448332172266
    }
  },
  "manifest": {
    "manifest_id": "R8",
    "source_decision_id": "D8",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 8,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 8,
          "scarcity_pressure": 6,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 5,
          "future_slack": 7,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 8,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 7,
          "scarcity_protection": 7
        },
        "intensity_score": 6,
        "remove_ratio": 0.22999999999999998
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 4,
        "threshold": 4.0,
        "worsening_allowance": 0.2
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X8",
    "kind": "alns",
    "iters": 62,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 10,
        "worst_task_removal": 14,
        "related_cluster_removal": 14,
        "critical_block_removal": 12,
        "route_rebalance_removal": 12
      },
      "removed_task_count_avg": 18.919355
    },
    "repair": {
      "candidate_tasks_total": 1744,
      "tasks_reinserted": 1159,
      "tasks_left_unassigned": 585,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 9442
      }
    },
    "trial_flow": {
      "candidate_trials": 62,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 62,
      "acceptance_rejected": 12,
      "accepted_trials": 50,
      "best_improved_trials": 0
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V8",
    "contract_id": "C002",
    "decision_id": "D8",
    "manifest_id": "R8",
    "trace_id": "X8",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "intent_status": "achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 3.0,
        "unassigned_count": 4.0,
        "energy_total": -1124.8448332172266
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
    "dominant_blocker": "none",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false
    },
    "event_tags": [
      "working_quality_improved"
    ],
    "trace": {
      "trace_id": "X8",
      "kind": "alns",
      "iters": 62,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 10,
          "worst_task_removal": 14,
          "related_cluster_removal": 14,
          "critical_block_removal": 12,
          "route_rebalance_removal": 12
        },
        "removed_task_count_avg": 18.919355
      },
      "repair": {
        "candidate_tasks_total": 1744,
        "tasks_reinserted": 1159,
        "tasks_left_unassigned": 585,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 9442
        }
      },
      "trial_flow": {
        "candidate_trials": 62,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 62,
        "acceptance_rejected": 12,
        "accepted_trials": 50,
        "best_improved_trials": 0
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #117 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 007

```json
{
  "contract_id": "C002",
  "solver_actions": 6,
  "time_used_sec": 225.0,
  "iters_used": 420,
  "verification_ids": [
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8"
  ],
  "intent_status_counts": {
    "achieved": 6
  },
  "dominant_blocker_counts": {
    "none": 6
  },
  "metric_delta_total": {
    "missed_priority": -7.0,
    "unassigned_count": -5.0,
    "energy_total": -7269.843563380811
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #118 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 007

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #119 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 008

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O9",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 8,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 2,
      "time_sec": 75.0,
      "iters": 1580,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 11.0,
        "unassigned_count": 11.0,
        "energy_total": 63871.387416660626,
        "total_distance": 58241.49517519718,
        "makespan": 22007.377762869848,
        "route_balance": 0.26801933577250703
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 7.0,
        "energy_total": 63085.92916812443,
        "total_distance": 57706.15906485565,
        "makespan": 22007.377762869848,
        "route_balance": 0.23186944788008412
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V8",
    "intent_status": "achieved",
    "dominant_blocker": "none",
    "metric_delta": {
      "missed_priority": 3.0,
      "unassigned_count": 4.0,
      "energy_total": -1124.8448332172266
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 62,
      "feasibility_rejected": 0,
      "accepted": 50,
      "best_improved": 0
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 11.0,
        "unassigned_count": 11.0
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M6",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
    },
    {
      "record_id": "M7",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
    },
    {
      "record_id": "M8",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +3, unassigned_count +4, energy_total -1.12e+03, accepted 50/62, blocker none"
    }
  ]
}
```

</details>

### #120 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 008

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
    "observation_id": "O9",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 8,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 2,
        "time_sec": 75.0,
        "iters": 1580,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 11.0,
          "unassigned_count": 11.0,
          "energy_total": 63871.387416660626,
          "total_distance": 58241.49517519718,
          "makespan": 22007.377762869848,
          "route_balance": 0.26801933577250703
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 7.0,
          "energy_total": 63085.92916812443,
          "total_distance": 57706.15906485565,
          "makespan": 22007.377762869848,
          "route_balance": 0.23186944788008412
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V8",
      "intent_status": "achieved",
      "dominant_blocker": "none",
      "metric_delta": {
        "missed_priority": 3.0,
        "unassigned_count": 4.0,
        "energy_total": -1124.8448332172266
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 62,
        "feasibility_rejected": 0,
        "accepted": 50,
        "best_improved": 0
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 11.0,
          "unassigned_count": 11.0
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M6",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +1, unassigned_count +3, energy_total -2.16e+03, accepted 58/69, blocker none"
      },
      {
        "record_id": "M7",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
      },
      {
        "record_id": "M8",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +3, unassigned_count +4, energy_total -1.12e+03, accepted 50/62, blocker none"
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
                "T_scarce_unassigned",
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

### #121 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 008

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {"name": "worst_task_removal", "score": 10}
      ],
      "signal_scores": [
        {"name": "mobility_opportunity", "score": 8},
        {"name": "scarcity_protection", "score": 8}
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {"name": "regret_insertion", "score": 10}
      ],
      "task_signal_scores": [
        {"name": "priority_loss", "score": 9},
        {"name": "scarcity_pressure", "score": 7}
      ],
      "position_signal_scores": [
        {"name": "future_slack", "score": 8},
        {"name": "insert_cost", "score": 6}
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 6
    },
    "explanation": {
      "strategy": "Target unassigned priority tasks using worst_task_removal to remove high-cost tasks, then reinsert with regret_insertion prioritizing priority_loss and scarcity_pressure signals, and position using future_slack and insert_cost to improve coverage and reduce energy. Use simulated annealing with moderate intensity to explore and accept improvements."
    }
  }
}
```

</details>

### #122 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 008

```json
{
  "solver_decision": {
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "destroy_control": {
      "operator_scores": [
        {
          "name": "worst_task_removal",
          "score": 10
        }
      ],
      "signal_scores": [
        {
          "name": "mobility_opportunity",
          "score": 8
        },
        {
          "name": "scarcity_protection",
          "score": 8
        }
      ],
      "intensity_score": 5
    },
    "insertion_control": {
      "operator_scores": [
        {
          "name": "regret_insertion",
          "score": 10
        }
      ],
      "task_signal_scores": [
        {
          "name": "priority_loss",
          "score": 9
        },
        {
          "name": "scarcity_pressure",
          "score": 7
        }
      ],
      "position_signal_scores": [
        {
          "name": "future_slack",
          "score": 8
        },
        {
          "name": "insert_cost",
          "score": 6
        }
      ]
    },
    "acceptance_control": {
      "mode": "sa",
      "intensity_score": 6
    },
    "explanation": {
      "strategy": "Target unassigned priority tasks using worst_task_removal to remove high-cost tasks, then reinsert with regret_insertion prioritizing priority_loss and scarcity_pressure signals, and position using future_slack and insert_cost to improve coverage and reduce energy. Use simulated annealing with moderate intensity to explore and accept improvements."
    }
  }
}
```

### #123 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 008

```json
{
  "manifest_id": "R9",
  "source_decision_id": "D9",
  "contract_id": "C002",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "insertion": {
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 10,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 8,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      }
    },
    "destroy": {
      "operator_weights": {
        "random_removal": 2,
        "worst_task_removal": 10,
        "related_cluster_removal": 2,
        "critical_block_removal": 2,
        "route_rebalance_removal": 2
      },
      "signal_weights": {
        "cost_pressure": 0,
        "coupling_pressure": 0,
        "route_balance_pressure": 0,
        "mobility_opportunity": 8,
        "scarcity_protection": 8
      },
      "intensity_score": 5,
      "remove_ratio": 0.2
    },
    "acceptance": {
      "mode": "sa",
      "intensity_score": 6,
      "threshold": 6.0,
      "worsening_allowance": 0.30000000000000004
    }
  },
  "defaults_applied": [
    "insertion.operator_weights.greedy_insertion=2",
    "insertion.operator_weights.scarcity_first_insertion=2",
    "insertion.operator_weights.bottleneck_insertion=2",
    "insertion.operator_weights.diversified_insertion=2",
    "insertion.task_signal_weights.regret_pressure=0",
    "insertion.task_signal_weights.bottleneck_pressure=0",
    "insertion.task_signal_weights.mobility_opportunity=0",
    "insertion.position_signal_weights.route_balance_gain=0",
    "insertion.position_signal_weights.local_coupling_penalty=0",
    "insertion.position_signal_weights.diversity_gain=0",
    "destroy.operator_weights.random_removal=2",
    "destroy.operator_weights.related_cluster_removal=2",
    "destroy.operator_weights.critical_block_removal=2",
    "destroy.operator_weights.route_rebalance_removal=2",
    "destroy.signal_weights.cost_pressure=0",
    "destroy.signal_weights.coupling_pressure=0",
    "destroy.signal_weights.route_balance_pressure=0"
  ],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #124 [COMP] COMPILED_SOLVER_POLICY | C002 / SOLVER 008

```json
{
  "destroy_policy": {
    "operator_weights": {
      "random_removal": 2,
      "worst_task_removal": 10,
      "related_cluster_removal": 2,
      "critical_block_removal": 2,
      "route_rebalance_removal": 2
    },
    "signal_weights": {
      "cost_pressure": 0,
      "coupling_pressure": 0,
      "route_balance_pressure": 0,
      "mobility_opportunity": 8,
      "scarcity_protection": 8
    },
    "intensity_score": 5,
    "remove_ratio": 0.2
  },
  "insertion_policy": {
    "operator_weights": {
      "greedy_insertion": 2,
      "scarcity_first_insertion": 2,
      "regret_insertion": 10,
      "bottleneck_insertion": 2,
      "diversified_insertion": 2
    },
    "task_signal_weights": {
      "priority_loss": 9,
      "scarcity_pressure": 7,
      "regret_pressure": 0,
      "bottleneck_pressure": 0,
      "mobility_opportunity": 0
    },
    "position_signal_weights": {
      "insert_cost": 6,
      "future_slack": 8,
      "route_balance_gain": 0,
      "local_coupling_penalty": 0,
      "diversity_gain": 0
    }
  },
  "acceptance_policy": {
    "mode": "sa",
    "intensity_score": 6,
    "accept_level": 0.30000000000000004,
    "exploration_score": 6.0
  },
  "reaction_factor": 0.2,
  "prior_mix_lambda": 0.25
}
```

### #125 [SOLVER] SOLVER_REQUEST | C002 / SOLVER 008

```json
{
  "time_limit_sec": 37.5,
  "max_iters": 790
}
```

### #126 [SOLVER] SOLVER_RESULT | C002 / SOLVER 008

```json
{
  "working_solution": {
    "is_feasible": true,
    "lex_key": [
      17.0,
      66664.64253074997
    ],
    "quality_summary": {
      "missed_priority": 17.0,
      "unassigned_count": 14.0,
      "energy_total": 66664.64253074997,
      "total_distance": 61327.379083336906,
      "makespan": 22007.377762869848,
      "route_balance": 0.2661749567967348
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
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 8,
          "scarcity_protection": 8
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 10,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 8,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 6,
        "accept_level": 0.30000000000000004,
        "exploration_score": 6.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 73,
    "actual_iters_used": 73,
    "actual_time_used_sec": 37.60012660000211,
    "best_update_count": 3,
    "best_update_iters": [
      29,
      31,
      38
    ],
    "best_update_lex_keys": [
      [
        10.0,
        66875.97570589242
      ],
      [
        10.0,
        66636.90944765175
      ],
      [
        10.0,
        66281.03427356566
      ]
    ],
    "first_best_iter": 29,
    "last_best_iter": 38,
    "plateau_iters_after_last_update": 35,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 1,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy.",
      "delta_soft": 0.23529411764705882,
      "temperature": 0.12060793656043428
    },
    "last_destroy_move": {
      "operator_name": "related_cluster_removal",
      "shape": "cluster",
      "task_ids": [
        76,
        82,
        74,
        69,
        75,
        78,
        68,
        73,
        79,
        80,
        81,
        83,
        77,
        8,
        86,
        14,
        15,
        10
      ],
      "affected_routes": [
        0,
        4,
        5
      ],
      "features": {
        "cost_pressure": 0.6233646641150107,
        "priority_loss": 0.4375,
        "scarcity_pressure": 0.3334265417392403,
        "coupling_pressure": 0.5375930140423701,
        "mobility_opportunity": 0.688393895173338,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": 2.839738827472782,
      "metadata": {
        "target_k": 18,
        "seed_task": 76
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 2,
        "scarcity_first_insertion": 2,
        "regret_insertion": 10,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 9,
        "scarcity_pressure": 7,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 6,
        "future_slack": 8,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "diversified_insertion": 2,
        "regret_insertion": 11,
        "scarcity_first_insertion": 1,
        "greedy_insertion": 2
      },
      "unassigned_before": 30,
      "unassigned_after": 14,
      "inserted_count": 16,
      "failed_count": 14,
      "tasks_analyzed": 374,
      "positions_generated": 230,
      "positions_strict_checked": 230,
      "strict_feasible_positions": 230,
      "failure_breakdown": {
        "no_candidate": 199,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
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
          "task_id": 22,
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
          "task_id": 25,
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
          "task_id": 26,
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
          "task_id": 58,
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
      "time_ms": 493.9154,
      "operator": "regret_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          64523.50473781536
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          64523.50473781536
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          64523.50473781536
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65892.67089944439
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          63871.387416660626
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          65029.59776572205
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          65029.59776572205
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          65029.59776572205
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          65029.59776572205
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          66756.54966443457
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          66591.53324413736
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          66907.23507600932
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          66907.23507600932
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65749.0247269479
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65598.33931537314
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65598.33931537314
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65598.33931537314
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65433.32289507594
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65433.32289507594
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 11.0,
        "current_lex_key": [
          11.0,
          65433.32289507594
        ],
        "best_feasible_objective": 11.0,
        "best_feasible_lex_key": [
          11.0,
          63871.387416660626
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66875.97570589242
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66875.97570589242
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66875.97570589242
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66875.97570589242
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66636.90944765175
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66636.90944765175
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66636.90944765175
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67490.31652570945
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67449.53524000163
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67449.53524000163
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67449.53524000163
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66636.90944765175
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67449.53524000163
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67799.95597213486
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67404.49296313178
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66334.49797169959
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68853.25531398584
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          68853.25531398584
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66953.72596029882
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66953.72596029882
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66953.72596029882
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          66953.72596029882
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          67645.3941393239
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68865.24353392483
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68865.24353392483
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68865.24353392483
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          69211.36034232427
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68947.09672047102
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          68068.67655578643
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67645.66464264797
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67645.66464264797
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67645.66464264797
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67645.66464264797
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67304.58158385441
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          67543.1687704063
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          65316.42650927922
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 12.0,
        "current_lex_key": [
          12.0,
          66133.3968620916
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 14.0,
        "current_lex_key": [
          14.0,
          68731.89909044188
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 70,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          68777.16308332303
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 71,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          68777.16308332303
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 72,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          65784.14884352096
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 73,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 17.0,
        "current_lex_key": [
          17.0,
          66664.64253074997
        ],
        "best_feasible_objective": 10.0,
        "best_feasible_lex_key": [
          10.0,
          66281.03427356566
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 19.0,
      "worst_task_removal": 17.0,
      "related_cluster_removal": 8.0,
      "critical_block_removal": 15.0,
      "route_rebalance_removal": 14.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1993.0,
      "tasks_reinserted": 1222.0,
      "tasks_left_unassigned": 771.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 11382.0,
        "no_feasible": 51.0
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
          "worst_task_removal": 10.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.189207115002721,
          "worst_task_removal": 1.7782794100389228,
          "related_cluster_removal": 1.189207115002721,
          "critical_block_removal": 1.189207115002721,
          "route_rebalance_removal": 1.189207115002721
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 2.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 10.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 73,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 19,
          "worst_task_removal": 17,
          "related_cluster_removal": 8,
          "critical_block_removal": 15,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 16.958904
      },
      "repair": {
        "candidate_tasks_total": 1993,
        "tasks_reinserted": 1222,
        "tasks_left_unassigned": 771,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 11382,
          "no_feasible": 51
        }
      },
      "trial_flow": {
        "candidate_trials": 73,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 73,
        "acceptance_rejected": 14,
        "accepted_trials": 59,
        "best_improved_trials": 3
      },
      "rejection_reasons": {}
    },
    "accepted_trial_count": 59,
    "rejected_trial_count": 14
  }
}
```

### #127 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 008

```json
{
  "trace_id": "",
  "kind": "alns",
  "iters": 73,
  "destroy": {
    "selected_operator_counts": {
      "random_removal": 19,
      "worst_task_removal": 17,
      "related_cluster_removal": 8,
      "critical_block_removal": 15,
      "route_rebalance_removal": 14
    },
    "removed_task_count_avg": 16.958904
  },
  "repair": {
    "candidate_tasks_total": 1993,
    "tasks_reinserted": 1222,
    "tasks_left_unassigned": 771,
    "dominant_repair_failure": "no_candidate",
    "repair_failure_reasons": {
      "no_candidate": 11382,
      "no_feasible": 51
    }
  },
  "trial_flow": {
    "candidate_trials": 73,
    "hard_filter_failed": 0,
    "feasibility_rejected": 0,
    "admissible_trials": 73,
    "acceptance_rejected": 14,
    "accepted_trials": 59,
    "best_improved_trials": 3
  },
  "rejection_reasons": {}
}
```

### #128 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 008

```json
{
  "verification_id": "V9",
  "contract_id": "C002",
  "decision_id": "D9",
  "manifest_id": "R9",
  "trace_id": "X9",
  "action": "run_alns",
  "target_id": "T_unassigned_priority",
  "intent_status": "not_achieved",
  "metric_delta": {
    "working": {
      "missed_priority": 6.0,
      "unassigned_count": 3.0,
      "energy_total": 2793.2551140893484
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
    "quality_problem": true
  },
  "event_tags": [
    "no_quality_gain"
  ],
  "trace": {
    "trace_id": "X9",
    "kind": "alns",
    "iters": 73,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 19,
        "worst_task_removal": 17,
        "related_cluster_removal": 8,
        "critical_block_removal": 15,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 16.958904
    },
    "repair": {
      "candidate_tasks_total": 1993,
      "tasks_reinserted": 1222,
      "tasks_left_unassigned": 771,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 11382,
        "no_feasible": 51
      }
    },
    "trial_flow": {
      "candidate_trials": 73,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 73,
      "acceptance_rejected": 14,
      "accepted_trials": 59,
      "best_improved_trials": 3
    },
    "rejection_reasons": {}
  }
}
```

### #129 [MEM] MEMORY_UPDATE | C002 / SOLVER 008

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M9",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O9",
  "decision_id": "D9",
  "manifest_id": "R9",
  "trace_id": "X9",
  "verification_id": "V9",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [
      "worst_task_removal",
      "critical_block_removal"
    ],
    "insert_task_top": [
      "priority_loss",
      "scarcity_pressure"
    ],
    "insert_pos_top": [
      "future_slack",
      "insert_cost"
    ],
    "acceptance": "sa:6"
  },
  "outcome_fingerprint": {
    "intent_status": "not_achieved",
    "dominant_blocker": "no_quality_gain",
    "best_improved": true,
    "metric_delta": {
      "missed_priority": 6.0,
      "unassigned_count": 3.0,
      "energy_total": 2793.2551140893484
    }
  },
  "manifest": {
    "manifest_id": "R9",
    "source_decision_id": "D9",
    "contract_id": "C002",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "insertion": {
        "operator_weights": {
          "greedy_insertion": 2,
          "scarcity_first_insertion": 2,
          "regret_insertion": 10,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 9,
          "scarcity_pressure": 7,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 6,
          "future_slack": 8,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "destroy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 8,
          "scarcity_protection": 8
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "acceptance": {
        "mode": "sa",
        "intensity_score": 6,
        "threshold": 6.0,
        "worsening_allowance": 0.30000000000000004
      }
    },
    "defaults_applied": [
      "insertion.operator_weights.greedy_insertion=2",
      "insertion.operator_weights.scarcity_first_insertion=2",
      "insertion.operator_weights.bottleneck_insertion=2",
      "insertion.operator_weights.diversified_insertion=2",
      "insertion.task_signal_weights.regret_pressure=0",
      "insertion.task_signal_weights.bottleneck_pressure=0",
      "insertion.task_signal_weights.mobility_opportunity=0",
      "insertion.position_signal_weights.route_balance_gain=0",
      "insertion.position_signal_weights.local_coupling_penalty=0",
      "insertion.position_signal_weights.diversity_gain=0",
      "destroy.operator_weights.random_removal=2",
      "destroy.operator_weights.related_cluster_removal=2",
      "destroy.operator_weights.critical_block_removal=2",
      "destroy.operator_weights.route_rebalance_removal=2",
      "destroy.signal_weights.cost_pressure=0",
      "destroy.signal_weights.coupling_pressure=0",
      "destroy.signal_weights.route_balance_pressure=0"
    ],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X9",
    "kind": "alns",
    "iters": 73,
    "destroy": {
      "selected_operator_counts": {
        "random_removal": 19,
        "worst_task_removal": 17,
        "related_cluster_removal": 8,
        "critical_block_removal": 15,
        "route_rebalance_removal": 14
      },
      "removed_task_count_avg": 16.958904
    },
    "repair": {
      "candidate_tasks_total": 1993,
      "tasks_reinserted": 1222,
      "tasks_left_unassigned": 771,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 11382,
        "no_feasible": 51
      }
    },
    "trial_flow": {
      "candidate_trials": 73,
      "hard_filter_failed": 0,
      "feasibility_rejected": 0,
      "admissible_trials": 73,
      "acceptance_rejected": 14,
      "accepted_trials": 59,
      "best_improved_trials": 3
    },
    "rejection_reasons": {}
  },
  "verification": {
    "verification_id": "V9",
    "contract_id": "C002",
    "decision_id": "D9",
    "manifest_id": "R9",
    "trace_id": "X9",
    "action": "run_alns",
    "target_id": "T_unassigned_priority",
    "intent_status": "not_achieved",
    "metric_delta": {
      "working": {
        "missed_priority": 6.0,
        "unassigned_count": 3.0,
        "energy_total": 2793.2551140893484
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
      "quality_problem": true
    },
    "event_tags": [
      "no_quality_gain"
    ],
    "trace": {
      "trace_id": "X9",
      "kind": "alns",
      "iters": 73,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 19,
          "worst_task_removal": 17,
          "related_cluster_removal": 8,
          "critical_block_removal": 15,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 16.958904
      },
      "repair": {
        "candidate_tasks_total": 1993,
        "tasks_reinserted": 1222,
        "tasks_left_unassigned": 771,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 11382,
          "no_feasible": 51
        }
      },
      "trial_flow": {
        "candidate_trials": 73,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 73,
        "acceptance_rejected": 14,
        "accepted_trials": 59,
        "best_improved_trials": 3
      },
      "rejection_reasons": {}
    }
  }
}
```

</details>

### #130 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 008

```json
{
  "contract_id": "C002",
  "solver_actions": 7,
  "time_used_sec": 262.5,
  "iters_used": 493,
  "verification_ids": [
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8",
    "V9"
  ],
  "intent_status_counts": {
    "achieved": 6,
    "not_achieved": 1
  },
  "dominant_blocker_counts": {
    "none": 6,
    "no_quality_gain": 1
  },
  "metric_delta_total": {
    "missed_priority": -1.0,
    "unassigned_count": -2.0,
    "energy_total": -4476.588449291463
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #131 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 008

```json
{
  "completion_status": "continue",
  "completion_reason": "conditions_not_met",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": false,
  "reason": "conditions_not_met",
  "result": "continue"
}
```

### #132 [OBS] SOLVER_OBSERVATION | C002 / SOLVER 009

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O10",
  "frame_type": "solver_step",
  "role": "solver",
  "step_index": 9,
  "contract_view": {
    "contract_id": "C002",
    "contract_type": "alns_search",
    "objective_layers": [
      "missed_priority",
      "unassigned_count",
      "energy_total"
    ],
    "feasibility_mode": "strict",
    "protected_metrics": [],
    "remaining_resources": {
      "actions": 1,
      "time_sec": 37.5,
      "iters": 1507,
      "min_actions_remaining": 0
    }
  },
  "state_digest": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 17.0,
        "unassigned_count": 14.0,
        "energy_total": 66664.64253074997,
        "total_distance": 61327.379083336906,
        "makespan": 22007.377762869848,
        "route_balance": 0.2661749567967348
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 7.0,
        "energy_total": 63085.92916812443,
        "total_distance": 57706.15906485565,
        "makespan": 22007.377762869848,
        "route_balance": 0.23186944788008412
      }
    }
  },
  "last_action_verification": {
    "exists": true,
    "verification_id": "V9",
    "intent_status": "not_achieved",
    "dominant_blocker": "no_quality_gain",
    "metric_delta": {
      "missed_priority": 6.0,
      "unassigned_count": 3.0,
      "energy_total": 2793.2551140893484
    },
    "debt_delta": {
      "energy": 0.0,
      "time_window": 0.0
    },
    "trace_counts": {
      "candidate_trials": 73,
      "feasibility_rejected": 0,
      "accepted": 59,
      "best_improved": 3
    }
  },
  "decision_targets": [
    {
      "target_id": "T_unassigned_priority",
      "kind": "unassigned_priority",
      "metric_pressure": {
        "missed_priority": 17.0,
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
      "target_id": "T_scarce_unassigned",
      "kind": "scarce_unassigned",
      "metric_pressure": {
        "count": 0
      },
      "recommended_controls": {
        "insertion_control.task_signal_scores": [
          "scarcity_pressure",
          "priority_loss"
        ],
        "insertion_control.position_signal_scores": [
          "future_slack"
        ],
        "destroy_control.signal_scores": [
          "scarcity_protection",
          "mobility_opportunity"
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
      "record_id": "M7",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
      "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
    },
    {
      "record_id": "M8",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
      "outcome": "missed_priority +3, unassigned_count +4, energy_total -1.12e+03, accepted 50/62, blocker none"
    },
    {
      "record_id": "M9",
      "target_kind": "unassigned_priority",
      "control_summary": "worst_task_removal + priority_loss + future_slack + sa:6",
      "outcome": "missed_priority +6, unassigned_count +3, energy_total +2.79e+03, accepted 59/73, blocker no_quality_gain"
    }
  ]
}
```

</details>

### #133 [PROMPT] SOLVER_PROMPT | C002 / SOLVER 009

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
    "observation_id": "O10",
    "frame_type": "solver_step",
    "role": "solver",
    "step_index": 9,
    "contract_view": {
      "contract_id": "C002",
      "contract_type": "alns_search",
      "objective_layers": [
        "missed_priority",
        "unassigned_count",
        "energy_total"
      ],
      "feasibility_mode": "strict",
      "protected_metrics": [],
      "remaining_resources": {
        "actions": 1,
        "time_sec": 37.5,
        "iters": 1507,
        "min_actions_remaining": 0
      }
    },
    "state_digest": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 17.0,
          "unassigned_count": 14.0,
          "energy_total": 66664.64253074997,
          "total_distance": 61327.379083336906,
          "makespan": 22007.377762869848,
          "route_balance": 0.2661749567967348
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 7.0,
          "energy_total": 63085.92916812443,
          "total_distance": 57706.15906485565,
          "makespan": 22007.377762869848,
          "route_balance": 0.23186944788008412
        }
      }
    },
    "last_action_verification": {
      "exists": true,
      "verification_id": "V9",
      "intent_status": "not_achieved",
      "dominant_blocker": "no_quality_gain",
      "metric_delta": {
        "missed_priority": 6.0,
        "unassigned_count": 3.0,
        "energy_total": 2793.2551140893484
      },
      "debt_delta": {
        "energy": 0.0,
        "time_window": 0.0
      },
      "trace_counts": {
        "candidate_trials": 73,
        "feasibility_rejected": 0,
        "accepted": 59,
        "best_improved": 3
      }
    },
    "decision_targets": [
      {
        "target_id": "T_unassigned_priority",
        "kind": "unassigned_priority",
        "metric_pressure": {
          "missed_priority": 17.0,
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
        "target_id": "T_scarce_unassigned",
        "kind": "scarce_unassigned",
        "metric_pressure": {
          "count": 0
        },
        "recommended_controls": {
          "insertion_control.task_signal_scores": [
            "scarcity_pressure",
            "priority_loss"
          ],
          "insertion_control.position_signal_scores": [
            "future_slack"
          ],
          "destroy_control.signal_scores": [
            "scarcity_protection",
            "mobility_opportunity"
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
        "record_id": "M7",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:5",
        "outcome": "missed_priority -1, unassigned_count -2, energy_total -2.35e+03, accepted 62/76, blocker none"
      },
      {
        "record_id": "M8",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:4",
        "outcome": "missed_priority +3, unassigned_count +4, energy_total -1.12e+03, accepted 50/62, blocker none"
      },
      {
        "record_id": "M9",
        "target_kind": "unassigned_priority",
        "control_summary": "worst_task_removal + priority_loss + future_slack + sa:6",
        "outcome": "missed_priority +6, unassigned_count +3, energy_total +2.79e+03, accepted 59/73, blocker no_quality_gain"
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
                "T_scarce_unassigned",
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

### #134 [RAW] SOLVER_RAW_OUTPUT | C002 / SOLVER 009

<details>
<summary>Open raw LLM output</summary>

```text
{
  "solver_decision": {
    "action": "request_supervisor_review",
    "target_id": "T_unassigned_priority",
    "explanation": {
      "reason": "Last action caused quality degradation (missed_priority +6). Need supervisor guidance to adjust strategy for reducing missed_priority."
    }
  }
}
```

</details>

### #135 [OK] SOLVER_VALIDATED_PAYLOAD | C002 / SOLVER 009

```json
{
  "solver_decision": {
    "action": "request_supervisor_review",
    "target_id": "T_unassigned_priority",
    "explanation": {
      "reason": "Last action caused quality degradation (missed_priority +6). Need supervisor guidance to adjust strategy for reducing missed_priority."
    }
  }
}
```

### #136 [COMP] RUNTIME_CONTROL_MANIFEST | C002 / SOLVER 009

```json
{
  "manifest_id": "R10",
  "source_decision_id": "D10",
  "contract_id": "C002",
  "action": "request_supervisor_review",
  "target_id": "T_unassigned_priority",
  "compiled": {
    "feasibility": {
      "mode": "strict",
      "limits": {}
    },
    "resource": {
      "min_actions": 1,
      "max_actions": 8,
      "max_iters": 2000,
      "max_time_sec": 300.0
    },
    "review_request": {
      "requested": 1
    }
  },
  "defaults_applied": [],
  "validation_report": {
    "all_candidate_names_valid": true,
    "all_operational_fields_consumed": true,
    "explanation_ignored_by_runtime": true
  }
}
```

### #137 [SOLVER] EXECUTION_TRACE | C002 / SOLVER 009

```json
{
  "trace_id": "",
  "kind": "review_request"
}
```

### #138 [AUDIT] OUTCOME_VERIFICATION | C002 / SOLVER 009

```json
{
  "verification_id": "V10",
  "contract_id": "C002",
  "decision_id": "D10",
  "manifest_id": "R10",
  "trace_id": "X10",
  "action": "request_supervisor_review",
  "target_id": "T_unassigned_priority",
  "intent_status": "not_applicable",
  "metric_delta": {
    "working": {},
    "best_feasible": {}
  },
  "debt_delta": {},
  "protected_metric_result": {
    "passed": true,
    "violations": []
  },
  "dominant_blocker": "solver_requested_review",
  "flow_diagnosis": {
    "candidate_problem": false,
    "hard_filter_problem": false,
    "feasibility_problem": false,
    "acceptance_problem": false,
    "quality_problem": false
  },
  "event_tags": [],
  "trace": {
    "trace_id": "X10",
    "kind": "review_request"
  }
}
```

### #139 [MEM] MEMORY_UPDATE | C002 / SOLVER 009

<details>
<summary>Open memory update</summary>

```json
{
  "record_id": "M10",
  "kind": "verified_action",
  "contract_id": "C002",
  "observation_id": "O10",
  "decision_id": "D10",
  "manifest_id": "R10",
  "trace_id": "X10",
  "verification_id": "V10",
  "target_id": "T_unassigned_priority",
  "target_kind": "unassigned_priority",
  "control_fingerprint": {
    "destroy_top": [],
    "insert_task_top": [],
    "insert_pos_top": [],
    "acceptance": ""
  },
  "outcome_fingerprint": {
    "intent_status": "not_applicable",
    "dominant_blocker": "solver_requested_review",
    "best_improved": false,
    "metric_delta": {}
  },
  "manifest": {
    "manifest_id": "R10",
    "source_decision_id": "D10",
    "contract_id": "C002",
    "action": "request_supervisor_review",
    "target_id": "T_unassigned_priority",
    "compiled": {
      "feasibility": {
        "mode": "strict",
        "limits": {}
      },
      "resource": {
        "min_actions": 1,
        "max_actions": 8,
        "max_iters": 2000,
        "max_time_sec": 300.0
      },
      "review_request": {
        "requested": 1
      }
    },
    "defaults_applied": [],
    "validation_report": {
      "all_candidate_names_valid": true,
      "all_operational_fields_consumed": true,
      "explanation_ignored_by_runtime": true
    }
  },
  "trace": {
    "trace_id": "X10",
    "kind": "review_request"
  },
  "verification": {
    "verification_id": "V10",
    "contract_id": "C002",
    "decision_id": "D10",
    "manifest_id": "R10",
    "trace_id": "X10",
    "action": "request_supervisor_review",
    "target_id": "T_unassigned_priority",
    "intent_status": "not_applicable",
    "metric_delta": {
      "working": {},
      "best_feasible": {}
    },
    "debt_delta": {},
    "protected_metric_result": {
      "passed": true,
      "violations": []
    },
    "dominant_blocker": "solver_requested_review",
    "flow_diagnosis": {
      "candidate_problem": false,
      "hard_filter_problem": false,
      "feasibility_problem": false,
      "acceptance_problem": false,
      "quality_problem": false
    },
    "event_tags": [],
    "trace": {
      "trace_id": "X10",
      "kind": "review_request"
    }
  }
}
```

</details>

### #140 [CONTRACT] CONTRACT_PROGRESS | C002 / SOLVER 009

```json
{
  "contract_id": "C002",
  "solver_actions": 8,
  "time_used_sec": 262.5,
  "iters_used": 493,
  "verification_ids": [
    "V3",
    "V4",
    "V5",
    "V6",
    "V7",
    "V8",
    "V9",
    "V10"
  ],
  "intent_status_counts": {
    "achieved": 6,
    "not_achieved": 1,
    "not_applicable": 1
  },
  "dominant_blocker_counts": {
    "none": 6,
    "no_quality_gain": 1,
    "solver_requested_review": 1
  },
  "metric_delta_total": {
    "missed_priority": -1.0,
    "unassigned_count": -2.0,
    "energy_total": -4476.588449291463
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ]
}
```

### #141 [CONTRACT] CONTRACT_COMPLETION_CHECK | C002 / SOLVER 009

```json
{
  "completion_status": "resource_exhausted",
  "completion_reason": "max_actions_reached",
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "completed": true,
  "reason": "max_actions_reached",
  "result": "resource_exhausted"
}
```

### #142 [CONTRACT] CONTRACT_END | C002

```json
{
  "completion": {
    "completion_status": "resource_exhausted",
    "completion_reason": "max_actions_reached",
    "condition_report": [
      {
        "condition_id": "s2",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 5,
        "passed": false
      },
      {
        "condition_id": "f2",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 8,
        "window": 1,
        "passed": false
      }
    ],
    "completed": true,
    "reason": "max_actions_reached",
    "result": "resource_exhausted"
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
    "progress": {
      "contract_id": "C002",
      "solver_actions": 8,
      "time_used_sec": 262.5,
      "iters_used": 493,
      "verification_ids": [
        "V3",
        "V4",
        "V5",
        "V6",
        "V7",
        "V8",
        "V9",
        "V10"
      ],
      "intent_status_counts": {
        "achieved": 6,
        "not_achieved": 1,
        "not_applicable": 1
      },
      "dominant_blocker_counts": {
        "none": 6,
        "no_quality_gain": 1,
        "solver_requested_review": 1
      },
      "metric_delta_total": {
        "missed_priority": -1.0,
        "unassigned_count": -2.0,
        "energy_total": -4476.588449291463
      },
      "condition_report": [
        {
          "condition_id": "s2",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 5,
          "passed": false
        },
        {
          "condition_id": "f2",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 8,
          "window": 1,
          "passed": false
        }
      ]
    },
    "completion": {
      "completion_status": "resource_exhausted",
      "completion_reason": "max_actions_reached",
      "condition_report": [
        {
          "condition_id": "s2",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 5,
          "passed": false
        },
        {
          "condition_id": "f2",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 8,
          "window": 1,
          "passed": false
        }
      ],
      "completed": true,
      "reason": "max_actions_reached",
      "result": "resource_exhausted"
    }
  }
}
```

### #143 [OBS] SUPERVISOR_REVIEW_OBSERVATION | C002

<details>
<summary>Open LLM observation input</summary>

```json
{
  "observation_id": "O_review_10",
  "frame_type": "supervisor_review",
  "role": "supervisor",
  "budget_caps": {
    "max_solver_actions": 0,
    "max_time_sec": 37.5,
    "max_iters": 1507
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
    "protected_metrics": []
  },
  "contract_completion": {
    "completion_status": "resource_exhausted",
    "completion_reason": "max_actions_reached",
    "condition_report": [
      {
        "condition_id": "s2",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 5,
        "passed": false
      },
      {
        "condition_id": "f2",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 8,
        "window": 1,
        "passed": false
      }
    ],
    "completed": true,
    "reason": "max_actions_reached",
    "result": "resource_exhausted"
  },
  "condition_report": [
    {
      "condition_id": "s2",
      "source": "missed_priority",
      "actual": null,
      "op": "==",
      "expected": 0,
      "window": 5,
      "passed": false
    },
    {
      "condition_id": "f2",
      "source": "total_actions",
      "actual": null,
      "op": ">=",
      "expected": 8,
      "window": 1,
      "passed": false
    }
  ],
  "stage_verification_summary": {
    "verification_ids": [
      "V3",
      "V4",
      "V5",
      "V6",
      "V7",
      "V8",
      "V9",
      "V10"
    ],
    "intent_status_counts": {
      "achieved": 6,
      "not_achieved": 1,
      "not_applicable": 1
    },
    "dominant_blocker_counts": {
      "none": 6,
      "no_quality_gain": 1,
      "solver_requested_review": 1
    },
    "last": {
      "exists": true,
      "verification_id": "V10",
      "intent_status": "not_applicable",
      "dominant_blocker": "solver_requested_review",
      "metric_delta": {},
      "debt_delta": {},
      "trace_counts": {
        "candidate_trials": 0,
        "feasibility_rejected": 0,
        "accepted": 0,
        "best_improved": 0
      }
    }
  },
  "solution_position": {
    "working": {
      "is_feasible": true,
      "quality": {
        "missed_priority": 17.0,
        "unassigned_count": 14.0,
        "energy_total": 66664.64253074997,
        "total_distance": 61327.379083336906,
        "makespan": 22007.377762869848,
        "route_balance": 0.2661749567967348
      },
      "debt": {
        "total": 0.0,
        "dominant_type": "time_window",
        "dominant_ratio": 0.0
      }
    },
    "best_feasible": {
      "exists": true,
      "quality": {
        "missed_priority": 7.0,
        "unassigned_count": 7.0,
        "energy_total": 63085.92916812443,
        "total_distance": 57706.15906485565,
        "makespan": 22007.377762869848,
        "route_balance": 0.23186944788008412
      }
    }
  },
  "usable_memory": [
    {
      "record_id": "M5",
      "contract_id": "C002",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M6",
      "contract_id": "C002",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M7",
      "contract_id": "C002",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M8",
      "contract_id": "C002",
      "intent_status": "achieved",
      "dominant_blocker": "none"
    },
    {
      "record_id": "M9",
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
    "max_time_sec_allowed": 37.5,
    "max_iters_allowed": 1507
  }
}
```

</details>

### #144 [PROMPT] SUPERVISOR_REVIEW_PROMPT | C002

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
    "observation_id": "O_review_10",
    "frame_type": "supervisor_review",
    "role": "supervisor",
    "budget_caps": {
      "max_solver_actions": 0,
      "max_time_sec": 37.5,
      "max_iters": 1507
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
      "protected_metrics": []
    },
    "contract_completion": {
      "completion_status": "resource_exhausted",
      "completion_reason": "max_actions_reached",
      "condition_report": [
        {
          "condition_id": "s2",
          "source": "missed_priority",
          "actual": null,
          "op": "==",
          "expected": 0,
          "window": 5,
          "passed": false
        },
        {
          "condition_id": "f2",
          "source": "total_actions",
          "actual": null,
          "op": ">=",
          "expected": 8,
          "window": 1,
          "passed": false
        }
      ],
      "completed": true,
      "reason": "max_actions_reached",
      "result": "resource_exhausted"
    },
    "condition_report": [
      {
        "condition_id": "s2",
        "source": "missed_priority",
        "actual": null,
        "op": "==",
        "expected": 0,
        "window": 5,
        "passed": false
      },
      {
        "condition_id": "f2",
        "source": "total_actions",
        "actual": null,
        "op": ">=",
        "expected": 8,
        "window": 1,
        "passed": false
      }
    ],
    "stage_verification_summary": {
      "verification_ids": [
        "V3",
        "V4",
        "V5",
        "V6",
        "V7",
        "V8",
        "V9",
        "V10"
      ],
      "intent_status_counts": {
        "achieved": 6,
        "not_achieved": 1,
        "not_applicable": 1
      },
      "dominant_blocker_counts": {
        "none": 6,
        "no_quality_gain": 1,
        "solver_requested_review": 1
      },
      "last": {
        "exists": true,
        "verification_id": "V10",
        "intent_status": "not_applicable",
        "dominant_blocker": "solver_requested_review",
        "metric_delta": {},
        "debt_delta": {},
        "trace_counts": {
          "candidate_trials": 0,
          "feasibility_rejected": 0,
          "accepted": 0,
          "best_improved": 0
        }
      }
    },
    "solution_position": {
      "working": {
        "is_feasible": true,
        "quality": {
          "missed_priority": 17.0,
          "unassigned_count": 14.0,
          "energy_total": 66664.64253074997,
          "total_distance": 61327.379083336906,
          "makespan": 22007.377762869848,
          "route_balance": 0.2661749567967348
        },
        "debt": {
          "total": 0.0,
          "dominant_type": "time_window",
          "dominant_ratio": 0.0
        }
      },
      "best_feasible": {
        "exists": true,
        "quality": {
          "missed_priority": 7.0,
          "unassigned_count": 7.0,
          "energy_total": 63085.92916812443,
          "total_distance": 57706.15906485565,
          "makespan": 22007.377762869848,
          "route_balance": 0.23186944788008412
        }
      }
    },
    "usable_memory": [
      {
        "record_id": "M5",
        "contract_id": "C002",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M6",
        "contract_id": "C002",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M7",
        "contract_id": "C002",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M8",
        "contract_id": "C002",
        "intent_status": "achieved",
        "dominant_blocker": "none"
      },
      {
        "record_id": "M9",
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
      "max_time_sec_allowed": 37.5,
      "max_iters_allowed": 1507
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
                          "scarce_unassigned",
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
                    "description": "A metric that may not worsen beyond the provided amount.",
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
                      "maximum": 1507
                    },
                    "max_time_sec": {
                      "type": "number",
                      "exclusiveMinimum": 0,
                      "maximum": 37.5
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
                            "description": "Supported source path read from OutcomeVerification/progress."
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
                            "description": "Supported source path read from OutcomeVerification/progress."
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

### #145 [RAW] SUPERVISOR_REVIEW_RAW_OUTPUT | C002

<details>
<summary>Open raw LLM output</summary>

```text
{
  "supervisor_decision": {
    "action": "stop_run",
    "contract_review": {
      "outcome_summary": "ALNS search contract C002 terminated after exhausting maximum solver actions (max_actions_reached). The solution improved from initial missed_priority=17 and unassigned_count=14 to best feasible values of 7 each, but the target of zero missed priority and minimal unassigned was not achieved. The last verification (V10) returned 'not_applicable' with a 'solver_requested_review' blocker, indicating the solver recognized no further progress was possible.",
      "main_lesson": "Given that the global budget caps have been exhausted (max_solver_actions=0), no further optimization can be performed. The best feasible solution is the final result."
    },
    "stop_explanation": "All solver actions have been exhausted (global max_solver_actions=0). No additional contracts can be issued because any search or recovery would require actions. The current best feasible solution (missed_priority=7, unassigned_count=7) is the best achievable under the resource constraints."
  }
}
```

</details>

### #146 [OK] SUPERVISOR_REVIEW_VALIDATED_PAYLOAD | C002

```json
{
  "supervisor_decision": {
    "action": "stop_run",
    "contract_review": {
      "outcome_summary": "ALNS search contract C002 terminated after exhausting maximum solver actions (max_actions_reached). The solution improved from initial missed_priority=17 and unassigned_count=14 to best feasible values of 7 each, but the target of zero missed priority and minimal unassigned was not achieved. The last verification (V10) returned 'not_applicable' with a 'solver_requested_review' blocker, indicating the solver recognized no further progress was possible.",
      "main_lesson": "Given that the global budget caps have been exhausted (max_solver_actions=0), no further optimization can be performed. The best feasible solution is the final result."
    },
    "stop_explanation": "All solver actions have been exhausted (global max_solver_actions=0). No additional contracts can be issued because any search or recovery would require actions. The current best feasible solution (missed_priority=7, unassigned_count=7) is the best achievable under the resource constraints."
  }
}
```

### #147 [FINAL] FINAL_RESULT

```json
{
  "summary": {
    "is_feasible": true,
    "lex_key": [
      7.0,
      63085.92916812443
    ],
    "quality_summary": {
      "missed_priority": 7.0,
      "unassigned_count": 7.0,
      "energy_total": 63085.92916812443,
      "total_distance": 57706.15906485565,
      "makespan": 22007.377762869848,
      "route_balance": 0.23186944788008412
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
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 10,
        "solver_calls": 8,
        "time_sec": 262.5,
        "iters": 493
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 12.0,
        "time_sec": 37.5,
        "iters": 1507.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 453.114202
  }
}
```


---

## Final Solution

```json
{
  "routes": {
    "0": [
      51,
      85,
      54,
      55,
      4,
      87,
      39,
      40,
      89,
      90,
      91,
      92,
      62,
      77,
      95,
      96,
      97,
      47,
      67,
      29,
      81
    ],
    "1": [
      84,
      35,
      36,
      38,
      21,
      22,
      43,
      93,
      11,
      12,
      13,
      98,
      99,
      27,
      49,
      30,
      33
    ],
    "2": [
      34,
      20,
      88,
      41,
      42,
      24,
      64,
      26,
      48,
      31
    ],
    "3": [
      52,
      53,
      2,
      37,
      56,
      57,
      58,
      23,
      9,
      44,
      45,
      65,
      66
    ],
    "4": [
      17,
      68,
      69,
      70,
      71,
      72,
      73,
      74,
      75,
      76,
      78,
      79,
      80,
      82
    ],
    "5": [
      0,
      18,
      19,
      3,
      5,
      6,
      7,
      8,
      61,
      10,
      94,
      14,
      15,
      16,
      28,
      50,
      83,
      32
    ]
  },
  "unassigned": [
    1,
    25,
    46,
    59,
    60,
    63,
    86
  ],
  "schedule": {
    "0:51": [
      355.6734210998373,
      574.5830050364287
    ],
    "0:85": [
      1699.970400733211,
      1877.2616448359518
    ],
    "0:54": [
      2589.799384637674,
      2828.6240246037473
    ],
    "0:55": [
      3094.6956885768295,
      3324.235156561147
    ],
    "0:4": [
      3847.6241759977393,
      3986.2438805670795
    ],
    "0:87": [
      4587.353724330949,
      4727.569917722721
    ],
    "0:39": [
      5359.425290840632,
      5560.976565104588
    ],
    "0:40": [
      5605.80004307104,
      5820.971973083092
    ],
    "0:89": [
      6259.258966933841,
      6566.397165424431
    ],
    "0:90": [
      6871.543217199576,
      7067.226949745339
    ],
    "0:91": [
      7713.116056537147,
      7774.67465018621
    ],
    "0:92": [
      8545.218855079145,
      8791.303388023422
    ],
    "0:62": [
      9232.416555711921,
      9344.187586614802
    ],
    "0:77": [
      10247.016341119572,
      10286.463099800127
    ],
    "0:95": [
      10718.7434947172,
      10826.436104607412
    ],
    "0:96": [
      10912.440560790654,
      10931.998402568463
    ],
    "0:97": [
      11140.74288038423,
      11378.729871817628
    ],
    "0:47": [
      11881.705039363704,
      12121.05895231105
    ],
    "0:67": [
      13455.15147855146,
      13747.540341857926
    ],
    "0:29": [
      14348.923338079558,
      14375.775968248847
    ],
    "0:81": [
      14931.920010866143,
      15151.896067681486
    ],
    "1:84": [
      673.6611483287305,
      700.653156827761
    ],
    "1:35": [
      1778.2741728878516,
      2022.1487223699073
    ],
    "1:36": [
      2067.2383198972784,
      2338.1457731368605
    ],
    "1:38": [
      3792.424742841841,
      4102.462465263104
    ],
    "1:21": [
      5594.501348771404,
      5948.720833841435
    ],
    "1:22": [
      6730.92378262174,
      6930.977846058505
    ],
    "1:43": [
      8260.18699953338,
      8455.561495194986
    ],
    "1:93": [
      9048.034752443798,
      9214.560991149068
    ],
    "1:11": [
      9939.71129904656,
      10041.406159545868
    ],
    "1:12": [
      10253.625487463669,
      10422.8203186208
    ],
    "1:13": [
      10691.950044678622,
      10793.669206469387
    ],
    "1:98": [
      11861.604607950774,
      12131.20275759871
    ],
    "1:99": [
      12501.296220860311,
      12770.564468417013
    ],
    "1:27": [
      13160.807994021114,
      13450.008173760609
    ],
    "1:49": [
      14150.101680364638,
      14159.040897128541
    ],
    "1:30": [
      16101.550701007767,
      16448.137986050406
    ],
    "1:33": [
      20597.466424408758,
      20838.21408407861
    ],
    "2:34": [
      746.9732363799544,
      945.1347586825343
    ],
    "2:20": [
      3552.498174742652,
      3630.807418534252
    ],
    "2:88": [
      5397.783901024961,
      5563.364151686739
    ],
    "2:41": [
      6176.983246223035,
      6375.121404541712
    ],
    "2:42": [
      6717.697071485096,
      6998.104662534658
    ],
    "2:24": [
      9166.440909730358,
      9326.618022976543
    ],
    "2:64": [
      11057.450828478039,
      11312.921446362589
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
    "3:52": [
      1139.9613114145436,
      1474.5029177042932
    ],
    "3:53": [
      1751.0110863631744,
      1839.9511645954676
    ],
    "3:2": [
      2479.001084975513,
      2690.282869475541
    ],
    "3:37": [
      3252.399740688261,
      3280.4722467363367
    ],
    "3:56": [
      4243.181848888948,
      4574.404970060138
    ],
    "3:57": [
      5030.150470541645,
      5366.745103085456
    ],
    "3:58": [
      5672.069276895063,
      5851.031005189563
    ],
    "3:23": [
      7534.233564955634,
      7861.354503501883
    ],
    "3:9": [
      8442.692456812249,
      8637.760456595295
    ],
    "3:44": [
      9185.628516129489,
      9336.475691938418
    ],
    "3:45": [
      10085.919581988113,
      10213.849233344627
    ],
    "3:65": [
      12007.99584736222,
      12185.730420001732
    ],
    "3:66": [
      12568.077955696106,
      12906.978723339087
    ],
    "4:17": [
      588.6270558304483,
      633.5464636235188
    ],
    "4:68": [
      829.7263457441582,
      1018.8073133207761
    ],
    "4:69": [
      2264.3535593190345,
      2484.601425902791
    ],
    "4:70": [
      2730.8877039882364,
      2788.9263803168797
    ],
    "4:71": [
      3282.1390780264333,
      3309.621432161379
    ],
    "4:72": [
      4025.53700816546,
      4323.470963320181
    ],
    "4:73": [
      5763.06297017044,
      5932.856843529306
    ],
    "4:74": [
      7151.69952900944,
      7308.365790778997
    ],
    "4:75": [
      8378.540681164415,
      8720.922168619089
    ],
    "4:76": [
      9501.22842414789,
      9661.546550930323
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
    "5:3": [
      3226.4610879202455,
      3499.0311003173238
    ],
    "5:5": [
      4413.621920453816,
      4659.6742325653295
    ],
    "5:6": [
      5193.838532475616,
      5543.774471871117
    ],
    "5:7": [
      6446.140688511011,
      6776.961359504672
    ],
    "5:8": [
      7412.392565486335,
      7676.415484440712
    ],
    "5:61": [
      8274.588527963224,
      8484.785427512212
    ],
    "5:10": [
      9358.357604689314,
      9367.887869771841
    ],
    "5:94": [
      9808.30204415559,
      9962.204644124591
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
    "5:28": [
      13704.561374893663,
      14013.93775887259
    ],
    "5:50": [
      14866.779084421754,
      14940.15020870754
    ],
    "5:83": [
      16220.518373689501,
      16521.349546205958
    ],
    "5:32": [
      18978.5474093071,
      19244.406903576626
    ]
  },
  "eval": {
    "quality_metrics": {
      "missed_priority": 7.0,
      "unassigned_count": 7.0,
      "energy_total": 63085.92916812443,
      "total_distance": 57706.15906485565,
      "makespan": 22007.377762869848,
      "route_balance": 0.23186944788008412
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
            "task_id": 55,
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
            "task_id": 87,
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
            "task_id": 90,
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
            "task_id": 92,
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
            "task_id": 77,
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
            "task_id": 96,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 97,
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
            "task_id": 67,
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
            "task_id": 81,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 84,
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
            "task_id": 38,
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
            "task_id": 93,
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
            "task_id": 13,
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
            "task_id": 99,
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
            "task_id": 49,
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
          },
          {
            "task_id": 34,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 20,
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
            "task_id": 41,
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
            "task_id": 24,
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
            "task_id": 37,
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
            "task_id": 57,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 58,
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
            "task_id": 9,
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
            "task_id": 45,
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
            "task_id": 66,
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
            "task_id": 68,
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
            "task_id": 71,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 72,
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
            "task_id": 75,
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
            "task_id": 3,
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
            "task_id": 6,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 7,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 8,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 61,
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
            "task_id": 94,
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
            "task_id": 28,
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
            "task_id": 83,
            "lateness": 0.0,
            "time_ref": 100.0,
            "ratio": 0.0
          },
          {
            "task_id": 32,
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
    },
    "lex_key": [
      7.0,
      63085.92916812443
    ]
  },
  "solver_diagnostics": {
    "algorithm": "weighted_alns",
    "policy": {
      "destroy_policy": {
        "operator_weights": {
          "random_removal": 2,
          "worst_task_removal": 10,
          "related_cluster_removal": 2,
          "critical_block_removal": 2,
          "route_rebalance_removal": 2
        },
        "signal_weights": {
          "cost_pressure": 0,
          "coupling_pressure": 0,
          "route_balance_pressure": 0,
          "mobility_opportunity": 10,
          "scarcity_protection": 10
        },
        "intensity_score": 5,
        "remove_ratio": 0.2
      },
      "insertion_policy": {
        "operator_weights": {
          "greedy_insertion": 10,
          "scarcity_first_insertion": 2,
          "regret_insertion": 2,
          "bottleneck_insertion": 2,
          "diversified_insertion": 2
        },
        "task_signal_weights": {
          "priority_loss": 10,
          "scarcity_pressure": 10,
          "regret_pressure": 0,
          "bottleneck_pressure": 0,
          "mobility_opportunity": 0
        },
        "position_signal_weights": {
          "insert_cost": 10,
          "future_slack": 10,
          "route_balance_gain": 0,
          "local_coupling_penalty": 0,
          "diversity_gain": 0
        }
      },
      "acceptance_policy": {
        "mode": "sa",
        "intensity_score": 5,
        "accept_level": 0.25,
        "exploration_score": 5.0
      },
      "reaction_factor": 0.2,
      "prior_mix_lambda": 0.25
    },
    "total_iters": 76,
    "actual_iters_used": 76,
    "actual_time_used_sec": 38.17738939999981,
    "best_update_count": 8,
    "best_update_iters": [
      1,
      8,
      10,
      11,
      26,
      27,
      29,
      44
    ],
    "best_update_lex_keys": [
      [
        9.0,
        65127.77287545939
      ],
      [
        9.0,
        64821.28316284199
      ],
      [
        9.0,
        64049.89790690675
      ],
      [
        9.0,
        63765.376010321495
      ],
      [
        8.0,
        64723.329890372755
      ],
      [
        8.0,
        63611.49343462049
      ],
      [
        8.0,
        62339.76950957247
      ],
      [
        7.0,
        63085.92916812443
      ]
    ],
    "first_best_iter": 1,
    "last_best_iter": 44,
    "plateau_iters_after_last_update": 32,
    "initial_solution_feasible": true,
    "returned_solution_source": "final_current",
    "returned_solution_feasible": true,
    "last_acceptance_decision": {
      "compare_result": 0,
      "accepted": true,
      "accept_mode": "sa",
      "feasibility_admissible": true,
      "accept_scope": "working_and_best_candidate",
      "feasibility_reason": "Trial is feasible under strict policy."
    },
    "last_destroy_move": {
      "operator_name": "related_cluster_removal",
      "shape": "cluster",
      "task_ids": [
        32,
        16,
        10,
        0,
        19,
        7,
        14,
        99,
        27,
        83,
        28,
        87,
        3,
        11,
        50,
        5,
        6,
        18,
        15
      ],
      "affected_routes": [
        0,
        1,
        5
      ],
      "features": {
        "cost_pressure": 0.39483093454022056,
        "priority_loss": 0.5384615384615384,
        "scarcity_pressure": 0.5384615384615389,
        "coupling_pressure": 0.3357691173615551,
        "mobility_opportunity": 0.0,
        "route_balance_pressure": 0.0,
        "violation_pressure": 0.0,
        "regret_pressure": 0.0,
        "bottleneck_pressure": 0.0
      },
      "score": -5.384615384615389,
      "metadata": {
        "target_k": 19,
        "seed_task": 32
      }
    },
    "last_insertion": {
      "context": "alns",
      "feasibility_mode": "strict",
      "operator_weights": {
        "greedy_insertion": 10,
        "scarcity_first_insertion": 2,
        "regret_insertion": 2,
        "bottleneck_insertion": 2,
        "diversified_insertion": 2
      },
      "task_signal_weights": {
        "priority_loss": 10,
        "scarcity_pressure": 10,
        "regret_pressure": 0,
        "bottleneck_pressure": 0,
        "mobility_opportunity": 0
      },
      "position_signal_weights": {
        "insert_cost": 10,
        "future_slack": 10,
        "route_balance_gain": 0,
        "local_coupling_penalty": 0,
        "diversity_gain": 0
      },
      "operator_use": {
        "regret_insertion": 4,
        "greedy_insertion": 10,
        "scarcity_first_insertion": 1,
        "diversified_insertion": 2,
        "bottleneck_insertion": 2
      },
      "unassigned_before": 26,
      "unassigned_after": 7,
      "inserted_count": 19,
      "failed_count": 7,
      "tasks_analyzed": 330,
      "positions_generated": 290,
      "positions_strict_checked": 290,
      "strict_feasible_positions": 290,
      "failure_breakdown": {
        "no_candidate": 117,
        "no_feasible": 0,
        "time_window": 0,
        "energy": 0,
        "skill": 0
      },
      "top_failed_tasks": [
        {
          "task_id": 25,
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
          "task_id": 46,
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
          "task_id": 59,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 60,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        },
        {
          "task_id": 63,
          "priority": 0.0,
          "capable_agents": 5,
          "candidate_positions": 0,
          "hard_feasible_positions": 0,
          "hard_filter_rejections": {
            "no_candidate_position": 1
          },
          "dominant_reason": "no_candidate_position"
        }
      ],
      "time_ms": 430.217,
      "operator": "greedy_insertion"
    },
    "iteration_trace": [
      {
        "iteration": 1,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65127.77287545939
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 2,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65127.77287545939
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 3,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          65026.0474978257
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 4,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          64996.58387971225
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 5,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          64996.58387971225
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 6,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          63944.99825086735
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 7,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 13.0,
        "current_lex_key": [
          13.0,
          63944.99825086735
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          65127.77287545939
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 8,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64821.28316284199
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64821.28316284199
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 9,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65296.132900789824
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64821.28316284199
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 10,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64049.89790690675
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          64049.89790690675
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 11,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          63765.376010321495
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 12,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          63765.376010321495
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 13,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 14,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 15,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 16,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 17,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 18,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 19,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65321.32151653283
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 20,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          65321.32151653283
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 21,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 22,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 9.0,
        "current_lex_key": [
          9.0,
          64970.31041586985
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 23,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 24,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 25,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 10.0,
        "current_lex_key": [
          10.0,
          65246.99085161778
        ],
        "best_feasible_objective": 9.0,
        "best_feasible_lex_key": [
          9.0,
          63765.376010321495
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 26,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64723.329890372755
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          64723.329890372755
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 27,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63611.49343462049
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          63611.49343462049
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 28,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63611.49343462049
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          63611.49343462049
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 29,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62339.76950957247
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 30,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62599.47845350863
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 31,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62599.47845350863
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 32,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63823.71005100893
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 33,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63806.92825972712
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 34,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 35,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 36,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63836.39187784058
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 37,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 38,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 39,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 40,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 41,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 42,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63831.741212376226
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 43,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          62783.86304758176
        ],
        "best_feasible_objective": 8.0,
        "best_feasible_lex_key": [
          8.0,
          62339.76950957247
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 44,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 45,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 46,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 47,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 48,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 49,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63085.92916812443
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 50,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 51,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 52,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          64006.65145620458
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 53,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63965.40321883399
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 54,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 7.0,
        "current_lex_key": [
          7.0,
          63965.40321883399
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 55,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 56,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 57,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64802.39892752095
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 58,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.123559936306
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 59,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.123559936306
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 60,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          63952.38849492484
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 61,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 62,
        "destroy_operator": "route_rebalance_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 63,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 64,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 65,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 66,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 67,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 68,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 69,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 70,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 71,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 72,
        "destroy_operator": "random_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 73,
        "destroy_operator": "critical_block_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 74,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": false,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          65916.954537958
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 75,
        "destroy_operator": "worst_task_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      },
      {
        "iteration": 76,
        "destroy_operator": "related_cluster_removal",
        "insertion_operator": "kernel",
        "accepted": true,
        "current_objective": 8.0,
        "current_lex_key": [
          8.0,
          64996.23224987785
        ],
        "best_feasible_objective": 7.0,
        "best_feasible_lex_key": [
          7.0,
          63085.92916812443
        ],
        "violation_total": 0.0,
        "violation_ratio_by_type": {
          "time_window": 0.0,
          "energy": 0.0
        },
        "feasibility_reason": "Trial is feasible under strict policy."
      }
    ],
    "destroy_operator_summary": {
      "random_removal": 23.0,
      "worst_task_removal": 19.0,
      "related_cluster_removal": 9.0,
      "critical_block_removal": 11.0,
      "route_rebalance_removal": 14.0
    },
    "insertion_operator_summary": {
      "candidate_tasks_total": 1973.0,
      "tasks_reinserted": 1319.0,
      "tasks_left_unassigned": 654.0,
      "dominant_repair_failure": "no_candidate",
      "repair_failure_reasons": {
        "no_candidate": 10222.0
      }
    },
    "operator_weights": {
      "destroy_operators": {
        "adaptive": {
          "random_removal": 0.8250000000000001,
          "worst_task_removal": 1.1280000000000001,
          "related_cluster_removal": 1.1466666666666667,
          "critical_block_removal": 0.8400000000000001,
          "route_rebalance_removal": 1.1555555555555554
        },
        "llm_score_prior": {
          "random_removal": 2.0,
          "worst_task_removal": 10.0,
          "related_cluster_removal": 2.0,
          "critical_block_removal": 2.0,
          "route_rebalance_removal": 2.0
        },
        "fused_final": {
          "random_removal": 1.0294327018993874,
          "worst_task_removal": 1.9463987846063942,
          "related_cluster_removal": 1.3177571757279425,
          "critical_block_removal": 1.0434387559088079,
          "route_rebalance_removal": 1.3254111547145038
        }
      },
      "insertion_operators": {
        "llm_weights": {
          "greedy_insertion": 10.0,
          "scarcity_first_insertion": 2.0,
          "regret_insertion": 2.0,
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
    "execution_trace": {
      "trace_id": "",
      "kind": "alns",
      "iters": 76,
      "destroy": {
        "selected_operator_counts": {
          "random_removal": 23,
          "worst_task_removal": 19,
          "related_cluster_removal": 9,
          "critical_block_removal": 11,
          "route_rebalance_removal": 14
        },
        "removed_task_count_avg": 17.486842
      },
      "repair": {
        "candidate_tasks_total": 1973,
        "tasks_reinserted": 1319,
        "tasks_left_unassigned": 654,
        "dominant_repair_failure": "no_candidate",
        "repair_failure_reasons": {
          "no_candidate": 10222
        }
      },
      "trial_flow": {
        "candidate_trials": 76,
        "hard_filter_failed": 0,
        "feasibility_rejected": 0,
        "admissible_trials": 76,
        "acceptance_rejected": 14,
        "accepted_trials": 62,
        "best_improved_trials": 8
      },
      "rejection_reasons": {}
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
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 10,
        "solver_calls": 8,
        "time_sec": 262.5,
        "iters": 493
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 12.0,
        "time_sec": 37.5,
        "iters": 1507.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 453.114202
  }
}
```


## Final Summary

```json
{
  "instance": "T100",
  "llm_mode": "api",
  "hard_feasible": true,
  "violation_total": 0.0,
  "missed_priority": 7.0,
  "unassigned_count": 7,
  "energy_total": 63085.92916812443,
  "total_distance": 57706.15906485565,
  "makespan": 22007.377762869848,
  "quality_summary": {
    "missed_priority": 7.0,
    "unassigned_count": 7.0,
    "energy_total": 63085.92916812443,
    "total_distance": 57706.15906485565,
    "makespan": 22007.377762869848,
    "route_balance": 0.23186944788008412
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
        "name": "energy_total",
        "metric": "energy_total",
        "direction": "min"
      }
    ],
    "budget": {
      "used": {
        "step_calls": 10,
        "solver_calls": 8,
        "time_sec": 262.5,
        "iters": 493
      },
      "remaining": {
        "step_calls": 0.0,
        "solver_calls": 12.0,
        "time_sec": 37.5,
        "iters": 1507.0
      }
    },
    "llm_fallback_used": false,
    "elapsed_sec": 453.114202
  },
  "elapsed_sec": 454.2406
}
```


> Status: finished
