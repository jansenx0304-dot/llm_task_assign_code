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
                "decision_evidence": _supervisor_evidence(),
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

    def test_unknown_basis_source_is_rejected(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["decision_evidence"]["basis"][0]["source"] = "unknown_source"
        with self.assertRaises(AgentIOError):
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )

    def test_unknown_basis_name_is_rejected(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["decision_evidence"]["basis"][0]["name"] = "unknown_name"
        with self.assertRaisesRegex(AgentIOError, "basis name is not allowed"):
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )

    def test_argument_uses_index_out_of_range_is_rejected(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["decision_evidence"]["argument"][0]["uses"] = [2]
        with self.assertRaisesRegex(AgentIOError, "uses index out of range"):
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )

    def test_executable_step_requires_expected_effect(self) -> None:
        observation = _step_observation()
        payload = _valid_step_payload()
        payload["step_decision"]["decision_evidence"]["expected_effects"] = []
        with self.assertRaisesRegex(AgentIOError, "at least one expected_effect"):
            parse_validate_compile_step(
                raw_text=json.dumps(payload),
                schema=step_schema(observation["action_space"], observation["active_stage"]),
                observation=observation,
                active_stage=_stage(),
                config=Config(),
            )

    def test_review_request_allows_empty_expected_effects(self) -> None:
        observation = _step_observation(actions=["request_supervisor_review"])
        payload = _valid_review_payload()
        decision, control = parse_validate_compile_step(
            raw_text=json.dumps(payload),
            schema=step_schema(observation["action_space"], observation["active_stage"]),
            observation=observation,
            active_stage=_stage(),
            config=Config(),
        )
        self.assertEqual(decision.action, "request_supervisor_review")
        self.assertEqual(control.action, "request_supervisor_review")


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


def _step_observation(actions=None):
    actions = ["construct_initial"] if actions is None else list(actions)
    action_space = build_action_space()
    action_space["hard_executable_actions"] = actions
    stage = _stage().as_observation()
    return {
        "run_context": {"observation_id": "O1"},
        "execution_state": {
            "hard_executable_actions": actions,
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
            "decision_evidence": _step_evidence(),
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


def _valid_review_payload():
    return {
        "step_decision": {
            "action": "request_supervisor_review",
            "decision_evidence": {
                "basis": [{"source": "execution_state", "name": "hard_executable_actions"}],
                "argument": [{"claim": "Review is needed because no useful solver action remains.", "uses": [0]}],
                "control_intent": "Request supervisor review.",
                "expected_effects": [],
            },
            "review_request": {"reason": "No useful executable algorithm action remains."},
        }
    }


def _step_evidence():
    return {
        "basis": [
            {"source": "execution_state", "name": "hard_executable_actions"},
            {"source": "targetable_evidence", "name": "visible_task_ids"},
        ],
        "argument": [
            {"claim": "construct_initial is executable and targetable tasks are visible.", "uses": [0, 1]}
        ],
        "control_intent": "Construct an initial solution using visible targetable tasks.",
        "expected_effects": [{"metric": "missed_priority", "direction": "decrease"}],
    }


def _supervisor_evidence():
    return {
        "basis": [
            {"source": "run_context", "name": "remaining_global_resources"},
            {"source": "solution_state", "name": "missed_priority"},
        ],
        "argument": [
            {"claim": "A bounded initial construction stage is needed under the remaining budget.", "uses": [0, 1]}
        ],
        "control_intent": "Issue a small initial construction stage.",
        "expected_effects": [{"metric": "missed_priority", "direction": "decrease"}],
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
