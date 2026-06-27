from __future__ import annotations

import json
import unittest

from sar_alloc.agent_io import AgentIOError, parse_validate_compile_step, parse_validate_compile_supervisor
from sar_alloc.config import Config
from sar_alloc.schemas import build_action_space, step_schema, supervisor_schema
from sar_alloc.supervisor import StagePlan


class AgentIOTest(unittest.TestCase):
    def test_step_schema_rejects_unknown_operator(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["insertion_control"]["operator_scores"] = [
            {"name": "missing_operator", "score": 5}
        ]
        with self.assertRaises(AgentIOError) as ctx:
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )
        self.assertIn("missing_operator", str(ctx.exception))

    def test_supervisor_schema_rejects_budget_overrun(self) -> None:
        action_space = build_action_space()
        action_space["next_stage_resource_limits"] = {
            "max_solver_actions_allowed": 1,
            "max_time_sec_allowed": 1.0,
            "max_iters_allowed": 1,
        }
        observation = {
            "run_context": {"observation_id": "O1", "remaining_global_resources": {}},
            "solution_state": {"working": {"quality": {"missed_priority": 10.0}}},
            "action_space": action_space,
        }
        payload = {
            "supervisor_decision": {
                "action": "issue_stage",
                "global_objective": {"objective_layers": ["missed_priority"]},
                "next_stage": _raw_stage(max_actions=2, max_iters=1, max_time=1.0),
            }
        }
        with self.assertRaises(AgentIOError):
            parse_validate_compile_supervisor(
                raw_text=json.dumps(payload),
                schema=supervisor_schema("kickoff", action_space),
                observation=observation,
                phase="kickoff",
                config=Config(),
                stage_index=1,
            )

    def test_runtime_target_rejects_non_visible_ids(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["runtime_target"]["task_ids"] = [99]
        with self.assertRaises(AgentIOError) as ctx:
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )
        self.assertIn("non-visible task id", str(ctx.exception))


def _stage() -> StagePlan:
    return StagePlan(
        stage_id="S001",
        stage_type="initial_construction",
        objective_layers=[{"metric": "missed_priority", "direction": "min"}],
        target_intents=[{"intent_id": "construct_coverage", "intent_type": "construction"}],
        feasibility_policy={"mode": "strict"},
        protected_metrics=[],
        resource_policy={"min_actions": 1, "max_actions": 1, "max_iters": 1, "max_time_sec": 1.0},
    )


def _step_observation():
    action_space = build_action_space()
    action_space["hard_executable_actions"] = ["construct_initial"]
    stage = _stage().as_observation()
    return {
        "run_context": {"observation_id": "O1"},
        "execution_state": {
            "hard_executable_actions": ["construct_initial"],
            "remaining_stage_resources": {"actions": 1, "time_sec": 1.0, "iters": 1},
        },
        "active_stage": stage,
        "targetable_evidence": {"visible_task_ids": [1], "visible_agent_ids": [2]},
        "action_space": action_space,
    }


def _valid_step_payload():
    return {
        "step_decision": {
            "action": "construct_initial",
            "decision_basis": [
                {
                    "basis_id": "B1",
                    "claim": "construct",
                    "evidence_refs": ["targetable_evidence.visible_task_ids"],
                }
            ],
            "situation_summary": {"summary": "construct", "basis_ids": ["B1"]},
            "intent_id": "construct_coverage",
            "runtime_target": {
                "scope_kind": "task_scope",
                "task_ids": [1],
                "agent_ids": [],
                "focus_metrics": ["missed_priority"],
            },
            "insertion_control": {
                "operator_scores": [{"name": "greedy_insertion", "score": 5}],
                "task_signal_scores": [{"name": "priority_loss", "score": 5}],
                "position_signal_scores": [{"name": "insert_cost", "score": 5}],
            },
            "solver_budget": {"max_iters": 1, "max_time_sec": 1.0},
        }
    }


def _raw_stage(max_actions: int, max_iters: int, max_time: float):
    return {
        "stage_type": "initial_construction",
        "objective_layers": ["missed_priority"],
        "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
        "target_intents": [
            {
                "intent_id": "construct_coverage",
                "intent_type": "construction",
                "evidence_refs": ["run_context.remaining_global_resources"],
                "rationale": "construct",
            }
        ],
        "protected_metrics": [],
        "resource_policy": {
            "min_actions": 1,
            "max_actions": max_actions,
            "max_iters": max_iters,
            "max_time_sec": max_time,
            "require_feasible": False,
            "metric_thresholds": {},
        },
    }


if __name__ == "__main__":
    unittest.main()
