from __future__ import annotations

import json
import unittest

from sar_alloc.config import Config
from sar_alloc.control_surface import DESTROY_SIGNAL_NAMES, FIELD_CANDIDATES
from sar_alloc.demo_policy import demo_solver_decision
from sar_alloc.llm_orchestrator import AgentState, _call_validated
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.observation import build_solver_observation
from sar_alloc.operators.destroy import build_destroy_landscape
from sar_alloc.policy_validator import validate_solver_decision
from sar_alloc.schemas import solver_decision_schema_for_candidates
from sar_alloc.solution import AssignmentSolution


def _instance() -> Instance:
    return Instance(
        tasks=(
            Task(id=1, loc=(1.0, 0.0), tw_start=0.0, tw_end=20.0, service_time=1.0, skill_req={"a"}, priority=5.0),
            Task(id=2, loc=(2.0, 0.0), tw_start=0.0, tw_end=20.0, service_time=1.0, skill_req={"a"}, priority=2.0),
        ),
        agents=(
            Agent(id=0, init_energy=100.0, skills={"a"}, speed=1.0, travel_energy_rate=1.0,
                  standby_power=0.0, skill_energy_rate={"a": 1.0}),
        ),
        depot=Depot(id=0, loc=(0.0, 0.0)),
        default_speed=1.0,
    )


def _enum_at(schema: dict, action: str, field_path: str) -> set[str]:
    branch = next(
        item for item in schema["properties"]["solver_decision"]["oneOf"]
        if item["properties"]["action"]["const"] == action
    )
    node = branch["properties"]
    for part in field_path.split("."):
        node = node[part] if part in node else node["properties"][part]
    if field_path.endswith("mode"):
        return set(node["enum"])
    return set(node["items"]["properties"]["name"]["enum"])


class ControlFieldContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = _instance()
        self.config = Config()
        self.candidates = build_public_candidates(self.instance, self.config)
        self.contract = {
            "contract_id": "C1",
            "contract_type": "alns_search",
            "objective_layers": ["missed_priority"],
            "feasibility_control": {"mode": "strict"},
            "protected_metrics": [],
            "target_policy": {"preferred_target_kinds": ["unassigned_priority", "route_balance"]},
        }
        self.observation = build_solver_observation(
            active_contract=self.contract,
            contract_progress={},
            remaining_contract_resources={"actions": 1, "time_sec": 1.0, "iters": 1},
            working_summary={
                "quality_summary": {"missed_priority": 2.0, "unassigned_count": 1, "route_balance": 0.5},
                "feasibility_summary": {"is_feasible": True, "violation_ratio_by_type": {}},
            },
            best_summary=None,
            candidate_landscape={"candidate_stats": {}, "task_pressure": {}},
            candidates=self.candidates,
        )

    def test_registry_matches_public_candidates(self) -> None:
        mapping = {
            "destroy_control.operator_scores": "destroy_operator_candidates",
            "destroy_control.signal_scores": "destroy_signal_candidates",
            "insertion_control.operator_scores": "insertion_operator_candidates",
            "insertion_control.task_signal_scores": "insertion_task_signal_candidates",
            "insertion_control.position_signal_scores": "insertion_position_signal_candidates",
            "acceptance_control.mode": "acceptance_candidates",
        }
        for field_path, candidate_field in mapping.items():
            self.assertEqual(FIELD_CANDIDATES[field_path], self.candidates.names(candidate_field))

    def test_observation_recommendations_are_field_valid(self) -> None:
        raw = json.dumps(self.observation, ensure_ascii=False)
        self.assertNotIn("usable_signals", raw)
        self.assertNotIn("recommended_control_axis", raw)
        for target in self.observation["decision_targets"]:
            for field_path, names in target.get("recommended_controls", {}).items():
                self.assertIn(field_path, FIELD_CANDIDATES)
                self.assertLessEqual(set(names), set(FIELD_CANDIDATES[field_path]))

    def test_destroy_landscape_exposes_only_public_destroy_signals(self) -> None:
        solution = AssignmentSolution(routes={0: [1, 2]}, unassigned=set())
        landscape = build_destroy_landscape(solution, self.instance, self.config)
        raw = json.dumps(landscape, ensure_ascii=False)
        self.assertNotIn("top_feature_levels", raw)
        for item in landscape["candidate_move_landscape"].values():
            self.assertLessEqual(set(item["top_signal_levels"]), set(DESTROY_SIGNAL_NAMES))
        for internal_name in ("priority_loss", "scarcity_pressure", "regret_pressure", "bottleneck_pressure", "violation_pressure"):
            self.assertNotIn(internal_name, raw)

    def test_dynamic_schema_isolates_each_field_enum(self) -> None:
        schema = solver_decision_schema_for_candidates(self.candidates, self.observation)
        destroy = _enum_at(schema, "run_alns", "destroy_control.signal_scores")
        task = _enum_at(schema, "run_alns", "insertion_control.task_signal_scores")
        position = _enum_at(schema, "run_alns", "insertion_control.position_signal_scores")
        acceptance = _enum_at(schema, "run_alns", "acceptance_control.mode")
        self.assertIn("scarcity_protection", destroy)
        self.assertNotIn("scarcity_pressure", destroy)
        self.assertIn("scarcity_pressure", task)
        self.assertNotIn("scarcity_protection", task)
        self.assertIn("future_slack", position)
        self.assertNotIn("future_slack", destroy)
        self.assertIn("threshold", acceptance)
        self.assertNotIn("threshold", destroy | task | position)

    def test_validator_rejects_cross_field_scarcity_name(self) -> None:
        payload = demo_solver_decision(self.observation)
        payload["solver_decision"]["destroy_control"]["signal_scores"] = [
            {"name": "scarcity_pressure", "score": 8}
        ]
        with self.assertRaisesRegex(ValueError, "destroy_control.signal_scores"):
            validate_solver_decision(payload, self.observation, candidates=self.candidates)

        payload["solver_decision"]["destroy_control"]["signal_scores"] = [
            {"name": "scarcity_protection", "score": 8}
        ]
        payload["solver_decision"]["insertion_control"]["task_signal_scores"] = [
            {"name": "scarcity_pressure", "score": 8}
        ]
        validate_solver_decision(payload, self.observation, candidates=self.candidates)

    def test_fallback_payload_uses_current_action_space(self) -> None:
        restricted = dict(self.observation)
        restricted["action_space"] = dict(self.observation["action_space"])
        restricted["action_space"].update({
            "allowed_destroy_operators": ["random_removal"],
            "allowed_destroy_signals": ["scarcity_protection"],
            "allowed_insertion_operators": ["greedy_insertion"],
            "allowed_task_signals": ["bottleneck_pressure"],
            "allowed_position_signals": ["diversity_gain"],
            "allowed_acceptance_modes": ["sa"],
        })
        payload = demo_solver_decision(restricted)
        validate_solver_decision(payload, restricted, candidates=self.candidates)
        raw = json.dumps(payload)
        for expected in ("random_removal", "scarcity_protection", "greedy_insertion", "bottleneck_pressure", "diversity_gain", "sa"):
            self.assertIn(expected, raw)

    def test_call_validated_repairs_once(self) -> None:
        class RepairClient:
            def __init__(self) -> None:
                self.calls = 0

            def chat(self, messages, **kwargs):
                del messages, kwargs
                self.calls += 1
                return json.dumps({"value": "bad" if self.calls == 1 else "good"})

        client = RepairClient()

        def validator(payload: dict) -> None:
            if payload.get("value") != "good":
                raise ValueError("value must be good")

        payload = _call_validated(
            client, AgentState(), "solver", {}, "ROLE: SOLVER", validator,
            lambda observation: {"value": "fallback"}, False,
        )
        self.assertEqual(client.calls, 2)
        self.assertEqual(payload, {"value": "good"})


if __name__ == "__main__":
    unittest.main()
