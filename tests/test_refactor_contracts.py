from __future__ import annotations

import random
import unittest
from dataclasses import replace
from unittest.mock import patch

from sar_alloc.config import Budget, Config, ObjectiveLayer
from sar_alloc.demo_policy import demo_solver_decision, demo_supervisor_kickoff, demo_supervisor_review
from sar_alloc.llm_client import DummyLLMClient
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.models import Agent, Depot, Instance, Task
import sar_alloc.operators.insertion as insertion_module
from sar_alloc.operators import InsertPosition, LandscapeFeatures
from sar_alloc.operators.destroy import DestroyMove
from sar_alloc.operators.insertion import InsertionContext, run_insertion_kernel
from sar_alloc.policy_validator import validate_solver_decision, validate_supervisor_kickoff, validate_supervisor_review
from sar_alloc.reporting import ConsoleTracePrinter
from sar_alloc.schemas import SOLVER_DECISION_SCHEMA, SUPERVISOR_KICKOFF_SCHEMA, SUPERVISOR_REVIEW_SCHEMA
from sar_alloc.solution import AssignmentSolution
from sar_alloc.tools.assign_solvers import _sample_rank_weighted_destroy_move
from sar_alloc.tools.llm_utils import (
    ContractProgress,
    compile_acceptance,
    compile_contract,
    compile_destroy_control,
    compile_insertion_control,
    compile_solver_control,
    derive_solver_request,
)


def tiny_instance() -> Instance:
    return Instance(
        tasks=(
            Task(id=1, loc=(1.0, 0.0), tw_start=0.0, tw_end=50.0, service_time=1.0, skill_req={"a"}, priority=5.0),
            Task(id=2, loc=(2.0, 0.0), tw_start=0.0, tw_end=50.0, service_time=1.0, skill_req={"missing"}, priority=2.0),
        ),
        agents=(Agent(id=0, init_energy=100.0, skills={"a"}, speed=1.0, travel_energy_rate=1.0, standby_power=0.0, skill_energy_rate={"a": 1.0}),),
        depot=Depot(id=0, loc=(0.0, 0.0)),
        default_speed=1.0,
    )


class PublicContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = tiny_instance()
        self.config = Config()
        self.config.eval.objective_policy.layers = [ObjectiveLayer(name="missed_priority", metric="missed_priority", direction="min")]
        self.candidates = build_public_candidates(self.instance, self.config)
        self.remaining = {"step_calls": 10.0, "solver_calls": 10.0, "time_sec": 10.0, "iters": 100.0}

    def test_public_candidates_are_name_description_only(self) -> None:
        for group in self.candidates.as_dict().values():
            for item in group:
                self.assertEqual(set(item), {"name", "description"})
                self.assertTrue(item["description"])

    def test_schema_properties_have_descriptions(self) -> None:
        def walk(node: object) -> None:
            if isinstance(node, dict):
                for value in node.get("properties", {}).values():
                    self.assertIn("description", value)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        for schema in (SUPERVISOR_KICKOFF_SCHEMA, SUPERVISOR_REVIEW_SCHEMA, SOLVER_DECISION_SCHEMA):
            walk(schema)

    def test_solver_shapes_and_no_solver_request(self) -> None:
        initial = demo_solver_decision({"active_contract": {"contract_type": "initial_construction"}})
        validate_solver_decision(initial, self.candidates, "initial_construction", evidence_items=[{"id": "E1"}], memory_items=[])
        run = demo_solver_decision({"active_contract": {"contract_type": "alns_search"}})
        validate_solver_decision(run, self.candidates, "alns_search", evidence_items=[{"id": "E1"}], memory_items=[])
        bad = {
            "solver_decision": {
                "action": "construct_initial",
                "reason": "wrong stage",
                "insertion_control": run["solver_decision"]["insertion_control"],
                "decision_basis": {"evidence_refs": ["E1"], "memory_refs": [], "summary": "x"},
            }
        }
        with self.assertRaises(ValueError):
            validate_solver_decision(bad, self.candidates, "alns_search", evidence_items=[{"id": "E1"}], memory_items=[])
        extra = demo_solver_decision({"active_contract": {"contract_type": "alns_search"}})
        extra["solver_decision"]["solver_request"] = {"time_limit_sec": 1, "max_iters": 1}
        with self.assertRaises(ValueError):
            validate_solver_decision(extra, self.candidates, "alns_search", evidence_items=[{"id": "E1"}], memory_items=[])

    def test_kickoff_and_review_validate(self) -> None:
        kickoff = demo_supervisor_kickoff({"remaining_global_budget": self.remaining})
        validate_supervisor_kickoff(kickoff, self.candidates, [{"id": "E1"}], [], self.config, self.remaining)
        review = demo_supervisor_review({"remaining_global_budget": self.remaining})
        validate_supervisor_review(review, self.candidates, [{"id": "E1"}], [], self.config, self.remaining)


class CompilationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidates = build_public_candidates(tiny_instance(), Config())
        self.remaining = {"step_calls": 10.0, "solver_calls": 10.0, "time_sec": 10.0, "iters": 100.0}

    def test_sparse_defaults_and_mappings(self) -> None:
        insertion_control = demo_solver_decision({"active_contract": {"contract_type": "initial_construction"}})["solver_decision"]["insertion_control"]
        insertion = compile_insertion_control(insertion_control, self.candidates)
        self.assertEqual(insertion.operator_weights["greedy_insertion"], 2)
        self.assertEqual(insertion.operator_weights["scarcity_first_insertion"], 8)
        self.assertEqual(insertion.task_signal_weights["regret_pressure"], 0)
        solver = demo_solver_decision({"active_contract": {"contract_type": "alns_search"}})
        destroy = compile_destroy_control(solver["solver_decision"]["destroy_control"], self.candidates)
        self.assertAlmostEqual(destroy.remove_ratio, 0.20)
        acceptance = compile_acceptance({"mode": "threshold", "intensity_score": 5, "reason": "x"})
        self.assertAlmostEqual(acceptance.accept_level, 0.10)
        self.assertAlmostEqual(acceptance.exploration_score, 2.5)

    def test_contract_and_solver_request(self) -> None:
        raw = demo_supervisor_review({"remaining_global_budget": self.remaining})["supervisor_decision"]["next_contract"]
        contract = compile_contract(raw, "C001", Config())
        request = derive_solver_request(contract, ContractProgress("C001"))
        self.assertEqual(request.max_iters, 1)
        self.assertAlmostEqual(request.time_limit_sec, 1.0 / 3.0)

    def test_compiled_solver_summary_shows_llm_operator_scores(self) -> None:
        solver = demo_solver_decision({"active_contract": {"contract_type": "alns_search"}})
        compiled = compile_solver_control(solver, self.candidates).as_dict()
        compiled["llm_operator_scores"] = {
            "destroy": solver["solver_decision"]["destroy_control"]["operator_scores"],
            "insertion": solver["solver_decision"]["insertion_control"]["operator_scores"],
        }
        summary = ConsoleTracePrinter(use_color=False, use_emoji=False)._compiled_solver_summary(compiled)
        self.assertIn("llm_destroy_scores=[related_cluster_removal:8]", summary)
        self.assertIn("scarcity_first_insertion:8", summary)


class InsertionKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = tiny_instance()
        self.config = Config()
        self.config.eval.objective_policy.layers = [ObjectiveLayer(name="missed_priority", metric="missed_priority", direction="min")]
        candidates = build_public_candidates(self.instance, self.config)
        control = demo_solver_decision({"active_contract": {"contract_type": "initial_construction"}})["solver_decision"]["insertion_control"]
        self.policy = compile_insertion_control(control, candidates)

    def test_same_kernel_builds_initial_and_reinserts(self) -> None:
        empty = AssignmentSolution.empty_from_instance(self.instance, put_all_unassigned=False)
        initial = run_insertion_kernel(empty, [1, 2], self.policy, InsertionContext("initial"), instance=self.instance, config=self.config, rng=random.Random(0))
        self.assertIn(1, initial.all_assigned_tasks())
        self.assertIn(2, initial.unassigned)
        partial = initial.clone(deep=True)
        partial.remove_task(0, 1, to_unassigned=True)
        rebuilt = run_insertion_kernel(partial, [1, 2], self.policy, InsertionContext("alns"), instance=self.instance, config=self.config, rng=random.Random(0))
        self.assertIn(1, rebuilt.all_assigned_tasks())
        self.assertIn(2, rebuilt.unassigned)
        self.assertEqual(rebuilt.solver_diagnostics["last_insertion"]["context"], "alns")

    def test_collect_task_insertion_stats_evaluates_all_hard_filtered_positions(self) -> None:
        positions = [InsertPosition(agent_id=0, position=i) for i in range(12)]
        scored = [
            insertion_module.InsertionCandidate(
                tid=1,
                agent_id=0,
                position=i,
                delta_distance=float(i),
                delta_energy=0.0,
                route_duration_after=0.0,
                suffix_min_slack=10.0 + float(i),
                suffix_tardiness_total=0.0,
                suffix_ratio=0.0,
                energy_remaining_ratio=1.0,
                depot_return_pressure=0.0,
                route_pressure_after=0.0,
                balance_improvement=0.0,
                candidate_cost=float(i),
                dominated=False,
                strict_feasible=False,
                position_score=float(12 - i),
            )
            for i in range(12)
        ]
        calls = []

        def fake_eval(candidate, sol, *, instance, config):
            del sol, instance, config
            calls.append(int(candidate.position))
            return replace(candidate, strict_feasible=True)

        empty = AssignmentSolution.empty_from_instance(self.instance, put_all_unassigned=False)
        with patch.object(insertion_module, "enumerate_hard_filtered_positions", return_value=positions), \
             patch.object(insertion_module, "score_insert_positions", return_value=scored), \
             patch.object(insertion_module, "_strict_evaluate_insertion_candidate", side_effect=fake_eval):
            stats, diagnostics = insertion_module.collect_task_insertion_stats(
                empty,
                1,
                self.instance,
                self.config,
                self.policy,
                {0: 0.0},
                None,
            )

        self.assertEqual(calls, list(range(12)))
        self.assertEqual(stats.candidate_count, 12)
        self.assertEqual(diagnostics["positions_generated"], 12)
        self.assertEqual(diagnostics["positions_strict_checked"], 12)


