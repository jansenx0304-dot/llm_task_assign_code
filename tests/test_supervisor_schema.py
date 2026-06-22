from __future__ import annotations

import copy
import json
import unittest

from sar_alloc.config import Config
from sar_alloc.demo_policy import demo_supervisor_kickoff, demo_supervisor_review
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.observation import build_supervisor_review_observation
from sar_alloc.policy_validator import validate_supervisor_kickoff, validate_supervisor_review
from sar_alloc.schemas import schema_text, supervisor_review_schema_for_limits


def _instance() -> Instance:
    return Instance(
        tasks=(Task(1, (1.0, 0.0), 0.0, 10.0, 1.0, {"a"}, 1.0),),
        agents=(Agent(0, 100.0, {"a"}, 1.0, 1.0, 0.0, {"a": 1.0}),),
        depot=Depot(0, (0.0, 0.0)),
        default_speed=1.0,
    )


class SupervisorSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config()
        self.candidates = build_public_candidates(_instance(), self.config)
        self.remaining = {"step_calls": 10.0, "solver_calls": 10.0, "time_sec": 10.0, "iters": 100.0}
        self.evidence = [{"id": "E1"}, {"id": "E2"}, {"id": "E3"}, {"id": "E4"}, {"id": "E5"}, {"id": "E6"}]

    def test_valid_kickoff_review_and_stop_pass(self) -> None:
        validate_supervisor_kickoff(demo_supervisor_kickoff({"remaining_global_budget": self.remaining}), self.candidates, self.evidence, [], self.config, self.remaining)
        validate_supervisor_review(demo_supervisor_review({"remaining_global_budget": self.remaining}), self.candidates, self.evidence, [], self.config, self.remaining)
        validate_supervisor_review(demo_supervisor_review({"remaining_global_budget": self.remaining}, stop=True), self.candidates, self.evidence, [], self.config, self.remaining)

    def test_kickoff_requires_initial_contract(self) -> None:
        payload = demo_supervisor_kickoff({"remaining_global_budget": self.remaining})
        payload["supervisor_decision"]["next_contract"]["contract_type"] = "alns_search"
        with self.assertRaises(ValueError):
            validate_supervisor_kickoff(payload, self.candidates, self.evidence, [], self.config, self.remaining)

    def test_duplicate_global_objective_fails(self) -> None:
        payload = demo_supervisor_kickoff({"remaining_global_budget": self.remaining})
        objective = payload["supervisor_decision"]["global_objective"]
        objective["objective_layers"][1] = "missed_priority"
        objective["selection_basis"][1]["metric"] = "missed_priority"
        with self.assertRaises(ValueError):
            validate_supervisor_kickoff(payload, self.candidates, self.evidence, [], self.config, self.remaining)

    def test_legacy_payload_shape_fails(self) -> None:
        bad = {"supervisor" + "_plan": {"action": "issue_contract", "budget": {}, "review" + "_policy": {}}}
        with self.assertRaises(ValueError):
            validate_supervisor_review(bad, self.candidates, self.evidence, [], self.config, self.remaining)

    def test_invalid_completion_and_feasibility_fail(self) -> None:
        payload = demo_supervisor_review({"remaining_global_budget": self.remaining})
        contract = payload["supervisor_decision"]["next_contract"]
        bad = copy.deepcopy(payload)
        bad["supervisor_decision"]["next_contract"]["completion_policy"]["min_solver_actions"] = 4
        bad["supervisor_decision"]["next_contract"]["completion_policy"]["max_solver_actions"] = 3
        with self.assertRaises(ValueError):
            validate_supervisor_review(bad, self.candidates, self.evidence, [], self.config, self.remaining)

        bad = copy.deepcopy(payload)
        bad["supervisor_decision"]["next_contract"]["completion_policy"]["success_rules"][0]["event"] = "unknown_event"
        with self.assertRaises(ValueError):
            validate_supervisor_review(bad, self.candidates, self.evidence, [], self.config, self.remaining)

        bad = copy.deepcopy(payload)
        bad["supervisor_decision"]["next_contract"]["feasibility_control"] = {
            "mode": "strict",
            "relaxation_ratios": [{"type": "energy", "limit_ratio": 0.1, "reason": "x"}],
        }
        with self.assertRaises(ValueError):
            validate_supervisor_review(bad, self.candidates, self.evidence, [], self.config, self.remaining)

        bad = copy.deepcopy(payload)
        bad["supervisor_decision"]["next_contract"]["feasibility_control"] = {
            "mode": "relaxed_recoverable",
            "relaxation_ratios": [],
        }
        with self.assertRaises(ValueError):
            validate_supervisor_review(bad, self.candidates, self.evidence, [], self.config, self.remaining)

    def test_review_observation_and_schema_expose_dynamic_contract_limits(self) -> None:
        remaining = {"step_calls": 9.0, "solver_calls": 20.0, "time_sec": 300.0, "iters": 2000.0}
        observation = build_supervisor_review_observation(
            remaining_global_budget=remaining,
            completed_contract={
                "contract_id": "C001",
                "contract_type": "initial_construction",
                "stage_goal": {"summary": "x", "main_problem": "x", "search_intent": "x"},
                "stage_objective_layers": [{"metric": "missed_priority", "direction": "min"}],
                "guidance": {},
                "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
                "feasibility_policy": {"mode": "strict"},
                "completion_policy": {},
            },
            completed_contract_progress={},
            completed_contract_result={},
            working_summary={},
            best_summary=None,
            candidate_landscape={},
            recent_memory=[],
            candidates=self.candidates,
            relaxation_scale_context={},
        )
        self.assertEqual(
            observation["next_contract_resource_limits"],
            {
                "max_solver_actions_allowed": 9,
                "max_time_sec_allowed": 300.0,
                "max_iters_allowed": 2000,
            },
        )
        dynamic_schema = schema_text(supervisor_review_schema_for_limits(observation["next_contract_resource_limits"]))
        parsed = json.loads(dynamic_schema)
        issue_contract = parsed["properties"]["supervisor_decision"]["oneOf"][0]
        completion_policy = issue_contract["properties"]["next_contract"]["properties"]["completion_policy"]
        policy_props = completion_policy["properties"]
        self.assertEqual(policy_props["max_solver_actions"]["maximum"], 9)
        self.assertEqual(policy_props["max_time_sec"]["maximum"], 300.0)
        self.assertEqual(policy_props["max_iters"]["maximum"], 2000)


if __name__ == "__main__":
    unittest.main()