class DestroySamplingTests(unittest.TestCase):
    def test_rank_weighted_destroy_sampling_allows_low_rank_candidates(self) -> None:
        features = LandscapeFeatures(
            cost_pressure=0.0,
            priority_loss=0.0,
            scarcity_pressure=0.0,
            coupling_pressure=0.0,
            mobility_opportunity=0.0,
            route_balance_pressure=0.0,
            violation_pressure=0.0,
            regret_pressure=0.0,
            bottleneck_pressure=0.0,
        )
        moves = [
            DestroyMove(
                operator_name="worst_task_removal",
                shape="task_set",
                task_ids=(i,),
                affected_routes=(0,),
                features=features,
                score=float(10 - i),
                metadata={"index": i},
            )
            for i in range(10)
        ]
        rng = random.Random(0)
        seen = {
            int(_sample_rank_weighted_destroy_move(moves, rng).metadata["index"])
            for _ in range(2000)
        }
        self.assertTrue(any(index >= 5 for index in seen))


class OrchestratorTests(unittest.TestCase):
    def test_dummy_call_order_and_trace(self) -> None:
        solution = run_orchestrator(
            DummyLLMClient(),
            tiny_instance(),
            "cover tasks",
            Config(),
            Budget(time_limit_sec=0.2, max_iters=4),
            max_agent_steps=5,
            max_solver_calls=4,
            llm_mode="dummy",
        )
        event_types = [event["event_type"] for event in solution.run_artifact["trace_events"]]
        required = [
            "supervisor_kickoff_observation",
            "supervisor_kickoff_prompt",
            "supervisor_kickoff_raw_output",
            "supervisor_kickoff_validated_payload",
            "global_objective_applied",
            "compiled_contract",
            "solver_observation",
            "solver_validated_payload",
            "compiled_initial_policy",
            "initial_insertion_result",
            "contract_completion_check",
            "supervisor_review_observation",
            "compiled_solver_policy",
            "solver_result",
            "final_result",
        ]
        positions = [event_types.index(name) for name in required]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("objective_observation", event_types)
        self.assertNotIn("initial_observation", event_types)

    def test_trace_callback_failure_does_not_interrupt_or_drop_events(self) -> None:
        callback_events = []

        def failing_callback(event):
            callback_events.append(event["event_type"])
            raise RuntimeError("reporter unavailable")

        solution = run_orchestrator(
            DummyLLMClient(),
            tiny_instance(),
            "cover tasks",
            Config(),
            Budget(time_limit_sec=0.2, max_iters=4),
            max_agent_steps=5,
            max_solver_calls=4,
            llm_mode="dummy",
            trace_callback=failing_callback,
        )
        event_types = [event["event_type"] for event in solution.run_artifact["trace_events"]]
        self.assertEqual(callback_events, event_types)
        self.assertIn("final_result", event_types)


if __name__ == "__main__":
    unittest.main()
